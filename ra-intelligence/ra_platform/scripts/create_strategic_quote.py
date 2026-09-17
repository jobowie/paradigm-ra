from datetime import date
from decimal import Decimal
from uuid import UUID

from ra_platform.billing.models import (
    Quote,
    QuoteLine,
)
from ra_platform.billing.service import (
    refresh_quote,
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
    SQLiteEngagementRepository,
    SQLiteOrganizationRepository,
    SQLiteQuoteRepository,
)


PARADIGM_RA_ID = UUID(
    "00000000-0000-4000-8000-000000000001"
)

STRATEGIC_ID = UUID(
    "00000000-0000-4000-8000-000000000002"
)

WEBSITE_ENGAGEMENT_ID = UUID(
    "00000000-0000-4000-8000-000000000003"
)

STRATEGIC_QUOTE_ID = UUID(
    "00000000-0000-4000-8000-000000000004"
)


def main():
    connection = create_connection()

    initialize_database(connection)

    organizations = SQLiteOrganizationRepository(
        connection
    )

    engagements = SQLiteEngagementRepository(
        connection
    )

    quotes = SQLiteQuoteRepository(
        connection
    )

    existing = connection.execute(
        """
        SELECT id
        FROM quotes
        WHERE id = ?
        """,
        (str(STRATEGIC_QUOTE_ID),),
    ).fetchone()

    if existing is not None:
        print(
            "Strategic Crime Prevention "
            "local quote already exists."
        )

        print(
            f"Quote ID: {STRATEGIC_QUOTE_ID}"
        )

        print(
            f"Client Organization ID: {STRATEGIC_ID}"
        )

        connection.close()
        return

    paradigm_ra = Organization(
        id=PARADIGM_RA_ID,
        name="Paradigm Ra",
        type=OrganizationType.PARADIGM_RA,
    )

    strategic = Organization(
        id=STRATEGIC_ID,
        name="Strategic Crime Prevention",
        type=OrganizationType.CLIENT,
    )

    organizations.add(paradigm_ra)
    organizations.add(strategic)

    website_engagement = Engagement(
        id=WEBSITE_ENGAGEMENT_ID,
        client_organization_id=strategic.id,
        owner_organization_id=paradigm_ra.id,
        name="Website Design & Development",
        service_type="website_design_development",
        source=EngagementSource.DIRECT,
        status=EngagementStatus.ACTIVE,
    )

    engagements.add(
        website_engagement
    )

    quote = Quote(
        id=STRATEGIC_QUOTE_ID,
        client_organization_id=strategic.id,
        engagement_id=website_engagement.id,
        quote_number="RA-Q-2026-001",
        issue_date=date(2026, 9, 16),
        expiration_date=date(2026, 9, 30),
        bill_to_name="Strategic Crime Prevention",
        line_items=[
            QuoteLine(
                description=(
                    "Website Design & Development"
                ),
                quantity=Decimal("1"),
                unit_rate=Decimal("750.00"),
            )
        ],
        notes=(
            "Production website based on the "
            "client-approved design concept."
        ),
        terms=(
            "50% deposit on acceptance. "
            "Remaining 50% due before launch. "
            "Two revision rounds included. "
            "Ongoing support is separate."
        ),
    )

    refresh_quote(quote)

    quotes.add(quote)

    connection.commit()
    connection.close()

    print("Local quote created.")
    print(
        f"Quote ID: {STRATEGIC_QUOTE_ID}"
    )
    print(
        f"Client Organization ID: {STRATEGIC_ID}"
    )


if __name__ == "__main__":
    main()