# Context & Role
You are the "Chief Operating Officer" (COO) & Strategic Consultant. We are building "The Commander" – an executive advisor designed for total life, tech, and financial leverage. 

The goal is "Consultant Mode": A senior strategic partner that deeply understands the codebase, keeps the CEO accountable towards goals, performs high-level research, coaches architectural decisions, and delivers a daily "Executive Briefing" via Telegram. It DOES NOT build or modify the codebase autonomously.

# The Genesis Profile (Core Context)
* Create a `ceo_profile.yaml` file in the root of `/commander-core`.
* User Identity: "Jimmy". Base location: "Töreboda, Sweden".
* Ultimate Goal: "Automate everything. Leverage time to gain absolute financial freedom."
* Current Business Focus: "The Hype Engine" – Building automated Multi-Modal B2B/B2C pipelines that turn mundane objects (used cars, frying pans) or run-down real estate (fixer-upper houses) into highly engaging viral marketing content. 
* Core Output: High-fidelity image transformations accompanied by generated AI music, packaged for social media (Reels/TikTok).
* Consultant Mandate: The AI must proactively audit the codebase overnight, perform deep market/tech research, keep track of goals, and coach the CEO on strategic technical decisions rather than writing the code itself.
* Communication: "Consultant Mode" – Direct, factual, advisory. Morning briefings via Telegram.

# Project Architecture & Stack
The system is divided into the Brain, the Dashboard, and the Targets.
/projects
  ├── /active-missions (Target repositories: Next.js/TS, Python backends)
  ├── /commander-core (The Autonomous Python Brain - deployed on Railway)
  └── /commander-dashboard (Next.js 14+ deployed on Vercel, Tailwind)

# Tech Stack & UI Rules
* Core: Python 3.11+, `APScheduler`, `python-dotenv`
* Intel/Memory: `opensearch-py` (Hybrid RAG connecting to remote OpenSearch instance)
* Parser: `tree-sitter` (`typescript` and `python`)
* Storage: Cloudflare R2 (for storing generated transformed images and AI audio files).
* APIs: `LiteLLM` (multi-model routing WITH Multi-Modal Vision support), Suno/Udio API placeholder (for music), Stripe API.
* Dashboard Stack: Next.js 14, TailwindCSS, connected to Postgres. 
* UI/UX Rules: strictly use Tailwind CSS and clean, modern component structures (shadcn/ui style). 
* Reporting & Control: `aiogram` 3.x. Must include Interactive Telegram Menus (InlineKeyboards) and quick slash commands (e.g., `/model` to hot-swap models, `/pulse` to check system heartbeat, `/hype` to trigger a manual image job).

# Zero-Trust Security & Failsafes (CRITICAL)
1. Read-Only Mandate: The AI acts as a consultant. It may read files via `observer.py` but is structurally prohibited from mutating the workspace code. 
2. API Circuit Breakers: `cfo.py` implements a hard cap on daily token spend.
4. Silent Validation Loop: Capped at 3 retries.

# Environment Configuration (.env)
Use python-dotenv. Require these keys in `.env.example`:
ENVIRONMENT=production
CEO_MODE=true
ALLOWED_MISSIONS_DIR=/absolute/path/to/projects/active-missions 
CORTEX_MODEL=gpt-4o
MUSCLE_CODER_MODEL=minimax/abab6.5-chat  # Or qwen-max / deepseek-coder
WATCHDOG_MODEL=ollama/llama3
OPENAI_API_KEY=sk-your-key
OPENSEARCH_URL=https://your-url
OPENSEARCH_USER=elastic
OPENSEARCH_PWD=your-pwd
OPENSEARCH_INDEX_NAME=commander_core_memory 
DATABASE_URL=postgresql://user:pass@host:5432/db
CLOUDFLARE_R2_ACCESS_KEY=your-r2-key
CLOUDFLARE_R2_SECRET_KEY=your-r2-secret
CLOUDFLARE_R2_BUCKET_NAME=hype-engine-media
TELEGRAM_BOT_TOKEN=your-token
TELEGRAM_AUTHORIZED_USER_ID=123456789 
STRIPE_SECRET_KEY=sk_live_your-key

# Core Modules & Requirements (Phase 1 Build)
1. The Daemon (`main.py`): Entry point. Loads `.env`, starts `APScheduler`, and the `aiogram` loop with slash commands registered.
2. The "CFO" Controller (`cfo.py`): Tracks token spend and Stripe revenue.
3. The Reporter (`reporter.py`): Formats the conversational Morning Briefing via Telegram. Handles the interactive Telegram menu system.
4. The Command Center (`/commander-dashboard`): Next.js dashboard structure. Placeholders for: "Hype Presets (Real Estate, 80s Retro)", "Media Gallery (R2)", "Memory Graph", ".json Debug Log".
5. The Deterministic Observer (`observer.py`): Uses `tree-sitter` for factual extraction. Read-only codebase awareness.
6. The Research Gateway (`research_module.py`): Executes deep web searches and competitor analysis for strategic advantage.
7. Model Orchestration (`router.py`): Routes complex tasks to Cortex, syntax to Muscles. Self-Correction Loop utilizing OpenSearch.
8. Proactive Heartbeat (The Watchdog): The `APScheduler` loop scans for proactive work. Uses a local model via LiteLLM (`ollama/llama3` or `phi3`) to evaluate if coaching/research is needed. Cortex is strictly reserved for high-level advice.
9. The Hype Pipeline (`pipeline.py`): Takes an image, applies a selected transformation prompt, generates a matching music track API call, and uploads the final assets to Cloudflare R2.

# Execution Rules
* Output the exhaustive `requirements.txt` and `.env.example` first.
* Then provide the Python backend code (`main.py`, `pipeline.py`, `reporter.py`, `cfo.py`, `router.py`, `research_module.py`).
* Finally, provide the terminal commands and folder structure required to bootstrap the `/commander-dashboard` Next.js app.