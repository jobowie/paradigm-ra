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


async function readJsonResponse<T>(
  response: Response,
  fallbackMessage: string,
): Promise<T> {
  const raw = await response.text();

  if (!raw.trim()) {
    throw new Error(fallbackMessage);
  }

  try {
    return JSON.parse(raw) as T;
  } catch {
    throw new Error(fallbackMessage);
  }
}


const QUESTION_TRANSITION_MS = 200;


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

  const [transitioning, setTransitioning] =
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
      await readJsonResponse<{
        error?: string;
      }>(
        response,
        "We couldn’t begin the discovery just now. Please try again.",
      );

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
      await readJsonResponse<
        TurnResponse | { error?: string }
      >(
        response,
        "We couldn’t continue the discovery just now. Please try again.",
      );

    if (!response.ok) {
      throw new Error(
        "We couldn’t continue the discovery just now. Please try again.",
      );
    }

    const result =
      body as TurnResponse;

    setTransitioning(true);

    const transitionDelay =
      window.matchMedia(
        "(prefers-reduced-motion: reduce)",
      ).matches
        ? 0
        : QUESTION_TRANSITION_MS;

    if (transitionDelay > 0) {
      await new Promise<void>(
        (resolve) => {
          window.setTimeout(
            resolve,
            transitionDelay,
          );
        },
      );
    }

    setLastAnswer(answer);
    setMessage("");

    if (result.complete) {
      setTransitioning(false);
      setMode("complete");
      return;
    }

    setQuestion(result.reply);

    setQuestionNumber(
      (current) => current + 1,
    );

    window.requestAnimationFrame(
      () => {
        setTransitioning(false);
      },
    );
  } catch {
    setTransitioning(false);

    setError(
      "We couldn’t continue the discovery just now. Please try again.",
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
  setTransitioning(false);
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

          <div
          className={`ra-current-question${
            transitioning
              ? " is-transitioning"
              : ""
          }`}
          aria-live="polite"
        >
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
          Thanks, {contact.firstName}. We’ll be in touch.
        </h3>

        <p className="ra-complete-reply">
          Someone from the Paradigm Ra team will follow up to discuss
          what you shared, your priorities, and the best next step.
        </p>

        <div className="ra-complete-actions">
          <button
            className="ra-text-button"
            type="button"
            onClick={restart}
          >
            Start over
          </button>
        </div>

        <p className="ra-private-note">
          Your discovery stays with Paradigm Ra.
        </p>
        </div>
      )}
    </div>
  );
}
