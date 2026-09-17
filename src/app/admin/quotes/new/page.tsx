import {
  AdminQuoteForm,
} from "@/components/AdminQuoteForm";

export default function NewQuotePage() {
  return (
    <main className="admin-page">
      <div className="shell admin-shell">
        <p className="kicker">
          PARADIGM RA PLATFORM
        </p>

        <h1>
          Create Client Quote
        </h1>

        <p className="admin-intro">
          Define the projected work,
          payment milestones, and
          client terms. Paradigm Ra
          will calculate and persist
          the quote, then generate
          the secure client link.
        </p>

        <AdminQuoteForm />
      </div>
    </main>
  );
}
