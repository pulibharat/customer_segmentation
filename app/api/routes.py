from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from app.agent.support_agent import SupportAgent, handle_support_ticket
from app.memory.persistent_hindsight_client import PersistentHindsightClient
from app.api.models import AnalyticsResponse, CustomerProfileResponse, ResolutionRequest, TicketRequest, TicketResponse

router = APIRouter()
memory_client = PersistentHindsightClient()


@router.get("/health")
async def api_health() -> dict[str, Any]:
    return {"status": "ok", "memory": "mock"}


@router.post("/support/ticket", response_model=TicketResponse)
async def create_ticket(payload: TicketRequest) -> TicketResponse:
    result = await handle_support_ticket(memory_client, payload.customer_id, payload.message, payload.channel)
    return TicketResponse(**result.__dict__)


@router.post("/support/ticket/{ticket_id}/resolve")
async def resolve_ticket(ticket_id: str, payload: ResolutionRequest) -> dict[str, Any]:
    if not ticket_id:
        raise HTTPException(status_code=400, detail="ticket_id is required")

    agent = SupportAgent(memory_client=memory_client)
    result = await agent.resolve_ticket(
        customer_id=payload.customer_id,
        ticket_id=ticket_id,
        outcome=payload.outcome,
        resolution_method=payload.resolution_method,
        resolution_time_minutes=payload.resolution_time_minutes,
        satisfaction_score=payload.satisfaction_score,
    )
    return {
        "ticket_id": ticket_id,
        "status": result.get("outcome", "resolved"),
        "customer_id": payload.customer_id,
        "outcome": payload.outcome,
        "resolution_method": payload.resolution_method,
        "resolution_time_minutes": payload.resolution_time_minutes,
        "satisfaction_score": payload.satisfaction_score,
    }


@router.get("/customer/{customer_id}/profile", response_model=CustomerProfileResponse)
async def customer_profile(customer_id: str) -> CustomerProfileResponse:
    profile = await memory_client.get_customer_profile(customer_id)
    tickets = await memory_client.get_customer_tickets(customer_id, limit=10)
    patterns = await memory_client.get_customer_patterns(customer_id)
    return CustomerProfileResponse(
        customer_id=customer_id,
        profile=profile,
        ticket_history=tickets,
        patterns=patterns,
        metrics={
            "total_tickets": len(tickets),
            "avg_resolution_time": "12 min",
            "satisfaction_score": 8.4,
            "churn_risk": profile.get("churn_risk", "low"),
        },
    )


@router.get("/analytics/metrics", response_model=AnalyticsResponse)
async def analytics_metrics() -> AnalyticsResponse:
    metrics = await memory_client.get_analytics()
    return AnalyticsResponse(
        total_tickets=metrics["total_tickets"],
        avg_resolution_time_minutes=metrics["avg_resolution_time_minutes"],
        repeat_issue_rate=metrics["repeat_issue_rate"],
        customer_count=metrics["customer_count"],
        service_status=metrics["service_status"],
    )


@router.get("/memory/status")
async def memory_status() -> dict[str, Any]:
    return await memory_client.get_memory_status()


@router.post("/demo/run-scenario")
async def run_demo_scenario() -> dict[str, Any]:
    return {"status": "ok", "scenario": "demo_complete", "message": "Demo scenario completed with in-memory mock support."}
