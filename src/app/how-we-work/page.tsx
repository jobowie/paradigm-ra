import type { Metadata } from "next";
import Link from "next/link";

import { MobileNav } from "@/components/MobileNav";
import { ServiceScrollMotion } from "@/components/ServiceScrollMotion";
import { site } from "@/content/site";

export const metadata: Metadata = {
  title: "How We Work | Paradigm Ra",
  description:
    "Learn how Paradigm Ra moves from business discovery to scoped implementation, proposals, delivery, and ongoing support.",
  alternates: {
    canonical: "/how-we-work",
  },
  openGraph: {
    title: "How We Work | Paradigm Ra",
    description:
      "Discovery first. Scope before price. Clear implementation and support built around the business need.",
    url: "/how-we-work",
    siteName: "Paradigm Ra",
    type: "website",
  },
};

const engagementTypes = [
  {
    number: "01",
    title: "Build",
    body:
      "Websites, portals, internal tools, applications, and custom digital experiences designed around how the business actually operates.",
  },
  {
    number: "02",
    title: "Integrate",
    body:
      "Automation, AI, APIs, data flows, system connections, and workflows that help existing tools work together more effectively.",
  },
  {
    number: "03",
    title: "Support",
    body:
      "Ongoing technical, operational, accounting, maintenance, implementation, and advisory support when the work continues beyond launch.",
  },
];

export default function HowWeWorkPage() {
  return (
    <main className="how-page">
      <ServiceScrollMotion />
      <section className="how-hero">
        <div className="how-hero-art" aria-hidden="true">
          <span className="how-orbit how-orbit-a" />
          <span className="how-orbit how-orbit-b" />
          <span className="how-orbit how-orbit-c" />
          <span className="how-core" />
        </div>

        <header className="site-header shell">
          <Link className="brand" href="/" aria-label="Paradigm Ra home">
            <img
              className="brand-logo"
              src="/work/RALogo.png"
              alt=""
              aria-hidden="true"
            />
            <span className="brand-name">PARADIGM RA</span>
          </Link>

          <nav className="nav" aria-label="Primary navigation">
            <Link href="/#solutions">Solutions</Link>
            <Link href="/#accounting">Accounting</Link>
            <Link href="/#approach">Technology</Link>
            <Link href="/#products">Products</Link>
            <Link href="/how-we-work">How We Work</Link>
          </nav>

          <MobileNav />
        </header>

        <div className="shell how-hero-inner">
          <div className="how-hero-copy" data-ra-reveal="left">
            <p className="kicker">HOW WE WORK</p>

            <h1>
              Clear process.
              <br />
              <span>Scoped to the business.</span>
            </h1>

            <p className="how-hero-lede">
              Our goal is to understand what you&apos;re trying to accomplish,
              define the right scope, and build the solution around your
              business—not force you into a predetermined package.
            </p>

            <div className="actions">
              <Link
                className="button button-primary"
                href="/?discovery=start#discovery"
              >
                Start Ra Discovery <span>→</span>
              </Link>

              <Link className="button button-secondary" href="/#solutions">
                Explore solutions
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="how-section shell">
        <div className="how-step" data-ra-reveal="lock">
          <div className="how-step-marker">
            <span>01</span>
          </div>

          <div className="how-step-copy">
            <p className="kicker">START WITH THE BUSINESS NEED</p>
            <h2>Understand before prescribing.</h2>

            <p>
              Every engagement begins with context. You may already know
              exactly what you need, or you may simply know what you want to
              build, improve, connect, or explore.
            </p>

            <p>
              Ra Discovery helps us understand the objective without assuming
              the solution in advance.
            </p>

            <div className="how-signal-grid" data-ra-reveal="lock" data-ra-delay="80">
              <span>What matters</span>
              <span>What already exists</span>
              <span>What is known</span>
              <span>What remains unknown</span>
              <span>What should happen next</span>
            </div>
          </div>
        </div>
      </section>

      <section className="how-section how-section-dark">
        <div className="shell">
          <div className="how-step" data-ra-reveal="lock">
            <div className="how-step-marker">
              <span>02</span>
            </div>

            <div className="how-step-copy">
              <p className="kicker">DEFINE THE ENGAGEMENT</p>
              <h2>The right shape for the work.</h2>

              <p>
                An engagement may involve one area or a combination. These
                aren&apos;t pricing tiers. They describe the kind of
                responsibility Paradigm Ra is taking on.
              </p>

              <div className="how-engagement-list">
                {engagementTypes.map((item, index) => (
                  <div
                    className="how-engagement-row"
                    key={item.title}
                    data-ra-reveal="lock"
                    data-ra-delay={index * 70}
                  >
                    <span>{item.number}</span>
                    <h3>{item.title}</h3>
                    <p>{item.body}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="how-section shell">
        <div className="how-step" data-ra-reveal="lock">
          <div className="how-step-marker">
            <span>03</span>
          </div>

          <div className="how-step-copy">
            <p className="kicker">SCOPE BEFORE PRICE</p>
            <h2>Price what we are actually responsible for delivering.</h2>

            <p>
              Two businesses can ask for what sounds like the same solution
              and require very different work. Investment is based on the
              actual engagement rather than a predetermined package.
            </p>

            <div className="how-factor-line" data-ra-reveal="lock" data-ra-delay="80">
              <span>Scope</span>
              <span>Complexity</span>
              <span>Integrations</span>
              <span>Existing systems</span>
              <span>Content</span>
              <span>Timeline</span>
              <span>Support</span>
            </div>
          </div>
        </div>
      </section>

      <section className="how-section how-section-dark">
        <div className="shell">
          <div className="how-step" data-ra-reveal="lock">
            <div className="how-step-marker">
              <span>04</span>
            </div>

            <div className="how-step-copy">
              <p className="kicker">PROPOSAL + QUOTE</p>
              <h2>Make the commitment visible.</h2>

              <p>
                Once the scope is understood, Paradigm Ra provides a formal
                proposal or quote that can define deliverables, boundaries,
                milestones, payment schedules, support options, and applicable
                third-party costs.
              </p>

              <blockquote className="how-quote" data-ra-reveal="left" data-ra-delay="80">
                Quoted pricing reflects the scope, availability, and
                requirements known at the time of the proposal and remains
                valid through the expiration date shown on the quote.
              </blockquote>
            </div>
          </div>
        </div>
      </section>

      <section className="how-section shell">
        <div className="how-step" data-ra-reveal="lock">
          <div className="how-step-marker">
            <span>05</span>
          </div>

          <div className="how-step-copy">
            <p className="kicker">BUILD WITH VISIBILITY</p>
            <h2>The approved scope stays authoritative.</h2>

            <p>
              Implementation moves through defined stages rather than
              disappearing into a black box. What was agreed remains the
              reference point for the work.
            </p>

            <p>
              If requirements materially change, we make the change visible,
              revisit the boundary, and determine the right next step before
              silently expanding the engagement.
            </p>

            <div className="how-flow" data-ra-reveal="lock" data-ra-delay="80">
              <span>Understand</span>
              <i>→</i>
              <span>Scope</span>
              <i>→</i>
              <span>Build</span>
              <i>→</i>
              <span>Verify</span>
            </div>
          </div>
        </div>
      </section>

      <section className="how-section how-section-dark">
        <div className="shell">
          <div className="how-step" data-ra-reveal="lock">
            <div className="how-step-marker">
              <span>06</span>
            </div>

            <div className="how-step-copy">
              <p className="kicker">LAUNCH ISN&apos;T ALWAYS THE END</p>
              <h2>Continue where it creates value.</h2>

              <p>
                Some engagements finish when the solution launches. Others
                continue through maintenance, bookkeeping and accounting
                support, automation management, integrations, technical
                support, or additional development.
              </p>

              <p>
                Ongoing work is scoped separately so the original engagement
                never quietly becomes an undefined commitment.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="how-final-cta">
        <div className="how-final-art" aria-hidden="true">
          <span />
          <span />
          <span />
        </div>

        <div className="shell how-final-inner" data-ra-reveal="left">
          <p className="kicker">START A CONVERSATION</p>

          <h2>
            Ready to explore what
            <br />
            Paradigm Ra can build with you?
          </h2>

          <p>
            Tell us what you&apos;re trying to accomplish. Ra Discovery will
            help us understand the need and determine the right next step.
          </p>

          <Link
            className="button button-primary"
            href="/?discovery=start#discovery"
          >
            Start Ra Discovery <span>→</span>
          </Link>

          <span className="how-final-note">
            Discovery is complimentary. No predefined package required.
          </span>
        </div>
      </section>

      <footer className="footer shell">
        <span>© 2026 Paradigm Ra</span>
        <span>{site.tagline}</span>
      </footer>
    </main>
  );
}
