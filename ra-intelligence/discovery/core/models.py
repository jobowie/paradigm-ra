from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from discovery.models import (
    DiscoveryAgentResponse,
    DiscoveryState,
)


DiscoveryRole = Literal[
    "rapid",
    "complex",
    "handoff",
]


class ReadinessDecision(BaseModel):
    complete: bool
    score: int = Field(ge=0, le=100)
    gaps: list[str] = Field(default_factory=list)
    reason: str


class RouteDecision(BaseModel):
    role: DiscoveryRole
    complexity_score: int = Field(ge=0)
    reason: str


class FlowPlan(BaseModel):
    state: DiscoveryState
    readiness: ReadinessDecision
    route: RouteDecision


class ReconciliationResult(BaseModel):
    state: DiscoveryState
    preserved_fields: list[str] = Field(default_factory=list)
    updated_fields: list[str] = Field(default_factory=list)


class FlowFinalization(BaseModel):
    state: DiscoveryState
    readiness: ReadinessDecision
    preserved_fields: list[str] = Field(default_factory=list)
    updated_fields: list[str] = Field(default_factory=list)


class ProviderAttempt(BaseModel):
    role: Literal[
        "rapid",
        "complex",
    ]

    provider: str
    model: str | None = None

    success: bool
    error: str | None = None

    latency_ms: float | None = None
    estimated_cost_usd: float | None = None


class RaDiscoveryResult(BaseModel):
    response: DiscoveryAgentResponse

    planned_role: DiscoveryRole
    provider_used: str | None = None
    fallback_used: bool = False

    readiness_before: ReadinessDecision
    readiness_after: ReadinessDecision

    attempts: list[ProviderAttempt] = Field(
        default_factory=list
    )
