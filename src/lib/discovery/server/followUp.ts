import type {
  CompletedLead,
} from "@/lib/discovery/server/postDiscovery";


export async function notifyCompletedLead(
  lead: CompletedLead,
): Promise<void> {
  /*
   * Follow-Up v0.1
   *
   * This is the boundary for future internal
   * notifications: email, Slack, CRM, etc.
   *
   * No prospect-facing communication happens here yet.
   */

  console.info(
    "RA POST-DISCOVERY — LEAD READY",
    {
      leadId: lead.id,
      sessionId: lead.sessionId,
      status: lead.status,
      completedAt: lead.completedAt,
    },
  );
}
