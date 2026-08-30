import { HeroMotion } from "@/components/HeroMotion";
import { RaDiscovery } from "@/components/RaDiscovery";
import { MobileNav } from "@/components/MobileNav";
import { ServiceScrollMotion } from "@/components/ServiceScrollMotion";
import { services, site } from "@/content/site";

export default function HomePage() {
  return (
    <main>
      <ServiceScrollMotion />
      <section className="hero" id="top">
        <HeroMotion />
        <div className="hero-shade" />
        <header className="site-header shell">
          <a className="brand" href="#top" aria-label="Paradigm Ra home">
            <img
              className="brand-logo"
              src="/work/RALogo.png"
              alt=""
              aria-hidden="true"
            />
            <span className="brand-name">PARADIGM RA</span>
          </a>
          <nav className="nav" aria-label="Primary navigation">
            <a href="#solutions">Solutions</a>
            <a href="#accounting">Accounting</a>
            <a href="#approach">Technology</a>
            <a href="#products">Products</a>
          </nav>

          <MobileNav />
        </header>

        <div className="hero-content hero-grid shell">
          <div className="hero-copy">
            <p className="eyebrow"><span className="status-dot" /> SOFTWARE · SYSTEMS · FINANCIAL CLARITY</p>
            <h1>Clarity,<br /><span>engineered.</span></h1>
            <p className="hero-lede">
              Software, systems, accounting, automation, and consulting designed to reduce friction and make your business easier to operate.
            </p>
            <div className="actions">
              <a className="button button-primary" href="#solutions">Explore solutions <span>→</span></a>
              <a className="button button-secondary" href="#approach">How we work</a>
            </div>
          </div>
        </div>
      </section>

      <section className="section shell" id="solutions">
        <div className="section-intro" data-ra-reveal="lock">
          <div>
            <p className="kicker">WHAT WE BUILD</p>
            <h2>One business.<br />Connected systems.</h2>
          </div>
          <p>
            Paradigm Ra brings software, systems, financial operations, and business consulting into the same conversation—then helps design and implement the right solution.
          </p>
        </div>

        <div className="service-list">
          {services.map((service, index) => {
            const href =
              service.number === "01"
                ? "/services/web-software-solutions"
                : service.number === "02"
                  ? "/services/accounting-operational-solutions"
                  : "/services/business-systems-technical-consulting";

            return (
              <a
                className={`service-row service-row-${index + 1}`}
                key={service.number}
                id={service.number === "02" ? "accounting" : undefined}
                href={href}
                aria-label={`Explore ${service.title}`}
                data-ra-reveal="lock"
                data-ra-delay={index * 70}
              >
                <span className="service-number">{service.number}</span>
                <h3>{service.title}</h3>
                <p>{service.description}</p>
              </a>
            );
          })}
        </div>
      </section>

      <section className="systems" id="approach">
        <div className="systems-art" aria-hidden="true">
          <span className="system-orbit orbit-a" />
          <span className="system-orbit orbit-b" />
          <span className="system-orbit orbit-c" />
        </div>
        <div className="shell systems-inner" data-ra-reveal="lock">
          <p className="kicker">PARADIGM RA SYSTEMS</p>
          <h2>From complexity<br />to clarity.</h2>
          <div className="flow-grid">
            <div><span>INPUT</span><strong>Operations</strong></div>
            <div><span>CONNECT</span><strong>Systems</strong></div>
            <div><span>UNDERSTAND</span><strong>Insight</strong></div>
            <div><span>ACT</span><strong>Decisions</strong></div>
          </div>

          <a
            className="systems-service-link"
            href="/services/business-automation"
          >
            Explore Business Automation + Integration
            <span aria-hidden="true">→</span>
          </a>
        </div>
      </section>

      <section className="product section shell" id="products">
        <div className="product-heading" data-ra-reveal="left">
          <p className="kicker">PRODUCT ENGINEERING / PARADIGM RA</p>
          <h2>Xyloglyphic</h2>
          <p className="product-subline">
            Build the environment. Keep the authorship.
          </p>
        </div>

        <div className="product-copy" data-ra-reveal="right" data-ra-delay="100">
          <div className="product-visual">
            <img
              src="/work/xyloglyphic-product.jpg"
              alt="Xyloglyphic desktop music production system"
            />
          </div>

          <p>
            A desktop music-production system that translates creative intent
            into structured DAW sessions through deterministic orchestration,
            reusable session blueprints, and isolated DAW integrations.
          </p>

          <div
            className="product-proof"
            aria-label="Xyloglyphic capabilities"
          >
            <span>Desktop software</span>
            <span>Session blueprints</span>
            <span>DAW orchestration</span>
            <span>FL Studio integration</span>
          </div>

          <span className="product-status">
            ACTIVE PRODUCT R&amp;D
          </span>
        </div>
      </section>

      <section className="client-work" id="work">
        <div className="shell client-work-inner">
          <div className="client-work-heading" data-ra-reveal="left">
            <p className="kicker">CLIENT DELIVERY / PARADIGM RA</p>
            <h2>MCT VISIONS ENT</h2>
            <p className="client-project-line">
              From vision to digital presence.
            </p>
          </div>

          <div className="client-work-copy" data-ra-reveal="right" data-ra-delay="100">
            <div className="client-work-visuals">
            <button
              type="button"
              className="client-visual client-visual-primary"
              aria-label="View MCT Visions website in full color"
            >
              <img
                src="/work/mct-visions-site.jpg"
                alt="MCT Visions Entertainment website"
              />
            </button>

            <button
              type="button"
              className="client-visual client-visual-campaign"
              aria-label="View Cold Feet campaign artwork in full color"
            >
              <img
                src="/work/mct-cold-feet.jpg"
                alt="Cold Feet promotional campaign artwork"
              />
            </button>
          </div>

          <p>
              Website design and development, responsive implementation,
              digital brand support, and promotional collateral created
              around MCT Visions Entertainment's film and event work.
            </p>

            <div
              className="client-work-proof"
              aria-label="MCT Visions project deliverables"
            >
              <span>Website development</span>
              <span>Responsive experience</span>
              <span>Digital brand support</span>
              <span>Campaign collateral</span>
            </div>

            <div className="client-work-meta">
              <span>CLIENT PROJECT</span>
              <a
                href="https://mctvisions.com"
                target="_blank"
                rel="noreferrer"
              >
                Visit MCT Visions <span aria-hidden="true">↗</span>
              </a>
            </div>
          </div>
        </div>
      </section>

      <section className="cta" id="discovery">
        <div className="shell cta-inner">
          <p className="kicker">START A CONVERSATION</p>
          <h2>Better systems begin with a clearer problem.</h2>
          <p>Tell us what is slowing your business down. We’ll help identify where software, automation, or accounting systems can create leverage.</p>
          <RaDiscovery email={site.email} />
          <p className="email-note">
            Prefer email?{" "}
            <a href={`mailto:${site.email}`}>{site.email}</a>
          </p>
        </div>
      </section>

      <footer className="footer shell">
        <span>© 2026 Paradigm Ra</span>
        <span>{site.tagline}</span>
      </footer>
    </main>
  );
}
