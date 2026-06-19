"""
Creates, stores, updates, and validates user behavioral baselines — the
"trusted behavioral identity" against which all future sessions are compared.

This is the behavioral equivalent of a stored face template in facial recognition:
    Face Recognition:  face → embedding → compare vs stored face template
    AEGIS-X:           behavior → embedding → compare vs stored behavioral baseline

A baseline is the centroid (mean) of multiple trusted session embeddings,
representing "how does this genuine user normally behave?" in 384-D space.

"""

import numpy as np
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple


# Minimum sessions required to establish a reliable baseline
MIN_ENROLLMENT_SESSIONS = 5

# Maximum sessions to include in initial baseline computation
MAX_ENROLLMENT_SESSIONS = 30

# EMA decay factor for baseline updates (higher = more inertia, slower adaptation)
# 0.95 means: new_baseline = 0.95 * old + 0.05 * current
# This ensures ~20 trusted sessions to shift baseline significantly
EMA_DECAY = 0.95

# Trust threshold required to allow baseline update (from proposal: ALLOW > 0.85)
# We use a slightly higher threshold for baseline updates to be conservative
BASELINE_UPDATE_THRESHOLD = 0.90

# Directory for persisted baseline files
BASELINES_DIR = Path(__file__).parent.parent.parent / "embeddings" / "baselines"


class BaselineService:
    """
    Manages behavioral identity baselines for all users.

    Lifecycle:
        1. ENROLLMENT: User performs 5+ normal sessions → initial baseline created
        2. VERIFICATION: Each new session compared against baseline → drift score
        3. ADAPTATION: If trust remains high, baseline slowly adapts via EMA
        4. PROTECTION: Low-trust sessions NEVER update baseline (anti-poisoning)

    Storage:
        Currently: .npz files in embeddings/baselines/ (prototype)
        Production: PostgreSQL BYTEA column (see schema below)

    PostgreSQL schema (for later):
        CREATE TABLE user_baselines (
            user_id TEXT PRIMARY KEY,
            baseline_embedding BYTEA NOT NULL,
            session_count INTEGER DEFAULT 0,
            confidence_score FLOAT DEFAULT 0.0,
            created_at TIMESTAMP WITH TIME ZONE,
            updated_at TIMESTAMP WITH TIME ZONE,
            last_verified_at TIMESTAMP WITH TIME ZONE
        );
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Args:
            storage_dir: Directory for persisting baselines. Defaults to embeddings/baselines/
        """
        self.storage_dir = storage_dir or BASELINES_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    # ═══════════════════════════════════════════════════════════════════════
    # ENROLLMENT: Creating a new baseline from scratch
    # ═══════════════════════════════════════════════════════════════════════

    def create_baseline(
        self,
        embeddings: np.ndarray,
        weights: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Compute a user's behavioral baseline from multiple trusted session embeddings.

        The baseline is the (optionally weighted) centroid of all enrollment embeddings,
        L2-normalized to the unit sphere for cosine similarity operations.

        Args:
            embeddings: Array of shape (n_sessions, 384) from verified normal sessions.
            weights: Optional array of shape (n_sessions,) for weighted averaging.
                     More recent sessions can be weighted higher for freshness.
                     If None, uniform weights are used.

        Returns:
            Baseline embedding of shape (384,), L2-normalized.

        Raises:
            ValueError: If fewer than MIN_ENROLLMENT_SESSIONS provided.
        """
        embeddings = np.array(embeddings)

        if len(embeddings) < MIN_ENROLLMENT_SESSIONS:
            raise ValueError(
                f"Insufficient enrollment data: got {len(embeddings)} sessions, "
                f"need at least {MIN_ENROLLMENT_SESSIONS}. "
                f"User must complete more trusted sessions before baseline can be established."
            )

        # Cap at maximum to prevent over-smoothing
        if len(embeddings) > MAX_ENROLLMENT_SESSIONS:
            # Keep most recent sessions (recency bias)
            embeddings = embeddings[-MAX_ENROLLMENT_SESSIONS:]
            if weights is not None:
                weights = weights[-MAX_ENROLLMENT_SESSIONS:]

        # Weighted or uniform mean
        if weights is not None:
            weights = np.array(weights, dtype=np.float64)
            weights = weights / weights.sum()  # normalize to sum=1
            centroid = np.average(embeddings, axis=0, weights=weights)
        else:
            centroid = np.mean(embeddings, axis=0)

        # L2 normalize to unit sphere (essential for cosine similarity)
        norm = np.linalg.norm(centroid)
        if norm > 0:
            centroid = centroid / norm

        return centroid.astype(np.float32)

    def create_baseline_with_recency_weighting(
        self,
        embeddings: np.ndarray,
        recency_factor: float = 0.8
    ) -> np.ndarray:
        """
        Create baseline with exponential recency weighting.
        More recent sessions contribute more to the baseline.

        Args:
            embeddings: Array of shape (n_sessions, 384), chronologically ordered.
            recency_factor: Base of exponential decay. 0.8 means each older session
                           contributes 80% of the next newer one.

        Returns:
            Recency-weighted baseline of shape (384,), L2-normalized.
        """
        n = len(embeddings)
        # weights[i] = recency_factor^(n - 1 - i), so most recent = 1.0
        weights = np.array([recency_factor ** (n - 1 - i) for i in range(n)])
        return self.create_baseline(embeddings, weights=weights)

    # ═══════════════════════════════════════════════════════════════════════
    # ADAPTATION: Updating baseline over time (concept drift mitigation)
    # ═══════════════════════════════════════════════════════════════════════

    def update_baseline(
        self,
        current_baseline: np.ndarray,
        new_embedding: np.ndarray,
        trust_score: float,
        decay: float = EMA_DECAY
    ) -> Tuple[np.ndarray, bool]:
        """
        Conditionally update baseline using Exponential Moving Average.

        SECURITY CRITICAL: Only updates if trust_score > BASELINE_UPDATE_THRESHOLD.
        This prevents an attacker from poisoning the baseline during a takeover.

        The EMA formula:
            new_baseline = decay * old_baseline + (1 - decay) * current_embedding

        With decay=0.95, it takes ~20 high-trust sessions to significantly shift
        the baseline, making it resistant to short-term behavioral anomalies.

        Args:
            current_baseline: Existing baseline embedding (384,)
            new_embedding: Current session's embedding (384,)
            trust_score: Current Trust Score T(t) from trust engine
            decay: EMA decay factor (0.95 = slow adaptation, 0.80 = fast adaptation)

        Returns:
            Tuple of (updated_baseline, was_updated):
            - updated_baseline: New baseline (may be unchanged if trust too low)
            - was_updated: Boolean indicating whether update occurred
        """
        # SECURITY GATE: Block update if trust is insufficient
        if trust_score < BASELINE_UPDATE_THRESHOLD:
            return current_baseline, False

        # EMA update
        updated = decay * current_baseline + (1 - decay) * new_embedding

        # Re-normalize to unit sphere
        norm = np.linalg.norm(updated)
        if norm > 0:
            updated = updated / norm

        return updated.astype(np.float32), True

    # ═══════════════════════════════════════════════════════════════════════
    # VERIFICATION: Comparing current behavior against baseline
    # ═══════════════════════════════════════════════════════════════════════

    def verify_against_baseline(
        self,
        current_embedding: np.ndarray,
        baseline: np.ndarray
    ) -> Dict:
        """
        Compare a session's embedding against the user's stored baseline.
        This is the core identity verification operation.

        Args:
            current_embedding: Current session embedding (384,)
            baseline: User's stored baseline (384,)

        Returns:
            Dictionary with verification results:
            - similarity: cosine similarity [-1, 1]
            - drift_score: 1 - similarity [0, 2] (higher = more anomalous)
            - is_consistent: bool, whether behavior matches baseline
            - risk_level: "low" | "elevated" | "critical"
            - can_update_baseline: bool, whether this session is trusted enough to update
        """
        # Cosine similarity (dot product of normalized vectors)
        similarity = float(np.dot(current_embedding, baseline))
        similarity = np.clip(similarity, -1.0, 1.0)
        drift_score = 1.0 - similarity

        # Risk assessment based on proposal thresholds
        if similarity > 0.85:
            risk_level = "low"
            is_consistent = True
        elif similarity > 0.60:
            risk_level = "elevated"
            is_consistent = False
        else:
            risk_level = "critical"
            is_consistent = False

        # Only allow baseline updates for very high similarity sessions
        can_update = similarity > BASELINE_UPDATE_THRESHOLD

        return {
            "similarity": round(similarity, 6),
            "drift_score": round(drift_score, 6),
            "is_consistent": is_consistent,
            "risk_level": risk_level,
            "can_update_baseline": can_update,
        }

    # ═══════════════════════════════════════════════════════════════════════
    # QUALITY METRICS: Baseline reliability assessment
    # ═══════════════════════════════════════════════════════════════════════

    def compute_baseline_confidence(
        self,
        embeddings: np.ndarray,
        baseline: np.ndarray
    ) -> Dict:
        """
        Assess how reliable/tight the baseline is.
        A user with very consistent behavior will have high confidence.
        A user with wildly varying behavior will have lower confidence.

        Args:
            embeddings: All enrollment embeddings (n, 384)
            baseline: Computed baseline (384,)

        Returns:
            Dictionary with:
            - mean_similarity: Average similarity of sessions to baseline
            - min_similarity: Worst session similarity (weakest signal)
            - std_similarity: Spread of similarities (lower = more consistent user)
            - confidence_score: Overall confidence in baseline quality [0, 1]
            - session_count: Number of sessions used
        """
        similarities = np.array([
            float(np.dot(emb, baseline))
            for emb in embeddings
        ])

        mean_sim = float(np.mean(similarities))
        min_sim = float(np.min(similarities))
        std_sim = float(np.std(similarities))

        # Confidence formula: high mean, low spread, sufficient sessions
        session_factor = min(1.0, len(embeddings) / 10.0)  # saturates at 10 sessions
        consistency_factor = max(0.0, 1.0 - std_sim * 10)  # penalize high variance
        strength_factor = max(0.0, (mean_sim - 0.7) / 0.3)  # require mean > 0.7

        confidence = session_factor * consistency_factor * strength_factor
        confidence = float(np.clip(confidence, 0.0, 1.0))

        return {
            "mean_similarity": round(mean_sim, 6),
            "min_similarity": round(min_sim, 6),
            "std_similarity": round(std_sim, 6),
            "confidence_score": round(confidence, 4),
            "session_count": len(embeddings),
        }

    # ═══════════════════════════════════════════════════════════════════════
    # PERSISTENCE: Save/Load baselines to disk
    # ═══════════════════════════════════════════════════════════════════════

    def save_baseline(
        self,
        user_id: str,
        baseline: np.ndarray,
        metadata: Optional[Dict] = None
    ) -> Path:
        """
        Persist a user's baseline to disk.

        Args:
            user_id: Unique user identifier.
            baseline: Baseline embedding (384,).
            metadata: Optional metadata (session_count, confidence, timestamps).

        Returns:
            Path to saved file.
        """
        filepath = self.storage_dir / f"{user_id}.npz"

        save_data = {
            "baseline": baseline,
        }

        # Store metadata as JSON string in the npz
        meta = metadata or {}
        meta.setdefault("user_id", user_id)
        meta.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        meta.setdefault("updated_at", datetime.now(timezone.utc).isoformat())
        meta.setdefault("embedding_dim", int(baseline.shape[0]))

        save_data["metadata"] = np.array([json.dumps(meta)])

        np.savez_compressed(filepath, **save_data)
        return filepath

    def load_baseline(self, user_id: str) -> Tuple[Optional[np.ndarray], Optional[Dict]]:
        """
        Load a user's persisted baseline.

        Args:
            user_id: Unique user identifier.

        Returns:
            Tuple of (baseline_embedding, metadata) or (None, None) if not found.
        """
        filepath = self.storage_dir / f"{user_id}.npz"

        if not filepath.exists():
            return None, None

        data = np.load(filepath, allow_pickle=True)
        baseline = data["baseline"]

        metadata = None
        if "metadata" in data:
            metadata = json.loads(str(data["metadata"][0]))

        return baseline, metadata

    def baseline_exists(self, user_id: str) -> bool:
        """Check if a user has an established baseline."""
        filepath = self.storage_dir / f"{user_id}.npz"
        return filepath.exists()

    def delete_baseline(self, user_id: str) -> bool:
        """
        Delete a user's baseline (account closure, re-enrollment request).

        Returns:
            True if deleted, False if baseline didn't exist.
        """
        filepath = self.storage_dir / f"{user_id}.npz"
        if filepath.exists():
            filepath.unlink()
            return True
        return False

    def list_enrolled_users(self) -> List[str]:
        """List all user IDs with established baselines."""
        return [
            f.stem for f in self.storage_dir.glob("*.npz")
        ]
