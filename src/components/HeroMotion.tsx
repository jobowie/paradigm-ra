"use client";

import { useEffect, useRef } from "react";

export function HeroMotion() {
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduceMotion) return;

    const onPointerMove = (event: PointerEvent) => {
      const rect = root.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / rect.width - 0.5) * 18;
      const y = ((event.clientY - rect.top) / rect.height - 0.5) * 18;
      root.style.setProperty("--mx", `${x}px`);
      root.style.setProperty("--my", `${y}px`);
    };

    const onPointerLeave = () => {
      root.style.setProperty("--mx", "0px");
      root.style.setProperty("--my", "0px");
    };

    root.addEventListener("pointermove", onPointerMove);
    root.addEventListener("pointerleave", onPointerLeave);

    return () => {
      root.removeEventListener("pointermove", onPointerMove);
      root.removeEventListener("pointerleave", onPointerLeave);
    };
  }, []);

  return (
    <div ref={rootRef} className="hero-art" aria-hidden="true">
      <div className="ambient ambient-a" />
      <div className="ambient ambient-b" />
      <div className="light-sweep" />
      <svg className="hero-svg" viewBox="0 0 1200 820" preserveAspectRatio="xMidYMid slice">
        <defs>
          <linearGradient id="heroBg" x1="0" y1="1" x2="1" y2="0">
            <stop offset="0" stopColor="#08090b" />
            <stop offset="1" stopColor="#151925" />
          </linearGradient>
          <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#8b7cff" stopOpacity=".32" />
            <stop offset="1" stopColor="#7bd8ff" stopOpacity=".025" />
          </linearGradient>
          <linearGradient id="signal" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stopColor="#8b7cff" stopOpacity=".08" />
            <stop offset=".55" stopColor="#9c90ff" stopOpacity=".88" />
            <stop offset="1" stopColor="#79dcff" stopOpacity=".08" />
          </linearGradient>
          <filter id="blur"><feGaussianBlur stdDeviation="24" /></filter>
        </defs>
        <rect width="1200" height="820" fill="url(#heroBg)" />
        <circle className="orb" cx="970" cy="180" r="180" fill="#8b7cff" opacity=".09" filter="url(#blur)" />
        <g className="architecture">
          <path d="M635 60 L1085 -15 L1205 565 L735 725 Z" fill="url(#glass)" stroke="#363949" strokeWidth="1.4" />
          <path d="M690 132 L1042 88 L1090 515 L765 603 Z" fill="none" stroke="#8b7cff" strokeOpacity=".28" strokeWidth="1.4" />
          <path d="M742 205 L995 180 L1024 458 L798 508 Z" fill="#0d0f14" fillOpacity=".58" stroke="#343746" />
          <g opacity=".38" stroke="#515466">
            <line x1="772" y1="248" x2="996" y2="224" />
            <line x1="779" y1="298" x2="1002" y2="276" />
            <line x1="786" y1="348" x2="1008" y2="327" />
            <line x1="793" y1="398" x2="1015" y2="379" />
          </g>
        </g>
        <g fill="none" stroke="url(#signal)" strokeLinecap="round">
          <path className="signal signal-1" d="M350 690 C525 335 765 180 1135 315" strokeWidth="2.3" />
          <path className="signal signal-2" d="M300 750 C545 430 810 305 1190 418" strokeWidth="1.7" />
          <path className="signal signal-3" d="M445 790 C615 515 865 420 1210 520" strokeWidth="1.25" />
        </g>
        <g fill="#9c90ff">
          <circle className="node node-1" cx="645" cy="405" r="6" />
          <circle className="node node-2" cx="825" cy="305" r="5" />
          <circle className="node node-3" cx="980" cy="346" r="6" />
        </g>
      </svg>
    </div>
  );
}
