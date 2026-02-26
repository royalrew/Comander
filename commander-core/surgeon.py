import subprocess
from .io_jail import write_file, read_file
from .router import router

class Surgeon:
    """
    Action Gateway taking directives from the Cortex Router and implementing them using
    the Muscle models. Modifies code in the Active Missions directly.
    """
    def __init__(self):
        # We enforce a strict max retry loop on self-correction
        self.max_retries = 3

    def refactor_file(self, filepath: str, objective: str) -> bool:
        """
        Reads a file, sends it to the Muscle Coder with an objective, 
        and rewrites it if successful.
        """
        try:
            original_code = read_file(filepath)
            
            # Using Muscle model for pure code syntax replacement
            new_code = router.ask_muscle_coder(
                task_description=f"Refactor this file to achieve: {objective}",
                code_context=original_code
            )
            
            # Very basic extraction (Muscle is prompted to output strictly code)
            # A real implementation would parse markdown fences if the model disobeys
            if "```" in new_code:
                lines = new_code.split('\n')
                code_lines = []
                in_block = False
                for line in lines:
                    if line.startswith('```'):
                        in_block = not in_block
                        continue
                    if in_block:
                        code_lines.append(line)
                new_code = '\n'.join(code_lines)
            
            # Write back via the IO Jail ensuring zero-trust boundary
            write_file(filepath, new_code)
            return True
            
        except Exception as e:
            print(f"Surgeon failed to refactor {filepath}: {e}")
            return False

    def validate_code(self, filepath: str, command: list[str]) -> bool:
        """
        Runs a local shell command (e.g. `pytest` or `npm run lint`) to validate the new code.
        CRITICAL SECURITY: `shell=True` is explicitly disabled to prevent injection.
        """
        retries = 0
        while retries < self.max_retries:
            try:
                # `command` must be a list of explicit args, e.g. ['pytest', 'tests/test_file.py']
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=30,  # 30 second hard cap
                    shell=False  # ZERO-TRUST: Mandatory False
                )
                
                if result.returncode == 0:
                    return True
                else:
                    # Self-correction loop
                    error_log = result.stderr or result.stdout
                    print(f"Validation failed (Attempt {retries+1}). Passing to Muscle for correction...")
                    
                    prompt = f"The following code failed validation via command `{' '.join(command)}`:\n\nError Log:\n{error_log}\n\nFix it."
                    self.refactor_file(filepath, prompt)
                    
                    retries += 1
                    
            except subprocess.TimeoutExpired:
                print("Validation command timed out.")
                break
            except Exception as e:
                print(f"Validation execution failed: {e}")
                break
                
        return False

surgeon = Surgeon()
