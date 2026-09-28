import asyncio
from typing import Any

from app.agent.support_agent import SupportAgent
from app.memory.hindsight_client import HindsightClient


class FakeGroqClient:
    async def generate_support_decision(
        self,
        customer_id: str,
        message: str,
        context: Any,
        fallback_sentiment: Any,
    ) -> dict[str, Any]:
        return {
            "sentiment": {
                "frustration": 0.91,
                "urgency": 0.88,
                "keywords": ["outage"],
            },
            "category": "api",
            "response": "I have prioritized the outage and need the affected endpoint to continue triage.",
            "resolution_time_minutes": 7,
            "confidence": 0.94,
        }


def test_groq_decision_overrides_fallback_response() -> None:
    agent = SupportAgent(
        memory_client=HindsightClient(),
        groq_client=FakeGroqClient(),
    )

    result = asyncio.run(
        agent.process_ticket(
            customer_id="cust_groq",
            message="The API is down",
        )
    )

    assert result.response.startswith("I have prioritized")
    assert result.metadata["urgency"] == 0.88
    assert result.metadata["frustration"] == 0.91
    assert result.metadata["escalation_route"] == "priority_support"
    assert result.metadata["response_provider"] == "groq"
