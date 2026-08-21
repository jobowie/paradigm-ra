from __future__ import annotations

import json
from pathlib import Path

from discovery.benchmark.evaluator import (
    evaluate_automatically,
)
from discovery.benchmark.scenarios import (
    DISCOVERY_BENCHMARK_SCENARIOS,
)
from discovery.core.flow import (
    finalize_flow,
    plan_flow,
)
from discovery.core.models import (
    FlowFinalization,
)
from discovery.core.output import (
    apply_output_policy,
    build_handoff_response,
)
from discovery.models import (
    DiscoveryAgentResponse,
    DiscoveryProviderResult,
    DiscoveryTurnInput,
)
from discovery.providers.roles import (
    provider_for_role,
)


RUNS_DIR = Path(
    "discovery/benchmark/runs"
)

PROVIDERS = (
    "mistral",
    "openai",
)


def scenario_map():
    return {
        scenario.id: scenario
        for scenario
        in DISCOVERY_BENCHMARK_SCENARIOS
    }


def load_round(
    provider: str,
) -> dict:
    path = (
        RUNS_DIR
        / f"{provider}-round1.json"
    )

    return json.loads(
        path.read_text()
    )


def successful_cases(
    run: dict,
) -> dict[str, dict]:
    return {
        case["scenario_id"]: case
        for case in run["cases"]
        if (
            not case.get("error")
            and case.get("response")
            and case.get("automatic_score")
        )
    }


def make_turn(
    scenario,
) -> DiscoveryTurnInput:
    return DiscoveryTurnInput(
        contact=scenario.contact,
        history=scenario.history,
        latest_prospect_message=(
            scenario.latest_prospect_message
        ),
        current_state=(
            scenario.current_state
        ),
    )


def replay_candidate(
    provider: str,
    case: dict,
    scenario,
) -> dict:
    """
    Replay one stored model response through Ra.

    No provider API is called.
    """

    turn = make_turn(
        scenario
    )

    plan = plan_flow(
        turn
    )

    before = float(
        case["automatic_score"]["total"]
    )

    if plan.route.role == "handoff":
        finalization = FlowFinalization(
            state=plan.state.model_copy(
                update={
                    "qualification_score": (
                        plan.readiness.score
                    ),
                    "missing_information": [],
                }
            ),
            readiness=plan.readiness,
        )

        response = build_handoff_response(
            turn.contact.first_name,
            finalization,
        )

        latency_ms = 0.0
        estimated_cost = 0.0
        action = "preflight_handoff"

    else:
        candidate = (
            DiscoveryAgentResponse
            .model_validate(
                case["response"]
            )
        )

        finalization = finalize_flow(
            prior_state=plan.state,
            candidate_state=(
                candidate.state
            ),
        )

        response = apply_output_policy(
            candidate=candidate,
            finalization=finalization,
            first_name=(
                turn.contact.first_name
            ),
        )

        latency_ms = float(
            case.get(
                "latency_ms",
                0.0,
            )
            or 0.0
        )

        estimated_cost = (
            case.get(
                "estimated_cost_usd"
            )
        )

        if (
            response.complete
            and response.recommended_next_step
            == "book_discovery_call"
        ):
            action = "postflight_handoff"

        elif (
            response.complete
            and response.recommended_next_step
            == "not_a_fit"
        ):
            action = "not_a_fit"

        else:
            action = "continue"

    result = DiscoveryProviderResult(
        provider=provider,
        model=case["model"],
        response=response,
        latency_ms=latency_ms,
        estimated_cost_usd=(
            estimated_cost
        ),
    )

    score = evaluate_automatically(
        scenario,
        result,
    )

    after = score.total

    return {
        "scenario_id": scenario.id,
        "provider": provider,
        "route": plan.route.role,
        "action": action,
        "before": before,
        "after": after,
        "delta": after - before,
        "response": response.model_dump(),
        "automatic_score": (
            score.model_dump()
        ),
    }


def print_provider_replay(
    provider: str,
    results: list[dict],
) -> None:
    before_average = (
        sum(
            item["before"]
            for item in results
        )
        / len(results)
    )

    after_average = (
        sum(
            item["after"]
            for item in results
        )
        / len(results)
    )

    improved = sum(
        1
        for item in results
        if item["delta"] > 0.01
    )

    unchanged = sum(
        1
        for item in results
        if abs(item["delta"]) <= 0.01
    )

    regressed = sum(
        1
        for item in results
        if item["delta"] < -0.01
    )

    print()
    print(provider.upper())
    print("-" * len(provider))

    for item in results:
        print(
            f'{item["before"]:5.1f}'
            f' -> '
            f'{item["after"]:5.1f}'
            f'  '
            f'{item["delta"]:+5.1f}'
            f'  '
            f'{item["scenario_id"]:<20}'
            f' {item["action"]}'
        )

    print()
    print(
        f"Average: "
        f"{before_average:.2f}"
        f" -> "
        f"{after_average:.2f}"
        f" "
        f"({after_average - before_average:+.2f})"
    )

    print(
        f"Improved: {improved} | "
        f"Unchanged: {unchanged} | "
        f"Regressed: {regressed}"
    )


def build_hybrid(
    cases_by_provider: dict[
        str,
        dict[str, dict],
    ],
) -> list[dict]:
    """
    Simulate the actual Ra role policy using stored
    Derby responses:

        rapid   -> Mistral
        complex -> OpenAI

    No model sees or knows about the other.
    """

    scenarios = scenario_map()

    results: list[dict] = []

    for scenario in (
        DISCOVERY_BENCHMARK_SCENARIOS
    ):
        turn = make_turn(
            scenario
        )

        plan = plan_flow(
            turn
        )

        if plan.route.role == "handoff":
            finalization = FlowFinalization(
                state=plan.state.model_copy(
                    update={
                        "qualification_score": (
                            plan.readiness.score
                        ),
                        "missing_information": [],
                    }
                ),
                readiness=plan.readiness,
            )

            response = build_handoff_response(
                turn.contact.first_name,
                finalization,
            )

            result = DiscoveryProviderResult(
                provider="ra-core",
                model="deterministic",
                response=response,
                latency_ms=0.0,
                estimated_cost_usd=0.0,
            )

            score = evaluate_automatically(
                scenario,
                result,
            )

            results.append(
                {
                    "scenario_id": scenario.id,
                    "role": "handoff",
                    "provider": None,
                    "action": (
                        "preflight_handoff"
                    ),
                    "score": score.total,
                    "latency_ms": 0.0,
                    "cost": 0.0,
                }
            )

            continue

        provider = provider_for_role(
            plan.route.role
        )

        if provider is None:
            raise RuntimeError(
                "No provider bound to "
                f"{plan.route.role}"
            )

        case = (
            cases_by_provider[
                provider
            ][scenario.id]
        )

        replayed = replay_candidate(
            provider=provider,
            case=case,
            scenario=scenarios[
                scenario.id
            ],
        )

        results.append(
            {
                "scenario_id": scenario.id,
                "role": plan.route.role,
                "provider": provider,
                "action": replayed[
                    "action"
                ],
                "score": replayed[
                    "after"
                ],
                "latency_ms": (
                    case.get(
                        "latency_ms",
                        0.0,
                    )
                    or 0.0
                ),
                "cost": (
                    case.get(
                        "estimated_cost_usd"
                    )
                    or 0.0
                ),
            }
        )

    return results


def print_hybrid(
    results: list[dict],
) -> None:
    average = (
        sum(
            item["score"]
            for item in results
        )
        / len(results)
    )

    total_cost = sum(
        item["cost"]
        for item in results
    )

    model_calls = sum(
        1
        for item in results
        if item["provider"] is not None
    )

    print()
    print(
        "RA HYBRID — ROLE POLICY"
    )
    print(
        "-----------------------"
    )

    for item in results:
        resource = (
            item["provider"]
            if item["provider"]
            else "RA ONLY"
        )

        print(
            f'{item["score"]:5.1f}/60  '
            f'{item["scenario_id"]:<20} '
            f'{item["role"]:<8} '
            f'{resource:<8} '
            f'{item["action"]}'
        )

    print()
    print(
        f"Automatic average: "
        f"{average:.2f}/60"
    )

    print(
        f"Stored-call cost:   "
        f"${total_cost:.5f}"
    )

    print(
        f"Model calls:        "
        f"{model_calls}/"
        f"{len(results)}"
    )


def main() -> None:
    print()
    print(
        "RA DISCOVERY — OFFLINE FLOW REPLAY"
    )
    print(
        "----------------------------------"
    )
    print(
        "Network calls: 0"
    )
    print(
        "Stored Derby responses only"
    )

    runs = {
        provider: load_round(
            provider
        )
        for provider in PROVIDERS
    }

    cases_by_provider = {
        provider: successful_cases(
            run
        )
        for provider, run
        in runs.items()
    }

    provider_results = {}

    scenarios = scenario_map()

    for provider in PROVIDERS:
        results = []

        for scenario_id, case in (
            cases_by_provider[
                provider
            ].items()
        ):
            results.append(
                replay_candidate(
                    provider=provider,
                    case=case,
                    scenario=scenarios[
                        scenario_id
                    ],
                )
            )

        provider_results[
            provider
        ] = results

        print_provider_replay(
            provider,
            results,
        )

    hybrid = build_hybrid(
        cases_by_provider
    )

    print_hybrid(
        hybrid
    )

    output = {
        "network_calls": 0,
        "provider_replays": (
            provider_results
        ),
        "hybrid": hybrid,
    }

    path = (
        RUNS_DIR
        / "ra-core-offline-replay.json"
    )

    path.write_text(
        json.dumps(
            output,
            indent=2,
        )
        + "\n"
    )

    print()
    print(
        f"Saved: {path}"
    )
    print()


if __name__ == "__main__":
    main()
