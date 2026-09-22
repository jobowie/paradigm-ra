"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";


interface Contact {
  id: string;
  organization_id: string;

  name: string;
  title: string | null;
  email: string | null;
  phone: string | null;
  contact_type: string | null;

  is_primary: boolean;
}


interface Props {
  organizationId: string;
}


export function OrganizationContactsCard({
  organizationId,
}: Props) {
  const [
    contacts,
    setContacts,
  ] = useState<Contact[]>([]);

  const [
    managing,
    setManaging,
  ] = useState(false);

  const [
    editorOpen,
    setEditorOpen,
  ] = useState(false);

  const [
    editingId,
    setEditingId,
  ] = useState<string | null>(
    null,
  );

  const [
    name,
    setName,
  ] = useState("");

  const [
    title,
    setTitle,
  ] = useState("");

  const [
    email,
    setEmail,
  ] = useState("");

  const [
    phone,
    setPhone,
  ] = useState("");

  const [
    contactType,
    setContactType,
  ] = useState("");

  const [
    isPrimary,
    setIsPrimary,
  ] = useState(false);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    saving,
    setSaving,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState("");

  const [
    notice,
    setNotice,
  ] = useState("");


  async function loadContacts() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `/api/admin/organizations/${organizationId}/contacts`,
        {
          cache: "no-store",
        },
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ??
            "Unable to load contacts."
        );
      }

      setContacts(data);

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load contacts."
      );

    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadContacts();
  }, [organizationId]);


  function resetEditor() {
    setEditingId(null);
    setName("");
    setTitle("");
    setEmail("");
    setPhone("");
    setContactType("");
    setIsPrimary(false);
    setEditorOpen(false);
  }


  function editContact(
    contact: Contact,
  ) {
    setEditingId(
      contact.id
    );

    setName(
      contact.name
    );

    setTitle(
      contact.title ?? ""
    );

    setEmail(
      contact.email ?? ""
    );

    setPhone(
      contact.phone ?? ""
    );

    setContactType(
      contact.contact_type ?? ""
    );

    setIsPrimary(
      contact.is_primary
    );

    setEditorOpen(true);
  }


  async function handleSave(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setSaving(true);
    setError("");
    setNotice("");

    try {
      const endpoint = editingId
        ? `/api/admin/organizations/${organizationId}/contacts/${editingId}`
        : `/api/admin/organizations/${organizationId}/contacts`;

      const response = await fetch(
        endpoint,
        {
          method:
            editingId
              ? "PUT"
              : "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            name: name.trim(),
            title:
              title || null,
            email:
              email || null,
            phone:
              phone || null,
            contact_type:
              contactType || null,
            is_primary:
              isPrimary,
          }),
        },
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ??
            "Unable to save contact."
        );
      }

      await loadContacts();

      setNotice(
        editingId
          ? "Contact updated."
          : "Contact added."
      );

      resetEditor();

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to save contact."
      );

    } finally {
      setSaving(false);
    }
  }


  if (loading) {
    return (
      <section className="admin-org-detail-card">
        <p className="admin-platform-empty">
          Loading contacts…
        </p>
      </section>
    );
  }


  return (
    <section className="admin-org-detail-card">
      <div className="admin-section-heading">
        <div>
          <p className="kicker">
            CONTACTS
          </p>

          <h3>
            People & roles
          </h3>
        </div>

        <button
          type="button"
          className="admin-inline-action"
          onClick={() => {
            setManaging(
              !managing
            );

            if (managing) {
              resetEditor();
            }
          }}
        >
          {managing
            ? "Done"
            : "Manage →"}
        </button>
      </div>

      {notice ? (
        <p className="admin-notice">
          {notice}
        </p>
      ) : null}

      {error ? (
        <p className="admin-error">
          {error}
        </p>
      ) : null}

      <div className="admin-contact-list">
        {contacts.length ? (
          contacts.map(
            (contact) => (
              <article
                key={contact.id}
                className="admin-contact-row"
              >
                <div>
                  <strong>
                    {contact.name}
                  </strong>

                  <span>
                    {contact.title
                      || contact.contact_type
                      || "Contact"}
                  </span>

                  {contact.email ? (
                    <small>
                      {contact.email}
                    </small>
                  ) : null}

                  {contact.phone ? (
                    <small>
                      {contact.phone}
                    </small>
                  ) : null}
                </div>

                <div className="admin-contact-row-actions">
                  {contact.is_primary ? (
                    <span className="admin-contact-primary">
                      Primary
                    </span>
                  ) : null}

                  {managing ? (
                    <button
                      type="button"
                      className="admin-inline-action"
                      onClick={() =>
                        editContact(
                          contact
                        )
                      }
                    >
                      Edit
                    </button>
                  ) : null}
                </div>
              </article>
            ),
          )
        ) : (
          <p className="admin-platform-empty">
            No contacts added.
          </p>
        )}
      </div>

      {managing && !editorOpen ? (
        <button
          type="button"
          className="admin-org-edit-button"
          onClick={() => {
            resetEditor();
            setEditorOpen(true);
          }}
        >
          + Add Contact
        </button>
      ) : null}

      {managing && editorOpen ? (
        <form
          className="admin-contact-form"
          onSubmit={handleSave}
        >
          <label>
            <span>Name</span>

            <input
              required
              value={name}
              onChange={(event) =>
                setName(
                  event.target.value
                )
              }
            />
          </label>

          <label>
            <span>Title</span>

            <input
              value={title}
              onChange={(event) =>
                setTitle(
                  event.target.value
                )
              }
              placeholder="CFO"
            />
          </label>

          <label>
            <span>Email</span>

            <input
              type="email"
              value={email}
              onChange={(event) =>
                setEmail(
                  event.target.value
                )
              }
            />
          </label>

          <label>
            <span>Phone</span>

            <input
              value={phone}
              onChange={(event) =>
                setPhone(
                  event.target.value
                )
              }
            />
          </label>

          <label>
            <span>
              Contact Function
            </span>

            <input
              value={contactType}
              onChange={(event) =>
                setContactType(
                  event.target.value
                )
              }
              placeholder="Accounting"
            />
          </label>

          <label className="admin-contact-primary-toggle">
            <input
              type="checkbox"
              checked={isPrimary}
              onChange={(event) =>
                setIsPrimary(
                  event.target.checked
                )
              }
            />

            <span>
              Primary contact
            </span>
          </label>

          <div className="admin-org-edit-actions">
            <button
              type="button"
              className="admin-cancel-button"
              onClick={
                resetEditor
              }
            >
              Cancel
            </button>

            <button
              type="submit"
              className="button button-primary"
              disabled={saving}
            >
              {saving
                ? "Saving…"
                : editingId
                  ? "Update Contact"
                  : "Add Contact"}
            </button>
          </div>
        </form>
      ) : null}
    </section>
  );
}
