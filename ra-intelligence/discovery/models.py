from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


DiscoveryService = Literal[
    "web",
    "automation",
    "integrations",
    "accounting_solutions",
    "custom_software",
    "advisory",
    "mixed",
    "unknown",
]

DiscoveryStage = Literal[
    "problem",
    "business_context",
    "current_process",
    "systems",
    "impact",
    "desired_outcome",
    "scope",
    "timeline",
    "budget",
    "decision_process",
    "complete",
]

DiscoveryNextStep = Literal[
    "continue_discovery",
    "book_discovery_call",
    "request_more_information",
    "not_a_fit",
]


class DiscoveryContact(BaseModel):
    first_name: str
    company: str
    email: str
    phone: str | None = None


class DiscoveryState(BaseModel):
    company_name: str | None = None
    contact_name: str | None = None
    website: str | None = None

    business_description: str | None = None
    primary_problem: str | None = None
    current_process: str | None = None

    current_systems: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    desired_outcomes: list[str] = Field(default_factory=list)

    service_category: DiscoveryService = "unknown"

    users_or_teams_affected: list[str] = Field(default_factory=list)
    integrations_needed: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)

    business_impact: str | None = None
    urgency: str | None = None
    timeline: str | None = None
    budget_context: str | None = None
    decision_process: str | None = None

    qualification_score: int = Field(default=0, ge=0, le=100)
    missing_information: list[str] = Field(default_factory=list)


class DiscoveryAgentResponse(BaseModel):
    reply: str
    stage: DiscoveryStage
    complete: bool
    recommended_next_step: DiscoveryNextStep
    state: DiscoveryState


class DiscoveryMessage(BaseModel):
    role: Literal["prospect", "agent"]
    content: str


class DiscoveryTurnInput(BaseModel):
    contact: DiscoveryContact
    history: list[DiscoveryMessage] = Field(default_factory=list)
    latest_prospect_message: str
    current_state: dict = Field(default_factory=dict)


class DiscoveryProviderResult(BaseModel):
    provider: str
    model: str
    response: DiscoveryAgentResponse

    latency_ms: float

    input_tokens: int | None = None
    output_tokens: int | None = None
    estimated_cost_usd: float | None = None
