from __future__ import annotations

from discovery.providers.base import (
    DiscoveryProvider,
)


def create_discovery_provider(
    provider: str,
) -> DiscoveryProvider:
    """
    Infrastructure-only provider construction.

    Ra Core routes by capability role.
    Provider names are resolved only at this boundary.
    """

    if provider == "mistral":
        from discovery.providers.mistral import (
            MistralDiscoveryProvider,
        )

        return MistralDiscoveryProvider()

    if provider == "openai":
        from discovery.providers.openai_provider import (
            OpenAIDiscoveryProvider,
        )

        return OpenAIDiscoveryProvider()

    raise ValueError(
        f"Unsupported Ra Discovery provider: {provider}"
    )
