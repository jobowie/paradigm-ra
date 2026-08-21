from __future__ import annotations

from datetime import datetime, timezone

from discovery.benchmark.evaluator import evaluate_automatically
from discovery.benchmark.results import (
    BenchmarkCaseResult,
    BenchmarkRunResult,
    HumanScore,
)
from discovery.benchmark.scenarios import (
    DISCOVERY_BENCHMARK_SCENARIOS,
)
from discovery.models import DiscoveryTurnInput
from discovery.providers.base import DiscoveryProvider


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def run_discovery_benchmark(
    provider: DiscoveryProvider,
) -> BenchmarkRunResult:
    started_at = utc_now()

    cases: list[BenchmarkCaseResult] = []

    for scenario in DISCOVERY_BENCHMARK_SCENARIOS:
        try:
            turn = DiscoveryTurnInput(
                contact=scenario.contact,
                history=scenario.history,
                latest_prospect_message=(
                    scenario.latest_prospect_message
                ),
                current_state=scenario.current_state,
            )

            result = provider.discover(turn)

            automatic_score = evaluate_automatically(
                scenario,
                result,
            )

            cases.append(
                BenchmarkCaseResult(
                    scenario_id=scenario.id,
                    scenario_title=scenario.title,
                    provider=result.provider,
                    model=result.model,
                    response=result.response,
                    latency_ms=result.latency_ms,
                    estimated_cost_usd=(
                        result.estimated_cost_usd
                    ),
                    automatic_score=automatic_score,
                    human_score=HumanScore(),
                )
            )

        except Exception as error:
            cases.append(
                BenchmarkCaseResult(
                    scenario_id=scenario.id,
                    scenario_title=scenario.title,
                    provider=provider.provider,
                    model=provider.model,
                    error=str(error),
                )
            )

    successful = [
        case
        for case in cases
        if case.automatic_score is not None
    ]

    automatic_average = (
        sum(
            case.automatic_score.total
            for case in successful
            if case.automatic_score is not None
        )
        / len(successful)
        if successful
        else 0
    )

    return BenchmarkRunResult(
        provider=provider.provider,
        model=provider.model,
        started_at=started_at,
        completed_at=utc_now(),
        cases=cases,
        automatic_average=automatic_average,
    )
