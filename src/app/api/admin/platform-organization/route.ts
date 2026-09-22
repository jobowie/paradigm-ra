import {
  platformAdminFetch,
} from "@/lib/server/platformAdminApi";

export async function GET() {
  return platformAdminFetch(
    "/admin/platform-organization",
  );
}
