"""
Generates synthetic labeled data for training the Random Forest cognitive
state classifier (100 estimators, as specified in Section 6.c).

Each state has distinct behavioral signatures mapped from the 16-dim feature space.
We extract the 8 features most relevant to cognitive assessment:

    1. hesitation_ratio         — fraction of time idle (strongest coercion signal)
    2. correction_rate          — backspace/undo frequency (panic indicator)
    3. typing_speed_cps         — chars per second (stress slows typing)
    4. typing_rhythm_variance   — inter-key timing irregularity (stress → erratic)
    5. touch_duration_mean      — finger hold time (freezing under pressure)
    6. gyroscope_variance       — device shake (physical stress response)
    7. interaction_intensity    — taps per 2s window (engagement level)
    8. swipe_straightness       — path linearity (impaired motor control → curved)

These 8 features are the cognitive subset of the full 16-dim vector.
The Random Forest learns the non-linear boundaries between states.
"""

import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "synthetic"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Samples per cognitive state
N_PER_STATE = 2000


def generate_calm(n: int) -> pd.DataFrame:
    """
    CALM: Normal baseline user behavior.
    - Relaxed interaction, natural rhythm
    - Low hesitation, low corrections
    - Stable device motion, moderate typing speed
    - Regular engagement level
    """
    return pd.DataFrame({
        "hesitation_ratio": np.random.beta(2, 20, n).clip(0.01, 0.15),
        "correction_rate": np.random.beta(2, 45, n).clip(0.005, 0.08),
        "typing_speed_cps": np.random.normal(3.8, 0.5, n).clip(2.5, 5.5),
        "typing_rhythm_variance": np.random.gamma(2.5, 14, n).clip(10, 60),
        "touch_duration_mean": np.random.normal(115, 18, n).clip(70, 170),
        "gyroscope_variance": np.random.gamma(3, 0.004, n).clip(0.005, 0.025),
        "interaction_intensity": np.random.poisson(8, n).clip(4, 15),
        "swipe_straightness": np.random.normal(0.83, 0.04, n).clip(0.72, 0.94),
        "cognitive_state": "calm",
    })


def generate_focused(n: int) -> pd.DataFrame:
    """
    FOCUSED: User actively performing an important task.
    - Slightly slower, more deliberate typing
    - Very few corrections (careful input)
    - Stable but attentive behavior
    - Higher interaction density (engaged)
    """
    return pd.DataFrame({
        "hesitation_ratio": np.random.beta(2.5, 16, n).clip(0.03, 0.20),
        "correction_rate": np.random.beta(2, 50, n).clip(0.005, 0.06),
        "typing_speed_cps": np.random.normal(3.2, 0.4, n).clip(2.0, 4.5),
        "typing_rhythm_variance": np.random.gamma(2, 12, n).clip(8, 50),
        "touch_duration_mean": np.random.normal(130, 20, n).clip(85, 190),
        "gyroscope_variance": np.random.gamma(2.5, 0.004, n).clip(0.004, 0.022),
        "interaction_intensity": np.random.poisson(10, n).clip(5, 18),
        "swipe_straightness": np.random.normal(0.85, 0.035, n).clip(0.75, 0.95),
        "cognitive_state": "focused",
    })


def generate_distressed(n: int) -> pd.DataFrame:
    """
    DISTRESSED: Beginning of uncertainty/anxiety.
    - Elevated hesitation (thinking, doubting)
    - Increased corrections (mistakes from divided attention)
    - Typing slows, rhythm becomes erratic
    - Slight device tremor
    - Reduced swipe precision
    """
    return pd.DataFrame({
        "hesitation_ratio": np.random.beta(4, 8, n).clip(0.15, 0.50),
        "correction_rate": np.random.beta(3, 12, n).clip(0.08, 0.30),
        "typing_speed_cps": np.random.normal(2.5, 0.5, n).clip(1.2, 3.8),
        "typing_rhythm_variance": np.random.gamma(3.5, 22, n).clip(30, 130),
        "touch_duration_mean": np.random.normal(160, 30, n).clip(100, 250),
        "gyroscope_variance": np.random.gamma(3, 0.008, n).clip(0.010, 0.045),
        "interaction_intensity": np.random.poisson(6, n).clip(2, 12),
        "swipe_straightness": np.random.normal(0.74, 0.06, n).clip(0.55, 0.88),
        "cognitive_state": "distressed",
    })


def generate_panicked(n: int) -> pd.DataFrame:
    """
    PANICKED: Active scam victim, severe stress.
    - Very high hesitation (frozen, conflicted)
    - High corrections (panic-induced errors)
    - Very slow typing (distracted by phone call)
    - Highly erratic rhythm
    - Significant device shaking (physical stress)
    - Low interaction (paralysis)
    """
    return pd.DataFrame({
        "hesitation_ratio": np.random.beta(6, 5, n).clip(0.30, 0.75),
        "correction_rate": np.random.beta(5, 7, n).clip(0.15, 0.55),
        "typing_speed_cps": np.random.normal(1.5, 0.4, n).clip(0.5, 2.8),
        "typing_rhythm_variance": np.random.gamma(4, 35, n).clip(60, 280),
        "touch_duration_mean": np.random.normal(220, 45, n).clip(130, 400),
        "gyroscope_variance": np.random.gamma(4, 0.01, n).clip(0.020, 0.080),
        "interaction_intensity": np.random.poisson(3, n).clip(1, 8),
        "swipe_straightness": np.random.normal(0.63, 0.08, n).clip(0.40, 0.80),
        "cognitive_state": "panicked",
    })


def generate_coerced(n: int) -> pd.DataFrame:
    """
    COERCED: Most dangerous state — victim under active external control.
    - Extreme hesitation with sudden bursts (told what to do, then freezes)
    - Very high corrections (conflicted between compliance and resistance)
    - Extremely slow typing
    - Maximum rhythm irregularity
    - Severe device instability
    - Sporadic interaction (follows instructions mechanically)
    """
    return pd.DataFrame({
        "hesitation_ratio": np.random.beta(7, 4, n).clip(0.45, 0.90),
        "correction_rate": np.random.beta(5, 5, n).clip(0.20, 0.65),
        "typing_speed_cps": np.random.normal(1.0, 0.3, n).clip(0.3, 2.0),
        "typing_rhythm_variance": np.random.gamma(5, 40, n).clip(100, 350),
        "touch_duration_mean": np.random.normal(280, 60, n).clip(160, 500),
        "gyroscope_variance": np.random.gamma(5, 0.012, n).clip(0.030, 0.120),
        "interaction_intensity": np.random.poisson(2, n).clip(1, 6),
        "swipe_straightness": np.random.normal(0.55, 0.09, n).clip(0.30, 0.75),
        "cognitive_state": "coerced",
    })


def generate_robotic(n: int) -> pd.DataFrame:
    """
    ROBOTIC: Automated script / remote malware control.
    - Near-zero hesitation (no human decision-making)
    - Zero corrections (scripted actions, no mistakes)
    - Extremely fast typing (inhuman speed)
    - Near-zero rhythm variance (machine precision)
    - Zero device motion (phone on desk, remotely controlled)
    - Very high interaction density (rapid automated taps)
    - Perfect swipe paths (programmatic gestures)
    """
    return pd.DataFrame({
        "hesitation_ratio": np.random.exponential(0.005, n).clip(0.0, 0.03),
        "correction_rate": np.random.exponential(0.002, n).clip(0.0, 0.01),
        "typing_speed_cps": np.random.normal(9.5, 0.3, n).clip(8.0, 12.0),
        "typing_rhythm_variance": np.random.exponential(1.5, n).clip(0.1, 6.0),
        "touch_duration_mean": np.random.normal(48, 4, n).clip(35, 62),
        "gyroscope_variance": np.random.exponential(0.0005, n).clip(0.0001, 0.003),
        "interaction_intensity": np.random.poisson(18, n).clip(12, 28),
        "swipe_straightness": np.random.normal(0.98, 0.008, n).clip(0.96, 1.0),
        "cognitive_state": "robotic",
    })


def main():
    print("=" * 70)
    print("AEGIS-X Phase 4B: Cognitive State Dataset Generation")
    print("=" * 70)
    print()

    print(f"Generating {N_PER_STATE} samples per state (6 states)...")
    print()

    df_calm = generate_calm(N_PER_STATE)
    df_focused = generate_focused(N_PER_STATE)
    df_distressed = generate_distressed(N_PER_STATE)
    df_panicked = generate_panicked(N_PER_STATE)
    df_coerced = generate_coerced(N_PER_STATE)
    df_robotic = generate_robotic(N_PER_STATE)

    # Combine and shuffle
    dataset = pd.concat(
        [df_calm, df_focused, df_distressed, df_panicked, df_coerced, df_robotic],
        ignore_index=True
    )
    dataset = dataset.sample(frac=1, random_state=42).reset_index(drop=True)

    # Save
    output_path = OUTPUT_DIR / "cognitive_training_dataset.csv"
    dataset.to_csv(output_path, index=False)

    print(f"Total samples: {len(dataset):,}")
    print(f"\nClass distribution:")
    print(dataset["cognitive_state"].value_counts().to_string())
    print(f"\nFeature statistics per state:")
    print("-" * 70)

    feature_cols = [
        "hesitation_ratio", "correction_rate", "typing_speed_cps",
        "gyroscope_variance", "interaction_intensity"
    ]
    summary = dataset.groupby("cognitive_state")[feature_cols].mean().round(4)
    print(summary.to_string())
    print(f"\nSaved to: {output_path.resolve()}")
    print()


if __name__ == "__main__":
    main()
