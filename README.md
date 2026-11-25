# Lyftr AI Chatbot

A full-stack LLM chatbot built with React, FastAPI, LiteLLM, and SQLite. It supports multiple API keys, failure simulation, response caching, and persistent conversation history.

## Live URLs

- Frontend: Not deployed yet
- Backend: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- GitHub: https://github.com/DimpleRogha/lyftr_ai_chatbot

## Run locally: with Docker

Docker setup is not yet configured.

## Run locally: without Docker

### Backend

```bash
cd backend
python -m venv venv
```

Activate the environment and install dependencies:

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Configure these environment variables in `backend/.env`:

```env
OPENROUTER_API_KEY_1=your_key_1
OPENROUTER_API_KEY_2=your_key_2
OPENROUTER_MODEL=openrouter/google/gemma-3-27b-it
ENABLE_FAILURE_SIMULATION=true
```

## Design decisions

### Key fallback
Two OpenRouter API keys are configured as separate LiteLLM deployments. If one deployment fails, the application attempts the second.

### Caching
LiteLLM response caching is enabled to reuse responses for repeated requests.

### SQLite session storage
Conversation messages and response metadata are stored in SQLite.

## Verification

- Failover: Send `X-Simulate-Failure: key_1=429`.
- Complete failure: Send `X-Simulate-Failure: *=429`.
- Cache hits: Repeat an identical prompt in a new session.
- Token usage: Inspect `input_tokens` and `output_tokens` in the response metadata.

## Setup Used

- React
- Python
- FastAPI
- LiteLLM
- SQLite
- OpenRouter

## Bonus features

- API failure simulation
- Persistent session history
- Response metadata and token tracking