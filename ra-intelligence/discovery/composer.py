from __future__ import annotations

import json

from discovery.models import DiscoveryTurnInput
from discovery.prompt import RA_DISCOVERY_SYSTEM_PROMPT


def compose_discovery_request(
    turn: DiscoveryTurnInput,
) -> dict[str, str]:
    history = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in turn.history
    ]

    context = {
        "contact": {
            "first_name": turn.contact.first_name,
            "company": turn.contact.company,
        },
        "conversation_history": history,
        "current_state": turn.current_state,
        "latest_prospect_message": (
            turn.latest_prospect_message
        ),
    }

    user_prompt = f"""
DISCOVERY CONTEXT

{json.dumps(context, indent=2)}

TASK

Process the latest prospect message using the established
conversation and discovery state.

Preserve previously established facts unless the prospect
explicitly corrects them.

Extract all useful information from the prospect's message.

Then determine whether discovery should:
- continue with ONE useful next question,
- move to a Paradigm Ra discovery call,
- request necessary additional information, or
- end because the opportunity is not a fit.

Return a DiscoveryAgentResponse matching the required schema.
""".strip()

    return {
        "system": RA_DISCOVERY_SYSTEM_PROMPT.strip(),
        "user": user_prompt,
    }
