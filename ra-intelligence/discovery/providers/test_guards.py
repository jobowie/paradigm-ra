from discovery.benchmark.scenarios import (
    DISCOVERY_BENCHMARK_SCENARIOS,
)
from discovery.models import DiscoveryTurnInput
from discovery.providers.anthropic_provider import (
    AnthropicDiscoveryProvider,
)
from discovery.providers.gemini_provider import (
    GeminiDiscoveryProvider,
)
from discovery.providers.mistral import (
    MistralDiscoveryProvider,
)
from discovery.providers.openai_provider import (
    OpenAIDiscoveryProvider,
)


def main() -> None:
    scenario = DISCOVERY_BENCHMARK_SCENARIOS[0]

    turn = DiscoveryTurnInput(
        contact=scenario.contact,
        history=scenario.history,
        latest_prospect_message=(
            scenario.latest_prospect_message
        ),
        current_state=scenario.current_state,
    )

    providers = [
        OpenAIDiscoveryProvider(),
        AnthropicDiscoveryProvider(),
        GeminiDiscoveryProvider(),
        MistralDiscoveryProvider(),
    ]

    expected_keys = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "mistral": "MISTRAL_API_KEY",
    }

    print()
    print("RA DISCOVERY — PADDOCK GUARDS")
    print("-----------------------------")

    for provider in providers:
        try:
            provider.discover(turn)

        except RuntimeError as error:
            expected = expected_keys[
                provider.provider
            ]

            if expected not in str(error):
                raise

            print(
                f"{provider.provider:<10} PASS ✓ "
                "no request made"
            )
            continue

        raise AssertionError(
            f"{provider.provider}: "
            "expected missing-key guard."
        )

    print()
    print("All provider guards: PASS ✓")
    print("Network requests made: 0")
    print()


if __name__ == "__main__":
    main()
