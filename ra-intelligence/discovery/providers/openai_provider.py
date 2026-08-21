from __future__ import annotations

import os
import time

from discovery.composer import compose_discovery_request
from discovery.models import (
    DiscoveryAgentResponse,
    DiscoveryProviderResult,
    DiscoveryTurnInput,
)
from discovery.providers.config import PROVIDER_CONFIG


class OpenAIDiscoveryProvider:
    provider = "openai"

    def __init__(self) -> None:
        self.model = PROVIDER_CONFIG["openai"]["model"]

    def discover(
        self,
        turn: DiscoveryTurnInput,
    ) -> DiscoveryProviderResult:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured. "
                "No API request was made."
            )

        from openai import OpenAI

        request = compose_discovery_request(turn)

        client = OpenAI(api_key=api_key)

        started = time.perf_counter()

        response = client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": request["system"],
                },
                {
                    "role": "user",
                    "content": request["user"],
                },
            ],
            text_format=DiscoveryAgentResponse,
            store=False,
        )

        latency_ms = (
            time.perf_counter() - started
        ) * 1000

        parsed = response.output_parsed

        if parsed is None:
            raise RuntimeError(
                "OpenAI returned no parsed discovery response."
            )

        usage = getattr(response, "usage", None)

        input_tokens = getattr(
            usage,
            "input_tokens",
            None,
        )

        output_tokens = getattr(
            usage,
            "output_tokens",
            None,
        )

        estimated_cost_usd = None

        if (
            input_tokens is not None
            and output_tokens is not None
        ):
            estimated_cost_usd = (
                (input_tokens * 2.00)
                + (output_tokens * 12.00)
            ) / 1_000_000

        return DiscoveryProviderResult(
            provider=self.provider,
            model=self.model,
            response=parsed,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost_usd=estimated_cost_usd,
        )
