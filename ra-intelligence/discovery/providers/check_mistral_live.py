from __future__ import annotations

import os


def main() -> None:
    api_key = os.getenv("MISTRAL_API_KEY")

    if not api_key:
        raise RuntimeError(
            "MISTRAL_API_KEY is not configured."
        )

    from mistralai.client import Mistral

    client = Mistral(api_key=api_key)

    response = client.models.list()

    model_ids = sorted(
        model.id
        for model in response.data
        if getattr(model, "id", None)
    )

    target = "mistral-medium-3-5"

    print()
    print("RA DISCOVERY — MISTRAL ACCESS")
    print("-----------------------------")

    if target in model_ids:
        print(f"{target}: AVAILABLE ✓")
    else:
        print(f"{target}: NOT AVAILABLE")
        print()
        print("Relevant available models:")

        for model_id in model_ids:
            if (
                "medium" in model_id.lower()
                or "small" in model_id.lower()
            ):
                print(f"  {model_id}")

    print()


if __name__ == "__main__":
    main()
