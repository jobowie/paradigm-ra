import sqlite3
from uuid import UUID

from ra_platform.organizations.models import (
    Organization,
    OrganizationStatus,
    OrganizationType,
)
from ra_platform.engagements.models import (
    Engagement,
    EngagementSource,
    EngagementStatus,
)


class SQLiteOrganizationRepository:
    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self.connection = connection

    def add(
        self,
        organization: Organization,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO organizations (
                id,
                name,
                type,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(organization.id),
                organization.name,
                organization.type.value,
                organization.status.value,
                organization.created_at.isoformat(),
                organization.updated_at.isoformat(),
            ),
        )

    def get(
        self,
        organization_id: UUID,
    ) -> Organization | None:
        row = self.connection.execute(
            """
            SELECT *
            FROM organizations
            WHERE id = ?
            """,
            (str(organization_id),),
        ).fetchone()

        if row is None:
            return None

        return Organization(
            id=UUID(row["id"]),
            name=row["name"],
            type=OrganizationType(row["type"]),
            status=OrganizationStatus(row["status"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


class SQLiteEngagementRepository:
    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self.connection = connection

    def add(
        self,
        engagement: Engagement,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO engagements (
                id,
                client_organization_id,
                owner_organization_id,
                name,
                service_type,
                source,
                status,
                source_opportunity_id,
                discovery_session_id,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(engagement.id),
                str(engagement.client_organization_id),
                str(engagement.owner_organization_id),
                engagement.name,
                engagement.service_type,
                engagement.source.value,
                engagement.status.value,
                (
                    str(engagement.source_opportunity_id)
                    if engagement.source_opportunity_id
                    else None
                ),
                (
                    str(engagement.discovery_session_id)
                    if engagement.discovery_session_id
                    else None
                ),
                engagement.created_at.isoformat(),
                engagement.updated_at.isoformat(),
            ),
        )

    def get(
        self,
        engagement_id: UUID,
    ) -> Engagement | None:
        row = self.connection.execute(
            """
            SELECT *
            FROM engagements
            WHERE id = ?
            """,
            (str(engagement_id),),
        ).fetchone()

        if row is None:
            return None

        return Engagement(
            id=UUID(row["id"]),
            client_organization_id=UUID(
                row["client_organization_id"]
            ),
            owner_organization_id=UUID(
                row["owner_organization_id"]
            ),
            name=row["name"],
            service_type=row["service_type"],
            source=EngagementSource(row["source"]),
            status=EngagementStatus(row["status"]),
            source_opportunity_id=(
                UUID(row["source_opportunity_id"])
                if row["source_opportunity_id"]
                else None
            ),
            discovery_session_id=(
                UUID(row["discovery_session_id"])
                if row["discovery_session_id"]
                else None
            ),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
