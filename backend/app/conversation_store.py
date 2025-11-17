from __future__ import annotations

import logging
import secrets
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from app.embeddings import generate_embeddings

logger = logging.getLogger(__name__)


@dataclass
class Conversation:
    history: List[dict] = field(default_factory=list)
    document_text: str = ""
    document_chunks: List[str] = field(default_factory=list)
    chunk_embeddings: Optional[np.ndarray] = None


class ConversationStore:
    def __init__(self) -> None:
        self._store: Dict[str, Conversation] = {}
        self._document_uploads: int = 0
        self._query_count: int = 0

    def start_conversation(self) -> str:
        conversation_id = secrets.token_hex(16)
        self._store[conversation_id] = Conversation()
        return conversation_id

    def append_message(self, conversation_id: str, role: str, content: str) -> None:
        conversation = self._store.setdefault(conversation_id, Conversation())
        conversation.history.append({"role": role, "content": content})
        if role == "user":
            self._query_count += 1

    def get_history(self, conversation_id: str) -> List[dict]:
        return self._store.get(conversation_id, Conversation()).history

    def ensure_conversation(self, conversation_id: str) -> str:
        if conversation_id not in self._store:
            self._store[conversation_id] = Conversation()
        return conversation_id
    
    def store_document(self, conversation_id: str, text: str) -> None:
        """Store document text, create chunks, and generate embeddings for RAG."""
        conversation = self._store.setdefault(conversation_id, Conversation())
        conversation.document_text = text
        
        # Smart chunking with overlap (import here to avoid circular dependency)
        from app.rag_service import chunk_text_smart
        chunks = chunk_text_smart(text, chunk_size=500, overlap=100)
        conversation.document_chunks = chunks
        
        # Generate embeddings for all chunks
        try:
            if chunks:
                embeddings = generate_embeddings(chunks)
                conversation.chunk_embeddings = embeddings
                self._document_uploads += 1
            else:
                conversation.chunk_embeddings = None
        except Exception as e:
            # If embeddings fail, store None and fall back to keyword search
            logger.warning(f"Failed to generate embeddings: {e}. Will use keyword search fallback.")
            conversation.chunk_embeddings = None
    
    def get_document_chunks(self, conversation_id: str) -> List[str]:
        """Get document chunks for RAG retrieval."""
        return self._store.get(conversation_id, Conversation()).document_chunks
    
    def get_chunk_embeddings(self, conversation_id: str) -> Optional[np.ndarray]:
        """Get chunk embeddings for semantic search."""
        return self._store.get(conversation_id, Conversation()).chunk_embeddings

    def get_stats(self) -> dict:
        """Return simple usage metrics for admin dashboard."""
        return {
            "total_conversations": len(self._store),
            "documents_indexed": self._document_uploads,
            "total_queries": self._query_count,
        }


conversation_store = ConversationStore()

