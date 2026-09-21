from __future__ import annotations

import base64
from dataclasses import dataclass

import resend


class ResendDeliveryError(Exception):
    pass


@dataclass(frozen=True)
class ResendDelivery:
    message_id: str


def send_pdf_email(
    *,
    api_key: str,
    from_address: str,
    to_address: str,
    subject: str,
    text: str,
    pdf_bytes: bytes,
    pdf_filename: str,
    idempotency_key: str,
    reply_to: str | None = None,
) -> ResendDelivery:
    if not api_key:
        raise ValueError(
            "Resend API key is required."
        )

    if not from_address:
        raise ValueError(
            "Email sender is required."
        )

    if not to_address:
        raise ValueError(
            "Email recipient is required."
        )

    resend.api_key = api_key

    params: resend.Emails.SendParams = {
        "from": from_address,
        "to": [to_address],
        "subject": subject,
        "text": text,
        "attachments": [
            {
                "filename": pdf_filename,
                "content": (
                    base64.b64encode(
                        pdf_bytes
                    ).decode("ascii")
                ),
            }
        ],
    }

    if reply_to:
        params["reply_to"] = reply_to

    try:
        result = resend.Emails.send(
            params
        )

    except Exception as exc:
        raise ResendDeliveryError(
            "Resend rejected the invoice "
            f"email: {exc}"
        ) from exc

    message_id = (
        result.get("id")
        if isinstance(result, dict)
        else getattr(
            result,
            "id",
            None,
        )
    )

    if not isinstance(
        message_id,
        str,
    ) or not message_id:
        raise ResendDeliveryError(
            "Resend response did not include "
            "an email id."
        )

    return ResendDelivery(
        message_id=message_id
    )
