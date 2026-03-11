"""Intelligence Data Ingestor — Postgres + JSONB Edition (no pgvector).

Reads scraped JSON files from the Safe Zone, extracts readable content,
generates embeddings via LiteLLM, and stores everything in Railway Postgres
with JSONB for exact structural queries and in-app cosine similarity for search.

Uses the same embedding-as-TEXT strategy as memory_module.py since Railway
Postgres does not have the pgvector extension installed.

Usage:
    from modules.ingest_postgres import ingest_directory, search_intel

    # Ingest all JSON from a mission
    stats = ingest_directory("C:/path/to/intel/competitors/2026-03-07", mission_id="operation_glass_house")

    # Hybrid search: semantic + JSONB
    results = search_intel("competitors using Stripe", limit=5)
"""

import os
import json
import logging
import uuid
import numpy as np
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from litellm import embedding
from sqlalchemy import text as sql_text

load_dotenv()
logger = logging.getLogger("IntelIngest")
logger.setLevel(logging.INFO)

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMS = 1536


def _get_engine():
    """Lazily imports the shared SQLAlchemy engine from database.py.

    Returns:
        sqlalchemy.engine.Engine: The shared database engine.

    Raises:
        ImportError: If database module is not available.
    """
    from database import engine
    return engine


def ensure_schema():
    """Creates the intelligence_data table if it doesn't exist.

    This is idempotent — safe to call on every startup.

    Returns:
        bool: True if schema was ensured successfully, False otherwise.
    """
    engine = _get_engine()
    try:
        with engine.begin() as conn:
            conn.execute(sql_text("""
                CREATE TABLE IF NOT EXISTS intelligence_data (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    source_url TEXT,
                    mission_id VARCHAR(100),
                    scraped_at TIMESTAMPTZ DEFAULT NOW(),
                    content TEXT NOT NULL,
                    embedding TEXT,
                    raw_data JSONB
                );
            """))

            # Create an index for fast JSONB containment queries
            conn.execute(sql_text("""
                CREATE INDEX IF NOT EXISTS idx_intel_raw_data_gin
                ON intelligence_data USING GIN (raw_data);
            """))

            # Index on mission_id for fast filtering
            conn.execute(sql_text("""
                CREATE INDEX IF NOT EXISTS idx_intel_mission_id
                ON intelligence_data (mission_id);
            """))

        logger.info("Schema ensured: intelligence_data table + JSONB index ready.")
        return True
    except Exception as e:
        logger.error(f"Schema creation failed: {e}")
        return False


def _generate_embedding(text: str) -> list[float]:
    """Generates an embedding vector for the given text using OpenAI via LiteLLM.

    Args:
        text: The text to embed. Will be truncated to 8000 chars to stay within token limits.

    Returns:
        list[float]: The embedding vector (1536 dimensions), or empty list on failure.
    """
    try:
        truncated = text[:8000]
        response = embedding(model=EMBEDDING_MODEL, input=truncated)
        return response.data[0]["embedding"]
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        return []


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Computes cosine similarity between two vectors using numpy.

    Args:
        vec_a: First embedding vector.
        vec_b: Second embedding vector.

    Returns:
        float: Cosine similarity score between 0 and 1.
    """
    a = np.array(vec_a)
    b = np.array(vec_b)
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


def extract_content(json_data: dict, source_file: str = "") -> str:
    """Extracts human-readable text from a raw JSON payload for RAG context.

    Handles multiple JSON structures: OneTrust configs, generic API responses,
    and nested objects. Prioritizes names, descriptions, and labels.

    Args:
        json_data: The parsed JSON dictionary.
        source_file: The originating filename (for context).

    Returns:
        str: A readable text summary of the JSON content.
    """
    parts = [f"Source: {source_file}"]

    interesting_keys = {
        "name", "description", "groupname", "groupdescription", "hostname",
        "displayname", "maintext", "maininfotext", "alertnoticetext",
        "cookiesettingbuttontext", "aboutcookiestext", "privacypolicy",
        "host", "category", "title", "label", "text", "message",
        "status", "type", "url", "pricing", "price", "cost", "tier",
        "plan", "feature", "product", "service",
    }

    def _walk(obj, depth=0):
        """Recursively extracts interesting string values from nested structures."""
        if depth > 5:
            return
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and len(value) > 3:
                    if key.lower() in interesting_keys:
                        parts.append(f"{key}: {value[:500]}")
                elif isinstance(value, (dict, list)):
                    _walk(value, depth + 1)
        elif isinstance(obj, list):
            for item in obj[:50]:
                _walk(item, depth + 1)

    _walk(json_data)

    if len(parts) <= 1:
        raw_str = json.dumps(json_data, ensure_ascii=False)[:2000]
        parts.append(f"Raw content: {raw_str}")

    return "\n".join(parts)


def ingest_directory(intel_dir: str, mission_id: str = "unknown") -> dict:
    """Ingests all JSON files from a directory into Postgres.

    Walks the directory, parses each .json file, extracts content, generates
    embeddings, and inserts rows into the intelligence_data table.

    Args:
        intel_dir: Absolute path to the directory containing JSON files.
        mission_id: Identifier for the mission (e.g., 'operation_glass_house').

    Returns:
        dict: Statistics with keys 'total_files', 'ingested', 'skipped', 'errors'.
    """
    ensure_schema()
    engine = _get_engine()

    intel_path = Path(intel_dir)
    if not intel_path.exists():
        logger.error(f"Directory not found: {intel_dir}")
        return {"total_files": 0, "ingested": 0, "skipped": 0, "errors": 1}

    json_files = list(intel_path.glob("**/*.json"))
    stats = {"total_files": len(json_files), "ingested": 0, "skipped": 0, "errors": 0}

    logger.info(f"Starting ingest of {len(json_files)} JSON files from {intel_dir} (mission: {mission_id})")

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                raw_text = f.read()

            # Skip tiny files (healthchecks, empty responses)
            if len(raw_text) < 20:
                stats["skipped"] += 1
                continue

            json_data = json.loads(raw_text)

            # Extract readable content for RAG
            content = extract_content(json_data, source_file=json_file.name)

            # Skip if extraction yielded nothing useful
            if len(content) < 50:
                stats["skipped"] += 1
                continue

            # Generate embedding
            emb_vector = _generate_embedding(content)
            if not emb_vector:
                logger.warning(f"Skipping {json_file.name}: embedding failed")
                stats["errors"] += 1
                continue

            # Sanitize JSON for Postgres JSONB (strip null bytes, cap size)
            raw_json_str = json.dumps(json_data, ensure_ascii=False)
            raw_json_str = raw_json_str.replace("\u0000", "")
            if len(raw_json_str) > 500_000:
                raw_json_str = json.dumps({"_truncated": True, "_original_size": len(raw_json_str)})

            # Insert into Postgres
            with engine.begin() as conn:
                conn.execute(
                    sql_text("""
                        INSERT INTO intelligence_data (id, source_url, mission_id, scraped_at, content, embedding, raw_data)
                        VALUES (:id, :source_url, :mission_id, :scraped_at, :content, :embedding, CAST(:raw_data AS jsonb))
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "source_url": json_file.name,
                        "mission_id": mission_id,
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                        "content": content,
                        "embedding": json.dumps(emb_vector),
                        "raw_data": raw_json_str,
                    }
                )

            stats["ingested"] += 1
            logger.info(f"Ingested: {json_file.name} ({len(content)} chars)")

        except json.JSONDecodeError:
            logger.warning(f"Skipping non-JSON file: {json_file.name}")
            stats["skipped"] += 1
        except Exception as e:
            logger.error(f"Failed to ingest {json_file.name}: {e}")
            stats["errors"] += 1

    logger.info(f"Ingest complete: {stats}")
    return stats


def search_intel(
    query: str,
    limit: int = 5,
    mission_id: Optional[str] = None,
) -> list[dict]:
    """Hybrid search: semantic similarity (in-app cosine) + JSONB.

    Loads all intelligence rows (optionally filtered by mission_id), computes
    cosine similarity in Python, and returns the top results.

    Args:
        query: Natural language search query.
        limit: Maximum number of results to return.
        mission_id: Optional filter by mission identifier.

    Returns:
        list[dict]: Ranked results with keys: id, source_url, mission_id,
                    content_preview, similarity_score.
    """
    engine = _get_engine()

    query_vec = _generate_embedding(query)
    if not query_vec:
        return []

    # Build query
    if mission_id:
        sql = "SELECT id, source_url, mission_id, LEFT(content, 500), embedding FROM intelligence_data WHERE mission_id = :mid"
        params = {"mid": mission_id}
    else:
        sql = "SELECT id, source_url, mission_id, LEFT(content, 500), embedding FROM intelligence_data"
        params = {}

    try:
        with engine.connect() as conn:
            result = conn.execute(sql_text(sql), params)
            rows = result.fetchall()

        scored = []
        for row in rows:
            row_id, source_url, mid, content_preview, emb_json = row
            if not emb_json:
                continue
            try:
                row_vec = json.loads(emb_json)
                score = _cosine_similarity(query_vec, row_vec)
                scored.append({
                    "id": str(row_id),
                    "source_url": source_url,
                    "mission_id": mid,
                    "content_preview": content_preview,
                    "similarity_score": round(score, 4),
                })
            except (json.JSONDecodeError, ValueError):
                continue

        scored.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored[:limit]

    except Exception as e:
        logger.error(f"Intel search failed: {e}")
        return []


def count_intel(mission_id: Optional[str] = None) -> int:
    """Returns the total count of intelligence records, optionally filtered by mission.

    Args:
        mission_id: Optional filter to count records for a specific mission.

    Returns:
        int: Number of intelligence records.
    """
    engine = _get_engine()
    try:
        with engine.connect() as conn:
            if mission_id:
                result = conn.execute(
                    sql_text("SELECT COUNT(*) FROM intelligence_data WHERE mission_id = :mid"),
                    {"mid": mission_id}
                )
            else:
                result = conn.execute(sql_text("SELECT COUNT(*) FROM intelligence_data"))
            return result.scalar() or 0
    except Exception as e:
        logger.error(f"Count failed: {e}")
        return 0
