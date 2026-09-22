from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class OrganizationCompanyProfile(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    organization_id: UUID

    business_type: str | None = None
    industry: str | None = None
    website: str | None = None
    phone: str | None = None
    company_size: str | None = None

    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state_region: str | None = None
    postal_code: str | None = None
    country: str = "US"

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )


class OrganizationContact(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    organization_id: UUID

    name: str = Field(min_length=1)

    title: str | None = None
    email: str | None = None
    phone: str | None = None

    contact_type: str | None = None

    is_primary: bool = False

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )
