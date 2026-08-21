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


class MistralDiscoveryProvider:
    provider = "mistral"

    def __init__(self) -> None:
        self.model = PROVIDER_CONFIG["mistral"]["model"]

    def discover(
        self,
        turn: DiscoveryTurnInput,
    ) -> DiscoveryProviderResult:
        api_key = os.getenv("MISTRAL_API_KEY")

        if not api_key:
            raise RuntimeError(
                "MISTRAL_API_KEY is not configured. "
                "No API request was made."
            )

        from mistralai.client import Mistral

        request = compose_discovery_request(turn)

        client = Mistral(api_key=api_key)

        started = time.perf_counter()

        response = client.chat.parse(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": request["system"],
                },
                {
                    "role": "user",
                    "content": request["user"],
                },
            ],
            response_format=DiscoveryAgentResponse,
            temperature=0,
            max_tokens=1600,
        )

        latency_ms = (
            time.perf_counter() - started
        ) * 1000

        raw_content = (
            response.choices[0].message.content
        )

        if not isinstance(raw_content, str):
            raise RuntimeError(
                "Mistral returned an unexpected response format."
            )

        parsed = DiscoveryAgentResponse.model_validate_json(
            raw_content
        )

        usage = getattr(response, "usage", None)

        input_tokens = getattr(
            usage,
            "prompt_tokens",
            None,
        )

        output_tokens = getattr(
            usage,
            "completion_tokens",
            None,
        )

        estimated_cost_usd = None

        if (
            input_tokens is not None
            and output_tokens is not None
        ):
            estimated_cost_usd = (
                (input_tokens * 1.50)
                + (output_tokens * 7.50)
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
