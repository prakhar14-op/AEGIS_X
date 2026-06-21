"""
The Session Manager is the CENTRAL NERVOUS SYSTEM of AEGIS-X. It orchestrates
the entire trust pipeline for every active user session, maintaining state
between WebSocket heartbeats and coordinating all downstream services.

What lives inside a session:
    - user_id + session_id (identity)
    - baseline embedding (the trusted behavioral fingerprint)
    - CUSUM detector state (accumulated drift evidence)
    - similarity history buffer (temporal dynamics: dT/dt, d²T/dt²)
    - trust score history (for velocity/acceleration computation)
    - cognitive state trajectory (escalation detection)
    - event count + timestamps (session metadata)
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from collections import deque
import uuid

from backend.services.feature_engineering import FeatureEngineer
from backend.services.serializer import BehavioralSerializer
from backend.services.embedding_service import EmbeddingService
from backend.services.baseline_service import BaselineService
from backend.services.similarity_service import SimilarityService
from backend.services.history_service import SimilarityHistory
from backend.services.drift_service import CUSUMDetector
from backend.services.cognitive_service import CognitiveService
from backend.services.trust_service import TrustService, TransactionScorer
from backend.services.decision_service import DecisionService


# Session configuration
SESSION_TTL_SECONDS = 1800          # 30 minutes inactivity → expire
MAX_EVENT_HISTORY = 100             # Store last 100 raw events per session
MAX_TRUST_HISTORY = 50              # Last 50 trust scores (100s at 2s rate)
BASELINE_UPDATE_INTERVAL = 10       # Check baseline update every 10 events


@dataclass
class SessionState:
    """
    Complete state container for one active user session.

    This is the in-memory representation of everything we know about
    a user's current session. Updated every 2 seconds via process_event().
    """
    # Identity
    user_id: str
    session_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Behavioral baseline (loaded from storage at session start)
    baseline: Optional[np.ndarray] = None

    # Per-session detectors (fresh state per session)
    cusum_detector: CUSUMDetector = field(default_factory=CUSUMDetector)
    similarity_history: SimilarityHistory = field(default_factory=SimilarityHistory)
    trust_engine: TrustService = field(default_factory=TrustService)

    # Session history
    event_count: int = 0
    cognitive_trajectory: List[str] = field(default_factory=list)
    trust_trajectory: List[float] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)

    # Latest state (cached for dashboard queries)
    latest_trust_score: float = 1.0
    latest_cognitive_state: str = "calm"
    latest_similarity: float = 1.0
    latest_decision: str = "ALLOW"
    latest_drift_detected: bool = False

    # Session flags
    is_active: bool = True
    is_blocked: bool = False
    block_reason: Optional[str] = None

    @property
    def duration_seconds(self) -> float:
        """How long this session has been active."""
        return (datetime.now(timezone.utc) - self.created_at).total_seconds()

    @property
    def is_expired(self) -> bool:
        """Whether session has been inactive too long."""
        elapsed = (datetime.now(timezone.utc) - self.last_activity).total_seconds()
        return elapsed > SESSION_TTL_SECONDS


class SessionManager:
    """
    Orchestrates the real-time trust pipeline for all active sessions.

    This is the top-level component that:
    1. Manages session lifecycle (create/process/destroy)
    2. Coordinates all ML services per event
    3. Maintains per-session state (CUSUM, history, trajectory)
    4. Returns trust decisions to the WebSocket layer

    Usage (from WebSocket handler):
        manager = SessionManager()

        # User connects
        session = manager.create_session(user_id="user_123")

        # Every 2s SDK heartbeat
        result = manager.process_event(user_id="user_123", raw_event={...})
        # result["decision"]["action"] == "ALLOW" | "STEP_UP" | "BLOCK"

        # User disconnects
        manager.end_session(user_id="user_123")
    """

    def __init__(self):
        """Initialize the session manager with all pipeline services."""
        # Shared services (stateless, thread-safe)
        self._feature_engineer = FeatureEngineer()
        self._serializer = BehavioralSerializer()
        self._embedding_service = EmbeddingService()
        self._baseline_service = BaselineService()
        self._similarity_service = SimilarityService()
        self._cognitive_service = CognitiveService()
        self._transaction_scorer = TransactionScorer()
        self._decision_service = DecisionService()

        # Active sessions (in-memory for MVP; Redis-backed in production)
        self._sessions: Dict[str, SessionState] = {}

    # ═══════════════════════════════════════════════════════════════════════
    # SESSION LIFECYCLE
    # ═══════════════════════════════════════════════════════════════════════

    def create_session(self, user_id: str, session_id: Optional[str] = None) -> Dict:
        """
        Initialize a new trust session for a user.

        Called when user opens the app / authenticates.
        Loads their behavioral baseline and prepares fresh detectors.

        Args:
            user_id: Unique user identifier.
            session_id: Optional session ID. Generated if not provided.

        Returns:
            Session creation confirmation with initial state.
        """
        if session_id is None:
            session_id = f"sess_{uuid.uuid4().hex[:12]}"

        # Load user's baseline (or None if not enrolled)
        baseline, metadata = self._baseline_service.load_baseline(user_id)

        # Create session state
        session = SessionState(
            user_id=user_id,
            session_id=session_id,
            baseline=baseline,
        )

        # Store in active sessions
        self._sessions[user_id] = session

        has_baseline = baseline is not None
        return {
            "user_id": user_id,
            "session_id": session_id,
            "has_baseline": has_baseline,
            "status": "active",
            "message": (
                "Session created with established baseline."
                if has_baseline
                else "Session created — user in enrollment phase (no baseline yet)."
            ),
        }

    def end_session(self, user_id: str) -> Dict:
        """
        Terminate a user session and cleanup resources.

        Called when user logs out or session expires.
        Optionally updates baseline if session was trusted.

        Args:
            user_id: User whose session to end.

        Returns:
            Session summary statistics.
        """
        session = self._sessions.pop(user_id, None)
        if session is None:
            return {"status": "not_found", "user_id": user_id}

        session.is_active = False

        # Session summary
        return {
            "user_id": user_id,
            "session_id": session.session_id,
            "status": "ended",
            "duration_seconds": round(session.duration_seconds, 1),
            "total_events": session.event_count,
            "final_trust_score": round(session.latest_trust_score, 4),
            "final_decision": session.latest_decision,
            "was_blocked": session.is_blocked,
            "cognitive_states_observed": list(set(session.cognitive_trajectory)),
            "drift_detected": session.latest_drift_detected,
        }

    def get_session(self, user_id: str) -> Optional[SessionState]:
        """Get active session for a user (None if not found)."""
        return self._sessions.get(user_id)

    def get_active_sessions(self) -> List[Dict]:
        """List all active sessions (for dashboard monitoring)."""
        return [
            {
                "user_id": s.user_id,
                "session_id": s.session_id,
                "duration": round(s.duration_seconds, 1),
                "events": s.event_count,
                "trust_score": round(s.latest_trust_score, 4),
                "cognitive_state": s.latest_cognitive_state,
                "decision": s.latest_decision,
                "drift_detected": s.latest_drift_detected,
            }
            for s in self._sessions.values()
            if s.is_active and not s.is_expired
        ]

    # ═══════════════════════════════════════════════════════════════════════
    # CORE PIPELINE: Process a single behavioral event
    # ═══════════════════════════════════════════════════════════════════════

    def process_event(
        self,
        user_id: str,
        raw_event: Dict,
        transaction_amount: float = 0.0,
        is_new_beneficiary: bool = False,
    ) -> Dict:
        """
        Process a single 2-second behavioral heartbeat through the full trust pipeline.

        THIS IS THE MAIN ENTRY POINT — called every 2 seconds by the WebSocket handler.

        Pipeline execution (10 steps, target < 100ms total):
            1. Extract 16-dim feature vector
            2. Serialize to behavioral text
            3. Generate 384-dim MiniLM embedding
            4. Compute cosine similarity vs baseline
            5. Update CUSUM drift detector
            6. Classify cognitive state
            7. Score transaction normality
            8. Compute Trust Score T(t)
            9. Make ALLOW/STEP_UP/BLOCK decision
            10. Update session state

        Args:
            user_id: User identifier (must have active session).
            raw_event: Raw behavioral telemetry from SDK (16 features).
            transaction_amount: Amount of pending transaction (₹0 if browsing).
            is_new_beneficiary: Whether transfer target is new/unknown.

        Returns:
            Complete trust update for WebSocket response:
            - trust_score, decision, cognitive_state, drift, temporal dynamics, etc.
        """
        # ─── VALIDATE SESSION ──────────────────────────────────────────────
        session = self._sessions.get(user_id)
        if session is None:
            return {"error": "no_active_session", "user_id": user_id}

        if session.is_blocked:
            return {
                "error": "session_blocked",
                "reason": session.block_reason,
                "action": "BLOCK",
            }

        # ─── STEP 1: Feature Extraction ───────────────────────────────────
        features = self._feature_engineer.extract(raw_event)

        # ─── STEP 2: Behavioral Serialization ─────────────────────────────
        behavioral_text = self._serializer.serialize(features)

        # ─── STEP 3: Generate 384-dim Embedding ───────────────────────────
        current_embedding = self._embedding_service.generate_embedding(behavioral_text)

        # ─── STEP 4: Similarity vs Baseline ───────────────────────────────
        if session.baseline is not None:
            similarity = self._similarity_service.calculate_similarity(
                session.baseline, current_embedding
            )
        else:
            # No baseline yet (enrollment phase) — assume trusted
            similarity = 1.0

        # ─── STEP 5: CUSUM Drift Detection ────────────────────────────────
        drift_result = session.cusum_detector.update(similarity)

        # ─── STEP 6: Similarity History + Temporal Dynamics ────────────────
        session.similarity_history.add(similarity)
        temporal = session.similarity_history.compute_temporal_dynamics()

        # ─── STEP 7: Cognitive State Classification ────────────────────────
        cognitive_result = self._cognitive_service.assess(features)

        # ─── STEP 8: Transaction Normality ─────────────────────────────────
        tx_result = self._transaction_scorer.score_transaction(
            amount=transaction_amount,
            is_new_beneficiary=is_new_beneficiary,
        )

        # ─── STEP 9: Trust Score T(t) ─────────────────────────────────────
        trust_result = session.trust_engine.compute(
            behavioral_similarity=similarity,
            device_trust=1.0,  # MVP: same device assumed
            transaction_normality=tx_result["score"],
            cognitive_stability=cognitive_result["stability_score"],
            drift_detected=drift_result["drift_detected"],
            drift_severity=drift_result["severity"],
        )

        # ─── STEP 10: Decision ─────────────────────────────────────────────
        decision_result = self._decision_service.decide(
            trust_score=trust_result["effective_trust"],
            trust_velocity=trust_result["temporal"]["velocity"],
            drift_detected=drift_result["drift_detected"],
            drift_severity=drift_result["severity"],
            cognitive_state=cognitive_result["state"],
            transaction_amount=transaction_amount,
        )

        # ─── UPDATE SESSION STATE ──────────────────────────────────────────
        session.event_count += 1
        session.last_activity = datetime.now(timezone.utc)
        session.latest_trust_score = trust_result["trust_score"]
        session.latest_cognitive_state = cognitive_result["state"]
        session.latest_similarity = similarity
        session.latest_decision = decision_result["action"]
        session.latest_drift_detected = drift_result["drift_detected"]

        # Trajectory tracking (for temporal analysis)
        session.cognitive_trajectory.append(cognitive_result["state"])
        if len(session.cognitive_trajectory) > MAX_TRUST_HISTORY:
            session.cognitive_trajectory = session.cognitive_trajectory[-MAX_TRUST_HISTORY:]

        session.trust_trajectory.append(trust_result["trust_score"])
        if len(session.trust_trajectory) > MAX_TRUST_HISTORY:
            session.trust_trajectory = session.trust_trajectory[-MAX_TRUST_HISTORY:]

        session.decisions.append(decision_result["action"])

        # ─── BLOCK SESSION IF CRITICAL ─────────────────────────────────────
        if decision_result["action"] == "BLOCK":
            session.is_blocked = True
            session.block_reason = decision_result["explanation"]

        # ─── CONDITIONAL BASELINE UPDATE ───────────────────────────────────
        if (session.baseline is not None
                and session.event_count % BASELINE_UPDATE_INTERVAL == 0
                and trust_result["trust_score"] > 0.90):
            updated_baseline, was_updated = self._baseline_service.update_baseline(
                current_baseline=session.baseline,
                new_embedding=current_embedding,
                trust_score=trust_result["trust_score"],
            )
            if was_updated:
                session.baseline = updated_baseline

        # ─── BUILD RESPONSE (WebSocket payload format) ─────────────────────
        return {
            "type": "trust_update",
            "user_id": user_id,
            "session_id": session.session_id,
            "event_number": session.event_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trust_state": {
                "trust_score": round(trust_result["trust_score"], 4),
                "effective_trust": round(trust_result["effective_trust"], 4),
                "trust_level": trust_result["trust_level"],
                "drift_score": round(drift_result["cusum_value"], 4),
                "cognitive_state": cognitive_result["state"],
                "cognitive_stability": cognitive_result["stability_score"],
                "action": decision_result["action"],
            },
            "temporal_dynamics": {
                "velocity": round(trust_result["temporal"]["velocity"], 6),
                "acceleration": round(trust_result["temporal"]["acceleration"], 6),
                "trend": trust_result["temporal"]["trend"],
                "entropy": temporal["entropy"],
            },
            "drift": {
                "detected": drift_result["drift_detected"],
                "severity": drift_result["severity"],
                "cusum_value": round(drift_result["cusum_value"], 4),
                "instant_jump": drift_result["instant_jump"],
            },
            "decision": {
                "action": decision_result["action"],
                "confidence": decision_result["confidence"],
                "reasons": decision_result["reasons"],
                "step_up_methods": decision_result.get("step_up_methods", []),
            },
            "similarity": {
                "current": round(similarity, 4),
                "mean": round(session.similarity_history.statistics().get("mean", 1.0), 4),
            },
        }

    # ═══════════════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════════════════════

    def get_session_summary(self, user_id: str) -> Optional[Dict]:
        """Get current session status for dashboard display."""
        session = self._sessions.get(user_id)
        if session is None:
            return None

        return {
            "user_id": session.user_id,
            "session_id": session.session_id,
            "duration_seconds": round(session.duration_seconds, 1),
            "event_count": session.event_count,
            "is_active": session.is_active,
            "is_blocked": session.is_blocked,
            "current_state": {
                "trust_score": round(session.latest_trust_score, 4),
                "cognitive_state": session.latest_cognitive_state,
                "similarity": round(session.latest_similarity, 4),
                "decision": session.latest_decision,
                "drift_detected": session.latest_drift_detected,
            },
            "trajectory": {
                "trust_scores": session.trust_trajectory[-10:],
                "cognitive_states": session.cognitive_trajectory[-10:],
                "decisions": session.decisions[-10:],
            },
        }

    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions. Returns count of cleaned sessions."""
        expired_users = [
            uid for uid, s in self._sessions.items()
            if s.is_expired
        ]
        for uid in expired_users:
            self._sessions.pop(uid, None)
        return len(expired_users)

    @property
    def active_session_count(self) -> int:
        """Number of currently active sessions."""
        return sum(1 for s in self._sessions.values() if s.is_active and not s.is_expired)
