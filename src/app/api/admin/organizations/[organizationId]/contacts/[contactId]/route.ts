import {
  platformAdminFetch,
} from "@/lib/server/platformAdminApi";

export async function PUT(
  request: Request,
  context: {
    params: Promise<{
      organizationId: string;
      contactId: string;
    }>;
  },
) {
  const {
    organizationId,
    contactId,
  } = await context.params;

  return platformAdminFetch(
    `/admin/organizations/${organizationId}/contacts/${contactId}`,
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
