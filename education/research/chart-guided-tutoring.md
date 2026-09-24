# Direct chart tutoring: research and decision

Reviewed 2026-09-10. Scope: improve direct AI-assisted chart teaching in this course. Not a claim of profitable technical analysis or measured learning gains.

## Update 2026-09-12 — visual-first candle teaching

The learner explicitly requests platform-like candlestick illustrations instead of numeric OHLC-heavy explanations. Expanded the existing project skill and router to cover synthetic candle lessons as well as native chart work. Use deterministic hypothetical diagrams for concepts, actual preserved chart data for platform walkthroughs, and numbers only where necessary. No new tools, global configuration, strategy change or mastery claim. Existing first-zone-touch illustration is a source/geometry reference, not newly render-verified evidence. Boundary review: retest concept uses candle illustration; pure fee arithmetic does not require one; actual chart diagnosis still requires fresh state. Course and skill validators plus environment audit are run for this change; new-session auto-discovery and learning gains remain untested.

## Decision

Keep the connected Brave browser and native chart drawings in FX Replay / TradingView. Add project skill `.agents/skills/chart-guided-tutoring`, routed by TradingWorkspace AGENTS.md. No new MCP, account, API, package, subscription, model switch or background service.

The measured gap is pedagogical and operational: the agent could draw, but a purple region did not show which peak its prose referred to; initial screenshot-coordinate placement was affected by autoscaling; a newly revealed candle changed what "new peak" could mean; an arbitrary three-bar exercise did not explain what no contact with a distant region meant.

The user's feedback after callouts and a direction arrow was positive ("đúng rồi nên z"). This is evidence of preferred presentation, not a comprehension or retention test.

## Sources actually opened

| Source | What it establishes | Application / limit |
|---|---|---|
| [OpenAI browser extension](https://learn.chatgpt.com/docs/chrome-extension) | Supported signed-in browser control including Brave; website access controls; screenshots and page text can enter chat context. | Reuse tested browser connection and site scope. Does not establish chart-trading authority, price-feed access or teaching effectiveness. |
| [TradingView Callout](https://www.tradingview.com/support/solutions/43000516978-callout-drawing-tool/) | Two-point placement, in-chart text, text/background styling, precise price/bar coordinates for the target and container. | Anchor concept to candle, put text in readable nearby space. FX Replay embed support separately verified in the actual UI. |
| [Advanced Charts Drawings](https://www.tradingview.com/charting-library-docs/latest/ui_elements/drawings/) | Native shapes, drawing management and an API within the chart library. | A developer integration option, not proof of a public API for existing personal accounts. No custom API integration needed or tested. |
| [IES / WWC practice guide](https://ies.ed.gov/ncee/wwc/PracticeGuide/1) | Recommendations with moderate evidence for combining graphics and verbal descriptions, integrating concrete and abstract representations, and alternating worked examples with exercises. Expanded recommendation 3 read on the page. | Show the actual candles while naming the concept, then fade guidance. Broad education evidence, not a trial of AI chart tutoring, this learner or this model. |

An additional search for Vanderbilt's educational-video guidance returned PDF results; the document was not opened and is not used as evidence here. No numeric learning-speed or token-saving claim is made.

## Capability comparison

- **Connected chart UI: selected.** Native drawings persist with the chart, and the learner can continue in the same session. Canvas placement is fragile under zoom/autoscale; use explicit coordinates and screenshot verification.
- **Chart-library API: deferred.** Could offer deterministic price/time placement in a chart application we own, but there is no verified supported bridge to this signed-in session. Building another chart would introduce data, replay and maintenance obligations without fixing the immediate teaching gap.
- **Screenshot-only / synthetic visual: fallback.** Useful if direct access is unavailable, but does not edit the learner's platform. Do not regenerate price history or imply the artifact is a live drawing.
- **Trading/data MCP: no new installation.** Reading quotes, order access and chart annotation are separate capabilities. No demonstrated need for extra permissions or a broker connector in this request.

## Teaching and UI acceptance

Positive fixture: MK-01, OANDA EURUSD H1, original zone1.1615–1.1622, peak A near1.1620, B near1.15994; latest known bar at19:59:59 UTC has H1.16339 and C1.16091. Four callouts and one Arrow were rendered, reviewed and saved in the preceding live task, with original Rectangle preserved and no tutor replay/order actions. The last candle must be distinguished from B, not retroactively relabeled as the same peak.

Validation layers are separate:

1. Skill structure, project routing, references and environment budget: run validators after edits.
2. Same-agent live read-only recheck of the saved chart under the new workflow: verify labels/anchors, changed-state handling and save indicator. Log outcome below after executing; do not claim a new drawing pass if only inspecting.
3. Semantic boundary cases: arithmetic-only request should not draw; a moved/replayed chart requires fresh mapping; absent account permission must not become an install/order action; ambiguous "is the region wrong?" requires checking bounds and meaning before mutation.
4. Not tested: independent model forward-test, skill auto-discovery in a new task, measurable learning gains, delayed retention, strategy edge.

The positive fixture and boundary review are not a quantitative benchmark. Preserve pending learning status; changing teaching tools does not complete the course.

### Validation results, 2026-09-10

- `quick_validate.py`: skill valid. Both skill reference links resolve; fixed an initial excess parent-directory traversal before completion.
- `education/check_setup.py`: PASS; 49 recorded learner attempts unchanged. No student response or mastery generated by testing.
- Same-agent live read-only acceptance: fresh screenshot shows four readable callouts (A, B, rebound, new candle), Arrow and unchanged purple zone; A and B leaders point to the intended historical peak areas. Replay clock19:59:59 UTC, latest price1.16091, balance200, realized/unrealized0 and empty Open Positions match the saved context. AX reports All changes saved. No drawings/orders/replay were mutated in this recheck; exact Coordinates were verified during the preceding creation, not reopened here.
- Semantic review: arithmetic-only prompt routes out; changed chart/crosshair case requires fresh evidence and stable references; uncertain region diagnosis does not authorize moving it; chart annotation permission never becomes a trade/API permission. These are same-agent reviews, not independently executed model tests.
- Project router is explicit and read in the current task. Automatic skill catalog discovery in a new task is not tested; the router provides a file-read fallback.
