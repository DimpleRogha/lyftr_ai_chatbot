from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
from fastapi import Request
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import time

from database import save_message, get_messages
from llm import get_ai_response

from database import init_db, get_messages, get_connection

load_dotenv()

class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=4000)
    system_prompt: Optional[str] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Lyftr AI Chatbot",
    lifespan=lifespan
)

origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Lyftr AI Chatbot Backend Running"}


@app.get("/health")
async def health():
    with get_connection() as conn:
        conn.execute("SELECT 1")

    keys = sum(
        bool(os.getenv(f"OPENROUTER_API_KEY_{i}"))
        for i in range(1, 3)
    )

    return {
        "status": "ok",
        "keys_configured": keys,
        "cache_enabled": True
    }


@app.get("/sessions/{session_id}/messages")
async def session_messages(session_id: str):
    messages = get_messages(session_id)

    if not messages:
        raise HTTPException(
            status_code=404,
            detail="session not found"
        )

    return {
        "session_id": session_id,
        "messages": messages
    }

@app.post("/chat")
def chat(
    request: ChatRequest,
    http_request: Request,
    x_simulate_failure: Optional[str] = Header(default=None)
):
    session_id = request.session_id
    message = request.message.strip()

    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be empty")

    history = get_messages(session_id)

    system_prompt = request.system_prompt or (
        "You are Lyftr AI, a helpful and intelligent assistant."
    )

    messages = [{"role": "system", "content": system_prompt}]

    for item in history:
        messages.append({
            "role": item["role"],
            "content": item["content"]
        })

    messages.append({"role": "user", "content": message})

    simulation = x_simulate_failure
    if os.getenv("ENABLE_FAILURE_SIMULATION", "false").lower() == "true":
        simulation = http_request.headers.get("X-Simulate-Failure")

    start_time = time.perf_counter()

    try:
        response, cache_hit, key_id, fallback_attempts = (
            get_ai_response(messages, simulation)
        )

        latency = int((time.perf_counter() - start_time) * 1000)

        reply = response.choices[0].message.content

        if not reply:
            raise Exception("Empty AI response")

        usage = response.usage

        metadata = {
            "resolution_source": "LLM_CACHE" if cache_hit else "LIVE_INFERENCE",
            "model": response.model,
            "latency_ms": latency,
            "input_tokens": usage.prompt_tokens,
            "output_tokens": usage.completion_tokens,
            "key_id": key_id,
            "fallback_attempts": 0 if cache_hit else fallback_attempts
        }

        save_message(session_id, "user", message)
        save_message(session_id, "assistant", reply, metadata)

        return {
            "session_id": session_id,
            "reply": reply,
            "metadata": metadata
        }

    except Exception as e:
        print("Chat error:", str(e))
        raise HTTPException(
            status_code=503,
            detail="all providers unavailable"
        )