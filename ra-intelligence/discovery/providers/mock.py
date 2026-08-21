from __future__ import annotations

from discovery.models import (
    DiscoveryAgentResponse,
    DiscoveryProviderResult,
    DiscoveryState,
    DiscoveryTurnInput,
)


class MockDiscoveryProvider:
    provider = "ra"
    model = "mock-v0"

    def discover(
        self,
        turn: DiscoveryTurnInput,
    ) -> DiscoveryProviderResult:
        state_data = dict(turn.current_state)

        state_data.setdefault(
            "company_name",
            turn.contact.company,
        )

        state_data.setdefault(
            "contact_name",
            turn.contact.first_name,
        )

        state_data.setdefault(
            "primary_problem",
            turn.latest_prospect_message,
        )

        state = DiscoveryState(
            **state_data,
        )

        response = DiscoveryAgentResponse(
            reply=(
                "That gives me a useful starting point. "
                "What outcome would make solving this "
                "most valuable to the business?"
            ),
            stage="desired_outcome",
            complete=False,
            recommended_next_step="continue_discovery",
            state=state,
        )

        return DiscoveryProviderResult(
            provider=self.provider,
            model=self.model,
            response=response,
            latency_ms=25,
            input_tokens=0,
            output_tokens=0,
            estimated_cost_usd=0,
        )
