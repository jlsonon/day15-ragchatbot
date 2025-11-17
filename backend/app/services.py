from __future__ import annotations

import logging
from typing import List

from fastapi import UploadFile

from app.conversation_store import conversation_store
from app.document_parser import parse_document
from app.models import ChatResponse, FollowUpRequest, ParsedDocument, RetrievedSource
from app.rag_service import chat_with_rag

logger = logging.getLogger(__name__)


async def upload_document(file: UploadFile, conversation_id: str) -> ParsedDocument:
    """Upload and parse document for RAG."""
    conversation_store.ensure_conversation(conversation_id)
    document = await parse_document(file)
    
    # Store document text in conversation for RAG
    conversation_store.store_document(conversation_id, document.text)
    
    conversation_store.append_message(
        conversation_id,
        role="system",
        content=f"Document '{document.metadata.filename}' uploaded ({document.metadata.word_count} words). Ready for questions.",
    )
    return document


async def chat_with_rag_context(request: FollowUpRequest) -> ChatResponse:
    """Chat with RAG context from uploaded documents."""
    conversation_store.append_message(
        request.conversation_id,
        role="user",
        content=request.question,
    )
    
    # Use RAG service with embeddings (no need to pass chunks, service gets them)
    answer, retrieved_chunks = await chat_with_rag(
        request.conversation_id,
        request.question,
    )
    
    conversation_store.append_message(
        request.conversation_id,
        role="assistant",
        content=answer,
    )
    
    # Extract key points from answer
    key_points = _extract_bullets(answer)

    # Map retrieved chunks into grounding sources for transparency
    sources: List[RetrievedSource] = []
    for idx, (chunk_text, similarity) in enumerate(retrieved_chunks, start=1):
        sources.append(
            RetrievedSource(
                excerpt_id=idx,
                content=chunk_text,
                similarity=float(similarity),
            )
        )

    return ChatResponse(
        conversation_id=request.conversation_id,
        answer=answer,
        key_points=key_points,
        sources=sources,
    )






def _extract_bullets(answer: str) -> List[str]:
    bullets = []
    for line in answer.splitlines():
        if line.strip().startswith(("-", "*")):
            bullets.append(line.strip("-* ").strip())
    return bullets[:5] or [answer[:120]]

