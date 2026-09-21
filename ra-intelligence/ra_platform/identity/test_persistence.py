import sqlite3

from datetime import datetime, timezone

from ra_platform.identity.models import (
    AuditEvent,
    AuthSession,
    MembershipRole,
    OrganizationMembership,
    User,
)
from ra_platform.organizations.models import (
    Organization,
    OrganizationType,
)
from ra_platform.persistence.sqlite import (
    initialize_database,
)
from ra_platform.persistence.sqlite_repositories import (
    SQLiteAuditEventRepository,
    SQLiteAuthSessionRepository,
    SQLiteOrganizationMembershipRepository,
    SQLiteOrganizationRepository,
    SQLiteUserRepository,
)
from ra_platform.security.auth import (
    generate_session_token,
    hash_password,
    hash_session_token,
    session_expiration,
)


def make_connection():
    connection = sqlite3.connect(
        ":memory:"
    )
    connection.row_factory = sqlite3.Row

    initialize_database(connection)

    return connection


def test_user_round_trip_and_email_lookup():
    connection = make_connection()

    repository = SQLiteUserRepository(
        connection
    )

    user = User(
        email="CEO@ParadigmRa.Tech",
        display_name="Paradigm Ra CEO",
        password_hash=hash_password(
            "temporary-test-password"
        ),
    )

    repository.add(user)
    connection.commit()

    loaded = repository.get(
        user.id
    )

    by_email = repository.get_by_email(
        "ceo@paradigmra.tech"
    )

    assert loaded is not None
    assert loaded.id == user.id
    assert loaded.email == (
        "ceo@paradigmra.tech"
    )

    assert by_email is not None
    assert by_email.id == user.id


def test_membership_is_scoped_to_organization():
    connection = make_connection()

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

    paradigm_ra = Organization(
        name="Paradigm Ra",
        type=OrganizationType.PARADIGM_RA,
    )

    brewbird = Organization(
        name="BrewBird Coffee",
        type=OrganizationType.CLIENT,
    )

    organizations.add(paradigm_ra)
    organizations.add(brewbird)

    user = User(
        email="executive@paradigmra.tech",
        display_name="Executive",
        password_hash=hash_password(
            "test-password"
        ),
    )

    users.add(user)

    membership = OrganizationMembership(
        user_id=user.id,
        organization_id=paradigm_ra.id,
        role=(
            MembershipRole.PARADIGM_RA_EXECUTIVE
        ),
    )

    memberships.add(membership)
    connection.commit()

    allowed = (
        memberships
        .get_for_user_and_organization(
            user_id=user.id,
            organization_id=paradigm_ra.id,
        )
    )

    not_allowed = (
        memberships
        .get_for_user_and_organization(
            user_id=user.id,
            organization_id=brewbird.id,
        )
    )

    assert allowed is not None
    assert allowed.role == (
        MembershipRole.PARADIGM_RA_EXECUTIVE
    )

    assert not_allowed is None


def test_session_round_trip_and_revocation():
    connection = make_connection()

    organizations = (
        SQLiteOrganizationRepository(
            connection
        )
    )
    users = SQLiteUserRepository(
        connection
    )
    sessions = SQLiteAuthSessionRepository(
        connection
    )

    paradigm_ra = Organization(
        name="Paradigm Ra",
        type=OrganizationType.PARADIGM_RA,
    )
    organizations.add(paradigm_ra)

    user = User(
        email="admin@paradigmra.tech",
        display_name="Admin",
        password_hash=hash_password(
            "test-password"
        ),
    )
    users.add(user)

    raw_token = generate_session_token()

    session = AuthSession(
        user_id=user.id,
        token_hash=hash_session_token(
            raw_token
        ),
        expires_at=session_expiration(),
    )

    sessions.add(session)
    connection.commit()

    loaded = sessions.get_by_token_hash(
        hash_session_token(raw_token)
    )

    assert loaded is not None
    assert loaded.user_id == user.id
    assert loaded.token_hash != raw_token
    assert loaded.revoked_at is None

    revoked_at = datetime.now(
        timezone.utc
    )

    sessions.revoke(
        session.id,
        revoked_at=revoked_at,
    )
    connection.commit()

    revoked = sessions.get_by_token_hash(
        hash_session_token(raw_token)
    )

    assert revoked is not None
    assert revoked.revoked_at is not None


def test_audit_event_retains_actor_and_scope():
    connection = make_connection()

    organizations = (
        SQLiteOrganizationRepository(
            connection
        )
    )
    users = SQLiteUserRepository(
        connection
    )
    audit = SQLiteAuditEventRepository(
        connection
    )

    brewbird = Organization(
        name="BrewBird Coffee",
        type=OrganizationType.CLIENT,
    )
    organizations.add(brewbird)

    user = User(
        email="admin@paradigmra.tech",
        display_name="Admin",
        password_hash=hash_password(
            "test-password"
        ),
    )
    users.add(user)

    event = AuditEvent(
        actor_user_id=user.id,
        organization_id=brewbird.id,
        action="invoice.created",
        resource_type="invoice",
        metadata_json=(
            '{"source":"admin_platform"}'
        ),
    )

    audit.add(event)
    connection.commit()

    events = audit.list_for_organization(
        brewbird.id
    )

    assert len(events) == 1
    assert events[0].actor_user_id == user.id
    assert events[0].organization_id == (
        brewbird.id
    )
    assert events[0].action == (
        "invoice.created"
    )
