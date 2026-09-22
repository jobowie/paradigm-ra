from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from ra_platform.organizations.billing_profile import (
    OrganizationBillingProfile,
)
from ra_platform.persistence.billing_profiles import (
    SQLiteOrganizationBillingProfileRepository,
)
from ra_platform.security.financial_data import (
    encrypt_financial_value,
    financial_last_four,
)


class BillingProfileUpdateError(
    ValueError
):
    pass


PROFILE_FIELDS = {
    "billing_name",
    "billing_email",
    "address_line1",
    "address_line2",
    "city",
    "state_region",
    "postal_code",
    "country",
    "bank_name",
    "account_type",
}


def _normalize_optional_text(
    value: Any,
) -> str | None:
    if value is None:
        return None

    text = str(value).strip()

    return text or None


def _financial_context(
    *,
    organization_id: UUID,
    field_name: str,
) -> str:
    return (
        f"organization:"
        f"{organization_id}:"
        f"{field_name}"
    )


def update_organization_billing_profile(
    *,
    repository: (
        SQLiteOrganizationBillingProfileRepository
    ),
    organization_id: UUID,
    values: dict[str, Any],
    fields_set: set[str],
    key: bytes | None = None,
) -> OrganizationBillingProfile:
    profile = (
        repository
        .get_for_organization(
            organization_id
        )
    )

    if profile is None:
        profile = (
            OrganizationBillingProfile(
                organization_id=(
                    organization_id
                )
            )
        )

    for field_name in PROFILE_FIELDS:
        if field_name not in fields_set:
            continue

        value = _normalize_optional_text(
            values.get(
                field_name
            )
        )

        if (
            field_name == "country"
            and value is None
        ):
            value = "US"

        setattr(
            profile,
            field_name,
            value,
        )

    _update_financial_field(
        profile=profile,
        values=values,
        fields_set=fields_set,
        plaintext_field=(
            "routing_number"
        ),
        clear_field=(
            "clear_routing_number"
        ),
        ciphertext_field=(
            "routing_number_ciphertext"
        ),
        last4_field=(
            "routing_number_last4"
        ),
        key=key,
    )

    _update_financial_field(
        profile=profile,
        values=values,
        fields_set=fields_set,
        plaintext_field=(
            "account_number"
        ),
        clear_field=(
            "clear_account_number"
        ),
        ciphertext_field=(
            "account_number_ciphertext"
        ),
        last4_field=(
            "account_number_last4"
        ),
        key=key,
    )

    profile.updated_at = (
        datetime.now(
            timezone.utc
        )
    )

    repository.upsert(
        profile
    )

    return profile


def _update_financial_field(
    *,
    profile: OrganizationBillingProfile,
    values: dict[str, Any],
    fields_set: set[str],
    plaintext_field: str,
    clear_field: str,
    ciphertext_field: str,
    last4_field: str,
    key: bytes | None,
) -> None:
    should_clear = bool(
        values.get(
            clear_field,
            False,
        )
    )

    has_new_value = (
        plaintext_field
        in fields_set
    )

    if should_clear and has_new_value:
        raise BillingProfileUpdateError(
            f"{plaintext_field} cannot "
            "be replaced and cleared "
            "in the same request."
        )

    if should_clear:
        setattr(
            profile,
            ciphertext_field,
            None,
        )

        setattr(
            profile,
            last4_field,
            None,
        )

        return

    if not has_new_value:
        return

    raw_value = values.get(
        plaintext_field
    )

    if raw_value is None:
        raise BillingProfileUpdateError(
            f"{plaintext_field} cannot "
            "be null. Use the clear "
            "flag to remove it."
        )

    normalized = "".join(
        character
        for character
        in str(raw_value)
        if character.isalnum()
    )

    if not normalized:
        raise BillingProfileUpdateError(
            f"{plaintext_field} cannot "
            "be empty."
        )

    context = _financial_context(
        organization_id=(
            profile.organization_id
        ),
        field_name=(
            plaintext_field
        ),
    )

    encrypted = (
        encrypt_financial_value(
            normalized,
            context=context,
            key=key,
        )
    )

    setattr(
        profile,
        ciphertext_field,
        encrypted,
    )

    setattr(
        profile,
        last4_field,
        financial_last_four(
            normalized
        ),
    )
