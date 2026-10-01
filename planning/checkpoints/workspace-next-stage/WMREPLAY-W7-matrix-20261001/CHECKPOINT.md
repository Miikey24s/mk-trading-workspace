# WMREPLAY W7 locale/theme/motion matrix — 2026-10-01

**Owner:** `/root`  
**Scope:** read-only shell matrix for EN, light theme, reduced motion and responsive overflow.  
**Status:** bounded matrix passed; this is a supporting packet, not whole W7/W8 acceptance.

## Verification

Using the existing local Vite origin and intercepted overview payload (no real backend/provider), Playwright ran two modes at 1440×900:

- normal motion → language toggle to EN → light theme;
- `prefers-reduced-motion: reduce` → same EN/light toggles.

Both cases reported `document.documentElement.lang = en`, app theme `light`, `scrollWidth - innerWidth = 0`, no page errors and no unexpected console errors. Normal nav transitions remained `0.14s`; reduced-motion transitions collapsed to `1e-06s` (browser's computed CSS representation of zero-duration reduction). Screenshots and machine-readable output are in [runtime.json](runtime.json), [normal-en-light-1440.png](normal-en-light-1440.png) and [reduced-en-light-1440.png](reduced-en-light-1440.png).

## Limits and resume

This matrix does not prove native browser zoom, automated axe/WCAG tree, screenshot pixel-diff, chart throughput/full-bleed or long-duration heap stability. Resume from `RESUME.md`, then use the remaining W8 chart/visual gates before changing `SHELL_SKELETON_MODE`.
