from ra_platform.billing.models import (
    Invoice,
    InvoiceStatus,
)
from ra_platform.billing.service import (
    send_invoice,
)


def build_invoice() -> Invoice:
    return Invoice(
        client_organization_id=(
            "11111111-1111-1111-1111-111111111111"
        ),
        invoice_number=(
            "RA-INV-TEST-001"
        ),
        bill_to_name="Test Client",
    )


def test_send_invoice_marks_draft_sent():
    invoice = build_invoice()

    result = send_invoice(
        invoice
    )

    assert (
        result.status
        == InvoiceStatus.SENT
    )

    assert result.sent_at is not None


def test_send_invoice_rejects_second_send():
    invoice = build_invoice()

    send_invoice(
        invoice
    )

    try:
        send_invoice(
            invoice
        )
    except ValueError as exc:
        assert (
            "Only draft invoices"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Second send should fail."
        )
