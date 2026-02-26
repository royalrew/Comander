import os
from pathlib import Path
from tree_sitter import Language, Parser
from io_jail import read_file, list_files

# Note: Tree-sitter setup in real environments requires compiling the shared objects (.so / .dll).
# We are creating a mock wrapper that assumes the languages are available.

class DeterministicObserver:
    """
    Observer module utilizing tree-sitter for deterministic code extraction.
    Ensures factual grounding before the Cortex model makes routing decisions.
    """
    def __init__(self):
        # In a full implementation, you'd load the compiled language files:
        # e.g., Language.build_library('build/my-languages.so', ['tree-sitter-python'])
        # self.PY_LANGUAGE = Language('build/my-languages.so', 'python')
        # self.TS_LANGUAGE = Language('build/my-languages.so', 'typescript')
        pass

    def analyze_python_file(self, filepath: str) -> dict:
        """
        Parses a target Python file and extracts function signatures and docstrings.
        Uses the zero-trust IO jail to read the file.
        """
        try:
            content = read_file(filepath)
            # Placeholder logic for tree-sitter AST queries
            # We would use a Query: `(function_definition name: (identifier) @name)`
            return {"file": filepath, "status": "Observer AST parsing mock (Python)", "content_length": len(content)}
        except Exception as e:
            return {"error": str(e)}

    def analyze_typescript_file(self, filepath: str) -> dict:
        """
        Parses a Next.js / React TypeScript file to identify React Components
        and Hooks for the Surgeon.
        """
        try:
            content = read_file(filepath)
            # Placeholder logic for tree-sitter AST queries
            return {"file": filepath, "status": "Observer AST parsing mock (TypeScript)", "content_length": len(content)}
        except Exception as e:
            return {"error": str(e)}

    def scan_active_mission(self, mission_name: str) -> list[str]:
        """
        Scans a specific mission directory for code files using the IO Jail.
        """
        try:
            # We use the IO jail to strictly list files in the target subfolder
            all_files = list_files(mission_name)
            return [f for f in all_files if f.endswith('.py') or f.endswith('.ts') or f.endswith('.tsx')]
        except Exception as e:
            print(f"Error scanning mission {mission_name}: {e}")
            return []

observer = DeterministicObserver()
