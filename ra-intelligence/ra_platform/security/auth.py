import base64
import hashlib
import secrets

from datetime import datetime, timedelta, timezone


SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_DKLEN = 64


def hash_password(
    password: str,
) -> str:
    if not password:
        raise ValueError(
            "Password is required."
        )

    salt = secrets.token_bytes(16)

    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=SCRYPT_DKLEN,
    )

    encoded_salt = base64.urlsafe_b64encode(
        salt
    ).decode("ascii")

    encoded_hash = base64.urlsafe_b64encode(
        derived
    ).decode("ascii")

    return (
        f"scrypt${SCRYPT_N}"
        f"${SCRYPT_R}"
        f"${SCRYPT_P}"
        f"${encoded_salt}"
        f"${encoded_hash}"
    )


def verify_password(
    password: str,
    encoded: str,
) -> bool:
    try:
        (
            algorithm,
            n,
            r,
            p,
            encoded_salt,
            encoded_hash,
        ) = encoded.split("$")
    except ValueError:
        return False

    if algorithm != "scrypt":
        return False

    try:
        salt = base64.urlsafe_b64decode(
            encoded_salt.encode("ascii")
        )

        expected = base64.urlsafe_b64decode(
            encoded_hash.encode("ascii")
        )

        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(expected),
        )

    except (ValueError, TypeError):
        return False

    return secrets.compare_digest(
        actual,
        expected,
    )


def generate_session_token() -> str:
    return (
        "ra_s_"
        + secrets.token_urlsafe(32)
    )


def hash_session_token(
    token: str,
) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def session_expiration(
    *,
    hours: int = 12,
) -> datetime:
    return (
        datetime.now(timezone.utc)
        + timedelta(hours=hours)
    )
