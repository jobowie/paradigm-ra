"use client";

import { useEffect } from "react";

export function ServiceScrollMotion() {
  useEffect(() => {
    const root = document.documentElement;
    const elements = Array.from(
      document.querySelectorAll<HTMLElement>("[data-ra-reveal]")
    );

    root.classList.add("ra-motion-ready");

    const reducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;

    if (reducedMotion || !("IntersectionObserver" in window)) {
      elements.forEach((element) => {
        element.classList.add("is-ra-revealed");
      });

      return () => {
        root.classList.remove("ra-motion-ready");
      };
    }

    elements.forEach((element) => {
      const delay = element.dataset.raDelay;

      if (delay) {
        element.style.setProperty("--ra-reveal-delay", `${delay}ms`);
      }
    });

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;

          const element = entry.target as HTMLElement;
          element.classList.add("is-ra-revealed");
          observer.unobserve(element);
        });
      },
      {
        threshold: 0.12,
        rootMargin: "0px 0px -8% 0px",
      }
    );

    elements.forEach((element) => observer.observe(element));

    return () => {
      observer.disconnect();
      root.classList.remove("ra-motion-ready");
    };
  }, []);

  return null;
}
