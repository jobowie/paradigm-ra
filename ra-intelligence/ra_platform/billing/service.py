from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from .models import (
    EngagementBillingTerms,
    Invoice,
    InvoiceLine,
    InvoiceStatus,
    Payment,
    PaymentStatus,
    Quote,
    QuoteStatus,
    TimeEntry,
    TimeEntryStatus,
)
from .repository import BillingUnitOfWork


def calculate_line_amount(
    quantity: Decimal,
    unit_rate: Decimal,
) -> Decimal:
    return quantity * unit_rate


def calculate_subtotal(invoice: Invoice) -> Decimal:
    return sum(
        (
            calculate_line_amount(
                line.quantity,
                line.unit_rate,
            )
            for line in invoice.line_items
        ),
        start=Decimal("0.00"),
    )


def calculate_total(invoice: Invoice) -> Decimal:
    return calculate_subtotal(invoice) + invoice.tax_amount


def calculate_amount_paid(
    invoice: Invoice,
    payments: list[Payment],
) -> Decimal:
    return sum(
        (
            payment.amount
            for payment in payments
            if payment.invoice_id == invoice.id
            and payment.status == PaymentStatus.RECEIVED
        ),
        start=Decimal("0.00"),
    )


def calculate_balance_due(
    invoice: Invoice,
    payments: list[Payment],
) -> Decimal:
    total = calculate_total(invoice)
    amount_paid = calculate_amount_paid(
        invoice,
        payments,
    )

    return max(
        total - amount_paid,
        Decimal("0.00"),
    )


def determine_invoice_status(
    invoice: Invoice,
    payments: list[Payment],
) -> InvoiceStatus:
    if invoice.status == InvoiceStatus.VOID:
        return InvoiceStatus.VOID

    total = calculate_total(invoice)
    amount_paid = calculate_amount_paid(
        invoice,
        payments,
    )

    if (
        amount_paid >= total
        and total > Decimal("0.00")
    ):
        return InvoiceStatus.PAID
    return invoice.status




def refresh_invoice(
    invoice: Invoice,
    payments: list[Payment],
) -> Invoice:
    for line in invoice.line_items:
        line.amount = calculate_line_amount(
            line.quantity,
            line.unit_rate,
        )

    invoice.subtotal = calculate_subtotal(invoice)
    invoice.total = calculate_total(invoice)

    invoice.amount_paid = calculate_amount_paid(
        invoice,
        payments,
    )

    invoice.balance_due = calculate_balance_due(
        invoice,
        payments,
    )

    invoice.status = determine_invoice_status(
        invoice,
        payments,
    )

    return invoice


def resolve_hourly_rate(
    engagement_id: UUID,
    work_date: date,
    billing_terms: list[EngagementBillingTerms],
) -> Decimal:
    matching_terms = [
        terms
        for terms in billing_terms
        if terms.engagement_id == engagement_id
        and terms.effective_from <= work_date
        and (
            terms.effective_to is None
            or work_date <= terms.effective_to
        )
    ]

    if not matching_terms:
        raise ValueError(
            "No billing terms found for engagement "
            f"{engagement_id} on {work_date}"
        )

    matching_terms.sort(
        key=lambda terms: terms.effective_from,
        reverse=True,
    )

    rate = matching_terms[0].hourly_rate

    if rate is None:
        raise ValueError(
            f"Engagement {engagement_id} "
            "does not have an hourly rate"
        )

    return rate


def build_invoice_lines_from_time_entries(
    time_entries: list[TimeEntry],
    billing_terms: list[EngagementBillingTerms],
) -> list[InvoiceLine]:
    invoice_lines: list[InvoiceLine] = []

    for entry in time_entries:
        if entry.status != TimeEntryStatus.APPROVED:
            continue

        rate = resolve_hourly_rate(
            engagement_id=entry.engagement_id,
            work_date=entry.work_date,
            billing_terms=billing_terms,
        )

        amount = calculate_line_amount(
            quantity=entry.hours,
            unit_rate=rate,
        )

        invoice_lines.append(
            InvoiceLine(
                engagement_id=entry.engagement_id,
                source_time_entry_ids=[entry.id],
                description=(
                    f"{entry.work_date.isoformat()} - "
                    f"{entry.description}"
                ),
                quantity=entry.hours,
                unit_rate=rate,
                amount=amount,
            )
        )

    return invoice_lines



def approve_time_entry(
    time_entry: TimeEntry,
) -> TimeEntry:
    if (
        time_entry.status
        == TimeEntryStatus.INVOICED
        or time_entry.invoice_id
        is not None
    ):
        raise ValueError(
            "Invoiced time entries "
            "cannot be approved."
        )

    if (
        time_entry.status
        == TimeEntryStatus.APPROVED
    ):
        return time_entry

    if (
        time_entry.status
        != TimeEntryStatus.DRAFT
    ):
        raise ValueError(
            "Only draft time entries "
            "can be approved."
        )

    time_entry.status = (
        TimeEntryStatus.APPROVED
    )

    return time_entry



def mark_time_entries_invoiced(
    time_entries: list[TimeEntry],
    invoice: Invoice,
) -> list[TimeEntry]:
    invoiced_entry_ids = {
        time_entry_id
        for line in invoice.line_items
        for time_entry_id in line.source_time_entry_ids
    }

    for entry in time_entries:
        if entry.id in invoiced_entry_ids:
            entry.status = TimeEntryStatus.INVOICED
            entry.invoice_id = invoice.id

    return time_entries


def generate_invoice_from_time_entries(
    *,
    client_organization_id: UUID,
    invoice_number: str,
    time_entries: list[TimeEntry],
    billing_terms: list[EngagementBillingTerms],
    bill_to_name: str,
    issue_date: date,
    payment_terms_days: int = 30,
    tax_amount: Decimal = Decimal("0.00"),
    bill_to_email: str | None = None,
    bill_to_address: str | None = None,
    notes: str | None = None,
) -> Invoice:
    eligible_entries = [
        entry
        for entry in time_entries
        if entry.status == TimeEntryStatus.APPROVED
        and entry.invoice_id is None
    ]

    if not eligible_entries:
        raise ValueError(
            "No approved, uninvoiced time entries were provided."
        )

    invoice_lines = build_invoice_lines_from_time_entries(
        time_entries=eligible_entries,
        billing_terms=billing_terms,
    )

    if not invoice_lines:
        raise ValueError(
            "No invoice lines could be generated."
        )

    invoice = Invoice(
        client_organization_id=client_organization_id,
        invoice_number=invoice_number,
        issue_date=issue_date,
        due_date=issue_date + timedelta(
            days=payment_terms_days
        ),
        bill_to_name=bill_to_name,
        bill_to_email=bill_to_email,
        bill_to_address=bill_to_address,
        line_items=invoice_lines,
        tax_amount=tax_amount,
        notes=notes,
    )

    return refresh_invoice(
        invoice=invoice,
        payments=[],
    )


def create_invoice_from_time_entries(
    *,
    uow: BillingUnitOfWork,
    client_organization_id: UUID,
    invoice_number: str,
    time_entries: list[TimeEntry],
    billing_terms: list[EngagementBillingTerms],
    bill_to_name: str,
    issue_date: date,
    payment_terms_days: int = 30,
    tax_amount: Decimal = Decimal("0.00"),
    bill_to_email: str | None = None,
    bill_to_address: str | None = None,
    notes: str | None = None,
) -> Invoice:
    invoice = generate_invoice_from_time_entries(
        client_organization_id=client_organization_id,
        invoice_number=invoice_number,
        time_entries=time_entries,
        billing_terms=billing_terms,
        bill_to_name=bill_to_name,
        issue_date=issue_date,
        payment_terms_days=payment_terms_days,
        tax_amount=tax_amount,
        bill_to_email=bill_to_email,
        bill_to_address=bill_to_address,
        notes=notes,
    )

    with uow:
        uow.invoices.add(invoice)

        updated_entries = mark_time_entries_invoiced(
            time_entries=time_entries,
            invoice=invoice,
        )

        uow.time_entries.update_many(
            updated_entries
        )

        uow.commit()

    return invoice

def calculate_quote_subtotal(
    quote: Quote,
) -> Decimal:
    return sum(
        (
            line.quantity * line.unit_rate
            for line in quote.line_items
        ),
        start=Decimal("0.00"),
    )


def calculate_quote_total(
    quote: Quote,
) -> Decimal:
    return (
        calculate_quote_subtotal(quote)
        + quote.tax_amount
    )


def refresh_quote(
    quote: Quote,
) -> Quote:
    for line in quote.line_items:
        line.amount = (
            line.quantity
            * line.unit_rate
        )

    quote.subtotal = calculate_quote_subtotal(
        quote
    )

    quote.total = calculate_quote_total(
        quote
    )

    return quote



def send_invoice(
    invoice: Invoice,
    *,
    sent_at: datetime | None = None,
) -> Invoice:
    if (
        invoice.status
        != InvoiceStatus.DRAFT
    ):
        raise ValueError(
            "Only draft invoices can be sent."
        )

    timestamp = (
        sent_at
        or datetime.now(timezone.utc)
    )

    invoice.status = (
        InvoiceStatus.SENT
    )

    invoice.sent_at = timestamp
    invoice.updated_at = timestamp

    return invoice



def send_quote(
    quote: Quote,
    *,
    sent_at: datetime | None = None,
) -> Quote:
    if quote.status != QuoteStatus.DRAFT:
        raise ValueError(
            "Only draft quotes can be sent."
        )

    quote.status = QuoteStatus.SENT
    quote.sent_at = (
        sent_at
        or datetime.now(timezone.utc)
    )

    return quote


def accept_quote(
    quote: Quote,
    *,
    accepted_at: datetime | None = None,
) -> Quote:
    if quote.status != QuoteStatus.SENT:
        raise ValueError(
            "Only sent quotes can be accepted."
        )

    timestamp = (
        accepted_at
        or datetime.now(timezone.utc)
    )

    if (
        quote.expiration_date is not None
        and timestamp.date()
        > quote.expiration_date
    ):
        quote.status = QuoteStatus.EXPIRED

        raise ValueError(
            "Expired quotes cannot be accepted."
        )

    quote.status = QuoteStatus.ACCEPTED
    quote.accepted_at = timestamp

    return quote


def decline_quote(
    quote: Quote,
    *,
    declined_at: datetime | None = None,
) -> Quote:
    if quote.status != QuoteStatus.SENT:
        raise ValueError(
            "Only sent quotes can be declined."
        )

    quote.status = QuoteStatus.DECLINED
    quote.declined_at = (
        declined_at
        or datetime.now(timezone.utc)
    )

    return quote

def create_invoice_from_accepted_quote(
    *,
    quote: Quote,
    invoice_number: str,
    invoice_amount: Decimal,
    description: str,
    issue_date: date,
    due_date: date,
    existing_invoices: list[Invoice] | None = None,
) -> Invoice:
    if quote.status != QuoteStatus.ACCEPTED:
        raise ValueError(
            "Only accepted quotes can create invoices."
        )

    if invoice_amount <= Decimal("0.00"):
        raise ValueError(
            "Invoice amount must be greater than zero."
        )

    existing_invoices = existing_invoices or []

    already_invoiced = sum(
        (
            invoice.total
            for invoice in existing_invoices
            if invoice.source_quote_id == quote.id
            and invoice.status != InvoiceStatus.VOID
        ),
        start=Decimal("0.00"),
    )

    if already_invoiced + invoice_amount > quote.total:
        raise ValueError(
            "Invoice would exceed the accepted quote total."
        )

    invoice = Invoice(
        client_organization_id=quote.client_organization_id,
        source_quote_id=quote.id,
        invoice_number=invoice_number,
        issue_date=issue_date,
        due_date=due_date,
        bill_to_name=quote.bill_to_name,
        bill_to_email=quote.bill_to_email,
        bill_to_address=quote.bill_to_address,
        line_items=[
            InvoiceLine(
                engagement_id=quote.engagement_id,
                description=description,
                quantity=Decimal("1"),
                unit_rate=invoice_amount,
            )
        ],
        notes=quote.notes,
        terms=quote.terms,
    )

    return refresh_invoice(
        invoice=invoice,
        payments=[],
    )

