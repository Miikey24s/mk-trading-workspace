# WMREPLAY W8 native browser zoom probe — 2026-10-01

**Owner:** /root/native_zoom_probe (read-only QA lane)  
**Scope:** Local WMREPLAY fixture and browser automation only. No product source was edited. This packet does not claim native browser zoom or WCAG conformance.

## Prompt and boundaries

The lane was asked to obtain stronger native browser zoom evidence using the existing Playwright headed/browser automation or CUA, without installing axe/dependencies or calling backend/provider/broker/OAuth/external services. Durable writes are limited to this checkpoint directory.

Source/product ownership was not changed. At the run boundary, the nested MT5 checkout had unrelated dirty WIP in foundation_v2/web/src/FxReplayShell.jsx and foundation_v2/web/src/fx-shell-story.css; those files were not edited by this lane.

## Attempt 1 — headed Playwright + installed Chrome

Command:

~~~text
Set-Location D:/ANNAM/TradingWorkspace
node planning/checkpoints/workspace-next-stage/WMREPLAY-W8-NATIVE-ZOOM-20261001/run_headed_native_zoom.mjs
~~~

The runner used the existing local playwright dependency and installed Chrome at C:/Program Files/Google/Chrome/Application/chrome.exe with headless: false. It started a temporary Vite server at http://127.0.0.1:4201, intercepted every /api/** request with local read-only fixture data, and terminated its owned Vite process. It navigated to:

/?view=overview&workspace=native-zoom-w8

The script sent these browser shortcut variants to the headed page:

1. Control+Equal
2. Control+Shift+Equal
3. Control+Equal
4. Control+0

Before, after each step, and after reset it recorded innerWidth, outerWidth, devicePixelRatio, visualViewport.scale, visual viewport dimensions, document width, body height, and overflow. All five screenshots were captured and a Playwright trace was saved.

Measured baseline and every step were identical:

- innerWidth=1440, innerHeight=900
- outerWidth=1456, outerHeight=988
- devicePixelRatio=1
- visualViewport.scale=1, visual viewport 1440x900
- scrollWidth=1440, clientWidth=1440, overflow=false
- no page errors or console errors

The five PNG SHA-256 hashes are identical (3FFB22418FAA4D1A5BFE414B05E99B0E61393227649425AD7C62ED1A6EC2B3EC), so this headed Playwright path produced no observable browser-zoom transition. The browser did launch successfully; the limitation is that Playwright page keyboard dispatch did not reach Chrome browser chrome zoom in this environment.

Files:

- headed-runtime.json — machine-readable metrics and result (headed_launch_succeeded=true, native_zoom_observed=false)
- run_headed_native_zoom.mjs — reproducible runner
- headed-overview.trace.zip — Playwright trace
- headed-before-1440.png
- headed-Control_Equal-1.png
- headed-Control_Shift_Equal-2.png
- headed-Control_Equal-3.png
- headed-Control_0-4.png
- screenshot-hashes.json

## Attempt 2 — CUA in-app browser

A local Vite server was started at http://127.0.0.1:4202 and opened in the Codex in-app browser using the CUA tab API. The CUA visibility API rejected visible=true in a subagent thread, so a background tab was used. The tab legacy CUA surface accepted and sent:

- tab.pressKey(null, 'Control++')
- tab.pressKey(null, 'Control+Shift+=')
- tab.pressKey(null, 'ctrl+plus')

After each action, tab.getAXState() reported no accessibility-tree change. A screenshot before/after showed no observable text/layout scaling. The CUA surface does not expose window.visualViewport, document metrics, or browser chrome state, so it cannot turn this attempt into stronger numeric evidence. Details are in cua-attempt.json.

## Decision

**Status: PARTIAL / native browser zoom remains OPEN.**

This packet strengthens the limitation evidence:

- Headed Playwright Chrome launched successfully, but page-level keyboard dispatch did not change native browser zoom metrics or screenshots.
- CUA sent multiple shortcut spellings, but the in-app browser reported no AX change and subagent visibility is unavailable.
- Existing headless W8 evidence also reported no native zoom change.
- CSS viewport proxies at approximately 125%/200% remain useful responsive evidence, but they are not native browser zoom.

No acceptance flag was changed and no product source was modified.

## Resume path

1. In a sanctioned visible browser session or user-controlled native Chrome window, trigger browser chrome zoom at 125% and 200% (for example through the browser menu or OS-level shortcut), capture the browser zoom indicator and page metrics/screenshot, then reset to 100% and repeat the same local fixture.
2. Keep the route and fixture ID native-zoom-w8 so evidence remains comparable.
3. Do not install axe or other dependencies solely for this packet; the separate W8 accessibility packet remains the authority for CDP tree evidence and records axe as unavailable.
4. Continue remaining W8 gates independently: canonical screenshot baseline, chart full-bleed/throughput, and long-duration heap/frame soak.

## Rollback / safety

There is no product-code rollback. Only the checkpoint artifacts may be removed if this evidence packet is retired. The runners own only temporary local Vite children. No credentials, provider cache, broker state, backend mutation, external upload, deploy, or destructive deletion occurred.

