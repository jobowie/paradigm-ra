import sqlite3

from cryptography.hazmat.primitives.ciphers.aead import (
    AESGCM,
)

from ra_platform.organizations.billing_profile_service import (
    update_organization_billing_profile,
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
    decrypt_financial_value,
)


def make_context():
    connection = sqlite3.connect(
        ":memory:"
    )

    connection.row_factory = (
        sqlite3.Row
    )

    initialize_database(
        connection
    )

    organization = Organization(
        name="Billing Service Test",
        type=OrganizationType.CLIENT,
    )

    SQLiteOrganizationRepository(
        connection
    ).add(
        organization
    )

    repository = (
        SQLiteOrganizationBillingProfileRepository(
            connection
        )
    )

    key = AESGCM.generate_key(
        bit_length=256
    )

    return (
        connection,
        organization,
        repository,
        key,
    )


def test_service_encrypts_new_bank_values():
    (
        connection,
        organization,
        repository,
        key,
    ) = make_context()

    profile = (
        update_organization_billing_profile(
            repository=repository,
            organization_id=(
                organization.id
            ),
            values={
                "billing_name":
                    "Billing Service Test",
                "routing_number":
                    "123456789",
                "account_number":
                    "987654321012",
            },
            fields_set={
                "billing_name",
                "routing_number",
                "account_number",
            },
            key=key,
        )
    )

    connection.commit()

    assert (
        profile.routing_number_ciphertext
        is not None
    )

    assert (
        profile.account_number_ciphertext
        is not None
    )

    assert profile.routing_number_last4 == (
        "6789"
    )

    assert profile.account_number_last4 == (
        "1012"
    )

    routing = decrypt_financial_value(
        profile.routing_number_ciphertext,
        context=(
            f"organization:"
            f"{organization.id}:"
            "routing_number"
        ),
        key=key,
    )

    account = decrypt_financial_value(
        profile.account_number_ciphertext,
        context=(
            f"organization:"
            f"{organization.id}:"
            "account_number"
        ),
        key=key,
    )

    assert routing == "123456789"
    assert account == "987654321012"

    connection.close()


def test_address_edit_preserves_bank_values():
    (
        connection,
        organization,
        repository,
        key,
    ) = make_context()

    original = (
        update_organization_billing_profile(
            repository=repository,
            organization_id=(
                organization.id
            ),
            values={
                "routing_number":
                    "123456789",
                "account_number":
                    "987654321012",
            },
            fields_set={
                "routing_number",
                "account_number",
            },
            key=key,
        )
    )

    original_routing = (
        original
        .routing_number_ciphertext
    )

    original_account = (
        original
        .account_number_ciphertext
    )

    updated = (
        update_organization_billing_profile(
            repository=repository,
            organization_id=(
                organization.id
            ),
            values={
                "address_line1":
                    "200 Updated Street",
                "city":
                    "Sacramento",
            },
            fields_set={
                "address_line1",
                "city",
            },
            key=key,
        )
    )

    assert (
        updated
        .routing_number_ciphertext
        == original_routing
    )

    assert (
        updated
        .account_number_ciphertext
        == original_account
    )

    connection.close()


def test_explicit_clear_removes_account_number():
    (
        connection,
        organization,
        repository,
        key,
    ) = make_context()

    update_organization_billing_profile(
        repository=repository,
        organization_id=(
            organization.id
        ),
        values={
            "account_number":
                "987654321012",
        },
        fields_set={
            "account_number",
        },
        key=key,
    )

    updated = (
        update_organization_billing_profile(
            repository=repository,
            organization_id=(
                organization.id
            ),
            values={
                "clear_account_number":
                    True,
            },
            fields_set={
                "clear_account_number",
            },
            key=key,
        )
    )

    assert (
        updated
        .account_number_ciphertext
        is None
    )

    assert (
        updated
        .account_number_last4
        is None
    )

    connection.close()
