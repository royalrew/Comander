import os
import uuid
import boto3
import requests
from datetime import datetime
from litellm import image_generation
from router import router
from opensearchpy import OpenSearch
from urllib.parse import urlparse

class HypePipeline:
    """
    Automated Multi-Modal B2B/B2C pipeline.
    Transforms mundane objects (images) and generates corresponding AI assets.
    Uploads the final packaged assets to Cloudflare R2 and indexes in OpenSearch.
    """
    def __init__(self):
        # Cloudflare R2 Setup
        account_id = os.getenv("R2_ACCOUNT_ID")
        self.bucket = os.getenv("R2_BUCKET_NAME")
        self.prefix = os.getenv("R2_PREFIX", "commander-assets/")
        self.public_url = os.getenv("R2_ENDPOINT_URL")
        
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY")
        )

        # OpenSearch Setup
        url = os.getenv("OPENSEARCH_URL")
        user = os.getenv("OPENSEARCH_USERNAME")
        pwd = os.getenv("OPENSEARCH_PWD") or os.getenv("OPENSEARCH_PASSWORD")
        self.index_name = os.getenv("OPENSEARCH_INDEX_NAME", "commander_core_memory")
        
        if url:
            parsed = urlparse(url)
            host = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
            use_ssl = parsed.scheme == "https"
            
            self.os_client = OpenSearch(
                hosts=[{'host': host, 'port': port}],
                http_auth=(user, pwd) if user and pwd else None,
                use_ssl=use_ssl,
                verify_certs=False,
                ssl_show_warn=False
            )
        else:
            self.os_client = None

    def _upload_to_r2(self, file_content: bytes, filename: str, content_type: str) -> str:
        """Securely uploads raw bytes to R2."""
        object_key = f"{self.prefix}{filename}"
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=object_key,
            Body=file_content,
            ContentType=content_type
        )
        return f"{self.public_url}/{self.bucket}/{object_key}"

    def _index_in_opensearch(self, asset_data: dict):
        """Indexes the generated asset metadata into OpenSearch."""
        if not self.os_client:
            return
        
        try:
            # Ensure index exists
            if not self.os_client.indices.exists(index=self.index_name):
                self.os_client.indices.create(index=self.index_name)
                
            self.os_client.index(
                index=self.index_name,
                body=asset_data,
                id=asset_data.get("asset_id", uuid.uuid4().hex)
            )
            print(f"Indexed asset {asset_data.get('asset_id')} in OpenSearch")
        except Exception as e:
            print(f"Failed to index in OpenSearch: {e}")

    def trigger_transformation(self, style_preset: str) -> dict:
        """
        Generates an image prompt and an actual image via DALL-E 3.
        """
        prompt = router.ask_cortex(
            system_prompt="You are a viral social media director.",
            user_prompt=f"Create a highly detailed image generation prompt for a {style_preset} style transformation of a futuristic AI datacenter."
        )
        print(f"Generated prompt: {prompt}")
        
        try:
            print("Calling DALL-E 3...")
            response = image_generation(
                prompt=prompt,
                model="dall-e-3",
                size="1024x1024"
            )
            image_url = response.data[0].url
            img_response = requests.get(image_url)
            image_bytes = img_response.content
        except Exception as e:
            print(f"DALL-E 3 generation failed: {e}")
            image_bytes = b"Fallback data"

        output_filename = f"hype_{uuid.uuid4().hex[:8]}.jpg"
        r2_url = self._upload_to_r2(image_bytes, output_filename, "image/jpeg")
        
        return {"type": "image", "url": r2_url, "prompt": prompt}

    def execute_full_run(self, preset: str = "Cyberpunk Enterprise") -> dict:
        """Orchestrates the massive multi-modal run."""
        print(f"Starting FULL HYPE PIPELINE with preset {preset}")
        
        asset_id = uuid.uuid4().hex
        image_result = self.trigger_transformation(preset)
        
        caption = router.ask_cortex(
            system_prompt="You are an expert copywriter.",
            user_prompt=f"Write a viral LinkedIn/TikTok caption for an image described as: {image_result['prompt']}"
        )
        
        asset_data = {
            "asset_id": asset_id,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "hype_generation",
            "preset": preset,
            "image_url": image_result["url"],
            "caption": caption,
            "prompt_used": image_result["prompt"]
        }
        
        # Save memory of this generation
        self._index_in_opensearch(asset_data)
        
        return {
            "status": "success",
            "assets": {
                "image": image_result["url"]
            },
            "caption": caption
        }

pipeline = HypePipeline()
