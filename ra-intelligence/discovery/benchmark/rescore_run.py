from __future__ import annotations

import json
import sys
from pathlib import Path

from discovery.benchmark.evaluator import evaluate_automatically
from discovery.benchmark.scenarios import DISCOVERY_BENCHMARK_SCENARIOS
from discovery.models import DiscoveryProviderResult


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python -m discovery.benchmark.rescore_run <provider>"
        )

    provider = sys.argv[1]

    path = Path(
        f"discovery/benchmark/runs/{provider}-round1.json"
    )

    data = json.loads(path.read_text())

    scenarios = {
        scenario.id: scenario
        for scenario in DISCOVERY_BENCHMARK_SCENARIOS
    }

    scores = []

    for case in data["cases"]:
        if case.get("error") or not case.get("response"):
            continue

        scenario = scenarios[case["scenario_id"]]

        result = DiscoveryProviderResult(
            provider=case["provider"],
            model=case["model"],
            response=case["response"],
            latency_ms=case["latency_ms"],
            estimated_cost_usd=case.get(
                "estimated_cost_usd"
            ),
        )

        score = evaluate_automatically(
            scenario,
            result,
        )

        case["automatic_score"] = score.model_dump()
        scores.append(score.total)

    data["automatic_average"] = (
        sum(scores) / len(scores)
        if scores
        else 0
    )

    path.write_text(
        json.dumps(data, indent=2) + "\n"
    )

    print()
    print("RA DERBY — OFFLINE RESCORE")
    print("--------------------------")
    print(f"Provider: {provider}")
    print(f"Cases:    {len(scores)}")
    print(
        f"Average:  {data['automatic_average']:.2f}/60"
    )
    print("API calls: 0")
    print()


if __name__ == "__main__":
    main()
