"use client";

import { useEffect, useState } from "react";

export default function LandingBackgroundVideo() {
  const [reduceMotion, setReduceMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    const syncMotionPreference = () => setReduceMotion(mediaQuery.matches);

    syncMotionPreference();
    mediaQuery.addEventListener("change", syncMotionPreference);
    return () => mediaQuery.removeEventListener("change", syncMotionPreference);
  }, []);

  if (reduceMotion) {
    return null;
  }

  return (
    <video
      aria-hidden="true"
      autoPlay
      className="pointer-events-none absolute inset-0 -z-20 h-full w-full object-cover"
      loop
      muted
      playsInline
      preload="metadata"
    >
      <source src="/assets/main-bg.mp4" type="video/mp4" />
    </video>
  );
}
