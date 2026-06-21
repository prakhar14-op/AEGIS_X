"""
Aggregates signals from similarity, drift (CUSUM), and temporal dynamics
into a single risk evaluation with actionable output.

    LOW_RISK    → [ALLOW]   Continue normally
    MEDIUM_RISK → [STEP-UP] Require biometric/OTP verification
    HIGH_RISK   → [BLOCK]   Terminate session, flag for review
"""

import numpy as np
from typing import Dict, Optional
from datetime import datetime, timezone


class RiskService:
    """
    Aggregates multiple fraud signals into a unified risk assessment.

    Input signals:
    1. Similarity score (behavioral_similarity component)
    2. CUSUM drift detection result
    3. Temporal dynamics (velocity, acceleration, entropy)
    4. Drift severity level

    Output:
    - Risk level: LOW_RISK | MEDIUM_RISK | HIGH_RISK | CRITICAL
    - Recommended action: ALLOW | STEP_UP | BLOCK
    - Confidence: how certain we are about the assessment
    - Reasoning: human-readable explanation (for compliance audit trail)
    """

    def evaluate(
        self,
        similarity: float,
        drift_detected: bool,
        drift_severity: str = "none",
        trust_velocity: float = 0.0,
        trust_entropy: float = 0.0,
        cusum_value: float = 0.0,
    ) -> Dict:
        """
        Perform unified risk evaluation from all available signals.

        Args:
            similarity: Current cosine similarity to baseline [0, 1]
            drift_detected: Whether CUSUM has triggered
            drift_severity: "none" | "low" | "medium" | "high" | "critical"
            trust_velocity: dT/dt from history buffer (negative = decaying)
            trust_entropy: H(t) from history buffer (high = oscillating)
            cusum_value: Current CUSUM accumulation

        Returns:
            Comprehensive risk assessment dictionary.
        """
        # ─── COMPUTE RISK SCORE (0-1, higher = more risky) ────────────────
        risk_score = self._compute_risk_score(
            similarity, drift_detected, drift_severity,
            trust_velocity, trust_entropy, cusum_value
        )

        # ─── CLASSIFY RISK LEVEL ──────────────────────────────────────────
        risk_level = self._classify_risk(risk_score, similarity, drift_severity)

        # ─── DETERMINE ACTION ─────────────────────────────────────────────
        action = self._determine_action(risk_level, similarity)

        # ─── GENERATE REASONING ───────────────────────────────────────────
        reasons = self._generate_reasons(
            similarity, drift_detected, drift_severity,
            trust_velocity, trust_entropy
        )

        # ─── DETECT ATTACK PATTERN ────────────────────────────────────────
        attack_pattern = self._identify_attack_pattern(
            similarity, drift_severity, trust_velocity, trust_entropy
        )

        return {
            "risk_score": round(risk_score, 4),
            "risk_level": risk_level,
            "action": action,
            "confidence": round(self._compute_confidence(risk_score), 4),
            "attack_pattern": attack_pattern,
            "reasons": reasons,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "signals": {
                "similarity": round(similarity, 6),
                "drift_detected": drift_detected,
                "drift_severity": drift_severity,
                "trust_velocity": round(trust_velocity, 6),
                "trust_entropy": round(trust_entropy, 6),
                "cusum_value": round(cusum_value, 6),
            },
        }

    def _compute_risk_score(
        self,
        similarity: float,
        drift_detected: bool,
        drift_severity: str,
        trust_velocity: float,
        trust_entropy: float,
        cusum_value: float,
    ) -> float:
        """
        Compute a composite risk score from all signals.

        Weighted combination:
        - Similarity inverse: 40% (primary behavioral signal)
        - Drift detection: 25% (CUSUM accumulated evidence)
        - Velocity signal: 20% (rate of deterioration)
        - Entropy signal: 15% (behavioral instability)
        """
        # Similarity contribution (inverted: low similarity = high risk)
        sim_risk = max(0.0, 1.0 - similarity)

        # Drift contribution
        severity_weights = {
            "none": 0.0, "low": 0.3, "medium": 0.6, "high": 0.85, "critical": 1.0
        }
        drift_risk = severity_weights.get(drift_severity, 0.0)
        if drift_detected:
            drift_risk = max(drift_risk, 0.5)

        # Velocity contribution (negative velocity = increasing risk)
        velocity_risk = max(0.0, min(1.0, -trust_velocity * 10))

        # Entropy contribution (high entropy = oscillating = social engineering)
        entropy_risk = min(1.0, trust_entropy)

        # Weighted combination
        risk_score = (
            0.40 * sim_risk
            + 0.25 * drift_risk
            + 0.20 * velocity_risk
            + 0.15 * entropy_risk
        )

        return float(np.clip(risk_score, 0.0, 1.0))

    def _classify_risk(
        self, risk_score: float, similarity: float, drift_severity: str
    ) -> str:
        """Classify risk into discrete levels."""
        # Override: critical drift severity = always CRITICAL
        if drift_severity == "critical":
            return "CRITICAL"

        # Override: very low similarity = always HIGH_RISK
        if similarity < 0.50:
            return "CRITICAL"

        if risk_score > 0.70:
            return "HIGH_RISK"
        elif risk_score > 0.40:
            return "MEDIUM_RISK"
        elif risk_score > 0.15:
            return "LOW_RISK"
        return "MINIMAL"

    def _determine_action(self, risk_level: str, similarity: float) -> str:
        """
        Map risk level to concrete action.
        Aligns with proposal: [ALLOW] T>0.85 | [STEP-UP] 0.60-0.85 | [BLOCK] T<0.60
        """
        action_map = {
            "MINIMAL": "ALLOW",
            "LOW_RISK": "ALLOW",
            "MEDIUM_RISK": "STEP_UP",
            "HIGH_RISK": "BLOCK",
            "CRITICAL": "BLOCK",
        }
        return action_map.get(risk_level, "STEP_UP")

    def _compute_confidence(self, risk_score: float) -> float:
        """
        Confidence in the risk assessment.
        High confidence when risk_score is far from decision boundaries.
        Low confidence when near threshold boundaries.
        """
        boundaries = [0.15, 0.40, 0.70]
        min_distance = min(abs(risk_score - b) for b in boundaries)
        return min(1.0, min_distance / 0.15)

    def _identify_attack_pattern(
        self,
        similarity: float,
        drift_severity: str,
        trust_velocity: float,
        trust_entropy: float,
    ) -> str:
        """
        Identify which attack scenario matches the current signals.
        Maps to proposal Section 7.c demo scenarios.
        """
        # Malware: high similarity but robotic (caught by other means)
        # Actually malware has low hesitation but moderate similarity
        if similarity > 0.80 and trust_entropy < 0.1 and trust_velocity < -0.01:
            return "possible_account_takeover"

        if trust_entropy > 0.5:
            return "possible_social_engineering"

        if trust_velocity < -0.03 and drift_severity in ("medium", "high", "critical"):
            return "possible_account_takeover"

        if similarity < 0.60:
            return "severe_behavioral_mismatch"

        if drift_severity in ("high", "critical"):
            return "significant_drift"

        return "normal"

    def _generate_reasons(
        self,
        similarity: float,
        drift_detected: bool,
        drift_severity: str,
        trust_velocity: float,
        trust_entropy: float,
    ) -> list:
        """
        Generate human-readable reasons for the risk assessment.
        Used in compliance audit trail and dashboard alerts.
        """
        reasons = []

        if similarity < 0.60:
            reasons.append("Behavioral similarity critically low — likely different user.")
        elif similarity < 0.75:
            reasons.append("Significant behavioral deviation from established baseline.")
        elif similarity < 0.90:
            reasons.append("Moderate behavioral variation detected.")

        if drift_detected:
            reasons.append(f"CUSUM drift detector triggered (severity: {drift_severity}).")

        if trust_velocity < -0.03:
            reasons.append("Trust score declining rapidly (negative velocity).")
        elif trust_velocity < -0.01:
            reasons.append("Slow trust erosion detected.")

        if trust_entropy > 0.5:
            reasons.append("Behavioral pattern oscillating — possible coercion indicator.")
        elif trust_entropy > 0.3:
            reasons.append("Elevated behavioral unpredictability.")

        if not reasons:
            reasons.append("All signals within normal operating parameters.")

        return reasons
