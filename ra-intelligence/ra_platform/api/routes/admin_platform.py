import sqlite3

from datetime import date
from decimal import Decimal

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from pydantic import (
    BaseModel,
    Field,
)

from ra_platform.api.auth import (
    get_current_principal,
)
from ra_platform.billing.models import (
    Invoice,
    TimeEntry,
    TimeEntryFriction,
    TimeEntryWorkstream,
)
from ra_platform.billing.numbering import (
    next_invoice_number,
)
from ra_platform.billing.service import (
    approve_time_entry,
    create_invoice_from_time_entries,
)
from ra_platform.api.dependencies import (
    get_database_connection,
)
from ra_platform.identity.authorization import (
    AuthorizationError,
    Permission,
    authorize,
)
from ra_platform.identity.service import (
    AuthenticatedPrincipal,
)
from ra_platform.organizations.models import (
    OrganizationType,
)
from ra_platform.persistence.sqlite_repositories import (
    SQLiteBillingUnitOfWork,
    SQLiteEngagementBillingTermsRepository,
    SQLiteEngagementRepository,
    SQLiteInvoiceRepository,
    SQLiteOrganizationRepository,
    SQLiteTimeEntryRepository,
)


router = APIRouter(
    prefix="/admin",
    tags=["admin-platform"],
)


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    type: str
    status: str


class EngagementResponse(BaseModel):
    id: UUID
    client_organization_id: UUID
    owner_organization_id: UUID

    name: str
    service_type: str
    source: str
    status: str


class BillingTermsResponse(BaseModel):
    id: UUID
    engagement_id: UUID

    billing_type: str
    billing_cadence: str

    hourly_rate: str | None

    expected_hours_min: str | None
    expected_hours_max: str | None

    payment_terms_days: int

    effective_from: str
    effective_to: str | None


def require_permission(
    *,
    principal: AuthenticatedPrincipal,
    permission: Permission,
    organization_id: UUID | None = None,
) -> None:
    try:
        authorize(
            principal=principal,
            permission=permission,
            organization_id=organization_id,
        )
    except AuthorizationError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        ) from exc


@router.get(
    "/organizations",
    response_model=list[
        OrganizationResponse
    ],
)
def list_client_organizations(
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    require_permission(
        principal=principal,
        permission=(
            Permission.VIEW_ORGANIZATION
        ),
    )

    repository = (
        SQLiteOrganizationRepository(
            connection
        )
    )

    organizations = [
        organization
        for organization
        in repository.list_all()
        if (
            organization.type
            == OrganizationType.CLIENT
        )
    ]

    return [
        OrganizationResponse(
            id=organization.id,
            name=organization.name,
            type=organization.type.value,
            status=(
                organization.status.value
            ),
        )
        for organization
        in organizations
    ]


@router.get(
    "/organizations/"
    "{organization_id}/engagements",
    response_model=list[
        EngagementResponse
    ],
)
def list_organization_engagements(
    organization_id: UUID,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    organizations = (
        SQLiteOrganizationRepository(
            connection
        )
    )

    organization = organizations.get(
        organization_id
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found.",
        )

    require_permission(
        principal=principal,
        permission=(
            Permission.VIEW_ENGAGEMENT
        ),
        organization_id=organization.id,
    )

    engagements = (
        SQLiteEngagementRepository(
            connection
        ).list_for_client(
            organization.id
        )
    )

    return [
        EngagementResponse(
            id=engagement.id,
            client_organization_id=(
                engagement.client_organization_id
            ),
            owner_organization_id=(
                engagement.owner_organization_id
            ),
            name=engagement.name,
            service_type=(
                engagement.service_type
            ),
            source=engagement.source.value,
            status=engagement.status.value,
        )
        for engagement
        in engagements
    ]


@router.get(
    "/engagements/"
    "{engagement_id}/billing-terms",
    response_model=list[
        BillingTermsResponse
    ],
)
def list_engagement_billing_terms(
    engagement_id: UUID,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    engagements = (
        SQLiteEngagementRepository(
            connection
        )
    )

    engagement = engagements.get(
        engagement_id
    )

    if engagement is None:
        raise HTTPException(
            status_code=404,
            detail="Engagement not found.",
        )

    require_permission(
        principal=principal,
        permission=Permission.VIEW_BILLING,
        organization_id=(
            engagement.client_organization_id
        ),
    )

    terms = (
        SQLiteEngagementBillingTermsRepository(
            connection
        ).list_for_engagement(
            engagement.id
        )
    )

    return [
        BillingTermsResponse(
            id=item.id,
            engagement_id=(
                item.engagement_id
            ),
            billing_type=(
                item.billing_type.value
            ),
            billing_cadence=(
                item.billing_cadence.value
            ),
            hourly_rate=(
                str(item.hourly_rate)
                if item.hourly_rate
                is not None
                else None
            ),
            expected_hours_min=(
                str(
                    item.expected_hours_min
                )
                if item.expected_hours_min
                is not None
                else None
            ),
            expected_hours_max=(
                str(
                    item.expected_hours_max
                )
                if item.expected_hours_max
                is not None
                else None
            ),
            payment_terms_days=(
                item.payment_terms_days
            ),
            effective_from=(
                item.effective_from
                .isoformat()
            ),
            effective_to=(
                item.effective_to
                .isoformat()
                if item.effective_to
                else None
            ),
        )
        for item in terms
    ]


class CreateTimeEntryRequest(BaseModel):
    work_date: date

    description: str = Field(
        min_length=1
    )

    hours: Decimal = Field(
        gt=0
    )

    workstream: (
        TimeEntryWorkstream
        | None
    ) = None

    friction: (
        TimeEntryFriction
        | None
    ) = None

    operational_note: str | None = None


class TimeEntryResponse(BaseModel):
    id: UUID
    engagement_id: UUID

    work_date: str
    description: str
    hours: str

    workstream: str | None
    friction: str | None
    operational_note: str | None

    status: str

    invoice_id: UUID | None


class GenerateInvoiceRequest(BaseModel):
    issue_date: date | None = None

    bill_to_email: str | None = None
    notes: str | None = None


class InvoiceLineResponse(BaseModel):
    id: UUID
    engagement_id: UUID

    description: str

    quantity: str
    unit_rate: str
    amount: str


class InvoiceResponse(BaseModel):
    id: UUID

    invoice_number: str
    status: str

    issue_date: str | None
    due_date: str | None
    sent_at: str | None

    bill_to_name: str
    bill_to_email: str | None

    subtotal: str
    tax_amount: str
    total: str

    amount_paid: str
    balance_due: str

    line_items: list[
        InvoiceLineResponse
    ]


def build_time_entry_response(
    entry: TimeEntry,
) -> TimeEntryResponse:
    return TimeEntryResponse(
        id=entry.id,
        engagement_id=(
            entry.engagement_id
        ),
        work_date=(
            entry.work_date.isoformat()
        ),
        description=entry.description,
        hours=str(entry.hours),
        workstream=(
            entry.workstream.value
            if entry.workstream
            else None
        ),
        friction=(
            entry.friction.value
            if entry.friction
            else None
        ),
        operational_note=(
            entry.operational_note
        ),
        status=entry.status.value,
        invoice_id=entry.invoice_id,
    )


def build_invoice_response(
    invoice: Invoice,
) -> InvoiceResponse:
    return InvoiceResponse(
        id=invoice.id,
        invoice_number=(
            invoice.invoice_number
        ),
        status=invoice.status.value,
        issue_date=(
            invoice.issue_date.isoformat()
            if invoice.issue_date
            else None
        ),
        due_date=(
            invoice.due_date.isoformat()
            if invoice.due_date
            else None
        ),
        sent_at=(
            invoice.sent_at.isoformat()
            if invoice.sent_at
            else None
        ),
        bill_to_name=(
            invoice.bill_to_name
        ),
        bill_to_email=(
            invoice.bill_to_email
        ),
        subtotal=str(invoice.subtotal),
        tax_amount=str(
            invoice.tax_amount
        ),
        total=str(invoice.total),
        amount_paid=str(
            invoice.amount_paid
        ),
        balance_due=str(
            invoice.balance_due
        ),
        line_items=[
            InvoiceLineResponse(
                id=line.id,
                engagement_id=(
                    line.engagement_id
                ),
                description=(
                    line.description
                ),
                quantity=str(
                    line.quantity
                ),
                unit_rate=str(
                    line.unit_rate
                ),
                amount=str(
                    line.amount
                ),
            )
            for line
            in invoice.line_items
        ],
    )


def get_engagement_or_404(
    *,
    engagement_id: UUID,
    connection: sqlite3.Connection,
):
    engagement = (
        SQLiteEngagementRepository(
            connection
        ).get(engagement_id)
    )

    if engagement is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Engagement not found."
            ),
        )

    return engagement


@router.get(
    "/engagements/"
    "{engagement_id}/time-entries",
    response_model=list[
        TimeEntryResponse
    ],
)
def list_time_entries(
    engagement_id: UUID,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    engagement = get_engagement_or_404(
        engagement_id=engagement_id,
        connection=connection,
    )

    require_permission(
        principal=principal,
        permission=Permission.VIEW_BILLING,
        organization_id=(
            engagement.client_organization_id
        ),
    )

    entries = (
        SQLiteTimeEntryRepository(
            connection
        ).list_for_engagement(
            engagement.id
        )
    )

    return [
        build_time_entry_response(
            entry
        )
        for entry in entries
    ]


@router.post(
    "/engagements/"
    "{engagement_id}/time-entries",
    response_model=TimeEntryResponse,
)
def create_time_entry(
    engagement_id: UUID,
    body: CreateTimeEntryRequest,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    engagement = get_engagement_or_404(
        engagement_id=engagement_id,
        connection=connection,
    )

    require_permission(
        principal=principal,
        permission=(
            Permission.CREATE_INVOICE
        ),
        organization_id=(
            engagement.client_organization_id
        ),
    )

    entry = TimeEntry(
        engagement_id=engagement.id,
        work_date=body.work_date,
        description=(
            body.description.strip()
        ),
        hours=body.hours,
        workstream=body.workstream,
        friction=body.friction,
        operational_note=(
            body.operational_note.strip()
            if (
                body.operational_note
                and body.operational_note.strip()
            )
            else None
        ),
    )

    repository = (
        SQLiteTimeEntryRepository(
            connection
        )
    )

    repository.add_many(
        [entry]
    )

    connection.commit()

    return build_time_entry_response(
        entry
    )


@router.post(
    "/time-entries/"
    "{time_entry_id}/approve",
    response_model=TimeEntryResponse,
)
def approve_admin_time_entry(
    time_entry_id: UUID,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    repository = (
        SQLiteTimeEntryRepository(
            connection
        )
    )

    entry = repository.get(
        time_entry_id
    )

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Time entry not found."
            ),
        )

    engagement = get_engagement_or_404(
        engagement_id=(
            entry.engagement_id
        ),
        connection=connection,
    )

    require_permission(
        principal=principal,
        permission=(
            Permission.CREATE_INVOICE
        ),
        organization_id=(
            engagement.client_organization_id
        ),
    )

    try:
        approve_time_entry(
            entry
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    repository.update_many(
        [entry]
    )

    connection.commit()

    return build_time_entry_response(
        entry
    )


@router.get(
    "/engagements/"
    "{engagement_id}/invoices",
    response_model=list[
        InvoiceResponse
    ],
)
def list_engagement_invoices(
    engagement_id: UUID,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    engagement = get_engagement_or_404(
        engagement_id=engagement_id,
        connection=connection,
    )

    require_permission(
        principal=principal,
        permission=Permission.VIEW_BILLING,
        organization_id=(
            engagement.client_organization_id
        ),
    )

    invoices = (
        SQLiteInvoiceRepository(
            connection
        ).list_for_engagement(
            engagement.id
        )
    )

    return [
        build_invoice_response(
            invoice
        )
        for invoice in invoices
    ]


@router.post(
    "/engagements/"
    "{engagement_id}/invoices/generate",
    response_model=InvoiceResponse,
)
def generate_engagement_invoice(
    engagement_id: UUID,
    body: GenerateInvoiceRequest,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    engagement = get_engagement_or_404(
        engagement_id=engagement_id,
        connection=connection,
    )

    require_permission(
        principal=principal,
        permission=(
            Permission.CREATE_INVOICE
        ),
        organization_id=(
            engagement.client_organization_id
        ),
    )

    organization = (
        SQLiteOrganizationRepository(
            connection
        ).get(
            engagement.client_organization_id
        )
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Client organization "
                "not found."
            ),
        )

    time_entries = (
        SQLiteTimeEntryRepository(
            connection
        ).list_for_engagement(
            engagement.id
        )
    )

    billing_terms = (
        SQLiteEngagementBillingTermsRepository(
            connection
        ).list_for_engagement(
            engagement.id
        )
    )

    invoice_date = (
        body.issue_date
        or date.today()
    )

    effective_terms = [
        terms
        for terms in billing_terms
        if (
            terms.effective_from
            <= invoice_date
            and (
                terms.effective_to
                is None
                or invoice_date
                <= terms.effective_to
            )
        )
    ]

    payment_terms_days = 30

    if effective_terms:
        current_terms = max(
            effective_terms,
            key=lambda terms:
                terms.effective_from,
        )

        payment_terms_days = (
            current_terms
            .payment_terms_days
        )

    try:
        invoice = (
            create_invoice_from_time_entries(
                uow=SQLiteBillingUnitOfWork(
                    connection
                ),
                client_organization_id=(
                    engagement
                    .client_organization_id
                ),
                invoice_number=(
                    next_invoice_number(
                        connection,
                        invoice_date=(
                            invoice_date
                        ),
                    )
                ),
                time_entries=time_entries,
                billing_terms=(
                    billing_terms
                ),
                bill_to_name=(
                    organization.name
                ),
                bill_to_email=(
                    body.bill_to_email
                ),
                issue_date=invoice_date,
                payment_terms_days=(
                    payment_terms_days
                ),
                notes=body.notes,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    return build_invoice_response(
        invoice
    )


# ---------------------------------------------------------
# Invoice delivery
# ---------------------------------------------------------

import hashlib
import json
import os

from ra_platform.billing.invoice_pdf import (
    build_invoice_pdf,
)
from ra_platform.billing.models import (
    InvoiceStatus,
)
from ra_platform.billing.service import (
    send_invoice as mark_invoice_sent,
)
from ra_platform.identity.models import (
    AuditEvent,
)
from ra_platform.notifications.resend import (
    ResendDeliveryError,
    send_pdf_email,
)
from ra_platform.persistence.sqlite_repositories import (
    SQLiteAuditEventRepository,
    SQLiteUserRepository,
)


class SendInvoiceResponse(BaseModel):
    invoice: InvoiceResponse
    provider_message_id: str
    pdf_sha256: str


@router.post(
    "/invoices/{invoice_id}/send",
    response_model=SendInvoiceResponse,
)
def send_admin_invoice(
    invoice_id: UUID,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    invoices = SQLiteInvoiceRepository(
        connection
    )

    invoice = invoices.get(
        invoice_id
    )

    if invoice is None:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found.",
        )

    require_permission(
        principal=principal,
        permission=Permission.SEND_INVOICE,
        organization_id=(
            invoice.client_organization_id
        ),
    )

    if (
        invoice.status
        != InvoiceStatus.DRAFT
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Only draft invoices "
                "can be sent."
            ),
        )

    if not invoice.bill_to_email:
        raise HTTPException(
            status_code=422,
            detail=(
                "Invoice does not have "
                "a billing email."
            ),
        )

    api_key = os.environ.get(
        "RESEND_API_KEY",
        "",
    ).strip()

    from_address = (
        os.environ.get(
            "RA_INVOICE_FROM",
            "",
        ).strip()
        or os.environ.get(
            "RA_LEAD_NOTIFICATION_FROM",
            "",
        ).strip()
    )

    issuer_email = os.environ.get(
        "RA_BILLING_ISSUER_EMAIL",
        "",
    ).strip()

    issuer_title = (
        os.environ.get(
            "RA_BILLING_ISSUER_TITLE",
            "Chief Financial Officer",
        ).strip()
        or "Chief Financial Officer"
    )

    reply_to = (
        os.environ.get(
            "RA_INVOICE_REPLY_TO",
            "",
        ).strip()
        or None
    )

    if (
        not api_key
        or not from_address
        or not issuer_email
    ):
        raise HTTPException(
            status_code=503,
            detail=(
                "Invoice email configuration "
                "is incomplete."
            ),
        )

    issuer = SQLiteUserRepository(
        connection
    ).get_by_email(
        issuer_email
    )

    if issuer is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Configured billing issuer "
                "was not found."
            ),
        )

    try:
        pdf_bytes = build_invoice_pdf(
            invoice=invoice,
            issuer_name=(
                issuer.display_name
            ),
            issuer_title=issuer_title,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Invoice PDF generation "
                "failed."
            ),
        ) from exc

    pdf_sha256 = hashlib.sha256(
        pdf_bytes
    ).hexdigest()

    pdf_filename = (
        f"{invoice.invoice_number}.pdf"
    )

    email_text = "\n".join(
        [
            (
                f"Hello "
                f"{invoice.bill_to_name},"
            ),
            "",
            (
                "Attached is invoice "
                f"{invoice.invoice_number} "
                "from Paradigm Ra."
            ),
            "",
            (
                "Balance due: "
                f"${invoice.balance_due:,.2f}"
            ),
            (
                "Due date: "
                + (
                    invoice.due_date.isoformat()
                    if invoice.due_date
                    else "See attached invoice"
                )
            ),
            "",
            "Thank you,",
            issuer.display_name,
            issuer_title,
            "Paradigm Ra",
        ]
    )

    try:
        delivery = send_pdf_email(
            api_key=api_key,
            from_address=from_address,
            to_address=(
                invoice.bill_to_email
            ),
            reply_to=reply_to,
            subject=(
                "Paradigm Ra Invoice "
                f"{invoice.invoice_number}"
            ),
            text=email_text,
            pdf_bytes=pdf_bytes,
            pdf_filename=pdf_filename,
            idempotency_key=(
                "invoice-send/"
                f"{invoice.id}"
            ),
        )

    except ResendDeliveryError as exc:
        # No invoice state has changed.
        connection.rollback()

        print(
            "INVOICE EMAIL DELIVERY FAILED:",
            str(exc),
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Invoice email delivery "
                "failed."
            ),
        ) from exc

    try:
        mark_invoice_sent(
            invoice
        )

        invoices.update(
            invoice
        )

        SQLiteAuditEventRepository(
            connection
        ).add(
            AuditEvent(
                actor_user_id=(
                    principal.user.id
                ),
                organization_id=(
                    invoice
                    .client_organization_id
                ),
                action=(
                    "billing.invoice_sent"
                ),
                resource_type="invoice",
                resource_id=invoice.id,
                metadata_json=json.dumps(
                    {
                        "invoice_number": (
                            invoice
                            .invoice_number
                        ),
                        "recipient": (
                            invoice
                            .bill_to_email
                        ),
                        "billing_issuer_user_id": (
                            str(issuer.id)
                        ),
                        "provider": "resend",
                        "provider_message_id": (
                            delivery.message_id
                        ),
                        "pdf_filename": (
                            pdf_filename
                        ),
                        "pdf_sha256": (
                            pdf_sha256
                        ),
                    },
                    sort_keys=True,
                ),
            )
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    return SendInvoiceResponse(
        invoice=build_invoice_response(
            invoice
        ),
        provider_message_id=(
            delivery.message_id
        ),
        pdf_sha256=pdf_sha256,
    )
