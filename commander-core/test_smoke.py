import os
import asyncio
import boto3
import stripe
import psycopg2
from litellm import completion
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

async def test_openai():
    print("Testing OpenAI (LiteLLM)...")
    try:
        response = completion(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say 'LiteLLM OK'"}],
            max_tokens=10
        )
        print(f"✅ OpenAI: {response.choices[0].message.content.strip()}")
    except Exception as e:
        print(f"❌ OpenAI Error: {e}")

async def test_telegram():
    print("Testing Telegram Bot...")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    try:
        bot = Bot(token=token)
        me = await bot.get_me()
        print(f"✅ Telegram: Connected as @{me.username}")
        await bot.session.close()
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

def test_r2():
    print("Testing Cloudflare R2...")
    try:
        account_id = os.getenv("R2_ACCOUNT_ID")
        s3 = boto3.client(
            's3',
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY")
        )
        s3.list_buckets()
        print("✅ Cloudflare R2: Connection Successful")
    except Exception as e:
        print(f"❌ R2 Error: {e}")

def test_postgres():
    print("Testing PostgreSQL...")
    url = os.getenv("DATABASE_URL")
    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        ver = cur.fetchone()
        print(f"✅ Postgres: {ver[0]}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Postgres Error: {e}")

def test_stripe():
    print("Testing Stripe...")
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    try:
        acc = stripe.Account.retrieve()
        print(f"✅ Stripe: Connected to account {acc.id}")
    except Exception as e:
        print(f"❌ Stripe Error: {e}")

def test_memory_bank():
    print("Testing MemoryBank (PostgreSQL)...")
    from memory_module import memory_bank
    if memory_bank.enabled:
        count = memory_bank.count_memories()
        print(f"✅ MemoryBank: Connected and operational (Memories stored: {count})")
    else:
        print("❌ MemoryBank Error: Initialization failed. Check PostgreSQL connection and logs.")

async def run_all():
    print("=== COMMANDER SMOKE TEST ===\n")
    await test_openai()
    await test_telegram()
    test_r2()
    test_postgres()
    test_stripe()
    test_memory_bank()
    print("\n=== SMOKE TEST COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(run_all())
