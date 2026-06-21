"""
AEGIS-X Phase 7: Explainability Engine (Langfun Layer)
=======================================================
Converts raw technical ML signals into human-readable business language
for compliance officers, bank managers, audit trails, and dashboards.

With this:
    "Trust declined from 0.91 to 0.43 due to elevated hesitation patterns,
     significant behavioral drift (42% deviation from baseline), and cognitive
     state classified as PANICKED. Assessment: possible social engineering attack.
     Recommended: block transaction, initiate fraud review."
    → Bank manager: "This is exactly what we need."
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass


# ═══════════════════════════════════════════════════════════════════════════
# RISK CLASSIFICATION (Phase 7C)
# ═══════════════════════════════════════════════════════════════════════════

class RiskClassification:
    """Maps numeric trust scores to enterprise risk labels."""

    @staticmethod
    def classify(trust_score: float) -> str:
        if trust_score > 0.85:
            return "LOW"
        elif trust_score > 0.60:
            return "MEDIUM"
        elif trust_score > 0.40:
            return "HIGH"
        return "CRITICAL"

    @staticmethod
    def risk_color(risk: str) -> str:
        """For dashboard visualization."""
        return {"LOW": "green", "MEDIUM": "amber", "HIGH": "orange", "CRITICAL": "red"}.get(risk, "gray")


# ═══════════════════════════════════════════════════════════════════════════
# INCIDENT CATEGORIZATION (Phase 7F)
# ═══════════════════════════════════════════════════════════════════════════

class IncidentClassifier:
    """Categorizes security incidents from trust pipeline signals."""

    CATEGORIES = {
        "NORMAL_ACTIVITY": "Normal user activity — no security concerns.",
        "BEHAVIORAL_DRIFT": "Gradual behavioral deviation from established baseline.",
        "SOCIAL_ENGINEERING": "Possible social engineering / scam call coercion.",
        "ACCOUNT_TAKEOVER": "Possible unauthorized account access by different actor.",
        "AUTOMATED_ACTIVITY": "Scripted or remotely-controlled device activity.",
        "HIGH_RISK_TRANSACTION": "Abnormal transaction pattern with elevated risk factors.",
    }

    @staticmethod
    def categorize(
        cognitive_state: str,
        similarity: float,
        drift_detected: bool,
        drift_severity: str,
        trust_score: float,
        transaction_score: float,
    ) -> Tuple[str, str]:
        """
        Determine incident category from pipeline signals.

        Returns:
            Tuple of (category_code, description)
        """
        # Priority order matters — most dangerous first
        if cognitive_state == "robotic":
            return "AUTOMATED_ACTIVITY", IncidentClassifier.CATEGORIES["AUTOMATED_ACTIVITY"]

        if cognitive_state in ("coerced", "panicked") and trust_score < 0.70:
            return "SOCIAL_ENGINEERING", IncidentClassifier.CATEGORIES["SOCIAL_ENGINEERING"]

        if similarity < 0.65 and drift_detected:
            return "ACCOUNT_TAKEOVER", IncidentClassifier.CATEGORIES["ACCOUNT_TAKEOVER"]

        if drift_detected and drift_severity in ("high", "critical"):
            return "BEHAVIORAL_DRIFT", IncidentClassifier.CATEGORIES["BEHAVIORAL_DRIFT"]

        if transaction_score < 0.50 and trust_score < 0.75:
            return "HIGH_RISK_TRANSACTION", IncidentClassifier.CATEGORIES["HIGH_RISK_TRANSACTION"]

        if drift_detected and drift_severity == "medium":
            return "BEHAVIORAL_DRIFT", IncidentClassifier.CATEGORIES["BEHAVIORAL_DRIFT"]

        return "NORMAL_ACTIVITY", IncidentClassifier.CATEGORIES["NORMAL_ACTIVITY"]


# ═══════════════════════════════════════════════════════════════════════════
# ROOT CAUSE ANALYSIS (Phase 7B)
# ═══════════════════════════════════════════════════════════════════════════

class RootCauseAnalyzer:
    """Identifies the contributing factors behind a trust decision."""

    @staticmethod
    def analyze(
        similarity: float,
        cognitive_state: str,
        cognitive_stability: float,
        drift_detected: bool,
        drift_severity: str,
        transaction_score: float,
        velocity: float,
        entropy: float,
        trust_score: float,
    ) -> List[Dict]:
        """
        Generate ranked list of root causes for the current trust state.

        Returns:
            List of dicts with: cause, impact (high/medium/low), detail
        """
        causes = []

        # Behavioral similarity
        if similarity < 0.60:
            causes.append({
                "cause": "Severe behavioral identity mismatch",
                "impact": "high",
                "detail": f"Behavioral similarity at {similarity:.0%} — "
                          f"significant deviation from verified user baseline.",
                "component": "behavioral_similarity",
            })
        elif similarity < 0.80:
            causes.append({
                "cause": "Moderate behavioral deviation",
                "impact": "medium",
                "detail": f"Behavioral similarity at {similarity:.0%} — "
                          f"noticeable departure from established patterns.",
                "component": "behavioral_similarity",
            })

        # Cognitive state
        if cognitive_state == "coerced":
            causes.append({
                "cause": "External coercion indicators",
                "impact": "high",
                "detail": "Behavioral signature consistent with user acting under "
                          "external direction (extreme hesitation, forced decision patterns).",
                "component": "cognitive_stability",
            })
        elif cognitive_state == "panicked":
            causes.append({
                "cause": "Acute psychological distress",
                "impact": "high",
                "detail": "Elevated hesitation, high correction frequency, and motor "
                          "control degradation suggest severe stress or panic.",
                "component": "cognitive_stability",
            })
        elif cognitive_state == "robotic":
            causes.append({
                "cause": "Automated interaction pattern",
                "impact": "high",
                "detail": "Near-zero variance across all behavioral features — "
                          "characteristic of scripted or remotely-controlled input.",
                "component": "cognitive_stability",
            })
        elif cognitive_state == "distressed":
            causes.append({
                "cause": "Cognitive uncertainty detected",
                "impact": "medium",
                "detail": f"User showing signs of confusion or divided attention "
                          f"(stability: {cognitive_stability:.0%}).",
                "component": "cognitive_stability",
            })

        # Drift
        if drift_detected:
            severity_desc = {
                "low": "gradual behavioral shift",
                "medium": "sustained behavioral divergence",
                "high": "significant cumulative deviation",
                "critical": "catastrophic behavioral change",
            }
            causes.append({
                "cause": f"CUSUM drift alert ({drift_severity})",
                "impact": "medium" if drift_severity in ("low", "medium") else "high",
                "detail": f"Change-point detection triggered — "
                          f"{severity_desc.get(drift_severity, 'behavioral anomaly')}.",
                "component": "drift_detection",
            })

        # Transaction
        if transaction_score < 0.50:
            causes.append({
                "cause": "Abnormal transaction pattern",
                "impact": "medium",
                "detail": "Transaction characteristics deviate from user's normal "
                          "patterns (amount, beneficiary, timing).",
                "component": "transaction_normality",
            })

        # Velocity
        if velocity < -0.03:
            causes.append({
                "cause": "Accelerating trust decay",
                "impact": "medium",
                "detail": f"Trust score declining at {velocity:.4f}/step — "
                          f"situation is actively worsening.",
                "component": "temporal_dynamics",
            })

        # Entropy
        if entropy > 0.4:
            causes.append({
                "cause": "Behavioral instability (oscillation)",
                "impact": "medium",
                "detail": "Erratic behavior pattern — user alternating between "
                          "compliance and resistance (social engineering indicator).",
                "component": "temporal_dynamics",
            })

        # Sort by impact
        impact_order = {"high": 0, "medium": 1, "low": 2}
        causes.sort(key=lambda c: impact_order.get(c["impact"], 3))

        return causes


# ═══════════════════════════════════════════════════════════════════════════
# NARRATIVE GENERATOR (Phase 7D, 7G, 7H)
# ═══════════════════════════════════════════════════════════════════════════

class NarrativeGenerator:
    """
    Generates human-readable narratives from trust signals.

    In production, this would use Langfun/LLM for richer language.
    For MVP, structured templates provide deterministic, fast output.
    """

    @staticmethod
    def incident_summary(
        trust_score: float,
        similarity: float,
        cognitive_state: str,
        drift_detected: bool,
        decision: str,
        incident_type: str,
        root_causes: List[Dict],
    ) -> str:
        """
        Phase 7D: Generate a concise incident summary paragraph.
        This is what appears on the dashboard alert card.
        """
        lines = []

        # Opening assessment
        if decision == "BLOCK":
            lines.append(
                f"SECURITY INCIDENT: Session terminated with trust score {trust_score:.2f}."
            )
        elif decision == "STEP_UP":
            lines.append(
                f"ELEVATED RISK: Additional verification requested (trust: {trust_score:.2f})."
            )
        else:
            lines.append(
                f"Session operating normally (trust: {trust_score:.2f})."
            )

        # Primary cause
        if root_causes:
            primary = root_causes[0]
            lines.append(f"Primary factor: {primary['detail']}")

        # Cognitive assessment
        state_descriptions = {
            "calm": "User interaction patterns are consistent and relaxed.",
            "focused": "User is actively engaged with deliberate actions.",
            "distressed": "Signs of uncertainty and divided attention observed.",
            "panicked": "Severe stress indicators — elevated hesitation, motor control degradation.",
            "coerced": "Behavioral signature strongly suggests external manipulation or duress.",
            "robotic": "Input patterns indicate automated or remotely-controlled interaction.",
        }
        if cognitive_state in ("panicked", "coerced", "robotic", "distressed"):
            lines.append(f"Cognitive assessment: {state_descriptions.get(cognitive_state, '')}")

        # Incident classification
        if incident_type != "NORMAL_ACTIVITY":
            lines.append(f"Classification: {incident_type.replace('_', ' ').title()}.")

        return " ".join(lines)

    @staticmethod
    def timeline_narrative(trust_history: List[float], cognitive_history: List[str]) -> str:
        """
        Phase 7G: Generate a narrative describing trust trajectory over time.
        This tells the STORY of what happened during the session.
        """
        if not trust_history:
            return "Insufficient session data for timeline analysis."

        lines = []
        n = len(trust_history)

        # Opening state
        initial_trust = trust_history[0]
        if initial_trust > 0.90:
            lines.append("The session began with high trust — behavior consistent with verified identity.")
        else:
            lines.append(f"The session started with moderate trust ({initial_trust:.2f}).")

        # Trajectory analysis
        if n >= 3:
            final_trust = trust_history[-1]
            delta = final_trust - initial_trust

            if delta < -0.20:
                lines.append(
                    f"Trust deteriorated significantly from {initial_trust:.2f} to {final_trust:.2f} "
                    f"over {n} observations."
                )
            elif delta < -0.05:
                lines.append("A gradual decline in trust was observed during the session.")
            elif abs(delta) < 0.05:
                lines.append("Trust remained stable throughout the session.")
            else:
                lines.append("Trust recovered during the session.")

        # Cognitive progression
        if cognitive_history and len(cognitive_history) >= 3:
            unique_states = list(dict.fromkeys(cognitive_history))  # preserve order, dedupe
            if len(unique_states) > 1:
                progression = " → ".join(unique_states)
                lines.append(f"Cognitive state progression: {progression}.")

            # Check for escalation
            severity_map = {"calm": 0, "focused": 1, "distressed": 2, "panicked": 3, "coerced": 4, "robotic": 5}
            severities = [severity_map.get(s, 0) for s in cognitive_history]
            if len(severities) >= 3 and severities[-1] > severities[0]:
                lines.append("The cognitive state escalated during the session, indicating worsening conditions.")

        # Closing
        if trust_history[-1] < 0.60:
            lines.append("The session ended in a blocked state due to critical trust failure.")
        elif trust_history[-1] < 0.85:
            lines.append("The session concluded with elevated risk requiring additional verification.")

        return " ".join(lines)

    @staticmethod
    def executive_summary(
        user_id: str,
        session_duration_seconds: float,
        total_events: int,
        trust_min: float,
        trust_max: float,
        final_trust: float,
        final_decision: str,
        cognitive_states_observed: List[str],
        incident_type: str,
        total_alerts: int,
        root_causes: List[Dict],
    ) -> str:
        """
        Phase 7H: One-paragraph executive summary of entire session.
        This is what a bank fraud investigation team reads first.
        """
        duration_min = session_duration_seconds / 60

        lines = [
            f"SESSION REPORT — User: {user_id}",
            f"Duration: {duration_min:.1f} minutes ({total_events} behavioral observations).",
            f"Trust range: {trust_min:.2f} – {trust_max:.2f} (final: {final_trust:.2f}).",
            f"Final decision: {final_decision}.",
        ]

        if incident_type != "NORMAL_ACTIVITY":
            lines.append(f"Incident classification: {incident_type.replace('_', ' ').title()}.")

        if cognitive_states_observed:
            severe_states = [s for s in cognitive_states_observed if s in ("panicked", "coerced", "robotic")]
            if severe_states:
                lines.append(f"Concerning cognitive states detected: {', '.join(set(severe_states))}.")

        if root_causes:
            high_causes = [c["cause"] for c in root_causes if c["impact"] == "high"]
            if high_causes:
                lines.append(f"Primary risk factors: {'; '.join(high_causes)}.")

        if total_alerts > 0:
            lines.append(f"Security alerts generated during session: {total_alerts}.")

        if final_decision == "BLOCK":
            lines.append("Recommendation: Initiate fraud review and contact customer through verified channel.")
        elif final_decision == "STEP_UP":
            lines.append("Recommendation: Require biometric re-verification before proceeding.")

        return " ".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN EXPLAINABILITY SERVICE (combines all components)
# ═══════════════════════════════════════════════════════════════════════════

class ExplainabilityService:
    """
    Unified explainability interface — converts pipeline output to business language.

    Single method: explain(pipeline_result) → complete explanation package.
    """

    def __init__(self):
        self._risk_classifier = RiskClassification()
        self._incident_classifier = IncidentClassifier()
        self._root_cause_analyzer = RootCauseAnalyzer()
        self._narrative_generator = NarrativeGenerator()

    def explain(
        self,
        trust_score: float,
        similarity: float,
        cognitive_state: str,
        cognitive_stability: float,
        drift_detected: bool,
        drift_severity: str,
        transaction_score: float,
        velocity: float,
        entropy: float,
        decision: str,
        trust_history: Optional[List[float]] = None,
        cognitive_history: Optional[List[str]] = None,
    ) -> Dict:
        """
        Generate complete explanation package from pipeline signals.

        This is called after every trust pipeline execution to enrich
        the response with human-readable context.

        Returns:
            {
                "risk_level": "CRITICAL",
                "incident_type": "SOCIAL_ENGINEERING",
                "incident_description": "...",
                "root_causes": [...],
                "summary": "...",
                "timeline_narrative": "...",
                "recommended_actions": [...]
            }
        """
        # Risk classification
        risk_level = self._risk_classifier.classify(trust_score)

        # Incident categorization
        incident_type, incident_desc = self._incident_classifier.categorize(
            cognitive_state=cognitive_state,
            similarity=similarity,
            drift_detected=drift_detected,
            drift_severity=drift_severity,
            trust_score=trust_score,
            transaction_score=transaction_score,
        )

        # Root cause analysis
        root_causes = self._root_cause_analyzer.analyze(
            similarity=similarity,
            cognitive_state=cognitive_state,
            cognitive_stability=cognitive_stability,
            drift_detected=drift_detected,
            drift_severity=drift_severity,
            transaction_score=transaction_score,
            velocity=velocity,
            entropy=entropy,
            trust_score=trust_score,
        )

        # Incident summary
        summary = self._narrative_generator.incident_summary(
            trust_score=trust_score,
            similarity=similarity,
            cognitive_state=cognitive_state,
            drift_detected=drift_detected,
            decision=decision,
            incident_type=incident_type,
            root_causes=root_causes,
        )

        # Timeline narrative
        timeline = ""
        if trust_history:
            timeline = self._narrative_generator.timeline_narrative(
                trust_history=trust_history,
                cognitive_history=cognitive_history or [],
            )

        # Recommended actions
        actions = self._generate_actions(decision, cognitive_state, incident_type)

        return {
            "risk_level": risk_level,
            "risk_color": self._risk_classifier.risk_color(risk_level),
            "incident_type": incident_type,
            "incident_description": incident_desc,
            "root_causes": root_causes,
            "summary": summary,
            "timeline_narrative": timeline,
            "recommended_actions": actions,
        }

    def _generate_actions(self, decision: str, cognitive_state: str, incident_type: str) -> List[str]:
        """Generate recommended response actions based on the situation."""
        actions = []

        if decision == "BLOCK":
            actions.append("Immediately block pending transaction.")
            actions.append("Flag session for fraud investigation team review.")

            if cognitive_state in ("panicked", "coerced"):
                actions.append("Contact customer through verified phone number to confirm wellbeing.")
                actions.append("Do NOT use in-app messaging (scammer may be reading screen).")
            elif cognitive_state == "robotic":
                actions.append("Initiate device security scan request.")
                actions.append("Temporarily lock account pending device verification.")
            else:
                actions.append("Request customer re-authentication through separate channel.")

        elif decision == "STEP_UP":
            actions.append("Request biometric face verification before proceeding.")
            if cognitive_state in ("distressed", "panicked"):
                actions.append("Display cool-down timer (30 seconds) before allowing retry.")
                actions.append("Show in-app safety message: 'Are you being asked to make this transfer?'")
            else:
                actions.append("Send OTP to registered mobile number.")

        else:
            actions.append("No action required — session operating within normal parameters.")

        return actions
