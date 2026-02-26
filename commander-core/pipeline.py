import os
import uuid
import boto3
from .router import router

class HypePipeline:
    """
    Automated Multi-Modal B2B/B2C pipeline.
    Transforms mundane objects (images) and generates corresponding AI music.
    Uploads the final packaged assets to Cloudflare R2 for social media (Reels/TikTok).
    """
    def __init__(self):
        # Cloudflare R2 Setup (S3 Compatible API)
        account_id = os.getenv("R2_ACCOUNT_ID")
        self.bucket = os.getenv("R2_BUCKET_NAME")
        self.prefix = os.getenv("R2_PREFIX", "commander-assets/")
        
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY")
        )

    def _upload_to_r2(self, file_content: bytes, filename: str, content_type: str) -> str:
        """Securely uploads raw bytes to R2 under the locked prefix."""
        object_key = f"{self.prefix}{filename}"
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=object_key,
            Body=file_content,
            ContentType=content_type
        )
        return f"s3://{self.bucket}/{object_key}"

    def trigger_transformation(self, image_path: str, style_preset: str) -> dict:
        """
        Takes a base image, applies a transformation prompt via the Cortex Vision model,
        and returns the R2 URL of the resulting generated image.
        """
        # 1. Ask Cortex for the exact Image Generation Prompt based on style
        prompt = router.ask_cortex(
            system_prompt="You are a viral social media director.",
            user_prompt=f"Create an image generation prompt for a {style_preset} style transformation of the attached image context."
        )
        
        print(f"Hype Pipeline generated prompt: {prompt}")
        
        # 2. Trigger Image Model (e.g. DALL-E 3, Midjourney API, or local Stable Diffusion)
        # Note: Litellm requires specific `litellm.image_generation` routing. We mock the bytes here.
        mock_image_bytes = b"mock_image_data_based_on_prompt"
        
        # 3. Upload to R2
        output_filename = f"hype_{uuid.uuid4().hex[:8]}.jpg"
        r2_url = self._upload_to_r2(mock_image_bytes, output_filename, "image/jpeg")
        
        return {"type": "image", "url": r2_url, "prompt": prompt}

    def trigger_audio(self, visual_context: str) -> dict:
        """
        Generates corresponding AI music perfectly synched to the visual vibe.
        """
        # 1. Ask Cortex for audio prompt
        prompt = router.ask_cortex(
            system_prompt="You are an audio engineer matching generative beats to viral visuals.",
            user_prompt=f"Create a Suno/Udio prompt matching this vibe: {visual_context}"
        )
        
        # 2. Trigger Audio API (Suno / Udio Placeholder)
        mock_audio_bytes = b"mock_mp3_data_based_on_audio_prompt"
        
        # 3. Upload to R2
        output_filename = f"beat_{uuid.uuid4().hex[:8]}.mp3"
        r2_url = self._upload_to_r2(mock_audio_bytes, output_filename, "audio/mpeg")
        
        return {"type": "audio", "url": r2_url, "prompt": prompt}

    def execute_full_run(self, original_image_path: str, preset: str = "Real Estate 80s Retro") -> dict:
        """
        Orchestrates the massive multi-modal run and packages it.
        """
        print(f"Starting FULL HYPE PIPELINE for {original_image_path} with preset {preset}")
        image_result = self.trigger_transformation(original_image_path, preset)
        audio_result = self.trigger_audio(image_result["prompt"])
        
        return {
            "status": "success",
            "assets": {
                "image": image_result["url"],
                "audio": audio_result["url"]
            },
            "suggested_caption": router.ask_cortex(
                system_prompt="You are an expert copywriter.",
                user_prompt=f"Write a viral TikTok caption for an image described as: {image_result['prompt']} and beat: {audio_result['prompt']}"
            )
        }

pipeline = HypePipeline()
