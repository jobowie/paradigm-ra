from __future__ import annotations

from discovery.core.models import ReadinessDecision
from discovery.models import DiscoveryState


def _has_text(value: str | None) -> bool:
    return bool(value and value.strip())


def _has_items(values: list[str]) -> bool:
    return bool(values)


def evaluate_readiness(
    state: DiscoveryState,
) -> ReadinessDecision:
    """
    Determine whether Ra has enough information to move a
    qualified opportunity into a productive human discovery call.

    This is intentionally independent of provider opinion.
    """

    core = {
        "primary_problem": _has_text(state.primary_problem),
        "desired_outcomes": _has_items(state.desired_outcomes),
        "timeline_or_urgency": (
            _has_text(state.timeline)
            or _has_text(state.urgency)
        ),
        "decision_process": _has_text(
            state.decision_process
        ),
    }

    context = {
        "current_process": _has_text(
            state.current_process
        ),
        "current_systems": _has_items(
            state.current_systems
        ),
        "pain_points": _has_items(
            state.pain_points
        ),
        "users_or_teams": _has_items(
            state.users_or_teams_affected
        ),
        "business_impact": _has_text(
            state.business_impact
        ),
        "scope": bool(
            state.requirements
            or state.integrations_needed
        ),
    }

    score = 0

    if core["primary_problem"]:
        score += 20

    if core["desired_outcomes"]:
        score += 20

    if core["timeline_or_urgency"]:
        score += 15

    if core["decision_process"]:
        score += 15

    context_count = sum(context.values())

    score += min(
        context_count * 5,
        30,
    )

    complete = (
        all(core.values())
        and context_count >= 2
    )

    gaps: list[str] = []

    if not core["primary_problem"]:
        gaps.append("primary_problem")

    if not core["desired_outcomes"]:
        gaps.append("desired_outcomes")

    if not core["timeline_or_urgency"]:
        gaps.append("timeline_or_urgency")

    if not core["decision_process"]:
        gaps.append("decision_process")

    if context_count < 2:
        gaps.append("business_context")

    if complete:
        reason = (
            "Ra has enough grounded business context "
            "for a productive human discovery call."
        )
        gaps = []
    else:
        reason = (
            "Discovery should continue only for the "
            "highest-value unresolved gap."
        )

    return ReadinessDecision(
        complete=complete,
        score=min(score, 100),
        gaps=gaps,
        reason=reason,
    )
