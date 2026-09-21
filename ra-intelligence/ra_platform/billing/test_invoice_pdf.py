from datetime import date
from decimal import Decimal

from ra_platform.billing.invoice_pdf import (
    build_invoice_pdf,
)
from ra_platform.billing.models import (
    Invoice,
    InvoiceLine,
)


def test_build_invoice_pdf():
    invoice = Invoice(
        client_organization_id=(
            "11111111-1111-1111-1111-111111111111"
        ),
        invoice_number="RA-INV-2026-001",
        issue_date=date(2026, 9, 21),
        due_date=date(2026, 10, 21),
        bill_to_name="BrewBird Coffee",
        bill_to_email="billing@example.com",
        line_items=[
            InvoiceLine(
                engagement_id=(
                    "22222222-2222-2222-2222-222222222222"
                ),
                description=(
                    "Bank reconciliation"
                ),
                quantity=Decimal("1"),
                unit_rate=Decimal("70.00"),
                amount=Decimal("70.00"),
            )
        ],
        subtotal=Decimal("70.00"),
        tax_amount=Decimal("0.00"),
        total=Decimal("70.00"),
        amount_paid=Decimal("0.00"),
        balance_due=Decimal("70.00"),
        terms="Net 30",
    )

    pdf = build_invoice_pdf(
        invoice=invoice,
        issuer_name="Test Executive",
    )

    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000
