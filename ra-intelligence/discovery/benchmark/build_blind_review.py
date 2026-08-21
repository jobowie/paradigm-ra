from __future__ import annotations

import json
import random
from pathlib import Path


PROVIDERS = ["mistral", "openai"]

RUNS_DIR = Path("discovery/benchmark/runs")
OUTPUT_PATH = RUNS_DIR / "finalists-blind-review.json"
KEY_PATH = RUNS_DIR / "finalists-blind-key.json"


def main() -> None:
    runs = {}

    for provider in PROVIDERS:
        path = RUNS_DIR / f"{provider}-round1.json"
        runs[provider] = json.loads(path.read_text())

    scenario_ids = [
        case["scenario_id"]
        for case in runs["mistral"]["cases"]
        if not case.get("error")
    ]

    review = []
    answer_key = []

    rng = random.Random(42)

    for scenario_id in scenario_ids:
        entries = []

        for provider in PROVIDERS:
            case = next(
                case
                for case in runs[provider]["cases"]
                if case["scenario_id"] == scenario_id
            )

            if case.get("error"):
                continue

            entries.append(
                {
                    "provider": provider,
                    "reply": case["response"]["reply"],
                    "state": case["response"]["state"],
                    "automatic_score": case[
                        "automatic_score"
                    ]["total"],
                }
            )

        rng.shuffle(entries)

        labels = ["A", "B"]

        blind_entries = []
        key_entries = []

        for label, entry in zip(labels, entries):
            blind_entries.append(
                {
                    "label": label,
                    "reply": entry["reply"],
                    "state": entry["state"],
                    "human_score": {
                        "next_question_quality": None,
                        "consultative_tone": None,
                        "experience_continuity": None,
                    },
                    "review_notes": "",
                }
            )

            key_entries.append(
                {
                    "label": label,
                    "provider": entry["provider"],
                    "automatic_score": entry[
                        "automatic_score"
                    ],
                }
            )

        review.append(
            {
                "scenario_id": scenario_id,
                "responses": blind_entries,
            }
        )

        answer_key.append(
            {
                "scenario_id": scenario_id,
                "responses": key_entries,
            }
        )

    OUTPUT_PATH.write_text(
        json.dumps(review, indent=2) + "\n"
    )

    KEY_PATH.write_text(
        json.dumps(answer_key, indent=2) + "\n"
    )

    print()
    print("RA DISCOVERY — FINALIST REVIEW")
    print("-----------------------------")
    print("Finalists: 2")
    print(f"Scenarios: {len(review)}")
    print(f"Review:    {OUTPUT_PATH}")
    print(f"Key:       {KEY_PATH}")
    print()
    print("Blind review packet generated ✓")
    print()


if __name__ == "__main__":
    main()
