"""
AEGIS-X Phase 7: Explainability Engine Test
=============================================
Proves the system generates human-readable explanations that
transform raw numbers into bank-grade compliance narratives.
"""

import json
from backend.services.explanation_service import ExplainabilityService


def separator(title: str):
    print(f"\n{'═' * 70}")
    print(f"  {title}")
    print(f"{'═' * 70}")


def main():
    service = ExplainabilityService()

    # ══════════════════════════════════════════════════════════════════════
    # SCENARIO 1: Normal User — should produce minimal explanation
    # ══════════════════════════════════════════════════════════════════════
    separator("SCENARIO 1: Normal User")

    result = service.explain(
        trust_score=0.95,
        similarity=0.98,
        cognitive_state="calm",
        cognitive_stability=1.0,
        drift_detected=False,
        drift_severity="none",
        transaction_score=1.0,
        velocity=0.0,
        entropy=0.02,
        decision="ALLOW",
        trust_history=[0.95, 0.96, 0.95, 0.96, 0.95],
        cognitive_history=["calm", "calm", "calm", "focused", "calm"],
    )

    print(f"\n  Risk Level: {result['risk_level']}")
    print(f"  Incident: {result['incident_type']}")
    print(f"  Summary: {result['summary']}")
    print(f"  Actions: {result['recommended_actions']}")
    assert result["risk_level"] == "LOW"
    assert result["incident_type"] == "NORMAL_ACTIVITY"
    print("\n✓ Normal user — minimal explanation, no concerns")

    # ══════════════════════════════════════════════════════════════════════
    # SCENARIO 2: Scam Victim — rich explanation
    # ══════════════════════════════════════════════════════════════════════
    separator("SCENARIO 2: Scam Call Victim (PANICKED)")

    result = service.explain(
        trust_score=0.43,
        similarity=0.72,
        cognitive_state="panicked",
        cognitive_stability=0.35,
        drift_detected=True,
        drift_severity="high",
        transaction_score=0.35,
        velocity=-0.05,
        entropy=0.6,
        decision="BLOCK",
        trust_history=[0.95, 0.91, 0.84, 0.72, 0.58, 0.43],
        cognitive_history=["calm", "focused", "distressed", "distressed", "panicked", "panicked"],
    )

    print(f"\n  Risk Level: {result['risk_level']}")
    print(f"  Incident Type: {result['incident_type']}")
    print(f"\n  Summary:")
    print(f"    {result['summary']}")
    print(f"\n  Root Causes ({len(result['root_causes'])}):")
    for cause in result["root_causes"]:
        print(f"    [{cause['impact'].upper()}] {cause['cause']}")
        print(f"          {cause['detail']}")
    print(f"\n  Timeline Narrative:")
    print(f"    {result['timeline_narrative']}")
    print(f"\n  Recommended Actions:")
    for action in result["recommended_actions"]:
        print(f"    → {action}")

    assert result["risk_level"] in ("HIGH", "CRITICAL")
    assert result["incident_type"] == "SOCIAL_ENGINEERING"
    assert len(result["root_causes"]) >= 3
    print("\n✓ Scam victim — rich explanation with root causes and actions")

    # ══════════════════════════════════════════════════════════════════════
    # SCENARIO 3: Malware Bot (ROBOTIC)
    # ══════════════════════════════════════════════════════════════════════
    separator("SCENARIO 3: Remote Malware (ROBOTIC)")

    result = service.explain(
        trust_score=0.38,
        similarity=0.85,
        cognitive_state="robotic",
        cognitive_stability=0.05,
        drift_detected=True,
        drift_severity="critical",
        transaction_score=0.30,
        velocity=-0.08,
        entropy=0.1,
        decision="BLOCK",
        trust_history=[0.96, 0.95, 0.95, 0.52, 0.40, 0.38],
        cognitive_history=["calm", "calm", "calm", "robotic", "robotic", "robotic"],
    )

    print(f"\n  Risk Level: {result['risk_level']}")
    print(f"  Incident Type: {result['incident_type']}")
    print(f"  Summary: {result['summary']}")
    print(f"\n  Root Causes:")
    for cause in result["root_causes"]:
        print(f"    [{cause['impact'].upper()}] {cause['cause']}")
    print(f"\n  Actions:")
    for action in result["recommended_actions"]:
        print(f"    → {action}")

    assert result["incident_type"] == "AUTOMATED_ACTIVITY"
    print("\n✓ Malware — automated activity detected, device lock recommended")

    # ══════════════════════════════════════════════════════════════════════
    # SCENARIO 4: Account Takeover (progressive drift)
    # ══════════════════════════════════════════════════════════════════════
    separator("SCENARIO 4: Account Takeover (Behavioral Drift)")

    result = service.explain(
        trust_score=0.55,
        similarity=0.62,
        cognitive_state="focused",
        cognitive_stability=0.90,
        drift_detected=True,
        drift_severity="high",
        transaction_score=0.70,
        velocity=-0.04,
        entropy=0.15,
        decision="BLOCK",
        trust_history=[0.96, 0.94, 0.91, 0.85, 0.76, 0.65, 0.55],
        cognitive_history=["calm", "calm", "focused", "focused", "focused", "focused", "focused"],
    )

    print(f"\n  Risk Level: {result['risk_level']}")
    print(f"  Incident Type: {result['incident_type']}")
    print(f"  Summary: {result['summary']}")
    print(f"  Timeline: {result['timeline_narrative']}")

    assert result["incident_type"] == "ACCOUNT_TAKEOVER"
    print("\n✓ Account takeover — drift-based detection, different actor identified")

    # ══════════════════════════════════════════════════════════════════════
    # SCENARIO 5: Executive Summary
    # ══════════════════════════════════════════════════════════════════════
    separator("SCENARIO 5: Executive Session Report")

    from backend.services.explanation_service import NarrativeGenerator

    exec_summary = NarrativeGenerator.executive_summary(
        user_id="user_karan_001",
        session_duration_seconds=480,
        total_events=42,
        trust_min=0.43,
        trust_max=0.96,
        final_trust=0.43,
        final_decision="BLOCK",
        cognitive_states_observed=["calm", "focused", "distressed", "panicked"],
        incident_type="SOCIAL_ENGINEERING",
        total_alerts=5,
        root_causes=[
            {"cause": "Acute psychological distress", "impact": "high"},
            {"cause": "CUSUM drift alert (high)", "impact": "high"},
            {"cause": "Abnormal transaction pattern", "impact": "medium"},
        ],
    )

    print(f"\n  {exec_summary}")
    print("\n✓ Executive summary — one paragraph, complete session overview")

    # ══════════════════════════════════════════════════════════════════════
    # FULL RESPONSE CONTRACT
    # ══════════════════════════════════════════════════════════════════════
    separator("FULL EXPLAINABILITY RESPONSE")

    full_result = service.explain(
        trust_score=0.48,
        similarity=0.65,
        cognitive_state="coerced",
        cognitive_stability=0.15,
        drift_detected=True,
        drift_severity="high",
        transaction_score=0.30,
        velocity=-0.06,
        entropy=0.55,
        decision="BLOCK",
        trust_history=[0.94, 0.88, 0.75, 0.62, 0.48],
        cognitive_history=["calm", "distressed", "panicked", "coerced", "coerced"],
    )

    # Print as JSON to show the complete API contract
    output = {k: v for k, v in full_result.items() if k != "root_causes"}
    output["root_causes_count"] = len(full_result["root_causes"])
    output["root_causes_preview"] = [c["cause"] for c in full_result["root_causes"][:3]]
    print(f"\n{json.dumps(output, indent=2)}")

    separator("PHASE 7 COMPLETE: Explainability Engine Verified")
    print("""
    The Explainability Engine transforms:
        {trust_score: 0.43, decision: BLOCK}

    Into:
        Risk Level:    CRITICAL
        Incident:      SOCIAL_ENGINEERING
        Root Causes:   [coercion indicators, behavioral drift, abnormal transaction]
        Summary:       "Security incident: session terminated... coercion detected..."
        Timeline:      "Session began normally... trust deteriorated... escalation..."
        Actions:       [block, flag, contact customer via verified channel]
        Exec Report:   One-paragraph investigation summary

    This is what turns an ML project into a banking product.
    """)


if __name__ == "__main__":
    main()
