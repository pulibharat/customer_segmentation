"""Persistent Hindsight memory adapter with local fallback."""

from __future__ import annotations

import logging
from typing import Any

from app.memory.hindsight_client import HindsightClient
from config import HINDSIGHT_API_KEY, HINDSIGHT_BANK_ID, HINDSIGHT_BASE_URL, HINDSIGHT_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)


class PersistentHindsightClient(HindsightClient):
    """Use Hindsight Cloud when configured and retain the local demo fallback."""

    def __init__(self) -> None:
        super().__init__()
        self.bank_id = HINDSIGHT_BANK_ID
        self.remote_enabled = bool(HINDSIGHT_API_KEY and HINDSIGHT_BASE_URL)
        self.remote_client: Any | None = None
        if self.remote_enabled:
            try:
                from hindsight_client import Hindsight

                self.remote_client = Hindsight(
                    base_url=HINDSIGHT_BASE_URL,
                    api_key=HINDSIGHT_API_KEY,
                    timeout=HINDSIGHT_TIMEOUT_SECONDS,
                )
            except Exception:
                logger.warning(
                    "Hindsight SDK unavailable; using local memory fallback", exc_info=True)
                self.remote_enabled = False

    @staticmethod
    def _customer_tag(customer_id: str) -> str:
        return f"customer:{customer_id}"

    async def warmup(self) -> dict[str, Any]:
        if not self.remote_enabled or self.remote_client is None:
            return await super().warmup()
        try:
            await self.remote_client.acreate_bank(
                bank_id=self.bank_id,
                name="Customer Support Agent",
                mission="Remember customer support interactions, issues, resolutions, and preferences.",
                retain_mission="Extract customer issues, resolutions, sentiment, and useful support context.",
                enable_observations=True,
            )
            version = await self.remote_client.aget_version()
            return {"status": "connected", "provider": "hindsight", "api_version": version.api_version}
        except Exception:
            logger.warning(
                "Hindsight warmup failed; using local memory fallback", exc_info=True)
            return {"status": "fallback", "provider": "local"}

    async def get_customer_tickets(self, customer_id: str, limit: int = 5) -> list[dict[str, Any]]:
        if not self.remote_enabled or self.remote_client is None:
            return await super().get_customer_tickets(customer_id, limit)
        try:
            response = await self.remote_client.arecall(
                bank_id=self.bank_id,
                query=f"support tickets, customer messages, agent responses, and resolutions for customer {customer_id}",
                types=["experience", "observation"],
                max_tokens=3500,
                budget="mid",
                tags=[self._customer_tag(customer_id)],
                tags_match="any_strict",
            )
            results = []
            for item in response.results[:limit]:
                text = getattr(item, "text", None) or (
                    item.get("text", "") if isinstance(item, dict) else "")
                results.append({
                    "customer_id": customer_id,
                    "ticket_id": getattr(item, "document_id", None) or (item.get("document_id") if isinstance(item, dict) else None) or "hindsight-memory",
                    "message": text,
                    "response": text,
                    "category": "memory",
                    "channel": "hindsight",
                    "status": "remembered",
                })
            return results
        except Exception:
            logger.warning(
                "Hindsight recall failed; using local ticket history", exc_info=True)
            return await super().get_customer_tickets(customer_id, limit)

    async def get_customer_profile(self, customer_id: str) -> dict[str, Any]:
        profile = await super().get_customer_profile(customer_id)
        if self.remote_enabled:
            tickets = await self.get_customer_tickets(customer_id, limit=100)
            profile["total_tickets"] = max(
                profile.get("total_tickets", 0), len(tickets))
        return profile

    async def record_ticket_interaction(
        self,
        customer_id: str,
        message: str,
        response: str,
        category: str,
        ticket_id: str,
        channel: str,
    ) -> dict[str, Any]:
        entry = await super().record_ticket_interaction(
            customer_id=customer_id,
            message=message,
            response=response,
            category=category,
            ticket_id=ticket_id,
            channel=channel,
        )
        if self.remote_enabled and self.remote_client is not None:
            try:
                content = (
                    f"Customer {customer_id} opened support ticket {ticket_id} through {channel}. "
                    f"Issue category: {category}. Customer message: {message}. "
                    f"Agent response: {response}."
                )
                await self.remote_client.aretain(
                    bank_id=self.bank_id,
                    content=content,
                    context="Customer support ticket interaction",
                    document_id=ticket_id,
                    metadata={"customer_id": customer_id,
                              "category": category, "channel": channel},
                    tags=[self._customer_tag(
                        customer_id), f"ticket:{ticket_id}", f"category:{category}"],
                    retain_async=False,
                )
            except Exception:
                logger.warning(
                    "Hindsight retain failed; local interaction was preserved", exc_info=True)
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
        result = await super().resolve_ticket(
            customer_id=customer_id,
            ticket_id=ticket_id,
            outcome=outcome,
            resolution_method=resolution_method,
            resolution_time_minutes=resolution_time_minutes,
            satisfaction_score=satisfaction_score,
        )
        if self.remote_enabled and self.remote_client is not None:
            try:
                content = (
                    f"Support ticket {ticket_id} for customer {customer_id} was {outcome}. "
                    f"Resolution method: {resolution_method or 'standard_flow'}. "
                    f"Resolution time: {resolution_time_minutes} minutes. "
                    f"Satisfaction score: {satisfaction_score if satisfaction_score is not None else 'not provided'}."
                )
                await self.remote_client.aretain(
                    bank_id=self.bank_id,
                    content=content,
                    context="Customer support ticket resolution",
                    document_id=f"{ticket_id}:resolution",
                    metadata={"customer_id": customer_id,
                              "ticket_id": ticket_id, "outcome": outcome},
                    tags=[self._customer_tag(
                        customer_id), f"ticket:{ticket_id}", "resolution"],
                    retain_async=False,
                )
            except Exception:
                logger.warning(
                    "Hindsight resolution retain failed; local resolution was preserved", exc_info=True)
        return result

    async def get_memory_status(self) -> dict[str, Any]:
        if not self.remote_enabled:
            return await super().get_memory_status()
        try:
            version = await self.remote_client.aget_version()
            return {
                "status": "connected",
                "provider": "hindsight",
                "bank_id": self.bank_id,
                "api_version": version.api_version,
            }
        except Exception:
            return {"status": "fallback", "provider": "local", "bank_id": self.bank_id}

    async def close(self) -> None:
        if self.remote_client is not None:
            await self.remote_client.aclose()
