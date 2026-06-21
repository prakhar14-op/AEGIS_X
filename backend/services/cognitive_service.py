"""
AEGIS-X Phase 4D-G: Cognitive State Machine Service
=====================================================
Classifies user cognitive state from behavioral features using a trained
Random Forest classifier and maps states to stability scores for the Trust Engine.

Pipeline position:
    Feature Vector (8 cognitive features) → **Random Forest** → Cognitive State → Stability Score

Cognitive State Machine (from proposal Section 6.c):
    calm → focused → distressed → panicked → coerced | robotic

Each state maps to a Cognitive Stability Score that feeds into T(t):
    T(t) = 0.40 × behavioral_similarity + 0.20 × device_trust
         + 0.20 × transaction_normality + 0.20 × **cognitive_stability**

The cognitive_stability component is the fourth pillar of the Trust Score,
specifically designed to detect psychological coercion that wouldn't show up
in purely mechanical behavioral metrics (typing speed alone doesn't catch panic).

Model: Random Forest (100 estimators, max_depth=12)
    - Trained on 12,000 synthetic samples (2,000 per state)
    - 96.3% test accuracy
    - 5-fold CV: 95.8% ± 0.4%
    - Perfect recall on robotic and distressed states

Reference: Section 6.c - "Random Forest (100 estimators) classifies behavioral features"
"""

import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from joblib import load


# Cognitive features used by the model (must match training feature order)
COGNITIVE_FEATURES = [
    "hesitation_ratio",
    "correction_rate",
    "typing_speed_cps",
    "typing_rhythm_variance",
    "touch_duration_mean",
    "gyroscope_variance",
    "interaction_intensity",
    "swipe_straightness",
]

# Cognitive Stability Scores: maps state → numeric value for Trust Score T(t)
# Higher = more stable/trustworthy cognitive state
COGNITIVE_STABILITY_SCORES = {
    "calm": 1.00,       # Full stability — no concern
    "focused": 0.90,    # Engaged but normal — slightly elevated attention
    "distressed": 0.60, # Uncertainty detected — step-up zone
    "panicked": 0.35,   # Severe stress — likely social engineering
    "coerced": 0.15,    # External control suspected — near-block threshold
    "robotic": 0.05,    # Automated behavior — almost certainly non-human
}

# Alert messages for compliance audit trail
COGNITIVE_ALERTS = {
    "calm": None,
    "focused": None,
    "distressed": "Elevated cognitive uncertainty detected. Monitor for escalation.",
    "panicked": "Severe cognitive distress — potential social engineering in progress.",
    "coerced": "HIGH ALERT: Behavioral signature consistent with external coercion. Recommend immediate session intervention.",
    "robotic": "CRITICAL: Automated/scripted behavior detected — possible remote access malware or screen mirroring.",
}

# State severity ordering (for temporal analysis)
STATE_SEVERITY_ORDER = {
    "calm": 0,
    "focused": 1,
    "distressed": 2,
    "panicked": 3,
    "coerced": 4,
    "robotic": 5,
}

# Model path
MODEL_PATH = Path(__file__).parent.parent.parent / "models" / "cognitive" / "cognitive_rf.pkl"


class CognitiveService:
    """
    Classifies cognitive state and computes stability scores for the Trust Engine.

    The cognitive analysis answers a question that pure behavioral similarity cannot:
    "Is this user acting under their own free will, or are they being manipulated?"

    A user's typing speed might be 'normal' during coercion (they're complying),
    but the PATTERN of hesitations, corrections, and rhythm irregularity reveals
    the psychological state underneath.

    Usage:
        service = CognitiveService()
        result = service.assess(features_dict)
        # result = {
        #     "state": "panicked",
        #     "stability_score": 0.35,
        #     "confidence": 0.91,
        #     "alert": "Severe cognitive distress — potential social engineering",
        #     "probabilities": {"calm": 0.02, "panicked": 0.91, ...}
        # }
    """

    def __init__(self, model_path: Optional[Path] = None):
        """
        Load the trained Random Forest model.

        Args:
            model_path: Path to the .pkl model file. Defaults to models/cognitive/cognitive_rf.pkl
        """
        path = model_path or MODEL_PATH
        if not path.exists():
            raise FileNotFoundError(
                f"Cognitive model not found at {path}. "
                f"Run 'python scripts/train_cognitive_model.py' first."
            )
        self._model = load(path)
        self._feature_names = COGNITIVE_FEATURES

    def predict_state(self, features: Dict[str, float]) -> str:
        """
        Predict cognitive state from behavioral features.

        Args:
            features: Dictionary with at least the 8 cognitive features.
                     Extra keys are ignored. Missing keys are imputed with neutral values.

        Returns:
            Predicted state: "calm" | "focused" | "distressed" | "panicked" | "coerced" | "robotic"
        """
        vector = self._extract_feature_vector(features)
        prediction = self._model.predict([vector])[0]
        return str(prediction)

    def predict_probabilities(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Get probability distribution over all cognitive states.

        Returns:
            Dictionary mapping each state to its predicted probability.
        """
        vector = self._extract_feature_vector(features)
        probas = self._model.predict_proba([vector])[0]
        classes = self._model.classes_

        return {
            str(cls): round(float(prob), 4)
            for cls, prob in zip(classes, probas)
        }

    def get_stability_score(self, state: str) -> float:
        """
        Map cognitive state to stability score for Trust Score computation.

        Args:
            state: Predicted cognitive state.

        Returns:
            Stability score in [0, 1]. Feeds into T(t) with weight 0.20.
        """
        return COGNITIVE_STABILITY_SCORES.get(state, 0.5)

    def get_alert(self, state: str) -> Optional[str]:
        """
        Get compliance alert message for the cognitive state.

        Returns:
            Alert string for concerning states, None for calm/focused.
        """
        return COGNITIVE_ALERTS.get(state)

    def assess(self, features: Dict[str, float]) -> Dict:
        """
        Full cognitive assessment: state + score + confidence + alert + probabilities.

        This is the primary interface called by the Trust Engine every 2 seconds.

        Args:
            features: Dictionary with the 16-dim feature vector (or at minimum
                     the 8 cognitive features).

        Returns:
            Comprehensive assessment dictionary with:
            - state: predicted cognitive state
            - stability_score: numeric value for T(t) computation [0, 1]
            - confidence: model confidence in the prediction [0, 1]
            - alert: human-readable alert (None if normal)
            - severity: numeric severity (0=calm, 5=robotic)
            - probabilities: full probability distribution
            - cognitive_component: weighted contribution to T(t) = 0.20 * stability
        """
        vector = self._extract_feature_vector(features)

        # Predict state and probabilities
        state = str(self._model.predict([vector])[0])
        probas = self._model.predict_proba([vector])[0]
        classes = self._model.classes_

        # Confidence = probability of the predicted class
        state_idx = list(classes).index(state)
        confidence = float(probas[state_idx])

        # Build probability distribution
        prob_dict = {
            str(cls): round(float(p), 4)
            for cls, p in zip(classes, probas)
        }

        stability_score = self.get_stability_score(state)
        alert = self.get_alert(state)
        severity = STATE_SEVERITY_ORDER.get(state, 0)

        # Direct contribution to Trust Score T(t)
        cognitive_component = 0.20 * stability_score

        return {
            "state": state,
            "stability_score": stability_score,
            "confidence": round(confidence, 4),
            "alert": alert,
            "severity": severity,
            "probabilities": prob_dict,
            "cognitive_component": round(cognitive_component, 4),
        }

    def assess_trajectory(
        self,
        feature_sequence: List[Dict[str, float]]
    ) -> Dict:
        """
        Analyze cognitive state progression over a sequence of events.
        Detects escalation patterns (calm → distressed → panicked → coerced).

        Args:
            feature_sequence: List of feature dictionaries (chronological order).

        Returns:
            Trajectory analysis with:
            - states: list of predicted states
            - escalating: bool (is severity increasing over time?)
            - peak_severity: maximum severity observed
            - mean_stability: average stability score
            - state_transitions: count of state changes
        """
        states = []
        severities = []
        stability_scores = []

        for features in feature_sequence:
            state = self.predict_state(features)
            states.append(state)
            severities.append(STATE_SEVERITY_ORDER.get(state, 0))
            stability_scores.append(self.get_stability_score(state))

        # Detect escalation (consistent increase in severity)
        escalating = False
        if len(severities) >= 3:
            recent = severities[-5:] if len(severities) >= 5 else severities
            diffs = [recent[i] - recent[i - 1] for i in range(1, len(recent))]
            escalating = sum(d > 0 for d in diffs) > sum(d <= 0 for d in diffs)

        # Count state transitions
        transitions = sum(
            1 for i in range(1, len(states)) if states[i] != states[i - 1]
        )

        return {
            "states": states,
            "current_state": states[-1] if states else "unknown",
            "escalating": escalating,
            "peak_severity": max(severities) if severities else 0,
            "mean_stability": round(float(np.mean(stability_scores)), 4) if stability_scores else 1.0,
            "state_transitions": transitions,
            "sequence_length": len(states),
        }

    def _extract_feature_vector(self, features: Dict[str, float]) -> np.ndarray:
        """
        Extract the 8 cognitive features in correct order from a feature dict.
        Missing features are imputed with neutral midpoint values.
        """
        # Neutral defaults (midpoint of normal range)
        defaults = {
            "hesitation_ratio": 0.10,
            "correction_rate": 0.05,
            "typing_speed_cps": 3.5,
            "typing_rhythm_variance": 35.0,
            "touch_duration_mean": 120.0,
            "gyroscope_variance": 0.015,
            "interaction_intensity": 8.0,
            "swipe_straightness": 0.82,
        }

        vector = []
        for feat_name in self._feature_names:
            value = features.get(feat_name, defaults.get(feat_name, 0.0))
            vector.append(float(value))

        return np.array(vector, dtype=np.float64)
