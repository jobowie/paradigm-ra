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


class GeminiDiscoveryProvider:
    provider = "gemini"

    def __init__(self) -> None:
        self.model = PROVIDER_CONFIG["gemini"]["model"]

    def discover(
        self,
        turn: DiscoveryTurnInput,
    ) -> DiscoveryProviderResult:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "No API request was made."
            )

        from google import genai

        request = compose_discovery_request(turn)

        client = genai.Client(api_key=api_key)

        started = time.perf_counter()

        interaction = client.interactions.create(
            model=self.model,
            input=request["user"],
            system_instruction=request["system"],
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": (
                    DiscoveryAgentResponse.model_json_schema()
                ),
            },
            store=False,
        )

        latency_ms = (
            time.perf_counter() - started
        ) * 1000

        if not interaction.output_text:
            raise RuntimeError(
                "Gemini returned no discovery output."
            )

        parsed = DiscoveryAgentResponse.model_validate_json(
            interaction.output_text
        )

        usage = getattr(
            interaction,
            "usage",
            None,
        )

        input_tokens = getattr(
            usage,
            "total_input_tokens",
            None,
        )

        output_tokens = getattr(
            usage,
            "total_output_tokens",
            None,
        )

        thought_tokens = getattr(
            usage,
            "total_thought_tokens",
            0,
        ) or 0

        estimated_cost_usd = None

        if (
            input_tokens is not None
            and output_tokens is not None
        ):
            estimated_cost_usd = (
                (input_tokens * 0.75)
                + (
                    (output_tokens + thought_tokens)
                    * 3.75
                )
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
