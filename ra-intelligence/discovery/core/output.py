from __future__ import annotations

import re

from discovery.core.models import FlowFinalization
from discovery.models import (
    DiscoveryAgentResponse,
    DiscoveryStage,
)


PROVIDER_IDENTITY_TERMS = (
    "openai",
    "mistral",
    "claude",
    "anthropic",
    "gemini",
    "google ai",
)


PREMATURE_HANDOFF_PATTERNS = (
    r"\bdiscovery call\b",
    r"\bquick call\b",
    r"\bschedule (?:a|the) call\b",
    r"\bbook (?:a|the) call\b",
    r"\bready for (?:a|the) call\b",
    r"\bmove to (?:a|the) call\b",
    r"\bconnect with paradigm ra\b",
    r"\bnext step is (?:to )?connect\b",
    r"\benough context\b",
    r"\benough information\b",
    r"\benough to work with\b",
    r"\bwe have what we need\b",
    r"\bwe have enough\b",
)


GAP_STAGE: dict[str, DiscoveryStage] = {
    "primary_problem": "problem",
    "desired_outcomes": "desired_outcome",
    "timeline_or_urgency": "timeline",
    "decision_process": "decision_process",
    "business_context": "business_context",
}


GAP_QUESTIONS = {
    "primary_problem": (
        "What is the biggest problem this process "
        "is creating for the business today?"
    ),
    "desired_outcomes": (
        "What would a successful improvement to "
        "this process look like for your team?"
    ),
    "timeline_or_urgency": (
        "When would you ideally like this process "
        "improved or replaced?"
    ),
    "decision_process": (
        "Who else would be involved in evaluating "
        "or approving a change to this process?"
    ),
    "business_context": (
        "What impact is this process having on "
        "the team or the business today?"
    ),
}


def _stage_from_gaps(
    gaps: list[str],
) -> DiscoveryStage:
    if not gaps:
        return "business_context"

    return GAP_STAGE.get(
        gaps[0],
        "business_context",
    )


def _reply_is_safe(
    reply: str,
) -> bool:
    lowered = reply.casefold()

    if len(reply) > 1200:
        return False

    if reply.count("?") != 1:
        return False

    for term in PROVIDER_IDENTITY_TERMS:
        if term in lowered:
            return False

    for pattern in PREMATURE_HANDOFF_PATTERNS:
        if re.search(
            pattern,
            lowered,
        ):
            return False

    return True


def build_gap_response(
    finalization: FlowFinalization,
) -> DiscoveryAgentResponse:
    """
    Deterministic Ra repair.

    When provider language violates the open-discovery
    contract, preserve the validated state but replace
    the outbound wording with Ra's highest-value gap.
    """

    gaps = finalization.readiness.gaps

    primary_gap = (
        gaps[0]
        if gaps
        else "business_context"
    )

    reply = GAP_QUESTIONS.get(
        primary_gap,
        GAP_QUESTIONS["business_context"],
    )

    return DiscoveryAgentResponse(
        reply=reply,
        stage=_stage_from_gaps(
            gaps
        ),
        complete=False,
        recommended_next_step=(
            "continue_discovery"
        ),
        state=finalization.state,
    )


def build_handoff_response(
    first_name: str,
    finalization: FlowFinalization,
) -> DiscoveryAgentResponse:
    reply = (
        f"Thanks, {first_name}. "
        "That gives us enough context for a productive "
        "discovery call. The next step is to connect "
        "with Paradigm Ra so we can review the workflow, "
        "priorities, and scope together."
    )

    return DiscoveryAgentResponse(
        reply=reply,
        stage="complete",
        complete=True,
        recommended_next_step=(
            "book_discovery_call"
        ),
        state=finalization.state,
    )


def apply_output_policy(
    candidate: DiscoveryAgentResponse,
    finalization: FlowFinalization,
    first_name: str,
) -> DiscoveryAgentResponse:
    """
    Models propose.
    Ra authorizes what leaves.
    """

    if finalization.readiness.complete:
        return build_handoff_response(
            first_name,
            finalization,
        )

    if (
        candidate.complete
        and candidate.recommended_next_step
        == "not_a_fit"
    ):
        return DiscoveryAgentResponse(
            reply=candidate.reply,
            stage="complete",
            complete=True,
            recommended_next_step="not_a_fit",
            state=finalization.state,
        )

    if not _reply_is_safe(
        candidate.reply
    ):
        return build_gap_response(
            finalization
        )

    return DiscoveryAgentResponse(
        reply=candidate.reply,
        stage=_stage_from_gaps(
            finalization.readiness.gaps
        ),
        complete=False,
        recommended_next_step=(
            "continue_discovery"
        ),
        state=finalization.state,
    )
