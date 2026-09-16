from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EngagementSource(str, Enum):
    DIRECT = "direct"
    CONTRACT_CONVERSION = "contract_conversion"
    PARTNER = "partner"
    EXISTING_CLIENT = "existing_client"
    REFERRAL = "referral"
    WEBSITE = "website"
    EVENT = "event"
    OTHER = "other"


class EngagementStatus(str, Enum):
    PENDING_OFFER = "pending_offer"
    PROPOSED = "proposed"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Engagement(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    client_organization_id: UUID
    owner_organization_id: UUID

    name: str = Field(min_length=1)
    service_type: str = Field(min_length=1)

    source: EngagementSource

    status: EngagementStatus = EngagementStatus.PROPOSED

    source_opportunity_id: UUID | None = None
    discovery_session_id: UUID | None = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
