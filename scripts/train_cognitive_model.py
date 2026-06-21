"""
Trains a Random Forest (100 estimators) to classify behavioral features
into cognitive states: calm, focused, distressed, panicked, coerced, robotic.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from joblib import dump

# Paths
DATA_PATH = Path(__file__).parent.parent / "data" / "synthetic" / "cognitive_training_dataset.csv"
MODEL_DIR = Path(__file__).parent.parent / "models" / "cognitive"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "cognitive_rf.pkl"

# Cognitive feature columns (8 features for cognitive assessment)
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

# Ordered states (matches proposal's state machine progression)
STATE_ORDER = ["calm", "focused", "distressed", "panicked", "coerced", "robotic"]


def main():
    print("=" * 70)
    print("AEGIS-X Phase 4C: Training Cognitive State Classifier")
    print("=" * 70)
    print()

    # ─── Load Data ─────────────────────────────────────────────────────────
    print(f"Loading dataset from: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    print(f"Total samples: {len(df):,}")
    print(f"Features: {COGNITIVE_FEATURES}")
    print(f"States: {df['cognitive_state'].unique().tolist()}")
    print()

    X = df[COGNITIVE_FEATURES].to_numpy()
    y = df["cognitive_state"].to_numpy()

    # ─── Train/Test Split ──────────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"Training set: {len(X_train):,} samples")
    print(f"Test set:     {len(X_test):,} samples")
    print()

    # ─── Train Random Forest ───────────────────────────────────────────────
    print("Training Random Forest (100 estimators)...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        min_samples_split=10,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,  # Use all CPU cores
    )
    model.fit(X_train, y_train)
    print("Training complete.")
    print()

    # ─── Evaluate ──────────────────────────────────────────────────────────
    train_accuracy = model.score(X_train, y_train)
    test_accuracy = model.score(X_test, y_test)
    print(f"Training accuracy: {train_accuracy:.4f}")
    print(f"Test accuracy:     {test_accuracy:.4f}")
    print()

    # Cross-validation for robust estimate
    print("5-fold cross-validation...")
    cv_scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
    print(f"CV scores: {cv_scores.round(4)}")
    print(f"CV mean:   {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    print()

    # Classification report
    y_pred = model.predict(X_test)
    print("Classification Report:")
    print("-" * 70)
    print(classification_report(y_test, y_pred, target_names=STATE_ORDER, digits=4))

    # Feature importance
    print("Feature Importance:")
    print("-" * 70)
    importances = model.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]
    for idx in sorted_idx:
        print(f"  {COGNITIVE_FEATURES[idx]:<25} {importances[idx]:.4f}")
    print()

    # ─── Save Model ────────────────────────────────────────────────────────
    dump(model, MODEL_PATH)
    print(f"Model saved to: {MODEL_PATH.resolve()}")
    print(f"Model size: {MODEL_PATH.stat().st_size / 1024:.1f} KB")
    print()

    # ─── Quick Inference Test ──────────────────────────────────────────────
    print("Quick Inference Test:")
    print("-" * 70)
    test_cases = [
        ("CALM user", [0.08, 0.04, 3.8, 38, 120, 0.015, 8, 0.83]),
        ("PANICKED user", [0.55, 0.40, 1.5, 140, 220, 0.045, 3, 0.62]),
        ("COERCED user", [0.70, 0.50, 0.9, 200, 300, 0.070, 2, 0.50]),
        ("ROBOTIC (malware)", [0.005, 0.001, 9.5, 1.5, 48, 0.0005, 18, 0.98]),
    ]

    for name, features in test_cases:
        prediction = model.predict([features])[0]
        probabilities = model.predict_proba([features])[0]
        max_prob = max(probabilities)
        print(f"  {name:<20} → {prediction:<12} (confidence: {max_prob:.2f})")
    print()

    print("=" * 70)
    print("  Phase 4C COMPLETE: Cognitive model trained and saved")
    print("=" * 70)


if __name__ == "__main__":
    main()
