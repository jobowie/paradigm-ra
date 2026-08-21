from __future__ import annotations

import json
import sys
from pathlib import Path

from discovery.benchmark.evaluator import (
    evaluate_automatically,
)
from discovery.benchmark.scenarios import (
    DISCOVERY_BENCHMARK_SCENARIOS,
)
from discovery.models import DiscoveryTurnInput


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


def get_scenario(scenario_id: str):
    for scenario in DISCOVERY_BENCHMARK_SCENARIOS:
        if scenario.id == scenario_id:
            return scenario

    raise ValueError(
        f"Unknown scenario: {scenario_id}"
    )


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: python -m discovery.benchmark.run_one "
            "<provider> <scenario_id>"
        )

    provider_name = sys.argv[1]
    scenario_id = sys.argv[2]

    provider = get_provider(provider_name)
    scenario = get_scenario(scenario_id)

    turn = DiscoveryTurnInput(
        contact=scenario.contact,
        history=scenario.history,
        latest_prospect_message=(
            scenario.latest_prospect_message
        ),
        current_state=scenario.current_state,
    )

    print()
    print("RA DISCOVERY DERBY — LIVE LAP")
    print("-----------------------------")
    print(
        f"Horse:    {provider.provider}"
    )
    print(
        f"Model:    {provider.model}"
    )
    print(
        f"Scenario: {scenario.id} — {scenario.title}"
    )
    print()

    result = provider.discover(turn)

    score = evaluate_automatically(
        scenario,
        result,
    )

    print("RA RESPONSE")
    print("-----------")
    print(result.response.reply)
    print()

    print("DISCOVERY STATE")
    print("---------------")
    print(
        result.response.state.model_dump_json(
            indent=2
        )
    )
    print()

    print("AUTOMATIC SCORE")
    print("---------------")
    print(
        f"Business understanding: "
        f"{score.business_understanding:.1f}/20"
    )
    print(
        f"Discovery efficiency:   "
        f"{score.discovery_efficiency:.1f}/20"
    )
    print(
        f"State accuracy:         "
        f"{score.state_accuracy:.1f}/15"
    )
    print(
        f"Latency:                "
        f"{score.latency:.1f}/3"
    )
    print(
        f"Cost:                   "
        f"{score.cost:.1f}/2"
    )
    print(
        f"TOTAL:                  "
        f"{score.total:.1f}/60"
    )
    print()

    if score.notes:
        print("SCORER NOTES")
        print("------------")

        for note in score.notes:
            print(f"- {note}")

        print()

    output = {
        "provider": result.provider,
        "model": result.model,
        "scenario_id": scenario.id,
        "scenario_title": scenario.title,
        "latency_ms": result.latency_ms,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "response": result.response.model_dump(),
        "automatic_score": score.model_dump(),
    }

    path = Path(
        "discovery/benchmark/runs"
    ) / (
        f"{provider.provider}-"
        f"{scenario.id}.json"
    )

    path.write_text(
        json.dumps(
            output,
            indent=2,
        )
    )

    print(f"Result saved: {path}")
    print()


if __name__ == "__main__":
    main()
