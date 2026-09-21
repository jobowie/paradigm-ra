import {
  platformAdminFetch,
} from "@/lib/server/platformAdminApi";


export async function GET(
  _request: Request,
  context: {
    params: Promise<{
      engagementId: string;
    }>;
  },
) {
  const {
    engagementId,
  } = await context.params;

  return platformAdminFetch(
    `/admin/engagements/${engagementId}/billing-terms`,
  );
}
