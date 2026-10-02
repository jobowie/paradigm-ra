from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from ra_platform.billing.models import Invoice


ASSET_DIR = (
    Path(__file__).resolve().parents[1]
    / "assets"
)

DEFAULT_LOGO_PATH = (
    ASSET_DIR / "RALogo.png"
)


@dataclass(frozen=True)
class InvoiceBillTo:
    name: str
    contact_name: str | None = None
    email: str | None = None
    address: str | None = None


@dataclass(frozen=True)
class InvoiceRemittance:
    payee_name: str
    remittance_email: str | None = None
    address: str | None = None
    bank_name: str | None = None
    account_type: str | None = None
    routing_number: str | None = None
    account_number: str | None = None


def _html_lines(
    value: str,
) -> str:
    return "<br/>".join(
        escape(line.strip())
        for line in value.splitlines()
        if line.strip()
    )


def _labeled_table(
    rows,
    *,
    col_widths,
    label_style,
    body_style,
):
    rendered_rows = []

    for label, value in rows:
        if value is None:
            continue

        value_text = str(value).strip()

        if not value_text:
            continue

        rendered_rows.append(
            [
                Paragraph(
                    escape(label.upper()),
                    label_style,
                ),
                Paragraph(
                    _html_lines(value_text),
                    body_style,
                ),
            ]
        )

    table = Table(
        rendered_rows,
        colWidths=col_widths,
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    return table


def _money(value) -> str:
    return f"${value:,.2f}"


def build_invoice_pdf(
    *,
    invoice: Invoice,
    issuer_name: str,
    issuer_title: str = "Chief Executive Officer",
    bill_to: InvoiceBillTo | None = None,
    remittance: InvoiceRemittance | None = None,
    logo_path: Path = DEFAULT_LOGO_PATH,
) -> bytes:
    if not issuer_name.strip():
        raise ValueError(
            "Invoice issuer name is required."
        )

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title=(
            f"Paradigm Ra Invoice "
            f"{invoice.invoice_number}"
        ),
        author="Paradigm Ra",
    )

    styles = getSampleStyleSheet()

    label_style = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor(
            "#777B86"
        ),
        spaceAfter=2,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor(
            "#17181C"
        ),
    )

    line_description_style = ParagraphStyle(
        "InvoiceLineDescription",
        parent=body_style,
        fontSize=9,
        leading=12,
        spaceAfter=0,
    )

    small_style = ParagraphStyle(
        "Small",
        parent=body_style,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor(
            "#555A65"
        ),
    )

    invoice_title_style = ParagraphStyle(
        "InvoiceTitle",
        parent=styles["Heading1"],
        fontSize=23,
        leading=25,
        alignment=TA_RIGHT,
        textColor=colors.HexColor(
            "#111217"
        ),
        spaceAfter=4,
    )

    invoice_number_style = ParagraphStyle(
        "InvoiceNumber",
        parent=small_style,
        alignment=TA_RIGHT,
    )

    story = []

    logo = Image(
        str(logo_path),
        width=0.56 * inch,
        height=0.56 * inch,
    )

    brand = Paragraph(
        "<b>PARADIGM RA</b><br/>"
        "<font size='8'>"
        "Software and Accounting Solutions "
        "for Business"
        "</font>",
        body_style,
    )

    invoice_heading = Paragraph(
        "INVOICE",
        invoice_title_style,
    )

    invoice_number = Paragraph(
        invoice.invoice_number,
        invoice_number_style,
    )

    header = Table(
        [
            [
                Table(
                    [[logo, brand]],
                    colWidths=[
                        0.68 * inch,
                        2.8 * inch,
                    ],
                ),
                Table(
                    [
                        [invoice_heading],
                        [invoice_number],
                    ]
                ),
            ]
        ],
        colWidths=[
            3.8 * inch,
            3.0 * inch,
        ],
    )

    header.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, 0),
                    "RIGHT",
                ),
            ]
        )
    )

    story.append(header)
    story.append(
        Spacer(1, 0.16 * inch)
    )

    # RA spectrum rule.
    rule = Table(
        [["", "", ""]],
        colWidths=[
            3.2 * inch,
            3.2 * inch,
            0.4 * inch,
        ],
        rowHeights=[3],
    )

    rule.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, 0),
                    colors.HexColor(
                        "#766BFF"
                    ),
                ),
                (
                    "BACKGROUND",
                    (1, 0),
                    (1, 0),
                    colors.HexColor(
                        "#38CFF2"
                    ),
                ),
                (
                    "BACKGROUND",
                    (2, 0),
                    (2, 0),
                    colors.HexColor(
                        "#F39B3D"
                    ),
                ),
            ]
        )
    )

    story.append(rule)
    story.append(
        Spacer(1, 0.26 * inch)
    )

    issue_date = (
        invoice.issue_date.isoformat()
        if invoice.issue_date
        else "Not specified"
    )

    due_date = (
        invoice.due_date.isoformat()
        if invoice.due_date
        else "Not specified"
    )

    bill_to_details = (
        bill_to
        or InvoiceBillTo(
            name=invoice.bill_to_name,
            email=invoice.bill_to_email,
            address=invoice.bill_to_address,
        )
    )

    remittance_details = (
        remittance
        or InvoiceRemittance(
            payee_name="Paradigm Ra",
        )
    )

    bill_to_table = _labeled_table(
        [
            (
                "Client",
                bill_to_details.name,
            ),
            (
                "Billing Contact",
                bill_to_details.contact_name,
            ),
            (
                "Billing Address",
                bill_to_details.address,
            ),
            (
                "Billing Email",
                bill_to_details.email,
            ),
        ],
        col_widths=[
            0.85 * inch,
            1.50 * inch,
        ],
        label_style=label_style,
        body_style=body_style,
    )

    remittance_table = _labeled_table(
        [
            (
                "Payee",
                remittance_details.payee_name,
            ),
            (
                "Remit Address",
                remittance_details.address,
            ),
            (
                "Bank Name",
                remittance_details.bank_name,
            ),
            (
                "Account Type",
                remittance_details.account_type,
            ),
            (
                "Routing Number",
                remittance_details.routing_number,
            ),
            (
                "Account Number",
                remittance_details.account_number,
            ),
            (
                "Remit Email",
                remittance_details.remittance_email,
            ),
        ],
        col_widths=[
            0.95 * inch,
            1.80 * inch,
        ],
        label_style=label_style,
        body_style=body_style,
    )

    invoice_details_table = _labeled_table(
        [
            (
                "Issue",
                issue_date,
            ),
            (
                "Due",
                due_date,
            ),
            (
                "Balance",
                _money(
                    invoice.balance_due
                ),
            ),
        ],
        col_widths=[
            0.68 * inch,
            0.72 * inch,
        ],
        label_style=label_style,
        body_style=body_style,
    )

    details = Table(
        [
            [
                Paragraph(
                    "<b>BILL TO</b>",
                    label_style,
                ),
                Paragraph(
                    "<b>PAY TO / REMIT TO</b>",
                    label_style,
                ),
                Paragraph(
                    "<b>INVOICE DETAILS</b>",
                    label_style,
                ),
            ],
            [
                bill_to_table,
                remittance_table,
                invoice_details_table,
            ],
        ],
        colWidths=[
            2.45 * inch,
            2.85 * inch,
            1.50 * inch,
        ],
    )

    details.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, 0),
                    7,
                ),
                (
                    "LINEAFTER",
                    (0, 0),
                    (0, -1),
                    0.35,
                    colors.HexColor(
                        "#D9DBE1"
                    ),
                ),
                (
                    "LINEAFTER",
                    (1, 0),
                    (1, -1),
                    0.35,
                    colors.HexColor(
                        "#D9DBE1"
                    ),
                ),
            ]
        )
    )

    story.append(details)
    story.append(
        Spacer(1, 0.34 * inch)
    )

    rows = [
        [
            "DESCRIPTION",
            "QTY",
            "RATE",
            "AMOUNT",
        ]
    ]

    for line in invoice.line_items:
        rows.append(
            [
                Paragraph(
                    escape(
                        line.description
                    ),
                    line_description_style,
                ),
                f"{line.quantity}",
                _money(
                    line.unit_rate
                ),
                _money(
                    line.amount
                ),
            ]
        )

    line_table = Table(
        rows,
        colWidths=[
            3.75 * inch,
            0.75 * inch,
            1.15 * inch,
            1.15 * inch,
        ],
        repeatRows=1,
    )

    line_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#F3F4F7"
                    ),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#555A65"
                    ),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, 0),
                    8,
                ),
                (
                    "FONTSIZE",
                    (0, 1),
                    (-1, -1),
                    9,
                ),
                (
                    "ALIGN",
                    (1, 1),
                    (-1, -1),
                    "RIGHT",
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LINEBELOW",
                    (0, 0),
                    (-1, 0),
                    0.5,
                    colors.HexColor(
                        "#D9DBE1"
                    ),
                ),
                (
                    "LINEBELOW",
                    (0, 1),
                    (-1, -1),
                    0.35,
                    colors.HexColor(
                        "#E6E7EB"
                    ),
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
            ]
        )
    )

    story.append(line_table)
    story.append(
        Spacer(1, 0.24 * inch)
    )

    totals = Table(
        [
            [
                "",
                "Subtotal",
                _money(
                    invoice.subtotal
                ),
            ],
            [
                "",
                "Tax",
                _money(
                    invoice.tax_amount
                ),
            ],
            [
                "",
                "Paid",
                _money(
                    invoice.amount_paid
                ),
            ],
            [
                "",
                "Balance Due",
                _money(
                    invoice.balance_due
                ),
            ],
        ],
        colWidths=[
            4.30 * inch,
            1.30 * inch,
            1.20 * inch,
        ],
    )

    totals.setStyle(
        TableStyle(
            [
                (
                    "ALIGN",
                    (1, 0),
                    (-1, -1),
                    "RIGHT",
                ),
                (
                    "FONTNAME",
                    (1, 3),
                    (-1, 3),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "LINEABOVE",
                    (1, 3),
                    (-1, 3),
                    1,
                    colors.HexColor(
                        "#22242A"
                    ),
                ),
                (
                    "TOPPADDING",
                    (1, 3),
                    (-1, 3),
                    8,
                ),
            ]
        )
    )

    story.append(totals)

    if invoice.terms:
        story.append(
            Spacer(1, 0.3 * inch)
        )
        story.append(
            Paragraph(
                "PAYMENT TERMS",
                label_style,
            )
        )
        story.append(
            Paragraph(
                invoice.terms,
                small_style,
            )
        )

    if invoice.notes:
        story.append(
            Spacer(1, 0.18 * inch)
        )
        story.append(
            Paragraph(
                "NOTES",
                label_style,
            )
        )
        story.append(
            Paragraph(
                invoice.notes,
                small_style,
            )
        )

    story.append(
        Spacer(1, 0.38 * inch)
    )

    story.append(
        Paragraph(
            (
                "Paradigm Ra"
                " &nbsp;&nbsp;|&nbsp;&nbsp; "
                "Secure operational billing"
            ),
            small_style,
        )
    )

    document.build(story)

    return buffer.getvalue()
