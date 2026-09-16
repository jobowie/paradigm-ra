import sqlite3
from uuid import UUID

from ra_platform.organizations.models import (
    Organization,
    OrganizationStatus,
    OrganizationType,
)
from ra_platform.engagements.models import (
    Engagement,
    EngagementSource,
    EngagementStatus,
)


class SQLiteOrganizationRepository:
    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self.connection = connection

    def add(
        self,
        organization: Organization,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO organizations (
                id,
                name,
                type,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(organization.id),
                organization.name,
                organization.type.value,
                organization.status.value,
                organization.created_at.isoformat(),
                organization.updated_at.isoformat(),
            ),
        )

    def get(
        self,
        organization_id: UUID,
    ) -> Organization | None:
        row = self.connection.execute(
            """
            SELECT *
            FROM organizations
            WHERE id = ?
            """,
            (str(organization_id),),
        ).fetchone()

        if row is None:
            return None

        return Organization(
            id=UUID(row["id"]),
            name=row["name"],
            type=OrganizationType(row["type"]),
            status=OrganizationStatus(row["status"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


class SQLiteEngagementRepository:
    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self.connection = connection

    def add(
        self,
        engagement: Engagement,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO engagements (
                id,
                client_organization_id,
                owner_organization_id,
                name,
                service_type,
                source,
                status,
                source_opportunity_id,
                discovery_session_id,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(engagement.id),
                str(engagement.client_organization_id),
                str(engagement.owner_organization_id),
                engagement.name,
                engagement.service_type,
                engagement.source.value,
                engagement.status.value,
                (
                    str(engagement.source_opportunity_id)
                    if engagement.source_opportunity_id
                    else None
                ),
                (
                    str(engagement.discovery_session_id)
                    if engagement.discovery_session_id
                    else None
                ),
                engagement.created_at.isoformat(),
                engagement.updated_at.isoformat(),
            ),
        )

    def get(
        self,
        engagement_id: UUID,
    ) -> Engagement | None:
        row = self.connection.execute(
            """
            SELECT *
            FROM engagements
            WHERE id = ?
            """,
            (str(engagement_id),),
        ).fetchone()

        if row is None:
            return None

        return Engagement(
            id=UUID(row["id"]),
            client_organization_id=UUID(
                row["client_organization_id"]
            ),
            owner_organization_id=UUID(
                row["owner_organization_id"]
            ),
            name=row["name"],
            service_type=row["service_type"],
            source=EngagementSource(row["source"]),
            status=EngagementStatus(row["status"]),
            source_opportunity_id=(
                UUID(row["source_opportunity_id"])
                if row["source_opportunity_id"]
                else None
            ),
            discovery_session_id=(
                UUID(row["discovery_session_id"])
                if row["discovery_session_id"]
                else None
            ),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
from datetime import date
from decimal import Decimal

from ra_platform.billing.models import (
    Invoice,
    InvoiceLine,
    InvoiceStatus,
    TimeEntry,
    TimeEntryStatus,
)


class SQLiteInvoiceRepository:
    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self.connection = connection

    def add(
        self,
        invoice: Invoice,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO invoices (
                id,
                client_organization_id,
                invoice_number,
                status,
                issue_date,
                due_date,
                bill_to_name,
                bill_to_email,
                bill_to_address,
                subtotal,
                tax_amount,
                total,
                amount_paid,
                balance_due,
                notes,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(invoice.id),
                str(invoice.client_organization_id),
                invoice.invoice_number,
                invoice.status.value,
                invoice.issue_date.isoformat()
                if invoice.issue_date else None,
                invoice.due_date.isoformat()
                if invoice.due_date else None,
                invoice.bill_to_name,
                invoice.bill_to_email,
                invoice.bill_to_address,
                str(invoice.subtotal),
                str(invoice.tax_amount),
                str(invoice.total),
                str(invoice.amount_paid),
                str(invoice.balance_due),
                invoice.notes,
                invoice.created_at.isoformat(),
                invoice.updated_at.isoformat(),
            ),
        )

        for line in invoice.line_items:
            self.connection.execute(
                """
                INSERT INTO invoice_lines (
                    id,
                    invoice_id,
                    engagement_id,
                    description,
                    quantity,
                    unit_rate,
                    amount
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(line.id),
                    str(invoice.id),
                    str(line.engagement_id),
                    line.description,
                    str(line.quantity),
                    str(line.unit_rate),
                    str(line.amount),
                ),
            )

            for time_entry_id in line.source_time_entry_ids:
                self.connection.execute(
                    """
                    INSERT INTO invoice_line_time_entries (
                        invoice_line_id,
                        time_entry_id
                    )
                    VALUES (?, ?)
                    """,
                    (
                        str(line.id),
                        str(time_entry_id),
                    ),
                )

    def get(
        self,
        invoice_id: UUID,
    ) -> Invoice | None:
        row = self.connection.execute(
            """
            SELECT *
            FROM invoices
            WHERE id = ?
            """,
            (str(invoice_id),),
        ).fetchone()

        if row is None:
            return None

        line_rows = self.connection.execute(
            """
            SELECT *
            FROM invoice_lines
            WHERE invoice_id = ?
            ORDER BY rowid
            """,
            (str(invoice_id),),
        ).fetchall()

        line_items = []

        for line_row in line_rows:
            source_rows = self.connection.execute(
                """
                SELECT time_entry_id
                FROM invoice_line_time_entries
                WHERE invoice_line_id = ?
                """,
                (line_row["id"],),
            ).fetchall()

            line_items.append(
                InvoiceLine(
                    id=UUID(line_row["id"]),
                    engagement_id=UUID(
                        line_row["engagement_id"]
                    ),
                    source_time_entry_ids=[
                        UUID(source_row["time_entry_id"])
                        for source_row in source_rows
                    ],
                    description=line_row["description"],
                    quantity=Decimal(
                        line_row["quantity"]
                    ),
                    unit_rate=Decimal(
                        line_row["unit_rate"]
                    ),
                    amount=Decimal(
                        line_row["amount"]
                    ),
                )
            )

        return Invoice(
            id=UUID(row["id"]),
            client_organization_id=UUID(
                row["client_organization_id"]
            ),
            invoice_number=row["invoice_number"],
            status=InvoiceStatus(row["status"]),
            issue_date=(
                date.fromisoformat(row["issue_date"])
                if row["issue_date"]
                else None
            ),
            due_date=(
                date.fromisoformat(row["due_date"])
                if row["due_date"]
                else None
            ),
            bill_to_name=row["bill_to_name"],
            bill_to_email=row["bill_to_email"],
            bill_to_address=row["bill_to_address"],
            line_items=line_items,
            subtotal=Decimal(row["subtotal"]),
            tax_amount=Decimal(row["tax_amount"]),
            total=Decimal(row["total"]),
            amount_paid=Decimal(row["amount_paid"]),
            balance_due=Decimal(row["balance_due"]),
            notes=row["notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


class SQLiteTimeEntryRepository:
    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self.connection = connection

    def add_many(
        self,
        time_entries: list[TimeEntry],
    ) -> None:
        for entry in time_entries:
            self.connection.execute(
                """
                INSERT INTO time_entries (
                    id,
                    engagement_id,
                    work_date,
                    description,
                    hours,
                    status,
                    invoice_id,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(entry.id),
                    str(entry.engagement_id),
                    entry.work_date.isoformat(),
                    entry.description,
                    str(entry.hours),
                    entry.status.value,
                    (
                        str(entry.invoice_id)
                        if entry.invoice_id
                        else None
                    ),
                    entry.created_at.isoformat(),
                ),
            )

    def update_many(
        self,
        time_entries: list[TimeEntry],
    ) -> None:
        for entry in time_entries:
            self.connection.execute(
                """
                UPDATE time_entries
                SET
                    status = ?,
                    invoice_id = ?
                WHERE id = ?
                """,
                (
                    entry.status.value,
                    (
                        str(entry.invoice_id)
                        if entry.invoice_id
                        else None
                    ),
                    str(entry.id),
                ),
            )

    def get(
        self,
        time_entry_id: UUID,
    ) -> TimeEntry | None:
        row = self.connection.execute(
            """
            SELECT *
            FROM time_entries
            WHERE id = ?
            """,
            (str(time_entry_id),),
        ).fetchone()

        if row is None:
            return None

        return TimeEntry(
            id=UUID(row["id"]),
            engagement_id=UUID(
                row["engagement_id"]
            ),
            work_date=date.fromisoformat(
                row["work_date"]
            ),
            description=row["description"],
            hours=Decimal(row["hours"]),
            status=TimeEntryStatus(
                row["status"]
            ),
            invoice_id=(
                UUID(row["invoice_id"])
                if row["invoice_id"]
                else None
            ),
            created_at=row["created_at"],
        )


class SQLiteBillingUnitOfWork:
    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self.connection = connection

        self.invoices = SQLiteInvoiceRepository(
            connection
        )

        self.time_entries = SQLiteTimeEntryRepository(
            connection
        )

    def __enter__(
        self,
    ) -> "SQLiteBillingUnitOfWork":
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        self.connection.commit()

    def rollback(self) -> None:
        self.connection.rollback()