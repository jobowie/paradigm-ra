import { HeroMotion } from "@/components/HeroMotion";
import { RaDiscovery } from "@/components/RaDiscovery";
import { services, site } from "@/content/site";

export default function HomePage() {
  return (
    <main>
      <section className="hero" id="top">
        <HeroMotion />
        <div className="hero-shade" />
        <header className="site-header shell">
          <a className="brand" href="#top" aria-label="Paradigm Ra home">
             <span className="brand-mark">RA</span>
             <span className="brand-name">PARADIGM RA</span>
          </a>
          <nav className="nav" aria-label="Primary navigation">
            <a href="#solutions">Solutions</a>
            <a href="#accounting">Accounting</a>
            <a href="#approach">Technology</a>
            <a href="#products">Products</a>
          </nav>
        </header>

        <div className="hero-content shell">
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
        <div className="section-intro">
          <div>
            <p className="kicker">WHAT WE BUILD</p>
            <h2>One business.<br />Connected systems.</h2>
          </div>
          <p>
            Paradigm Ra brings software, systems, financial operations, and business consulting into the same conversation—then helps design and implement the right solution.
          </p>
        </div>

        <div className="service-list">
          {services.map((service) => (
            <article className="service-row" key={service.number} id={service.number === "02" ? "accounting" : undefined}>
              <span className="service-number">{service.number}</span>
              <h3>{service.title}</h3>
              <p>{service.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="systems" id="approach">
        <div className="systems-art" aria-hidden="true">
          <span className="system-orbit orbit-a" />
          <span className="system-orbit orbit-b" />
          <span className="system-orbit orbit-c" />
        </div>
        <div className="shell systems-inner">
          <p className="kicker">PARADIGM RA SYSTEMS</p>
          <h2>From complexity<br />to clarity.</h2>
          <div className="flow-grid">
            <div><span>INPUT</span><strong>Operations</strong></div>
            <div><span>CONNECT</span><strong>Systems</strong></div>
            <div><span>UNDERSTAND</span><strong>Insight</strong></div>
            <div><span>ACT</span><strong>Decisions</strong></div>
          </div>
        </div>
      </section>

      <section className="product section shell" id="products">
        <div>
          <p className="kicker">PARADIGM RA / 001</p>
          <h2>Xyloglyphic</h2>
        </div>
        <div className="product-copy">
          <p>
            A proprietary production-workflow system designed to translate creative intent into structured DAW sessions—built by Paradigm Ra as the first expression of our product R&amp;D practice.
          </p>
          <span className="product-status">IN DEVELOPMENT</span>
        </div>
      </section>

      <section className="cta">
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
