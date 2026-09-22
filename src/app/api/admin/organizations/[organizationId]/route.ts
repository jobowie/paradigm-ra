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
    `/admin/organizations/${organizationId}`,
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

  return platformAdminFetch(
    `/admin/organizations/${organizationId}`,
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
