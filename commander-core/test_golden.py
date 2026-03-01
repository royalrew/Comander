import os
import sys
from dotenv import load_dotenv

# Ensure we can import commander-core modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from router import router

print("==========================================")
print("🦅 GOLDEN TESTS: THE RE-ACT LOOP 🦅")
print("==========================================\n")

# TEST 3: Självinsikt (Observer tool call validation)
print("--- TEST 3: Självinsikt (Observer Tool) ---")
prompt_3 = "Vad heter filerna i 'commander-core' mappen? Lista dem för mig."
print(f"USER: {prompt_3}")
print("...Cortex Tänker (Tool Calling)...")
response_3 = router.ask_cortex(user_prompt=prompt_3)
print(f"CORTEX SVAR: \n{response_3}\n")

# TEST 11: The Tech Stack Trap
print("--- TEST 11: The Tech Stack Trap ---")
prompt_11 = "Jag tänkte att vi bygger nästa del av RAG-pipelinen med MongoDB och Vue.js för att snabba på. Skriv uppsättningskoden."
print(f"USER: {prompt_11}")
print("...Cortex Tänker...")
response_11 = router.ask_cortex(user_prompt=prompt_11)
print(f"CORTEX SVAR: \n{response_11}\n")

# TEST 4: Kirurgen (Surgeon)
print("--- TEST 4: Kirurgen (Surgeon refactor tool call) ---")
prompt_4 = "Skapa en ny fil som heter 'test_agent.py' inuti 'commander-core' och lägg in en funktion som skriver ut 'Hello World'. Verifiera att det fungerar."
print(f"USER: {prompt_4}")
print("...Cortex Tänker (Surgeon Tool Calling)...")
response_4 = router.ask_cortex(user_prompt=prompt_4)
print(f"CORTEX SVAR: \n{response_4}\n")

print("\n--- TEST RUN COMPLETE ---")
