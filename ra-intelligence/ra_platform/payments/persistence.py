import sqlite3

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ra_platform.billing.models import (
    Invoice,
    Payment,
    PaymentMethod,
    PaymentStatus,
)
from ra_platform.persistence.sqlite_repositories import (
    SQLiteInvoiceRepository,
)


class SQLitePaymentPersistence:
    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self.connection = connection

        self.invoices = SQLiteInvoiceRepository(
            connection
        )


    def get_invoices_for_quote(
        self,
        quote_id: UUID,
    ) -> list[Invoice]:
        rows = self.connection.execute(
            """
            SELECT id
            FROM invoices
            WHERE source_quote_id = ?
            ORDER BY created_at
            """,
            (str(quote_id),),
        ).fetchall()

        invoices: list[Invoice] = []

        for row in rows:
            invoice = self.invoices.get(
                UUID(row["id"])
            )

            if invoice is not None:
                invoices.append(invoice)

        return invoices


    def get_deposit_invoice_for_quote(
        self,
        quote_id: UUID,
    ) -> Invoice | None:
        row = self.connection.execute(
            """
            SELECT DISTINCT i.id
            FROM invoices AS i
            JOIN invoice_lines AS il
              ON il.invoice_id = i.id
            WHERE i.source_quote_id = ?
              AND i.status != 'void'
              AND lower(il.description)
                  LIKE '%deposit%'
            ORDER BY i.created_at
            LIMIT 1
            """,
            (str(quote_id),),
        ).fetchone()

        if row is None:
            return None

        return self.invoices.get(
            UUID(row["id"])
        )


    def update_invoice(
        self,
        invoice: Invoice,
    ) -> None:
        result = self.connection.execute(
            """
            UPDATE invoices
            SET
                status = ?,
                subtotal = ?,
                tax_amount = ?,
                total = ?,
                amount_paid = ?,
                balance_due = ?,
                notes = ?,
                terms = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                invoice.status.value,
                str(invoice.subtotal),
                str(invoice.tax_amount),
                str(invoice.total),
                str(invoice.amount_paid),
                str(invoice.balance_due),
                invoice.notes,
                invoice.terms,
                invoice.updated_at.isoformat(),
                str(invoice.id),
            ),
        )

        if result.rowcount == 0:
            raise ValueError(
                "Invoice does not exist."
            )


    def add_payment(
        self,
        payment: Payment,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO payments (
                id,
                invoice_id,
                amount,
                payment_method,
                status,
                external_reference,
                received_at,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(payment.id),
                str(payment.invoice_id),
                str(payment.amount),
                payment.payment_method.value,
                payment.status.value,
                payment.external_reference,
                (
                    payment.received_at.isoformat()
                    if payment.received_at
                    else None
                ),
                payment.created_at.isoformat(),
            ),
        )


    def get_payments_for_invoice(
        self,
        invoice_id: UUID,
    ) -> list[Payment]:
        rows = self.connection.execute(
            """
            SELECT *
            FROM payments
            WHERE invoice_id = ?
            ORDER BY created_at
            """,
            (str(invoice_id),),
        ).fetchall()

        return [
            Payment(
                id=UUID(row["id"]),
                invoice_id=UUID(
                    row["invoice_id"]
                ),
                amount=Decimal(
                    row["amount"]
                ),
                payment_method=PaymentMethod(
                    row["payment_method"]
                ),
                status=PaymentStatus(
                    row["status"]
                ),
                external_reference=(
                    row["external_reference"]
                ),
                received_at=(
                    datetime.fromisoformat(
                        row["received_at"]
                    )
                    if row["received_at"]
                    else None
                ),
                created_at=datetime.fromisoformat(
                    row["created_at"]
                ),
            )
            for row in rows
        ]


    def get_payment_by_external_reference(
        self,
        external_reference: str,
    ) -> Payment | None:
        row = self.connection.execute(
            """
            SELECT *
            FROM payments
            WHERE external_reference = ?
            LIMIT 1
            """,
            (external_reference,),
        ).fetchone()

        if row is None:
            return None

        return Payment(
            id=UUID(row["id"]),
            invoice_id=UUID(
                row["invoice_id"]
            ),
            amount=Decimal(
                row["amount"]
            ),
            payment_method=PaymentMethod(
                row["payment_method"]
            ),
            status=PaymentStatus(
                row["status"]
            ),
            external_reference=(
                row["external_reference"]
            ),
            received_at=(
                datetime.fromisoformat(
                    row["received_at"]
                )
                if row["received_at"]
                else None
            ),
            created_at=datetime.fromisoformat(
                row["created_at"]
            ),
        )
