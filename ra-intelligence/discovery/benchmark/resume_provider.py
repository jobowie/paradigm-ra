from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

from discovery.benchmark.evaluator import evaluate_automatically
from discovery.benchmark.prompt_lock import prompt_hash
from discovery.benchmark.results import (
    BenchmarkCaseResult,
    HumanScore,
)
from discovery.benchmark.scenarios import (
    DISCOVERY_BENCHMARK_SCENARIOS,
)
from discovery.benchmark.run_provider import get_provider
from discovery.models import DiscoveryTurnInput


def retry_delay(error: Exception) -> float:
    text = str(error)

    match = re.search(
        r"retry in ([0-9.]+)s",
        text,
        re.IGNORECASE,
    )

    if match:
        return float(match.group(1)) + 5

    return 65


def save_round(
    path: Path,
    data: dict,
) -> None:
    successful = [
        case
        for case in data["cases"]
        if (
            not case.get("error")
            and case.get("automatic_score")
        )
    ]

    if successful:
        data["automatic_average"] = sum(
            case["automatic_score"]["total"]
            for case in successful
        ) / len(successful)

    data["estimated_total_cost_usd"] = sum(
        case.get("estimated_cost_usd") or 0
        for case in successful
    )

    path.write_text(
        json.dumps(data, indent=2) + "\n"
    )


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python -m discovery.benchmark.resume_provider "
            "<provider>"
        )

    provider_name = sys.argv[1]

    path = Path(
        f"discovery/benchmark/runs/"
        f"{provider_name}-round1.json"
    )

    data = json.loads(path.read_text())

    stored_hash = data.get("prompt_sha256")

    if stored_hash and stored_hash != prompt_hash():
        raise RuntimeError(
            "Frozen Ra prompt does not match this round."
        )

    provider = get_provider(provider_name)

    scenarios = {
        scenario.id: scenario
        for scenario in DISCOVERY_BENCHMARK_SCENARIOS
    }

    failed_indexes = [
        index
        for index, case in enumerate(data["cases"])
        if case.get("error")
    ]

    print()
    print("RA DISCOVERY DERBY — RESUME")
    print("---------------------------")
    print(f"Horse:  {provider.provider}")
    print(f"Failed: {len(failed_indexes)}")
    print()

    for index in failed_indexes:
        old_case = data["cases"][index]
        scenario = scenarios[
            old_case["scenario_id"]
        ]

        turn = DiscoveryTurnInput(
            contact=scenario.contact,
            history=scenario.history,
            latest_prospect_message=(
                scenario.latest_prospect_message
            ),
            current_state=scenario.current_state,
        )

        try:
            result = provider.discover(turn)

            score = evaluate_automatically(
                scenario,
                result,
            )

            new_case = BenchmarkCaseResult(
                scenario_id=scenario.id,
                scenario_title=scenario.title,
                provider=result.provider,
                model=result.model,
                response=result.response,
                latency_ms=result.latency_ms,
                estimated_cost_usd=(
                    result.estimated_cost_usd
                ),
                automatic_score=score,
                human_score=HumanScore(),
            )

            data["cases"][index] = (
                new_case.model_dump()
            )

            save_round(path, data)

            print(
                f"{score.total:5.1f}/60  "
                f"{result.latency_ms:8.0f}ms  "
                f"{scenario.id}"
            )

        except Exception as error:
            text = str(error)

            if (
                "429" in text
                or "too_many_requests" in text.lower()
                or "quota" in text.lower()
            ):
                print()
                print(
                    f"Gemini quota reached at {scenario.id}."
                )
                print(
                    "Run paused safely. No completed results "
                    "will be repeated."
                )
                break

            print(
                f"ERROR {scenario.id}: {error}"
            )

    save_round(path, data)

    remaining = sum(
        1
        for case in data["cases"]
        if case.get("error")
    )

    print()
    print(
        f"Automatic average: "
        f"{data['automatic_average']:.2f}/60"
    )
    print(
        f"Remaining errors:  {remaining}"
    )
    print()


if __name__ == "__main__":
    main()
