"""Seed the support agent memory with a few sample records."""

from __future__ import annotations

import asyncio

from app.memory.hindsight_client import HindsightClient


async def main() -> None:
    client = HindsightClient()
    await client.record_ticket_interaction(
        customer_id="cust_001",
        message="API timeouts on production",
        response="We recommend checking your recent deployment and reviewing request logs.",
        category="api",
        ticket_id="ticket_001",
        channel="chat",
    )
    await client.record_ticket_interaction(
        customer_id="cust_001",
        message="Still seeing API timeouts",
        response="The fix is to roll back the last version and clear stale caches.",
        category="api",
        ticket_id="ticket_002",
        channel="email",
    )
    await client.record_ticket_interaction(
        customer_id="cust_002",
        message="Billing invoice is wrong",
        response="I’ve checked the account and the credit was applied.",
        category="billing",
        ticket_id="ticket_003",
        channel="chat",
    )
    print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(main())
