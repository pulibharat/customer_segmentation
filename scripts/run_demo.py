"""Run the minimal demo narratives for the support agent."""

from __future__ import annotations

import asyncio

from app.agent.support_agent import handle_support_ticket
from app.memory.hindsight_client import HindsightClient


async def main() -> None:
    client = HindsightClient()
    scenarios = [
        ("cust_001", "API timeout in production"),
        ("cust_001", "API timeout again after deploy"),
        ("cust_002", "Invoice total seems incorrect"),
    ]
    for customer_id, message in scenarios:
        result = await handle_support_ticket(client, customer_id, message)
        print(f"{customer_id}: {result.response}")
    print("Demo complete.")


if __name__ == "__main__":
    asyncio.run(main())
