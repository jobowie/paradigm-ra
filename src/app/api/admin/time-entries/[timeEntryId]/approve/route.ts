import {
  platformAdminFetch,
} from "@/lib/server/platformAdminApi";


export async function POST(
  _request: Request,
  context: {
    params: Promise<{
      timeEntryId: string;
    }>;
  },
) {
  const {
    timeEntryId,
  } = await context.params;

  return platformAdminFetch(
    `/admin/time-entries/${timeEntryId}/approve`,
    {
      method: "POST",
    },
  );
}
