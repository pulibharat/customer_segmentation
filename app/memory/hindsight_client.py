"""In-memory Hindsight-style client used for demos and local testing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryEntry:
    key: str
    data: dict[str, Any]
    tags: list[str] = field(default_factory=list)


class HindsightClient:
    """A lightweight in-memory memory interface that mimics Hindsight behavior."""

    def __init__(self) -> None:
        self.store: dict[str, dict[str, Any]] = {}
        self.tickets: dict[str, list[dict[str, Any]]] = {}
        self.resolution_log: list[dict[str, Any]] = []

    async def get_customer_profile(self, customer_id: str) -> dict[str, Any]:
        profile = self.store.get(f"customer:{customer_id}")
        if profile:
            return profile
        return {
            "customer_id": customer_id,
            "tier": "Standard",
            "total_tickets": 0,
            "churn_risk": "low",
            "communication_style": "balanced",
        }

    async def get_customer_tickets(self, customer_id: str, limit: int = 5) -> list[dict[str, Any]]:
        tickets = self.tickets.get(customer_id, [])
        return tickets[-limit:]

    async def get_customer_patterns(self, customer_id: str) -> dict[str, Any]:
        patterns = self.store.get(f"patterns:{customer_id}", {})
        return {
            "common_issues": patterns.get("common_issues", []),
            "successful_approaches": patterns.get("successful_approaches", []),
            "repeat_rate": patterns.get("repeat_rate", 0.15),
        }

    async def record_ticket_interaction(
        self,
        customer_id: str,
        message: str,
        response: str,
        category: str,
        ticket_id: str,
        channel: str,
    ) -> dict[str, Any]:
        entry = {
            "customer_id": customer_id,
            "ticket_id": ticket_id,
            "message": message,
            "response": response,
            "category": category,
            "channel": channel,
            "status": "open",
            "resolution_time_minutes": None,
        }
        self.tickets.setdefault(customer_id, []).append(entry)
        self.store[f"ticket:{customer_id}:{ticket_id}"] = entry

        profile = await self.get_customer_profile(customer_id)
        profile["total_tickets"] = len(self.tickets.get(customer_id, []))
        profile["tier"] = profile.get("tier", "Standard")
        profile["communication_style"] = profile.get(
            "communication_style", "balanced")
        self.store[f"customer:{customer_id}"] = profile

        patterns = self.store.get(f"patterns:{customer_id}", {
            "common_issues": [], "successful_approaches": [], "repeat_rate": 0.0,
        })
        patterns.setdefault("common_issues", [])
        if category not in patterns["common_issues"]:
            patterns["common_issues"].append(category)
        patterns.setdefault("successful_approaches", [])
        if response not in patterns["successful_approaches"]:
            patterns["successful_approaches"].append(response[:80])
        patterns["repeat_rate"] = min(
            1.0, (len(self.tickets.get(customer_id, [])) / 10))
        self.store[f"patterns:{customer_id}"] = patterns
        return entry

    async def resolve_ticket(
        self,
        customer_id: str,
        ticket_id: str,
        outcome: str,
        resolution_method: str | None = None,
        resolution_time_minutes: int = 0,
        satisfaction_score: float | None = None,
    ) -> dict[str, Any]:
        customer_tickets = self.tickets.setdefault(customer_id, [])
        for ticket in customer_tickets:
            if ticket.get("ticket_id") == ticket_id:
                ticket["status"] = outcome
                ticket["resolution_method"] = resolution_method or "standard_flow"
                ticket["resolution_time_minutes"] = resolution_time_minutes
                ticket["satisfaction_score"] = satisfaction_score
                self.store[f"ticket:{customer_id}:{ticket_id}"] = ticket
                break

        resolution_record = {
            "customer_id": customer_id,
            "ticket_id": ticket_id,
            "outcome": outcome,
            "resolution_method": resolution_method or "standard_flow",
            "resolution_time_minutes": resolution_time_minutes,
            "satisfaction_score": satisfaction_score,
        }
        self.resolution_log.append(resolution_record)

        profile = await self.get_customer_profile(customer_id)
        profile["total_tickets"] = len(customer_tickets)
        profile["churn_risk"] = "medium" if satisfaction_score is not None and satisfaction_score < 7 else "low"
        self.store[f"customer:{customer_id}"] = profile
        return resolution_record

    def build_memory_summary(self, customer_id: str, recent_tickets: list[dict[str, Any]], patterns: dict[str, Any]) -> str:
        if not recent_tickets:
            return "No prior tickets found for this customer."
        recent_issue = recent_tickets[-1].get("category", "general support")
        common_issues = ", ".join(patterns.get(
            "common_issues", [])[:3]) or recent_issue
        return f"This customer has {len(recent_tickets)} recent tickets and is most often associated with {common_issues}."

    async def warmup(self) -> dict[str, Any]:
        return {"status": "ok", "memory_store_size": len(self.store)}

    async def get_memory_status(self) -> dict[str, Any]:
        return {"status": "mock_active", "store_entries": len(self.store), "tickets_logged": len(self.resolution_log)}

    async def get_analytics(self) -> dict[str, Any]:
        all_tickets = []
        for customer_tickets in self.tickets.values():
            all_tickets.extend(customer_tickets)

        total_tickets = len(all_tickets)
        customer_count = len(self.tickets)
        avg_resolution = 0.0
        if self.resolution_log:
            avg_resolution = round(sum(item.get("resolution_time_minutes", 0)
                                   for item in self.resolution_log) / len(self.resolution_log), 2)

        repeat_issue_rate = 0.0
        if total_tickets:
            repeat_issue_rate = round(
                sum(1 for item in self.resolution_log if item.get(
                    "outcome") in {"resolved", "escalated"}) / total_tickets,
                3,
            )

        return {
            "total_tickets": total_tickets,
            "avg_resolution_time_minutes": avg_resolution,
            "repeat_issue_rate": repeat_issue_rate,
            "customer_count": customer_count,
            "service_status": "healthy",
        }
