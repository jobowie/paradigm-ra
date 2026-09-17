import sqlite3
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from ra_platform.api.dependencies import (
    get_database_connection,
)
from ra_platform.persistence.sqlite_repositories import (
    SQLiteQuoteRepository,
)


router = APIRouter(
    prefix="/quotes",
    tags=["quotes"],
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