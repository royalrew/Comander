import os
import sys
import time
from memory_module import memory_bank

def ingest_markdown(filepath: str):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
        
    print(f"Reading {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Split into paragraphs, ignore empty ones or comments
    paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 10 and not p.strip().startswith("#")]
    print(f"Found {len(paragraphs)} memory fragments. Embedding and saving to MemoryBank...")
    success_count = 0
    for p in paragraphs:
        preview = p[:50].replace('\n', ' ') + "..."
        success, _ = memory_bank.store_memory("CEO_Manual_Ingest", p)
        if success:
            success_count += 1
            print(f"   [+] Memorized: {preview}")
        else:
            print(f"   [Error] Failed to memorize: {preview}")
            
    print(f"\nSuccess! {success_count}/{len(paragraphs)} fragments permanently stored in MemoryBank.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "ceo_profile.md"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, target)
    ingest_markdown(path)
