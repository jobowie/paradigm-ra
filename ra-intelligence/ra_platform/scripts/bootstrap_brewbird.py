import sqlite3

from datetime import date
from decimal import Decimal
from uuid import UUID

from ra_platform.api.dependencies import (
    get_database_path,
)
from ra_platform.billing.models import (
    BillingCadence,
    BillingType,
    EngagementBillingTerms,
)
from ra_platform.engagements.models import (
    Engagement,
    EngagementSource,
    EngagementStatus,
)
from ra_platform.organizations.models import (
    Organization,
    OrganizationType,
)
from ra_platform.persistence.sqlite import (
    create_connection,
    initialize_database,
)
from ra_platform.persistence.sqlite_repositories import (
    SQLiteEngagementBillingTermsRepository,
    SQLiteEngagementRepository,
    SQLiteOrganizationRepository,
)


def get_or_create_organization(
    connection: sqlite3.Connection,
    *,
    name: str,
    organization_type: OrganizationType,
) -> Organization:
    row = connection.execute(
        """
        SELECT id
        FROM organizations
        WHERE lower(name) = lower(?)
          AND type = ?
        LIMIT 1
        """,
        (
            name,
            organization_type.value,
        ),
    ).fetchone()

    repository = (
        SQLiteOrganizationRepository(
            connection
        )
    )

    if row is not None:
        organization = repository.get(
            UUID(row["id"])
        )

        if organization is None:
            raise RuntimeError(
                "Organization lookup failed."
            )

        return organization

    organization = Organization(
        name=name,
        type=organization_type,
    )

    repository.add(
        organization
    )

    return organization


def main() -> None:
    connection = create_connection(
        get_database_path()
    )

    initialize_database(
        connection
    )

    try:
        paradigm_ra = (
            get_or_create_organization(
                connection,
                name="Paradigm Ra",
                organization_type=(
                    OrganizationType
                    .PARADIGM_RA
                ),
            )
        )

        brewbird = (
            get_or_create_organization(
                connection,
                name="BrewBird Coffee",
                organization_type=(
                    OrganizationType.CLIENT
                ),
            )
        )

        engagement_row = (
            connection.execute(
                """
                SELECT id
                FROM engagements
                WHERE client_organization_id = ?
                  AND lower(name) = lower(?)
                LIMIT 1
                """,
                (
                    str(brewbird.id),
                    "Bookkeeping",
                ),
            ).fetchone()
        )

        engagements = (
            SQLiteEngagementRepository(
                connection
            )
        )

        if engagement_row:
            bookkeeping = engagements.get(
                UUID(
                    engagement_row["id"]
                )
            )

            if bookkeeping is None:
                raise RuntimeError(
                    "Engagement lookup failed."
                )

        else:
            bookkeeping = Engagement(
                client_organization_id=(
                    brewbird.id
                ),
                owner_organization_id=(
                    paradigm_ra.id
                ),
                name="Bookkeeping",
                service_type="bookkeeping",
                source=(
                    EngagementSource
                    .CONTRACT_CONVERSION
                ),
                status=(
                    EngagementStatus.ACTIVE
                ),
            )

            engagements.add(
                bookkeeping
            )

        terms_row = connection.execute(
            """
            SELECT id
            FROM engagement_billing_terms
            WHERE engagement_id = ?
              AND effective_to IS NULL
            LIMIT 1
            """,
            (str(bookkeeping.id),),
        ).fetchone()

        if terms_row is None:
            terms = (
                EngagementBillingTerms(
                    engagement_id=(
                        bookkeeping.id
                    ),
                    billing_type=(
                        BillingType.HOURLY
                    ),
                    billing_cadence=(
                        BillingCadence.WEEKLY
                    ),
                    hourly_rate=Decimal(
                        "70.00"
                    ),
                    expected_hours_min=(
                        Decimal("15")
                    ),
                    expected_hours_max=(
                        Decimal("30")
                    ),
                    payment_terms_days=30,
                    effective_from=date(
                        2026,
                        9,
                        15,
                    ),
                )
            )

            (
                SQLiteEngagementBillingTermsRepository(
                    connection
                ).add(terms)
            )

        connection.commit()

        print(
            "BrewBird production context ready:"
        )
        print(
            f"  organization: {brewbird.id}"
        )
        print(
            f"  engagement: {bookkeeping.id}"
        )

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()
