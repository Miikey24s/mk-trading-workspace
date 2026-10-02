# Thực thi các PLAN hiện hành — 02/10/2026

**WORK: ACTIVE/PARTIAL · REVIEW: SCOPED_VALIDATED · FULL_WORKSPACE_NOT_COMPLETE.**

Owner steering sau interruption: **ưu tiên MT5, VI Dubber để sau**. Agent inventory
chỉ còn root; các worker dưới đây là historical provenance, không là active owners.
Final continuation chốt sau00:00+07 ngày03/10; parent folder giữ execution date02/10.

User giao thực thi toàn bộ PLAN trong workspace. Entry point là
[WORKSPACE-NEXT-STAGE-PLAN](../../../WORKSPACE-NEXT-STAGE-PLAN.md), sau đó PLAN
domain và nguồn trạng thái của từng project. Đây là checkpoint đối chiếu yêu cầu
với bằng chứng; không thay PLAN, ledger hoặc state producer.

## Phạm vi đã đối chiếu

| Nguồn | Phần được tiếp tục |
|---|---|
| Workspace M0–M7 | Baseline, tích hợp và operation còn thiếu; reuse M2/M3/M4 accepted-scoped |
| MT5 Product U0–U9 / Y01–Y26 | PATH-2, ledger hiện có, các phần software/UI/recovery đủ dependencies |
| WMREPLAY W0–W8 và UI/Figma/Prop appendix | Review, actual persisted UI, goldens, accessibility/performance; không khởi động lại exploration |
| TypeSafe U7 work package | Reuse offline contracts; chưa coi provider/eval/UI là full acceptance |
| VI PLAN và frontend UI-FIX queue | Harness repair, Job12 diagnosis, bounded local QA; baseline gate giữ nguyên |
| Quant / TradingAgents | README/AGENTS/contracts/checkpoints của project, offline correctness/regression |
| BR-01 STUDY-PLAN | Đối chiếu research receipt và development loop; không tự dạy hoặc cập nhật learner |
| Cleanup / UI platform / old research plans | Reuse requirements vào owner hiện có; lịch sử/future draft không tự thành worker mới |

Ledger MT5 revision389 có 37 task accepted **đúng scope đã đăng ký**, không có
takeover hoặc mutation trong lượt đối chiếu. Nó không chứng minh full U/Y. Các
receipt mới dưới đây chưa được tự nhận accepted vào ledger đó. `STATE.json` giữ
nguyên export từ producer; WAL/SHM chưa tracked không được stage hoặc xóa tùy ý.

## Yêu cầu → bằng chứng mới → phần còn mở

| Requirement | Kết quả đã kiểm | Giới hạn / bước tiếp |
|---|---|---|
| U5b manual replay ↔ engine fills | `b03304e` + `c98fef6`: protective sequence parity; `544e422` opt-in margin v2 closes declared-order admission divergence,166offline tests/23subtests và root35core/service checks | V1 bytes/behavior unchanged, no migration/DB integration. Original fixed budget chưa là broker free margin. Horizon/manual-no-signal/canonical floating-path, production data/OOS và fullU5b còn mở |
| U5a durable native resume | `55add2e`: streaming split/one-shot exact native output hash bằng nhau; public crash restore chưa được chứng minh | Engine/kernel/populated-cache serialization fail. Giữ durable mid-computation resume mở; không đổi engine/infra để né gate |
| U1/U4/W7 accessible persisted UI | `f11ddab`: Journal placeholders, Data provider/entitlement/warnings, Learn context/contrast/tablet reflow và mounted-chart Learn CTA;76web/build +144actual route/axe/reflow cases | Final UI source8205c89b…; independent16cases/416assertions +warning8cases/32observations. Automated pass không thay full manual WCAG |
| W8 independent visual review + bounded chart-state coverage | `f11ddab` approved24chart images; existing32four-route/8chart. New mixedOHLC/all5types/wheel-pan/type-switch/Volume/SMA/history renderer8/8,rootreview7byte-equal final images | Existing comparator keeps default perceptual threshold. Variant has no independent approval/goldenpromotion; touch/pinch/keyboard-only pan/manualWCAG/long-chart/fullW8 remain open |
| W8 long-duration Analytics fixture heap | `c26d425`: measured3.601.275ms/2.620iterations/61precise twice-GC samples,12,62→13,69MiB, delta1,0653MiB; DOMdelta0/errors0 | One-hour fixture PASS; source71373c3a… unchanged. Framep95=33,2ms không là verdict60Hz/whole-chart performance; historical74,3min coarse-heapFAIL vẫn giữ |
| U9/M7 current-schema restore | `c418a07`: 15 checks, real PostgreSQL18.6 dump/restore với replay execution/history/branch/drawing/tenant denial | Hai random owned DB được cleanup; không phải user backup, nonempty Prop/connector restore hoặc cloud acceptance |
| Y15/U9 clean setup | `6265dc3`: fresh Git archive 684 files/14,305,280bytes; locked uv/native runtime; 76 web +44 backend tests/build | Windows warm-cache; chưa cold machine, PostgreSQL/browser setup, macOS hoặc full U9 |
| Quant imported soak safety | `c498399`: supplied mode/capabilities/window được validate; 27 fail-before cases, 35 focused/257 full tests, Ruff | Actual 30–60day paper soak, supervisor/restart/restore/alerts chưa hoàn tất |
| TradingAgents atomic publication / PIT | HEAD `94e11a4`: 133 focused offline tests, socket denial, focused Ruff | Provider/network and broader production behavior không được mở |
| VI reload browser fixture | `3fc873f`: isolated temporary jobs/catalog/provider-denied fixture; 672 tests/1skip | Không xác nhận root cause navigation timeout lịch sử, không gọi đây là production Gradio fix |
| VI Job12 QA diagnosis | `e2940c1`: retained artifacts/hash unchanged, 122 unique failures, 9 existing listening clips/43.1s | QA false/full-track skipped; human verdict absent, M0-VI-ready/M5 giữ đóng |
| VI bounded full-track diagnostic | `fc81a26`/`af07c92`:143/143windows cover42.831,561s,1.723segments, freshfingerprintmatch,989resource samples;10retainedJSONhashes unchanged | Complete diagnostic riêng;115context-overlap boundaries/71suffix-prefix candidates prevent production stitching claim. QA122/human/P23/pipeline giữ mở |
| VI persisted preview readiness | `8253ef6`: current persisted state gates verified manifest for API list/play/download + UI restore/button/player | API28pass/1skip,browser5pass; blocked/stale/explicitready[] deny, legacyabsent usesverifiedmanifest. Không sửa retainedQA |
| VI narrow processing ticker/Header + state/error audit | `d46e9e4`/`43894e7`; `317ced9` preview403/500 intent/retry, explicit Final/QA verdict và keyboard/contrast;22browser tests/30captures/18axe scans,zero violations | Final-r6 independent sign-off absent; incomplete axe rules/fullWCAG/whole-track memory/listening giữ riêng. Owner deferred new VI work |
| BR-01 H2 research status | Superproject `65b5eb6`: count0→2/scenario từ stored events; derivative audit, 49 synthetic tests | H2 reject/P&L giữ nguyên; 2021 consumed as development; 2022/2025 chưa mở theo receipt. Learner state không đổi |
| U3/Y11 Learn bridge | `f11ddab` real-course API10checks/readyUI6cases/fullyloadedchart6journeys pass; course/progress hashes unchanged, noanswerkeys/writes | API8030 tạm đã teardown;8020 vẫnunconfigured. View20/canonical60/21rows giữ đúng; broader contextual flow/fullY11 còn mở |

Project evidence:

- [Final MT5 UI](../../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/wm-all-plan-20261002/ui-repair/CHECKPOINT.md), [chart r4 review](../../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/wm-all-plan-20261002/chart-review/r4/CHART-VISUAL-REVIEW.md), [Learn real-ready](../../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/wm-all-plan-20261002/learn-ready/CHECKPOINT.md), [restore](../../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/wm-all-plan-20261002/restore/CHECKPOINT.md), [clean setup](../../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/wm-all-plan-20261002/clean-setup/CHECKPOINT.md).
- [U5a feasibility](../../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/U5A-native-resume-feasibility-20261002/README.md), [U5b receipt](../../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/U5B-manual-execution-parity-r1.json), [sequence/gaps](../../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/U5B-manual-sequence-parity-r1.json).
- [Margin v2 completion](../../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/U5B-replay-margin-v2-CHECKPOINT.md), [VI final UI-state receipt](../../../../projects/vi-dubber/work/checkpoints/UI-state-audit-20261002/CHECKPOINT.md).
- [Mixed chart-state renderer QA](../../../../projects/mt5-tradingview-backtester/foundation_v2/evidence/wm-all-plan-20261002/chart-states/CHECKPOINT.md):8/8cases,40type/40wheel-pan/48captures, source unchanged, failed harness attempts retained.
- [VI reload](../../../../projects/vi-dubber/work/checkpoints/UI-reload-fixture-repair-20261002/CHECKPOINT.md), [Job12 listening packet](../../../../projects/vi-dubber/work/checkpoints/Job12-offline-qa-diagnosis-20261002/LISTENING.md), [bounded QA](../../../../projects/vi-dubber/work/checkpoints/Windowed-full-track-QA-20261002/CHECKPOINT.md).
- [BR-01 H2 status](../../../../education/research/br01-screen/OPTIMIZATION-02-STATUS.md).

## Data/state và trade-off

MT5 workspace/session/cursor chọn persisted read model; chart/Analytics/CSV đọc
đúng prefix, không advance khi xem lịch sử. Accessibility/formatting không sở hữu
arithmetic hay execution. Manual actions phải được khai trước trên prefix;
comparator đối chiếu fills/ledger/balance cùng immutable context.

VI đọc retained voice/config/segments, khóa identity rồi chạy tuần tự từng window
≤304s. Diagnostic output có lease và atomic checkpoints riêng; resume chỉ reuse
window cùng identity. Hash cả model và code tăng chi phí đọc disk nhưng ngăn trộn
kết quả qua code/model drift. Kết quả không có đường đổi `qa.passed` của Job12.

Quant giữ input safety fields thay vì che chúng bằng safe defaults. BR-01 sửa
summary từ stored events, tạo receipt derivative và giữ receipt gốc. Không mở
performance data hoặc biến số research âm thành bằng chứng edge.

## Process/WIP và resume

1. Heap chính xác tại `D:/ANNAM/TradingWorkspace/.artifacts/wm-all-plan-20261002/heap-long`
   đã kết thúc20:46:15+07, launcher24164 gone. Final scoped receipt `c26d425`
   PASS được giữ ở project; không start duplicate. Historical74.3min coarse-heapFAIL
   không bị rewrite hoặc giải thích hoàn toàn bởi lượt đo mới.
2. Root owns current MT5 work/workspace docs. VI audit is committed `317ced9`,
   with historical independent findings and root final review; no final-r6
   independent sign-off was published. U5b source/tests/evidence reviewed and
   committed `544e422`; no active child worker remains after interruption.
3. VI full run theo [exact packet](../../../../projects/vi-dubber/work/checkpoints/Windowed-full-track-QA-20261002/FULL-TRACK-RUN.md)
   và [launch receipt](../../../../projects/vi-dubber/work/checkpoints/Windowed-full-track-QA-20261002/FULL-TRACK-LAUNCH.md).
   Launcher10892 → worker3260; observer21444 →20492, start20:31:35+07,
   publication21:06:10+07; toàn bộ process gone, ownedlease/tempWAV removed;
   fingerprint0377b44a4f48bf1388fa90ff98302bd9eb830248cdd1ec5a1f8da60de8740b5d.
   Output riêng `projects/vi-dubber/work/artifacts/full-track-qa-job12-20261002`,143windows.
   [Completion receipt](../../../../projects/vi-dubber/work/checkpoints/Windowed-full-track-QA-20261002/COMPLETION.md)
   xác minh identity/resources/boundaries/retainedhash; không cần inference resume.
4. Journal/Data/Learn và chart promotion đã hoàn tất trong `f11ddab` ở final UI source
   `8205c89b2d79a832cb853ccad28b08ca13e1d9da67b2c185a517742752a180f1`.
  144route/32four-route/8chart và Learn10/6/6 pass. Failedsource-drift,
   hidden-link/loading race và service-down comparator được giữ. Historical
   launch receipt ở `.../ui-repair/services-resume-r1/` giữ API8020PID20928 và
   Vite5180PID20068/tool sessions28858/66234; fresh current check không thấy
   listeners5180/8020/8030. Root mở UI-only Vite5186PID18572/tool session34774 cho
   scoped chart-state fixture, không API/DB/reseed; exactprocesscommand verified
   trước teardown. Final listeners5180/5186/8020/8030 absent. Chart-state8/8 done;
   U5b margin v2 đã commit544e422. Không có current product service để giảlivejourney.
5. Sau mỗi coherent change: review diff, validation theo rủi ro, commit scoped;
   superproject pin gitlinks sau khi review project commits. Giữ unrelated untracked
   evidence `wm-ui-integration-20261001`/backend logs/resume-chart.

Final reviewed pins: MT5 `d0267d5` (margin `544e422` + chart-state evidence),
Quant `c498399`, VI `317ced9`, TradingAgents unchanged `94e11a4`. Workspace
handoff link check:7documents/57local links,0missing; scoped source/doc diff checks
pass. Margin8evidence blobs và chart186manifest entries byte-equal với Git index;
chart commit scan không thấy private-key/API-token patterns. Historical
`RESUME-READ-REVIEW.md` giữ nguyên; không coi read rehearsal là current service
liveness. Untracked WAL/SHM và unrelated evidence không được stage.

## Parent acceptance và gate cần owner

[Independent resume-read review](RESUME-READ-REVIEW.md) đã dẫn được next task,
owner, active PID và quyền, với22 entry links đúng. Đây là read rehearsal của
agent hiện có, không là fresh-WebGPT-root/provider acceptance. Findings route
được sửa bằng bổ sung base artifact và current-launch pointer; archived/history
receipts vẫn giữ nguyên. Model/cap profile cũ phải nhường current authorized
execution override, không tự đổi provider/global config.

M2 skeleton/Make QA, selected M3 integration và M4 shared release vẫn là
accepted-scoped, không chạy lan5 hoặc release lại. M0 còn VI quality/listening;
M5 production features chưa được mở trước baseline đủ scope. M6 core offline
contracts không thay actual destination/OAuth/revoke evidence. M7 mới có một phần
traceability/setup/restore, chưa integrated whole-release acceptance.

Broker/demo/live cần exact account/risk/symbol/action authorization và lifecycle
gates. Licensed real data/holdout, paid provider, OAuth/account, sensitive upload,
Miro/external publishing, deploy/destructive migration và human listening giữ
gate của PLAN. Chuẩn bị concrete packet và làm hết phần độc lập trước khi xin
quyền; không coi user giao full PLAN là waiver. 30–60day soak cần thời gian thật.
