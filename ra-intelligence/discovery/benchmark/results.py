from __future__ import annotations

from pydantic import BaseModel, Field

from discovery.models import DiscoveryAgentResponse


class AutomaticScore(BaseModel):
    business_understanding: float = Field(ge=0, le=20)
    discovery_efficiency: float = Field(ge=0, le=20)
    state_accuracy: float = Field(ge=0, le=15)
    latency: float = Field(ge=0, le=3)
    cost: float = Field(ge=0, le=2)

    total: float = Field(ge=0, le=60)
    max_score: int = 60

    notes: list[str] = Field(default_factory=list)


class HumanScore(BaseModel):
    next_question_quality: float | None = None
    consultative_tone: float | None = None
    experience_continuity: float | None = None

    total: float | None = None
    max_score: int = 40


class BenchmarkCaseResult(BaseModel):
    scenario_id: str
    scenario_title: str

    provider: str
    model: str

    response: DiscoveryAgentResponse | None = None

    latency_ms: float | None = None
    estimated_cost_usd: float | None = None

    automatic_score: AutomaticScore | None = None
    human_score: HumanScore = Field(default_factory=HumanScore)

    final_score: float | None = None
    error: str | None = None


class BenchmarkRunResult(BaseModel):
    provider: str
    model: str

    started_at: str
    completed_at: str

    cases: list[BenchmarkCaseResult]

    automatic_average: float
    reviewed_average: float | None = None
