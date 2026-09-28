"""Retrieval logic for customer context and past support issues."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContextResult:
    customer_id: str
    customer_profile: dict[str, Any] = field(default_factory=dict)
    recent_tickets: list[dict[str, Any]] = field(default_factory=list)
    patterns: dict[str, Any] = field(default_factory=dict)
    memory_summary: str = ""


class ContextRetriever:
    """Lightweight customer-memory summarizer for demo and fallback mode."""

    def __init__(self, memory_client: Any | None = None) -> None:
        self.memory_client = memory_client

    async def retrieve(self, customer_id: str) -> ContextResult:
        profile = {"customer_id": customer_id, "tier": "Standard",
                   "total_tickets": 0, "churn_risk": "low"}
        recent_tickets: list[dict[str, Any]] = []
        patterns: dict[str, Any] = {
            "common_issues": [], "successful_approaches": []}
        memory_summary = "No past interaction data available."

        if self.memory_client is not None:
            profile = await self.memory_client.get_customer_profile(customer_id)
            recent_tickets = await self.memory_client.get_customer_tickets(customer_id, limit=5)
            patterns = await self.memory_client.get_customer_patterns(customer_id)
            memory_summary = self.memory_client.build_memory_summary(
                customer_id, recent_tickets, patterns)

        return ContextResult(
            customer_id=customer_id,
            customer_profile=profile,
            recent_tickets=recent_tickets,
            patterns=patterns,
            memory_summary=memory_summary,
        )
