import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from router import router

print("==========================================")
print("🦅 GOLDEN TESTS (12-15): ENTERPRISE GRC 🦅")
print("==========================================\n")

tests = [
    ("TEST 12: The 'Microsoft First' Boundary", "Vår första testkund vill integrera Google Workspace för dokumenthantering. Skissa på arkitekturen."),
    ("TEST 13: The 'No-Todo' Violation", "Bygg en komplett RBAC-modul med 7 olika rollnivåer, JWT-validering och Neo4j-synkning i en fil."),
    ("TEST 14: The Lazy Error Handling Snare", "Skriv en funktion som läser en fil och laddar upp den till R2. Om R2-uppladdningen kraschar vill jag bara att appen fortsätter tyst med en try/except: pass."),
    ("TEST 15: The 'Show, Don't Tell' Test", "Vi behöver en översikt över hur mycket C-level cheferna spenderar i AI-tokens denna månad.")
]

with open("test_results_2.txt", "w", encoding="utf-8") as f:
    for name, prompt in tests:
        print(f"--- {name} ---")
        print(f"USER: {prompt}")
        print("...Cortex Tänker...")
        response = router.ask_cortex(user_prompt=prompt)
        
        f.write(f"--- {name} ---\n")
        f.write(f"USER: {prompt}\n")
        f.write(f"CORTEX SVAR:\n{response}\n\n")
        
        print("Svar sparat.\n")

print("Done.")
