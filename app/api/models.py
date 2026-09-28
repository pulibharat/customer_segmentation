from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class TicketRequest(BaseModel):
    customer_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    channel: str = Field(default="chat")


class ResolutionRequest(BaseModel):
    ticket_id: str | None = None
    customer_id: str
    outcome: str = "resolved"
    resolution_method: str | None = None
    resolution_time_minutes: int = 0
    satisfaction_score: float | None = None


class TicketResponse(BaseModel):
    ticket_id: str
    response: str
    memory_used: dict[str, Any]
    metadata: dict[str, Any]


class CustomerProfileResponse(BaseModel):
    customer_id: str
    profile: dict[str, Any]
    ticket_history: list[dict[str, Any]]
    patterns: dict[str, Any]
    metrics: dict[str, Any]


class AnalyticsResponse(BaseModel):
    total_tickets: int
    avg_resolution_time_minutes: float
    repeat_issue_rate: float
    customer_count: int
    service_status: str
