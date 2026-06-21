"""
Maintains a sliding window of similarity scores for temporal analysis.

Why history matters:
    A single similarity score (e.g., 0.93) is meaningless in isolation.
    Fraud is a PATTERN — progressive degradation over time:
        Normal:     [0.96, 0.95, 0.96, 0.95, 0.97]  → stable, no concern
        Takeover:   [0.96, 0.93, 0.89, 0.84, 0.76]  → clear downward trend
        Scam:       [0.85, 0.72, 0.80, 0.65, 0.73]  → oscillating, unstable

    CUSUM, trust velocity (dT/dt), and trust acceleration (d²T/dt²) all require
    historical context to compute. This buffer provides that context.

The buffer stores the last 50 similarity scores (100 seconds of behavioral data
at the 2-second SDK heartbeat rate), which is sufficient to detect:
    - Gradual drift (account takeover over 20+ steps)
    - Sudden jumps (malware injection)
    - Oscillating patterns (coercion/social engineering)

"""

import numpy as np
from collections import deque
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone


class SimilarityHistory:
    """
    Sliding-window buffer for similarity score time series.

    Stores the most recent N similarity scores and computes temporal
    statistics that feed into drift detection and trust scoring.

    Each entry is a tuple of (timestamp, similarity_score) to enable
    time-aware analysis (e.g., rate of change per second).
    """

    def __init__(self, max_length: int = 50):
        """
        Args:
            max_length: Maximum scores to retain. At 2s intervals,
                       50 entries = 100 seconds of behavioral history.
        """
        self.max_length = max_length
        self._scores: deque = deque(maxlen=max_length)
        self._timestamps: deque = deque(maxlen=max_length)

    def add(self, score: float, timestamp: Optional[datetime] = None):
        """
        Record a new similarity score.

        Args:
            score: Cosine similarity value from SimilarityService.
            timestamp: When this score was computed. Defaults to now.
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        self._scores.append(score)
        self._timestamps.append(timestamp)

    def get_scores(self) -> List[float]:
        """Return all stored similarity scores (oldest first)."""
        return list(self._scores)

    def get_latest(self, n: int = 1) -> List[float]:
        """Return the N most recent scores."""
        scores = list(self._scores)
        return scores[-n:] if n <= len(scores) else scores

    @property
    def length(self) -> int:
        """Current number of stored scores."""
        return len(self._scores)

    @property
    def is_full(self) -> bool:
        """Whether buffer has reached maximum capacity."""
        return len(self._scores) >= self.max_length

    def clear(self):
        """Reset the history buffer (new session start)."""
        self._scores.clear()
        self._timestamps.clear()

    # ═══════════════════════════════════════════════════════════════════════
    # TEMPORAL DYNAMICS (feeds into Trust Score temporal components)
    # ═══════════════════════════════════════════════════════════════════════

    def trust_velocity(self) -> float:
        """
        Compute Trust Velocity: dT/dt — rate of trust change.

        Positive = trust recovering (user returning to normal)
        Negative = trust decaying (behavioral divergence increasing)
        Zero = stable behavior

        Uses the last 5 scores for a smooth derivative estimate.

        Reference: Section 6.a - "Trust Velocity (dT/dt)"
        """
        scores = self.get_scores()
        if len(scores) < 2:
            return 0.0

        # Use last 5 scores for smoothed derivative
        window = scores[-min(5, len(scores)):]
        # Linear regression slope (simple finite difference)
        if len(window) < 2:
            return 0.0

        # dT/dt ≈ (T[n] - T[n-k]) / k, averaged over window
        deltas = [window[i] - window[i - 1] for i in range(1, len(window))]
        return float(np.mean(deltas))

    def trust_acceleration(self) -> float:
        """
        Compute Trust Acceleration: d²T/dt² — is trust decaying faster or slower?

        Negative acceleration + negative velocity = ACCELERATING DECAY (very bad)
        Positive acceleration + negative velocity = DECELERATING DECAY (recovering)

        Reference: Section 6.a - "Acceleration (d²T/dt²)"
        """
        scores = self.get_scores()
        if len(scores) < 3:
            return 0.0

        window = scores[-min(8, len(scores)):]
        if len(window) < 3:
            return 0.0

        # Second derivative: finite differences
        first_derivatives = [window[i] - window[i - 1] for i in range(1, len(window))]
        second_derivatives = [
            first_derivatives[i] - first_derivatives[i - 1]
            for i in range(1, len(first_derivatives))
        ]

        return float(np.mean(second_derivatives)) if second_derivatives else 0.0

    def trust_entropy(self) -> float:
        """
        Compute Trust Entropy: H(t) — behavioral unpredictability.

        High entropy = erratic, oscillating behavior (social engineering signature)
        Low entropy = stable or consistently declining (normal or takeover)

        Computed as normalized standard deviation of recent scores.

        Reference: Section 6.a - "Entropy H(t)"
        """
        scores = self.get_scores()
        if len(scores) < 3:
            return 0.0

        window = scores[-min(10, len(scores)):]
        std = float(np.std(window))
        # Normalize: std of 0.1 in similarity space is already quite high
        entropy = min(1.0, std / 0.1)
        return round(entropy, 6)

    def compute_temporal_dynamics(self) -> Dict:
        """
        Compute all temporal dynamics in one call.

        Returns:
            Dictionary with:
            - velocity: dT/dt (rate of change)
            - acceleration: d²T/dt² (rate of rate change)
            - entropy: H(t) (behavioral unpredictability)
            - trend: "stable" | "declining" | "recovering" | "oscillating"
            - window_size: number of scores used
        """
        velocity = self.trust_velocity()
        acceleration = self.trust_acceleration()
        entropy = self.trust_entropy()

        # Classify trend pattern
        if entropy > 0.5:
            trend = "oscillating"  # Social engineering signature
        elif velocity < -0.02:
            trend = "declining"  # Account takeover signature
        elif velocity > 0.02:
            trend = "recovering"
        else:
            trend = "stable"

        return {
            "velocity": round(velocity, 6),
            "acceleration": round(acceleration, 6),
            "entropy": entropy,
            "trend": trend,
            "window_size": self.length,
        }

    # ═══════════════════════════════════════════════════════════════════════
    # STATISTICAL SUMMARY
    # ═══════════════════════════════════════════════════════════════════════

    def statistics(self) -> Dict:
        """
        Compute summary statistics over the buffer.

        Returns:
            Dictionary with mean, min, max, std, current, and temporal dynamics.
        """
        scores = self.get_scores()
        if not scores:
            return {
                "mean": 0.0, "min": 0.0, "max": 0.0,
                "std": 0.0, "current": 0.0, "count": 0,
            }

        dynamics = self.compute_temporal_dynamics()

        return {
            "mean": round(float(np.mean(scores)), 6),
            "min": round(float(np.min(scores)), 6),
            "max": round(float(np.max(scores)), 6),
            "std": round(float(np.std(scores)), 6),
            "current": round(scores[-1], 6),
            "count": len(scores),
            **dynamics,
        }
