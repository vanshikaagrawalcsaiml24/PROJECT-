# ProjectMentor AI — Backend

> Convert any project idea into a complete, structured project blueprint using a multi-agent AI pipeline powered by **DeepSeek V3**.

---

## 🚀 Quick Start

### 1. Clone & navigate
```bash
cd backend
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env and add your DEEPSEEK_API_KEY
```

### 5. Run the server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

---

## 📡 API Reference

### `POST /generate-blueprint`

Generate a complete project blueprint from a project idea.

**Request body:**
```json
{
  "project_idea": "Build an AI Interview Preparation Platform"
}
```

**Response:**
```json
{
  "project_idea": "Build an AI Interview Preparation Platform",
  "problem_statement": "Job seekers struggle to prepare effectively...",
  "project_overview": "An AI-powered platform that...",
  "objectives": ["Reduce interview anxiety by 40%", "..."],
  "target_users": ["Fresh graduates", "Mid-level engineers", "..."],
  "features": ["Mock interview sessions", "AI-generated feedback", "..."],
  "tech_stack": {
    "frontend": ["React 18", "TypeScript", "TailwindCSS"],
    "backend": ["FastAPI", "Python 3.11", "Celery"],
    "database": ["PostgreSQL", "Redis"],
    "deployment": ["Docker", "AWS ECS", "GitHub Actions"],
    "ai_ml": ["DeepSeek API", "Whisper", "LangChain"],
    "devtools": ["pytest", "Ruff", "pre-commit"]
  },
  "architecture": "Microservices architecture with...",
  "architecture_components": [...],
  "database_suggestions": [...],
  "api_suggestions": [...],
  "development_roadmap": [
    {
      "phase": "Phase 1: Foundation Setup",
      "duration": "2 weeks",
      "tasks": ["Setup monorepo", "Configure CI/CD", "..."]
    }
  ],
  "future_scope": ["Mobile app", "Resume builder", "..."]
}
```

### `GET /health`

Returns service health status.

```json
{
  "status": "ok",
  "version": "1.0.0",
  "provider": "deepseek"
}
```

---

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app, middleware, routes
│   ├── config.py                  # Settings from environment variables
│   │
│   ├── routes/
│   │   └── project.py             # POST /generate-blueprint
│   │
│   ├── services/
│   │   ├── llm_provider.py        # Abstract LLM provider interface
│   │   ├── deepseek_service.py    # DeepSeek concrete provider
│   │   ├── openrouter_service.py  # OpenRouter concrete provider
│   │   └── orchestrator.py        # Multi-agent pipeline orchestrator
│   │
│   ├── agents/
│   │   ├── requirements_agent.py  # Extracts features, modules, personas
│   │   ├── documentation_agent.py # Problem statement, objectives
│   │   ├── architecture_agent.py  # System design, DB, API suggestions
│   │   └── techstack_agent.py     # Tech stack, roadmap, future scope
│   │
│   ├── prompts/
│   │   ├── requirements_prompt.py
│   │   ├── documentation_prompt.py
│   │   ├── architecture_prompt.py
│   │   └── techstack_prompt.py
│   │
│   └── models/
│       └── schemas.py             # Pydantic request/response models
│
├── .env                           # Your local environment variables
├── .env.example                   # Template (safe to commit)
├── requirements.txt
└── README.md
```

---

## 🤖 Multi-Agent Pipeline

```
User Input (project idea)
        │
        ▼
┌─────────────────────┐
│  Requirements Agent │  → Extracts features, modules, target users
└────────┬────────────┘
         │
         ▼
┌──────────────────────┐
│ Documentation Agent  │  → Problem statement, objectives, overview
└────────┬─────────────┘
         │
         ▼
┌─────────────────────┐
│  Architecture Agent │  → System design, DB schema, API endpoints
└────────┬────────────┘
         │
         ▼
┌──────────────────────┐
│  Tech Stack Agent    │  → Technologies, roadmap, future scope
└────────┬─────────────┘
         │
         ▼
    Merge Results
         │
         ▼
  ProjectBlueprintResponse (JSON)
```

---

## 🔌 LLM Provider Abstraction

Switching providers requires **only one environment variable change**:

```env
# Use DeepSeek (default)
LLM_PROVIDER=deepseek

# Use OpenRouter
LLM_PROVIDER=openrouter
```

All agents call `llm.generate(prompt)` — they never import provider-specific code.

To add a **new provider** (e.g., Anthropic):
1. Create `app/services/anthropic_service.py` implementing `LLMProvider`
2. Add an `elif` branch in `orchestrator._get_llm_provider()`
3. Add the API key to `.env`

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `deepseek` | Active provider (`deepseek` \| `openrouter`) |
| `DEEPSEEK_API_KEY` | — | **Required** for DeepSeek |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | DeepSeek API base URL |
| `DEEPSEEK_MODEL` | `deepseek-chat` | Model identifier |
| `OPENROUTER_API_KEY` | — | Required if using OpenRouter |
| `OPENROUTER_MODEL` | `deepseek/deepseek-chat` | OpenRouter model |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `LLM_TEMPERATURE` | `0.7` | Sampling temperature (0.0–2.0) |
| `LLM_MAX_TOKENS` | `4096` | Max tokens per LLM call |
| `LLM_TIMEOUT_SECONDS` | `120` | HTTP timeout for LLM calls |
| `CORS_ORIGINS` | `["*"]` | Allowed CORS origins |

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With verbose output
pytest -v

# Test specific module
pytest tests/test_routes.py
```

---

## 📝 License

MIT License — see [LICENSE](../LICENSE) for details.
