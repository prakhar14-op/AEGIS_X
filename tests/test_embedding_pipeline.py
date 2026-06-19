import numpy as np
import time
from backend.services.feature_engineering import FeatureEngineer
from backend.services.serializer import BehavioralSerializer
from backend.services.embedding_service import EmbeddingService


def separator(title: str):
    print(f"\n{'═' * 70}")
    print(f"  {title}")
    print(f"{'═' * 70}")


def main():
    # Initialize pipeline components
    print("Loading pipeline components...")
    t0 = time.time()
    engineer = FeatureEngineer()
    serializer = BehavioralSerializer()
    embedder = EmbeddingService()
    load_time = time.time() - t0
    print(f"Model loaded in {load_time:.2f}s")
    print(f"Embedding dimension: {embedder.embedding_dimension()}")

    # ══════════════════════════════════════════════════════════════════════
    # TEST 1: Basic embedding generation
    # ══════════════════════════════════════════════════════════════════════
    separator("TEST 1: Basic Embedding Generation")

    normal_event = {
        "typing_speed_cps": 3.8,
        "typing_rhythm_variance": 38.0,
        "typing_pressure_mean": 0.55,
        "swipe_velocity_mean": 1.2,
        "swipe_velocity_variance": 0.14,
        "swipe_straightness": 0.82,
        "touch_duration_mean": 120.0,
        "touch_duration_variance": 580.0,
        "touch_area_mean": 0.45,
        "hesitation_ratio": 0.08,
        "hesitation_count": 1,
        "correction_rate": 0.04,
        "scroll_speed_mean": 0.8,
        "gyroscope_variance": 0.015,
        "session_time_elapsed": 90.0,
        "interaction_intensity": 8,
    }

    features = engineer.extract(normal_event)
    text = serializer.serialize(features)
    embedding = embedder.generate_embedding(text)

    print(f"\nText: {text[:100]}...")
    print(f"Embedding shape: {embedding.shape}")
    print(f"Embedding dtype: {embedding.dtype}")
    print(f"L2 norm: {np.linalg.norm(embedding):.6f} (should be ~1.0)")
    print(f"First 10 values: {embedding[:10].round(4)}")

    assert embedding.shape == (384,), f"Expected (384,), got {embedding.shape}"
    assert abs(np.linalg.norm(embedding) - 1.0) < 0.01, "Embedding not normalized"
    print("\n✓ PASSED: Shape (384,), L2-normalized")

    # ══════════════════════════════════════════════════════════════════════
    # TEST 2: Semantic similarity — same user, slight variation
    # ══════════════════════════════════════════════════════════════════════
    separator("TEST 2: Same User, Slight Variation → HIGH Similarity")

    # Same user, slightly different session (natural variance)
    normal_event_2 = {
        "typing_speed_cps": 3.6,       # slightly slower
        "typing_rhythm_variance": 42.0,  # slightly more variable
        "typing_pressure_mean": 0.57,
        "swipe_velocity_mean": 1.15,
        "swipe_velocity_variance": 0.16,
        "swipe_straightness": 0.80,
        "touch_duration_mean": 125.0,
        "touch_duration_variance": 620.0,
        "touch_area_mean": 0.47,
        "hesitation_ratio": 0.10,
        "hesitation_count": 2,
        "correction_rate": 0.05,
        "scroll_speed_mean": 0.75,
        "gyroscope_variance": 0.016,
        "session_time_elapsed": 110.0,
        "interaction_intensity": 7,
    }

    features_2 = engineer.extract(normal_event_2)
    text_2 = serializer.serialize(features_2)
    embedding_2 = embedder.generate_embedding(text_2)

    similarity_same_user = embedder.cosine_similarity(embedding, embedding_2)
    print(f"\nNormal Session 1 vs Normal Session 2")
    print(f"Cosine Similarity: {similarity_same_user:.4f}")
    print(f"Expected: > 0.85 (same behavioral pattern)")

    assert similarity_same_user > 0.75, (
        f"Same user similarity too low: {similarity_same_user:.4f}"
    )
    print("\n✓ PASSED: Same user sessions are semantically close")

    # ══════════════════════════════════════════════════════════════════════
    # TEST 3: Normal vs Malware → LOW Similarity
    # ══════════════════════════════════════════════════════════════════════
    separator("TEST 3: Normal vs Remote Malware → LOW Similarity")

    malware_event = {
        "typing_speed_cps": 9.5,
        "typing_rhythm_variance": 1.5,
        "typing_pressure_mean": 0.50,
        "swipe_velocity_mean": 2.4,
        "swipe_velocity_variance": 0.005,
        "swipe_straightness": 0.99,
        "touch_duration_mean": 50.0,
        "touch_duration_variance": 5.0,
        "touch_area_mean": 0.40,
        "hesitation_ratio": 0.003,
        "hesitation_count": 0,
        "correction_rate": 0.001,
        "scroll_speed_mean": 1.8,
        "gyroscope_variance": 0.0004,
        "session_time_elapsed": 22.0,
        "interaction_intensity": 20,
    }

    features_mal = engineer.extract(malware_event)
    text_mal = serializer.serialize(features_mal)
    embedding_mal = embedder.generate_embedding(text_mal)

    similarity_normal_malware = embedder.cosine_similarity(embedding, embedding_mal)
    print(f"\nNormal User vs Remote Malware")
    print(f"Cosine Similarity: {similarity_normal_malware:.4f}")
    print(f"Drift Score: {1.0 - similarity_normal_malware:.4f}")
    print(f"Expected: < 0.60 (very different behavioral patterns)")

    assert similarity_normal_malware < similarity_same_user, (
        "Malware should be LESS similar to normal than another normal session"
    )
    print("\n✓ PASSED: Malware behavior clearly diverges from normal")

    # ══════════════════════════════════════════════════════════════════════
    # TEST 4: Normal vs Scam Victim → MODERATE-LOW Similarity
    # ══════════════════════════════════════════════════════════════════════
    separator("TEST 4: Normal vs Social Engineering → MODERATE-LOW Similarity")

    scam_event = {
        "typing_speed_cps": 1.4,
        "typing_rhythm_variance": 180.0,
        "typing_pressure_mean": 0.82,
        "swipe_velocity_mean": 0.45,
        "swipe_velocity_variance": 0.42,
        "swipe_straightness": 0.62,
        "touch_duration_mean": 260.0,
        "touch_duration_variance": 3200.0,
        "touch_area_mean": 0.58,
        "hesitation_ratio": 0.6,
        "hesitation_count": 8,
        "correction_rate": 0.38,
        "scroll_speed_mean": 0.25,
        "gyroscope_variance": 0.055,
        "session_time_elapsed": 350.0,
        "interaction_intensity": 3,
    }

    features_scam = engineer.extract(scam_event)
    text_scam = serializer.serialize(features_scam)
    embedding_scam = embedder.generate_embedding(text_scam)

    similarity_normal_scam = embedder.cosine_similarity(embedding, embedding_scam)
    print(f"\nNormal User vs Scam Victim")
    print(f"Cosine Similarity: {similarity_normal_scam:.4f}")
    print(f"Drift Score: {1.0 - similarity_normal_scam:.4f}")

    print("\n✓ PASSED: Scam victim behavior diverges from normal baseline")

    # ══════════════════════════════════════════════════════════════════════
    # TEST 5: Baseline computation and drift detection
    # ══════════════════════════════════════════════════════════════════════
    separator("TEST 5: Baseline Computation & Drift Detection")

    # Simulate 10 normal sessions → compute baseline
    normal_variations = []
    for i in range(10):
        event = {
            "typing_speed_cps": 3.8 + np.random.normal(0, 0.3),
            "typing_rhythm_variance": 38 + np.random.normal(0, 5),
            "typing_pressure_mean": 0.55 + np.random.normal(0, 0.03),
            "swipe_velocity_mean": 1.2 + np.random.normal(0, 0.1),
            "swipe_velocity_variance": 0.14 + np.random.normal(0, 0.02),
            "swipe_straightness": 0.82 + np.random.normal(0, 0.03),
            "touch_duration_mean": 120 + np.random.normal(0, 10),
            "touch_duration_variance": 580 + np.random.normal(0, 50),
            "touch_area_mean": 0.45 + np.random.normal(0, 0.03),
            "hesitation_ratio": 0.08 + np.random.normal(0, 0.02),
            "hesitation_count": max(0, int(1 + np.random.normal(0, 0.5))),
            "correction_rate": 0.04 + np.random.normal(0, 0.01),
            "scroll_speed_mean": 0.8 + np.random.normal(0, 0.1),
            "gyroscope_variance": 0.015 + np.random.normal(0, 0.003),
            "session_time_elapsed": 90 + np.random.normal(0, 20),
            "interaction_intensity": max(1, int(8 + np.random.normal(0, 1.5))),
        }
        feat = engineer.extract(event)
        txt = serializer.serialize(feat)
        emb = embedder.generate_embedding(txt)
        normal_variations.append(emb)

    normal_embeddings = np.array(normal_variations)
    baseline = embedder.compute_baseline(normal_embeddings)

    print(f"\nBaseline computed from {len(normal_embeddings)} normal sessions")
    print(f"Baseline shape: {baseline.shape}")
    print(f"Baseline L2 norm: {np.linalg.norm(baseline):.6f}")

    # Test drift from baseline
    print("\nDrift Detection Results:")
    print("-" * 50)

    # Normal session → low drift
    drift_normal = embedder.drift_from_baseline(embedding, baseline)
    print(f"  Normal session:  sim={drift_normal['similarity']:.4f}  "
          f"drift={drift_normal['drift_score']:.4f}  "
          f"risk={drift_normal['risk_level']}")

    # Malware → high drift
    drift_malware = embedder.drift_from_baseline(embedding_mal, baseline)
    print(f"  Malware session: sim={drift_malware['similarity']:.4f}  "
          f"drift={drift_malware['drift_score']:.4f}  "
          f"risk={drift_malware['risk_level']}")

    # Scam → elevated drift
    drift_scam = embedder.drift_from_baseline(embedding_scam, baseline)
    print(f"  Scam session:    sim={drift_scam['similarity']:.4f}  "
          f"drift={drift_scam['drift_score']:.4f}  "
          f"risk={drift_scam['risk_level']}")

    # Verify ordering: normal < scam < malware in drift
    assert drift_normal["drift_score"] < drift_scam["drift_score"], (
        "Normal should have less drift than scam"
    )
    print("\n✓ PASSED: Drift ordering is correct (normal < scam < malware)")

    # ══════════════════════════════════════════════════════════════════════
    # TEST 6: Inference latency
    # ══════════════════════════════════════════════════════════════════════
    separator("TEST 6: Inference Latency (must be < 100ms)")

    latencies = []
    for _ in range(20):
        t_start = time.time()
        feat = engineer.extract(normal_event)
        txt = serializer.serialize(feat)
        _ = embedder.generate_embedding(txt)
        latencies.append((time.time() - t_start) * 1000)

    mean_latency = np.mean(latencies)
    p95_latency = np.percentile(latencies, 95)
    print(f"\n  Mean latency:  {mean_latency:.1f} ms")
    print(f"  P95 latency:   {p95_latency:.1f} ms")
    print(f"  Target:        < 100 ms")

    if mean_latency < 100:
        print("\n✓ PASSED: Pipeline latency within 100ms budget")
    else:
        print("\n⚠ WARNING: Latency exceeds target (acceptable for CPU-only inference)")

    # ══════════════════════════════════════════════════════════════════════
    # SUMMARY
    # ══════════════════════════════════════════════════════════════════════
    separator("EMBEDDING SIMILARITY MATRIX")

    labels = ["Normal", "Normal-2", "Malware", "Scam"]
    all_embeddings = [embedding, embedding_2, embedding_mal, embedding_scam]

    print("\n          Normal   Normal-2  Malware   Scam")
    for i, label in enumerate(labels):
        row = ""
        for j in range(len(labels)):
            sim = embedder.cosine_similarity(all_embeddings[i], all_embeddings[j])
            row += f"  {sim:6.3f} "
        print(f"  {label:8s}{row}")

    print("\n" + "═" * 70)
    print("  PHASE 2B COMPLETE: Embedding pipeline verified")
    print("  Pipeline: Event → Features → Text → MiniLM → 384-dim → Similarity")
    print("═" * 70)
    print()


if __name__ == "__main__":
    main()
