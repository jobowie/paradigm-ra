"use client";

import Link from "next/link";
import { useState } from "react";

const links = [
  {
    label: "Solutions",
    href: "/#solutions",
  },
  {
    label: "Accounting",
    href: "/#accounting",
  },
  {
    label: "Technology",
    href: "/#approach",
  },
  {
    label: "Products",
    href: "/#products",
  },
];

export function MobileNav() {
  const [open, setOpen] =
    useState(false);

  return (
    <div
      className={`mobile-nav ${
        open ? "is-open" : ""
      }`}
    >
      <button
        className="mobile-nav-toggle"
        type="button"
        aria-label={
          open
            ? "Close navigation"
            : "Open navigation"
        }
        aria-expanded={open}
        aria-controls="mobile-navigation"
        onClick={() =>
          setOpen(
            (current) => !current,
          )
        }
      >
        <span />
        <span />
        <span />
      </button>

      <nav
        id="mobile-navigation"
        className="mobile-nav-panel"
        aria-label="Mobile navigation"
      >
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            onClick={() =>
              setOpen(false)
            }
          >
            {link.label}
            <span
              aria-hidden="true"
            >
              →
            </span>
          </Link>
        ))}
      </nav>
    </div>
  );
}
