from __future__ import annotations

import os

from discovery.core.models import (
    DiscoveryRole,
)


ROLE_BINDINGS = {
    "rapid": os.getenv(
        "RA_RAPID_PROVIDER",
        "mistral",
    ),
    "complex": os.getenv(
        "RA_COMPLEX_PROVIDER",
        "openai",
    ),
}


def provider_for_role(
    role: DiscoveryRole,
) -> str | None:
    """
    Translate a Ra capability role into infrastructure.

    Providers never receive or inspect this mapping.
    """

    if role == "handoff":
        return None

    return ROLE_BINDINGS[role]
