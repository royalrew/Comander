import os
from litellm import completion
from dotenv import load_dotenv
from .cfo import cfo, TokenLimitExceeded

load_dotenv()

class ModelOrchestrator:
    """
    Handles Multi-Model Routing via LiteLLM.
    Ensures Cortex models handle complex tasks and Muscle models handle simple/syntax tasks.
    Enforces cost-tracking via the CFO module.
    """
    def __init__(self):
        self.cortex_model = os.getenv("CORTEX_MODEL", "gpt-4o")
        self.muscle_coder = os.getenv("MUSCLE_CODER_MODEL", "deepseek-coder")
        self.watchdog_model = os.getenv("WATCHDOG_MODEL", "ollama/llama3")

    def _route_request(self, model_choice: str, messages: list[dict], **kwargs) -> str:
        """
        Internal wrapper around LiteLLM completion to handle standardized error reporting,
        retries, and CFO cost routing.
        """
        try:
            # Route to Litellm
            # litellm will use the API keys matching the provider string in model_choice
            response = completion(model=model_choice, messages=messages, **kwargs)
            
            # Extract usage metrics for CFO
            if hasattr(response, 'usage'):
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                cost = cfo.estimate_cost(prompt_tokens, completion_tokens, model_choice)
                cfo.add_cost(cost)
                
            return response.choices[0].message.content
            
        except TokenLimitExceeded as e:
            # Circuit Breaker triggered
            print(f"ROUTER BLOCKED: {e}")
            return "ERROR: FINANCIAL CIRCUIT BREAKER. Daily spend limit reached."
        except Exception as e:
            print(f"LiteLLM Error with model {model_choice}: {e}")
            return f"ERROR: Model generation failed. Details: {e}"

    def ask_cortex(self, system_prompt: str, user_prompt: str) -> str:
        """
        Uses the Cortex model (e.g. GPT-4o) for high-level reasoning, vision, or complex architecture decisions.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        return self._route_request(self.cortex_model, messages)

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
