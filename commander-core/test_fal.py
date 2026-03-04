import os
import asyncio
import fal_client

os.environ["FAL_KEY"] = "2c38c430-a6b0-49e4-8c07-0a7430e7e730:556337add54b22894d2798acbdc2546c"

async def test_minimax():
    print("Testing Fal.ai temporary file upload for Minimax...")
    try:
        import base64
        b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAZdEVYdFNvZnR3YXJlAHBhaW50Lm5ldCA0LjAuMTnU1rJ9AAAADUlEQVQYV2P4//8/AwAI/AL+XFhO0wAAAABJRU5ErkJggg=="
        image_bytes = base64.b64decode(b64)
        
        url = await fal_client.upload_async(image_bytes, "image/png")
        print("Upload Success:", url)
        
        result = await fal_client.subscribe_async(
            "fal-ai/minimax-video",
            arguments={
                "image_url": url,
                "prompt": "A cool ski hoverboard"
            }
        )
        print("Minimax Success:", result)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(test_minimax())
