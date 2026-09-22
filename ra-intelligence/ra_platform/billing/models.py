from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    VOID = "void"


class QuoteStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    RECEIVED = "received"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    EXTERNAL_AP = "external_ap"
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"
    CARD = "card"
    OTHER = "other"


class BillingType(str, Enum):
    HOURLY = "hourly"
    FIXED = "fixed"
    RETAINER = "retainer"


class BillingCadence(str, Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    MILESTONE = "milestone"


class TimeEntryStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    INVOICED = "invoiced"


class TimeEntryWorkstream(str, Enum):
    ACCOUNTS_PAYABLE = "accounts_payable"
    ACCOUNTS_RECEIVABLE = "accounts_receivable"
    RECONCILIATION = "reconciliation"
    EXPENSES = "expenses"
    REPORTING = "reporting"
    PAYROLL = "payroll"
    BOOKKEEPING = "bookkeeping"
    OTHER = "other"


class TimeEntryFriction(str, Enum):
    NONE_OBSERVED = "none_observed"
    MANUAL_ENTRY = "manual_entry"
    MISSING_INFORMATION = "missing_information"
    DUPLICATE_WORK = "duplicate_work"
    APPROVAL_DELAY = "approval_delay"
    SYSTEM_ISSUE = "system_issue"
    FOLLOW_UP_REQUIRED = "follow_up_required"
    OTHER = "other"


class QuoteLine(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    description: str = Field(min_length=1)

    quantity: Decimal = Field(gt=0)
    unit_rate: Decimal = Field(ge=0)

    amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
    )


class Quote(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    client_organization_id: UUID
    engagement_id: UUID

    quote_number: str = Field(min_length=1)

    status: QuoteStatus = QuoteStatus.DRAFT

    issue_date: date | None = None
    expiration_date: date | None = None

    bill_to_name: str = Field(min_length=1)
    bill_to_email: str | None = None
    bill_to_address: str | None = None

    line_items: list[QuoteLine] = Field(
        default_factory=list
    )

    subtotal: Decimal = Decimal("0.00")
    tax_amount: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")

    notes: str | None = None
    terms: str | None = None

    sent_at: datetime | None = None
    accepted_at: datetime | None = None
    declined_at: datetime | None = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class InvoiceLine(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    engagement_id: UUID

    source_time_entry_ids: list[UUID] = Field(
        default_factory=list
    )

    description: str = Field(min_length=1)

    quantity: Decimal = Field(gt=0)
    unit_rate: Decimal = Field(ge=0)

    amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
    )


class Invoice(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    client_organization_id: UUID
    source_quote_id: UUID | None = None

    invoice_number: str = Field(min_length=1)

    status: InvoiceStatus = InvoiceStatus.DRAFT

    issue_date: date | None = None
    due_date: date | None = None

    bill_to_name: str = Field(min_length=1)
    bill_to_email: str | None = None
    bill_to_address: str | None = None

    line_items: list[InvoiceLine] = Field(
        default_factory=list
    )

    subtotal: Decimal = Decimal("0.00")
    tax_amount: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")

    amount_paid: Decimal = Decimal("0.00")
    balance_due: Decimal = Decimal("0.00")

    notes: str | None = None
    terms: str | None = None

    sent_at: datetime | None = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class Payment(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    invoice_id: UUID

    amount: Decimal = Field(gt=0)

    payment_method: PaymentMethod
    status: PaymentStatus = PaymentStatus.PENDING

    external_reference: str | None = None
    received_at: datetime | None = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class EngagementBillingTerms(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    engagement_id: UUID

    billing_type: BillingType
    billing_cadence: BillingCadence

    hourly_rate: Decimal | None = None

    expected_hours_min: Decimal | None = None
    expected_hours_max: Decimal | None = None

    payment_terms_days: int = Field(
        default=30,
        ge=0,
    )

    effective_from: date
    effective_to: date | None = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class TimeEntry(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    engagement_id: UUID

    work_date: date
    description: str = Field(min_length=1)

    hours: Decimal = Field(gt=0)

    workstream: TimeEntryWorkstream | None = None
    friction: TimeEntryFriction | None = None
    operational_note: str | None = None

    status: TimeEntryStatus = TimeEntryStatus.DRAFT

    invoice_id: UUID | None = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    