import {
  platformAdminFetch,
} from "@/lib/server/platformAdminApi";


export async function POST(
  request: Request,
  context: {
    params: Promise<{
      engagementId: string;
    }>;
  },
) {
  const {
    engagementId,
  } = await context.params;

  const body =
    await request.json();

  return platformAdminFetch(
    `/admin/engagements/${engagementId}/invoices/generate`,
    {
      method: "POST",
      body: JSON.stringify(
        body,
      ),
    },
  );
}
