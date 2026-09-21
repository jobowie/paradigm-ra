import sqlite3

from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest

from ra_platform.identity.models import (
    AuthSession,
    MembershipRole,
    OrganizationMembership,
    User,
    UserStatus,
)
from ra_platform.identity.service import (
    AuthenticationError,
    SessionError,
    authenticate_and_create_session,
    resolve_authenticated_session,
    revoke_authenticated_session,
)
from ra_platform.organizations.models import (
    Organization,
    OrganizationType,
)
from ra_platform.persistence.sqlite import (
    initialize_database,
)
from ra_platform.persistence.sqlite_repositories import (
    SQLiteAuthSessionRepository,
    SQLiteOrganizationMembershipRepository,
    SQLiteOrganizationRepository,
    SQLiteUserRepository,
)
from ra_platform.security.auth import (
    generate_session_token,
    hash_password,
    hash_session_token,
    verify_password,
)


def make_context():
    connection = sqlite3.connect(
        ":memory:"
    )
    connection.row_factory = sqlite3.Row

    initialize_database(connection)

    organizations = (
        SQLiteOrganizationRepository(
            connection
        )
    )
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

    organization = Organization(
        name="Paradigm Ra",
        type=OrganizationType.PARADIGM_RA,
    )

    organizations.add(
        organization
    )

    user = User(
        email="executive@paradigmra.tech",
        display_name="Executive",
        password_hash=hash_password(
            "correct-password"
        ),
    )

    users.add(user)

    membership = OrganizationMembership(
        user_id=user.id,
        organization_id=organization.id,
        role=(
            MembershipRole.PARADIGM_RA_EXECUTIVE
        ),
    )

    memberships.add(
        membership
    )

    connection.commit()

    return (
        connection,
        user,
        organization,
        users,
        memberships,
        sessions,
    )


def test_authenticate_creates_resolvable_session():
    (
        _,
        user,
        organization,
        users,
        memberships,
        sessions,
    ) = make_context()

    result = authenticate_and_create_session(
        email="EXECUTIVE@PARADIGMRA.TECH",
        password="correct-password",
        users=users,
        memberships=memberships,
        sessions=sessions,
    )

    assert result.user.id == user.id

    assert len(
        result.memberships
    ) == 1

    assert (
        result.memberships[0]
        .organization_id
        == organization.id
    )

    assert (
        result.raw_token
        != result.session.token_hash
    )

    principal = resolve_authenticated_session(
        raw_token=result.raw_token,
        users=users,
        memberships=memberships,
        sessions=sessions,
    )

    assert principal.user.id == user.id
    assert len(principal.memberships) == 1


def test_wrong_password_is_rejected():
    (
        _,
        _,
        _,
        users,
        memberships,
        sessions,
    ) = make_context()

    with pytest.raises(
        AuthenticationError
    ):
        authenticate_and_create_session(
            email=(
                "executive@paradigmra.tech"
            ),
            password="wrong-password",
            users=users,
            memberships=memberships,
            sessions=sessions,
        )


def test_disabled_user_cannot_authenticate():
    (
        connection,
        user,
        _,
        users,
        memberships,
        sessions,
    ) = make_context()

    connection.execute(
        """
        UPDATE users
        SET status = ?
        WHERE id = ?
        """,
        (
            UserStatus.DISABLED.value,
            str(user.id),
        ),
    )
    connection.commit()

    with pytest.raises(
        AuthenticationError
    ):
        authenticate_and_create_session(
            email=user.email,
            password="correct-password",
            users=users,
            memberships=memberships,
            sessions=sessions,
        )


def test_expired_session_is_rejected():
    (
        connection,
        user,
        _,
        users,
        memberships,
        sessions,
    ) = make_context()

    raw_token = generate_session_token()

    session = AuthSession(
        user_id=user.id,
        token_hash=hash_session_token(
            raw_token
        ),
        expires_at=(
            datetime.now(timezone.utc)
            - timedelta(minutes=1)
        ),
    )

    sessions.add(session)
    connection.commit()

    with pytest.raises(
        SessionError
    ):
        resolve_authenticated_session(
            raw_token=raw_token,
            users=users,
            memberships=memberships,
            sessions=sessions,
        )


def test_revoked_session_is_rejected():
    (
        connection,
        user,
        _,
        users,
        memberships,
        sessions,
    ) = make_context()

    result = authenticate_and_create_session(
        email=user.email,
        password="correct-password",
        users=users,
        memberships=memberships,
        sessions=sessions,
    )
    connection.commit()

    revoke_authenticated_session(
        raw_token=result.raw_token,
        sessions=sessions,
    )
    connection.commit()

    with pytest.raises(
        SessionError
    ):
        resolve_authenticated_session(
            raw_token=result.raw_token,
            users=users,
            memberships=memberships,
            sessions=sessions,
        )


def test_password_change_clears_temporary_flag_and_revokes_sessions():
    (
        connection,
        user,
        _,
        users,
        memberships,
        sessions,
    ) = make_context()

    connection.execute(
        """
        UPDATE users
        SET must_change_password = 1
        WHERE id = ?
        """,
        (str(user.id),),
    )
    connection.commit()

    result = authenticate_and_create_session(
        email=user.email,
        password="correct-password",
        users=users,
        memberships=memberships,
        sessions=sessions,
    )
    connection.commit()

    principal = resolve_authenticated_session(
        raw_token=result.raw_token,
        users=users,
        memberships=memberships,
        sessions=sessions,
    )

    from ra_platform.identity.service import (
        change_password,
    )

    change_password(
        principal=principal,
        current_password="correct-password",
        new_password="new-secure-password",
        users=users,
        sessions=sessions,
    )
    connection.commit()

    updated = users.get(user.id)

    assert updated is not None

    assert (
        updated.must_change_password
        is False
    )

    assert verify_password(
        "new-secure-password",
        updated.password_hash,
    )

    with pytest.raises(
        SessionError
    ):
        resolve_authenticated_session(
            raw_token=result.raw_token,
            users=users,
            memberships=memberships,
            sessions=sessions,
        )
