from __future__ import annotations

from discovery.core.models import (
    DiscoveryRole,
)


def fallback_role_for(
    role: DiscoveryRole,
) -> DiscoveryRole | None:
    """
    One alternate capability role maximum.

    The failed provider is never identified to
    the fallback provider.
    """

    if role == "rapid":
        return "complex"

    if role == "complex":
        return "rapid"

    return None
