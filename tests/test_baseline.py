"""
Validates the complete baseline lifecycle:
    1. Enrollment: Multiple trusted sessions → baseline creation
    2. Verification: Current session vs baseline → drift detection
    3. Adaptation: EMA update with trust-gated security
    4. Persistence: Save/load baseline to disk
    5. Anti-poisoning: Attacker sessions CANNOT corrupt baseline

"""

import numpy as np
import time
from pathlib import Path

from backend.services.feature_engineering import FeatureEngineer
from backend.services.serializer import BehavioralSerializer
from backend.services.embedding_service import EmbeddingService
from backend.services.baseline_service import BaselineService


def separator(title: str):
    print(f"\n{'═' * 70}")
    print(f"  {title}")
    print(f"{'═' * 70}")


def generate_normal_event(variation_scale: float = 1.0) -> dict:
    """Generate a realistic normal user event with natural variation."""
    return {
        "typing_speed_cps": 3.8 + np.random.normal(0, 0.4 * variation_scale),
        "typing_rhythm_variance": 38 + np.random.normal(0, 6 * variation_scale),
        "typing_pressure_mean": 0.55 + np.random.normal(0, 0.04 * variation_scale),
        "swipe_velocity_mean": 1.2 + np.random.normal(0, 0.12 * variation_scale),
        "swipe_velocity_variance": 0.14 + np.random.normal(0, 0.03 * variation_scale),
        "swipe_straightness": 0.82 + np.random.normal(0, 0.03 * variation_scale),
        "touch_duration_mean": 120 + np.random.normal(0, 12 * variation_scale),
        "touch_duration_variance": 580 + np.random.normal(0, 60 * variation_scale),
        "touch_area_mean": 0.45 + np.random.normal(0, 0.04 * variation_scale),
        "hesitation_ratio": max(0, 0.08 + np.random.normal(0, 0.025 * variation_scale)),
        "hesitation_count": max(0, int(1 + np.random.normal(0, 0.6 * variation_scale))),
        "correction_rate": max(0, 0.04 + np.random.normal(0, 0.012 * variation_scale)),
        "scroll_speed_mean": 0.8 + np.random.normal(0, 0.1 * variation_scale),
        "gyroscope_variance": max(0.001, 0.015 + np.random.normal(0, 0.003 * variation_scale)),
        "session_time_elapsed": 90 + np.random.normal(0, 25 * variation_scale),
        "interaction_intensity": max(1, int(8 + np.random.normal(0, 1.5 * variation_scale))),
    }


def generate_attacker_event() -> dict:
    """Generate a takeover attacker event (very different behavioral profile)."""
    return {
        "typing_speed_cps": 6.5 + np.random.normal(0, 0.2),
        "typing_rhythm_variance": 8 + np.random.normal(0, 1.5),
        "typing_pressure_mean": 0.73 + np.random.normal(0, 0.02),
        "swipe_velocity_mean": 2.0 + np.random.normal(0, 0.1),
        "swipe_velocity_variance": 0.03 + np.random.normal(0, 0.005),
        "swipe_straightness": 0.94 + np.random.normal(0, 0.01),
        "touch_duration_mean": 70 + np.random.normal(0, 5),
        "touch_duration_variance": 120 + np.random.normal(0, 20),
        "touch_area_mean": 0.63 + np.random.normal(0, 0.02),
        "hesitation_ratio": max(0, 0.02 + np.random.normal(0, 0.005)),
        "hesitation_count": 0,
        "correction_rate": max(0, 0.008 + np.random.normal(0, 0.003)),
        "scroll_speed_mean": 1.6 + np.random.normal(0, 0.08),
        "gyroscope_variance": max(0.001, 0.006 + np.random.normal(0, 0.001)),
        "session_time_elapsed": 30 + np.random.normal(0, 5),
        "interaction_intensity": max(1, int(15 + np.random.normal(0, 1))),
    }


def main():
    # Pipeline components
    print("Initializing AEGIS-X pipeline...")
    engineer = FeatureEngineer()
    serializer = BehavioralSerializer()
    embedder = EmbeddingService()
    baseline_svc = BaselineService()

    print(f"Embedding dimension: {embedder.embedding_dimension()}")
    print(f"Baselines directory: {baseline_svc.storage_dir}")

    # ══════════════════════════════════════════════════════════════════════
    # TEST 1: Baseline Enrollment
    # ══════════════════════════════════════════════════════════════════════
    separator("TEST 1: Baseline Enrollment (10 trusted sessions)")

    # Simulate 10 normal sessions for user enrollment
    enrollment_embeddings = []
    for i in range(10):
        event = generate_normal_event()
        features = engineer.extract(event)
        text = serializer.serialize(features)
        emb = embedder.generate_embedding(text)
        enrollment_embeddings.append(emb)

    enrollment_array = np.array(enrollment_embeddings)
    print(f"Enrollment embeddings shape: {enrollment_array.shape}")

    # Create baseline
    baseline = baseline_svc.create_baseline(enrollment_array)
    print(f"Baseline shape: {baseline.shape}")
    print(f"Baseline L2 norm: {np.linalg.norm(baseline):.6f} (should be 1.0)")
    print(f"Baseline first 5 values: {baseline[:5].round(4)}")

    assert baseline.shape == (384,)
    assert abs(np.linalg.norm(baseline) - 1.0) < 0.001
    print("\n✓ PASSED: Baseline created successfully (384-dim, unit normalized)")

    # ══════════════════════════════════════════════════════════════════════
    # TEST 2: Baseline Confidence Scoring
    # ══════════════════════════════════════════════════════════════════════
    separator("TEST 2: Baseline Confidence Assessment")

    confidence = baseline_svc.compute_baseline_confidence(enrollment_array, baseline)
    print(f"\n  Session count:    {confidence['session_count']}")
    print(f"  Mean similarity:  {confidence['mean_similarity']:.4f}")
    print(f"  Min similarity:   {confidence['min_similarity']:.4f}")
    print(f"  Std similarity:   {confidence['std_similarity']:.6f}")
    print(f"  Confidence score: {confidence['confidence_score']:.4f}")

    assert confidence["confidence_score"] > 0.5, "Confidence should be high for consistent user"
    print("\n✓ PASSED: High confidence baseline — user behavior is consistent")

    # ══════════════════════════════════════════════════════════════════════
    # TEST 3: Verification — Normal user recognized
    # ══════════════════════════════════════════════════════════════════════
    separator("TEST 3: Verification — Same User (should match)")

    normal_event = generate_normal_event()
    features = engineer.extract(normal_event)
    text = serializer.serialize(features)
    normal_embedding = embedder.generate_embedding(text)

    result = baseline_svc.verify_against_baseline(normal_embedding, baseline)
    print(f"\n  Similarity:    {result['similarity']:.4f}")
    print(f"  Drift score:   {result['drift_score']:.4f}")
    print(f"  Risk level:    {result['risk_level']}")
    print(f"  Is consistent: {result['is_consistent']}")
    print(f"  Can update:    {result['can_update_baseline']}")

    assert result["is_consistent"], "Normal user should be recognized as consistent"
    assert result["risk_level"] == "low"
    print("\n✓ PASSED: Genuine user correctly identified — low risk")

    # ══════════════════════════════════════════════════════════════════════
    # TEST 4: Verification — Attacker detected
    # ══════════════════════════════════════════════════════════════════════
    separator("TEST 4: Verification — Attacker (should NOT match)")

    attacker_event = generate_attacker_event()
    features = engineer.extract(attacker_event)
    text = serializer.serialize(features)
    attacker_embedding = embedder.generate_embedding(text)

    result_attacker = baseline_svc.verify_against_baseline(attacker_embedding, baseline)
    print(f"\n  Similarity:    {result_attacker['similarity']:.4f}")
    print(f"  Drift score:   {result_attacker['drift_score']:.4f}")
    print(f"  Risk level:    {result_attacker['risk_level']}")
    print(f"  Is consistent: {result_attacker['is_consistent']}")
    print(f"  Can update:    {result_attacker['can_update_baseline']}")

    assert result_attacker["drift_score"] > result["drift_score"], (
        "Attacker should have higher drift than normal user"
    )
    assert not result_attacker["can_update_baseline"], (
        "Attacker should NOT be allowed to update baseline"
    )
    print("\n✓ PASSED: Attacker detected — higher drift, baseline update blocked")

    # ══════════════════════════════════════════════════════════════════════
    # TEST 5: EMA Baseline Update — Trust-gated security
    # ══════════════════════════════════════════════════════════════════════
    separator("TEST 5: Baseline Update — Trust-Gated Security")

    # High trust session → should update
    updated_baseline, was_updated = baseline_svc.update_baseline(
        current_baseline=baseline,
        new_embedding=normal_embedding,
        trust_score=0.95  # High trust
    )
    print(f"\n  Trust=0.95 (high): Updated={was_updated}")
    assert was_updated, "High trust session should update baseline"

    # Verify updated baseline is still normalized
    assert abs(np.linalg.norm(updated_baseline) - 1.0) < 0.001

    # Low trust session → should NOT update (anti-poisoning)
    unchanged_baseline, was_updated_low = baseline_svc.update_baseline(
        current_baseline=baseline,
        new_embedding=attacker_embedding,
        trust_score=0.45  # Low trust — attacker
    )
    print(f"  Trust=0.45 (low):  Updated={was_updated_low}")
    assert not was_updated_low, "Low trust session must NOT update baseline"
    assert np.array_equal(unchanged_baseline, baseline), "Baseline must be unchanged"

    # Borderline trust → should NOT update (conservative threshold)
    _, was_updated_border = baseline_svc.update_baseline(
        current_baseline=baseline,
        new_embedding=normal_embedding,
        trust_score=0.88  # Below 0.90 threshold
    )
    print(f"  Trust=0.88 (borderline): Updated={was_updated_border}")
    assert not was_updated_border, "Borderline trust should NOT update baseline"

    print("\n✓ PASSED: Anti-poisoning security gate working correctly")

    # ══════════════════════════════════════════════════════════════════════
    # TEST 6: Persistence — Save and Load
    # ══════════════════════════════════════════════════════════════════════
    separator("TEST 6: Persistence — Save & Load Baseline")

    test_user_id = "test_user_verification"
    metadata = {
        "session_count": 10,
        "confidence_score": confidence["confidence_score"],
        "enrollment_method": "initial_registration",
    }

    # Save
    filepath = baseline_svc.save_baseline(test_user_id, baseline, metadata)
    print(f"\n  Saved to: {filepath}")
    assert filepath.exists()

    # Load
    loaded_baseline, loaded_meta = baseline_svc.load_baseline(test_user_id)
    print(f"  Loaded shape: {loaded_baseline.shape}")
    print(f"  Metadata: user_id={loaded_meta['user_id']}, dim={loaded_meta['embedding_dim']}")

    # Verify integrity
    assert np.allclose(baseline, loaded_baseline, atol=1e-6), "Loaded baseline doesn't match"
    assert loaded_meta["user_id"] == test_user_id

    # Check existence
    assert baseline_svc.baseline_exists(test_user_id)
    assert not baseline_svc.baseline_exists("nonexistent_user")

    # Cleanup
    baseline_svc.delete_baseline(test_user_id)
    assert not baseline_svc.baseline_exists(test_user_id)
    print("  Cleanup: baseline deleted")

    print("\n✓ PASSED: Save/load/delete cycle works correctly")

    # ══════════════════════════════════════════════════════════════════════
    # TEST 7: Recency-weighted baseline
    # ══════════════════════════════════════════════════════════════════════
    separator("TEST 7: Recency-Weighted Baseline")

    # Recent sessions should influence baseline more than old ones
    recency_baseline = baseline_svc.create_baseline_with_recency_weighting(
        enrollment_array, recency_factor=0.8
    )
    print(f"\n  Recency baseline shape: {recency_baseline.shape}")
    print(f"  Recency baseline norm: {np.linalg.norm(recency_baseline):.6f}")

    # Should be similar but not identical to uniform baseline
    sim_to_uniform = float(np.dot(recency_baseline, baseline))
    print(f"  Similarity to uniform baseline: {sim_to_uniform:.4f}")
    assert sim_to_uniform > 0.95, "Recency baseline should be close to uniform for consistent user"
    print("\n✓ PASSED: Recency weighting produces valid, slightly shifted baseline")

    # ══════════════════════════════════════════════════════════════════════
    # TEST 8: Insufficient enrollment rejection
    # ══════════════════════════════════════════════════════════════════════
    separator("TEST 8: Insufficient Enrollment Rejection")

    try:
        baseline_svc.create_baseline(enrollment_array[:3])  # Only 3 sessions
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"\n  Correctly rejected: {e}")
        print("\n✓ PASSED: System refuses to create baseline from insufficient data")

    # ══════════════════════════════════════════════════════════════════════
    # SUMMARY
    # ══════════════════════════════════════════════════════════════════════
    separator("PHASE 2C COMPLETE: Baseline Identity System Verified")
    print("""
    Baseline Lifecycle:
    ┌─────────────────────────────────────────────────────────┐
    │  ENROLLMENT   → 5+ trusted sessions → compute centroid  │
    │  VERIFICATION → current vs baseline → drift score       │
    │  ADAPTATION   → EMA update (ONLY if T > 0.90)           │
    │  PROTECTION   → attacker sessions NEVER update baseline │
    └─────────────────────────────────────────────────────────┘

    Security Properties:
    • Minimum 5 sessions required for enrollment (no single-session baselines)
    • Trust-gated updates prevent baseline poisoning
    • L2 normalization ensures cosine similarity consistency
    • Persistence enables cross-session identity continuity
    """)


if __name__ == "__main__":
    main()
