# WMREPLAY W8 latent full-bleed CSS hardening — 2026-10-01

**Status: PASS_WITH_OPEN_GATES / SPIKE_NON_ACCEPTANCE.** The CSS branch now fits the local chart fixture at 1440×900, 768×900 and 390×844 while keeping decision cutoff and `broker locked` visible. This is a source-faithful in-memory flag spike, not live product acceptance. `SHELL_SKELETON_MODE` remains `true` in product source. Nested MT5 commit: `024808f` (`fix: preserve full-bleed replay context and responsive controls`).

## Prompt and decision

The parent worker assigned a narrow CSS lane after the earlier full-bleed spike found hidden cutoff/broker context, an unused utility-rail gutter, clipped/overlapping mobile header controls and a 768px replay transport below the viewport. Ownership was limited to `foundation_v2/web/src/ReplayWorkspace.css`, `foundation_v2/web/src/fx-shell-story.css`, optional focused test, and this checkpoint. No JSX, backend, dependency or production shell flag was changed.

The latent full-bleed branch now shows the existing replay context's practice symbol/timeframe, workspace and broker lock, decision cutoff and status. Dataset and row-count fields are omitted from this compact strip. The data, cursor and status still come from the existing replay response; CSS does not create authority. Conflict and historical banners are no longer hidden by this branch, but those two states were not exercised in this fixture. At <=900px the hidden utility rail no longer reserves a grid column. The header wraps into rows, the transport can grow to fit its controls, and the mobile cutoff cursor remains visible. All additions are scoped to `.is-chart-workspace`, so the current compact fallback and normal routes keep their prior layout.

The responsive header costs 71px at 768 and 103px at 390 in this fixture. Keeping explicit context costs another 62px/89px respectively; chart height still measures 692px/558px. The 390px screenshot shows three header rows, the cutoff and broker lock above the chart, a full-width 352px chart after the 38px tool rail, and transport controls inside the viewport. This is a deliberate trade-off for access and truthful state.

## Files and validation

- Nested MT5 source: `foundation_v2/web/src/ReplayWorkspace.css`, `foundation_v2/web/src/fx-shell-story.css` in commit `024808f`.
- Isolated runner: `run_fullbleed_spike.mjs` in this folder. From this folder: `node .\run_fullbleed_spike.mjs`. It starts local Vite on `127.0.0.1:4205`, intercepts all `/api` calls with a GET-only local 5,000-row EURUSD/M1 fixture, changes the one `SHELL_SKELETON_MODE = true` browser response assignment to false **in memory**, then closes the browser/server in `finally`. It does not edit product JSX or call an external service.
- `runtime.json`: 4,000 rows visible at cutoff index 3,999; future marker absent; cutoff and broker lock visible at all three widths; zero document horizontal overflow, clipped/overlapping/outside controls, inaccessible topbar center hits, page/console errors, non-GET calls and unmocked API calls. Keyboard first Tab reached the named Sessions back link; `?`/Escape opened/closed help; back then browser Back restored 4,000 rows.
- 768px: chart `724×692`, utility rail `display:none`, chart right edge x=768 (no hidden-rail gutter), transport bottom y=900. 390px: chart `352×558`, utility rail `display:none`, chart right edge x=390, transport bottom y=844. Desktop chart `1336×745`.
- `node --test tests/*.test.mjs` from `foundation_v2/web`: **53 passed, 0 failed**. `npm run build`: pass, 71 modules; existing JS chunk warning at 719.68 kB. Scoped `git diff --check` and staged diff check: pass.
- Bounded 180 pointer-move probe: 5,698ms wall time, one long task with max 66ms. This does not prove pan/zoom accuracy, input latency or a long session.

Screenshots and trace were produced by the runner and visually reviewed at 1440 and 390 (also checked 768 geometry): `fullbleed-1440.png`, `fullbleed-768.png`, `fullbleed-390.png`, `fullbleed-trace.zip`.

| Artifact | SHA-256 |
|---|---|
| `run_fullbleed_spike.mjs` | `60079C1F8888DD414994A93677434DF12B3AD3263BEE9FA31C3950A8DE1BB8E6` |
| `runtime.json` | `99D49EB4677AAB676C336A8EDBDDEE67A3569E9F41EA9C4CEEA82C39F70125A1` |
| `fullbleed-1440.png` | `09998EE6DA905FE9FB3134FDB13ED9BE31434E634C0C5E0F701F9997A8624C77` |
| `fullbleed-768.png` | `3CBC5F6D9C5091F0FBF1B5D48D3B14F92A946CDEF156BDCE873E8B32B8D9A08E` |
| `fullbleed-390.png` | `CCA078936F6B4EA44C9A30469A525D494352F3D9CD568BA2A599B244BAEA5C5E` |
| `fullbleed-trace.zip` | `2C5914CA743C36696657760642E0144DA8DD5279F6F4134FACA2002EA6B610DF` |

## Open gates and resume

The header still contains source-defined buttons without action handlers (`Tiến nhanh`, `Thêm chart`, timeframe, Indicators, Order flow, Analytics, Undo, Redo, Fullscreen). CSS has not assigned behavior to them. The source flag remains true, so users still see the current compact fallback; no production full-bleed route was activated. Before a source flip, the owner worker should resolve those visible inert controls or make their unavailable state truthful, test actual chart pan/zoom/annotation anchors, keyboard traversal and 125/200% browser zoom, run stronger accessibility and stable visual baselines, and repeat the loaded/empty/error/conflict/history route matrix on the changed source. A 360px or smaller viewport and long-session performance remain unproven. The current fixture is local, intercepted and bounded, so it grants no broker, provider, holdout, release or deploy authority.

Rollback of this CSS slice is `git revert 024808f` inside `projects/mt5-tradingview-backtester`; leave the root checkpoint as evidence. Until promotion, rerun `node .\run_fullbleed_spike.mjs` from this folder to assess the latent branch without changing the product flag.

 
## Post-commit rerun addendum - 2026-10-01

The runner was rerun after commit 024808f and after the coordinator completed the compact fallback and route-matrix reruns. The status remains PASS_WITH_OPEN_GATES / SPIKE_NON_ACCEPTANCE. The fresh runtime reports chart 1336x745 at 1440, 724x692 at 768 and 352x558 at 390; cutoff and broker lock visible; overflow, clipped, overlap, outside-control, page/console-error and unexpected API mutation counts are zero; 4,000 rows are visible with no future marker; 180 pointer moves produced a 66ms maximum long task. Fresh artifact hashes are below. The earlier hash table is retained as the first-run evidence record.

| Artifact | SHA-256 |
|---|---|
| runtime.json (post-commit rerun) | 6EC4657B3DF0250FD681B9758BF7522442FEFB819E4E9825945B8F22409E8E96 |
| fullbleed-1440.png (post-commit rerun) | 09998EE6DA905FE9FB3134FDB13ED9BE31434E634C0C5E0F701F9997A8624C77 |
| fullbleed-768.png (post-commit rerun) | 3CBC5F6D9C5091F0FBF1B5D48D3B14F92A946CDEF156BDCE873E8B32B8D9A08E |
| fullbleed-390.png (post-commit rerun) | CCA078936F6B4EA44C9A30469A525D494352F3D9CD568BA2A599B244BAEA5C5E |
| fullbleed-trace.zip (post-commit rerun) | 48EFB337A4C4378C25CE87112C35C455616953CF5517A34F52A7875DF6B2FC9D |

The bounded result still does not grant production promotion: header actions are inert in source and actual pan/zoom/annotation, 360px full-bleed, native zoom, axe/WCAG, canonical screenshot golden and long-session soak remain open. Rollback remains git revert 024808f.

## Control truthfulness rerun addendum - 2026-10-01

After nested MT5 commit 37ecaa2, the same source-faithful runner was rerun. The nine latent header controls without handlers are now disabled with an explicit unavailable title; no chart/API/provider behavior was invented. Geometry remains 1336x745 / 724x692 / 352x558 at 1440/768/390, cutoff and broker lock remain visible, overflow/clipping/overlap/outside/error counts remain zero, 4,000 rows remain visible without a future marker, and the 180-move probe reports a 65ms maximum long task. Status remains PASS_WITH_OPEN_GATES / SPIKE_NON_ACCEPTANCE because the production flag is still true and chart action semantics, pan/zoom/annotation, native zoom, axe/WCAG, canonical golden, 360px and long-session soak remain open.

Fresh artifact hashes for this rerun:

| Artifact | SHA-256 |
|---|---|
| runtime.json | 9830F6117906A7E44FF0323BD1BE662E691E897CE2A498E326DD665398EDBE2A |
| fullbleed-1440.png | B0868354DB6963875AD11F9748B5055128A6A51FA1B8B82A0B4FD1794350529A |
| fullbleed-768.png | CAB840CFA74E481630D4DEC04F5B5D58046CD87B6F884FEE000E2F08090C6BC1 |
| fullbleed-390.png | F04048DF39AD0BA070562E517751DA34069E1EF19696CD94E4C7925F22F8EBD9 |
| fullbleed-trace.zip | 4469C1D87110453B780E85E7DDC50353F68F7272B819ED5950110C1C41B50D42 |
