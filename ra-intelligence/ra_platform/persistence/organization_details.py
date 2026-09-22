import sqlite3

from uuid import UUID

from ra_platform.organizations.company_profile import (
    OrganizationCompanyProfile,
    OrganizationContact,
)


class SQLiteOrganizationCompanyProfileRepository:
    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self.connection = connection

    def get_for_organization(
        self,
        organization_id: UUID,
    ) -> OrganizationCompanyProfile | None:
        row = self.connection.execute(
            """
            SELECT *
            FROM organization_company_profiles
            WHERE organization_id = ?
            """,
            (str(organization_id),),
        ).fetchone()

        if row is None:
            return None

        return self._hydrate(row)

    def upsert(
        self,
        profile: OrganizationCompanyProfile,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO organization_company_profiles (
                id,
                organization_id,
                business_type,
                industry,
                website,
                phone,
                company_size,
                address_line1,
                address_line2,
                city,
                state_region,
                postal_code,
                country,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(organization_id)
            DO UPDATE SET
                business_type = excluded.business_type,
                industry = excluded.industry,
                website = excluded.website,
                phone = excluded.phone,
                company_size = excluded.company_size,
                address_line1 = excluded.address_line1,
                address_line2 = excluded.address_line2,
                city = excluded.city,
                state_region = excluded.state_region,
                postal_code = excluded.postal_code,
                country = excluded.country,
                updated_at = excluded.updated_at
            """,
            (
                str(profile.id),
                str(profile.organization_id),
                profile.business_type,
                profile.industry,
                profile.website,
                profile.phone,
                profile.company_size,
                profile.address_line1,
                profile.address_line2,
                profile.city,
                profile.state_region,
                profile.postal_code,
                profile.country,
                profile.created_at.isoformat(),
                profile.updated_at.isoformat(),
            ),
        )

    def _hydrate(
        self,
        row: sqlite3.Row,
    ) -> OrganizationCompanyProfile:
        return OrganizationCompanyProfile(
            id=UUID(row["id"]),
            organization_id=UUID(
                row["organization_id"]
            ),
            business_type=row["business_type"],
            industry=row["industry"],
            website=row["website"],
            phone=row["phone"],
            company_size=row["company_size"],
            address_line1=row["address_line1"],
            address_line2=row["address_line2"],
            city=row["city"],
            state_region=row["state_region"],
            postal_code=row["postal_code"],
            country=row["country"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


class SQLiteOrganizationContactRepository:
    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self.connection = connection

    def add(
        self,
        contact: OrganizationContact,
    ) -> None:
        if contact.is_primary:
            self._clear_primary(
                contact.organization_id
            )

        self.connection.execute(
            """
            INSERT INTO organization_contacts (
                id,
                organization_id,
                name,
                title,
                email,
                phone,
                contact_type,
                is_primary,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(contact.id),
                str(contact.organization_id),
                contact.name,
                contact.title,
                contact.email,
                contact.phone,
                contact.contact_type,
                int(contact.is_primary),
                contact.created_at.isoformat(),
                contact.updated_at.isoformat(),
            ),
        )

    def update(
        self,
        contact: OrganizationContact,
    ) -> None:
        if contact.is_primary:
            self._clear_primary(
                contact.organization_id
            )

        self.connection.execute(
            """
            UPDATE organization_contacts
            SET
                name = ?,
                title = ?,
                email = ?,
                phone = ?,
                contact_type = ?,
                is_primary = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                contact.name,
                contact.title,
                contact.email,
                contact.phone,
                contact.contact_type,
                int(contact.is_primary),
                contact.updated_at.isoformat(),
                str(contact.id),
            ),
        )

    def get(
        self,
        contact_id: UUID,
    ) -> OrganizationContact | None:
        row = self.connection.execute(
            """
            SELECT *
            FROM organization_contacts
            WHERE id = ?
            """,
            (str(contact_id),),
        ).fetchone()

        if row is None:
            return None

        return self._hydrate(row)

    def list_for_organization(
        self,
        organization_id: UUID,
    ) -> list[OrganizationContact]:
        rows = self.connection.execute(
            """
            SELECT *
            FROM organization_contacts
            WHERE organization_id = ?
            ORDER BY
                is_primary DESC,
                lower(name)
            """,
            (str(organization_id),),
        ).fetchall()

        return [
            self._hydrate(row)
            for row in rows
        ]

    def _clear_primary(
        self,
        organization_id: UUID,
    ) -> None:
        self.connection.execute(
            """
            UPDATE organization_contacts
            SET is_primary = 0
            WHERE organization_id = ?
            """,
            (str(organization_id),),
        )

    def _hydrate(
        self,
        row: sqlite3.Row,
    ) -> OrganizationContact:
        return OrganizationContact(
            id=UUID(row["id"]),
            organization_id=UUID(
                row["organization_id"]
            ),
            name=row["name"],
            title=row["title"],
            email=row["email"],
            phone=row["phone"],
            contact_type=row["contact_type"],
            is_primary=bool(
                row["is_primary"]
            ),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
