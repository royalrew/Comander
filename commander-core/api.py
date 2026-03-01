from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

from cfo import cfo

app = FastAPI(title="Sintari Commander API", version="0.1.0")

# Allow the Next.js dashboard to access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
async def health_check():
    return {"status": "online", "pulse": "stable"}

@app.get("/api/v1/cfo/status")
async def get_cfo_status():
    """Returns real-time financial data from the CFO module."""
    return {
        "current_spend_usd": cfo.current_daily_spend,
        "max_spend_usd": cfo.max_daily_spend,
        "revenue_usd": 0.00, # Placeholder for Stripe integration
        "circuit_breaker_active": cfo.current_daily_spend > cfo.max_daily_spend
    }

@app.get("/api/v1/memory/recent")
async def get_recent_memory():
    """Returns the simulated recent memory log for the dashboard."""
    # In a full implementation, this queries OpenSearch and PostgreSQL
    return {
        "memory_items": [
            {
                "file": "master.prompt.md",
                "category": "System Regler",
                "tokens": 4520,
                "timestamp": "Idag 14:32"
            },
            {
                "file": "api_test_results.json",
                "category": "Verifiering",
                "tokens": 842,
                "timestamp": "Idag 10:15"
            },
            {
                "file": "ceo_profile.yaml",
                "category": "Kontext",
                "tokens": 120,
                "timestamp": "Igår"
            }
        ],
        "opensearch_usage_percent": 12,
        "postgres_active_sessions": 4
    }

@app.get("/api/v1/tools/status")
async def get_tools_status():
    """Returns the current state of the AI's autonomous tools."""
    # This will eventually map to a DB setting, hardcoded for UI testing
    return {
        "tools": [
            {
                "id": "file_observer",
                "name": "File Observer",
                "active": True,
                "module": "observer.py"
            },
            {
                "id": "the_surgeon",
                "name": "The Surgeon",
                "active": True,
                "module": "surgeon.py",
                "critical": True
            },
            {
                "id": "omni_scraper",
                "name": "Omni-Scraper",
                "active": False,
                "module": "scraper.py"
            }
        ],
        "allowed_domains": [
            "https://docs.microsoft.com/*",
            "https://stripe.com/docs/*",
            "https://nextjs.org/docs/*"
        ]
    }
