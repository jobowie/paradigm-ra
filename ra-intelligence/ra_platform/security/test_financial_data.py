import base64

import pytest

from cryptography.hazmat.primitives.ciphers.aead import (
    AESGCM,
)

from ra_platform.security.financial_data import (
    FinancialDataEncryptionError,
    decode_billing_data_key,
    decrypt_financial_value,
    encrypt_financial_value,
    financial_last_four,
    masked_financial_value,
)


def make_key() -> bytes:
    return AESGCM.generate_key(
        bit_length=256
    )


def test_financial_value_encrypts_and_round_trips():
    key = make_key()

    plaintext = "1234567890123456"

    encrypted = (
        encrypt_financial_value(
            plaintext,
            context=(
                "organization:test:"
                "account_number"
            ),
            key=key,
        )
    )

    assert plaintext not in encrypted

    assert decrypt_financial_value(
        encrypted,
        context=(
            "organization:test:"
            "account_number"
        ),
        key=key,
    ) == plaintext


def test_financial_value_uses_unique_nonce():
    key = make_key()

    first = encrypt_financial_value(
        "123456789",
        context=(
            "organization:test:"
            "routing_number"
        ),
        key=key,
    )

    second = encrypt_financial_value(
        "123456789",
        context=(
            "organization:test:"
            "routing_number"
        ),
        key=key,
    )

    assert first != second


def test_financial_value_rejects_wrong_context():
    key = make_key()

    encrypted = (
        encrypt_financial_value(
            "1234567890123456",
            context=(
                "organization:a:"
                "account_number"
            ),
            key=key,
        )
    )

    with pytest.raises(
        FinancialDataEncryptionError
    ):
        decrypt_financial_value(
            encrypted,
            context=(
                "organization:b:"
                "account_number"
            ),
            key=key,
        )


def test_billing_key_requires_256_bits():
    short_key = (
        base64.urlsafe_b64encode(
            b"too-short"
        ).decode("ascii")
    )

    with pytest.raises(
        FinancialDataEncryptionError
    ):
        decode_billing_data_key(
            short_key
        )


def test_financial_masking_exposes_only_last_four():
    assert financial_last_four(
        "1234-5678-9012"
    ) == "9012"

    assert masked_financial_value(
        "9012"
    ) == "\u2022\u2022\u2022\u20229012"

    assert (
        masked_financial_value(
            None
        )
        is None
    )
