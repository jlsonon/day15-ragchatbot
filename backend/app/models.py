from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    filename: str
    file_type: str
    pages: Optional[int] = None
    word_count: int
    language: Optional[str] = None


class ParsedDocument(BaseModel):
    metadata: DocumentMetadata
    text: str


class UploadResponse(BaseModel):
    conversation_id: str
    message: str
    metadata: DocumentMetadata


class ConversationInitResponse(BaseModel):
    conversation_id: str


class FollowUpRequest(BaseModel):
    conversation_id: str
    question: str


class RetrievedSource(BaseModel):
    """Represents a retrieved document excerpt used to ground an answer."""

    excerpt_id: int
    content: str
    similarity: float


class AdminMetrics(BaseModel):
    total_conversations: int
    documents_indexed: int
    total_queries: int
    generated_at: str


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    key_points: List[str] = []
    sources: List[RetrievedSource] = []
