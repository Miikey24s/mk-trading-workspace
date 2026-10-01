# WMREPLAY Sessions/Prop mobile density — checkpoint 2026-10-01

- **Slice:** W8 follow-up — Sessions/Prop 390 px density and action truthfulness
- **Owner:** `/root/sessions_mobile_density`
- **Date:** 2026-10-01 (Asia/Ho_Chi_Minh)
- **Status:** `SCOPED_PASS / PROP_REVIEW_OPEN`

## Request and scope

User request routed to this worker: “Tiếp tục lane an toàn UI. Đọc AGENTS.md, CURRENT-CONTEXT, WMREPLAY master plan và audit checkpoint. Ownership duy nhất: `projects/mt5-tradingview-backtester/foundation_v2/web/src/session-picker.css` và nếu thật sự cần thì `SessionPicker.jsx`; không sửa file khác/WIP. Dùng fixture/local browser hoặc Playwright để đo Sessions/Prop ở 390px, xác định lỗi density/wrapping. Nếu có fix nhỏ, triển khai, chạy focused tests/build/screenshot và ghi checkpoint `planning/checkpoints/workspace-next-stage/WMREPLAY-W8-SESSIONS-MOBILE-20261001/CHECKPOINT.md`; nếu chưa đủ bằng chứng thì audit-only checkpoint, không sửa. Không broker/provider/OAuth/secret/deploy.”

Allowed product files were limited to:

- `projects/mt5-tradingview-backtester/foundation_v2/web/src/session-picker.css`
- `projects/mt5-tradingview-backtester/foundation_v2/web/src/SessionPicker.jsx` only when the measured UI had an action/state truthfulness issue.

Forbidden in this slice: `styles.css`, `PropWorkspace.jsx`, backend/API, provider, broker, OAuth, secrets, deploy and unrelated WIP. The Prop page was audited but intentionally not changed because its responsive rules live in `styles.css`, outside this ownership packet.

## Authority and reuse

Read before work: root `AGENTS.md`, `planning/CURRENT-CONTEXT.md`, `planning/mt5-tradingview-backtester/WMREPLAY-UI-MASTER-PLAN.md`, `planning/checkpoints/workspace-next-stage/WMREPLAY-PLAN-ALIGNMENT-20261001/CHECKPOINT.md`, and the current SessionPicker/Prop source. Existing SessionPicker markup, semantic classes, shell layout and local fixture routes were reused; no dependency or framework was added.

## Finding and decision

At 390×844 with a local replay-session fixture, the Sessions surface had no horizontal overflow (`document.documentElement.scrollWidth === 390`), long session names wrapped inside their cards, and action rows remained inside the 316 px content column. The two actions **Session Settings** and **Delete session** were visually enabled when a session was selected even though they had no handlers or state owner. That violated the plan’s truthful-action contract and made the danger action look available.

The focused fix disables both unowned actions in all states, gives them a Vietnamese title explaining why, and repairs the disabled selector typo so `.fxr-text-button` receives the same reduced-opacity/not-allowed treatment as other disabled buttons. This is a local truthfulness fix; it does not add settings or deletion semantics.

## Changed files

- `projects/mt5-tradingview-backtester/foundation_v2/web/src/SessionPicker.jsx`
  - `Session Settings` and `Delete session` are always disabled until an explicit state owner/handler exists.
  - Added `title="Chưa khả dụng trong Sessions shell"` to both controls.
- `projects/mt5-tradingview-backtester/foundation_v2/web/src/session-picker.css`
  - Corrected `.fx-text-button:disabled` to `.fxr-text-button:disabled`.

Commit/rollback: `b4c5793 fix(mt5-ui): disable unowned session actions`. Revert that commit to restore the prior action presentation. No other product or WIP files were staged.

## Validation evidence

Commands:

- `node --test tests/sessionPicker.test.mjs tests/fullbleed-controls.test.mjs tests/*.test.mjs` → **54 passed, 0 failed**.
- `npm run build` → **PASS**, 71 modules. Existing warning remains: minified JS chunk ~719.92 kB.
- `git diff --check -- foundation_v2/web/src/SessionPicker.jsx foundation_v2/web/src/session-picker.css` → **PASS**.

Playwright local fixture (`http://127.0.0.1:5173/?view=replay&select=1&workspace=tenant-a&session=prop-practice-session-with-a-long-name`, dark theme, 390×844, intercepted `/api/v2/replay/sessions` only):

- page width 390, document width 390, no horizontal overflow;
- long session heading wraps to three lines inside the summary card (`278 px` content width), with no clipping;
- both unowned actions report `disabled: true`, title `Chưa khả dụng trong Sessions shell`, computed opacity `0.45`;
- screenshot: [sessions-mobile-final-390.png](D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web/artifacts/sessions-mobile-final-390.png).

Prop fixture audit (`http://127.0.0.1:5173/?view=testing&workspace=tenant-prop-ui`, dark theme, 390×844, local intercepted `/api/v2/prop/**` responses):

- page width 390, document width 390, no horizontal overflow;
- sidebar collapses above main content; form fields become one column at ≤520 px; resume metrics/facts/objectives/report stack without clipped text;
- screenshot: [prop-mobile-390.png](D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester/foundation_v2/web/artifacts/prop-mobile-390.png).

No provider, broker, OAuth, secret, external upload or mutation request was used. Browser fixture is local-only and does not promote data to product acceptance.

## Open issues and next step

- The Prop 390 px page remains visually dense (small metadata typography and a long vertical form), but its CSS ownership is `styles.css`, outside this packet. Keep this as an open W7/W8 review finding for the owning lane; do not silently widen this slice.
- Sessions has no canonical screenshot golden, native zoom/axe run, or real backend catalog acceptance in this packet; those remain W7/W8 gates from the master plan.
- Next dependency: parent integrator should include `b4c5793`, retain the Prop density finding in the authoritative resume/plan, and rerun the shared route matrix after integration. Do not promote full-bleed or add settings/delete behavior without a state owner.

