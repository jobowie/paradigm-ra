import sqlite3

from datetime import date, datetime
from decimal import Decimal
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

from ra_platform.identity.models import (
    AuditEvent,
    AuthSession,
    MembershipRole,
    OrganizationMembership,
    User,
    UserStatus,
)

from ra_platform.billing.models import (
    BillingCadence,
    BillingType,
    EngagementBillingTerms,
    Invoice,
    InvoiceLine,
    InvoiceStatus,
    Quote,
    QuoteLine,
    QuoteStatus,
    TimeEntry,
    TimeEntryFriction,
    TimeEntryStatus,
    TimeEntryWorkstream,
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

    def update(
        self,
        organization: Organization,
    ) -> None:
        self.connection.execute(
            """
            UPDATE organizations
            SET
                name = ?,
                type = ?,
                status = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                organization.name,
                organization.type.value,
                organization.status.value,
                organization.updated_at.isoformat(),
                str(organization.id),
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



    def list_all(
        self,
    ) -> list[Organization]:
        rows = self.connection.execute(
            """
            SELECT *
            FROM organizations
            ORDER BY lower(name)
            """
        ).fetchall()

        return [
            Organization(
                id=UUID(row["id"]),
                name=row["name"],
                type=OrganizationType(
                    row["type"]
                ),
                status=OrganizationStatus(
                    row["status"]
                ),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]


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



    def list_for_client(
        self,
        client_organization_id: UUID,
    ) -> list[Engagement]:
        rows = self.connection.execute(
            """
            SELECT *
            FROM engagements
            WHERE client_organization_id = ?
            ORDER BY created_at
            """,
            (
                str(
                    client_organization_id
                ),
            ),
        ).fetchall()

        return [
            Engagement(
                id=UUID(row["id"]),
                client_organization_id=UUID(
                    row[
                        "client_organization_id"
                    ]
                ),
                owner_organization_id=UUID(
                    row[
                        "owner_organization_id"
                    ]
                ),
                name=row["name"],
                service_type=row[
                    "service_type"
                ],
                source=EngagementSource(
                    row["source"]
                ),
                status=EngagementStatus(
                    row["status"]
                ),
                source_opportunity_id=(
                    UUID(
                        row[
                            "source_opportunity_id"
                        ]
                    )
                    if row[
                        "source_opportunity_id"
                    ]
                    else None
                ),
                discovery_session_id=(
                    UUID(
                        row[
                            "discovery_session_id"
                        ]
                    )
                    if row[
                        "discovery_session_id"
                    ]
                    else None
                ),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]


class SQLiteQuoteRepository:
    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self.connection = connection

    def add(
        self,
        quote: Quote,
    ) -> None:
        engagement_row = self.connection.execute(
            """
            SELECT client_organization_id
            FROM engagements
            WHERE id = ?
            """,
            (str(quote.engagement_id),),
        ).fetchone()

        if engagement_row is None:
            raise ValueError(
                "Quote engagement does not exist."
            )

        if (
            engagement_row["client_organization_id"]
            != str(quote.client_organization_id)
        ):
            raise ValueError(
                "Quote client organization does not match "
                "the engagement client organization."
            )

        self.connection.execute(
            """
            INSERT INTO quotes (
                id,
                client_organization_id,
                engagement_id,
                quote_number,
                status,
                issue_date,
                expiration_date,
                bill_to_name,
                bill_to_email,
                bill_to_address,
                subtotal,
                tax_amount,
                total,
                notes,
                terms,
                sent_at,
                accepted_at,
                declined_at,
                created_at,
                updated_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                str(quote.id),
                str(quote.client_organization_id),
                str(quote.engagement_id),
                quote.quote_number,
                quote.status.value,
                (
                    quote.issue_date.isoformat()
                    if quote.issue_date
                    else None
                ),
                (
                    quote.expiration_date.isoformat()
                    if quote.expiration_date
                    else None
                ),
                quote.bill_to_name,
                quote.bill_to_email,
                quote.bill_to_address,
                str(quote.subtotal),
                str(quote.tax_amount),
                str(quote.total),
                quote.notes,
                quote.terms,
                (
                    quote.sent_at.isoformat()
                    if quote.sent_at
                    else None
                ),
                (
                    quote.accepted_at.isoformat()
                    if quote.accepted_at
                    else None
                ),
                (
                    quote.declined_at.isoformat()
                    if quote.declined_at
                    else None
                ),
                quote.created_at.isoformat(),
                quote.updated_at.isoformat(),
            ),
        )

        for line in quote.line_items:
            self.connection.execute(
                """
                INSERT INTO quote_lines (
                    id,
                    quote_id,
                    description,
                    quantity,
                    unit_rate,
                    amount
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(line.id),
                    str(quote.id),
                    line.description,
                    str(line.quantity),
                    str(line.unit_rate),
                    str(line.amount),
                ),
            )

    def get_for_client(
        self,
        quote_id: UUID,
        client_organization_id: UUID,
    ) -> Quote | None:
        row = self.connection.execute(
            """
            SELECT *
            FROM quotes
            WHERE id = ?
              AND client_organization_id = ?
            """,
            (
                str(quote_id),
                str(client_organization_id),
            ),
        ).fetchone()

        if row is None:
            return None

        line_rows = self.connection.execute(
            """
            SELECT *
            FROM quote_lines
            WHERE quote_id = ?
            ORDER BY rowid
            """,
            (str(quote_id),),
        ).fetchall()

        line_items = [
            QuoteLine(
                id=UUID(line["id"]),
                description=line["description"],
                quantity=Decimal(line["quantity"]),
                unit_rate=Decimal(line["unit_rate"]),
                amount=Decimal(line["amount"]),
            )
            for line in line_rows
        ]

        return Quote(
            id=UUID(row["id"]),
            client_organization_id=UUID(
                row["client_organization_id"]
            ),
            engagement_id=UUID(
                row["engagement_id"]
            ),
            quote_number=row["quote_number"],
            status=QuoteStatus(row["status"]),
            issue_date=(
                date.fromisoformat(row["issue_date"])
                if row["issue_date"]
                else None
            ),
            expiration_date=(
                date.fromisoformat(row["expiration_date"])
                if row["expiration_date"]
                else None
            ),
            bill_to_name=row["bill_to_name"],
            bill_to_email=row["bill_to_email"],
            bill_to_address=row["bill_to_address"],
            line_items=line_items,
            subtotal=Decimal(row["subtotal"]),
            tax_amount=Decimal(row["tax_amount"]),
            total=Decimal(row["total"]),
            notes=row["notes"],
            terms=row["terms"],
            sent_at=(
                datetime.fromisoformat(row["sent_at"])
                if row["sent_at"]
                else None
            ),
            accepted_at=(
                datetime.fromisoformat(
                    row["accepted_at"]
                )
                if row["accepted_at"]
                else None
            ),
            declined_at=(
                datetime.fromisoformat(
                    row["declined_at"]
                )
                if row["declined_at"]
                else None
            ),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def update(
        self,
        quote: Quote,
    ) -> None:
        result = self.connection.execute(
            """
            UPDATE quotes
            SET
                status = ?,
                subtotal = ?,
                tax_amount = ?,
                total = ?,
                notes = ?,
                terms = ?,
                sent_at = ?,
                accepted_at = ?,
                declined_at = ?,
                updated_at = ?
            WHERE id = ?
              AND client_organization_id = ?
            """,
            (
                quote.status.value,
                str(quote.subtotal),
                str(quote.tax_amount),
                str(quote.total),
                quote.notes,
                quote.terms,
                (
                    quote.sent_at.isoformat()
                    if quote.sent_at
                    else None
                ),
                (
                    quote.accepted_at.isoformat()
                    if quote.accepted_at
                    else None
                ),
                (
                    quote.declined_at.isoformat()
                    if quote.declined_at
                    else None
                ),
                quote.updated_at.isoformat(),
                str(quote.id),
                str(quote.client_organization_id),
            ),
        )

        if result.rowcount == 0:
            raise ValueError(
                "Quote does not exist."
            )

    def assign_public_token_hash(
        self,
        quote_id: UUID,
        public_token_hash: str,
    ) -> None:
        result = self.connection.execute(
            """
            UPDATE quotes
            SET public_token_hash = ?
            WHERE id = ?
            """,
            (
                public_token_hash,
                str(quote_id),
            ),
        )

        if result.rowcount == 0:
            raise ValueError(
                "Quote does not exist."
            )

    def get_by_public_token_hash(
        self,
        public_token_hash: str,
    ) -> Quote | None:
        row = self.connection.execute(
            """
            SELECT
                id,
                client_organization_id
            FROM quotes
            WHERE public_token_hash = ?
            """,
            (public_token_hash,),
        ).fetchone()

        if row is None:
            return None

        return self.get_for_client(
            quote_id=UUID(row["id"]),
            client_organization_id=UUID(
                row["client_organization_id"]
            ),
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
                source_quote_id,
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
                terms,
                sent_at,
                created_at,
                updated_at
            )
            VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
            """,
            (
                str(invoice.id),
                str(invoice.client_organization_id),
                (
                    str(invoice.source_quote_id)
                    if invoice.source_quote_id
                    else None
                ),
                invoice.invoice_number,
                invoice.status.value,
                (
                    invoice.issue_date.isoformat()
                    if invoice.issue_date
                    else None
                ),
                (
                    invoice.due_date.isoformat()
                    if invoice.due_date
                    else None
                ),
                invoice.bill_to_name,
                invoice.bill_to_email,
                invoice.bill_to_address,
                str(invoice.subtotal),
                str(invoice.tax_amount),
                str(invoice.total),
                str(invoice.amount_paid),
                str(invoice.balance_due),
                invoice.notes,
                invoice.terms,
                (
                    invoice.sent_at.isoformat()
                    if invoice.sent_at
                    else None
                ),
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
            source_quote_id=(
                UUID(row["source_quote_id"])
                if row["source_quote_id"]
                else None
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
            terms=row["terms"],
            sent_at=(
                datetime.fromisoformat(
                    row["sent_at"]
                )
                if row["sent_at"]
                else None
            ),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


    def update(
        self,
        invoice: Invoice,
    ) -> None:
        result = self.connection.execute(
            """
            UPDATE invoices
            SET
                status = ?,
                amount_paid = ?,
                balance_due = ?,
                sent_at = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                invoice.status.value,
                str(invoice.amount_paid),
                str(invoice.balance_due),
                (
                    invoice.sent_at.isoformat()
                    if invoice.sent_at
                    else None
                ),
                invoice.updated_at.isoformat(),
                str(invoice.id),
            ),
        )

        if result.rowcount == 0:
            raise ValueError(
                "Invoice does not exist."
            )


    def list_for_engagement(
        self,
        engagement_id: UUID,
    ) -> list[Invoice]:
        rows = self.connection.execute(
            """
            SELECT DISTINCT i.id
            FROM invoices AS i
            JOIN invoice_lines AS il
              ON il.invoice_id = i.id
            WHERE il.engagement_id = ?
            ORDER BY i.created_at DESC
            """,
            (str(engagement_id),),
        ).fetchall()

        invoices: list[Invoice] = []

        for row in rows:
            invoice = self.get(
                UUID(row["id"])
            )

            if invoice is not None:
                invoices.append(invoice)

        return invoices



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
                    workstream,
                    friction,
                    operational_note,
                    status,
                    invoice_id,
                    created_at
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?
                )
                """,
                (
                    str(entry.id),
                    str(entry.engagement_id),
                    entry.work_date.isoformat(),
                    entry.description,
                    str(entry.hours),
                    (
                        entry.workstream.value
                        if entry.workstream
                        else None
                    ),
                    (
                        entry.friction.value
                        if entry.friction
                        else None
                    ),
                    entry.operational_note,
                    entry.status.value,
                    (
                        str(entry.invoice_id)
                        if entry.invoice_id
                        else None
                    ),
                    entry.created_at.isoformat(),
                ),
            )

    def update_draft(
        self,
        entry: TimeEntry,
    ) -> None:
        if (
            entry.status
            != TimeEntryStatus.DRAFT
        ):
            raise ValueError(
                "Only draft time entries "
                "can be edited."
            )

        cursor = self.connection.execute(
            """
            UPDATE time_entries
            SET
                work_date = ?,
                description = ?,
                hours = ?,
                workstream = ?,
                friction = ?,
                operational_note = ?
            WHERE id = ?
              AND status = ?
            """,
            (
                entry.work_date.isoformat(),
                entry.description,
                str(entry.hours),
                (
                    entry.workstream.value
                    if entry.workstream
                    else None
                ),
                (
                    entry.friction.value
                    if entry.friction
                    else None
                ),
                entry.operational_note,
                str(entry.id),
                TimeEntryStatus.DRAFT.value,
            ),
        )

        if cursor.rowcount != 1:
            raise ValueError(
                "Only draft time entries "
                "can be edited."
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
            workstream=(
                TimeEntryWorkstream(
                    row["workstream"]
                )
                if row["workstream"]
                else None
            ),
            friction=(
                TimeEntryFriction(
                    row["friction"]
                )
                if row["friction"]
                else None
            ),
            operational_note=(
                row["operational_note"]
            ),
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



    def list_for_engagement(
        self,
        engagement_id: UUID,
    ) -> list[TimeEntry]:
        rows = self.connection.execute(
            """
            SELECT *
            FROM time_entries
            WHERE engagement_id = ?
            ORDER BY
                work_date DESC,
                created_at DESC
            """,
            (
                str(
                    engagement_id
                ),
            ),
        ).fetchall()

        return [
            TimeEntry(
                id=UUID(
                    row["id"]
                ),
                engagement_id=UUID(
                    row[
                        "engagement_id"
                    ]
                ),
                work_date=(
                    date.fromisoformat(
                        row[
                            "work_date"
                        ]
                    )
                ),
                description=(
                    row["description"]
                ),
                hours=Decimal(
                    row["hours"]
                ),
                workstream=(
                    TimeEntryWorkstream(
                        row["workstream"]
                    )
                    if row["workstream"]
                    else None
                ),
                friction=(
                    TimeEntryFriction(
                        row["friction"]
                    )
                    if row["friction"]
                    else None
                ),
                operational_note=(
                    row["operational_note"]
                ),
                status=(
                    TimeEntryStatus(
                        row["status"]
                    )
                ),
                invoice_id=(
                    UUID(
                        row[
                            "invoice_id"
                        ]
                    )
                    if row[
                        "invoice_id"
                    ]
                    else None
                ),
                created_at=(
                    row["created_at"]
                ),
            )
            for row in rows
        ]



class SQLiteEngagementBillingTermsRepository:
    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self.connection = connection

    def add(
        self,
        terms: EngagementBillingTerms,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO engagement_billing_terms (
                id,
                engagement_id,
                billing_type,
                billing_cadence,
                hourly_rate,
                expected_hours_min,
                expected_hours_max,
                payment_terms_days,
                effective_from,
                effective_to,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(terms.id),
                str(terms.engagement_id),
                terms.billing_type.value,
                terms.billing_cadence.value,
                (
                    str(terms.hourly_rate)
                    if terms.hourly_rate
                    is not None
                    else None
                ),
                (
                    str(
                        terms.expected_hours_min
                    )
                    if terms.expected_hours_min
                    is not None
                    else None
                ),
                (
                    str(
                        terms.expected_hours_max
                    )
                    if terms.expected_hours_max
                    is not None
                    else None
                ),
                terms.payment_terms_days,
                terms.effective_from.isoformat(),
                (
                    terms.effective_to.isoformat()
                    if terms.effective_to
                    else None
                ),
                terms.created_at.isoformat(),
            ),
        )

    def update_effective_to(
        self,
        terms: EngagementBillingTerms,
    ) -> None:
        self.connection.execute(
            """
            UPDATE engagement_billing_terms
            SET effective_to = ?
            WHERE id = ?
            """,
            (
                (
                    terms.effective_to
                    .isoformat()
                    if terms.effective_to
                    else None
                ),
                str(terms.id),
            ),
        )


    def list_for_engagement(
        self,
        engagement_id: UUID,
    ) -> list[EngagementBillingTerms]:
        rows = self.connection.execute(
            """
            SELECT *
            FROM engagement_billing_terms
            WHERE engagement_id = ?
            ORDER BY effective_from
            """,
            (str(engagement_id),),
        ).fetchall()

        return [
            EngagementBillingTerms(
                id=UUID(row["id"]),
                engagement_id=UUID(
                    row["engagement_id"]
                ),
                billing_type=BillingType(
                    row["billing_type"]
                ),
                billing_cadence=BillingCadence(
                    row["billing_cadence"]
                ),
                hourly_rate=(
                    Decimal(
                        row["hourly_rate"]
                    )
                    if row["hourly_rate"]
                    is not None
                    else None
                ),
                expected_hours_min=(
                    Decimal(
                        row[
                            "expected_hours_min"
                        ]
                    )
                    if row[
                        "expected_hours_min"
                    ]
                    is not None
                    else None
                ),
                expected_hours_max=(
                    Decimal(
                        row[
                            "expected_hours_max"
                        ]
                    )
                    if row[
                        "expected_hours_max"
                    ]
                    is not None
                    else None
                ),
                payment_terms_days=row[
                    "payment_terms_days"
                ],
                effective_from=date.fromisoformat(
                    row["effective_from"]
                ),
                effective_to=(
                    date.fromisoformat(
                        row["effective_to"]
                    )
                    if row["effective_to"]
                    else None
                ),
                created_at=datetime.fromisoformat(
                    row["created_at"]
                ),
            )
            for row in rows
        ]


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



class SQLiteUserRepository:
    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self.connection = connection

    def add(
        self,
        user: User,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO users (
                id,
                email,
                display_name,
                password_hash,
                status,
                must_change_password,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(user.id),
                user.email.strip().lower(),
                user.display_name.strip(),
                user.password_hash,
                user.status.value,
                int(user.must_change_password),
                user.created_at.isoformat(),
                user.updated_at.isoformat(),
            ),
        )

    def get(
        self,
        user_id: UUID,
    ) -> User | None:
        row = self.connection.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (str(user_id),),
        ).fetchone()

        if row is None:
            return None

        return self._from_row(row)

    def get_by_email(
        self,
        email: str,
    ) -> User | None:
        row = self.connection.execute(
            """
            SELECT *
            FROM users
            WHERE lower(email) = lower(?)
            """,
            (email.strip(),),
        ).fetchone()

        if row is None:
            return None

        return self._from_row(row)

    def update_password(
        self,
        *,
        user_id: UUID,
        password_hash: str,
        must_change_password: bool,
    ) -> None:
        result = self.connection.execute(
            """
            UPDATE users
            SET
                password_hash = ?,
                must_change_password = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                password_hash,
                int(must_change_password),
                datetime.now().astimezone().isoformat(),
                str(user_id),
            ),
        )

        if result.rowcount == 0:
            raise ValueError(
                "User does not exist."
            )


    @staticmethod
    def _from_row(
        row: sqlite3.Row,
    ) -> User:
        return User(
            id=UUID(row["id"]),
            email=row["email"],
            display_name=row["display_name"],
            password_hash=row["password_hash"],
            status=UserStatus(row["status"]),
            must_change_password=bool(
                row["must_change_password"]
            ),
            created_at=datetime.fromisoformat(
                row["created_at"]
            ),
            updated_at=datetime.fromisoformat(
                row["updated_at"]
            ),
        )


class SQLiteOrganizationMembershipRepository:
    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self.connection = connection

    def add(
        self,
        membership: OrganizationMembership,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO organization_memberships (
                id,
                user_id,
                organization_id,
                role,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(membership.id),
                str(membership.user_id),
                str(membership.organization_id),
                membership.role.value,
                membership.created_at.isoformat(),
            ),
        )

    def get_for_user_and_organization(
        self,
        *,
        user_id: UUID,
        organization_id: UUID,
    ) -> OrganizationMembership | None:
        row = self.connection.execute(
            """
            SELECT *
            FROM organization_memberships
            WHERE user_id = ?
              AND organization_id = ?
            """,
            (
                str(user_id),
                str(organization_id),
            ),
        ).fetchone()

        if row is None:
            return None

        return self._from_row(row)

    def list_for_user(
        self,
        user_id: UUID,
    ) -> list[OrganizationMembership]:
        rows = self.connection.execute(
            """
            SELECT *
            FROM organization_memberships
            WHERE user_id = ?
            ORDER BY created_at
            """,
            (str(user_id),),
        ).fetchall()

        return [
            self._from_row(row)
            for row in rows
        ]

    @staticmethod
    def _from_row(
        row: sqlite3.Row,
    ) -> OrganizationMembership:
        return OrganizationMembership(
            id=UUID(row["id"]),
            user_id=UUID(row["user_id"]),
            organization_id=UUID(
                row["organization_id"]
            ),
            role=MembershipRole(row["role"]),
            created_at=datetime.fromisoformat(
                row["created_at"]
            ),
        )


class SQLiteAuthSessionRepository:
    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self.connection = connection

    def add(
        self,
        session: AuthSession,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO auth_sessions (
                id,
                user_id,
                token_hash,
                expires_at,
                created_at,
                revoked_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(session.id),
                str(session.user_id),
                session.token_hash,
                session.expires_at.isoformat(),
                session.created_at.isoformat(),
                (
                    session.revoked_at.isoformat()
                    if session.revoked_at
                    else None
                ),
            ),
        )

    def get_by_token_hash(
        self,
        token_hash: str,
    ) -> AuthSession | None:
        row = self.connection.execute(
            """
            SELECT *
            FROM auth_sessions
            WHERE token_hash = ?
            LIMIT 1
            """,
            (token_hash,),
        ).fetchone()

        if row is None:
            return None

        return self._from_row(row)

    def revoke(
        self,
        session_id: UUID,
        *,
        revoked_at: datetime,
    ) -> None:
        result = self.connection.execute(
            """
            UPDATE auth_sessions
            SET revoked_at = ?
            WHERE id = ?
            """,
            (
                revoked_at.isoformat(),
                str(session_id),
            ),
        )

        if result.rowcount == 0:
            raise ValueError(
                "Auth session does not exist."
            )

    def revoke_all_for_user(
        self,
        user_id: UUID,
        *,
        revoked_at: datetime,
    ) -> None:
        self.connection.execute(
            """
            UPDATE auth_sessions
            SET revoked_at = ?
            WHERE user_id = ?
              AND revoked_at IS NULL
            """,
            (
                revoked_at.isoformat(),
                str(user_id),
            ),
        )


    @staticmethod
    def _from_row(
        row: sqlite3.Row,
    ) -> AuthSession:
        return AuthSession(
            id=UUID(row["id"]),
            user_id=UUID(row["user_id"]),
            token_hash=row["token_hash"],
            expires_at=datetime.fromisoformat(
                row["expires_at"]
            ),
            created_at=datetime.fromisoformat(
                row["created_at"]
            ),
            revoked_at=(
                datetime.fromisoformat(
                    row["revoked_at"]
                )
                if row["revoked_at"]
                else None
            ),
        )


class SQLiteAuditEventRepository:
    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self.connection = connection

    def add(
        self,
        event: AuditEvent,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO audit_events (
                id,
                actor_user_id,
                organization_id,
                action,
                resource_type,
                resource_id,
                metadata_json,
                occurred_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(event.id),
                (
                    str(event.actor_user_id)
                    if event.actor_user_id
                    else None
                ),
                (
                    str(event.organization_id)
                    if event.organization_id
                    else None
                ),
                event.action,
                event.resource_type,
                (
                    str(event.resource_id)
                    if event.resource_id
                    else None
                ),
                event.metadata_json,
                event.occurred_at.isoformat(),
            ),
        )

    def list_for_organization(
        self,
        organization_id: UUID,
    ) -> list[AuditEvent]:
        rows = self.connection.execute(
            """
            SELECT *
            FROM audit_events
            WHERE organization_id = ?
            ORDER BY occurred_at
            """,
            (str(organization_id),),
        ).fetchall()

        return [
            self._from_row(row)
            for row in rows
        ]

    @staticmethod
    def _from_row(
        row: sqlite3.Row,
    ) -> AuditEvent:
        return AuditEvent(
            id=UUID(row["id"]),
            actor_user_id=(
                UUID(row["actor_user_id"])
                if row["actor_user_id"]
                else None
            ),
            organization_id=(
                UUID(row["organization_id"])
                if row["organization_id"]
                else None
            ),
            action=row["action"],
            resource_type=row["resource_type"],
            resource_id=(
                UUID(row["resource_id"])
                if row["resource_id"]
                else None
            ),
            metadata_json=row["metadata_json"],
            occurred_at=datetime.fromisoformat(
                row["occurred_at"]
            ),
        )

