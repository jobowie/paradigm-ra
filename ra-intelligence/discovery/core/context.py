from __future__ import annotations

import os

from discovery.core.models import DiscoveryRole
from discovery.models import (
    DiscoveryState,
    DiscoveryTurnInput,
)


def _history_window_for_role(
    role: DiscoveryRole,
) -> int:
    if role == "rapid":
        return int(
            os.getenv(
                "RA_RAPID_HISTORY_MESSAGES",
                "2",
            )
        )

    if role == "complex":
        return int(
            os.getenv(
                "RA_COMPLEX_HISTORY_MESSAGES",
                "4",
            )
        )

    return 0


def meter_turn(
    turn: DiscoveryTurnInput,
    canonical_state: DiscoveryState,
    role: DiscoveryRole,
) -> DiscoveryTurnInput:
    """
    Ra context meter.

    Providers receive:
    - canonical Ra state
    - latest prospect message
    - only a bounded recent history window
    - contact object

    The existing composer already exposes only first name
    and company to the provider prompt, not email or phone.
    """

    window = _history_window_for_role(
        role
    )

    history = (
        turn.history[-window:]
        if window > 0
        else []
    )

    return DiscoveryTurnInput(
        contact=turn.contact,
        history=history,
        latest_prospect_message=(
            turn.latest_prospect_message
        ),
        current_state=(
            canonical_state.model_dump()
        ),
    )
