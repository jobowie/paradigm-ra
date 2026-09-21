import {
  platformAdminFetch,
} from "@/lib/server/platformAdminApi";


export async function GET(
  _request: Request,
  context: {
    params: Promise<{
      organizationId: string;
    }>;
  },
) {
  const {
    organizationId,
  } = await context.params;

  return platformAdminFetch(
    `/admin/organizations/${organizationId}/engagements`,
  );
}
