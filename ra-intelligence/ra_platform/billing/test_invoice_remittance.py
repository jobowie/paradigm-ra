from datetime import date
from decimal import Decimal
from uuid import UUID

from ra_platform.billing.invoice_pdf import (
    InvoiceBillTo,
    InvoiceRemittance,
    build_invoice_pdf,
)
from ra_platform.billing.models import (
    Invoice,
    InvoiceLine,
)
from ra_platform.organizations.billing_profile import (
    OrganizationBillingProfile,
)
from ra_platform.organizations.billing_profile_service import (
    decrypt_organization_financial_value,
)
from ra_platform.security.financial_data import (
    encrypt_financial_value,
)


def test_organization_financial_value_round_trip():
    organization_id = UUID(
        "11111111-1111-1111-1111-111111111111"
    )
    key = b"k" * 32

    profile = OrganizationBillingProfile(
        organization_id=organization_id
    )

    profile.routing_number_ciphertext = (
        encrypt_financial_value(
            "123456789",
            context=(
                f"organization:"
                f"{organization_id}:"
                "routing_number"
            ),
            key=key,
        )
    )

    assert (
        decrypt_organization_financial_value(
            profile=profile,
            field_name="routing_number",
            key=key,
        )
        == "123456789"
    )


def test_invoice_pdf_accepts_bill_to_and_remittance():
    invoice = Invoice(
        client_organization_id=UUID(
            "11111111-1111-1111-1111-111111111111"
        ),
        invoice_number="TRA-INV-2026-001",
        issue_date=date(2026, 9, 22),
        due_date=date(2026, 10, 7),
        bill_to_name="Paradigm Ra Internal Test",
        bill_to_email="billing@example.com",
        bill_to_address=(
            "123 Client Way\n"
            "Sacramento, CA 95829\n"
            "US"
        ),
        line_items=[
            InvoiceLine(
                engagement_id=UUID(
                    "22222222-2222-2222-2222-222222222222"
                ),
                description="Bookkeeping services",
                quantity=Decimal("1.00"),
                unit_rate=Decimal("70.00"),
                amount=Decimal("70.00"),
            )
        ],
        subtotal=Decimal("70.00"),
        tax_amount=Decimal("0.00"),
        total=Decimal("70.00"),
        amount_paid=Decimal("0.00"),
        balance_due=Decimal("70.00"),
        terms="Net 15",
    )

    pdf = build_invoice_pdf(
        invoice=invoice,
        issuer_name="Billing Owner",
        issuer_title="Chief Financial Officer",
        bill_to=InvoiceBillTo(
            name="Paradigm Ra Internal Test",
            contact_name="Test Billing Contact",
            email="billing@example.com",
            address=(
                "123 Client Way\n"
                "Sacramento, CA 95829\n"
                "US"
            ),
        ),
        remittance=InvoiceRemittance(
            payee_name="Paradigm Ra",
            remittance_email="billing@paradigmra.com",
            address=(
                "123 Remit Way\n"
                "Sacramento, CA 95829\n"
                "US"
            ),
            bank_name="Test Bank",
            account_type="Business Checking",
            routing_number="123456789",
            account_number="987654321",
        ),
    )

    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000
