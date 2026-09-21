import sqlite3

from datetime import datetime
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
)
from pydantic import BaseModel, Field

from ra_platform.api.auth import (
    extract_bearer_token,
    get_current_principal,
)
from ra_platform.api.dependencies import (
    get_database_connection,
)
from ra_platform.identity.models import (
    AuditEvent,
    OrganizationMembership,
    User,
)
from ra_platform.identity.service import (
    AuthenticatedPrincipal,
    AuthenticationError,
    authenticate_and_create_session,
    revoke_authenticated_session,
)
from ra_platform.persistence.sqlite_repositories import (
    SQLiteAuditEventRepository,
    SQLiteAuthSessionRepository,
    SQLiteOrganizationMembershipRepository,
    SQLiteUserRepository,
)


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=1)


class UserResponse(BaseModel):
    id: UUID
    email: str
    display_name: str
    status: str
    must_change_password: bool


class MembershipResponse(BaseModel):
    organization_id: UUID
    role: str


class LoginResponse(BaseModel):
    session_token: str
    expires_at: datetime

    user: UserResponse
    memberships: list[MembershipResponse]


class CurrentUserResponse(BaseModel):
    user: UserResponse
    memberships: list[MembershipResponse]


def build_user_response(
    user: User,
) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        status=user.status.value,
        must_change_password=(
            user.must_change_password
        ),
    )


def build_membership_response(
    membership: OrganizationMembership,
) -> MembershipResponse:
    return MembershipResponse(
        organization_id=(
            membership.organization_id
        ),
        role=membership.role.value,
    )


def build_current_user_response(
    principal: AuthenticatedPrincipal,
) -> CurrentUserResponse:
    return CurrentUserResponse(
        user=build_user_response(
            principal.user
        ),
        memberships=[
            build_membership_response(
                membership
            )
            for membership
            in principal.memberships
        ],
    )


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    request: LoginRequest,
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    users = SQLiteUserRepository(
        connection
    )
    memberships = (
        SQLiteOrganizationMembershipRepository(
            connection
        )
    )
    sessions = SQLiteAuthSessionRepository(
        connection
    )
    audit = SQLiteAuditEventRepository(
        connection
    )

    try:
        result = authenticate_and_create_session(
            email=request.email,
            password=request.password,
            users=users,
            memberships=memberships,
            sessions=sessions,
        )

    except AuthenticationError as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials.",
        ) from exc

    audit.add(
        AuditEvent(
            actor_user_id=result.user.id,
            organization_id=None,
            action="auth.login",
            resource_type="user",
            resource_id=result.user.id,
        )
    )

    connection.commit()

    return LoginResponse(
        session_token=result.raw_token,
        expires_at=result.session.expires_at,
        user=build_user_response(
            result.user
        ),
        memberships=[
            build_membership_response(
                membership
            )
            for membership
            in result.memberships
        ],
    )


@router.get(
    "/me",
    response_model=CurrentUserResponse,
)
def me(
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
):
    return build_current_user_response(
        principal
    )


@router.post("/logout")
def logout(
    authorization: str | None = Header(
        default=None
    ),
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    raw_token = extract_bearer_token(
        authorization
    )

    sessions = SQLiteAuthSessionRepository(
        connection
    )
    audit = SQLiteAuditEventRepository(
        connection
    )

    revoke_authenticated_session(
        raw_token=raw_token,
        sessions=sessions,
    )

    audit.add(
        AuditEvent(
            actor_user_id=principal.user.id,
            organization_id=None,
            action="auth.logout",
            resource_type="user",
            resource_id=principal.user.id,
        )
    )

    connection.commit()

    return {
        "logged_out": True,
    }


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(
        min_length=1
    )
    new_password: str = Field(
        min_length=12
    )


@router.post("/change-password")
def change_current_password(
    request: ChangePasswordRequest,
    principal: AuthenticatedPrincipal = Depends(
        get_current_principal
    ),
    connection: sqlite3.Connection = Depends(
        get_database_connection
    ),
):
    from ra_platform.identity.service import (
        PasswordChangeError,
        change_password,
    )

    users = SQLiteUserRepository(
        connection
    )

    sessions = SQLiteAuthSessionRepository(
        connection
    )

    audit = SQLiteAuditEventRepository(
        connection
    )

    try:
        change_password(
            principal=principal,
            current_password=(
                request.current_password
            ),
            new_password=(
                request.new_password
            ),
            users=users,
            sessions=sessions,
        )

    except PasswordChangeError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    audit.add(
        AuditEvent(
            actor_user_id=principal.user.id,
            organization_id=None,
            action="identity.password_changed",
            resource_type="user",
            resource_id=principal.user.id,
        )
    )

    connection.commit()

    return {
        "password_changed": True,
        "session_revoked": True,
    }
