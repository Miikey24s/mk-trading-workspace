# WMREPLAY Prop mobile density — checkpoint 2026-10-01

- **Slice:** W8 follow-up — Prop session metadata/header density at narrow widths
- **Owner:** `/root/prop_mobile_density`
- **Date:** 2026-10-01 (Asia/Ho_Chi_Minh)
- **Status:** `SCOPED_PASS / SOURCE_CHANGED`
- **Nested source revision:** `52482e4` (`fix(mt5-ui): stack prop metadata on narrow screens`)

## Request and allowed scope

The owning lane was asked to inspect the Prop route at 390 px, identify the small root cause behind the remaining metadata/session-header density finding, make only a reversible CSS fix, validate 390/768/1440, and preserve all broker/provider/owner gates. Product source ownership was limited to:

- `projects/mt5-tradingview-backtester/foundation_v2/web/src/styles.css`

The temporary fixture probe used for this run was deleted after evidence capture. No API, React state, backend, provider, broker, OAuth, secret, dependency, deployment or WIP file was changed.

## Diagnosis

At 390×844 with the local Prop fixture and the normal expanded shell rail, the Prop content column was 170 px wide. The base selector `.fx-content > .prop-shell > .prop-topbar { display: flex; }` has higher specificity than the mobile `.prop-topbar { display: grid; }` rule. The topbar therefore remained a flex row and shrank its title block to about 91 px. The section headers had the same flex-shrink problem: `.prop-section-head small { white-space: nowrap; }` reserved the metadata width, shrinking `Generic / custom practice profile` to about 33 px and wrapping it into a tall column of characters. This made the topbar and session metadata difficult to read even though the page had no horizontal overflow.

## Change

At `@media (max-width: 520px)` in `foundation_v2/web/src/styles.css`:

- override the higher-specificity mounted-shell selector so `.prop-topbar` actually becomes a one-column grid;
- make `.prop-section-head` a two-row grid with a small gap;
- allow section metadata to wrap;
- keep a refresh button aligned to the start of its own row.

This changes only narrow-screen layout. Desktop and tablet rules are unchanged; API/state semantics and safety copy are unchanged.

## Evidence

The local Playwright fixture is the existing `run_prop_ui_acceptance.mjs` harness with a temporary, deleted probe inserted only for this checkpoint. It intercepts local `/api/v2/prop/**` fixture responses and does not call a real backend/provider/broker.

390 px probe (`evidence/prop-probe-390.json`):

- viewport/document width: `390 / 390`, overflow `0`;
- topbar display: `grid`, title block width `170 px`, title height `52.875 px` (two readable lines);
- session section header display: `grid`, title block width `170 px`;
- `Generic / custom practice profile` height reduced to `32 px` (two normal lines) from the prior `128 px` narrow flex column;
- `1 phase · UTC · static loss` is fully visible on its own row;
- fixture state remains discoverable: `attempt-persisted-1`, cursor `#412`, report/objective content and simulation-only lock remain present.

Visual artifact: [prop-inspect-390.png](evidence/prop-inspect-390.png). The screenshot shows readable `Luyện challenge`, a full-width simulation lock, and stacked session metadata in the narrow route column.

The same fixture run produced responsive screenshots for 1440/768/360 and passed the existing full Prop acceptance flow (output recorded in [prop-acceptance.log](evidence/prop-acceptance.log)). Representative images:

- [prop-ui-fixture-1440.png](evidence/prop-ui-fixture-1440.png)
- [prop-ui-fixture-768.png](evidence/prop-ui-fixture-768.png)
- [prop-ui-fixture-360.png](evidence/prop-ui-fixture-360.png)

The harness also covered simulation-only lock, persisted session/attempt discovery, create/reload/resume, lifecycle transitions, objective/report rendering, replay-link provenance, report filters/CSV, Notion PREP_ONLY boundary, conflict/empty/denied/error states, no broker/credential mutation payloads, and no unexpected console errors. These are fixture checks, not whole-product/backend acceptance.

## Validation

- `node --test tests/*.test.mjs` → **54 passed, 0 failed**.
- `npm run build` → **PASS**, 71 modules. Existing warning remains: minified JS chunk `719.92 kB`.
- `git diff --check -- foundation_v2/web/src/styles.css` → **PASS**.
- Local Prop Playwright fixture with 390 probe plus existing 1440/768/360 responsive assertions → **PASS**.
- No horizontal overflow at 390 px (`document.documentElement.scrollWidth === 390`).
- Desktop 1440 screenshot shows the original multi-column form/metadata composition; 768 screenshot retains tablet two-column layout.

## Rollback

Revert commit `52482e4` in the nested MT5 checkout, or remove the four added mobile CSS declarations. Do not revert unrelated WIP.

## Remaining gates

This closes only the Prop narrow-header density finding. It does not close native browser zoom, axe/WCAG automation, canonical screenshot golden, full-bleed chart promotion, chart pan/zoom/annotation ownership, long-session heap acceptance, real backend catalog acceptance, Job12 provider/media QA, broker/live execution, OAuth/secrets, holdout, external upload, deploy/public release or destructive deletion.

## Evidence hashes

| Artifact | SHA-256 |
|---|---|
| `evidence/prop-probe-390.json` | `9C1718890E13B453FBF50A573B2B4577FB3469680B4F0921A01A0B8C4FCE8162` |
| `evidence/prop-inspect-390.png` | `81B6C82EC1BD5F30E56F22634722462EF9C7C8F72A4FE373C5C602AECD5C6E2E` |
| `evidence/prop-ui-fixture-1440.png` | `F33334A3F7D111F6FCDDE388C07DCFD9B5B7F5EBBFE06A5B18F1D1F71F4193D1` |
| `evidence/prop-ui-fixture-768.png` | `BC441AE84E1FBE325F740F2E77A4142B5E5B27DC40BCAF0D6D2C7D06F8429C09` |
| `evidence/prop-ui-fixture-360.png` | `4130935F051C3093541C859D383D2B6A1D25D9FDE79FE79C05F4645ABF31057F9B` |
| `evidence/prop-acceptance.log` | `027C79A6F1D4B9E4244891E70ABEE25E0F41D4FB18E2F3C8BDC394BA2AECC8F5` |

