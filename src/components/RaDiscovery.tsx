"use client";

import {
  FormEvent,
  useState,
} from "react";


type DiscoveryMode =
  | "closed"
  | "contact"
  | "discovery"
  | "complete";


interface RaDiscoveryProps {
  email: string;
}


interface ContactState {
  firstName: string;
  company: string;
  email: string;
}


interface TurnResponse {
  reply: string;
  stage: string;
  complete: boolean;
  recommendedNextStep: string;
}


const INITIAL_QUESTION =
  "What's creating the most friction in the business right now?";


export function RaDiscovery({
  email,
}: RaDiscoveryProps) {
  const [mode, setMode] =
    useState<DiscoveryMode>("closed");

  const [contact, setContact] =
    useState<ContactState>({
      firstName: "",
      company: "",
      email: "",
    });

  const [question, setQuestion] =
    useState(INITIAL_QUESTION);

  const [message, setMessage] =
    useState("");

  const [lastAnswer, setLastAnswer] =
    useState<string | null>(null);

  const [questionNumber, setQuestionNumber] =
    useState(1);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  async function beginDiscovery(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        "/api/discovery/session",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify(contact),
        },
      );

      const body =
        await response.json();

      if (!response.ok) {
        throw new Error(
          body.error ??
            "Unable to begin discovery.",
        );
      }

      setMode("discovery");
      setQuestion(INITIAL_QUESTION);
      setQuestionNumber(1);
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Unable to begin discovery.",
      );
    } finally {
      setLoading(false);
    }
  }


  async function submitAnswer(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const answer =
      message.trim();

    if (!answer || loading) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        "/api/discovery/turn",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            message: answer,
          }),
        },
      );

      const body =
        (await response.json()) as
          | TurnResponse
          | { error?: string };

      if (!response.ok) {
        throw new Error(
          "error" in body &&
          body.error
            ? body.error
            : "Discovery is temporarily unavailable.",
        );
      }

      const result =
        body as TurnResponse;

      setLastAnswer(answer);
      setMessage("");
      setQuestion(result.reply);

      if (result.complete) {
        setMode("complete");
        return;
      }

      setQuestionNumber(
        (current) => current + 1,
      );
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Discovery is temporarily unavailable.",
      );
    } finally {
      setLoading(false);
    }
  }


  function restart() {
    setMode("contact");

    setContact({
      firstName: "",
      company: "",
      email: "",
    });

    setQuestion(
      INITIAL_QUESTION,
    );

    setMessage("");
    setLastAnswer(null);
    setQuestionNumber(1);
    setError(null);
  }


  if (mode === "closed") {
    return (
      <div className="ra-launch">
        <button
          className="button button-primary"
          type="button"
          onClick={() =>
            setMode("contact")
          }
        >
          Begin discovery
          <span>→</span>
        </button>

        <p className="ra-launch-note">
          A short guided business assessment.
        </p>
      </div>
    );
  }


  return (
    <div className="ra-discovery">
      <div
        className="ra-discovery-glow"
        aria-hidden="true"
      />

      <div className="ra-discovery-header">
        <div>
          <p className="ra-system-label">
            <span className="ra-live-dot" />
            RA DISCOVERY
          </p>

          <p className="ra-system-state">
            Guided business discovery
          </p>
        </div>

        {mode !== "complete" && (
          <span className="ra-progress">
            {mode === "contact"
              ? "INTAKE"
              : `0${Math.min(
                  questionNumber,
                  9,
                )}`}
          </span>
        )}
      </div>


      {mode === "contact" && (
        <div className="ra-panel">
          <div className="ra-panel-copy">
            <p className="ra-overline">
              FIRST, WHO ARE WE
              WORKING WITH?
            </p>

            <h3>
              Start with the business.
            </h3>

            <p>
              Give us the basics first.
              From there, Ra will guide
              the conversation around the
              problem—not a generic form.
            </p>
          </div>

          <form
            className="ra-contact-form"
            onSubmit={beginDiscovery}
          >
            <label>
              <span>First name</span>
              <input
                type="text"
                autoComplete="given-name"
                maxLength={80}
                required
                value={
                  contact.firstName
                }
                onChange={(event) =>
                  setContact(
                    (current) => ({
                      ...current,
                      firstName:
                        event.target
                          .value,
                    }),
                  )
                }
              />
            </label>

            <label>
              <span>Company</span>
              <input
                type="text"
                autoComplete="organization"
                maxLength={160}
                required
                value={
                  contact.company
                }
                onChange={(event) =>
                  setContact(
                    (current) => ({
                      ...current,
                      company:
                        event.target
                          .value,
                    }),
                  )
                }
              />
            </label>

            <label className="ra-field-wide">
              <span>Email</span>
              <input
                type="email"
                autoComplete="email"
                maxLength={320}
                required
                value={
                  contact.email
                }
                onChange={(event) =>
                  setContact(
                    (current) => ({
                      ...current,
                      email:
                        event.target
                          .value,
                    }),
                  )
                }
              />
            </label>

            {error && (
              <p
                className="ra-error"
                role="alert"
              >
                {error}
              </p>
            )}

            <div className="ra-form-actions">
              <button
                className="ra-text-button"
                type="button"
                onClick={() =>
                  setMode("closed")
                }
              >
                Cancel
              </button>

              <button
                className="button button-primary"
                type="submit"
                disabled={loading}
              >
                {loading
                  ? "Opening..."
                  : "Begin discovery"}
                {!loading && (
                  <span>→</span>
                )}
              </button>
            </div>
          </form>
        </div>
      )}


      {mode === "discovery" && (
        <div className="ra-conversation">
          {lastAnswer && (
            <div className="ra-last-response">
              <span>
                YOUR LAST RESPONSE
              </span>

              <p>
                {lastAnswer}
              </p>
            </div>
          )}

          <div className="ra-current-question">
            <p className="ra-overline">
              CURRENT FOCUS
            </p>

            <h3>
              {question}
            </h3>
          </div>

          <form
            className="ra-response-form"
            onSubmit={submitAnswer}
          >
            <label
              htmlFor="ra-response"
              className="sr-only"
            >
              Your response
            </label>

            <textarea
              id="ra-response"
              value={message}
              maxLength={6000}
              rows={5}
              placeholder="Tell us what's happening..."
              onChange={(event) =>
                setMessage(
                  event.target.value,
                )
              }
            />

            {error && (
              <p
                className="ra-error"
                role="alert"
              >
                {error}
              </p>
            )}

            <div className="ra-response-actions">
              <span>
                One useful question
                at a time.
              </span>

              <button
                className="button button-primary"
                type="submit"
                disabled={
                  loading ||
                  !message.trim()
                }
              >
                {loading
                  ? "Processing..."
                  : "Continue"}
                {!loading && (
                  <span>→</span>
                )}
              </button>
            </div>
          </form>
        </div>
      )}


      {mode === "complete" && (
        <div className="ra-complete">
          <div className="ra-complete-mark">
            <span />
          </div>

          <p className="ra-overline">
            DISCOVERY COMPLETE
          </p>

          <h3>
            We have enough to
            work with.
          </h3>

          <p className="ra-complete-reply">
            {question}
          </p>

          <div className="ra-complete-actions">
            <a
              className="button button-primary"
              href={`mailto:${email}?subject=Paradigm%20Ra%20Discovery%20Follow-Up`}
            >
              Continue with Paradigm Ra
              <span>→</span>
            </a>

            <button
              className="ra-text-button"
              type="button"
              onClick={restart}
            >
              Start over
            </button>
          </div>

          <p className="ra-private-note">
            Your discovery stays with
            Paradigm Ra. Model and routing
            details are never exposed in
            this experience.
          </p>
        </div>
      )}
    </div>
  );
}
