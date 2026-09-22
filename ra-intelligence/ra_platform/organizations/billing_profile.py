from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class OrganizationBillingProfile(
    BaseModel
):
    id: UUID = Field(
        default_factory=uuid4
    )

    organization_id: UUID

    billing_name: str | None = None
    billing_email: str | None = None

    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state_region: str | None = None
    postal_code: str | None = None
    country: str = "US"

    bank_name: str | None = None
    account_type: str | None = None

    routing_number_ciphertext: (
        str | None
    ) = None

    routing_number_last4: (
        str | None
    ) = None

    account_number_ciphertext: (
        str | None
    ) = None

    account_number_last4: (
        str | None
    ) = None

    created_at: datetime = Field(
        default_factory=lambda:
            datetime.now(
                timezone.utc
            )
    )

    updated_at: datetime = Field(
        default_factory=lambda:
            datetime.now(
                timezone.utc
            )
    )
