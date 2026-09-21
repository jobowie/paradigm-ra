import {
  platformAdminFetch,
} from "@/lib/server/platformAdminApi";


export async function POST(
  _request: Request,
  context: {
    params: Promise<{
      invoiceId: string;
    }>;
  },
) {
  const {
    invoiceId,
  } = await context.params;

  return platformAdminFetch(
    `/admin/invoices/${invoiceId}/send`,
    {
      method: "POST",
    },
  );
}
