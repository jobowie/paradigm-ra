from discovery.benchmark.scenarios import (
    DISCOVERY_BENCHMARK_SCENARIOS,
)
from discovery.models import DiscoveryTurnInput
from discovery.providers.mistral import (
    MistralDiscoveryProvider,
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

    provider = MistralDiscoveryProvider()

    print()
    print("RA DISCOVERY — MISTRAL ADAPTER")
    print("------------------------------")
    print(f"Provider: {provider.provider}")
    print(f"Model:    {provider.model}")

    try:
        provider.discover(turn)

    except RuntimeError as error:
        expected = (
            "MISTRAL_API_KEY is not configured"
        )

        if expected not in str(error):
            raise

        print("API key:  intentionally absent")
        print("Network:  no request made")
        print()
        print("Adapter guard: PASS ✓")
        print()
        return

    raise AssertionError(
        "Smoke test expected the API-key guard."
    )


if __name__ == "__main__":
    main()
