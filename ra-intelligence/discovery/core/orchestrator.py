from __future__ import annotations

from collections.abc import Callable

from discovery.core.context import (
    meter_turn,
)
from discovery.core.failover import (
    fallback_role_for,
)
from discovery.core.flow import (
    finalize_flow,
    plan_flow,
)
from discovery.core.models import (
    FlowFinalization,
    ProviderAttempt,
    RaDiscoveryResult,
)
from discovery.core.output import (
    apply_output_policy,
    build_handoff_response,
)
from discovery.models import DiscoveryTurnInput
from discovery.providers.base import (
    DiscoveryProvider,
)
from discovery.providers.config import (
    provider_has_key,
)
from discovery.providers.factory import (
    create_discovery_provider,
)
from discovery.providers.roles import (
    provider_for_role,
)


ProviderFactory = Callable[
    [str],
    DiscoveryProvider,
]

ProviderAvailability = Callable[
    [str],
    bool,
]


class RaDiscoveryOrchestrator:
    """
    The Ra faucet.

    Ra controls:
    - whether a model is called
    - which capability role is needed
    - how much context flows in
    - one fallback maximum
    - canonical state reconciliation
    - what output is allowed through
    - when discovery ends

    Providers never receive routing or failure metadata.
    """

    def __init__(
        self,
        provider_factory: ProviderFactory = (
            create_discovery_provider
        ),
        provider_available: ProviderAvailability = (
            provider_has_key
        ),
    ) -> None:
        self.provider_factory = (
            provider_factory
        )

        self.provider_available = (
            provider_available
        )

    def discover(
        self,
        turn: DiscoveryTurnInput,
    ) -> RaDiscoveryResult:
        plan = plan_flow(
            turn
        )

        # PRE-FLIGHT SHUTOFF:
        # enough canonical truth already exists.
        if plan.route.role == "handoff":
            finalization = FlowFinalization(
                state=plan.state.model_copy(
                    update={
                        "qualification_score": (
                            plan.readiness.score
                        ),
                        "missing_information": [],
                    }
                ),
                readiness=plan.readiness,
            )

            response = build_handoff_response(
                turn.contact.first_name,
                finalization,
            )

            return RaDiscoveryResult(
                response=response,
                planned_role="handoff",
                provider_used=None,
                fallback_used=False,
                readiness_before=(
                    plan.readiness
                ),
                readiness_after=(
                    plan.readiness
                ),
                attempts=[],
            )

        primary_role = plan.route.role

        roles = [
            primary_role,
        ]

        fallback_role = fallback_role_for(
            primary_role
        )

        if fallback_role is not None:
            roles.append(
                fallback_role
            )

        attempts: list[ProviderAttempt] = []
        last_error: Exception | None = None

        for index, role in enumerate(
            roles[:2]
        ):
            provider_name = provider_for_role(
                role
            )

            if provider_name is None:
                continue

            # Prevent accidentally calling the same
            # infrastructure twice if bindings are
            # misconfigured.
            prior_provider_names = {
                attempt.provider
                for attempt in attempts
            }

            if provider_name in prior_provider_names:
                continue

            if not self.provider_available(
                provider_name
            ):
                attempts.append(
                    ProviderAttempt(
                        role=role,
                        provider=provider_name,
                        success=False,
                        error=(
                            "Provider unavailable."
                        ),
                    )
                )

                continue

            provider = self.provider_factory(
                provider_name
            )

            metered_turn = meter_turn(
                turn=turn,
                canonical_state=plan.state,
                role=role,
            )

            try:
                result = provider.discover(
                    metered_turn
                )

                finalization = finalize_flow(
                    prior_state=plan.state,
                    candidate_state=(
                        result.response.state
                    ),
                )

                response = apply_output_policy(
                    candidate=result.response,
                    finalization=finalization,
                    first_name=(
                        turn.contact.first_name
                    ),
                )

            except Exception as error:
                last_error = error

                attempts.append(
                    ProviderAttempt(
                        role=role,
                        provider=provider_name,
                        model=getattr(
                            provider,
                            "model",
                            None,
                        ),
                        success=False,
                        error=(
                            f"{type(error).__name__}: "
                            f"{error}"
                        ),
                    )
                )

                continue

            attempts.append(
                ProviderAttempt(
                    role=role,
                    provider=result.provider,
                    model=result.model,
                    success=True,
                    latency_ms=(
                        result.latency_ms
                    ),
                    estimated_cost_usd=(
                        result.estimated_cost_usd
                    ),
                )
            )

            return RaDiscoveryResult(
                response=response,
                planned_role=primary_role,
                provider_used=result.provider,
                fallback_used=(
                    index > 0
                ),
                readiness_before=(
                    plan.readiness
                ),
                readiness_after=(
                    finalization.readiness
                ),
                attempts=attempts,
            )

        raise RuntimeError(
            "Ra Discovery could not complete the turn "
            "after the primary role and one isolated "
            "fallback attempt."
        ) from last_error
