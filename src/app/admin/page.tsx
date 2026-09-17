import {
  AdminWorkspace,
} from "@/components/AdminWorkspace";


export default function AdminPage() {
  return (
    <main className="admin-page">
      <div className="shell admin-shell">
        <p className="kicker">
          PARADIGM RA PLATFORM
        </p>

        <h1>
          Administration
        </h1>

        <p className="admin-intro">
          Create client quotes,
          establish payment milestones,
          and generate secure links
          for client acceptance
          and payment.
        </p>

        <AdminWorkspace />
      </div>
    </main>
  );
}
