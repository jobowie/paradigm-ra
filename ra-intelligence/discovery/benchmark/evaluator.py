from __future__ import annotations

import re
from typing import Any

from discovery.benchmark.models import DiscoveryBenchmarkScenario
from discovery.benchmark.results import AutomaticScore
from discovery.models import DiscoveryProviderResult, DiscoveryState


STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "their",
    "what",
    "from",
    "into",
    "immediately",
    "again",
    "asking",
    "full",
    "one",
}


def normalize(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def field_is_captured(
    state: DiscoveryState,
    field_name: str,
) -> bool:
    value = getattr(state, field_name)

    if isinstance(value, list):
        return len(value) > 0

    if isinstance(value, str):
        return bool(value.strip())

    if isinstance(value, (int, float)):
        return True

    return value is not None


def topic_tokens(topic: str) -> list[str]:
    return [
        token
        for token in normalize(topic).split()
        if len(token) >= 3 and token not in STOPWORDS
    ]


def mentions_topic(
    text: str,
    topic: str,
) -> bool:
    normalized_text = normalize(text)
    tokens = topic_tokens(topic)

    if not tokens:
        return False

    hits = sum(
        1
        for token in tokens
        if token in normalized_text
    )

    required_hits = max(
        1,
        (len(tokens) + 1) // 2,
    )

    return hits >= required_hits


def values_preserved(
    expected: Any,
    actual: Any,
) -> bool:
    if isinstance(expected, list):
        if not isinstance(actual, list):
            return False

        normalized_actual = [
            normalize(item)
            if isinstance(item, str)
            else item
            for item in actual
        ]

        for item in expected:
            normalized_expected = (
                normalize(item)
                if isinstance(item, str)
                else item
            )

            if normalized_expected not in normalized_actual:
                return False

        return True

    if isinstance(expected, str) and isinstance(actual, str):
        expected_text = normalize(expected)
        actual_text = normalize(actual)

        return (
            expected_text == actual_text
            or expected_text in actual_text
            or actual_text in expected_text
        )

    return expected == actual


def score_business_understanding(
    scenario: DiscoveryBenchmarkScenario,
    result: DiscoveryProviderResult,
    notes: list[str],
) -> float:
    score = 0.0

    accepted_services = (
        scenario.expected.acceptable_service_categories
        or [scenario.expected.service_category]
    )

    if (
        result.response.state.service_category
        in accepted_services
    ):
        score += 10
    else:
        notes.append(
            "Service mismatch: "
            f"expected one of {accepted_services}, "
            f"received {result.response.state.service_category}."
        )

    required_fields = [
        field_name
        for field_name in scenario.expected.must_capture
        if field_name != "service_category"
    ]

    if not required_fields:
        return score + 10

    captured = sum(
        1
        for field_name in required_fields
        if field_is_captured(
            result.response.state,
            field_name,
        )
    )

    score += (captured / len(required_fields)) * 10

    if captured < len(required_fields):
        notes.append(
            f"Captured {captured}/{len(required_fields)} "
            "expected discovery fields."
        )

    return score


def score_discovery_efficiency(
    scenario: DiscoveryBenchmarkScenario,
    result: DiscoveryProviderResult,
    notes: list[str],
) -> float:
    score = 0.0
    reply = result.response.reply

    question_count = reply.count("?")

    if scenario.expected.complete:
        if question_count == 0:
            score += 10
        else:
            notes.append(
                "Expected discovery to stop, but response "
                f"asked {question_count} question(s)."
            )

    elif question_count <= 1:
        score += 10

    elif question_count == 2:
        score += 5
        notes.append(
            "Response asked two questions; Ra preference "
            "is one primary question per turn."
        )

    else:
        notes.append(
            f"Response asked {question_count} questions in one turn."
        )

    violations = [
        topic
        for topic in scenario.expected.avoid_question_topics
        if mentions_topic(reply, topic)
    ]

    if not violations:
        score += 10

    elif len(violations) == 1:
        score += 5
        notes.append(
            f"Potential unnecessary topic: {violations[0]}."
        )

    else:
        notes.append(
            "Multiple unnecessary topics detected: "
            + ", ".join(violations)
            + "."
        )

    return score


def score_state_accuracy(
    scenario: DiscoveryBenchmarkScenario,
    result: DiscoveryProviderResult,
    notes: list[str],
) -> float:
    score = 0.0

    if result.response.complete == scenario.expected.complete:
        score += 5
    else:
        notes.append(
            "Completion mismatch: "
            f"expected {scenario.expected.complete}, "
            f"received {result.response.complete}."
        )

    expected_next = scenario.expected.recommended_next_step

    if expected_next is None:
        score += 5

    elif result.response.recommended_next_step == expected_next:
        score += 5

    else:
        notes.append(
            "Next-step mismatch: "
            f"expected {expected_next}, "
            f"received {result.response.recommended_next_step}."
        )

    known_entries = list(
        scenario.current_state.items()
    )

    if not known_entries:
        score += 5
        return score

    output_state = result.response.state.model_dump()

    preserved = sum(
        1
        for key, value in known_entries
        if values_preserved(
            value,
            output_state.get(key),
        )
    )

    score += (
        preserved / len(known_entries)
    ) * 5

    if preserved < len(known_entries):
        notes.append(
            f"Preserved {preserved}/{len(known_entries)} "
            "previously established state fields."
        )

    return score


def score_latency(
    latency_ms: float,
) -> float:
    if latency_ms <= 2500:
        return 3

    if latency_ms <= 5000:
        return 2

    if latency_ms <= 8000:
        return 1

    return 0


def score_cost(
    estimated_cost_usd: float | None,
) -> float:
    if estimated_cost_usd is None:
        return 0

    if estimated_cost_usd <= 0.01:
        return 2

    if estimated_cost_usd <= 0.03:
        return 1.5

    if estimated_cost_usd <= 0.10:
        return 1

    return 0.5


def evaluate_automatically(
    scenario: DiscoveryBenchmarkScenario,
    result: DiscoveryProviderResult,
) -> AutomaticScore:
    notes: list[str] = []

    business_understanding = score_business_understanding(
        scenario,
        result,
        notes,
    )

    discovery_efficiency = score_discovery_efficiency(
        scenario,
        result,
        notes,
    )

    state_accuracy = score_state_accuracy(
        scenario,
        result,
        notes,
    )

    latency = score_latency(
        result.latency_ms,
    )

    cost = score_cost(
        result.estimated_cost_usd,
    )

    total = (
        business_understanding
        + discovery_efficiency
        + state_accuracy
        + latency
        + cost
    )

    return AutomaticScore(
        business_understanding=business_understanding,
        discovery_efficiency=discovery_efficiency,
        state_accuracy=state_accuracy,
        latency=latency,
        cost=cost,
        total=total,
        notes=notes,
    )
