# WMREPLAY replay contrast reconciliation — 2026-10-01

## Status

`AUDIT_PASS_WITH_RECONCILED_STALE_RECEIPT / NO_SOURCE_CHANGE`

The earlier `WMREPLAY-W8-A11Y-FALLBACK-20261001/report.json` recorded low light-theme colors (`#f0d69c`/`#cbb98f`) for the replay history banner. A fresh current-HEAD browser audit found that the existing high-specificity light-theme rules in `ReplayWorkspace.css` resolve the banner text to `#704609`, which passes the same contrast threshold. No product file was changed in this lane.

## Scope and safety

- Current nested MT5 source HEAD: `b4c5793`.
- Browser target: existing Vite `http://127.0.0.1:5173/` and local in-memory fixture `127.0.0.1:8010` only.
- Routes: loaded replay with historical cutoff `cursor=3`, Dashboard shell untouched.
- Viewports: 1440×900 and 390×844; themes: dark and light.
- No dependency install, axe package, broker, MT5 socket, provider, OAuth, secret, holdout, upload, deploy or destructive action.

## Current validation

Command:

```powershell
node D:/ANNAM/TradingWorkspace/planning/checkpoints/workspace-next-stage/WMREPLAY-W8-REPLAY-CONTRAST-20261001/current_contrast_audit.mjs
```

Result: **PASS**, `source_change=false`, 4 route/theme/viewport cases, zero document overflow, zero captured console errors, three banner text nodes per case, and every measured ratio ≥ 4.5. The exact colors, ratios and screenshots are in [report.json](report.json):

- [replay-contrast-dark-1440.png](replay-contrast-dark-1440.png)
- [replay-contrast-dark-390.png](replay-contrast-dark-390.png)
- [replay-contrast-light-1440.png](replay-contrast-light-1440.png)
- [replay-contrast-light-390.png](replay-contrast-light-390.png)

The script is a current fixture audit, not an axe/WCAG certification. It measures the three history-banner text nodes and does not close native browser zoom, full-bleed, canonical golden, or whole-route visual gates.

## Decision and resume

- Keep the existing `ReplayWorkspace.css` light-theme override; do not add a redundant token or dependency.
- Treat the older low-ratio rows as a stale/ordering-sensitive receipt requiring reconciliation, not as an unverified acceptance claim. The underlying a11y packet remains valid for its focus/name/overflow findings and still records native zoom/axe limitations.
- Re-run the 45/45 route matrix and full a11y fallback after any future CSS import/order change. Route any remaining low-contrast finding outside the banner to a narrowly owned CSS lane.
- Rollback: no product rollback; remove/supersede this checkpoint directory only.
