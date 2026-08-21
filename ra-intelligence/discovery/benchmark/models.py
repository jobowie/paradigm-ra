from __future__ import annotations

from pydantic import BaseModel, Field

from discovery.models import (
    DiscoveryContact,
    DiscoveryMessage,
    DiscoveryNextStep,
    DiscoveryService,
    DiscoveryStage,
)


class BenchmarkExpectation(BaseModel):
    service_category: DiscoveryService
    acceptable_service_categories: list[DiscoveryService] = Field(
        default_factory=list
    )
    complete: bool
    recommended_next_step: DiscoveryNextStep | None = None

    must_capture: list[str] = Field(default_factory=list)

    preferred_question_topics: list[str] = Field(default_factory=list)
    avoid_question_topics: list[str] = Field(default_factory=list)

    notes: str


class DiscoveryBenchmarkScenario(BaseModel):
    id: str
    title: str
    stage: DiscoveryStage

    contact: DiscoveryContact

    history: list[DiscoveryMessage] = Field(default_factory=list)
    latest_prospect_message: str

    current_state: dict = Field(default_factory=dict)

    expected: BenchmarkExpectation
