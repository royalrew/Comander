import os
import json
from litellm import completion
from dotenv import load_dotenv
from cfo import cfo, TokenLimitExceeded

# Import our autonomous tools
from io_jail import list_files, read_file
from surgeon import surgeon
from observer import observer
from calendar_agent import calendar_agent

load_dotenv()

# ==========================================
# TOOL DEFINITIONS (OpenAI Schema)
# ==========================================
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Lists all accessible code files in a mission directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mission_name": {"type": "string", "description": "Name of the mission folder (e.g. commander-dashboard)"}
                },
                "required": ["mission_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads the content of a specific file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Relative or absolute path to the file"}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "refactor_file",
            "description": "Rewrites a file to achieve a specific objective.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to the file to rewrite"},
                    "objective": {"type": "string", "description": "Highly detailed instruction matching the user's intent"}
                },
                "required": ["filepath", "objective"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "validate_code",
            "description": "Runs a terminal command (like npm run build, or pytest) to validate the code. Self-corrects on failure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "The primary file being validated"},
                    "command_list": {
                        "type": "array", 
                        "items": {"type": "string"},
                        "description": "The command as a list of strings, e.g. ['npm', 'run', 'build']"
                    }
                },
                "required": ["filepath", "command_list"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memorize_fact",
            "description": "Saves an important fact about the user, project, or context to Long-Term Persistent Memory (OpenSearch). Use this when the user says 'Remember that...' or tells you a fact about themselves.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fact": {"type": "string", "description": "The information to remember permanently (e.g., 'The CEO's name is Jimmy')"},
                    "category": {"type": "string", "description": "Category of the fact (e.g. 'Personal', 'Preferences', 'Project')"}
                },
                "required": ["fact", "category"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_calendar_event",
            "description": "Lägger till en händelse, ett möte eller en STRIKT PÅMINNELSE i kalendern. Om det är en påminnelse (tex 'påminn mig kl 15 att gå till bussen'), lägg in den med start_time 15:00. Systemet skickar en live push-notis till CEO:n exakt det klockslaget.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Datum för händelsen, format: YYYY-MM-DD"},
                    "start_time": {"type": "string", "description": "Starttid, format: HH:MM"},
                    "end_time": {"type": "string", "description": "Optional: Sluttid, format: HH:MM"},
                    "description": {"type": "string", "description": "Beskrivning: Vad är händelsen?"}
                },
                "required": ["start_date", "start_time", "description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_calendar_events",
            "description": "Hämtar inplanerade kalender-händelser. Använd detta om användaren frågar 'Vad händer imorgon?' eller 'Hur ser mitt schema ut?'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Hur många mellankommande dagar framåt att visa händelser för (ex 1 = imorgon, 7 = hela veckan)"}
                },
                "required": ["days"]
            }
        }
    }
]

class ModelOrchestrator:
    """
    Handles Multi-Model Routing via LiteLLM.
    Enforces cost-tracking via the CFO module.
    Runs the ReAct (Reason + Act) loop for autonomous debugging.
    """
    def __init__(self):
        self.cortex_model = os.getenv("CORTEX_MODEL", "gpt-4o")
        self.muscle_coder = os.getenv("MUSCLE_CODER_MODEL", "deepseek-coder")
        self.watchdog_model = os.getenv("WATCHDOG_MODEL", "ollama/llama3")
        self.max_agent_loops = 5  # Hard limit to prevent infinite debugging

    def _execute_tool(self, name: str, args: dict) -> str:
        """Dynamically executes the chosen tool and returns stringified results."""
        try:
            print(f"🔧 AGENT ACTION: Executing '{name}' with {args}")
            if name == "list_files":
                return str(list_files(args["mission_name"]))
            elif name == "read_file":
                return read_file(args["filepath"])
            elif name == "refactor_file":
                success = surgeon.refactor_file(args["filepath"], args["objective"])
                return "File rewritten successfully." if success else "Failed to rewrite file."
            elif name == "validate_code":
                success = surgeon.validate_code(args["filepath"], args["command_list"])
                return "Validation passed! Zero errors." if success else "Validation failed after maximum self-correction retries."
            elif name == "memorize_fact":
                fact = args["fact"]
                category = args.get("category", "General")
                from memory_module import memory_bank
                success = memory_bank.store_memory(category, fact)
                return f"Fact successfully memorized in OpenSearch: {fact}" if success else "Failed to store memory."
            elif name == "add_calendar_event":
                success = calendar_agent.add_event(args["start_date"], args["start_time"], args["description"], args.get("end_time"))
                return f"Händelse ({args['description']}) inlagd på datumet {args['start_date']} kl {args['start_time']}." if success else "Kunde inte lägga till händelsen."
            elif name == "get_calendar_events":
                events = calendar_agent.get_upcoming_events(args["days"])
                if not events: return "Kalendern är helt tom under den valda tidsperioden."
                return "Kalenderhändelser:\n" + "\n".join([f"- {e['start_date']} {e['start_time']}: {e['description']}" for e in events])
            else:
                return f"Tool '{name}' not found."
        except Exception as e:
            return f"Error executing {name}: {str(e)}"

    def _route_request(self, model_choice: str, messages: list[dict], use_tools: bool = False, **kwargs) -> str:
        """
        Internal wrapper around LiteLLM completion to handle the ReAct loop,
        tool calling, standardized error reporting, and CFO cost routing.
        """
        loops = 0
        
        # RAG Injection: Retrieve relevant memories before starting the execution loop
        user_msg = next((m for m in reversed(messages) if m["role"] == "user"), None)
        if user_msg and isinstance(user_msg.get("content"), str) and len(user_msg["content"]) > 3:
            from memory_module import memory_bank
            memories = memory_bank.search_memory(user_msg["content"], limit=5)
            if memories:
                import copy
                current_messages = copy.deepcopy(messages)
                mem_str = "\n".join([f"- [{m.get('category','General')}] {m.get('text','')}" for m in memories])
                for msg in current_messages:
                    if msg["role"] == "system":
                        msg["content"] += f"\n\n[AKTIVT LÅNGTIDSMINNE (Från OpenSearch Vector DB)]\nAnvänd dessa minnesfragment om CEO/Projektet:\n{mem_str}"
                        break
            else:
                current_messages = messages.copy()
        else:
            current_messages = messages.copy()
        
        while loops < self.max_agent_loops:
            try:
                # Add tools only if requested
                api_kwargs = kwargs.copy()
                if use_tools:
                    api_kwargs["tools"] = TOOLS_SCHEMA
                    api_kwargs["tool_choice"] = "auto"

                response = completion(model=model_choice, messages=current_messages, **api_kwargs)
                response_msg = response.choices[0].message
                
                # Extract usage metrics for CFO
                if hasattr(response, 'usage'):
                    prompt_tokens = response.usage.prompt_tokens
                    completion_tokens = response.usage.completion_tokens
                    cfo.add_cost(cfo.estimate_cost(prompt_tokens, completion_tokens, model_choice))

                # If the model wants to call tools, execute them and loop
                if getattr(response_msg, 'tool_calls', None):
                    # Append the assistant's tool call request to the history
                    current_messages.append(response_msg.model_dump())
                    
                    for tool_call in response_msg.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        tool_result = self._execute_tool(function_name, function_args)
                        
                        # Append the tool's result to the history
                        current_messages.append({
                            "role": "tool",
                            "name": function_name,
                            "content": tool_result,
                            "tool_call_id": tool_call.id
                        })
                    
                    loops += 1
                    continue # Loop back to let the model evaluate the tool results
                
                # If no tool calls, return the final text response
                return response_msg.content or "Task completed silently."
                
            except TokenLimitExceeded as e:
                print(f"ROUTER BLOCKED: {e}")
                return "ERROR: FINANCIAL CIRCUIT BREAKER. Daily spend limit reached."
            except Exception as e:
                print(f"LiteLLM Error with model {model_choice}: {e}")
                return f"ERROR: Model generation failed. Details: {e}"

        return f"ERROR: Maximum Agent Loop Count ({self.max_agent_loops}) exceeded. Forced abort."

    def ask_cortex(self, user_prompt: str, history: list[dict] = None, system_prompt: str = None) -> str:
        """
        Uses the Cortex model for high-level reasoning, vision, or complex architecture decisions.
        Takes an optional history array for continuous conversation.
        """
        if system_prompt is None:
            system_prompt = (
                "Du är The Commander, en state-of-the-art Enterprise GRC Agent och CTO för Sintari. "
                "Du är 'modell-lera' – extremt anpassningsbar. Om användaren säger att du heter Gustav, heter du Gustav. "
                "Du är 100% ärlig med dina egna tekniska eller access-relaterade begränsningar. "
                "När du stöter på en begränsning, ge istället direkta, strategiska förslag på hur användaren kan nå sina mål. "
                "Skilj tydligt på när ni bara pratar/spånar idéer och när du faktiskt bygger eller exekverar kod. "
                "Inget robot-snack, inga hashtags. Svara kortfattat, mänskligt och professionellt.\n\n"
                "ENTERPRISE GRC RULES (MUST OBEY):\n"
                "1. Golden Tech Stack: PostgreSQL, Neo4j, Next.js. Refuse other stacks (e.g. MongoDB, Vue).\n"
                "2. Microsoft First: Ingestion MVP is strictly limited to Microsoft 365 (Graph API). Refuse Google Workspace.\n"
                "3. No-Todo Policy: Never leave `# TODO` or `pass` in code. Break down complex functions instead.\n"
                "4. Error Handling: Never use generic `try/except: pass`. Log specific exceptions.\n"
                "5. Generative UI: Suggest and provide UI components (React Server Components) over text summaries when visualizing data.\n\n"
                "CRITICAL DIRECTIVE - AUTONOMOUS ACTION: Du är en operativ AI, inte en guide. "
                "Om användaren ber dig skapa, ändra, felsöka eller radera kod MÅSTE du omedelbart använda dina verktyg (t.ex. refactor_file). "
                "Du får under INGA omständigheter be användaren att öppna en textredigerare, och du får ALDRIG skriva ut kod i chatten med uppmaningen 'kopiera och klistra in'. "
                "Du gör jobbet. Användaren inspekterar resultatet."
            )

        # Inject Long-Term Persistent Memory
        memory_file = os.path.join(os.path.dirname(__file__), 'global_memory.txt')
        if os.path.exists(memory_file):
            with open(memory_file, "r", encoding="utf-8") as f:
                persistent_memory = f.read()
            if persistent_memory.strip():
                system_prompt += f"\n\nCRITICAL FACTS (LONG-TERM MEMORY):\n{persistent_memory}"

        # Inject Real-World Temporal Awareness
        temporal_state = calendar_agent.get_current_time_str()
        system_prompt += f"\n\nAKTUELL TID (Sverige): {temporal_state}\n\n*Notera: Om användaren ber dig lägga till något i kalendern ('nästa måndag', 'imorgon kl 15'), använd detta klockslag för att räkna ut rätt YYYY-MM-DD och anropa sedan `add_calendar_event`.*"

        messages = [{"role": "system", "content": system_prompt}]
        
        if history:
            # Append previous conversation context
            messages.extend(history)
            
        messages.append({"role": "user", "content": user_prompt})
        
        return self._route_request(self.cortex_model, messages, use_tools=True)

    def ask_muscle_coder(self, task_description: str, code_context: str) -> str:
        """
        Uses the Muscle model (e.g. DeepSeek-Coder, Qwen) for raw syntax generation or fast refactoring.
        """
        system_prompt = "You are an expert, precise code generator. Return strictly code implementing the requirements without markdown explanations."
        user_prompt = f"Context:\n{code_context}\n\nTask:\n{task_description}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        return self._route_request(self.muscle_coder, messages)

    def ask_watchdog(self, context_to_evaluate: str) -> bool:
        """
        Uses the local Watchdog model (e.g. local Ollama llama3) to evaluate if an action needs to be taken.
        Returns a boolean. This is free, allowing infinite heartbeat polling.
        """
        system_prompt = (
            "You are a watchdog evaluating system state. "
            "Reply EXPLICITLY with 'YES' if the context indicates action is required, or 'NO' if nominal."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context_to_evaluate}
        ]
        # Force lower temperature for deterministic true/false
        response = self._route_request(self.watchdog_model, messages, temperature=0.1)
        
        return "YES" in response.upper()

router = ModelOrchestrator()
