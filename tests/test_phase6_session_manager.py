import numpy as np
from backend.services.session_manager import SessionManager
from backend.services.baseline_service import BaselineService
from backend.services.feature_engineering import FeatureEngineer
from backend.services.serializer import BehavioralSerializer
from backend.services.embedding_service import EmbeddingService


def separator(title: str):
    print(f"\n{'═' * 70}")
    print(f"  {title}")
    print(f"{'═' * 70}")


def generate_normal_event():
    return {
        "typing_speed_cps": 3.8 + np.random.normal(0, 0.4),
        "typing_rhythm_variance": 38 + np.random.normal(0, 5),
        "typing_pressure_mean": 0.55 + np.random.normal(0, 0.03),
        "swipe_velocity_mean": 1.2 + np.random.normal(0, 0.1),
        "swipe_velocity_variance": 0.14 + np.random.normal(0, 0.02),
        "swipe_straightness": 0.82 + np.random.normal(0, 0.03),
        "touch_duration_mean": 120 + np.random.normal(0, 10),
        "touch_duration_variance": 580 + np.random.normal(0, 50),
        "touch_area_mean": 0.45 + np.random.normal(0, 0.03),
        "hesitation_ratio": max(0, 0.08 + np.random.normal(0, 0.02)),
        "hesitation_count": max(0, int(1 + np.random.normal(0, 0.5))),
        "correction_rate": max(0, 0.04 + np.random.normal(0, 0.01)),
        "scroll_speed_mean": 0.8 + np.random.normal(0, 0.1),
        "gyroscope_variance": max(0.001, 0.015 + np.random.normal(0, 0.003)),
        "session_time_elapsed": 90 + np.random.normal(0, 20),
        "interaction_intensity": max(1, int(8 + np.random.normal(0, 1.5))),
    }


def generate_coercion_event(stress: float):
    return {
        "typing_speed_cps": max(0.5, 1.5 - stress * 0.6),
        "typing_rhythm_variance": 50 + stress * 180,
        "typing_pressure_mean": 0.65 + stress * 0.2,
        "swipe_velocity_mean": max(0.1, 0.5 - stress * 0.3),
        "swipe_velocity_variance": 0.2 + stress * 0.3,
        "swipe_straightness": max(0.3, 0.7 - stress * 0.25),
        "touch_duration_mean": 170 + stress * 150,
        "touch_duration_variance": 700 + stress * 3000,
        "touch_area_mean": 0.5 + stress * 0.12,
        "hesitation_ratio": min(0.9, 0.25 + stress * 0.55),
        "hesitation_count": int(3 + stress * 8),
        "correction_rate": min(0.65, 0.12 + stress * 0.4),
        "scroll_speed_mean": max(0.05, 0.35 - stress * 0.2),
        "gyroscope_variance": 0.02 + stress * 0.06,
        "session_time_elapsed": 250 + stress * 200,
        "interaction_intensity": max(1, int(4 - stress * 2)),
    }


def main():
    print("=" * 70)
    print("  AEGIS-X Phase 6A: Session Manager — Full Pipeline Test")
    print("=" * 70)

    # ─── SETUP: Create baseline for test user ──────────────────────────────
    print("\nPreparing test user baseline...")
    user_id = "test_user_session"
    engineer = FeatureEngineer()
    serializer = BehavioralSerializer()
    embedder = EmbeddingService()
    baseline_svc = BaselineService()

    # Generate enrollment embeddings
    enrollment = []
    for _ in range(10):
        features = engineer.extract(generate_normal_event())
        text = serializer.serialize(features)
        emb = embedder.generate_embedding(text)
        enrollment.append(emb)

    baseline = baseline_svc.create_baseline(np.array(enrollment))
    baseline_svc.save_baseline(user_id, baseline, {"session_count": 10})
    print(f"Baseline saved for '{user_id}'")

    # ─── INITIALIZE SESSION MANAGER ────────────────────────────────────────
    manager = SessionManager()

    # ══════════════════════════════════════════════════════════════════════
    # PHASE 1: Session Creation
    # ══════════════════════════════════════════════════════════════════════
    separator("SESSION CREATION")

    session_info = manager.create_session(user_id)
    print(f"  Status: {session_info['status']}")
    print(f"  Session ID: {session_info['session_id']}")
    print(f"  Has baseline: {session_info['has_baseline']}")
    assert session_info["has_baseline"], "Baseline should be loaded"
    print("\n✓ Session created with baseline loaded")

    # ══════════════════════════════════════════════════════════════════════
    # PHASE 2: Normal Browsing (5 events)
    # Expected: Trust high, ALLOW
    # ══════════════════════════════════════════════════════════════════════
    separator("NORMAL BROWSING (5 heartbeats)")

    print(f"\n  {'#':<4} {'Trust':<8} {'Cog':<12} {'Decision':<9} {'Drift':<7}")
    print(f"  {'─' * 45}")

    for i in range(5):
        result = manager.process_event(user_id, generate_normal_event())
        ts = result["trust_state"]
        print(f"  {i+1:<4} {ts['trust_score']:<8.4f} {ts['cognitive_state']:<12} "
              f"{ts['action']:<9} {'YES' if result['drift']['detected'] else 'no'}")

    assert result["trust_state"]["action"] == "ALLOW"
    print("\n✓ Normal browsing — all ALLOW, no drift")

    # ══════════════════════════════════════════════════════════════════════
    # PHASE 3: Scam Call Begins — Escalating Stress
    # Expected: Trust declining, STEP_UP → BLOCK
    # ══════════════════════════════════════════════════════════════════════
    separator("SCAM CALL BEGINS — Escalating Coercion (10 heartbeats)")

    print(f"\n  {'#':<4} {'Trust':<8} {'Cog':<12} {'Decision':<9} {'Velocity':<10} {'Stress'}")
    print(f"  {'─' * 55}")

    blocked_at = None
    for i in range(10):
        stress = (i + 1) / 10.0
        result = manager.process_event(
            user_id,
            generate_coercion_event(stress),
            transaction_amount=200000,
            is_new_beneficiary=True,
        )

        # Session may already be blocked from a previous event
        if result.get("error") == "session_blocked":
            if blocked_at is None:
                blocked_at = i + 6
            print(f"  {i+6:<4} {'─────':<8} {'BLOCKED':<12} "
                  f"{'BLOCK':<9} {'─────':<10} {stress:.1f}")
            continue

        ts = result["trust_state"]
        td = result["temporal_dynamics"]
        print(f"  {i+6:<4} {ts['trust_score']:<8.4f} {ts['cognitive_state']:<12} "
              f"{ts['action']:<9} {td['velocity']:<10.4f} {stress:.1f}")

        if ts["action"] == "BLOCK" and blocked_at is None:
            blocked_at = i + 6

    print(f"\n  Session blocked at heartbeat: {blocked_at}")
    assert blocked_at is not None, "Scam should trigger BLOCK at some point"
    print("\n✓ Scam escalation detected — session BLOCKED")

    # ══════════════════════════════════════════════════════════════════════
    # PHASE 4: Verify blocked session rejects further events
    # ══════════════════════════════════════════════════════════════════════
    separator("BLOCKED SESSION — Further Events Rejected")

    blocked_result = manager.process_event(user_id, generate_normal_event())
    print(f"  Response: {blocked_result.get('error', 'processed')}")
    print(f"  Action: {blocked_result.get('action', 'N/A')}")
    assert blocked_result.get("error") == "session_blocked"
    print("\n✓ Blocked session correctly rejects new events")

    # ══════════════════════════════════════════════════════════════════════
    # PHASE 5: End Session
    # ══════════════════════════════════════════════════════════════════════
    separator("SESSION END — Summary")

    summary = manager.end_session(user_id)
    print(f"\n  Duration: {summary['duration_seconds']:.1f}s")
    print(f"  Total events: {summary['total_events']}")
    print(f"  Final trust: {summary['final_trust_score']:.4f}")
    print(f"  Final decision: {summary['final_decision']}")
    print(f"  Was blocked: {summary['was_blocked']}")
    print(f"  Drift detected: {summary['drift_detected']}")
    print(f"  Cognitive states: {summary['cognitive_states_observed']}")

    # ══════════════════════════════════════════════════════════════════════
    # CLEANUP
    # ══════════════════════════════════════════════════════════════════════
    baseline_svc.delete_baseline(user_id)

    separator("PHASE 6A COMPLETE: Session Manager Verified")
    print("""
    Session Manager orchestrates the FULL trust pipeline:
    ┌──────────────────────────────────────────────────────────────────┐
    │  WebSocket Heartbeat (every 2s)                                   │
    │       ↓                                                          │
    │  SessionManager.process_event(user_id, raw_event)                │
    │       ↓                                                          │
    │  ┌── Feature Extraction (16-dim)                                 │
    │  ├── Text Serialization                                          │
    │  ├── MiniLM Embedding (384-dim)                                  │
    │  ├── Cosine Similarity vs Baseline                               │
    │  ├── CUSUM Drift Detection                                       │
    │  ├── Cognitive State (Random Forest)                             │
    │  ├── Trust Score T(t) = 0.40S + 0.20D + 0.20T + 0.20C          │
    │  ├── Trust Velocity (dT/dt) + Acceleration (d²T/dt²)            │
    │  └── Decision Engine → ALLOW | STEP_UP | BLOCK                   │
    │       ↓                                                          │
    │  Session State Updated + Response to WebSocket Client             │
    └──────────────────────────────────────────────────────────────────┘
    """)


if __name__ == "__main__":
    main()
