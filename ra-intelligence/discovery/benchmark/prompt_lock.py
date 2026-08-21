from __future__ import annotations

import hashlib
import json
from pathlib import Path

from discovery.prompt import RA_DISCOVERY_SYSTEM_PROMPT


PROMPT_VERSION = "ra-discovery-v0.1"
LOCK_PATH = Path(
    "discovery/benchmark/prompt_manifest.json"
)


def prompt_hash() -> str:
    return hashlib.sha256(
        RA_DISCOVERY_SYSTEM_PROMPT.encode("utf-8")
    ).hexdigest()


def main() -> None:
    current_hash = prompt_hash()

    if LOCK_PATH.exists():
        manifest = json.loads(
            LOCK_PATH.read_text()
        )

        if manifest["sha256"] != current_hash:
            raise RuntimeError(
                "RA DISCOVERY PROMPT CHANGED AFTER FREEZE.\n"
                "Do not continue the Derby until the change "
                "is intentionally versioned."
            )

        print()
        print("RA DISCOVERY — PROMPT LOCK")
        print("--------------------------")
        print(f"Version: {manifest['version']}")
        print(f"SHA256:  {current_hash[:16]}...")
        print("Status:   FROZEN ✓")
        print()
        return

    manifest = {
        "version": PROMPT_VERSION,
        "sha256": current_hash,
    }

    LOCK_PATH.write_text(
        json.dumps(manifest, indent=2)
        + "\n"
    )

    print()
    print("RA DISCOVERY — PROMPT LOCK")
    print("--------------------------")
    print(f"Version: {PROMPT_VERSION}")
    print(f"SHA256:  {current_hash[:16]}...")
    print("Status:   FROZEN ✓")
    print()


if __name__ == "__main__":
    main()
