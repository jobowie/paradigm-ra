import sqlite3
from pathlib import Path


DEFAULT_DB_PATH = Path("data/paradigm_ra.db")


def create_connection(
    db_path: Path = DEFAULT_DB_PATH,
) -> sqlite3.Connection:
    db_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database(
    connection: sqlite3.Connection,
) -> None:
    connection.execute("PRAGMA foreign_keys = ON")

    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS organizations (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );


        CREATE TABLE IF NOT EXISTS engagements (
            id TEXT PRIMARY KEY,

            client_organization_id TEXT NOT NULL,
            owner_organization_id TEXT NOT NULL,

            name TEXT NOT NULL,
            service_type TEXT NOT NULL,

            source TEXT NOT NULL,
            status TEXT NOT NULL,

            source_opportunity_id TEXT,
            discovery_session_id TEXT,

            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,

            FOREIGN KEY (client_organization_id)
                REFERENCES organizations(id),

            FOREIGN KEY (owner_organization_id)
                REFERENCES organizations(id)
        );


        CREATE TABLE IF NOT EXISTS engagement_billing_terms (
            id TEXT PRIMARY KEY,

            engagement_id TEXT NOT NULL,

            billing_type TEXT NOT NULL,
            billing_cadence TEXT NOT NULL,

            hourly_rate TEXT,

            expected_hours_min TEXT,
            expected_hours_max TEXT,

            payment_terms_days INTEGER NOT NULL,

            effective_from TEXT NOT NULL,
            effective_to TEXT,

            created_at TEXT NOT NULL,

            FOREIGN KEY (engagement_id)
                REFERENCES engagements(id)
        );


        CREATE TABLE IF NOT EXISTS quotes (
            id TEXT PRIMARY KEY,

            client_organization_id TEXT NOT NULL,
            engagement_id TEXT NOT NULL,

            quote_number TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL,

            issue_date TEXT,
            expiration_date TEXT,

            bill_to_name TEXT NOT NULL,
            bill_to_email TEXT,
            bill_to_address TEXT,

            subtotal TEXT NOT NULL,
            tax_amount TEXT NOT NULL,
            total TEXT NOT NULL,

            notes TEXT,
            terms TEXT,

            sent_at TEXT,
            accepted_at TEXT,
            declined_at TEXT,

            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,

            FOREIGN KEY (client_organization_id)
                REFERENCES organizations(id),

            FOREIGN KEY (engagement_id)
                REFERENCES engagements(id)
        );


        CREATE TABLE IF NOT EXISTS quote_lines (
            id TEXT PRIMARY KEY,

            quote_id TEXT NOT NULL,

            description TEXT NOT NULL,

            quantity TEXT NOT NULL,
            unit_rate TEXT NOT NULL,
            amount TEXT NOT NULL,

            FOREIGN KEY (quote_id)
                REFERENCES quotes(id)
        );


        CREATE TABLE IF NOT EXISTS invoices (
            id TEXT PRIMARY KEY,

            client_organization_id TEXT NOT NULL,
            source_quote_id TEXT,

            invoice_number TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL,

            issue_date TEXT,
            due_date TEXT,

            bill_to_name TEXT NOT NULL,
            bill_to_email TEXT,
            bill_to_address TEXT,

            subtotal TEXT NOT NULL,
            tax_amount TEXT NOT NULL,
            total TEXT NOT NULL,

            amount_paid TEXT NOT NULL,
            balance_due TEXT NOT NULL,

            notes TEXT,
            terms TEXT,

            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,

            FOREIGN KEY (client_organization_id)
                REFERENCES organizations(id),

            FOREIGN KEY (source_quote_id)
                REFERENCES quotes(id)
        );


        CREATE TABLE IF NOT EXISTS invoice_lines (
            id TEXT PRIMARY KEY,

            invoice_id TEXT NOT NULL,
            engagement_id TEXT NOT NULL,

            description TEXT NOT NULL,

            quantity TEXT NOT NULL,
            unit_rate TEXT NOT NULL,
            amount TEXT NOT NULL,

            FOREIGN KEY (invoice_id)
                REFERENCES invoices(id),

            FOREIGN KEY (engagement_id)
                REFERENCES engagements(id)
        );


        CREATE TABLE IF NOT EXISTS time_entries (
            id TEXT PRIMARY KEY,

            engagement_id TEXT NOT NULL,

            work_date TEXT NOT NULL,
            description TEXT NOT NULL,
            hours TEXT NOT NULL,

            status TEXT NOT NULL,
            invoice_id TEXT,

            created_at TEXT NOT NULL,

            FOREIGN KEY (engagement_id)
                REFERENCES engagements(id),

            FOREIGN KEY (invoice_id)
                REFERENCES invoices(id)
        );


        CREATE TABLE IF NOT EXISTS invoice_line_time_entries (
            invoice_line_id TEXT NOT NULL,
            time_entry_id TEXT NOT NULL,

            PRIMARY KEY (
                invoice_line_id,
                time_entry_id
            ),

            FOREIGN KEY (invoice_line_id)
                REFERENCES invoice_lines(id),

            FOREIGN KEY (time_entry_id)
                REFERENCES time_entries(id)
        );


        CREATE TABLE IF NOT EXISTS payments (
            id TEXT PRIMARY KEY,

            invoice_id TEXT NOT NULL,

            amount TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            status TEXT NOT NULL,

            external_reference TEXT,
            received_at TEXT,
            created_at TEXT NOT NULL,

            FOREIGN KEY (invoice_id)
                REFERENCES invoices(id)
        );
        """
    )

    connection.commit()
    