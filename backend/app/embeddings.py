from __future__ import annotations

import logging
from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Global model instance (lazy loaded)
_embedding_model: Optional[SentenceTransformer] = None


def get_embedding_model() -> SentenceTransformer:
    """Lazy load the embedding model."""
    global _embedding_model
    if _embedding_model is None:
        try:
            # Use a lightweight, fast model
            _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    return _embedding_model


def generate_embeddings(texts: List[str]) -> np.ndarray:
    """Generate embeddings for a list of texts."""
    try:
        model = get_embedding_model()
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)


def find_similar_chunks(
    query_embedding: np.ndarray,
    chunk_embeddings: Optional[np.ndarray],
    chunks: List[str],
    top_k: int = 3,
    min_similarity: float = 0.3,
) -> List[tuple[str, float]]:
    """Find most similar chunks using cosine similarity."""
    if chunk_embeddings is None or len(chunk_embeddings) == 0:
        return []
    
    # Ensure numpy arrays
    chunk_vectors = np.atleast_2d(chunk_embeddings)
    query_vector = np.asarray(query_embedding)
    
    chunk_norms = np.linalg.norm(chunk_vectors, axis=1)
    query_norm = np.linalg.norm(query_vector)
    denom = (chunk_norms * query_norm) + 1e-10
    similarities = (chunk_vectors @ query_vector) / denom
    
    scored_indices = [
        (float(sim), idx) for idx, sim in enumerate(similarities) if sim >= min_similarity
    ]
    
    if not scored_indices:
        top_indices = np.argsort(similarities)[::-1][:top_k]
        scored_indices = [(float(similarities[idx]), int(idx)) for idx in top_indices]
    else:
        scored_indices.sort(reverse=True, key=lambda x: x[0])
    
    results: List[tuple[str, float]] = []
    for similarity, idx in scored_indices[:top_k]:
        if idx < len(chunks):
            results.append((chunks[idx], similarity))
    
    return results

