import os
import logging
from opensearchpy import OpenSearch
from litellm import embedding
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

OPENSEARCH_URL = os.getenv("OPENSEARCH_URL")
OPENSEARCH_USERNAME = os.getenv("OPENSEARCH_USERNAME")
OPENSEARCH_PWD = os.getenv("OPENSEARCH_PWD")
INDEX_NAME = os.getenv("OPENSEARCH_INDEX_NAME", "commander_core_memory")
EMBEDDING_MODEL = "text-embedding-3-small"

class MemoryBank:
    def __init__(self):
        if not OPENSEARCH_URL:
            logger.warning("OPENSEARCH_URL is not set. Memory Bank will be disabled.")
            self.client = None
            return

        host = OPENSEARCH_URL.replace("https://", "").replace("http://", "")
        port = 443
        if ":" in host:
            host, port_str = host.split(":")
            port = int(port_str.split("/")[0])

        self.client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_auth=(OPENSEARCH_USERNAME, OPENSEARCH_PWD),
            use_ssl=True,
            verify_certs=True,
            ssl_show_warn=False
        )
        self._ensure_index()

    def _ensure_index(self):
        """Creates the k-NN index if it doesn't already exist."""
        if not self.client: return
        
        try:
            if not self.client.indices.exists(index=INDEX_NAME):
                index_body = {
                    "settings": {
                        "index": {
                            "knn": True,
                            "knn.algo_param.ef_search": 100
                        }
                    },
                    "mappings": {
                        "properties": {
                            "text": {"type": "text"},
                            "category": {"type": "keyword"},
                            "timestamp": {"type": "date"},
                            "embedding": {
                                "type": "knn_vector",
                                "dimension": 1536,
                                "method": {
                                    "name": "hnsw",
                                    "space_type": "cosinesimil",
                                    "engine": "lucene"
                                }
                            }
                        }
                    }
                }
                self.client.indices.create(index=INDEX_NAME, body=index_body)
                logger.info(f"Created OpenSearch Index: {INDEX_NAME}")
        except Exception as e:
            logger.error(f"Failed to ensure OpenSearch Index: {e}")

    def _get_embedding(self, text: str) -> list[float]:
        try:
            # Uses OPENAI_API_KEY from environment
            response = embedding(model=EMBEDDING_MODEL, input=text)
            return response.data[0]['embedding']
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            return []

    def store_memory(self, category: str, text: str) -> bool:
        """Embeds and saves a new fact to OpenSearch."""
        if not self.client: return False
        
        vector = self._get_embedding(text)
        if not vector: return False
        
        from datetime import datetime
        doc = {
            "text": text,
            "category": category,
            "timestamp": datetime.utcnow().isoformat(),
            "embedding": vector
        }
        
        try:
            self.client.index(index=INDEX_NAME, body=doc, refresh=True)
            return True
        except Exception as e:
            logger.error(f"Failed to store memory to OpenSearch: {e}")
            return False

    def search_memory(self, query: str, limit: int = 5) -> list[dict]:
        """Performs a vector similarity search for relevant memories."""
        if not self.client: return []
        
        vector = self._get_embedding(query)
        if not vector: return []
        
        search_query = {
            "size": limit,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": vector,
                        "k": limit
                    }
                }
            },
            "_source": ["text", "category", "timestamp"]
        }
        
        try:
            response = self.client.search(index=INDEX_NAME, body=search_query)
            hits = response["hits"]["hits"]
            return [hit["_source"] for hit in hits]
        except Exception as e:
            logger.error(f"Failed to search OpenSearch: {e}")
            return []

memory_bank = MemoryBank()
