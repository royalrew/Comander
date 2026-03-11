import os
import sys
import time
import uuid
import boto3
from memory_module import memory_bank

def archive_to_r2(content: str, source_url: str, metadata: dict = None) -> bool:
    """Saves raw data (e.g., HTML) to Cloudflare R2 for auditability ("Zero Hallucination")."""
    try:
        r2_access_key = os.getenv("CLOUDFLARE_R2_ACCESS_KEY")
        r2_secret_key = os.getenv("CLOUDFLARE_R2_SECRET_KEY")
        bucket_name = os.getenv("CLOUDFLARE_R2_BUCKET_NAME", "hype-engine-media")
        
        if not r2_access_key or not r2_secret_key:
            print("R2 credentials not found. Skipping archive.")
            return False

        account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
        endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com" if account_id else None

        s3 = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=r2_access_key,
            aws_secret_access_key=r2_secret_key,
            region_name='auto' 
        )

        filename = f"archive/{uuid.uuid4().hex}.html"
        
        s3.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=content.encode('utf-8'),
            Metadata=metadata or {'source': source_url}
        )
        print(f"Archived raw content to R2: {filename}")
        return True
    except Exception as e:
        print(f"Failed to archive to R2: {e}")
        return False

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
