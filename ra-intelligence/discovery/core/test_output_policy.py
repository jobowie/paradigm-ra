from __future__ import annotations

from discovery.core.models import (
    FlowFinalization,
    ReadinessDecision,
)
from discovery.core.output import (
    apply_output_policy,
)
from discovery.models import (
    DiscoveryAgentResponse,
    DiscoveryState,
)


def open_finalization(
    gap: str = "decision_process",
) -> FlowFinalization:
    return FlowFinalization(
        state=DiscoveryState(
            primary_problem="Manual order entry",
            current_process=(
                "Orders are entered into QuickBooks manually."
            ),
            desired_outcomes=[
                "Digital order submission"
            ],
            timeline="Within three months",
            service_category="automation",
        ),
        readiness=ReadinessDecision(
            complete=False,
            score=70,
            gaps=[gap],
            reason="More discovery is required.",
        ),
    )


def candidate(
    reply: str,
) -> DiscoveryAgentResponse:
    return DiscoveryAgentResponse(
        reply=reply,
        stage="business_context",
        complete=False,
        recommended_next_step=(
            "continue_discovery"
        ),
        state=DiscoveryState(
            primary_problem="Manual order entry",
        ),
    )


def test_valid_question_passes() -> None:
    reply = (
        "That helps clarify the workflow. "
        "Who approves changes to this process?"
    )

    response = apply_output_policy(
        candidate(reply),
        open_finalization(),
        "Dana",
    )

    assert response.reply == reply


def test_quick_call_is_repaired() -> None:
    response = apply_output_policy(
        candidate(
            "Would you like to discuss how we "
            "might approach this in a quick call?"
        ),
        open_finalization(),
        "Dana",
    )

    assert "quick call" not in (
        response.reply.casefold()
    )

    assert response.reply == (
        "Who else would be involved in evaluating "
        "or approving a change to this process?"
    )


def test_premature_completion_is_repaired() -> None:
    response = apply_output_policy(
        candidate(
            "We have enough context for a "
            "productive discovery call."
        ),
        open_finalization(
            "timeline_or_urgency"
        ),
        "Dana",
    )

    assert response.complete is False

    assert response.reply == (
        "When would you ideally like this process "
        "improved or replaced?"
    )


def test_multiple_questions_are_repaired() -> None:
    response = apply_output_policy(
        candidate(
            "Who owns this process? "
            "When would you like it changed?"
        ),
        open_finalization(),
        "Dana",
    )

    assert response.reply.count("?") == 1


def test_provider_leak_is_repaired() -> None:
    response = apply_output_policy(
        candidate(
            "Mistral suggests this workflow could "
            "be automated. Who approves the change?"
        ),
        open_finalization(),
        "Dana",
    )

    assert "mistral" not in (
        response.reply.casefold()
    )


def main() -> None:
    tests = [
        test_valid_question_passes,
        test_quick_call_is_repaired,
        test_premature_completion_is_repaired,
        test_multiple_questions_are_repaired,
        test_provider_leak_is_repaired,
    ]

    for test in tests:
        test()

    print()
    print("RA OUTPUT VALVE v0.2")
    print("--------------------")
    print(
        f"Tests: {len(tests)}/{len(tests)} PASS"
    )
    print("Valid model output:       PASS")
    print("Premature call language:  REPAIRED")
    print("Premature completion:     REPAIRED")
    print("Multiple questions:       REPAIRED")
    print("Provider leakage:         REPAIRED")
    print()
    print(
        "Bad language does not require "
        "another model call. ✓"
    )
    print()


if __name__ == "__main__":
    main()
