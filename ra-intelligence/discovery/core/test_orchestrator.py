from __future__ import annotations

from discovery.core.context import (
    meter_turn,
)
from discovery.core.orchestrator import (
    RaDiscoveryOrchestrator,
)
from discovery.models import (
    DiscoveryAgentResponse,
    DiscoveryContact,
    DiscoveryMessage,
    DiscoveryProviderResult,
    DiscoveryState,
    DiscoveryTurnInput,
)


class FakeProvider:
    def __init__(
        self,
        provider: str,
        response: DiscoveryAgentResponse
        | None = None,
        error: Exception | None = None,
    ) -> None:
        self.provider = provider
        self.model = f"{provider}-test"
        self.response = response
        self.error = error
        self.turns: list[
            DiscoveryTurnInput
        ] = []

    def discover(
        self,
        turn: DiscoveryTurnInput,
    ) -> DiscoveryProviderResult:
        self.turns.append(
            turn
        )

        if self.error is not None:
            raise self.error

        if self.response is None:
            raise RuntimeError(
                "Fake response not configured."
            )

        return DiscoveryProviderResult(
            provider=self.provider,
            model=self.model,
            response=self.response,
            latency_ms=10.0,
            input_tokens=100,
            output_tokens=50,
            estimated_cost_usd=0.001,
        )


def make_contact(
    name: str = "Dana",
    company: str = "Westline Industrial",
) -> DiscoveryContact:
    return DiscoveryContact(
        first_name=name,
        company=company,
        email="private@example.com",
        phone="555-0100",
    )


def partial_response() -> DiscoveryAgentResponse:
    return DiscoveryAgentResponse(
        reply=(
            "How many orders do you typically "
            "process in a day or week?"
        ),
        stage="business_context",
        complete=False,
        recommended_next_step=(
            "continue_discovery"
        ),
        state=DiscoveryState(
            primary_problem=(
                "Manual order processing"
            ),
            current_process=(
                "Orders are written down and "
                "entered into QuickBooks."
            ),
            current_systems=[
                "QuickBooks"
            ],
            pain_points=[
                "Duplicate data entry"
            ],
            service_category="automation",
        ),
    )


def complete_response() -> DiscoveryAgentResponse:
    return DiscoveryAgentResponse(
        reply=(
            "What else would you like the "
            "reporting system to do?"
        ),
        stage="desired_outcome",
        complete=False,
        recommended_next_step=(
            "continue_discovery"
        ),
        state=DiscoveryState(
            primary_problem=(
                "Manual production reporting"
            ),
            current_process=(
                "Supervisors submit spreadsheets "
                "for daily consolidation."
            ),
            current_systems=[
                "Microsoft 365",
                "SQL Server",
            ],
            pain_points=[
                "Manual consolidation",
                "Delayed reporting",
            ],
            desired_outcomes=[
                "Near-real-time production reporting"
            ],
            users_or_teams_affected=[
                "Supervisors",
                "Operations",
                "Leadership",
            ],
            timeline="Within three months",
            decision_process=(
                "Taylor leads the project and "
                "the COO approves budget."
            ),
        ),
    )


def test_rapid_uses_only_mistral() -> None:
    rapid = FakeProvider(
        "mistral",
        response=partial_response(),
    )

    complex_provider = FakeProvider(
        "openai",
        response=partial_response(),
    )

    providers = {
        "mistral": rapid,
        "openai": complex_provider,
    }

    orchestrator = RaDiscoveryOrchestrator(
        provider_factory=lambda name: (
            providers[name]
        ),
        provider_available=lambda _: True,
    )

    turn = DiscoveryTurnInput(
        contact=make_contact(),
        latest_prospect_message=(
            "We write phone orders down and "
            "enter them into QuickBooks later."
        ),
    )

    result = orchestrator.discover(
        turn
    )

    assert result.planned_role == "rapid"
    assert result.provider_used == "mistral"
    assert result.fallback_used is False

    assert len(rapid.turns) == 1
    assert len(complex_provider.turns) == 0


def test_complex_uses_only_openai() -> None:
    rapid = FakeProvider(
        "mistral",
        response=partial_response(),
    )

    complex_provider = FakeProvider(
        "openai",
        response=partial_response(),
    )

    providers = {
        "mistral": rapid,
        "openai": complex_provider,
    }

    orchestrator = RaDiscoveryOrchestrator(
        provider_factory=lambda name: (
            providers[name]
        ),
        provider_available=lambda _: True,
    )

    turn = DiscoveryTurnInput(
        contact=make_contact(
            "Priya",
            "Northstar Logistics",
        ),
        latest_prospect_message=(
            "We need to modernize a legacy "
            "business-critical internal application "
            "used by several departments without "
            "disrupting operations."
        ),
    )

    result = orchestrator.discover(
        turn
    )

    assert result.planned_role == "complex"
    assert result.provider_used == "openai"

    assert len(complex_provider.turns) == 1
    assert len(rapid.turns) == 0


def test_one_isolated_fallback() -> None:
    rapid = FakeProvider(
        "mistral",
        error=RuntimeError(
            "simulated outage"
        ),
    )

    complex_provider = FakeProvider(
        "openai",
        response=partial_response(),
    )

    providers = {
        "mistral": rapid,
        "openai": complex_provider,
    }

    orchestrator = RaDiscoveryOrchestrator(
        provider_factory=lambda name: (
            providers[name]
        ),
        provider_available=lambda _: True,
    )

    turn = DiscoveryTurnInput(
        contact=make_contact(),
        latest_prospect_message=(
            "We manually enter phone orders."
        ),
    )

    result = orchestrator.discover(
        turn
    )

    assert result.provider_used == "openai"
    assert result.fallback_used is True

    assert len(rapid.turns) == 1
    assert len(complex_provider.turns) == 1
    assert len(result.attempts) == 2

    fallback_payload = (
        complex_provider.turns[0]
        .model_dump_json()
        .casefold()
    )

    assert "simulated outage" not in (
        fallback_payload
    )

    assert "mistral" not in (
        fallback_payload
    )


def test_preflight_requires_zero_models() -> None:
    rapid = FakeProvider(
        "mistral",
        response=partial_response(),
    )

    complex_provider = FakeProvider(
        "openai",
        response=partial_response(),
    )

    providers = {
        "mistral": rapid,
        "openai": complex_provider,
    }

    orchestrator = RaDiscoveryOrchestrator(
        provider_factory=lambda name: (
            providers[name]
        ),
        provider_available=lambda _: True,
    )

    state = DiscoveryState(
        primary_problem=(
            "Manual production reporting"
        ),
        current_process=(
            "Supervisors submit spreadsheets."
        ),
        current_systems=[
            "Microsoft 365",
            "SQL Server",
        ],
        desired_outcomes=[
            "Near-real-time reporting"
        ],
        users_or_teams_affected=[
            "Operations",
            "Leadership",
        ],
        timeline="Within three months",
        decision_process=(
            "Taylor leads and COO approves."
        ),
    )

    turn = DiscoveryTurnInput(
        contact=make_contact(
            "Taylor",
            "Crestview Manufacturing",
        ),
        latest_prospect_message=(
            "Anything else you need?"
        ),
        current_state=state.model_dump(),
    )

    result = orchestrator.discover(
        turn
    )

    assert result.provider_used is None
    assert result.response.complete is True
    assert (
        result.response.recommended_next_step
        == "book_discovery_call"
    )

    assert len(rapid.turns) == 0
    assert len(complex_provider.turns) == 0


def test_postflight_overrides_extra_question() -> None:
    rapid = FakeProvider(
        "mistral",
        response=complete_response(),
    )

    complex_provider = FakeProvider(
        "openai",
        response=partial_response(),
    )

    providers = {
        "mistral": rapid,
        "openai": complex_provider,
    }

    orchestrator = RaDiscoveryOrchestrator(
        provider_factory=lambda name: (
            providers[name]
        ),
        provider_available=lambda _: True,
    )

    turn = DiscoveryTurnInput(
        contact=make_contact(
            "Taylor",
            "Crestview Manufacturing",
        ),
        latest_prospect_message=(
            "We want near-real-time reporting "
            "within three months. I lead the "
            "project and our COO approves budget."
        ),
    )

    result = orchestrator.discover(
        turn
    )

    assert result.response.complete is True
    assert (
        result.response.recommended_next_step
        == "book_discovery_call"
    )

    assert "What else" not in (
        result.response.reply
    )

    assert "?" not in (
        result.response.reply
    )

    assert (
        result.response.state.qualification_score
        == result.readiness_after.score
    )


def test_context_is_metered() -> None:
    history = [
        DiscoveryMessage(
            role=(
                "prospect"
                if index % 2 == 0
                else "agent"
            ),
            content=f"Message {index}",
        )
        for index in range(10)
    ]

    turn = DiscoveryTurnInput(
        contact=make_contact(),
        history=history,
        latest_prospect_message=(
            "Latest message"
        ),
    )

    state = DiscoveryState(
        primary_problem="Manual work"
    )

    rapid_turn = meter_turn(
        turn,
        state,
        "rapid",
    )

    complex_turn = meter_turn(
        turn,
        state,
        "complex",
    )

    assert len(rapid_turn.history) == 2
    assert len(complex_turn.history) == 4

    assert rapid_turn.history[0].content == (
        "Message 8"
    )

    assert complex_turn.history[0].content == (
        "Message 6"
    )


def test_contact_truth_is_ra_owned() -> None:
    rapid = FakeProvider(
        "mistral",
        response=partial_response(),
    )

    providers = {
        "mistral": rapid,
        "openai": FakeProvider(
            "openai",
            response=partial_response(),
        ),
    }

    orchestrator = RaDiscoveryOrchestrator(
        provider_factory=lambda name: (
            providers[name]
        ),
        provider_available=lambda _: True,
    )

    turn = DiscoveryTurnInput(
        contact=make_contact(
            "Dana",
            "Westline Industrial",
        ),
        latest_prospect_message=(
            "We manually enter orders."
        ),
    )

    result = orchestrator.discover(
        turn
    )

    assert (
        result.response.state.contact_name
        == "Dana"
    )

    assert (
        result.response.state.company_name
        == "Westline Industrial"
    )


def main() -> None:
    tests = [
        test_rapid_uses_only_mistral,
        test_complex_uses_only_openai,
        test_one_isolated_fallback,
        test_preflight_requires_zero_models,
        test_postflight_overrides_extra_question,
        test_context_is_metered,
        test_contact_truth_is_ra_owned,
    ]

    for test in tests:
        test()

    print()
    print("RA ORCHESTRATOR")
    print("----------------")
    print(
        f"Tests: {len(tests)}/{len(tests)} PASS"
    )
    print("Rapid isolation:        PASS")
    print("Complex isolation:      PASS")
    print("One fallback maximum:   PASS")
    print("Preflight shutoff:      PASS")
    print("Postflight override:    PASS")
    print("Context metering:       PASS")
    print("Contact ownership:      PASS")
    print()
    print(
        "Models provide pressure. "
        "Ra controls the flow. ✓"
    )
    print()


if __name__ == "__main__":
    main()
