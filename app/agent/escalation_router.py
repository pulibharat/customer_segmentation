"""Routes issues to the most appropriate support flow."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EscalationDecision:
    should_escalate: bool
    route: str
    reason: str


class EscalationRouter:
    """Simple rule-based escalation logic for demo purposes."""

    def route(self, sentiment, customer_profile: dict | None = None, issue_category: str = "technical") -> EscalationDecision:
        profile = customer_profile or {}
        tier = profile.get("tier", "Standard")
        urgency = getattr(sentiment, "urgency", 0.0)
        frustration = getattr(sentiment, "frustration", 0.0)

        if urgency >= 0.8 or frustration >= 0.8:
            return EscalationDecision(
                should_escalate=True,
                route="priority_support",
                reason="Customer expressed urgent or highly frustrated conditions.",
            )

        if tier in {"Enterprise", "VIP"} and issue_category in {"api", "authentication"}:
            return EscalationDecision(
                should_escalate=True,
                route="enterprise_team",
                reason="High-value customer with a technical issue requiring specialized support.",
            )

        if issue_category == "billing":
            return EscalationDecision(
                should_escalate=False,
                route="billing_team",
                reason="Billing issue appropriate for billing specialists.",
            )

        return EscalationDecision(
            should_escalate=False,
            route="general_support",
            reason="Issue can be handled through standard support flow.",
        )
