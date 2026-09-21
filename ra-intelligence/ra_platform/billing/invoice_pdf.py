from __future__ import annotations

from io import BytesIO
from pathlib import Path

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


def _money(value) -> str:
    return f"${value:,.2f}"


def build_invoice_pdf(
    *,
    invoice: Invoice,
    issuer_name: str,
    issuer_title: str = "Chief Executive Officer",
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

    bill_to = (
        f"<b>{invoice.bill_to_name}</b>"
    )

    if invoice.bill_to_email:
        bill_to += (
            f"<br/>{invoice.bill_to_email}"
        )

    if invoice.bill_to_address:
        bill_to += (
            "<br/>"
            + invoice.bill_to_address
        )

    issuer = (
        f"<b>{issuer_name}</b>"
        f"<br/>{issuer_title}"
        "<br/>Paradigm Ra"
    )

    details = Table(
        [
            [
                Paragraph(
                    "FROM",
                    label_style,
                ),
                Paragraph(
                    "BILL TO",
                    label_style,
                ),
                Paragraph(
                    "INVOICE DETAILS",
                    label_style,
                ),
            ],
            [
                Paragraph(
                    issuer,
                    body_style,
                ),
                Paragraph(
                    bill_to,
                    body_style,
                ),
                Paragraph(
                    (
                        f"<b>Issue:</b> "
                        f"{issue_date}"
                        "<br/>"
                        f"<b>Due:</b> "
                        f"{due_date}"
                    ),
                    body_style,
                ),
            ],
        ],
        colWidths=[
            2.2 * inch,
            2.65 * inch,
            1.95 * inch,
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
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, 0),
                    5,
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
                line.description,
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
            4.45 * inch,
            1.15 * inch,
            1.2 * inch,
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
