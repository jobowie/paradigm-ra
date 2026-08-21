export interface DiscoveryFollowUpContext {
  contactCaptured: boolean;
  complete: boolean;
  questionsAnswered: number;
  followUpsSent: number;
}

export function getFollowUpLimit(
  questionsAnswered: number,
): number {
  if (questionsAnswered <= 0) {
    return 0;
  }

  if (questionsAnswered <= 2) {
    return 1;
  }

  return 2;
}

export function shouldSendDiscoveryFollowUp(
  context: DiscoveryFollowUpContext,
): boolean {
  if (!context.contactCaptured || context.complete) {
    return false;
  }

  const limit = getFollowUpLimit(
    context.questionsAnswered,
  );

  return context.followUpsSent < limit;
}
