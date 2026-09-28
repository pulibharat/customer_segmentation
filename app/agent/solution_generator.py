"""Generate issue-aware support replies from customer context and memory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SolutionResult:
    response: str
    category: str
    resolution_time_minutes: int
    confidence: float


class SolutionGenerator:
    """Generates deterministic support replies that work without external LLM APIs."""

    def generate(self, customer_id: str, message: str, context: Any, sentiment: Any) -> SolutionResult:
        category = "technical"
        message_lower = (message or "").lower()
        if "billing" in message_lower or "invoice" in message_lower:
            category = "billing"
        elif "login" in message_lower or "password" in message_lower or "auth" in message_lower:
            category = "authentication"
        elif "api" in message_lower or "timeout" in message_lower:
            category = "api"

        memory_note = ""
        if context and getattr(context, "memory_summary", None):
            memory_note = f" Based on previous support history, {context.memory_summary.lower()}"

        if getattr(sentiment, "category", "normal") == "high":
            response = (
                f"I’m sorry this is impacting your operations. I’ve flagged this as high-priority and we’ll move quickly."
                f"{memory_note} Please share the exact error message and affected workflow so we can resolve it immediately."
            )
            resolution_minutes = 10
            confidence = 0.86
        else:
            response = (
                f"Thanks for sharing this. I can help with the {category} issue and keep the troubleshooting focused."
                f"{memory_note} Let’s verify the affected endpoint, account state, and any recent changes so we can isolate the cause quickly."
            )
            resolution_minutes = 15
            confidence = 0.8

        return SolutionResult(
            response=response,
            category=category,
            resolution_time_minutes=resolution_minutes,
            confidence=round(confidence, 3),
        )
