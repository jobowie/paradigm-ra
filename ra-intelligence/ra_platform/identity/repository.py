from datetime import datetime
from typing import Protocol
from uuid import UUID

from ra_platform.identity.models import (
    AuthSession,
    OrganizationMembership,
    User,
)


class UserRepository(Protocol):
    def get(
        self,
        user_id: UUID,
    ) -> User | None:
        ...

    def get_by_email(
        self,
        email: str,
    ) -> User | None:
        ...

    def update_password(
        self,
        *,
        user_id: UUID,
        password_hash: str,
        must_change_password: bool,
    ) -> None:
        ...


class MembershipRepository(Protocol):
    def list_for_user(
        self,
        user_id: UUID,
    ) -> list[OrganizationMembership]:
        ...


class AuthSessionRepository(Protocol):
    def add(
        self,
        session: AuthSession,
    ) -> None:
        ...

    def get_by_token_hash(
        self,
        token_hash: str,
    ) -> AuthSession | None:
        ...

    def revoke(
        self,
        session_id: UUID,
        *,
        revoked_at: datetime,
    ) -> None:
        ...

    def revoke_all_for_user(
        self,
        user_id: UUID,
        *,
        revoked_at: datetime,
    ) -> None:
        ...
