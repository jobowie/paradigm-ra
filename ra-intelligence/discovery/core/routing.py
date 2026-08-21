from __future__ import annotations

import re

from discovery.core.models import (
    ReadinessDecision,
    RouteDecision,
)
from discovery.models import DiscoveryState


COMPLEX_SERVICES = {
    "custom_software",
    "advisory",
    "mixed",
}


STRONG_COMPLEXITY_LANGUAGE = (
    "legacy",
    "moderniz",
    "migration",
    "architecture",
    "business-critical",
    "replace or integrate",
    "replace versus",
    "replace vs",
    "fragmented",
    "different teams",
    "multiple departments",
    "several departments",
)


SYSTEM_MARKERS = (
    "quickbooks",
    "sql server",
    "crm",
    "erp",
    "excel",
    "microsoft 365",
    "database",
    "application",
    "software",
    "platform",
    "system",
    "systems",
    "tool",
    "tools",
)


STAKEHOLDER_MARKERS = (
    "location",
    "locations",
    "department",
    "departments",
    "team",
    "teams",
    "employees",
    "staff",
    "supervisors",
    "leadership",
    "operations",
    "sales",
    "estimating",
    "management",
)


FUTURE_STATE_MARKERS = (
    "want to",
    "would like",
    "need to",
    "looking to",
    "goal",
    "automate",
    "automation",
    "integrate",
    "integration",
    "connect",
    "online",
    "modernize",
    "modernise",
    "replace",
    "improve",
)


PROCESS_MARKERS = (
    "manual",
    "manually",
    "enter",
    "entered",
    "re-enter",
    "update",
    "updated",
    "write",
    "written",
    "send",
    "sends",
    "email",
    "call",
    "consolidate",
    "combine",
    "flow",
)


TIMELINE_PATTERNS = (
    r"\bthis quarter\b",
    r"\bnext quarter\b",
    r"\bwithin\b",
    r"\bbefore january\b",
    r"\bbefore february\b",
    r"\bbefore march\b",
    r"\bbefore april\b",
    r"\bbefore may\b",
    r"\bbefore june\b",
    r"\bbefore july\b",
    r"\bbefore august\b",
    r"\bbefore september\b",
    r"\bbefore october\b",
    r"\bbefore november\b",
    r"\bbefore december\b",
    r"\bnext \d+ (?:days?|weeks?|months?)\b",
    r"\bwithin \d+ (?:days?|weeks?|months?)\b",
)


SCALE_PATTERN = re.compile(
    r"\b(?:"
    r"\d[\d,]*"
    r"|one|two|three|four|five"
    r"|six|seven|eight|nine|ten"
    r"|dozens?|hundreds?"
    r")\s+"
    r"(?:orders?|locations?|users?|employees?|"
    r"people|supervisors?|departments?|teams?|"
    r"quotes?|hours?|days?|weeks?|months?)\b",
    re.IGNORECASE,
)


def _contains_any(
    text: str,
    markers: tuple[str, ...],
) -> bool:
    return any(
        marker in text
        for marker in markers
    )


def detect_signal_families(
    latest_message: str,
) -> set[str]:
    """
    Identify distinct business-information families.

    Complexity is based on information density rather
    than raw message length.
    """

    text = latest_message.casefold()

    signals: set[str] = set()

    if _contains_any(
        text,
        SYSTEM_MARKERS,
    ):
        signals.add("systems")

    if _contains_any(
        text,
        STAKEHOLDER_MARKERS,
    ):
        signals.add("stakeholders")

    if _contains_any(
        text,
        FUTURE_STATE_MARKERS,
    ):
        signals.add("future_state")

    process_hits = sum(
        1
        for marker in PROCESS_MARKERS
        if marker in text
    )

    if process_hits >= 2:
        signals.add("process_chain")

    if any(
        re.search(
            pattern,
            text,
        )
        for pattern in TIMELINE_PATTERNS
    ):
        signals.add("timeline")

    if SCALE_PATTERN.search(text):
        signals.add("scale")

    return signals


def choose_route(
    state: DiscoveryState,
    latest_message: str,
    readiness: ReadinessDecision,
) -> RouteDecision:
    """
    Select a Ra capability ROLE.

    Normal business context does not automatically
    mean complex reasoning. Ra escalates when multiple
    complexity indicators accumulate.
    """

    if readiness.complete:
        return RouteDecision(
            role="handoff",
            complexity_score=0,
            reason=(
                "Ra readiness is complete. "
                "No discovery model call is required."
            ),
        )

    text = latest_message.strip().casefold()
    words = len(latest_message.split())

    signals = detect_signal_families(
        latest_message
    )

    score = 0
    reasons: list[str] = []

    # Ordinary discovery information.
    # Useful context, but not enough by itself
    # to justify complex-model compute.
    base_signals = {
        "systems",
        "stakeholders",
        "future_state",
        "process_chain",
    }

    for signal in sorted(
        signals & base_signals
    ):
        score += 1
        reasons.append(signal)

    # Stronger complexity indicators.
    if "timeline" in signals:
        score += 1
        reasons.append("timeline")

    if "scale" in signals:
        score += 2
        reasons.append("scale")

    if state.service_category in COMPLEX_SERVICES:
        score += 4
        reasons.append(
            "complex service category"
        )

    strong_hits = [
        marker
        for marker
        in STRONG_COMPLEXITY_LANGUAGE
        if marker in text
    ]

    if strong_hits:
        score += 3
        reasons.append(
            "strong complexity language"
        )

    if len(state.current_systems) >= 2:
        score += 2
        reasons.append(
            "multiple known systems"
        )

    if (
        len(state.users_or_teams_affected)
        >= 2
    ):
        score += 1
        reasons.append(
            "multiple stakeholder groups"
        )

    if (
        len(state.integrations_needed) >= 2
        or len(state.requirements) >= 3
    ):
        score += 2
        reasons.append(
            "multi-part known scope"
        )

    # Length is a tie-breaker only.
    if words >= 45:
        score += 1
        reasons.append(
            "dense response length"
        )

    if score >= 6:
        return RouteDecision(
            role="complex",
            complexity_score=score,
            reason="; ".join(reasons),
        )

    return RouteDecision(
        role="rapid",
        complexity_score=score,
        reason=(
            "; ".join(reasons)
            if reasons
            else "straightforward discovery gap"
        ),
    )
