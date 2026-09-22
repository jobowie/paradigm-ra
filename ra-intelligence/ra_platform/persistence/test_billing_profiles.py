import sqlite3

from cryptography.hazmat.primitives.ciphers.aead import (
    AESGCM,
)

from ra_platform.organizations.billing_profile import (
    OrganizationBillingProfile,
)
from ra_platform.organizations.models import (
    Organization,
    OrganizationType,
)
from ra_platform.persistence.billing_profiles import (
    SQLiteOrganizationBillingProfileRepository,
)
from ra_platform.persistence.sqlite import (
    initialize_database,
)
from ra_platform.persistence.sqlite_repositories import (
    SQLiteOrganizationRepository,
)
from ra_platform.security.financial_data import (
    encrypt_financial_value,
    financial_last_four,
)


def make_connection():
    connection = sqlite3.connect(
        ":memory:"
    )

    connection.row_factory = (
        sqlite3.Row
    )

    initialize_database(
        connection
    )

    return connection


def test_billing_profile_persists_encrypted_financial_data():
    connection = make_connection()

    organization = Organization(
        name=(
            "Client: Billing Profile Test"
        ),
        type=OrganizationType.CLIENT,
    )

    SQLiteOrganizationRepository(
        connection
    ).add(
        organization
    )

    key = AESGCM.generate_key(
        bit_length=256
    )

    routing = "123456789"
    account = "987654321012"

    routing_context = (
        f"organization:"
        f"{organization.id}:"
        "routing_number"
    )

    account_context = (
        f"organization:"
        f"{organization.id}:"
        "account_number"
    )

    profile = (
        OrganizationBillingProfile(
            organization_id=(
                organization.id
            ),
            billing_name=(
                organization.name
            ),
            billing_email=(
                "billing@example.com"
            ),
            address_line1=(
                "100 Test Street"
            ),
            city="Sacramento",
            state_region="CA",
            postal_code="95814",
            bank_name="Test Bank",
            account_type="checking",

            routing_number_ciphertext=(
                encrypt_financial_value(
                    routing,
                    context=(
                        routing_context
                    ),
                    key=key,
                )
            ),
            routing_number_last4=(
                financial_last_four(
                    routing
                )
            ),

            account_number_ciphertext=(
                encrypt_financial_value(
                    account,
                    context=(
                        account_context
                    ),
                    key=key,
                )
            ),
            account_number_last4=(
                financial_last_four(
                    account
                )
            ),
        )
    )

    repository = (
        SQLiteOrganizationBillingProfileRepository(
            connection
        )
    )

    repository.upsert(
        profile
    )

    connection.commit()

    stored = connection.execute(
        """
        SELECT *
        FROM organization_billing_profiles
        WHERE organization_id = ?
        """,
        (
            str(
                organization.id
            ),
        ),
    ).fetchone()

    assert stored is not None

    assert (
        stored[
            "routing_number_ciphertext"
        ]
        != routing
    )

    assert (
        stored[
            "account_number_ciphertext"
        ]
        != account
    )

    assert routing not in (
        stored[
            "routing_number_ciphertext"
        ]
    )

    assert account not in (
        stored[
            "account_number_ciphertext"
        ]
    )

    assert (
        stored[
            "routing_number_last4"
        ]
        == "6789"
    )

    assert (
        stored[
            "account_number_last4"
        ]
        == "1012"
    )

    loaded = (
        repository
        .get_for_organization(
            organization.id
        )
    )

    assert loaded is not None

    assert loaded.billing_email == (
        "billing@example.com"
    )

    assert (
        loaded.routing_number_last4
        == "6789"
    )

    assert (
        loaded.account_number_last4
        == "1012"
    )

    connection.close()
