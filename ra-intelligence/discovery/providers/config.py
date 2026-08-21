from __future__ import annotations

import os

from dotenv import load_dotenv


load_dotenv()


PROVIDER_CONFIG = {
    "openai": {
        "key_env": "OPENAI_API_KEY",
        "model": os.getenv(
            "RA_OPENAI_MODEL",
            "gpt-5.6-terra",
        ),
    },

    "anthropic": {
        "key_env": "ANTHROPIC_API_KEY",
        "model": os.getenv(
            "RA_ANTHROPIC_MODEL",
            "",
        ),
    },

    "gemini": {
        "key_env": "GEMINI_API_KEY",
        "model": os.getenv(
            "RA_GEMINI_MODEL",
            "gemini-3.7-flash",
        ),
    },

    "mistral": {
        "key_env": "MISTRAL_API_KEY",
        "model": os.getenv(
            "RA_MISTRAL_MODEL",
            "mistral-medium-3-5",
        ),
    },
}


def provider_has_key(
    provider: str,
) -> bool:
    config = PROVIDER_CONFIG[provider]

    return bool(
        os.getenv(config["key_env"])
    )
