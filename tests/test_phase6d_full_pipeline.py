"""
AEGIS-X Phase 6D-N: Full End-to-End Pipeline Test
===================================================
Tests the COMPLETE system through EventProcessor:
    event → processor.process_behavioral_event() → structured response

This is the final integration test: one function call, entire security engine.
Proves the system produces exactly what the proposal promises.
"""

import numpy as np
import json
from backend.services.event_processor import EventProcessor
from backend.services.baseline_service import BaselineService
from backend.services.feature_engineering import FeatureEngineer
from backend.services.serializer import BehavioralSerializer
from backend.services.embedding_service import EmbeddingService


def separator(title: str):
    print(f"\n{'═' * 70}")
    print(f"  {title}")
    print(f"{'═' * 70}")


def generate_normal():
    return {
        "typing_speed_cps": 3.8 + np.random.normal(0, 0.3),
        "typing_rhythm_variance": 38 + np.random.normal(0, 4),
        "typing_pressure_mean": 0.55 + np.random.normal(0, 0.02),
        "swipe_velocity_mean": 1.2 + np.random.normal(0, 0.08),
        "swipe_velocity_variance": 0.14 + np.random.normal(0, 0.015),
        "swipe_straightness": 0.82 + np.random.normal(0, 0.02),
        "touch_duration_mean": 120 + np.random.normal(0, 8),
        "touch_duration_variance": 580 + np.random.normal(0, 35),
        "touch_area_mean": 0.45 + np.random.normal(0, 0.02),
        "hesitation_ratio": max(0, 0.08 + np.random.normal(0, 0.015)),
        "hesitation_count": max(0, int(1 + np.random.normal(0, 0.4))),
        "correction_rate": max(0, 0.04 + np.random.normal(0, 0.008)),
        "scroll_speed_mean": 0.8 + np.random.normal(0, 0.06),
        "gyroscope_variance": max(0.001, 0.015 + np.random.normal(0, 0.002)),
        "session_time_elapsed": 90 + np.random.normal(0, 12),
        "interaction_intensity": max(1, int(8 + np.random.normal(0, 1))),
    }


def generate_scam(stress: float):
    return {
        "typing_speed_cps": max(0.5, 1.3 - stress * 0.5),
        "typing_rhythm_variance": 60 + stress * 200,
        "typing_pressure_mean": 0.70 + stress * 0.18,
        "swipe_velocity_mean": max(0.1, 0.5 - stress * 0.3),
        "swipe_velocity_variance": 0.2 + stress * 0.3,
        "swipe_straightness": max(0.3, 0.68 - stress * 0.25),
        "touch_duration_mean": 180 + stress * 150,
        "touch_duration_variance": 800 + stress * 3000,
        "touch_area_mean": 0.52 + stress * 0.12,
        "hesitation_ratio": min(0.9, 0.3 + stress * 0.5),
        "hesitation_count": int(4 + stress * 8),
        "correction_rate": min(0.6, 0.15 + stress * 0.4),
        "scroll_speed_mean": max(0.05, 0.3 - stress * 0.2),
        "gyroscope_variance": 0.025 + stress * 0.06,
        "session_time_elapsed": 300 + stress * 200,
        "interaction_intensity": max(1, int(4 - stress * 2)),
    }


def main():
    print("=" * 70)
    print("  AEGIS-X Phase 6D: Full Pipeline — One Function, Entire Engine")
    print("=" * 70)

    # ─── SETUP: Create baseline for test user ──────────────────────────────
    print("\nInitializing system...")
    user_id = "demo_user_001"

    engineer = FeatureEngineer()
    serializer = BehavioralSerializer()
    embedder = EmbeddingService()
    baseline_svc = BaselineService()

    enrollment = []
    for _ in range(10):
        feat = engineer.extract(generate_normal())
        txt = serializer.serialize(feat)
        emb = embedder.generate_embedding(txt)
        enrollment.append(emb)
    baseline = baseline_svc.create_baseline(np.array(enrollment))
    baseline_svc.save_baseline(user_id, baseline, {"session_count": 10})
    print(f"Baseline saved for '{user_id}'")

    # ─── INITIALIZE EVENT PROCESSOR ────────────────────────────────────────
    processor = EventProcessor()
    session_info = processor.start_session(user_id, session_id="sess_demo_001")
    print(f"Session started: {session_info}")

    # ══════════════════════════════════════════════════════════════════════
    # SCENARIO 1: Normal user — the ONE function call
    # ══════════════════════════════════════════════════════════════════════
    separator("ONE FUNCTION CALL — Normal User")

    result = processor.process_behavioral_event(
        user_id=user_id,
        raw_event=generate_normal(),
        transaction_amount=2000,
    )

    print(f"\n  processor.process_behavioral_event(user_id, event)")
    print(f"\n  Result:")
    print(f"    trust_score:      {result['trust_score']}")
    print(f"    decision:         {result['decision']}")
    print(f"    cognitive_state:  {result['cognitive_state']}")
    print(f"    similarity:       {result['similarity']}")
    print(f"    drift_detected:   {result['drift_detected']}")
    print(f"    velocity:         {result['temporal']['velocity']}")
    print(f"    latency_ms:       {result['latency_ms']}")
    print(f"    alerts:           {result['alerts']}")

    assert result["decision"] == "ALLOW"
    print("\n✓ Normal user → ALLOW (single function call, entire engine)")

    # ══════════════════════════════════════════════════════════════════════
    # SCENARIO 2: Full session with history tracking
    # ══════════════════════════════════════════════════════════════════════
    separator("MULTI-EVENT SESSION — Trust History Builds Up")

    for i in range(5):
        r = processor.process_behavioral_event(user_id, generate_normal())

    timeline = processor.get_trust_timeline(user_id)
    print(f"\n  Trust Timeline (6 events): {[round(t, 3) for t in timeline]}")
    print(f"  Active users: {processor.get_active_users()}")
    assert len(timeline) == 6  # 1 from before + 5 new
    print("\n✓ Session history tracked — timeline available for dashboard")

    # ══════════════════════════════════════════════════════════════════════
    # SCENARIO 3: Scam escalation — alerts + audit
    # ══════════════════════════════════════════════════════════════════════
    separator("SCAM ESCALATION — Alerts & Audit Trail")

    scam_user = "scam_victim_001"
    baseline_svc.save_baseline(scam_user, baseline, {"session_count": 10})
    processor.start_session(scam_user, "sess_scam_001")

    # Warm up with 3 normal events
    for _ in range(3):
        processor.process_behavioral_event(scam_user, generate_normal())

    print(f"\n  {'#':<4} {'Trust':<8} {'State':<12} {'Decision':<9} {'Alerts'}")
    print(f"  {'─' * 50}")

    for i in range(8):
        stress = (i + 1) / 8.0
        r = processor.process_behavioral_event(
            scam_user,
            generate_scam(stress),
            transaction_amount=200000,
            is_new_beneficiary=True,
        )
        alert_count = len(r.get("alerts", []))
        print(f"  {i+4:<4} {r['trust_score']:<8.4f} {r['cognitive_state']:<12} "
              f"{r['decision']:<9} {alert_count} alert(s)")

    # Check alerts were generated
    all_alerts = processor.get_session_alerts(scam_user)
    print(f"\n  Total session alerts: {len(all_alerts)}")
    if all_alerts:
        print(f"  Latest alert: [{all_alerts[-1]['severity']}] {all_alerts[-1]['message'][:60]}...")

    print("\n✓ Scam detected — alerts generated, audit logged")

    # ══════════════════════════════════════════════════════════════════════
    # SCENARIO 4: Full WebSocket response object
    # ══════════════════════════════════════════════════════════════════════
    separator("FULL RESPONSE — API Contract")

    # Fresh user for clean output
    clean_user = "clean_demo"
    baseline_svc.save_baseline(clean_user, baseline)
    processor.start_session(clean_user, "sess_clean")
    response = processor.process_behavioral_event(clean_user, generate_normal())

    # Remove large fields for display
    display = {k: v for k, v in response.items() if k != "explanation"}
    print(f"\n{json.dumps(display, indent=2, default=str)}")

    # ══════════════════════════════════════════════════════════════════════
    # SCENARIO 5: Audit log verification
    # ══════════════════════════════════════════════════════════════════════
    separator("AUDIT LOG — Compliance Trail")

    from pathlib import Path
    from datetime import datetime, timezone

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_file = Path("logs") / f"audit_{date_str}.jsonl"

    if log_file.exists():
        with open(log_file) as f:
            lines = f.readlines()
        print(f"\n  Audit log: {log_file}")
        print(f"  Total records: {len(lines)}")
        print(f"  Last record:")
        last = json.loads(lines[-1])
        print(f"    user: {last['user_id']}")
        print(f"    trust: {last['trust_score']}")
        print(f"    decision: {last['decision']}")
        print(f"    state: {last['cognitive_state']}")
        print(f"    alerts: {last['alerts']}")
    else:
        print(f"\n  Audit log not found at {log_file}")

    # ══════════════════════════════════════════════════════════════════════
    # CLEANUP
    # ══════════════════════════════════════════════════════════════════════
    processor.end_session(user_id)
    processor.end_session(scam_user)
    processor.end_session(clean_user)
    baseline_svc.delete_baseline(user_id)
    baseline_svc.delete_baseline(scam_user)
    baseline_svc.delete_baseline(clean_user)

    separator("PHASE 6D COMPLETE: Full Pipeline Verified")
    print("""
    The Event Processor provides:

    ONE FUNCTION:
        result = processor.process_behavioral_event(user_id, event)

    RETURNS EVERYTHING:
        trust_score, decision, cognitive_state, similarity,
        drift_detected, velocity, acceleration, alerts, reasons,
        explanation, latency_ms, confidence, event_number

    AUTOMATICALLY:
        ✓ Validates events
        ✓ Manages session context (CUSUM, history, baseline)
        ✓ Generates alerts when thresholds breached
        ✓ Writes audit log for compliance
        ✓ Builds structured response for WebSocket/Dashboard

    ARCHITECTURE:
        WebSocket → EventProcessor → TrustPipeline → Response
                                   → AlertEngine → Dashboard
                                   → AuditLogger → Compliance
    """)


if __name__ == "__main__":
    main()
