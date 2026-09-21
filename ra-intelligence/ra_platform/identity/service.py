from dataclasses import dataclass, field
from datetime import datetime, timezone

from ra_platform.identity.models import (
    AuthSession,
    OrganizationMembership,
    User,
    UserStatus,
)
from ra_platform.identity.repository import (
    AuthSessionRepository,
    MembershipRepository,
    UserRepository,
)
from ra_platform.security.auth import (
    generate_session_token,
    hash_session_token,
    session_expiration,
    verify_password,
)


class AuthenticationError(Exception):
    pass


class SessionError(Exception):
    pass


@dataclass(frozen=True)
class LoginResult:
    user: User
    memberships: list[OrganizationMembership]
    session: AuthSession
    raw_token: str = field(repr=False)


@dataclass(frozen=True)
class AuthenticatedPrincipal:
    user: User
    memberships: list[OrganizationMembership]
    session: AuthSession


def authenticate_and_create_session(
    *,
    email: str,
    password: str,
    users: UserRepository,
    memberships: MembershipRepository,
    sessions: AuthSessionRepository,
    session_hours: int = 12,
) -> LoginResult:
    user = users.get_by_email(email.strip())

    if (
        user is None
        or user.status != UserStatus.ACTIVE
        or not verify_password(
            password,
            user.password_hash,
        )
    ):
        raise AuthenticationError(
            "Invalid credentials."
        )

    raw_token = generate_session_token()

    session = AuthSession(
        user_id=user.id,
        token_hash=hash_session_token(
            raw_token
        ),
        expires_at=session_expiration(
            hours=session_hours
        ),
    )

    sessions.add(session)

    return LoginResult(
        user=user,
        memberships=memberships.list_for_user(
            user.id
        ),
        session=session,
        raw_token=raw_token,
    )


def resolve_authenticated_session(
    *,
    raw_token: str,
    users: UserRepository,
    memberships: MembershipRepository,
    sessions: AuthSessionRepository,
    now: datetime | None = None,
) -> AuthenticatedPrincipal:
    if not raw_token:
        raise SessionError(
            "Invalid session."
        )

    session = sessions.get_by_token_hash(
        hash_session_token(raw_token)
    )

    if session is None:
        raise SessionError(
            "Invalid session."
        )

    current_time = (
        now
        or datetime.now(timezone.utc)
    )

    if session.revoked_at is not None:
        raise SessionError(
            "Session has been revoked."
        )

    if session.expires_at <= current_time:
        raise SessionError(
            "Session has expired."
        )

    user = users.get(
        session.user_id
    )

    if (
        user is None
        or user.status != UserStatus.ACTIVE
    ):
        raise SessionError(
            "Session user is unavailable."
        )

    return AuthenticatedPrincipal(
        user=user,
        memberships=memberships.list_for_user(
            user.id
        ),
        session=session,
    )


def revoke_authenticated_session(
    *,
    raw_token: str,
    sessions: AuthSessionRepository,
    revoked_at: datetime | None = None,
) -> None:
    session = sessions.get_by_token_hash(
        hash_session_token(raw_token)
    )

    if session is None:
        return

    if session.revoked_at is not None:
        return

    sessions.revoke(
        session.id,
        revoked_at=(
            revoked_at
            or datetime.now(
                timezone.utc
            )
        ),
    )
