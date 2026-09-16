import sqlite3

from .sqlite import initialize_database


EXPECTED_TABLES = {
    "organizations",
    "engagements",
    "engagement_billing_terms",
    "invoices",
    "invoice_lines",
    "time_entries",
    "invoice_line_time_entries",
    "payments",
}


def test_database_schema_can_be_initialized():
    connection = sqlite3.connect(":memory:")

    initialize_database(connection)

    tables = {
        row[0]
        for row in connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        )
    }

    assert EXPECTED_TABLES.issubset(tables)


def test_foreign_keys_are_enforced():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")

    initialize_database(connection)

    try:
        connection.execute(
            """
            INSERT INTO engagements (
                id,
                client_organization_id,
                owner_organization_id,
                name,
                service_type,
                source,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "engagement-1",
                "missing-client",
                "missing-owner",
                "Bookkeeping",
                "bookkeeping",
                "contract_conversion",
                "active",
                "2026-09-15T00:00:00+00:00",
                "2026-09-15T00:00:00+00:00",
            ),
        )

        connection.commit()

        assert False, "Expected foreign-key failure"

    except sqlite3.IntegrityError:
        pass