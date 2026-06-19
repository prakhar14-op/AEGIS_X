import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import uuid

# Reproducibility
np.random.seed(42)

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "synthetic"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# CONFIGURATION: Based on proposal's behavioral signals
# ============================================================================

# Samples per scenario
N_NORMAL = 5000          # Majority class - represents typical user sessions
N_TAKEOVER = 2000        # Account takeover with progressive drift
N_SOCIAL_ENG = 2000      # Scam call / coercion victims
N_MALWARE = 1500         # Remote access malware / screen mirroring

# Number of unique simulated users
N_USERS_NORMAL = 200
N_USERS_TAKEOVER = 80
N_USERS_SOCIAL = 80
N_USERS_MALWARE = 60


def generate_user_ids(n_samples: int, n_users: int) -> np.ndarray:
    """Assign samples to simulated user sessions."""
    user_ids = [f"user_{uuid.uuid4().hex[:8]}" for _ in range(n_users)]
    return np.random.choice(user_ids, size=n_samples)


def generate_session_ids(n_samples: int) -> np.ndarray:
    """Generate unique session identifiers."""
    return [f"sess_{uuid.uuid4().hex[:12]}" for _ in range(n_samples)]


def generate_timestamps(n_samples: int, start: datetime = None) -> list:
    """Generate sequential timestamps at ~2-second intervals with jitter."""
    if start is None:
        start = datetime(2026, 6, 1, 8, 0, 0)
    timestamps = []
    for i in range(n_samples):
        # 2-second base interval + slight jitter (±200ms)
        offset = timedelta(seconds=2 * i + np.random.uniform(-0.2, 0.2))
        timestamps.append(start + offset)
    return timestamps


# ============================================================================
# FEATURE DEFINITIONS 
# ============================================================================
# The SDK captures these raw behavioral signals every 2 seconds:
#
# 1. typing_speed_cps        - Characters per second (typing cadence)
# 2. typing_rhythm_variance  - Variance in inter-key timing (ms²)
# 3. typing_pressure_mean    - Mean touch pressure during typing (0-1)
# 4. swipe_velocity_mean     - Mean swipe speed (pixels/ms)
# 5. swipe_velocity_variance - Variance in swipe speeds
# 6. swipe_straightness      - How linear the swipe path is (0-1, 1=perfectly straight)
# 7. touch_duration_mean     - Mean finger-on-screen time (ms)
# 8. touch_duration_variance - Variance in touch durations
# 9. touch_area_mean         - Mean touch contact area (relative units)
# 10. hesitation_ratio       - Fraction of 2s window spent idle (0-1)
# 11. hesitation_count       - Number of pause events (>500ms gaps)
# 12. correction_rate        - Backspace/undo events per character typed
# 13. scroll_speed_mean      - Mean scroll velocity (px/ms)
# 14. gyroscope_variance     - Device rotation variance (hand tremor indicator)
# 15. session_time_elapsed   - Seconds since session start
# 16. interaction_intensity  - Total touch/tap events in this 2s window
# ============================================================================


def generate_normal_sessions(n_samples: int) -> pd.DataFrame:
    """
    Normal user: Relaxed, natural interaction patterns.
    - Consistent typing rhythm with natural human variance
    - Moderate swipe speeds, slight irregularity in paths
    - Natural hesitations (thinking pauses)
    - Low correction rate
    - Moderate gyroscope variance (natural hand movement)
    Trust Score: T ∈ [0.78, 0.98]
    """
    data = {
        # Typing features
        "typing_speed_cps": np.random.normal(3.8, 0.6, n_samples).clip(1.5, 7.0),
        "typing_rhythm_variance": np.random.gamma(2.5, 15.0, n_samples).clip(5, 120),
        "typing_pressure_mean": np.random.normal(0.55, 0.08, n_samples).clip(0.2, 0.9),

        # Swipe features
        "swipe_velocity_mean": np.random.normal(1.2, 0.25, n_samples).clip(0.3, 2.5),
        "swipe_velocity_variance": np.random.gamma(2.0, 0.08, n_samples).clip(0.01, 0.8),
        "swipe_straightness": np.random.normal(0.82, 0.06, n_samples).clip(0.5, 0.98),

        # Touch features
        "touch_duration_mean": np.random.normal(120, 25, n_samples).clip(50, 300),
        "touch_duration_variance": np.random.gamma(3.0, 200, n_samples).clip(50, 2000),
        "touch_area_mean": np.random.normal(0.45, 0.08, n_samples).clip(0.15, 0.85),

        # Hesitation features
        "hesitation_ratio": np.random.beta(2, 18, n_samples).clip(0.0, 0.5),
        "hesitation_count": np.random.poisson(1.2, n_samples).clip(0, 8),

        # Correction features
        "correction_rate": np.random.beta(2, 40, n_samples).clip(0.0, 0.2),

        # Scroll features
        "scroll_speed_mean": np.random.normal(0.8, 0.2, n_samples).clip(0.1, 2.0),

        # Device motion
        "gyroscope_variance": np.random.gamma(3.0, 0.005, n_samples).clip(0.001, 0.08),

        # Session context
        "session_time_elapsed": np.random.uniform(5, 600, n_samples),
        "interaction_intensity": np.random.poisson(8, n_samples).clip(1, 30),
    }

    df = pd.DataFrame(data)
    df["user_id"] = generate_user_ids(n_samples, N_USERS_NORMAL)
    df["session_id"] = generate_session_ids(n_samples)
    df["timestamp"] = generate_timestamps(n_samples)
    df["label"] = "normal"
    df["cognitive_state"] = np.random.choice(
        ["calm", "focused"], size=n_samples, p=[0.6, 0.4]
    )

    return df


def generate_account_takeover_sessions(n_samples: int) -> pd.DataFrame:
    """
    Account Takeover: Attacker gains control mid-session.
    - Typing rhythm shifts dramatically (different person)
    - Swipe patterns become inconsistent with baseline
    - Touch pressure/area changes (different finger geometry)
    - No natural hesitations (attacker knows what they're doing)
    - Low correction rate (executing rehearsed actions)
    - Progressive drift: starts normal, degrades over ~20 steps
    Trust Score: T: 0.88 → 0.20 (progressive drift)
    """
    # Simulate progressive drift: first half looks somewhat normal, second half alien
    drift_progress = np.linspace(0, 1, n_samples)
    noise = np.random.uniform(-0.05, 0.05, n_samples)
    drift_factor = (drift_progress + noise).clip(0, 1)

    # Attacker's characteristics (very different from normal user)
    data = {
        # Typing: attacker types faster, more mechanical
        "typing_speed_cps": (
            3.8 * (1 - drift_factor) + 6.5 * drift_factor
            + np.random.normal(0, 0.3, n_samples)
        ).clip(1.5, 9.0),
        "typing_rhythm_variance": (
            35 * (1 - drift_factor) + 8 * drift_factor
            + np.random.normal(0, 3, n_samples)
        ).clip(2, 120),
        "typing_pressure_mean": (
            0.55 * (1 - drift_factor) + 0.72 * drift_factor
            + np.random.normal(0, 0.04, n_samples)
        ).clip(0.2, 0.95),

        # Swipes: attacker is more deliberate, different velocity profile
        "swipe_velocity_mean": (
            1.2 * (1 - drift_factor) + 1.9 * drift_factor
            + np.random.normal(0, 0.15, n_samples)
        ).clip(0.3, 3.0),
        "swipe_velocity_variance": (
            0.16 * (1 - drift_factor) + 0.04 * drift_factor
            + np.random.normal(0, 0.02, n_samples)
        ).clip(0.01, 0.5),
        "swipe_straightness": (
            0.82 * (1 - drift_factor) + 0.93 * drift_factor
            + np.random.normal(0, 0.03, n_samples)
        ).clip(0.5, 0.99),

        # Touch: different finger, different pressure profile
        "touch_duration_mean": (
            120 * (1 - drift_factor) + 75 * drift_factor
            + np.random.normal(0, 10, n_samples)
        ).clip(30, 300),
        "touch_duration_variance": (
            600 * (1 - drift_factor) + 150 * drift_factor
            + np.random.normal(0, 50, n_samples)
        ).clip(20, 2000),
        "touch_area_mean": (
            0.45 * (1 - drift_factor) + 0.62 * drift_factor
            + np.random.normal(0, 0.04, n_samples)
        ).clip(0.15, 0.9),

        # Hesitation: attacker doesn't hesitate like victim
        "hesitation_ratio": (
            0.10 * (1 - drift_factor) + 0.02 * drift_factor
            + np.random.beta(2, 30, n_samples) * 0.1
        ).clip(0.0, 0.4),
        "hesitation_count": np.where(
            drift_factor > 0.5,
            np.random.poisson(0.3, n_samples),
            np.random.poisson(1.2, n_samples)
        ).clip(0, 8),

        # Corrections: attacker makes very few mistakes
        "correction_rate": (
            0.05 * (1 - drift_factor) + 0.01 * drift_factor
            + np.random.beta(1, 50, n_samples) * 0.05
        ).clip(0.0, 0.15),

        # Scroll: attacker scrolls more aggressively
        "scroll_speed_mean": (
            0.8 * (1 - drift_factor) + 1.5 * drift_factor
            + np.random.normal(0, 0.1, n_samples)
        ).clip(0.1, 2.5),

        # Gyroscope: different holding pattern
        "gyroscope_variance": (
            0.015 * (1 - drift_factor) + 0.008 * drift_factor
            + np.random.gamma(2, 0.002, n_samples)
        ).clip(0.001, 0.06),

        # Session: attacker works quickly
        "session_time_elapsed": np.cumsum(
            np.random.uniform(1.8, 2.2, n_samples)
        ),
        "interaction_intensity": (
            8 * (1 - drift_factor) + 14 * drift_factor
            + np.random.poisson(2, n_samples)
        ).astype(int).clip(1, 35),
    }

    df = pd.DataFrame(data)
    df["user_id"] = generate_user_ids(n_samples, N_USERS_TAKEOVER)
    df["session_id"] = generate_session_ids(n_samples)
    df["timestamp"] = generate_timestamps(n_samples)
    df["label"] = "account_takeover"
    df["cognitive_state"] = np.where(
        drift_factor < 0.3, "focused",
        np.where(drift_factor < 0.7, "calm", "focused")
    )
    df["drift_progress"] = drift_factor

    return df


def generate_social_engineering_sessions(n_samples: int) -> pd.DataFrame:
    """
    Social Engineering / Scam Call Victim:
    - Under phone pressure from scammer
    - Extreme hesitation spikes (confusion, internal conflict)
    - High correction rate (making mistakes due to panic)
    - Oscillating behavior (compliant one moment, hesitant next)
    - Slower typing (distracted, multitasking with phone call)
    - Higher gyroscope variance (physical stress response)
    - Cognitive State Machine progression: focused → distressed → panicked → coerced
    Trust Score: T ∈ [0.35, 0.75] oscillating
    """
    # Panic oscillation pattern
    oscillation = np.sin(np.linspace(0, 8 * np.pi, n_samples)) * 0.3
    stress_level = np.linspace(0.2, 0.9, n_samples) + np.random.normal(0, 0.08, n_samples)
    stress_level = stress_level.clip(0.1, 1.0)

    data = {
        # Typing: slow, erratic under pressure
        "typing_speed_cps": (
            np.random.normal(1.8, 0.5, n_samples)
            - stress_level * 0.6
            + oscillation * 0.3
        ).clip(0.5, 4.0),
        "typing_rhythm_variance": (
            np.random.gamma(4, 30, n_samples)
            + stress_level * 80
        ).clip(10, 350),
        "typing_pressure_mean": (
            np.random.normal(0.65, 0.1, n_samples)
            + stress_level * 0.12
        ).clip(0.3, 0.95),

        # Swipes: hesitant, incomplete
        "swipe_velocity_mean": (
            np.random.normal(0.6, 0.15, n_samples)
            - stress_level * 0.2
            + oscillation * 0.1
        ).clip(0.1, 1.5),
        "swipe_velocity_variance": (
            np.random.gamma(3, 0.1, n_samples)
            + stress_level * 0.15
        ).clip(0.02, 0.8),
        "swipe_straightness": (
            np.random.normal(0.68, 0.08, n_samples)
            - stress_level * 0.12
        ).clip(0.35, 0.92),

        # Touch: longer holds (freezing), irregular
        "touch_duration_mean": (
            np.random.normal(180, 40, n_samples)
            + stress_level * 80
        ).clip(80, 500),
        "touch_duration_variance": (
            np.random.gamma(4, 400, n_samples)
            + stress_level * 1500
        ).clip(100, 5000),
        "touch_area_mean": (
            np.random.normal(0.50, 0.1, n_samples)
            + stress_level * 0.08
        ).clip(0.2, 0.9),

        # Hesitation: VERY HIGH - hallmark of coercion
        "hesitation_ratio": (
            np.random.beta(5, 5, n_samples) * 0.4
            + stress_level * 0.35
            + np.abs(oscillation) * 0.1
        ).clip(0.05, 0.85),
        "hesitation_count": (
            np.random.poisson(4, n_samples)
            + (stress_level * 5).astype(int)
        ).clip(0, 15),

        # Corrections: HIGH - panic causes errors
        "correction_rate": (
            np.random.beta(4, 6, n_samples) * 0.3
            + stress_level * 0.2
        ).clip(0.02, 0.6),

        # Scroll: minimal, victim is focused on transaction under pressure
        "scroll_speed_mean": (
            np.random.normal(0.4, 0.15, n_samples)
            - stress_level * 0.15
        ).clip(0.05, 1.2),

        # Gyroscope: HIGH - physical stress, shaking hands
        "gyroscope_variance": (
            np.random.gamma(4, 0.008, n_samples)
            + stress_level * 0.03
        ).clip(0.005, 0.12),

        # Session: long (scammer keeps victim on phone)
        "session_time_elapsed": np.cumsum(
            np.random.uniform(2.5, 4.0, n_samples)
        ),
        "interaction_intensity": (
            np.random.poisson(4, n_samples)
            - (stress_level * 2).astype(int)
        ).clip(1, 15),
    }

    df = pd.DataFrame(data)
    df["user_id"] = generate_user_ids(n_samples, N_USERS_SOCIAL)
    df["session_id"] = generate_session_ids(n_samples)
    df["timestamp"] = generate_timestamps(n_samples)
    df["label"] = "social_engineering"

    # Cognitive state progression: calm → focused → distressed → panicked → coerced
    cognitive_states = []
    for s in stress_level:
        if s < 0.25:
            cognitive_states.append("focused")
        elif s < 0.45:
            cognitive_states.append("distressed")
        elif s < 0.7:
            cognitive_states.append("panicked")
        else:
            cognitive_states.append("coerced")
    df["cognitive_state"] = cognitive_states
    df["stress_level"] = stress_level

    return df


def generate_remote_malware_sessions(n_samples: int) -> pd.DataFrame:
    """
    Remote Malware / Screen Mirroring:
    - Automated/scripted interactions
    - Near-zero variance in ALL features (robot-precise)
    - Extremely fast, perfectly timed inputs
    - No hesitations, no corrections
    - Perfect swipe straightness
    - Zero gyroscope movement (desktop controlling phone)
    - Sessions are short (automated fund transfer)
    Trust Score: T ∈ [0.25, 0.55]
    """
    data = {
        # Typing: inhuman speed, zero rhythm variance
        "typing_speed_cps": np.random.normal(9.5, 0.15, n_samples).clip(8.0, 12.0),
        "typing_rhythm_variance": np.random.exponential(1.5, n_samples).clip(0.1, 8.0),
        "typing_pressure_mean": np.random.normal(0.50, 0.01, n_samples).clip(0.45, 0.55),

        # Swipes: perfectly consistent (programmatic)
        "swipe_velocity_mean": np.random.normal(2.4, 0.06, n_samples).clip(2.0, 3.0),
        "swipe_velocity_variance": np.random.exponential(0.005, n_samples).clip(0.001, 0.03),
        "swipe_straightness": np.random.normal(0.99, 0.005, n_samples).clip(0.97, 1.0),

        # Touch: perfectly uniform (simulated touch events)
        "touch_duration_mean": np.random.normal(50, 3, n_samples).clip(40, 65),
        "touch_duration_variance": np.random.exponential(5, n_samples).clip(1, 25),
        "touch_area_mean": np.random.normal(0.40, 0.01, n_samples).clip(0.37, 0.43),

        # Hesitation: ZERO (no human decision-making)
        "hesitation_ratio": np.random.exponential(0.005, n_samples).clip(0.0, 0.03),
        "hesitation_count": np.zeros(n_samples, dtype=int),

        # Corrections: ZERO (no mistakes in scripted actions)
        "correction_rate": np.random.exponential(0.002, n_samples).clip(0.0, 0.01),

        # Scroll: precise, uniform
        "scroll_speed_mean": np.random.normal(1.8, 0.04, n_samples).clip(1.6, 2.1),

        # Gyroscope: near-zero (phone is stationary, controlled remotely)
        "gyroscope_variance": np.random.exponential(0.0005, n_samples).clip(0.0001, 0.003),

        # Session: short, automated fund transfers
        "session_time_elapsed": np.cumsum(
            np.random.uniform(1.9, 2.1, n_samples)
        ),
        "interaction_intensity": np.random.poisson(15, n_samples).clip(10, 25),
    }

    df = pd.DataFrame(data)
    df["user_id"] = generate_user_ids(n_samples, N_USERS_MALWARE)
    df["session_id"] = generate_session_ids(n_samples)
    df["timestamp"] = generate_timestamps(n_samples)
    df["label"] = "remote_malware"
    df["cognitive_state"] = "robotic"

    return df


# ============================================================================
# MAIN GENERATION
# ============================================================================

def main():
    print("=" * 70)
    print("AEGIS-X Phase 1: Behavioral Data Generation")
    print("=" * 70)
    print()

    # Generate each scenario
    print(f"[1/4] Generating Normal User sessions (n={N_NORMAL})...")
    df_normal = generate_normal_sessions(N_NORMAL)

    print(f"[2/4] Generating Account Takeover sessions (n={N_TAKEOVER})...")
    df_takeover = generate_account_takeover_sessions(N_TAKEOVER)

    print(f"[3/4] Generating Social Engineering sessions (n={N_SOCIAL_ENG})...")
    df_social = generate_social_engineering_sessions(N_SOCIAL_ENG)

    print(f"[4/4] Generating Remote Malware sessions (n={N_MALWARE})...")
    df_malware = generate_remote_malware_sessions(N_MALWARE)

    # Save individual CSVs
    print()
    print("Saving individual scenario files...")
    df_normal.to_csv(OUTPUT_DIR / "normal_sessions.csv", index=False)
    df_takeover.to_csv(OUTPUT_DIR / "account_takeover_sessions.csv", index=False)
    df_social.to_csv(OUTPUT_DIR / "social_engineering_sessions.csv", index=False)
    df_malware.to_csv(OUTPUT_DIR / "remote_malware_sessions.csv", index=False)

    # Combine and shuffle for training
    print("Creating combined dataset...")
    combined = pd.concat(
        [df_normal, df_takeover, df_social, df_malware],
        ignore_index=True
    )

    # Drop scenario-specific columns for combined training set
    training_cols = [
        "user_id", "session_id", "timestamp",
        "typing_speed_cps", "typing_rhythm_variance", "typing_pressure_mean",
        "swipe_velocity_mean", "swipe_velocity_variance", "swipe_straightness",
        "touch_duration_mean", "touch_duration_variance", "touch_area_mean",
        "hesitation_ratio", "hesitation_count", "correction_rate",
        "scroll_speed_mean", "gyroscope_variance",
        "session_time_elapsed", "interaction_intensity",
        "label", "cognitive_state"
    ]
    combined_clean = combined[[c for c in training_cols if c in combined.columns]]
    combined_clean = combined_clean.sample(frac=1, random_state=42).reset_index(drop=True)
    combined_clean.to_csv(OUTPUT_DIR / "combined_behavioral_dataset.csv", index=False)

    # Print summary statistics
    print()
    print("=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    print(f"\nTotal samples: {len(combined_clean):,}")
    print(f"\nClass distribution:")
    print(combined_clean["label"].value_counts().to_string())
    print(f"\nCognitive state distribution:")
    print(combined_clean["cognitive_state"].value_counts().to_string())
    print(f"\nFeature columns: {len(training_cols) - 4}")  # minus metadata cols
    print(f"\nFiles saved to: {OUTPUT_DIR.resolve()}")
    print()

    # Print feature statistics per class
    feature_cols = [
        "typing_speed_cps", "typing_rhythm_variance", "hesitation_ratio",
        "correction_rate", "swipe_velocity_mean", "gyroscope_variance"
    ]
    print("Key Feature Means by Class:")
    print("-" * 70)
    summary = combined_clean.groupby("label")[feature_cols].mean().round(4)
    print(summary.to_string())
    print()


if __name__ == "__main__":
    main()
