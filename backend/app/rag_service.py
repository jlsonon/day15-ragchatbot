from __future__ import annotations

import logging
from typing import List, Tuple, Optional

import numpy as np

from app.conversation_store import conversation_store
from app.embeddings import find_similar_chunks, generate_embeddings
from app.groq_api import GroqAPIError, groq_client

logger = logging.getLogger(__name__)

RAG_SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based on the provided document context.
Use the document excerpts to provide accurate, relevant answers. If the context doesn't contain enough information, say so.
Be concise and cite relevant parts of the document when possible. When referencing information, mention which excerpt it came from."""


def chunk_text_smart(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """Smart chunking that preserves sentence boundaries."""
    # First split by paragraphs
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        # If paragraph is small, add it to current chunk
        if len(current_chunk) + len(para) < chunk_size:
            current_chunk += "\n\n" + para if current_chunk else para
        else:
            # Save current chunk if it exists
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # If paragraph is large, split by sentences
            if len(para) > chunk_size:
                sentences = para.split(". ")
                temp_chunk = ""
                for sentence in sentences:
                    if len(temp_chunk) + len(sentence) < chunk_size:
                        temp_chunk += ". " + sentence if temp_chunk else sentence
                    else:
                        if temp_chunk:
                            chunks.append(temp_chunk.strip() + ".")
                        temp_chunk = sentence
                current_chunk = temp_chunk
            else:
                current_chunk = para
    
    # Add final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # Add overlap between chunks for better context
    if len(chunks) > 1 and overlap > 0:
        overlapped_chunks = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_chunk = chunks[i - 1]
            current_chunk = chunks[i]
            
            # Take last part of previous chunk
            prev_words = prev_chunk.split()
            overlap_text = " ".join(prev_words[-overlap // 10:]) if len(prev_words) > overlap // 10 else prev_chunk[-overlap:]
            
            # Combine with current chunk
            combined = overlap_text + " " + current_chunk
            overlapped_chunks.append(combined.strip())
        
        return overlapped_chunks
    
    return chunks


async def chat_with_rag(conversation_id: str, question: str) -> Tuple[str, List[Tuple[str, float]]]:
    """Full RAG chat with embeddings and semantic search.

    Returns a tuple of:
    - answer: the model-generated answer
    - retrieved_chunks: list of (chunk_text, similarity_score) used as grounding
    """
    history = conversation_store.get_history(conversation_id)
    previous_answer = _get_recent_assistant_answer(history)
    
    # Get document chunks and embeddings
    document_chunks = conversation_store.get_document_chunks(conversation_id)
    chunk_embeddings = conversation_store.get_chunk_embeddings(conversation_id)
    
    if not document_chunks:
        return "No document has been uploaded yet. Please upload a document first.", []
    
    if chunk_embeddings is None:
        logger.warning("Chunk embeddings missing; falling back to keyword search.")
        return await _fallback_keyword_search(question, document_chunks, history, previous_answer)
    
    # Generate query embedding
    try:
        query_embedding = generate_embeddings([question])[0]
    except Exception as e:
        logger.error(f"Error generating query embedding: {e}")
        # Fallback to keyword search
        return await _fallback_keyword_search(question, document_chunks, history, previous_answer)
    
    # Find similar chunks using semantic search
    similar_chunks = find_similar_chunks(
        query_embedding,
        chunk_embeddings,
        document_chunks,
        top_k=4,
        min_similarity=0.2,
    )
    
    if not similar_chunks:
        logger.info("Semantic search returned no chunks; using keyword fallback.")
        return await _fallback_keyword_search(question, document_chunks, history, previous_answer)
    
    # Build context from retrieved chunks
    context_parts = []
    for i, (chunk, similarity) in enumerate(similar_chunks, 1):
        context_parts.append(f"[Excerpt {i} (relevance: {similarity:.2f})]:\n{chunk}")
    
    context = "\n\n".join(context_parts)
    
    # Build messages with conversation history
    messages = [{"role": "system", "content": RAG_SYSTEM_PROMPT}]
    
    # Add recent conversation history (last 8 messages for better context)
    for msg in history[-8:]:
        if msg["role"] in ["user", "assistant"]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Add current question with retrieved context
    user_message = _build_user_prompt(context, question, previous_answer)
    
    messages.append({"role": "user", "content": user_message})
    
    try:
        answer = await groq_client.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=1000,
        )
        return answer, similar_chunks
    except GroqAPIError as e:
        logger.error(f"Groq API error during RAG chat: {e}")
        # Fallback: return top chunks as plain text but still surface them as retrieved sources
        top_chunks_text = "\n\n".join([chunk for chunk, _ in similar_chunks[:2]])
        fallback_answer = (
            "I found relevant information but couldn't process it with AI. "
            "Here are the most relevant excerpts:\n\n"
            f"{top_chunks_text}"
        )
        return fallback_answer, similar_chunks


async def _fallback_keyword_search(
    question: str,
    document_chunks: List[str],
    history: List[dict],
    previous_answer: Optional[str] = None,
) -> Tuple[str, List[Tuple[str, float]]]:
    """Fallback to keyword-based search if embeddings fail.

    Returns the generated answer along with a list of (chunk, pseudo_similarity)
    so the caller can still expose grounding information.
    """
    query_lower = question.lower()
    query_words = set(query_lower.split())
    
    scored_chunks = []
    for chunk in document_chunks:
        chunk_lower = chunk.lower()
        score = sum(1 for word in query_words if word in chunk_lower)
        if score > 0:
            scored_chunks.append((score, chunk))
    
    scored_chunks.sort(reverse=True, key=lambda x: x[0])
    relevant_chunks = [chunk for _, chunk in scored_chunks[:3]]
    
    if not relevant_chunks:
        if _is_follow_up_question(question):
            recent = previous_answer or "I have already shared all the details the document contains so far."
            answer = (
                f"I've already shared the available insights from the document. "
                f"Previous answer:\n{recent}\n\n"
                "If you need something specific, try asking about a particular section or topic."
            )
            return answer, []
        return "I couldn't find relevant information in the document related to that question.", []
    
    context = "\n\n".join([f"[Excerpt {i+1}]:\n{chunk}" for i, chunk in enumerate(relevant_chunks)])
    
    messages = [{"role": "system", "content": RAG_SYSTEM_PROMPT}]
    for msg in history[-6:]:
        if msg["role"] in ["user", "assistant"]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    previous_answer_text = f"\n\nPrevious answer: {previous_answer}" if previous_answer else ""
    user_message = (
        f"Document context:\n{context}\n\nQuestion: {question}{previous_answer_text}\n\n"
        "If the context does not answer the question, explain that the document doesn't mention it and suggest "
        "what the user could do next (e.g., check the cover page, metadata, or another section)."
    )
    messages.append({"role": "user", "content": user_message})
    
    try:
        answer = await groq_client.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=800,
        )
        # Use a simple normalized score as a pseudo-similarity so UI can sort / display grounding strength
        max_score = max(score for score, _ in scored_chunks) if scored_chunks else 1
        retrieved = []
        for score, chunk in scored_chunks[:3]:
            similarity = float(score) / float(max_score) if max_score else 0.0
            retrieved.append((chunk, similarity))
        return answer, retrieved
    except GroqAPIError:
        # Surface the raw chunks even if the LLM call fails
        max_score = max(score for score, _ in scored_chunks) if scored_chunks else 1
        retrieved = []
        for score, chunk in scored_chunks[:3]:
            similarity = float(score) / float(max_score) if max_score else 0.0
            retrieved.append((chunk, similarity))
        return "I found relevant information but couldn't process it. Please check your API configuration.", retrieved


def _get_recent_assistant_answer(history: List[dict]) -> Optional[str]:
    for msg in reversed(history):
        if msg.get("role") == "assistant":
            return msg.get("content")
    return None


def _is_follow_up_question(question: str) -> bool:
    q = question.strip().lower()
    if not q:
        return False
    follow_up_cues = [
        "other than that",
        "what else",
        "anything else",
        "something more",
        "tell me more",
        "what more",
        "what about the rest",
        "what improvements you can add",
    ]
    return any(cue in q for cue in follow_up_cues) or len(q.split()) <= 4


def _build_user_prompt(context: str, question: str, previous_answer: Optional[str]) -> str:
    previous_context = ""
    if previous_answer:
        previous_context = (
            "\n\nPrevious answer shared with the user (for reference, do not repeat verbatim unless needed):\n"
            f"{previous_answer}"
        )
    return (
        "Based on the following document excerpts, please answer the question.\n\n"
        f"{context}"
        f"{previous_context}\n\n"
        f"Question: {question}\n\n"
        "Please provide a clear, accurate answer based on the excerpts. If the excerpts don't contain enough "
        "information, say so explicitly and suggest where the user might look in the document."
    )
