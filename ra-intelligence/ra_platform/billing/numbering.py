import sqlite3

from datetime import date


PRODUCTION_INVOICE_PREFIX = "RA-INV"
TEST_INVOICE_PREFIX = "TRA-INV"

INTERNAL_TEST_ORGANIZATION_NAME = (
    "Paradigm Ra Internal Test"
)


def invoice_prefix_for_organization_name(
    organization_name: str,
) -> str:
    if (
        organization_name.strip().casefold()
        == INTERNAL_TEST_ORGANIZATION_NAME
        .casefold()
    ):
        return TEST_INVOICE_PREFIX

    return PRODUCTION_INVOICE_PREFIX


def next_invoice_number(
    connection: sqlite3.Connection,
    *,
    invoice_date: date,
    prefix: str = PRODUCTION_INVOICE_PREFIX,
) -> str:
    allowed_prefixes = {
        PRODUCTION_INVOICE_PREFIX,
        TEST_INVOICE_PREFIX,
    }

    if prefix not in allowed_prefixes:
        raise ValueError(
            "Unsupported invoice prefix."
        )

    stem = (
        f"{prefix}-"
        f"{invoice_date.year}-"
    )

    rows = connection.execute(
        """
        SELECT invoice_number
        FROM invoices
        WHERE invoice_number LIKE ?
        """,
        (f"{stem}%",),
    ).fetchall()

    highest = 0

    for row in rows:
        invoice_number = str(
            row[0]
        )

        if not invoice_number.startswith(
            stem
        ):
            continue

        suffix = invoice_number[
            len(stem):
        ]

        if suffix.isdigit():
            highest = max(
                highest,
                int(suffix),
            )

    return (
        f"{stem}"
        f"{highest + 1:03d}"
    )
