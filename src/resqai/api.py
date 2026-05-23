from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .model import DEFAULT_MODEL_PATH, load_model, predict_intent
from .responses import response_for_intent


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: str | None = Field(default="default")


class ChatResponse(BaseModel):
    message: str
    intent: str
    reply: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = None
    if DEFAULT_MODEL_PATH.exists():
        app.state.model = load_model(DEFAULT_MODEL_PATH)
    yield


app = FastAPI(title="ResQAI", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


import time

SESSIONS: dict[str, dict] = {}
SESSION_TIMEOUT = 300  # 5 minutes


def get_or_create_session(session_id: str) -> dict:
    now = time.time()
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {
            "last_categories": [],
            "last_updated": now
        }
    
    session = SESSIONS[session_id]
    if now - session["last_updated"] > SESSION_TIMEOUT:
        session["last_categories"] = []
    
    session["last_updated"] = now
    return session


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    model = app.state.model
    if model is None:
        raise HTTPException(status_code=503, detail="Model hazir degil. Once egitim calistirin.")

    session_id = request.session_id or "default"
    session = get_or_create_session(session_id)

    intent = predict_intent(model, request.message)

    # Reset session categories if new intent is not context-friendly
    context_friendly_intents = {"menu_isteme", "fiyat_sorma", "alerjen_oneri_isteme"}
    if intent not in context_friendly_intents:
        session["last_categories"] = []

    reply = response_for_intent(intent, request.message, session)
    return ChatResponse(message=request.message, intent=intent, reply=reply)
