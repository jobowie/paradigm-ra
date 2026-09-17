"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";

import {
  AdminQuoteForm,
} from "@/components/AdminQuoteForm";


const PLATFORM_API =
  "https://ra-platform-api.onrender.com";

const SESSION_KEY =
  "paradigm_ra_admin_key";


async function verifyAdminKey(
  adminKey: string,
): Promise<boolean> {
  const response = await fetch(
    `${PLATFORM_API}/admin/quotes/verify`,
    {
      method: "POST",
      headers: {
        "X-RA-Admin-Key":
          adminKey,
      },
      cache: "no-store",
    },
  );

  return response.ok;
}


export function AdminWorkspace() {
  const [adminKey, setAdminKey] =
    useState("");

  const [unlocked, setUnlocked] =
    useState(false);

  const [ready, setReady] =
    useState(false);

  const [verifying, setVerifying] =
    useState(false);

  const [error, setError] =
    useState("");


  useEffect(() => {
    let active = true;

    async function restoreSession() {
      const saved =
        sessionStorage.getItem(
          SESSION_KEY,
        );

      if (!saved) {
        if (active) {
          setReady(true);
        }

        return;
      }

      try {
        const valid =
          await verifyAdminKey(
            saved,
          );

        if (!active) {
          return;
        }

        if (valid) {
          setAdminKey(saved);
          setUnlocked(true);
        } else {
          sessionStorage.removeItem(
            SESSION_KEY,
          );
        }

      } catch {
        if (active) {
          sessionStorage.removeItem(
            SESSION_KEY,
          );
        }

      } finally {
        if (active) {
          setReady(true);
        }
      }
    }

    restoreSession();

    return () => {
      active = false;
    };
  }, []);


  async function handleUnlock(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const trimmed =
      adminKey.trim();

    if (!trimmed) {
      return;
    }

    setVerifying(true);
    setError("");

    try {
      const valid =
        await verifyAdminKey(
          trimmed,
        );

      if (!valid) {
        sessionStorage.removeItem(
          SESSION_KEY,
        );

        setUnlocked(false);

        setError(
          "Invalid administrator key.",
        );

        return;
      }

      sessionStorage.setItem(
        SESSION_KEY,
        trimmed,
      );

      setAdminKey(trimmed);
      setUnlocked(true);

    } catch {
      setError(
        "Unable to verify administrator access.",
      );

    } finally {
      setVerifying(false);
    }
  }


  function handleLock() {
    sessionStorage.removeItem(
      SESSION_KEY,
    );

    setAdminKey("");
    setUnlocked(false);
    setError("");
  }


  if (!ready) {
    return (
      <p className="admin-intro">
        Verifying admin session…
      </p>
    );
  }


  if (!unlocked) {
    return (
      <div className="admin-access">
        <p className="kicker">
          ADMIN ACCESS
        </p>

        <h2>
          Paradigm Ra Workspace
        </h2>

        <p className="admin-intro">
          Enter your Paradigm Ra
          administrator key to access
          internal quote tools.
        </p>

        <form
          className="admin-access-form"
          onSubmit={handleUnlock}
        >
          <label>
            <span>
              Admin Key
            </span>

            <input
              type="password"
              autoComplete="off"
              required
              value={adminKey}
              onChange={(event) =>
                setAdminKey(
                  event.target.value,
                )
              }
            />
          </label>

          <button
            className="button button-primary"
            type="submit"
            disabled={verifying}
          >
            {verifying
              ? "Verifying…"
              : "Open Admin Workspace"}
          </button>

          {error ? (
            <p className="quote-error">
              {error}
            </p>
          ) : null}
        </form>
      </div>
    );
  }


  return (
    <>
      <div className="admin-workspace-header">
        <div>
          <p className="kicker">
            ADMIN WORKSPACE
          </p>

          <h2>
            New Client Quote
          </h2>
        </div>

        <button
          type="button"
          className="button button-secondary"
          onClick={handleLock}
        >
          Lock Admin
        </button>
      </div>

      <AdminQuoteForm
        adminKey={adminKey}
      />
    </>
  );
}
