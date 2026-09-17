import sqlite3
from datetime import datetime, timezone
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from pydantic import BaseModel

from ra_platform.api.dependencies import (
    get_database_connection,
)
from ra_platform.billing.models import QuoteStatus
from ra_platform.billing.service import accept_quote
from ra_platform.persistence.sqlite_repositories import (
    SQLiteQuoteRepository,
)
from ra_platform.security.tokens import (
    hash_public_token,
)


router = APIRouter(
    prefix="/quotes",
    tags=["quotes"],
)


class PublicQuoteLineResponse(BaseModel):
    description: str
    quantity: str
    unit_rate: str
    amount: str


class PublicQuoteResponse(BaseModel):
    quote_number: str
    status: str

    issue_date: str | None
    expiration_date: str | None

    bill_to_name: str

    line_items: list[PublicQuoteLineResponse]

    subtotal: str
    tax_amount: str
    total: str

    notes: str | None
    terms: str | None

    sent_at: str | None
    accepted_at: str | None


def build_public_quote_response(
    quote,
) -> PublicQuoteResponse:
    return PublicQuoteResponse(
        quote_number=quote.quote_number,
        status=quote.status.value,
        issue_date=(
            quote.issue_date.isoformat()
            if quote.issue_date
            else None
        ),
        expiration_date=(
            quote.expiration_date.isoformat()
            if quote.expiration_date
            else None
        ),
        bill_to_name=quote.bill_to_name,
        line_items=[
            PublicQuoteLineResponse(
                description=line.description,
                quantity=str(line.quantity),
                unit_rate=str(line.unit_rate),
                amount=str(line.amount),
            )
            for line in quote.line_items
        ],
        subtotal=str(quote.subtotal),
        tax_amount=str(quote.tax_amount),
        total=str(quote.total),
        notes=quote.notes,
        terms=quote.terms,
        sent_at=(
            quote.sent_at.isoformat()
            if quote.sent_at
            else None
        ),
        accepted_at=(
            quote.accepted_at.isoformat()
            if quote.accepted_at
            else None
        ),
    )


@router.get(
    "/public/{token}",
    response_model=PublicQuoteResponse,
)
def get_public_quote(
    token: str,
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    repository = SQLiteQuoteRepository(
        connection
    )

    quote = repository.get_by_public_token_hash(
        hash_public_token(token)
    )

    if quote is None:
        raise HTTPException(
            status_code=404,
            detail="Quote not found.",
        )

    return build_public_quote_response(
        quote
    )


@router.post(
    "/public/{token}/accept",
    response_model=PublicQuoteResponse,
)
def accept_public_quote(
    token: str,
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    repository = SQLiteQuoteRepository(
        connection
    )

    quote = repository.get_by_public_token_hash(
        hash_public_token(token)
    )

    if quote is None:
        raise HTTPException(
            status_code=404,
            detail="Quote not found.",
        )

    if quote.status == QuoteStatus.ACCEPTED:
        return build_public_quote_response(
            quote
        )

    try:
        accept_quote(
            quote,
            accepted_at=datetime.now(
                timezone.utc
            ),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    repository.update(quote)
    connection.commit()

    return build_public_quote_response(
        quote
    )


@router.get("/{quote_id}")
def get_quote(
    quote_id: UUID,
    client_organization_id: UUID,
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    repository = SQLiteQuoteRepository(
        connection
    )

    quote = repository.get_for_client(
        quote_id=quote_id,
        client_organization_id=client_organization_id,
    )

    if quote is None:
        raise HTTPException(
            status_code=404,
            detail="Quote not found.",
        )

    return quote
