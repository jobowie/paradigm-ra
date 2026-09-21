"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";

import {
  AdminQuoteForm,
} from "@/components/AdminQuoteForm";

import {
  AdminInvoicingWorkspace,
} from "@/components/AdminInvoicingWorkspace";


interface Membership {
  organization_id: string;
  role: string;
}


interface CurrentUser {
  user: {
    id: string;
    email: string;
    display_name: string;
    status: string;
    must_change_password: boolean;
  };

  memberships: Membership[];
}


function formatRole(
  role: string,
) {
  const labels: Record<
    string,
    string
  > = {
    paradigm_ra_admin:
      "Paradigm Ra Admin",
    paradigm_ra_executive:
      "Paradigm Ra Executive",
    client_admin:
      "Client Admin",
    partner_admin:
      "Partner Admin",
  };

  return labels[role] ?? role;
}


function RaAccessMark() {
  return (
    <div
      className="admin-login-mark"
      aria-hidden="true"
    >
      <span className="admin-login-orbit admin-login-orbit-a" />
      <span className="admin-login-orbit admin-login-orbit-b" />
      <span className="admin-login-core">
        <img
          src="/work/RALogo.png"
          alt=""
          className="admin-login-logo"
        />
      </span>

      <span className="admin-login-flare" />
    </div>
  );
}


export function AdminWorkspace() {
  const [
    currentUser,
    setCurrentUser,
  ] = useState<CurrentUser | null>(
    null,
  );

  const [ready, setReady] =
    useState(false);

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [
    currentPassword,
    setCurrentPassword,
  ] = useState("");

  const [
    newPassword,
    setNewPassword,
  ] = useState("");

  const [
    confirmPassword,
    setConfirmPassword,
  ] = useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [notice, setNotice] =
    useState("");

  const [
    activePlatform,
    setActivePlatform,
  ] = useState<
    "quotes" | "invoicing" | null
  >(null);


  useEffect(() => {
    let active = true;

    async function initialize() {
      try {
        const response = await fetch(
          "/api/auth/me",
          {
            cache: "no-store",
          },
        );

        if (
          response.ok
          && active
        ) {
          setCurrentUser(
            await response.json()
          );
        }

      } finally {
        if (active) {
          setReady(true);
        }
      }
    }

    initialize();

    return () => {
      active = false;
    };
  }, []);


  async function handleLogin(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setLoading(true);
    setError("");
    setNotice("");

    try {
      const response = await fetch(
        "/api/auth/login",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            email,
            password,
          }),
        },
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail
          ?? "Unable to sign in.",
        );
      }

      setCurrentUser({
        user: data.user,
        memberships:
          data.memberships,
      });

      setPassword("");

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to sign in.",
      );

    } finally {
      setLoading(false);
    }
  }


  async function handlePasswordChange(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setError("");
    setNotice("");

    if (
      newPassword
      !== confirmPassword
    ) {
      setError(
        "New passwords do not match."
      );
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        "/api/auth/change-password",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            current_password:
              currentPassword,
            new_password:
              newPassword,
          }),
        },
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail
          ?? "Unable to change password.",
        );
      }

      setCurrentUser(null);

      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");

      setNotice(
        "Password updated. Sign in again with your new password."
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to change password.",
      );

    } finally {
      setLoading(false);
    }
  }


  async function handleLogout() {
    await fetch(
      "/api/auth/logout",
      {
        method: "POST",
      },
    );

    setCurrentUser(null);
    setEmail("");
    setPassword("");
    setError("");
    setNotice("");
    setActivePlatform(null);
  }


  if (!ready) {
    return (
      <div className="shell admin-shell admin-shell-login">
        <div className="admin-session-check">
          <span className="admin-status-dot" />
          Verifying secure session
        </div>
      </div>
    );
  }


  if (!currentUser) {
    return (
      <div className="shell admin-shell admin-shell-login">
        <section className="admin-login-stage">
          <div className="admin-login-visual">
            <RaAccessMark />

            <div className="admin-login-brand">
              <p className="kicker">
                PARADIGM RA
              </p>

              <h1>
                Operational
                <span>
                  {" "}Access
                </span>
              </h1>

              <p>
                Secure entry to the
                Paradigm Ra operating
                environment.
              </p>

              <div className="admin-trust-line">
                <span>
                  Secure
                </span>

                <span>
                  Audited
                </span>

                <span>
                  Scoped
                </span>
              </div>
            </div>
          </div>

          <div className="admin-login-panel">
            <div className="admin-login-panel-head">
              <p className="kicker">
                ADMINISTRATION
              </p>

              <h2>
                Enter the platform
              </h2>

              <p>
                Sign in with your
                Paradigm Ra account.
              </p>
            </div>

            <form
              className="admin-access-form"
              onSubmit={handleLogin}
            >
              <label>
                <span>Email</span>

                <input
                  type="email"
                  autoComplete="username"
                  required
                  value={email}
                  onChange={(event) =>
                    setEmail(
                      event.target.value
                    )
                  }
                  placeholder="you@paradigmra.tech"
                />
              </label>

              <label>
                <span>Password</span>

                <input
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(event) =>
                    setPassword(
                      event.target.value
                    )
                  }
                  placeholder="Enter your password"
                />
              </label>

              <button
                className="button button-primary admin-login-button"
                type="submit"
                disabled={loading}
              >
                {loading
                  ? "Entering Platform…"
                  : "Enter Platform"}
              </button>

              {notice ? (
                <p
                  className="admin-notice"
                  aria-live="polite"
                >
                  {notice}
                </p>
              ) : null}

              {error ? (
                <p
                  className="admin-error"
                  role="alert"
                >
                  {error}
                </p>
              ) : null}
            </form>

            <div className="admin-login-foot">
              <span className="admin-status-dot" />

              Identity protected by
              scoped platform access.
            </div>
          </div>
        </section>
      </div>
    );
  }


  if (
    currentUser.user
      .must_change_password
  ) {
    return (
      <div className="shell admin-shell admin-shell-login">
        <section className="admin-login-stage">
          <div className="admin-login-visual">
            <RaAccessMark />

            <div className="admin-login-brand">
              <p className="kicker">
                IDENTITY SETUP
              </p>

              <h1>
                Claim your
                <span>
                  {" "}access
                </span>
              </h1>

              <p>
                Replace the temporary
                credential with a
                password only you know.
              </p>
            </div>
          </div>

          <div className="admin-login-panel">
            <div className="admin-login-panel-head">
              <p className="kicker">
                FIRST LOGIN
              </p>

              <h2>
                Create your password
              </h2>

              <p>
                Your temporary session
                will be revoked when
                the password changes.
              </p>
            </div>

            <form
              className="admin-access-form"
              onSubmit={
                handlePasswordChange
              }
            >
              <label>
                <span>
                  Temporary Password
                </span>

                <input
                  type="password"
                  autoComplete="current-password"
                  required
                  value={currentPassword}
                  onChange={(event) =>
                    setCurrentPassword(
                      event.target.value
                    )
                  }
                />
              </label>

              <label>
                <span>
                  New Password
                </span>

                <input
                  type="password"
                  autoComplete="new-password"
                  minLength={12}
                  required
                  value={newPassword}
                  onChange={(event) =>
                    setNewPassword(
                      event.target.value
                    )
                  }
                />
              </label>

              <label>
                <span>
                  Confirm New Password
                </span>

                <input
                  type="password"
                  autoComplete="new-password"
                  minLength={12}
                  required
                  value={confirmPassword}
                  onChange={(event) =>
                    setConfirmPassword(
                      event.target.value
                    )
                  }
                />
              </label>

              <button
                className="button button-primary admin-login-button"
                type="submit"
                disabled={loading}
              >
                {loading
                  ? "Securing Account…"
                  : "Set Private Password"}
              </button>

              {error ? (
                <p
                  className="admin-error"
                  role="alert"
                >
                  {error}
                </p>
              ) : null}
            </form>
          </div>
        </section>
      </div>
    );
  }


  const role =
    currentUser.memberships[0]
      ?.role
    ?? "unknown";


  return (
    <div className="shell admin-shell admin-shell-workspace">
      <div className="admin-workspace">
        <header className="admin-workspace-header">
          <div>
            <p className="kicker">
              PARADIGM RA PLATFORM
            </p>

            <h1>
              Administration
            </h1>

            <p className="admin-workspace-lede">
              Operational control for
              organizations,
              engagements, billing,
              and client delivery.
            </p>
          </div>

          <div className="admin-identity-card">
            <span className="admin-status-dot" />

            <div>
              <strong>
                {currentUser.user
                  .display_name}
              </strong>

              <span>
                {currentUser.user.email}
              </span>

              <small>
                {formatRole(role)}
              </small>
            </div>

            <button
              type="button"
              className="admin-signout"
              onClick={handleLogout}
            >
              Sign Out
            </button>
          </div>
        </header>

        <div className="admin-spectrum-rule" />

        {activePlatform === null ? (
          <section className="admin-platform-launcher">
            <div className="admin-launch-heading">
              <p className="kicker">
                OPERATIONS
              </p>

              <h2>
                Choose a workspace
              </h2>

              <p>
                Quotes and invoicing
                remain separate business
                states while sharing the
                same organization and
                engagement context.
              </p>
            </div>

            <div className="admin-platform-grid">
              <button
                type="button"
                className="admin-platform-card admin-platform-card-quotes"
                onClick={() =>
                  setActivePlatform(
                    "quotes"
                  )
                }
              >
                <span className="admin-platform-number">
                  01
                </span>

                <div>
                  <p className="kicker">
                    QUOTES
                  </p>

                  <h3>
                    Scope. Present.
                    Accept.
                  </h3>

                  <p>
                    Create client
                    proposals, generate
                    secure acceptance
                    links, and track quote
                    state.
                  </p>
                </div>

                <strong>
                  Enter Quotes →
                </strong>
              </button>

              <button
                type="button"
                className="admin-platform-card admin-platform-card-invoicing"
                onClick={() =>
                  setActivePlatform(
                    "invoicing"
                  )
                }
              >
                <span className="admin-platform-number">
                  02
                </span>

                <div>
                  <p className="kicker">
                    INVOICING
                  </p>

                  <h3>
                    Bill. Track.
                    Reconcile.
                  </h3>

                  <p>
                    Work from client
                    organizations and
                    engagements through
                    billing, invoices,
                    payments, and history.
                  </p>
                </div>

                <strong>
                  Enter Invoicing →
                </strong>
              </button>
            </div>
          </section>
        ) : null}

        {activePlatform === "quotes" ? (
          <section className="admin-tool-panel">
            <button
              type="button"
              className="admin-workspace-back"
              onClick={() =>
                setActivePlatform(null)
              }
            >
              ← Administration
            </button>

            <div className="admin-tool-heading">
              <div>
                <p className="kicker">
                  QUOTES
                </p>

                <h2>
                  Create client quote
                </h2>
              </div>

              <p>
                Build a scoped proposal
                and generate its secure
                acceptance link.
              </p>
            </div>

            <AdminQuoteForm />
          </section>
        ) : null}

        {activePlatform === "invoicing" ? (
          <section className="admin-tool-panel">
            <button
              type="button"
              className="admin-workspace-back"
              onClick={() =>
                setActivePlatform(null)
              }
            >
              ← Administration
            </button>

            <div className="admin-tool-heading">
              <div>
                <p className="kicker">
                  INVOICING
                </p>

                <h2>
                  Client billing
                </h2>
              </div>

              <p>
                Organization,
                engagement, billing
                terms, invoice state,
                and payment history.
              </p>
            </div>

            <AdminInvoicingWorkspace />
          </section>
        ) : null}
      </div>
    </div>
  );
}