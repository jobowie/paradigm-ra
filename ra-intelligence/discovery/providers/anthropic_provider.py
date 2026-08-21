from __future__ import annotations

import json
import os
import time

from pydantic import BaseModel

from discovery.composer import compose_discovery_request
from discovery.models import (
    DiscoveryAgentResponse,
    DiscoveryProviderResult,
    DiscoveryState,
    DiscoveryTurnInput,
)
from discovery.providers.config import PROVIDER_CONFIG


class AnthropicEnvelope(BaseModel):
    reply: str
    stage: str
    complete: bool
    recommended_next_step: str
    state_json: str


STATE_TRANSPORT_INSTRUCTIONS = """
ANTHROPIC TRANSPORT FORMAT

The structured response contains a field named state_json.

state_json must be a JSON-encoded object representing Ra's canonical
DiscoveryState with exactly these fields:

company_name: string or null
contact_name: string or null
website: string or null
business_description: string or null
primary_problem: string or null
current_process: string or null
current_systems: array of strings
pain_points: array of strings
desired_outcomes: array of strings
service_category: one of web, automation, integrations,
  accounting_solutions, custom_software, advisory, mixed, unknown
users_or_teams_affected: array of strings
integrations_needed: array of strings
requirements: array of strings
business_impact: string or null
urgency: string or null
timeline: string or null
budget_context: string or null
decision_process: string or null
qualification_score: integer from 0 through 100
missing_information: array of strings

Use null or an empty array when information is unknown.
Do not omit any DiscoveryState field.

stage must be one of:
problem, business_context, current_process, systems, impact,
desired_outcome, scope, timeline, budget, decision_process, complete

recommended_next_step must be one of:
continue_discovery, book_discovery_call,
request_more_information, not_a_fit
""".strip()


class AnthropicDiscoveryProvider:
    provider = "anthropic"

    def __init__(self) -> None:
        self.model = PROVIDER_CONFIG["anthropic"]["model"]

    def discover(
        self,
        turn: DiscoveryTurnInput,
    ) -> DiscoveryProviderResult:
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not configured. "
                "No API request was made."
            )

        if not self.model:
            raise RuntimeError(
                "RA_ANTHROPIC_MODEL has not been selected. "
                "No API request was made."
            )

        from anthropic import Anthropic

        request = compose_discovery_request(turn)

        user_prompt = (
            request["user"]
            + "\n\n"
            + STATE_TRANSPORT_INSTRUCTIONS
        )

        client = Anthropic(api_key=api_key)

        started = time.perf_counter()

        response = client.messages.parse(
            model=self.model,
            max_tokens=1600,
            system=request["system"],
            messages=[
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            output_format=AnthropicEnvelope,
        )

        latency_ms = (
            time.perf_counter() - started
        ) * 1000

        envelope = response.parsed_output

        if envelope is None:
            raise RuntimeError(
                "Anthropic returned no parsed discovery response."
            )

        try:
            state_data = json.loads(
                envelope.state_json
            )
        except json.JSONDecodeError as error:
            raise RuntimeError(
                "Anthropic returned invalid state_json."
            ) from error

        state = DiscoveryState.model_validate(
            state_data
        )

        parsed = DiscoveryAgentResponse(
            reply=envelope.reply,
            stage=envelope.stage,
            complete=envelope.complete,
            recommended_next_step=(
                envelope.recommended_next_step
            ),
            state=state,
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
                + (output_tokens * 10.00)
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
