import sqlite3

from datetime import date


def next_invoice_number(
    connection: sqlite3.Connection,
    *,
    invoice_date: date | None = None,
) -> str:
    row = connection.execute(
        """
        SELECT COUNT(*) AS invoice_count
        FROM invoices
        """
    ).fetchone()

    count = int(
        row["invoice_count"]
    ) + 1

    year = (
        invoice_date
        or date.today()
    ).year

    return (
        f"RA-INV-"
        f"{year}-"
        f"{count:03d}"
    )
