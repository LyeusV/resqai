from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .model import DEFAULT_MODEL_PATH, load_model, predict_intent
from .responses import response_for_intent


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


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


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    model = app.state.model
    if model is None:
        raise HTTPException(status_code=503, detail="Model hazir degil. Once egitim calistirin.")

    intent = predict_intent(model, request.message)
    reply = response_for_intent(intent, request.message)
    return ChatResponse(message=request.message, intent=intent, reply=reply)
