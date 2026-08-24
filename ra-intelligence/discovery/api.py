from __future__ import annotations

import os

from fastapi import (
    Depends,
    FastAPI,
    Header,
    HTTPException,
)
from pydantic import BaseModel, Field

from discovery.core.orchestrator import (
    RaDiscoveryOrchestrator,
)
from discovery.models import (
    DiscoveryContact,
    DiscoveryMessage,
    DiscoveryState,
    DiscoveryTurnInput,
)


app = FastAPI(
    title="Ra Discovery",
    version="0.2.0",
    docs_url=None,
    redoc_url=None,
)


orchestrator = RaDiscoveryOrchestrator()


class RaContactInput(BaseModel):
    first_name: str = Field(
        min_length=1,
        max_length=80,
    )

    company: str = Field(
        min_length=1,
        max_length=160,
    )

    email: str = Field(
        min_length=3,
        max_length=320,
    )


class RaMessageInput(BaseModel):
    role: str
    content: str = Field(
        min_length=1,
        max_length=4000,
    )


class RaTurnRequest(BaseModel):
    contact: RaContactInput

    history: list[RaMessageInput] = Field(
        default_factory=list,
        max_length=20,
    )

    latest_prospect_message: str = Field(
        min_length=1,
        max_length=6000,
    )

    current_state: dict = Field(
        default_factory=dict,
    )


def require_internal_token(
    authorization: str | None = Header(
        default=None
    ),
) -> None:
    expected = os.getenv(
        "RA_DISCOVERY_INTERNAL_TOKEN"
    )

    if not expected:
        raise HTTPException(
            status_code=503,
            detail="Ra service authentication "
            "is not configured.",
        )

    prefix = "Bearer "

    if (
        authorization is None
        or not authorization.startswith(prefix)
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized.",
        )

    supplied = authorization[
        len(prefix):
    ]

    if supplied != expected:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized.",
        )


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "online",
        "service": "ra-discovery",
        "flow": "v0.2",
    }


@app.post(
    "/v1/discovery/turn",
    dependencies=[
        Depends(require_internal_token)
    ],
)
def discovery_turn(
    payload: RaTurnRequest,
) -> dict:
    history = [
        DiscoveryMessage(
            role=message.role,
            content=message.content,
        )
        for message in payload.history
        if message.role in {
            "prospect",
            "agent",
        }
    ]

    turn = DiscoveryTurnInput(
        contact=DiscoveryContact(
            first_name=(
                payload.contact.first_name
            ),
            company=(
                payload.contact.company
            ),
            email=payload.contact.email,
        ),
        history=history,
        latest_prospect_message=(
            payload.latest_prospect_message
        ),
        current_state=(
            payload.current_state
        ),
    )

    result = orchestrator.discover(
        turn
    )

    # SERVER-ONLY UAT TELEMETRY.
    # Never returned through the public API contract.
    attempt = (
        result.attempts[-1]
        if result.attempts
        else None
    )

    failed_attempt = next(
        (
            item
            for item in result.attempts
            if not item.success
        ),
        None,
    )

    print()
    print("RA FLOW — UAT")
    print("-------------")
    print(
        f"planned_role:    "
        f"{result.planned_role}"
    )
    print(
        f"provider_used:   "
        f"{result.provider_used or 'none'}"
    )
    print(
        f"fallback_used:   "
        f"{result.fallback_used}"
    )

    if failed_attempt is not None:
        print(
            f"failed_role:     "
            f"{failed_attempt.role}"
        )
        print(
            f"failed_provider: "
            f"{failed_attempt.provider}"
        )
        print(
            f"failure:         "
            f"{failed_attempt.error}"
        )

    print(
        f"readiness:       "
        f"{result.readiness_before.score}"
        f" -> "
        f"{result.readiness_after.score}"
    )
    print(
        f"complete:        "
        f"{result.response.complete}"
    )

    if attempt is not None:
        print(
            f"latency_ms:      "
            f"{attempt.latency_ms}"
        )
        print(
            f"estimated_cost:  "
            f"{attempt.estimated_cost_usd}"
        )

    print(
        f"next_step:       "
        f"{result.response.recommended_next_step}"
    )
    print()

    # PUBLIC CONTRACT:
    # Deliberately expose only Ra's authorized
    # prospect-facing result.
    #
    # No provider identity.
    # No routing decision.
    # No fallback metadata.
    # No token usage.
    # No provider cost.
    return result.response.model_dump()
