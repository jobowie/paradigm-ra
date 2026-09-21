import sqlite3

from fastapi import (
    Depends,
    Header,
    HTTPException,
)

from ra_platform.api.dependencies import (
    get_database_connection,
)
from ra_platform.identity.service import (
    AuthenticatedPrincipal,
    SessionError,
    resolve_authenticated_session,
)
from ra_platform.persistence.sqlite_repositories import (
    SQLiteAuthSessionRepository,
    SQLiteOrganizationMembershipRepository,
    SQLiteUserRepository,
)


def extract_bearer_token(
    authorization: str | None,
) -> str:
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
        )

    scheme, separator, token = (
        authorization.partition(" ")
    )

    if (
        separator != " "
        or scheme.lower() != "bearer"
        or not token.strip()
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication.",
        )

    return token.strip()


def get_current_principal(
    authorization: str | None = Header(
        default=None
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
) -> AuthenticatedPrincipal:
    raw_token = extract_bearer_token(
        authorization
    )

    try:
        return resolve_authenticated_session(
            raw_token=raw_token,
            users=SQLiteUserRepository(
                connection
            ),
            memberships=(
                SQLiteOrganizationMembershipRepository(
                    connection
                )
            ),
            sessions=SQLiteAuthSessionRepository(
                connection
            ),
        )

    except SessionError as exc:
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
        ) from exc
