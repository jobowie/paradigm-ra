import os
import secrets
import sqlite3

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
)
from pydantic import BaseModel, Field

from ra_platform.api.dependencies import (
    get_database_connection,
)
from ra_platform.billing.models import (
    Quote,
    QuoteLine,
    QuoteStatus,
)
from ra_platform.billing.service import (
    refresh_quote,
    send_quote,
)
from ra_platform.engagements.models import (
    Engagement,
    EngagementSource,
    EngagementStatus,
)
from ra_platform.organizations.models import (
    Organization,
    OrganizationStatus,
    OrganizationType,
)
from ra_platform.persistence.sqlite_repositories import (
    SQLiteEngagementRepository,
    SQLiteOrganizationRepository,
    SQLiteQuoteRepository,
)
from ra_platform.security.tokens import (
    generate_public_token,
    hash_public_token,
)


router = APIRouter(
    prefix="/admin/quotes",
    tags=["admin-quotes"],
)


class AdminQuoteCreateRequest(BaseModel):
    client_name: str = Field(min_length=1)
    client_email: str | None = None

    project_name: str = Field(min_length=1)
    service_type: str = "web_software_solutions"

    scope_items: list[str]

    deposit_amount: Decimal = Field(gt=0)
    deployment_amount: Decimal = Field(gt=0)

    terms: str
    expiration_date: date


class AdminQuoteCreateResponse(BaseModel):
    quote_number: str
    status: str
    total: str

    client_name: str
    project_name: str

    public_url: str


def require_admin_key(
    x_ra_admin_key: str | None = Header(
        default=None
    ),
) -> None:
    expected = os.getenv(
        "RA_ADMIN_API_KEY"
    )

    if not expected:
        raise HTTPException(
            status_code=503,
            detail=(
                "Admin API key is not configured."
            ),
        )

    if (
        not x_ra_admin_key
        or not secrets.compare_digest(
            x_ra_admin_key,
            expected,
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized.",
        )


@router.post("/verify")
def verify_admin_access(
    _: None = Depends(require_admin_key),
):
    return {
        "authorized": True,
    }



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
            name.strip(),
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

    now = datetime.now(timezone.utc)

    organization = Organization(
        id=uuid4(),
        name=name.strip(),
        type=organization_type,
        status=OrganizationStatus.ACTIVE,
        created_at=now,
        updated_at=now,
    )

    repository.add(
        organization
    )

    return organization


def get_or_create_engagement(
    connection: sqlite3.Connection,
    *,
    client_organization_id: UUID,
    owner_organization_id: UUID,
    project_name: str,
    service_type: str,
) -> Engagement:
    row = connection.execute(
        """
        SELECT id
        FROM engagements
        WHERE client_organization_id = ?
          AND lower(name) = lower(?)
        LIMIT 1
        """,
        (
            str(client_organization_id),
            project_name.strip(),
        ),
    ).fetchone()

    repository = (
        SQLiteEngagementRepository(
            connection
        )
    )

    if row is not None:
        engagement = repository.get(
            UUID(row["id"])
        )

        if engagement is None:
            raise RuntimeError(
                "Engagement lookup failed."
            )

        return engagement

    now = datetime.now(timezone.utc)

    engagement = Engagement(
        id=uuid4(),
        client_organization_id=(
            client_organization_id
        ),
        owner_organization_id=(
            owner_organization_id
        ),
        name=project_name.strip(),
        service_type=service_type,
        source=EngagementSource.DIRECT,
        status=EngagementStatus.PROPOSED,
        source_opportunity_id=None,
        discovery_session_id=None,
        created_at=now,
        updated_at=now,
    )

    repository.add(
        engagement
    )

    return engagement


def next_quote_number(
    connection: sqlite3.Connection,
) -> str:
    current_year = date.today().year

    row = connection.execute(
        """
        SELECT COUNT(*) AS quote_count
        FROM quotes
        """
    ).fetchone()

    sequence = int(
        row["quote_count"]
    ) + 1

    return (
        f"RA-Q-{current_year}-"
        f"{sequence:03d}"
    )


@router.post(
    "",
    response_model=(
        AdminQuoteCreateResponse
    ),
    dependencies=[
        Depends(require_admin_key)
    ],
)
def create_admin_quote(
    request: AdminQuoteCreateRequest,
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    try:
        paradigm_ra = (
            get_or_create_organization(
                connection,
                name="Paradigm Ra",
                organization_type=(
                    OrganizationType.PARADIGM_RA
                ),
            )
        )

        client = (
            get_or_create_organization(
                connection,
                name=request.client_name,
                organization_type=(
                    OrganizationType.CLIENT
                ),
            )
        )

        engagement = (
            get_or_create_engagement(
                connection,
                client_organization_id=(
                    client.id
                ),
                owner_organization_id=(
                    paradigm_ra.id
                ),
                project_name=(
                    request.project_name
                ),
                service_type=(
                    request.service_type
                ),
            )
        )

        now = datetime.now(
            timezone.utc
        )

        scope = "\n".join(
            f"• {item.strip()}"
            for item in request.scope_items
            if item.strip()
        )

        quote = Quote(
            id=uuid4(),
            client_organization_id=(
                client.id
            ),
            engagement_id=(
                engagement.id
            ),
            quote_number=(
                next_quote_number(
                    connection
                )
            ),
            status=QuoteStatus.DRAFT,
            issue_date=date.today(),
            expiration_date=(
                request.expiration_date
            ),
            bill_to_name=(
                request.client_name
            ),
            bill_to_email=(
                request.client_email
            ),
            bill_to_address=None,
            line_items=[
                QuoteLine(
                    id=uuid4(),
                    description=(
                        "Project Deposit"
                    ),
                    quantity=Decimal("1"),
                    unit_rate=(
                        request.deposit_amount
                    ),
                    amount=Decimal("0"),
                ),
                QuoteLine(
                    id=uuid4(),
                    description=(
                        "Deployment / "
                        "Launch Balance"
                    ),
                    quantity=Decimal("1"),
                    unit_rate=(
                        request.deployment_amount
                    ),
                    amount=Decimal("0"),
                ),
            ],
            subtotal=Decimal("0"),
            tax_amount=Decimal("0"),
            total=Decimal("0"),
            notes=scope,
            terms=request.terms,
            sent_at=None,
            accepted_at=None,
            declined_at=None,
            created_at=now,
            updated_at=now,
        )

        refresh_quote(
            quote
        )

        send_quote(
            quote
        )

        repository = (
            SQLiteQuoteRepository(
                connection
            )
        )

        repository.add(
            quote
        )

        token = (
            generate_public_token()
        )

        repository.assign_public_token_hash(
            quote_id=quote.id,
            public_token_hash=(
                hash_public_token(
                    token
                )
            ),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    public_app_url = os.getenv(
        "RA_PUBLIC_APP_URL",
        "http://localhost:3000",
    ).rstrip("/")

    return AdminQuoteCreateResponse(
        quote_number=(
            quote.quote_number
        ),
        status=quote.status.value,
        total=str(quote.total),
        client_name=request.client_name,
        project_name=(
            request.project_name
        ),
        public_url=(
            f"{public_app_url}"
            f"/quote/{token}"
        ),
    )
