from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class OrganizationType(str, Enum):
    PARADIGM_RA = "paradigm_ra"
    CLIENT = "client"
    PARTNER = "partner"


class OrganizationStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Organization(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    name: str = Field(min_length=1)

    type: OrganizationType

    status: OrganizationStatus = OrganizationStatus.ACTIVE

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
