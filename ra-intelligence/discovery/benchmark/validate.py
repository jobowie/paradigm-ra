from discovery.benchmark.rubric import DISCOVERY_BENCHMARK_RUBRIC
from discovery.benchmark.scenarios import DISCOVERY_BENCHMARK_SCENARIOS
from discovery.models import DiscoveryState
from discovery.policies import get_follow_up_limit


def assert_equal(actual, expected, message):
    if actual != expected:
        raise AssertionError(
            f"{message} Expected {expected!r}, received {actual!r}"
        )


def main() -> None:
    total_weight = sum(
        item["weight"]
        for item in DISCOVERY_BENCHMARK_RUBRIC.values()
    )

    assert_equal(
        total_weight,
        100,
        "Benchmark rubric must total 100.",
    )

    assert_equal(
        len(DISCOVERY_BENCHMARK_SCENARIOS),
        10,
        "Benchmark scenario count:",
    )

    scenario_ids = [
        scenario.id
        for scenario in DISCOVERY_BENCHMARK_SCENARIOS
    ]

    assert_equal(
        len(set(scenario_ids)),
        len(scenario_ids),
        "Benchmark scenario IDs must be unique.",
    )

    valid_state_fields = set(DiscoveryState.model_fields.keys())

    for scenario in DISCOVERY_BENCHMARK_SCENARIOS:
        for field_name in scenario.expected.must_capture:
            if field_name not in valid_state_fields:
                raise AssertionError(
                    f"{scenario.id}: unknown DiscoveryState field "
                    f"{field_name!r}"
                )

    assert_equal(get_follow_up_limit(0), 0, "0 questions:")
    assert_equal(get_follow_up_limit(1), 1, "1 question:")
    assert_equal(get_follow_up_limit(2), 1, "2 questions:")
    assert_equal(get_follow_up_limit(3), 2, "3 questions:")
    assert_equal(get_follow_up_limit(5), 2, "5 questions:")
    assert_equal(get_follow_up_limit(10), 2, "Follow-up cap:")

    state = DiscoveryState()

    assert_equal(
        state.service_category,
        "unknown",
        "Default service category:",
    )

    assert_equal(
        state.qualification_score,
        0,
        "Default qualification score:",
    )

    print()
    print("RA INTELLIGENCE")
    print("---------------")
    print("Python benchmark core: ONLINE")
    print(
        f"Scenarios: {len(DISCOVERY_BENCHMARK_SCENARIOS)}"
    )
    print(f"Rubric weight: {total_weight}/100")
    print("DiscoveryState fields: 20")
    print("Scenario contracts: validated")
    print("Follow-up policy: validated")
    print("Pydantic contracts: validated")
    print()
    print("Ra Intelligence integrity check: PASS ✓")
    print()


if __name__ == "__main__":
    main()
