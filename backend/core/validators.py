import re
from typing import Dict, Tuple, List


VALID_USER_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.]{3,128}$')
VALID_SESSION_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.]{3,128}$')

EXPECTED_FEATURE_KEYS = [
    "typing_speed_cps",
    "key_hold_mean_ms",
    "key_flight_mean_ms",
    "typing_burst_ratio",
    "correction_rate",
    "pause_frequency",
    "hesitation_ratio",
    "long_pause_count",
    "tap_interval_mean_ms",
    "tap_duration_mean_ms",
    "swipe_velocity_mean",
    "swipe_straightness",
    "scroll_speed_mean",
    "scroll_reversals",
    "gyroscope_variance",
    "accelerometer_jerk",
]

FEATURE_BOUNDS = {
    "typing_speed_cps": (0.0, 20.0),
    "key_hold_mean_ms": (0.0, 1000.0),
    "key_flight_mean_ms": (0.0, 2000.0),
    "typing_burst_ratio": (0.0, 1.0),
    "correction_rate": (0.0, 1.0),
    "pause_frequency": (0.0, 1.0),
    "hesitation_ratio": (0.0, 1.0),
    "long_pause_count": (0, 100),
    "tap_interval_mean_ms": (0.0, 5000.0),
    "tap_duration_mean_ms": (0.0, 2000.0),
    "swipe_velocity_mean": (0.0, 5000.0),
    "swipe_straightness": (0.0, 1.0),
    "scroll_speed_mean": (0.0, 10000.0),
    "scroll_reversals": (0, 200),
    "gyroscope_variance": (0.0, 10.0),
    "accelerometer_jerk": (0.0, 50.0),
}


def validate_user_id(user_id: str) -> Tuple[bool, str]:
    if not user_id:
        return False, "user_id is required"
    if not VALID_USER_ID_PATTERN.match(user_id):
        return False, "user_id must be 3-128 chars: alphanumeric, underscore, dash, dot"
    return True, ""


def validate_session_id(session_id: str) -> Tuple[bool, str]:
    if not session_id:
        return False, "session_id is required"
    if not VALID_SESSION_ID_PATTERN.match(session_id):
        return False, "session_id must be 3-128 chars: alphanumeric, underscore, dash, dot"
    return True, ""


def validate_behavioral_event(event: Dict) -> Tuple[bool, str, List[str]]:
    if not isinstance(event, dict):
        return False, "event must be a JSON object", []

    warnings: List[str] = []
    present_keys = set(event.keys())
    expected_keys = set(EXPECTED_FEATURE_KEYS)

    missing = expected_keys - present_keys
    if len(missing) > 8:
        return False, f"Too many missing features: {len(missing)}/16", list(missing)

    for key in present_keys & expected_keys:
        val = event[key]
        if not isinstance(val, (int, float)):
            warnings.append(f"{key}: expected numeric, got {type(val).__name__}")
            continue
        if key in FEATURE_BOUNDS:
            lo, hi = FEATURE_BOUNDS[key]
            if val < lo or val > hi:
                warnings.append(f"{key}: value {val} outside expected range [{lo}, {hi}]")

    return True, "", warnings


def validate_transaction_amount(amount: float) -> Tuple[bool, str]:
    if not isinstance(amount, (int, float)):
        return False, "transaction_amount must be numeric"
    if amount < 0:
        return False, "transaction_amount cannot be negative"
    if amount > 10_000_000:
        return False, "transaction_amount exceeds maximum allowed (₹1 crore)"
    return True, ""


def sanitize_string(value: str, max_length: int = 256) -> str:
    if not isinstance(value, str):
        return ""
    value = value.strip()
    value = re.sub(r'[<>{}]', '', value)
    return value[:max_length]
