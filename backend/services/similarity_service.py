"""
Computes behavioral similarity between a user's current session embedding
and their established baseline — the primary trust signal.

Pipeline position:
    Current Embedding + Baseline → **Similarity Score** → CUSUM → Risk Level

Similarity interpretation (from proposal thresholds):
    > 0.90  → TRUSTED    (high confidence: same user, normal behavior)
    > 0.75  → NORMAL     (acceptable variance, natural day-to-day drift)
    > 0.60  → SUSPICIOUS (significant deviation, step-up auth recommended)
    ≤ 0.60  → HIGH_RISK  (behavioral identity mismatch, likely different actor)
    
"""

import numpy as np
from typing import Dict, Tuple
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine


class SimilarityService:
    """
    Computes and classifies behavioral similarity between session embeddings.

    Uses cosine similarity on L2-normalized 384-dim embeddings from MiniLM.
    Since embeddings are already normalized, cosine similarity = dot product,
    but we use sklearn's implementation for numerical stability on edge cases.

    The similarity score feeds directly into:
    1. Trust Score T(t) as the behavioral_similarity component (weight: 0.40)
    2. CUSUM drift detector for change-point detection
    3. Risk classification for instant action decisions
    """

    # Classification thresholds calibrated against Phase 2B test results:
    #   Normal↔Normal: ~0.998 similarity
    #   Normal↔Takeover: ~0.87 similarity
    #   Normal↔Scam: ~0.78 similarity
    #   Normal↔Malware: ~0.86 similarity
    THRESHOLD_TRUSTED = 0.90
    THRESHOLD_NORMAL = 0.75
    THRESHOLD_SUSPICIOUS = 0.60

    def calculate_similarity(
        self,
        baseline_embedding: np.ndarray,
        current_embedding: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between baseline and current session.

        Args:
            baseline_embedding: User's stored behavioral baseline (384,)
            current_embedding: Current session's embedding (384,)

        Returns:
            Similarity score in [-1.0, 1.0]. Higher = more similar.
            Practically, values below 0.5 indicate completely different behavior.
        """
        baseline = baseline_embedding.reshape(1, -1)
        current = current_embedding.reshape(1, -1)

        similarity = sklearn_cosine(baseline, current)[0][0]
        return float(np.clip(similarity, -1.0, 1.0))

    def calculate_drift_score(
        self,
        baseline_embedding: np.ndarray,
        current_embedding: np.ndarray
    ) -> float:
        """
        Compute drift score (inverse of similarity).
        Drift Score D(t) = 1 - similarity.

        Returns:
            Drift score in [0.0, 2.0]. Higher = more anomalous.
            0.0 = identical behavior, 1.0 = orthogonal, 2.0 = opposite.
        """
        similarity = self.calculate_similarity(baseline_embedding, current_embedding)
        return 1.0 - similarity

    def classify_similarity(self, score: float) -> str:
        """
        Classify a similarity score into risk categories.

        Args:
            score: Cosine similarity value.

        Returns:
            One of: "TRUSTED", "NORMAL", "SUSPICIOUS", "HIGH_RISK"
        """
        if score > self.THRESHOLD_TRUSTED:
            return "TRUSTED"
        elif score > self.THRESHOLD_NORMAL:
            return "NORMAL"
        elif score > self.THRESHOLD_SUSPICIOUS:
            return "SUSPICIOUS"
        return "HIGH_RISK"

    def evaluate(
        self,
        baseline_embedding: np.ndarray,
        current_embedding: np.ndarray
    ) -> Dict:
        """
        Full similarity evaluation with score, drift, classification, and metadata.

        Args:
            baseline_embedding: User's baseline (384,)
            current_embedding: Current session embedding (384,)

        Returns:
            Dictionary with:
            - similarity: raw cosine similarity [-1, 1]
            - drift_score: 1 - similarity [0, 2]
            - classification: "TRUSTED" | "NORMAL" | "SUSPICIOUS" | "HIGH_RISK"
            - confidence: how far from the nearest threshold boundary [0, 1]
            - behavioral_similarity_component: weighted value for T(t) formula (0.40 * sim)
        """
        similarity = self.calculate_similarity(baseline_embedding, current_embedding)
        drift_score = 1.0 - similarity
        classification = self.classify_similarity(similarity)

        # Confidence: distance from nearest threshold boundary (normalized)
        thresholds = [self.THRESHOLD_TRUSTED, self.THRESHOLD_NORMAL, self.THRESHOLD_SUSPICIOUS]
        min_distance = min(abs(similarity - t) for t in thresholds)
        confidence = min(1.0, min_distance / 0.15)  # normalize to [0, 1]

        # Direct contribution to Trust Score T(t)
        # T(t) = 0.40 * behavioral_similarity + ...
        behavioral_component = 0.40 * max(0.0, similarity)

        return {
            "similarity": round(similarity, 6),
            "drift_score": round(drift_score, 6),
            "classification": classification,
            "confidence": round(confidence, 4),
            "behavioral_similarity_component": round(behavioral_component, 6),
        }

    def compare_multiple_sessions(
        self,
        baseline_embedding: np.ndarray,
        session_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Batch comparison of multiple session embeddings against a baseline.
        Useful for analyzing behavioral trajectories over time.

        Args:
            baseline_embedding: User's baseline (384,)
            session_embeddings: Array of shape (n_sessions, 384)

        Returns:
            Array of similarity scores, shape (n_sessions,)
        """
        baseline = baseline_embedding.reshape(1, -1)
        similarities = sklearn_cosine(baseline, session_embeddings)[0]
        return similarities.astype(np.float64)
