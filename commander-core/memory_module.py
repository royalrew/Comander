"""Memory Bank – PostgreSQL edition (no pgvector extension required).
Stores and retrieves AI memories using PostgreSQL with in-application cosine similarity.
Drop-in replacement for the previous OpenSearch-based implementation.

Strategy: 
- Embeddings are stored as JSON arrays in a TEXT column.
- On search, all embeddings are loaded and cosine similarity is computed in Python.
- This is highly performant for <10,000 memories (CEO single-user scenario).
"""

import os
import json
import logging
import uuid
import numpy as np
from datetime import datetime
from litellm import embedding
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMS = 1536


class MemoryBank:
    """Persistent vector memory using PostgreSQL with in-app similarity search.
    
    Provides the same interface as the previous OpenSearch-based MemoryBank:
    - store_memory(category, text) -> (bool, str)
    - search_memory(query, limit) -> list[dict]
    """

    def __init__(self):
        """Initializes the memory bank (PostgreSQL in prod, SQLite fallback in dev)."""
        try:
            from database import engine
            from sqlalchemy import text as sql_text

            self.engine = engine

            # Dialect-aware DDL so it works on both Postgres and SQLite (Railway is currently SQLite)
            dialect = engine.dialect.name
            if dialect == "sqlite":
                create_sql = """
                    CREATE TABLE IF NOT EXISTS memories (
                        id TEXT PRIMARY KEY,
                        text TEXT NOT NULL,
                        category VARCHAR(100) DEFAULT 'General',
                        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                        embedding TEXT
                    )
                """
            else:
                create_sql = """
                    CREATE TABLE IF NOT EXISTS memories (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        text TEXT NOT NULL,
                        category VARCHAR(100) DEFAULT 'General',
                        timestamp TIMESTAMPTZ DEFAULT NOW(),
                        embedding TEXT
                    )
                """

            # Create the memories table if it doesn't exist
            with engine.begin() as conn:
                conn.execute(sql_text(create_sql))

            logger.info(f"MemoryBank initialized with dialect='{dialect}' (in-app cosine similarity).")
            self.enabled = True
        except Exception as e:
            logger.error(f"Failed to initialize MemoryBank: {e}")
            self.enabled = False

    def _get_embedding(self, text: str) -> list[float]:
        """Generates an embedding vector for the given text using OpenAI."""
        try:
            response = embedding(model=EMBEDDING_MODEL, input=text)
            return response.data[0]['embedding']
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            return []

    @staticmethod
    def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
        """Computes cosine similarity between two vectors using numpy."""
        a = np.array(vec_a)
        b = np.array(vec_b)
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))

    def store_memory(self, category: str, text: str) -> tuple[bool, str]:
        """Embeds and saves a new fact to PostgreSQL. Returns (success, error_msg)."""
        if not self.enabled:
            return False, "Memory Bank is disabled (init failed)."

        vector = self._get_embedding(text)
        if not vector:
            return False, "Embedding failed via LiteLLM."

        try:
            from sqlalchemy import text as sql_text
            with self.engine.begin() as conn:
                conn.execute(
                    sql_text("""
                        INSERT INTO memories (id, text, category, timestamp, embedding)
                        VALUES (:id, :text, :category, :ts, :embedding)
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "text": text,
                        "category": category,
                        "ts": datetime.utcnow().isoformat(),
                        "embedding": json.dumps(vector)
                    }
                )
            return True, ""
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return False, str(e)

    def search_memory(self, query: str, limit: int = 5) -> list[dict]:
        """Performs a vector similarity search for relevant memories.
        
        Loads all embeddings from PostgreSQL and computes cosine similarity in Python.
        Highly efficient for <10,000 memories.
        """
        if not self.enabled:
            return []

        query_vec = self._get_embedding(query)
        if not query_vec:
            return []

        try:
            from sqlalchemy import text as sql_text
            with self.engine.connect() as conn:
                result = conn.execute(sql_text(
                    "SELECT id, text, category, timestamp, embedding FROM memories"
                ))
                rows = result.fetchall()

            # Compute cosine similarity for each memory
            scored = []
            for row in rows:
                mem_id, mem_text, mem_cat, mem_ts, mem_emb_json = row
                if not mem_emb_json:
                    continue
                try:
                    mem_vec = json.loads(mem_emb_json)
                    score = self._cosine_similarity(query_vec, mem_vec)
                    scored.append({
                        "text": mem_text,
                        "category": mem_cat,
                        "timestamp": mem_ts.isoformat() if mem_ts else None,
                        "score": score
                    })
                except (json.JSONDecodeError, ValueError):
                    continue

            # Sort by score descending and return top results
            scored.sort(key=lambda x: x["score"], reverse=True)
            return scored[:limit]

        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []

    def count_memories(self) -> int:
        """Returns the total number of stored memories."""
        if not self.enabled:
            return 0
        try:
            from sqlalchemy import text as sql_text
            with self.engine.connect() as conn:
                result = conn.execute(sql_text("SELECT COUNT(*) FROM memories"))
                return result.scalar() or 0
        except Exception as e:
            logger.error(f"Failed to count memories: {e}")
            return 0


memory_bank = MemoryBank()
