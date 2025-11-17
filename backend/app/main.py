from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.conversation_store import conversation_store
from app.models import AdminMetrics, ChatResponse, ConversationInitResponse, FollowUpRequest, UploadResponse
from app.services import chat_with_rag_context, upload_document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Chatbot", version="3.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.post("/conversation/init", response_model=ConversationInitResponse)
async def init_conversation() -> ConversationInitResponse:
    conversation_id = conversation_store.start_conversation()
    return ConversationInitResponse(conversation_id=conversation_id)


@app.post("/upload", response_model=UploadResponse)
async def upload(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = Form(None),
) -> UploadResponse:
    """Upload a document for RAG chat."""
    conversation_key = conversation_id or conversation_store.start_conversation()
    document = await upload_document(file, conversation_key)
    
    return UploadResponse(
        conversation_id=conversation_key,
        message=f"Document '{document.metadata.filename}' uploaded successfully. You can now ask questions about it.",
        metadata=document.metadata,
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: FollowUpRequest) -> ChatResponse:
    """Chat with RAG context from uploaded documents."""
    response = await chat_with_rag_context(request)
    return response


@app.get("/health")
async def health():
    return {"status": "ok", "service": "RAG Chatbot"}


@app.get("/admin/metrics", response_model=AdminMetrics)
async def admin_metrics() -> AdminMetrics:
    """Simple usage metrics for portfolio/demo admin view."""
    stats = conversation_store.get_stats()
    return AdminMetrics(
        total_conversations=stats["total_conversations"],
        documents_indexed=stats["documents_indexed"],
        total_queries=stats["total_queries"],
        generated_at=datetime.utcnow().isoformat() + "Z",
    )

