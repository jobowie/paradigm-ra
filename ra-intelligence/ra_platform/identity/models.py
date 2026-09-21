from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class UserStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"


class MembershipRole(str, Enum):
    PARADIGM_RA_ADMIN = "paradigm_ra_admin"
    PARADIGM_RA_EXECUTIVE = "paradigm_ra_executive"
    CLIENT_ADMIN = "client_admin"
    PARTNER_ADMIN = "partner_admin"


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    email: str = Field(min_length=3)
    display_name: str = Field(min_length=1)

    password_hash: str = Field(
        min_length=1,
        repr=False,
    )

    status: UserStatus = UserStatus.ACTIVE

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


class OrganizationMembership(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    user_id: UUID
    organization_id: UUID

    role: MembershipRole

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )


class AuthSession(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    user_id: UUID

    token_hash: str = Field(
        min_length=1,
        repr=False,
    )

    expires_at: datetime

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    revoked_at: datetime | None = None


class AuditEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    actor_user_id: UUID | None = None
    organization_id: UUID | None = None

    action: str = Field(min_length=1)

    resource_type: str = Field(
        min_length=1
    )

    resource_id: UUID | None = None

    metadata_json: str | None = None

    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )
