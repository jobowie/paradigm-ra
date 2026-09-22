from __future__ import annotations

import base64
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import (
    AESGCM,
)


BILLING_DATA_KEY_ENV = "RA_BILLING_DATA_KEY"

_ENVELOPE_VERSION = "v1"


class FinancialDataEncryptionError(
    ValueError
):
    pass


def _encode_base64(
    value: bytes,
) -> str:
    return (
        base64.urlsafe_b64encode(
            value
        )
        .decode("ascii")
        .rstrip("=")
    )


def _decode_base64(
    value: str,
) -> bytes:
    padding = "=" * (
        (-len(value)) % 4
    )

    try:
        return (
            base64.urlsafe_b64decode(
                value + padding
            )
        )

    except Exception as exc:
        raise FinancialDataEncryptionError(
            "Encrypted financial data "
            "contains invalid encoding."
        ) from exc


def decode_billing_data_key(
    encoded_key: str,
) -> bytes:
    if not encoded_key.strip():
        raise FinancialDataEncryptionError(
            "Billing data encryption key "
            "is not configured."
        )

    key = _decode_base64(
        encoded_key.strip()
    )

    if len(key) != 32:
        raise FinancialDataEncryptionError(
            "Billing data encryption key "
            "must decode to 32 bytes."
        )

    return key


def get_billing_data_key() -> bytes:
    return decode_billing_data_key(
        os.environ.get(
            BILLING_DATA_KEY_ENV,
            "",
        )
    )


def encrypt_financial_value(
    value: str,
    *,
    context: str,
    key: bytes | None = None,
) -> str:
    if not value:
        raise FinancialDataEncryptionError(
            "Financial value cannot be empty."
        )

    if not context:
        raise FinancialDataEncryptionError(
            "Encryption context is required."
        )

    encryption_key = (
        key
        if key is not None
        else get_billing_data_key()
    )

    if len(encryption_key) != 32:
        raise FinancialDataEncryptionError(
            "Billing data encryption key "
            "must be 32 bytes."
        )

    nonce = os.urandom(12)

    ciphertext = AESGCM(
        encryption_key
    ).encrypt(
        nonce,
        value.encode("utf-8"),
        context.encode("utf-8"),
    )

    return ".".join(
        [
            _ENVELOPE_VERSION,
            _encode_base64(nonce),
            _encode_base64(
                ciphertext
            ),
        ]
    )


def decrypt_financial_value(
    encrypted_value: str,
    *,
    context: str,
    key: bytes | None = None,
) -> str:
    if not context:
        raise FinancialDataEncryptionError(
            "Encryption context is required."
        )

    parts = encrypted_value.split(
        "."
    )

    if (
        len(parts) != 3
        or parts[0]
        != _ENVELOPE_VERSION
    ):
        raise FinancialDataEncryptionError(
            "Encrypted financial data "
            "has an unsupported format."
        )

    encryption_key = (
        key
        if key is not None
        else get_billing_data_key()
    )

    if len(encryption_key) != 32:
        raise FinancialDataEncryptionError(
            "Billing data encryption key "
            "must be 32 bytes."
        )

    nonce = _decode_base64(
        parts[1]
    )

    ciphertext = _decode_base64(
        parts[2]
    )

    try:
        plaintext = AESGCM(
            encryption_key
        ).decrypt(
            nonce,
            ciphertext,
            context.encode("utf-8"),
        )

    except InvalidTag as exc:
        raise FinancialDataEncryptionError(
            "Encrypted financial data "
            "could not be authenticated."
        ) from exc

    return plaintext.decode(
        "utf-8"
    )


def financial_last_four(
    value: str,
) -> str:
    compact = "".join(
        character
        for character in value
        if character.isalnum()
    )

    return compact[-4:]


def masked_financial_value(
    last_four: str | None,
) -> str | None:
    if not last_four:
        return None

    return (
        "\u2022\u2022\u2022\u2022"
        + last_four
    )
