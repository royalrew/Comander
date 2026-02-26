# Context & Role
You are the "Chief Operating Officer" (COO) AI Architect. We are building "The Commander" – an autonomous, multi-domain engine designed for total life and financial leverage. 

The goal is "CEO Mode": An asynchronous, proactive agent that solves problems before the user notices them, generates new capabilities dynamically, and delivers a daily "Executive Briefing" via Telegram. 

# The Genesis Profile (Core Context)
* Create a `ceo_profile.yaml` file in the root of `/commander-core`.
* User Identity: "Jimmy". Base location: "Töreboda, Sweden".
* Ultimate Goal: "Automate everything. Leverage time to gain absolute financial freedom."
* Current Business Focus: "The Hype Engine" – Building automated Multi-Modal B2B/B2C pipelines that turn mundane objects (used cars, frying pans) or run-down real estate (fixer-upper houses) into highly engaging viral marketing content. 
* Core Output: High-fidelity image transformations accompanied by generated AI music, packaged for social media (Reels/TikTok).
* Proactive Mandate: The AI must proactively analyze codebases overnight, implement non-breaking UI/UX improvements, and optimize workflows. 
* Communication: "CEO Mode" – Direct, factual. Morning briefings via Telegram.

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
1. The I/O Jail (`io_jail.py`): The AI has NO direct file system access. Ensure all read/write/mkdir operations are strictly confined to `WORKSPACE_ROOT`.
2. Execution Whitelist: `surgeon.py` MUST NOT use `shell=True` in `subprocess`. 
3. API Circuit Breakers: `cfo.py` implements a hard cap on daily token spend. 
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
5. The Deterministic Observer (`observer.py`): Uses `tree-sitter` for factual extraction. 
6. The Action Gateway (`surgeon.py`): Executes code patching via AST.
7. Model Orchestration (`router.py`): Routes complex tasks to Cortex, syntax to Muscles. Self-Correction Loop utilizing OpenSearch.
8. Proactive Heartbeat (The Watchdog): The `APScheduler` loop scans for proactive work. To prevent API drain, this heartbeat must strictly use a local model via LiteLLM (`ollama/llama3` or `phi3`) to evaluate if action is needed. Cortex is strictly reserved for execution.
9. The Hype Pipeline (`pipeline.py`): Takes an image, applies a selected transformation prompt, generates a matching music track API call, and uploads the final assets to Cloudflare R2.

# Execution Rules
* Output the exhaustive `requirements.txt` and `.env.example` first.
* Then provide the Python backend code (`main.py`, `pipeline.py`, `reporter.py`, `cfo.py`, `router.py`, `surgeon.py`).
* Finally, provide the terminal commands and folder structure required to bootstrap the `/commander-dashboard` Next.js app.