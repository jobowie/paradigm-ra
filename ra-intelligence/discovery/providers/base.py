from __future__ import annotations

from typing import Protocol

from discovery.models import (
    DiscoveryProviderResult,
    DiscoveryTurnInput,
)


class DiscoveryProvider(Protocol):
    provider: str
    model: str

    def discover(
        self,
        turn: DiscoveryTurnInput,
    ) -> DiscoveryProviderResult:
        ...
