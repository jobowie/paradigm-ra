from ra_platform.security.auth import (
    generate_session_token,
    hash_password,
    hash_session_token,
    verify_password,
)


def test_password_hash_round_trip():
    password = (
        "correct-horse-battery-staple"
    )

    encoded = hash_password(
        password
    )

    assert encoded != password

    assert verify_password(
        password,
        encoded,
    )

    assert not verify_password(
        "wrong-password",
        encoded,
    )


def test_password_hash_uses_unique_salt():
    password = "same-password"

    first = hash_password(password)
    second = hash_password(password)

    assert first != second

    assert verify_password(
        password,
        first,
    )

    assert verify_password(
        password,
        second,
    )


def test_session_token_is_not_stored_raw():
    token = generate_session_token()

    token_hash = hash_session_token(
        token
    )

    assert token.startswith(
        "ra_s_"
    )

    assert token_hash != token

    assert hash_session_token(
        token
    ) == token_hash
