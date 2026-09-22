import {
  platformAdminFetch,
} from "@/lib/server/platformAdminApi";

export async function PUT(
  request: Request,
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
    `/admin/time-entries/${timeEntryId}`,
    {
      method: "PUT",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: await request.text(),
    },
  );
}
