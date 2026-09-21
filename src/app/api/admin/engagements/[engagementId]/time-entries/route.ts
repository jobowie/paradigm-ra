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
    `/admin/engagements/${engagementId}/time-entries`,
  );
}


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
    `/admin/engagements/${engagementId}/time-entries`,
    {
      method: "POST",
      body: JSON.stringify(
        body,
      ),
    },
  );
}
