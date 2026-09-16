from typing import Protocol

from .models import Invoice, TimeEntry


class InvoiceRepository(Protocol):
    def add(
        self,
        invoice: Invoice,
    ) -> None:
        ...


class TimeEntryRepository(Protocol):
    def update_many(
        self,
        time_entries: list[TimeEntry],
    ) -> None:
        ...


class BillingUnitOfWork(Protocol):
    invoices: InvoiceRepository
    time_entries: TimeEntryRepository

    def __enter__(self) -> "BillingUnitOfWork":
        ...

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
