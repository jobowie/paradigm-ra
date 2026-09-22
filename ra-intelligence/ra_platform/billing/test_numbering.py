import sqlite3
from datetime import date

from ra_platform.billing.numbering import (
    PRODUCTION_INVOICE_PREFIX,
    TEST_INVOICE_PREFIX,
    invoice_prefix_for_organization_name,
    next_invoice_number,
)


def connection():
    db = sqlite3.connect(":memory:")

    db.execute(
        """
        CREATE TABLE invoices (
            invoice_number TEXT NOT NULL
        )
        """
    )

    return db


def test_internal_test_uses_test_prefix():
    assert (
        invoice_prefix_for_organization_name(
            "Paradigm Ra Internal Test"
        )
        == TEST_INVOICE_PREFIX
    )

    assert (
        invoice_prefix_for_organization_name(
            "BrewBird Coffee"
        )
        == PRODUCTION_INVOICE_PREFIX
    )


def test_test_and_real_sequences_are_independent():
    db = connection()

    db.executemany(
        """
        INSERT INTO invoices (
            invoice_number
        )
        VALUES (?)
        """,
        [
            ("RA-INV-2026-001",),
            ("RA-INV-2026-002",),
            ("TRA-INV-2026-001",),
        ],
    )

    assert (
        next_invoice_number(
            db,
            invoice_date=date(
                2026,
                9,
                22,
            ),
            prefix="RA-INV",
        )
        == "RA-INV-2026-003"
    )

    assert (
        next_invoice_number(
            db,
            invoice_date=date(
                2026,
                9,
                22,
            ),
            prefix="TRA-INV",
        )
        == "TRA-INV-2026-002"
    )


def test_numbering_resets_by_year():
    db = connection()

    db.execute(
        """
        INSERT INTO invoices (
            invoice_number
        )
        VALUES (?)
        """,
        ("RA-INV-2026-009",),
    )

    assert (
        next_invoice_number(
            db,
            invoice_date=date(
                2027,
                1,
                5,
            ),
            prefix="RA-INV",
        )
        == "RA-INV-2027-001"
    )
