from discovery.benchmark.runner import run_discovery_benchmark
from discovery.providers.mock import MockDiscoveryProvider


def main() -> None:
    provider = MockDiscoveryProvider()

    result = run_discovery_benchmark(
        provider,
    )

    print()
    print("RA DISCOVERY DERBY — DRY LAP")
    print("----------------------------")
    print(
        f"Provider: {result.provider}"
    )
    print(
        f"Model:    {result.model}"
    )
    print()

    for case in result.cases:
        if case.error:
            print(
                f"ERROR  {case.scenario_id:<18} "
                f"{case.error}"
            )
            continue

        score = (
            case.automatic_score.total
            if case.automatic_score
            else 0
        )

        print(
            f"{score:5.1f}/60  "
            f"{case.scenario_id:<18} "
            f"{case.scenario_title}"
        )

    print()
    print(
        "Automatic average: "
        f"{result.automatic_average:.2f}/60"
    )
    print(
        "Human review:      pending /40"
    )
    print()


if __name__ == "__main__":
    main()
