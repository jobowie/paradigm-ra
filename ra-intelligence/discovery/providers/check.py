from __future__ import annotations

from importlib.metadata import (
    PackageNotFoundError,
    version,
)

from discovery.providers.config import (
    PROVIDER_CONFIG,
    provider_has_key,
)


PACKAGES = {
    "openai": "openai",
    "anthropic": "anthropic",
    "gemini": "google-genai",
    "mistral": "mistralai",
}


def package_version(
    package: str,
) -> str | None:
    try:
        return version(package)
    except PackageNotFoundError:
        return None


def main() -> None:
    print()
    print("RA DISCOVERY — PADDOCK STATUS")
    print("----------------------------")

    for provider, package in PACKAGES.items():
        installed = package_version(package)
        config = PROVIDER_CONFIG[provider]

        sdk_status = (
            f"SDK {installed}"
            if installed
            else "SDK MISSING"
        )

        key_status = (
            "KEY READY"
            if provider_has_key(provider)
            else "KEY NOT SET"
        )

        model = (
            config["model"]
            if config["model"]
            else "select at activation"
        )

        print()
        print(provider.upper())
        print(f"  {sdk_status}")
        print(f"  {key_status}")
        print(f"  model: {model}")

    print()
    print(
        "No API requests were made."
    )
    print()


if __name__ == "__main__":
    main()
