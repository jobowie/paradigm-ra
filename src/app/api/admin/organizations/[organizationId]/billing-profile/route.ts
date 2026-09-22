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
    `/admin/organizations/${organizationId}/billing-profile`,
  );
}

export async function PUT(
  request: Request,
  context: {
    params: Promise<{
      organizationId: string;
    }>;
  },
) {
  const {
    organizationId,
  } = await context.params;

  const body =
    await request.text();

  return platformAdminFetch(
    `/admin/organizations/${organizationId}/billing-profile`,
    {
      method: "PUT",
      headers: {
        "Content-Type":
          "application/json",
      },
      body,
    },
  );
}
