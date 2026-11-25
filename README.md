# Lyftr AI Chatbot

A full-stack LLM chatbot built using React, FastAPI, LiteLLM, SQLite and OpenRouter. The application supports multi-turn conversations, multiple API keys with failover, response caching, and per-request token tracking.

## 1. Live URLs

| Component | URL |
|---|---|
| Frontend | https://lyftr-ai-chatbot-tan-xi.vercel.app |
| Backend | https://lyftr-backend-d7tx.onrender.com |
| Backend Health | https://lyftr-backend-d7tx.onrender.com/health |
| API Documentation | https://lyftr-backend-d7tx.onrender.com/docs |
| GitHub Repository | https://github.com/DimpleRogha/lyftr_ai_chatbot |

## 2. Run locally: with Docker and without

### Prerequisites

- Docker Desktop
- Python 3.11+
- Node.js 20+
- Two OpenRouter API keys

### With Docker

Clone the repository:

```bash
git clone https://github.com/DimpleRogha/lyftr_ai_chatbot.git
cd lyftr_ai_chatbot
```

Create `backend/.env`:

```env
OPENROUTER_API_KEY_1=your_first_api_key
OPENROUTER_API_KEY_2=your_second_api_key
OPENROUTER_MODEL=openrouter/google/gemma-3-27b-it
DATABASE_URL=sqlite:////data/app.db
ALLOWED_ORIGINS=http://localhost:3000
ENABLE_FAILURE_SIMULATION=true
```

Start the application:

```bash
docker compose up --build
```

Or, if Make is installed:

```bash
make up
```

Access the application:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Documentation: http://localhost:8000/docs

Stop the application:

```bash
docker compose down
```

### Without Docker

Backend:

```bash
cd backend
python -m venv venv
```

Activate the virtual environment on Windows:

```powershell
.\venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn main:app --reload --port 8000
```

Frontend (in another terminal):

```bash
cd frontend
npm install
npm run dev
```

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

Open the Vite development URL displayed in the terminal.

## 3. Design decisions: key fallback, caching, SQLite session storage

### Key fallback

The backend uses LiteLLM Router with two OpenRouter API key deployments.

When a configured key fails, the application attempts the next available key.

The `X-Simulate-Failure` header allows controlled testing of provider failures without exhausting actual API credits.

### Response caching

LiteLLM response caching is enabled to reduce repeated inference requests and improve response speed.

The API reports:

- `LIVE_INFERENCE` for newly generated responses.
- `LLM_CACHE` for cached responses.

### SQLite session storage

SQLite stores conversation history separately for each session.

Each message contains:

- Session ID
- Role
- Content
- Response metadata
- Creation timestamp

The database schema is created automatically during application startup.

Docker uses a named volume mounted at `/data` for database persistence.

## 4. Verification: how to see failover, cache hits and per-message token usage

Use Swagger UI:

http://localhost:8000/docs

### Health check

Call:

`GET /health`

Expected response:

```json
{
  "status": "ok",
  "keys_configured": 2,
  "cache_enabled": true
}
```

### Key failover

Send a POST request to `/chat` with:

Header:

```text
X-Simulate-Failure: key_1=429
```

Expected: HTTP 200, with `key_id` set to `key_2` and `fallback_attempts` set to 1.

### Complete provider failure

Use:

```text
X-Simulate-Failure: *=429
```

Expected:

```json
{
  "detail": "all providers unavailable"
}
```

HTTP status: 503.

Failed requests are not saved to conversation history.

### Response caching

Send the same first message using two different session IDs.

The second request should report `LLM_CACHE` and return the identical reply.

### Token tracking

Every assistant response includes:

- `input_tokens`
- `output_tokens`
- `latency_ms`
- `model`
- `resolution_source`

Token usage is tracked per request, not as a conversation total.

## 5. Setup Used: your editor and AI tools

- Editor: Visual Studio Code
- Backend: Python, FastAPI, LiteLLM
- Frontend: React and Vite
- Database: SQLite
- AI provider: OpenRouter
- Containerization: Docker and Docker Compose
- Version control: Git and GitHub
- Deployment: Render and Vercel
- AI assistance: ChatGPT

## 6. Bonus features (if any): what you added beyond the requirements and why

- Failure simulation through a custom HTTP header for repeatable failover testing.
- Persistent session history using SQLite.
- Per-response metadata displaying model, latency and token usage.
- Docker-based development environment for consistent local execution.