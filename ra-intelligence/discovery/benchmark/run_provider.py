from __future__ import annotations

import json
import sys
from pathlib import Path

from discovery.benchmark.prompt_lock import prompt_hash
from discovery.benchmark.runner import run_discovery_benchmark


def get_provider(name: str):
    if name == "mistral":
        from discovery.providers.mistral import (
            MistralDiscoveryProvider,
        )
        return MistralDiscoveryProvider()

    if name == "openai":
        from discovery.providers.openai_provider import (
            OpenAIDiscoveryProvider,
        )
        return OpenAIDiscoveryProvider()

    if name == "anthropic":
        from discovery.providers.anthropic_provider import (
            AnthropicDiscoveryProvider,
        )
        return AnthropicDiscoveryProvider()

    if name == "gemini":
        from discovery.providers.gemini_provider import (
            GeminiDiscoveryProvider,
        )
        return GeminiDiscoveryProvider()

    raise ValueError(
        f"Unknown provider: {name}"
    )


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python -m discovery.benchmark.run_provider "
            "<provider>"
        )

    provider = get_provider(sys.argv[1])

    print()
    print("RA DISCOVERY DERBY — ROUND 1")
    print("----------------------------")
    print(f"Horse: {provider.provider}")
    print(f"Model: {provider.model}")
    print(
        f"Prompt: {prompt_hash()[:16]}..."
    )
    print()

    result = run_discovery_benchmark(
        provider
    )

    total_cost = 0.0

    for case in result.cases:
        if case.error:
            print(
                f"ERROR      {case.scenario_id:<18} "
                f"{case.error}"
            )
            continue

        score = (
            case.automatic_score.total
            if case.automatic_score
            else 0
        )

        latency = (
            case.latency_ms
            if case.latency_ms
            else 0
        )

        cost = (
            case.estimated_cost_usd
            if case.estimated_cost_usd
            else 0
        )

        total_cost += cost

        print(
            f"{score:5.1f}/60  "
            f"{latency:7.0f}ms  "
            f"${cost:.5f}  "
            f"{case.scenario_id:<18} "
            f"{case.scenario_title}"
        )

    print()
    print(
        "Automatic average: "
        f"{result.automatic_average:.2f}/60"
    )
    print(
        f"Estimated run cost: ${total_cost:.5f}"
    )
    print("Human review:       pending /40")
    print()

    output_dir = Path(
        "discovery/benchmark/runs"
    )
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = output_dir / (
        f"{provider.provider}-round1.json"
    )

    data = result.model_dump()
    data["prompt_sha256"] = prompt_hash()
    data["estimated_total_cost_usd"] = (
        total_cost
    )

    path.write_text(
        json.dumps(
            data,
            indent=2,
        )
        + "\n"
    )

    print(f"Round saved: {path}")
    print()


if __name__ == "__main__":
    main()
