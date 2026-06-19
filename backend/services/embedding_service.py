"""
AEGIS-X Phase 2B: Embedding Engine
====================================
Converts behavioral text descriptions into 384-dimensional semantic embeddings
using sentence-transformers/all-MiniLM-L6-v2.


Why MiniLM on text instead of raw numbers?
    Raw numbers (3.4, 3.5, 3.6) carry no semantic meaning to a transformer.
    But "typing speed is normal" and "moderate typing rhythm" produce similar embeddings.
    This means behavioral descriptions that MEAN the same thing will cluster together
    in embedding space — regardless of exact wording. This is the foundation of
    drift detection: when a user's behavioral description changes semantically,
    the cosine distance from their baseline embedding increases.

"""

import numpy as np
from typing import List, Union, Optional
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Generates 384-dimensional behavioral embeddings from text descriptions.

    This is the core of AEGIS-X's behavioral fingerprinting system.
    Each user session produces a stream of embeddings — their "behavioral trajectory"
    through 384-dimensional space. Drift from the established baseline trajectory
    signals a potential identity change (takeover, malware, or coercion).

    Usage:
        service = EmbeddingService()
        embedding = service.generate_embedding("Typing speed is normal. Low hesitation.")
        # embedding.shape == (384,)

        # Batch processing for training data
        embeddings = service.generate_embeddings_batch([text1, text2, text3])
        # embeddings.shape == (3, 384)
    """

    _instance: Optional["EmbeddingService"] = None
    _model: Optional[SentenceTransformer] = None

    def __new__(cls):
        """Singleton pattern — model loads once, reused across all calls."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Load MiniLM-L6-v2 model (lazy initialization on first use)."""
        if EmbeddingService._model is None:
            EmbeddingService._model = SentenceTransformer(
                "all-MiniLM-L6-v2",
                device="cpu"  # CPU sufficient for <100ms latency at hackathon scale
            )

    @property
    def model(self) -> SentenceTransformer:
        return EmbeddingService._model

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate a single 384-dim embedding from a behavioral description.

        Args:
            text: Behavioral description string from BehavioralSerializer.

        Returns:
            numpy array of shape (384,) — the behavioral fingerprint.
        """
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True  # L2 normalize for cosine similarity
        )
        return embedding

    def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 64,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Generate embeddings for multiple behavioral descriptions at once.
        Significantly faster than calling generate_embedding() in a loop.

        Args:
            texts: List of behavioral description strings.
            batch_size: Number of texts to encode per batch (tune for memory).
            show_progress: Show progress bar during encoding.

        Returns:
            numpy array of shape (n_texts, 384).
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=show_progress
        )
        return embeddings

    def embedding_dimension(self) -> int:
        """Return the dimensionality of the embedding space (384 for MiniLM-L6-v2)."""
        return self.model.get_embedding_dimension()

    def cosine_similarity(
        self,
        embedding_a: np.ndarray,
        embedding_b: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between two embeddings.
        Since embeddings are L2-normalized, this is simply the dot product.

        Args:
            embedding_a: First embedding vector (384,)
            embedding_b: Second embedding vector (384,)

        Returns:
            Similarity score in [-1, 1]. Higher = more similar behavior.
            For AEGIS-X:
                > 0.85 → very similar (same user, normal behavior)
                0.60-0.85 → moderate drift (possible concern)
                < 0.60 → significant divergence (likely different actor)
        """
        # Normalized vectors: cosine_sim = dot product
        sim = np.dot(embedding_a, embedding_b)
        return float(np.clip(sim, -1.0, 1.0))

    def cosine_distance(
        self,
        embedding_a: np.ndarray,
        embedding_b: np.ndarray
    ) -> float:
        """
        Compute cosine distance (1 - similarity). Higher = more different.
        This is the Drift Score D(t) from the proposal.

        Returns:
            Distance in [0, 2]. 0 = identical, 2 = opposite.
        """
        return 1.0 - self.cosine_similarity(embedding_a, embedding_b)

    def compute_baseline(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Compute a user's behavioral baseline as the mean of their normal embeddings.
        This is the centroid of their behavioral fingerprint in 384-D space.

        Args:
            embeddings: Array of shape (n_sessions, 384) from user's normal behavior.

        Returns:
            Baseline embedding of shape (384,), L2-normalized.
        """
        if len(embeddings) == 0:
            raise ValueError("Cannot compute baseline from empty embedding set")

        centroid = np.mean(embeddings, axis=0)
        # Re-normalize to unit sphere
        norm = np.linalg.norm(centroid)
        if norm > 0:
            centroid = centroid / norm
        return centroid

    def drift_from_baseline(
        self,
        current_embedding: np.ndarray,
        baseline: np.ndarray
    ) -> dict:
        """
        Compute drift metrics between current behavior and established baseline.

        Args:
            current_embedding: Current session's embedding (384,)
            baseline: User's baseline embedding (384,)

        Returns:
            Dictionary with:
            - similarity: cosine similarity (higher = more normal)
            - drift_score: cosine distance (higher = more anomalous)
            - risk_level: categorical assessment
        """
        similarity = self.cosine_similarity(current_embedding, baseline)
        drift_score = 1.0 - similarity

        # Risk level based on proposal thresholds
        if similarity > 0.85:
            risk_level = "low"
        elif similarity > 0.60:
            risk_level = "elevated"
        else:
            risk_level = "critical"

        return {
            "similarity": similarity,
            "drift_score": drift_score,
            "risk_level": risk_level,
        }
