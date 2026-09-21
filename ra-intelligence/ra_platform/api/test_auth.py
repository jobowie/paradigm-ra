import sqlite3

from fastapi.testclient import TestClient

from ra_platform.api.main import app
from ra_platform.identity.models import (
    MembershipRole,
    OrganizationMembership,
    User,
)
from ra_platform.organizations.models import (
    Organization,
    OrganizationType,
)
from ra_platform.persistence.sqlite import (
    create_connection,
    initialize_database,
)
from ra_platform.persistence.sqlite_repositories import (
    SQLiteOrganizationMembershipRepository,
    SQLiteOrganizationRepository,
    SQLiteUserRepository,
)
from ra_platform.security.auth import (
    hash_password,
)


def seed_identity(
    db_path,
):
    connection = create_connection(
        db_path
    )
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

    paradigm_ra = Organization(
        name="Paradigm Ra",
        type=OrganizationType.PARADIGM_RA,
    )
    organizations.add(paradigm_ra)

    user = User(
        email="ceo@paradigmra.tech",
        display_name="Paradigm Ra CEO",
        password_hash=hash_password(
            "correct-password"
        ),
    )
    users.add(user)

    memberships.add(
        OrganizationMembership(
            user_id=user.id,
            organization_id=paradigm_ra.id,
            role=(
                MembershipRole
                .PARADIGM_RA_EXECUTIVE
            ),
        )
    )

    connection.commit()
    connection.close()

    return user, paradigm_ra


def test_login_me_logout(
    tmp_path,
    monkeypatch,
):
    db_path = (
        tmp_path
        / "auth-test.db"
    )

    monkeypatch.setenv(
        "RA_DB_PATH",
        str(db_path),
    )

    user, organization = seed_identity(
        db_path
    )

    client = TestClient(app)

    login = client.post(
        "/auth/login",
        json={
            "email": "CEO@PARADIGMRA.TECH",
            "password": "correct-password",
        },
    )

    assert login.status_code == 200

    body = login.json()

    assert body["user"]["id"] == str(
        user.id
    )

    assert (
        body["memberships"][0]
        ["organization_id"]
        == str(organization.id)
    )

    assert (
        body["memberships"][0]["role"]
        == "paradigm_ra_executive"
    )

    token = body["session_token"]

    me = client.get(
        "/auth/me",
        headers={
            "Authorization":
                f"Bearer {token}",
        },
    )

    assert me.status_code == 200
    assert (
        me.json()["user"]["email"]
        == "ceo@paradigmra.tech"
    )

    logout = client.post(
        "/auth/logout",
        headers={
            "Authorization":
                f"Bearer {token}",
        },
    )

    assert logout.status_code == 200
    assert logout.json() == {
        "logged_out": True,
    }

    after_logout = client.get(
        "/auth/me",
        headers={
            "Authorization":
                f"Bearer {token}",
        },
    )

    assert after_logout.status_code == 401


def test_wrong_password_returns_401(
    tmp_path,
    monkeypatch,
):
    db_path = (
        tmp_path
        / "wrong-password.db"
    )

    monkeypatch.setenv(
        "RA_DB_PATH",
        str(db_path),
    )

    seed_identity(
        db_path
    )

    client = TestClient(app)

    response = client.post(
        "/auth/login",
        json={
            "email": "ceo@paradigmra.tech",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid credentials."
    )


def test_me_requires_authentication(
    tmp_path,
    monkeypatch,
):
    db_path = (
        tmp_path
        / "missing-session.db"
    )

    monkeypatch.setenv(
        "RA_DB_PATH",
        str(db_path),
    )

    client = TestClient(app)

    response = client.get(
        "/auth/me"
    )

    assert response.status_code == 401
