# AI environment and skill review — 24/10/2026

Scope: remove the MT5 asset picker's implementation footer and improve the
instructions/skills using repeated owner feedback. This is a scoped environment
review, not acceptance of the full product plan.

## Decisions

The two proposed X rules are useful directions, with qualifications:

- Remove secondary copy that does not help the current task. Keep control names,
  units, meaningful states and guidance needed to avoid mistakes. Repair layout
  before explaining it with more text.
- Consider UX, DX and AX together. They can conflict: correctness and the user's
  needs take priority; agent convenience does not justify extra abstraction.

The global AGENTS now contains these durable principles. Workspace/project
AGENTS route conditional work; skills hold repeatable workflows; references hold
mode-specific detail. No new provider, package, MCP server or global tool config
was installed. Existing global instructions were backed up before editing.

This follows the official [skill guidance](https://learn.chatgpt.com/docs/build-skills)
and [progressive-disclosure guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra).
Minimal copy must retain needed input labels/instructions, consistent with
[W3C's explanation of SC 3.3.2](https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html).
The UX/DX/AX priority is the owner's engineering policy, not a claimed standard.

## Inventory findings and changes

There was no evidence that adding many narrow skills would help. The useful
changes were clearer triggers, selective loading and removing stale authority:

| Owner | Change |
| --- | --- |
| Workspace `ui-platform-workflow` | Short entrypoint; product changes and design-system work load separate references. Small fixes do not reopen historical exploration. |
| Product `trading-ui-qa` | Verification owns rendered evidence; interaction reference captures repeated asset, viewport, toast, chat, model and realtime regressions. Load only affected cases. |
| Product `mt5-runtime-operations` | New local workflow for owned runtime inspection, guarded rollout and authorized reconnect. Uses fresh manifests, E-drive artifacts, rollback and existing scripts. |
| Workspace `reverse-engineering` | Narrowed to actual reverse/security investigations. Removed blanket permission inherited from the old `work/mk-open` case; package-script authorization remains explicit. |

Keep UI design and QA separate because their outputs differ. Keep product-specific
runtime operations local. Split another skill only when it has a distinct
repeatable job, inputs/output, failure modes and useful positive/negative trigger.
Do not make one skill per component or copy every chat correction into global rules.

## Behavioral review

An independent agent used the new runtime skill for a read-only health request.
It verified fresh process identities/path/hash and API listener ownership, then
received HTTP 200 from `/health/live` and `/health/ready`. It checked the terminal
process ancestry but correctly stopped short of claiming broker connectivity.
No sync, reconnect, OrderCheck or OrderSend was performed in that review.

It also reviewed these routing cases; this is a manual forward-test, not a
statistical evaluation of automatic skill selection:

| Request | Route |
| --- | --- |
| Remove picker helper text | UI product reference, then focused product QA |
| Chart flicker | Product QA; performance skill for transport/render measurements |
| Does an old quote prove market closure? | Domain/API/source investigation; no automatic reverse/performance activation |
| Suspicious DLL stealing keys | Reverse/security skill; no automatic toolkit execution |

Four changed/new skill entrypoints passed `quick_validate.py`. Local Markdown
references were checked for existing targets. New skill files and manual use
are verified; automatic discovery in a future task remains harness-dependent.

## UI evidence

`Mt5SymbolPicker.jsx` now renders only the matching symbol count in its footer.
The data path is unchanged: SDK metadata -> category/search matches -> count.
Names, search, categories, selected state, empty/reconnect state and keyboard
handlers remain in place. The fixture now waits for the metadata response rather
than using explanatory copy as a readiness signal.

- Scoped build: tracked product HEAD `c06bcc0` plus the picker overlay; unrelated
  dirty frontend files excluded. Production build passed.
- Fixture browser checks at 1440, 768 and 390 px passed category/search/unknown/
  metadata-unavailable cases, with zero page errors or broker calls.
- UI promoted to the existing local preview on port 5180. Old hashed assets and
  private branding retained; index switched atomically with rollback captured.
- Real local browser checks at 1440 and 390 px passed: footer count only,
  description search and Escape. Zero page errors; no mutating API calls.
- Screenshots inspected. No API/terminal restart, live order or migration was
  needed. This check does not establish broker execution or full UI acceptance.

## Audit and artifacts

Final forced audits: zero errors and warnings for workspace and product roots.
Global AGENTS: 12,288 bytes. Reported active chains: workspace 20,694 bytes
(44,842 reserve under 64 KiB), product 16,263 bytes (49,273 reserve). The
product-root audit reports its direct chain; global + workspace + product files
together are 24,669 bytes, also below the practical 32 KiB target.

Artifacts and rollback are under
`E:/BACKUP-TRADINGWORKSPACE/ai-env-skills-20261024/`:

- `global-AGENTS.before.md`: original global instructions.
- `build.log`, `browser/report.json`, `browser/catalog-*.png`: isolated build/fixtures.
- `runtime-browser/report.json`, `runtime-browser/symbols-*.png`: actual local UI checks.
- `ui-before-verified/`, `ui-promotion-verified.json`: rollback and promotion hashes.
- `environment-audit.log`, `skill-validation.log`: deterministic validation.

Served index changed from
`5bcef031f338d71fe46aa47c6bce38c16c2b2266a7cbb184054cc35c144037ea`
to `5be6c5bb8175e98d4de66147d4d1a594404c358373cec1d56e41a0e857ed5c2e`.
