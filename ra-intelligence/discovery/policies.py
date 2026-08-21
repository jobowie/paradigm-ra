def get_follow_up_limit(questions_answered: int) -> int:
    if questions_answered <= 0:
        return 0

    if questions_answered <= 2:
        return 1

    return 2


def should_send_discovery_follow_up(
    *,
    contact_captured: bool,
    complete: bool,
    questions_answered: int,
    follow_ups_sent: int,
) -> bool:
    if not contact_captured or complete:
        return False

    limit = get_follow_up_limit(questions_answered)

    return follow_ups_sent < limit
