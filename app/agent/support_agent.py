"""Main orchestration layer for the customer support agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .context_retriever import ContextRetriever
from .escalation_router import EscalationRouter
from .sentiment_analyzer import SentimentAnalyzer
from .solution_generator import SolutionGenerator
from app.integrations.groq_client import GroqSupportClient


@dataclass
class SupportTicketResult:
    ticket_id: str
    response: str
    memory_used: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class SupportAgent:
    """Coordinate sentiment analysis, retrieval, solution generation, and routing."""

    def __init__(self, memory_client: Any | None = None, groq_client: Any | None = None) -> None:
        self.memory_client = memory_client
        self.sentiment_analyzer = SentimentAnalyzer()
        self.context_retriever = ContextRetriever(memory_client)
        self.solution_generator = SolutionGenerator()
        self.escalation_router = EscalationRouter()
        self.groq_client = groq_client if groq_client is not None else GroqSupportClient()

    async def process_ticket(self, customer_id: str, message: str, channel: str = "chat") -> SupportTicketResult:
        context = await self.context_retriever.retrieve(customer_id)
        sentiment = self.sentiment_analyzer.analyze(message)
        solution = self.solution_generator.generate(
            customer_id, message, context, sentiment)
        llm_decision = await self.groq_client.generate_support_decision(
            customer_id=customer_id,
            message=message,
            context=context,
            fallback_sentiment=sentiment,
        )
        response_provider = "deterministic_fallback"
        if llm_decision is not None:
            response_provider = "groq"
            sentiment.frustration = llm_decision["sentiment"]["frustration"]
            sentiment.urgency = llm_decision["sentiment"]["urgency"]
            sentiment.keywords = llm_decision["sentiment"]["keywords"]
            sentiment.category = "high" if max(sentiment.frustration, sentiment.urgency) >= 0.75 else "medium" if max(
                sentiment.frustration, sentiment.urgency) >= 0.5 else "normal"
            solution.response = llm_decision["response"]
            solution.category = llm_decision["category"]
            solution.resolution_time_minutes = llm_decision["resolution_time_minutes"]
            solution.confidence = llm_decision["confidence"]
        escalation = self.escalation_router.route(
            sentiment, context.customer_profile, solution.category)

        previous_count = len(context.recent_tickets)
        ticket_id = f"ticket_{customer_id}_{previous_count + 1}"

        if self.memory_client is not None:
            await self.memory_client.record_ticket_interaction(
                customer_id=customer_id,
                message=message,
                response=solution.response,
                category=solution.category,
                ticket_id=ticket_id,
                channel=channel,
            )

        return SupportTicketResult(
            ticket_id=ticket_id,
            response=solution.response,
            memory_used={
                "past_tickets_recalled": previous_count,
                "pattern_detected": bool(context.patterns.get("common_issues")),
                "escalation_suggested": escalation.should_escalate,
            },
            metadata={
                "resolution_time_estimate": f"{solution.resolution_time_minutes} min",
                "first_contact_resolution_probability": round(solution.confidence, 3),
                "customer_tier": context.customer_profile.get("tier", "Standard"),
                "escalation_route": escalation.route,
                "urgency": sentiment.urgency,
                "frustration": sentiment.frustration,
                "response_provider": response_provider,
            },
        )

    async def resolve_ticket(
        self,
        customer_id: str,
        ticket_id: str,
        outcome: str = "resolved",
        resolution_method: str | None = None,
        resolution_time_minutes: int = 5,
        satisfaction_score: float | None = None,
    ) -> dict[str, Any]:
        if self.memory_client is None:
            return {"status": "skipped", "customer_id": customer_id, "ticket_id": ticket_id}
        return await self.memory_client.resolve_ticket(
            customer_id=customer_id,
            ticket_id=ticket_id,
            outcome=outcome,
            resolution_method=resolution_method,
            resolution_time_minutes=resolution_time_minutes,
            satisfaction_score=satisfaction_score,
        )


async def handle_support_ticket(memory_client: Any | None, customer_id: str, message: str, channel: str = "chat") -> SupportTicketResult:
    agent = SupportAgent(memory_client=memory_client)
    return await agent.process_ticket(customer_id, message, channel)
