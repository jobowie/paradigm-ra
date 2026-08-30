import Link from "next/link";
import { MobileNav } from "@/components/MobileNav";
import { ServiceScrollMotion } from "@/components/ServiceScrollMotion";
import { site } from "@/content/site";

export type ServiceCapability = {
  title: string;
  description: string;
};

export type ServiceStep = {
  label: string;
  title: string;
  description: string;
};

export type ServicePageContent = {
  kicker: string;
  title: string;
  lede: string;
  principleTitle: string;
  principleBody: string;
  capabilities: ServiceCapability[];
  exampleTitle: string;
  exampleBody: string;
  exampleFlow: string[];
  fitTitle: string;
  fitBody: string;
  steps: ServiceStep[];
};

type ServicePageProps = {
  content: ServicePageContent;
};

export function ServicePage({ content }: ServicePageProps) {
  return (
    <main className="service-page">
      <ServiceScrollMotion />
      <header className="site-header service-site-header shell">
        <Link className="brand" href="/" aria-label="Paradigm Ra home">
          <img
            className="brand-logo"
            src="/work/RALogo.png"
            alt=""
            aria-hidden="true"
          />
          <span className="brand-name">PARADIGM RA</span>
        </Link>

        <nav className="nav service-nav" aria-label="Service navigation">
          <Link href="/#solutions">Solutions</Link>
          <Link href="/#accounting">Accounting</Link>
          <Link href="/#approach">Technology</Link>
          <Link href="/#products">Products</Link>
        </nav>

        <MobileNav />
      </header>

      <section className="service-hero">
        <div className="shell service-hero-inner">
          <div className="service-hero-copy">
            <p className="kicker" data-ra-reveal="lock">{content.kicker}</p>
            <h1 data-ra-reveal="lock" data-ra-delay="70">{content.title}</h1>
            <p className="service-lede" data-ra-reveal="lock" data-ra-delay="140">{content.lede}</p>

            <div className="actions" data-ra-reveal="lock" data-ra-delay="210">
              <Link
                className="button button-primary service-primary-cta"
                href="/?discovery=start#discovery"
              >
                Begin Discovery <span>→</span>
              </Link>

              <a
                className="button button-secondary"
                href={`mailto:${site.email}`}
              >
                Schedule a consultation
              </a>
            </div>
          </div>

          <div className="service-hero-signal" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
        </div>
      </section>

      <section className="service-section shell">
        <div className="service-section-intro" data-ra-reveal="lock">
          <p className="kicker">THE PRINCIPLE</p>
          <h2>{content.principleTitle}</h2>
          <p>{content.principleBody}</p>
        </div>
      </section>

      <section className="service-section shell">
        <div className="service-section-heading" data-ra-reveal="lock">
          <p className="kicker">WHAT WE HELP WITH</p>
          <h2>Practical systems. Clear outcomes.</h2>
        </div>

        <div className="service-capabilities">
          {content.capabilities.map((capability, index) => (
            <article
              className="service-capability"
              key={capability.title}
              data-ra-reveal="lock"
              data-ra-delay={index * 55}
            >
              <span>{String(index + 1).padStart(2, "0")}</span>
              <h3>{capability.title}</h3>
              <p>{capability.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="service-example">
        <div className="shell service-example-inner">
          <div data-ra-reveal="left">
            <p className="kicker">WHAT THIS CAN LOOK LIKE</p>
            <h2>{content.exampleTitle}</h2>
            <p>{content.exampleBody}</p>
          </div>

          <div className="service-flow" aria-label="Example workflow" data-ra-reveal="right" data-ra-delay="100">
            {content.exampleFlow.map((item, index) => (
              <div key={item}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <strong>{item}</strong>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="service-section shell">
        <div className="service-fit">
          <div data-ra-reveal="left">
            <p className="kicker">WHO THIS IS FOR</p>
            <h2>{content.fitTitle}</h2>
          </div>
          <p data-ra-reveal="right" data-ra-delay="90">{content.fitBody}</p>
        </div>
      </section>

      <section className="service-section shell">
        <div className="service-section-heading" data-ra-reveal="lock">
          <p className="kicker">HOW WE WORK</p>
          <h2>Understand before implementation.</h2>
        </div>

        <div className="service-steps">
          {content.steps.map((step, index) => (
            <article
              key={step.title}
              data-ra-reveal="lock"
              data-ra-delay={index * 60}
            >
              <span>{String(index + 1).padStart(2, "0")}</span>
              <div>
                <p>{step.label}</p>
                <h3>{step.title}</h3>
                <p>{step.description}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="service-final-cta">
        <div className="shell" data-ra-reveal="lock">
          <p className="kicker">START WITH THE PROBLEM</p>
          <h2>You do not need to know what software you need.</h2>
          <p>
            Tell us what is happening in your business today. We will help
            determine what deserves to change and whether automation is
            actually the right answer.
          </p>

          <Link
            className="button button-primary service-primary-cta"
            href="/?discovery=start#discovery"
          >
            Begin Discovery <span>→</span>
          </Link>
        </div>
      </section>

      <footer className="footer shell">
        <span>© 2026 Paradigm Ra</span>
        <span>{site.tagline}</span>
      </footer>
    </main>
  );
}
