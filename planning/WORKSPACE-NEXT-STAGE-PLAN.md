# TradingWorkspace — PLAN bàn giao giai đoạn tiếp theo

**v1.3 · 26/09/2026 · M2 UI SKELETON COMPLETE / FIGMA MAKE QA COMPLETE.**
**WORK: ACTIVE/PARTIAL · REVIEW: ACCEPTED-SCOPED (lan4 UI skeleton + selected M3/M4 product integration/shared release); M5 baseline and M6/M7 pending · DOC: EXECUTABLE SUMMARY.**

Đây là **một đường dẫn giao việc** cho coordinator. Trạng thái execution theo [RESUME](checkpoints/workspace-next-stage/RESUME.md); baseline planning v1.2 bên dưới chỉ là lịch sử tại thời điểm lập plan. Owner đã chốt `lan4` đúng mục tiêu khung xương và xác nhận kết thúc nhiệm vụ QA Figma Make. [Quyết định và bàn giao](checkpoints/workspace-next-stage/M2-PRODUCTIVITY-VI-MT5-lan4-review/CLOSEOUT.md) giữ scope, source/evidence và các lỗi chuyển sang tích hợp. Lượt cập nhật này không khởi động worker hoặc triển khai các mốc tiếp theo.

## 1. Mục tiêu, không mở lại toàn nền móng

Biến kết quả hiện tại thành workspace dùng lâu dài: VI Dubber dễ tìm/xem lại nội dung; UI các app có DNA chung nhưng giữ workflow riêng; Figma Make giúp cải thiện thiết kế; project và SaaS kết nối bằng contracts có quyền rõ. Mọi task bắt đầu bằng **reuse → adapt → shared khi có lợi thật → mới build**.

Không rewrite MT5 PATH-2 hoặc pipeline ASR/TTS; không gộp repository/database/model credentials; không dựng microservices/AI-company framework/registry chỉ để nối hai app. Không cố triển khai mọi ý trong roadmap 3–5 năm ở iteration này.

Kết luận chọn: **C — nền tối thiểu reuse → Make exploration nhỏ → chứng minh ở hai app → consolidate → production**. Research/lý do/nguồn/bảng model/tool ở [RESEARCH](research/WORKSPACE-NEXT-STAGE-2026-09-26.md); worker chỉ đọc đúng section theo mốc, không nạp toàn lịch sử.

## 2. Boot, scope và nguồn sự thật

Đọc theo thứ tự: AGENTS áp dụng → [CURRENT-CONTEXT](CURRENT-CONTEXT.md) → file này → [review R1–R7](WORKER-REVIEW-2026-09-26.md) → nguồn đúng project/task. Kiểm repo status, HEAD, current owner/tasks/WIP trước write; metadata dưới đây có thời điểm, không thế chỗ ledger.

| Phạm vi | Authority / đọc khi cần |
|---|---|
| MT5 yêu cầu hiện tại | [Product Plan](mt5-tradingview-backtester/PRODUCT-COMPLETION-PLAN.md), [entrypoint](mt5-tradingview-backtester/EXECUTION-ENTRYPOINT.md) → operational ledger/STATE/receipts; [PATH-2 ADR](mt5-tradingview-backtester/FOUNDATION-ADR-0001-PATH2.md) |
| VI baseline | [PLAN hiện tại](../projects/vi-dubber/PLAN.md), [README](../projects/vi-dubber/README.md), checkpoints; [UI-FIX-PLAN](../projects/vi-dubber/frontend/UI-FIX-PLAN.md) chỉ reuse requirements còn thiếu sau reconciliation |
| UI foundation | [UI skill](../.agents/skills/ui-platform-workflow/SKILL.md), [master UI plan](ui-platform/MASTER-UI-PLATFORM-PLAN.md), `D:/ANNAM/UI-Systems` docs/contracts; [trading semantics](../UI/docs/TRADING-UI-CONTRACT.md) |
| MT5 UI/Make acceptance | [UI autonomy/Figma/Prop](mt5-tradingview-backtester/UI-AUTONOMY-FIGMA-PROP-PLAN.md); reuse FM/PS/INT gates, không nghiệm thu lại phần đủ same-scope evidence |
| Integrations | [brief](WORKSPACE-INTEGRATIONS-RESEARCH-DRAFT.md), research archive E1–E7 chỉ khi tới connector |
| Tinh gọn/handoff | [CONTEXT-LIFECYCLE](CONTEXT-LIFECYCLE.md); complete khác compacted |

Baseline audit: VI `3f262a7`, P23/listening/P14 còn mở và 2 untracked files; MT5 `567c607`, STATE r379, PS-03 verifying. Review có 40 VI + 22 MT5 offline tests, không full product acceptance. Không dùng snapshot đó làm lệnh quay lại commit cũ.

**Phạm vi override khi user giao file này:** root **GPT-5.6 Sol**, tối đa **3 subagents đồng thời**, thay profile WebGPT/10-turn hoặc Gemini trong plan cũ **chỉ cho execution được điều phối bởi file này**. Không sửa provider/global config, không điều khiển task cũ tự động. Các source/domain/safety contracts cũ giữ nguyên. Nếu đọc trực tiếp một PLAN cũ ngoài orchestration này, file này không tự chiếm ownership.

Override workflow riêng trong lần giao này: Make manual steps được phép theo brief26/09 dù phụ lục cũ ưu tiên autonomous toàn vòng; dùng bounded candidate count tại §6 thay mặc định 3–5. Không override gate round-trip, human listening, shared/VI approval hoặc trading safety. Authoritative domain docs không bị sửa nhãn accepted bởi các override điều phối này.

### Figma Make thuộc PLAN nào?

| Nguồn | Phần sở hữu | Worker tiếp thế nào |
|---|---|---|
| PLAN MT5 hiện tại: U1d / Y26 + phụ lục FM-0…FM-6 | Yêu cầu vòng **code MT5 → Make → selected diff → code chạy thật → review → vòng incremental** | Vẫn là requirement của MT5; không chuyển ra ngoài để đóng PLAN MT5 sớm |
| PLAN này: M1–M4 | Điều phối Make/UI cho VI Dubber và MT5; chọn slice, capability/budget, convergence và reuse/shared release | Reuse MT5 receipt đạt đúng phạm vi; phần VI/shared thiếu thì làm thêm, không lặp lại chỉ vì đổi PLAN |

**Một lần làm, nhiều requirement tham chiếu cùng evidence:** root ghi mapping Y26/FM ↔ M2/M3 trong checkpoint/ledger owner. Same-scope receipt có thể phục vụ cả hai PLAN; vẫn kiểm từng gate, không lấy demo VI để đóng Y26 MT5 hoặc một dialog để nhận toàn UI. Khi giao file này, nó là entrypoint điều phối; PLAN domain giữ authority nghiệp vụ/acceptance.

Thứ tự là **reconcile hai PLAN → hoàn thiện/nhận baseline theo scope → mở phần phụ thuộc**, không phải bắt mọi mục hai PLAN COMPLETE rồi mới động vào Make. M1 và M2/M3 cách ly có thể giúp hoàn thành U1d/Y26 đang mở; production integration chỉ sau gate của capability được dùng. Nhánh live bị chặn không khóa toàn UI/media.

## 3. Architecture/ownership đã chọn cho iteration

| Layer | Own | Boundary |
|---|---|---|
| Global UI-Systems | Portable semantic tokens, generic behavior/contracts đã có 2 consumer thật, version/migration | Không account/risk/job semantics; không runtime import absolute D: path |
| Trading UI / MT5 | Chart/prop/risk/display units, research/report, course bridge | Broker authority/backend không đổi bởi UI/Figma/integration |
| VI Dubber | Source/job/rendition/artifacts/QA, Jobs/Review, inline preview/fullscreen; catalog theo giai đoạn | Không import MT5 store; Watch riêng hoãn tới MT5 course/Learn; translation runtime riêng vẫn tool-free/no auto failover |
| Connector module ở project sở hữu export | Permission/destination/external IDs/delivery/reconcile | Không tính lại metrics/dubbing, không source of truth song song |
| External tools | Design candidates, file copies, notes/index và review appointments | Repo/domain services quyết định đúng/sai; SaaS lỗi không khóa core |

Media manifests tiếp tục là authority pipeline. Catalog/watch/bookmarks reuse store đủ khả năng; nếu chưa có dùng project-local SQLite có migration/backup, không chuyển media bytes vào DB. Rebuild index không được mất annotations/progress. Nhiều user/máy sau này qua service + identity + replaceable store, không chia sẻ live SQLite file trên Drive/network share.

Contract ổn định trước chia code: media/rendition ID+revision/hash/language/timebase/QA; artifact ref có authenticated owner/destination; UI token/state semantic; export request identity + receipt/unknown/reconcile. Worker freeze schema/examples cùng acceptance trong **repo owner**, research không là runtime schema thứ hai.

## 4. Milestones và dependencies

| Mốc | Đầu ra | Phụ thuộc | Gate để đóng |
|---|---|---|---|
| **M0 — Reconcile và hoàn thiện baseline** | Sửa/review findings, map đủ việc còn mở từ hai PLAN, resume nguồn chuẩn, scoped acceptance | User giao execution + đọc state thật | R1 CSV được sửa/retest; R2 provider diagnosis có kết quả; VI gates xử lý theo phạm vi, không synthetic→real claim; PS-03 độc lập review. Full old plans chỉ đóng khi toàn requirements thực sự đạt |
| **M1 — Reuse và contracts tối thiểu** | Inventory delta, representative flows, artifact/token/ownership contracts, baseline screenshots/fixtures | Đọc M0; có thể làm spec/sandbox song song remediation | Không build trùng; contracts/state matrix/test oracles được root review; chưa global release |
| **M2 — Khung UI qua Figma Make — COMPLETE** | Owner chốt lan4: productivity, shared shell/tokens, VI Jobs/Review + MT5 Replay/Report; Make export và local QA đã nhận | M1; user đã chạy Make và gửi lan1–lan4 | **ACCEPTED-SCOPED: UI skeleton / FIGMA QA COMPLETE**. Build/typecheck đạt; 29/32 browser checks, 3 lỗi được owner cho sửa lúc tích hợp. [Closeout](checkpoints/workspace-next-stage/M2-PRODUCTIVITY-VI-MT5-lan4-review/CLOSEOUT.md); không cần lan5 hoặc thêm credits |
| **M3 — Tích hợp UI đã chọn — COMPLETE** | Reuse lan4 và existing components, map selected diff vào repo thật; VI inline preview/Review, MT5 Report/Prop/Replay | M1 + M2 accepted skeleton; baseline/service gate đúng capability | **ACCEPTED-SCOPED:** 3 lỗi VI bàn giao đã sửa trong runtime thật; VI build + 13 test pass, MT5 selected Prop/Report acceptance pass; visual/a11y/state review đạt. [M3/M4 closeout](checkpoints/workspace-next-stage/M3-M4-SHARED-UI-2026-09-26/CLOSEOUT.md) |
| **M4 — Shared release nhỏ — COMPLETE** | Tokens + tối thiểu controls chứng minh reuse, consumers pin; migration/rollback evidence | M3, E4 | **ACCEPTED-SCOPED:** `annam-productivity@1.0.0` có token source DTCG-compatible, deterministic snapshots/hash, pin ở VI+MT5 và một neutral button contract được cả hai app render/test đúng; domain UI vẫn local. [M3/M4 closeout](checkpoints/workspace-next-stage/M3-M4-SHARED-UI-2026-09-26/CLOSEOUT.md) |
| **M5 — VI app dùng lâu dài** | Local catalog/search, Review với inline preview/fullscreen, version/availability, export local; Watch/course player hoãn | **VI baseline M0 đạt scope cần thiết**, M1/M3/M4 | Các hành trình trong §7 trên real authorized media, service persistence/restart/restore; E3 performance + integrity; không bắt xây Watch riêng để đóng scope này |
| **M6 — Kết nối liên project và SaaS** | VI→Learn ref; Drive export đầu tiên; MT5 report projection khi ready; Notion/Calendar opt-in | M1 contracts; source capability accepted; M5 cho media | E5/permissions/revoke/dedupe/reconcile; core usable offline. Chưa connect thật thì chỉ software-verified, không integration complete |
| **M7 — Integrated acceptance và compact** | Traceability, compatibility, recovery/rollback, operation notes, evidence/known gaps; compact có nhãn | Scope M0–M6 đã đạt hoặc owner duyệt defer cụ thể | Không critical unresolved; full vs limited release tách; fresh-root resume E6, archive hash/link/preservation, update living docs |

Không cần MT5 live gate xong mới research UI hoặc dùng thư viện media độc lập. Nhưng **không khởi công feature production mới của VI trước baseline VI được nghiệm thu đúng scope**; M1/M2 prototypes cách ly được làm khi chờ human/provider gates. MT5 UI/integration slice cần acceptance services nó sử dụng, không cần mở broker để test màu/layout.

M0 là reconciliation + tiếp tục source PLAN, không chỉ sửa bảy findings rồi tuyên bố full cũ xong. P19 optional không bắt buộc; P14/human/full 6h còn required nếu owner chưa giảm scope. Worker không tự waiver để mở M5; tiếp phần độc lập hoặc báo blocker chính xác. M0 có thể chứa sub-scope đã đạt để không khóa mọi workstream.

Tránh dependency vòng: **M1 cần M0 đã reconcile đầu vào, không cần toàn M0 complete**; M2/M3 prototypes có thể hoàn thiện Y26/U1 còn thiếu trong M0. M0-VI-ready mới mở M5; M0-MT5-report-ready mới mở report connector. Release shared chưa đạt không được ngụy trang là done: product có thể tiếp với project-local baseline đã accepted, nhưng M4/shared requirement vẫn pending tới đủ proof hoặc owner quyết định scope.

## 5. M0 — sửa điểm yếu trước polish, không review lại vô hạn

1. Lấy fresh HEAD/WIP/ledger; phân biệt accepted scope, candidate, historical receipt và task interrupted. Giữ 2 file P23 untracked/evidence MT5; không stage toàn cây. Kiểm child/process ownership trước resume.
2. MT5 PS-03: xử lý CSV formula-injection R1 bằng export policy/test phù hợp; không phá numeric values. Review candidate/diff và rerun focused + scoped disposable-service tests; ledger promotion qua owner/controller hiện có, không edit STATE trực tiếp.
3. VI R2: retained payload chứa banner “Local tools unavailable”; isolate response extraction/provider-only path, không cấp Full harness/MCP theo nội dung output. Đo successful production batches trước tốn benchmark dài; no broad provider switch/global config change.
4. Đóng các remaining gates trong VI PLAN bằng evidence đúng loại. Listening cần người nghe, multi-speaker cần authorized fixture/token, real 6h cần resource/fault/media tests. UI cosmetics không thay chúng.
5. Đối chiếu PLAN/README/UI-FIX-PLAN với source mới; header model/Gradio/fallback cũ cần nhãn historical. Reconcile MT5 RESUME từ ledger hiện tại. Dọn diff phần liên quan, không mass-format.
6. Tạo baseline acceptance record riêng mỗi repo: scope, tested code/data/config/runtime, source hashes (raw vs normalized rõ), tests+not-run, reviewers, exceptions/remaining and rollback. Chỉ accepted scope trở thành prerequisite satisfied.

## 6. M1–M4 — UI/Figma cụ thể, không tự tạo framework

**Representative flows đã chốt cho khung:** VI Jobs → Review song ngữ với inline preview/fullscreen → sửa một đoạn/preview stale; MT5 report/filter/CSV → replay đúng cursor. Các nav khác giữ placeholder đúng phạm vi. Watch riêng sẽ đi cùng MT5 course/Learn ở giai đoạn sau.

**Minimal foundation:** reuse typography/font, token roles, spacing/focus/contrast/error/unknown semantics; raw value→semantic alias mapping. Native controls trước; Radix cho complex interaction nếu existing thiếu, không cài nhiều UI suites. Owner cho phép hiện đại hóa frontend thử nghiệm: hướng đã chọn là React 19 + TypeScript + Tailwind 4/toolchain Vite của lan4. Khi tích hợp, nâng theo diff riêng và kiểm API/domain/compatibility; không buộc giữ React 18/Tailwind 3 vì baseline cũ, cũng không ép mọi consumer cùng CSS framework. E4 phải test compatibility.

**M2 Figma route hiện hành trên Windows:** prototype lane, guidelines+approved code/context slice → Make → official resource fetch hoặc export/Make-created GitHub sandbox → root-reviewed diff vào app. Native prototype GitHub là one-way/default-branch, không push repo sản phẩm hiện có/two-way sync. Local-codebase branch/PR flow là Mac closed beta theo docs 26/09; chỉ revisit theo capability mới. Thiếu tool thì đưa user một packet/link/thao tác cần thiết, không bắt quản agent.

**Model/mode:** ưu tiên thử **Opus 4.8 + Build** cho first complex screen đã có brief; đây là candidate chứ không winner đã đo. Default+Build làm đối chứng khi cần và đủ budget. Task chưa rõ dùng **Default + Plan → Build** theo account capability; không giả Opus4.8 Plan vì docs còn ghi4.7. Sonnet4.6/Flash3.6/GPT5.6 cho sửa nhỏ theo task; Gemini3.1Pro chỉ thêm nếu cần creative alternative. Không đổi model mọi prompt hoặc chạy đủ sáu. Xem research §5/E2 cho budget/đo; manual direct edit tốt hơn model call cho chỉnh nhỏ rõ ràng.

**Budget:** trước run Make ghi quota còn, cap mà owner cho phép; tối đa một initial candidate + một comparison có lý do + hai vòng polish. Không biết budget thì chỉ chuẩn bị packet, hỏi permission ngắn khi cần dùng account/credits; không mua/nâng plan tự động. Hết vòng vẫn sai thì giữ last-known-good, sửa cause hoặc block, không hạ hard gate.

**M3 gate:** rubric mỗi mục mục tiêu ≥4/5: workflow, clarity/data, states, a11y, hierarchy/flat-first, consistency, domain ergonomics, integration quality. Hard gates: không mất data/context, không sai số/mode, không UI fake-success, no broker/cutoff leak, no stale-preview-as-final. Baselines cần reviewer thực, không auto-update ảnh để thành PASS.

**Authority:** MT5 aesthetics đã giao agent tự nghiệm thu; không hỏi owner màu/cỡ chữ. VI/shared-global visual lock còn theo policy hiện hành: root chuẩn bị một gói proof rõ rồi xin một lần nếu chưa được ủy quyền, không hỏi từng button. Human listening, OAuth, credits, permissions, source upload và public publish khác UI approval. Không tự suy delegation MT5 áp cho mọi project.

**M4 release:** token source ở UI-Systems, initial generated CSS snapshots/hash trong consumer repos; thử migration một slice mỗi app. Không link runtime tới path máy planner. Shared component chỉ promote khi contract/states/a11y/version và hai consumer thực sự giảm duplication; no global JobProvider/risk/store. Make kit/Code Connect/Storybook/token tooling chỉ thêm sau gap chứng minh, không điều kiện mandatory. External packages/fonts/assets cần license/pin/audit; giữ Attributions.md nếu donor yêu cầu.

### 6A. M2 đã đóng đúng scope — bàn giao sang code integration

Owner xác nhận mục tiêu là **khung xương**, đồng ý chốt lan4 và kết thúc QA Make. Quyết định này chốt productivity, shell chung, bốn màn đại diện, light/dark và domain state riêng; không bắt prototype đạt mọi tiêu chí vận hành sản phẩm. Source export `E:\WIN-MEDIA\Downloads\Figma_Make_M2_VI_Dubber\lan4`, manifest/hash và evidence tại [closeout](checkpoints/workspace-next-stage/M2-PRODUCTIVITY-VI-MT5-lan4-review/CLOSEOUT.md). Không tự mở lại Make, yêu cầu lan5 hoặc tiếp tục prompt sửa cũ.

| Việc chuyển sang M3 / owner tích hợp VI frontend | Điều kiện hoàn tất khi dùng luồng thật |
|---|---|
| M3-VI-01: download chunk kiểm prefix URL | Kiểm artifact availability độc lập codec, giữ revision/stale/QA gates; pending/missing/error không giả file tải được |
| M3-VI-02: native fullscreen → Import mất focus | Đợi exitFullscreen hoàn tất rồi mở/focus dialog; Tab/Shift+Tab/Escape/restore đúng |
| M3-VI-03: đổi segment trong lúc phát không seek | Tách seek chủ động với media timeupdate; đúng source/chunk-local time, giữ play/pause |

[Review runtime và repro](checkpoints/workspace-next-stage/M2-PRODUCTIVITY-VI-MT5-lan4-review/REVIEW.md) giữ nguyên 29 PASS / 3 FAIL. Ba lỗi được **defer khỏi scope skeleton**, chưa được sửa hay chuyển test thành PASS; giải quyết trong code trước acceptance luồng media liên quan. M2 complete không tự đóng M3/M4, product integration, MT5 U1d/Y26/FM hoặc human-listening/broker gates. E1 phần product integration chuyển tiếp sang M3, không bỏ requirement. Model/credit benchmark không cần để chốt skeleton và chưa được claim đã đo.

## 7. M5 — VI Dubber scope sản phẩm

| Hành trình | Bắt buộc | Acceptance |
|---|---|---|
| **A: Tạo và xem** | Chọn local/video nguồn có quyền → reuse job pipeline → preview/final/QA state → inline preview/fullscreen trong Review | Tiến độ thật; không final trước hoàn tất; source/translated track đúng version/time; missing/failed có action rõ |
| **B: Tìm và mở lại** | Catalog local/search/filter → mở đúng job/rendition trong Review; giữ ngữ cảnh làm việc | Restart/persistence đúng scope; không auto-play ngoài ý; metadata missing không fake duration; long transcript bounded rendering |
| **C: Review và lưu** | Existing reviewer → edit segment → invalidation → rerender phạm vi → chọn rendition/export | Bản cũ giữ lineage; preview cũ không hợp lệ không phát; export MP4/SRT/transcript cùng revision, checksum verify |

Catalog gắn media với job/artifact, không list mỗi retry như video độc lập. Source/dubbed/audio/subtitle/transcript tồn tại khi có use case, không bắt lưu nhiều bản vô ích. VI là target đầu; language tags/rendition schema chuẩn bị extension nhưng UI chỉ show ngôn ngữ/backend đã verify. Watch riêng, viewing library/course player và watch-progress/bookmark UX hoãn tới MT5 Learn; contracts/metadata có thể reuse khi tới scope đó. Đừng hứa lip-sync/cloud playback/all codec.

Dữ liệu catalog: manifest projection/index rebuildable; user bookmarks/watch history riêng có transaction/backup. Nếu SQLite: migration version + consistent backup API + restore test, không copy live DB vào Drive; chỉ metadata/search, không blobs. Xóa catalog item không xóa source/media mặc định. Relink file phải khớp fingerprint hoặc yêu cầu mapping mới; không đoán từ filename.

E3 benchmark deterministic metadata fixtures trước, rồi licensed real sample; bắt đầu 1.000 items/100.000 segments. Proposed budgets: p95 local list/search ≤500ms, initial metadata view ≤2s; freeze máy/versions/cold-warm/sample trước đo. Giới hạn RAM/DOM/thumbnail concurrency; seek cần timebase đúng và tolerance công bố. Đây là test targets, không claims đã đạt. Không chạy video6h trong mọi unit/CI run; baseline M0 giữ heavy gate riêng.

## 8. M6 — integration vừa đủ

| Lát | Product source / external owner | Gate trước execution |
|---|---|---|
| I1 VI→Learn | Dubber artifact authority; Learn lưu authorized reference, course progress owner không đổi | Signed/trusted identity & allowlisted resource; timestamp/QA/version/source visible, no answer-key/auto-complete |
| I2 Drive export | App giữ source; Drive giữ copy có remote ID/revision/checksum | User chọn account/destination/data class, `drive.file`+Picker khi phù hợp; no full-drive crawl |
| I3 MT5 report→Notion/index | MT5 metrics/version giữ nguyên; Notion phần generated có owner riêng user notes | Source report accepted+sanitized; không ghi đè user notes, no broker/account/holdout leak |
| I4 Calendar review | Calendar giữ appointment; app liên kết đúng run/media | User scope calendar/notification; không biến event text thành lệnh, không dùng thay economic news |

**Iteration mặc định:** I1 reference/contract + I2; UI Watch/course player của I1 theo giai đoạn Learn sau, không phát sinh màn mới trong khung đã chốt. I3/I4 là subsequent opt-in slices cùng plan, không tự tạo tài khoản/chi phí để hoàn tất checklist. Nếu không cấp quyền, core có thể accepted trong local scope; cloud mục đó BLOCKED, không full integration complete. `COMPLETE-LOCAL` nếu dùng phải nêu scope và owner chấp thuận deferred requirements, không lén giảm mục tiêu.

Reuse API SDK + existing durable jobs, không LLM vòng lặp copy file. Backend lưu intent/receipt/external-ID map; duplicate/retry/timeout/crash/revoke/cancel tested. Unknown outcome tra cứu trước resend; unsupported lookup chuyển manual reconciliation, không hứa exactly-once. Webhook là hint, không unique authority. Machines offline giữ pending; no always-on promise.

Connector share chỉ khi consumer2 dùng được cùng contract, secrets vẫn scoped per connection/project/user. Không chuyển broker/FFmpeg/backtest vào n8n nodes. n8n/Temporal/cloud relay chỉ thành task khi scale/operations evidence và approval riêng; không public tunnel terminal.

## 9. Một Sol coordinator, không cần user tự chia chat

**Model/effort đề xuất:** root GPT-5.6 Sol **high** cho coordination/contract/review; task UI/copy/adapter rõ có thể Sol **medium**; safety/data/unknown-write review **high**, tăng **xhigh** cho vấn đề khó có căn cứ. Không ghi model label thành runtime proof; model/effort unavailable thì báo gap, không tự fallback provider/cost. User/model picker chọn đúng root khi bắt đầu; plan không sửa cấu hình máy.

Tối đa **3 children đang chạy**, tính mọi child ở mọi nhánh; không nested spawn mặc định, root+children tối đa4. Concurrency browser/provider/GPU/DB là budget khác, không lấy coding-agent cap làm WebGPT dịch c2 cap. Trạng thái từng lane đọc RESUME/ledger mới nhất; M2 skeleton đã COMPLETE, lượt cập nhật này không tự dispatch worker.

| Wave | Root | Workstreams có thể tách |
|---|---|---|
| A | Reconcile scopes/permissions/contracts, không sửa shared files khi chưa freeze | VI remediation; MT5 remediation; read-only review tối đa child3 |
| B | Freeze minimal UI contract/fixture/source packet | Figma experiment (một writer); catalog contract/test fixture; read-only licensing/compatibility |
| C | Review/converge shared token diff, integration owner duy nhất | VI UI/library theo paths riêng; MT5 token consumer riêng; reviewer độc lập |
| D | Cross-project integration/acceptance và archive | Connector software tests; product QA riêng fixture namespaces; reviewer |

Không bắt dùng đủ3. Contract chưa freeze, cùng file, sharedGPU/process/account hoặc integration chưa rõ thì tuần tự. Shared contracts/tokens/lockfiles/PLAN chỉ root hoặc đúng owner ghi; mỗi task packet gồm baseline/version, allowed files, forbidden files/actions, reuse map, oracle, tests, exit/rollback và receipt locator.

Git: mỗi repo branch/worktree riêng nếu lane cần isolation; shared workspace không `git init`. Không hai app-agent ghi cùng UI-Systems files. Worker không stage/reset WIP người khác. Cross-repo changes contract add/backward-compatible trước, consumers sau; old/new compatibility test và rollback. Không cần distributed transaction qua Git repos, nhưng release receipt phải ghi cả hai commits+shared version.

## 10. Durable state, failure và review

- **Không hệ điều phối mới.** MT5 dùng ledger/controller hiện có; VI dùng owning PLAN/checkpoints. Outer PLAN chỉ stage summary/link dependencies, không chép mọi task status thành ledger thứ hai.
- Khi execution bắt đầu, root tạo `planning/checkpoints/workspace-next-stage/RESUME.md` **nếu chưa có**, format ngắn từ CONTEXT-LIFECYCLE: root/task identity, per-repo HEAD/WIP, active lane owners, last verified gate, evidence links, pending/external outcomes, next actions và permission blockers. File chưa cần tạo khi chưa có run.
- Domain docs của giai đoạn mới theo repo owner: bổ sung architecture/runbook hiện có hoặc `docs/` khi thật sự thiếu; mục này không cho phép tiếp tục append raw logs vào PLAN dài. Giữ map requirement→milestone→test/evidence trong checkpoint, IDs ổn định qua compaction.
- Mỗi lane có receipt tại repo owner: input contract/source hashes, output changes, tests pass/fail/not-run, artifact paths, exclusions, review findings và rollback. Lưu trước integration/compaction/đổi phase, không phụ thuộc cuối chat mới ghi.
- Child lỗi: root đọc status/diff/receipt, giữ WIP, không coi silence=success. Retry chỉ sau phân loại; hai attempt không tiến bộ cùng nguyên nhân thì dừng lane/sửa nguyên nhân, không tăng agents vô hạn. Không rerun unknown OAuth/export/publish side effect.
- Root bị ngắt/fresh chat: đọc outer PLAN → RESUME → domain ledger/checkpoint, xác minh HEAD/hash/owner/process rồi resume. Không nhận task cũ chỉ vì folder tồn tại; late child result sai baseline giữ quarantine/review, không merge mù.
- Review tác giả tự test trước; reviewer độc lập read-only cho shared contracts/persistence/export/trading-sensitive boundaries. Author sửa finding rồi reviewer confirm; root không rubber-stamp báo cáo child. UI reviewer xem screenshots **và** interaction/source evidence.
- Không dồn mọi review tới cuối: focused test mỗi slice; cross-module suite sau wave; integrated acceptance tại M7. Tránh full GPU/provider suite cho đổi CSS nhưng không bỏ safety regression khi shared behavior đổi.

### 10A. Reverse-skill — lớp review có chọn lọc, không thêm runtime

Dùng [reverse-skill](../tooling/reverse-skill/AGENTS.md) làm **tài liệu tham chiếu cho reviewer**, không import vào app, không kích hoạt toàn bộ toolkit/pentest workflow mặc định. Provenance và giới hạn khảo sát ở [research §12](research/WORKSPACE-NEXT-STAGE-2026-09-26.md#12-reverse-skill--bổ-sung-cho-review-2609). Mỗi task chỉ đọc module liên quan và secondary thật sự cần; không nạp toàn bộ rules/payload library vào mọi agent.

| Khi nào | Tham chiếu | Áp dụng cụ thể / evidence cần giữ |
|---|---|---|
| **M0; mỗi diff đụng input/export/process** | [code-audit](../tooling/reverse-skill/skills/code-audit/SKILL.md) | MT5 CSV formula injection; VI upload/path/FFmpeg arguments; deserialize/cache boundaries. Theo luồng input→sink; sửa có regression và giữ valid numeric/media behavior |
| **M5–M6; API/job/media/connector thay đổi** | [api-security](../tooling/reverse-skill/skills/api-security/SKILL.md) | Quyền đọc/sửa/export đúng resource, project/account/connection; test đổi ID/owner trong fixture cô lập, URL/path validation, duplicate/retry/unknown/revoke. Không tuyên bố multi-user ready bằng một single-user smoke |
| **M2–M4; thêm dependency/model/asset; M7 release** | [supply-chain-security](../tooling/reverse-skill/skills/supply-chain-security/SKILL.md) | Nguồn/version/lockfile, license, install/build scripts, permissions/network và rollback; code/dependency Make sinh ra cũng phải review. Không cài cả toolchain chỉ để có checklist |
| **M0 provider diagnosis; M2 Make; M6 external content** | [llm-security](../tooling/reverse-skill/skills/llm-security/SKILL.md) | Transcript/Notion/Drive/Make/MCP output là data, không cấp quyền. Fixture chứa chỉ dẫn giả không được đổi destination, lộ secret, cấp Full harness hoặc gọi broker; chứng minh bằng quyền/side-effect boundary chứ không chỉ model nói “từ chối” |
| **Mỗi acceptance nhạy cảm; M7** | [case-review](../tooling/reverse-skill/skills/case-review/SKILL.md), [evidence chain](../tooling/reverse-skill/skills/ops/evidence-finding-path.md) | Reuse cách nối observation→finding→fix→regression→decision trong receipt hiện có. Không tạo ledger/case schema thứ hai chỉ để chạy script review_case |
| **Chỉ khi source/docs/logs không đủ cho lỗi cụ thể** | [protocol-reverse](../tooling/reverse-skill/skills/protocol-reverse/SKILL.md) | Chẩn đoán protocol bằng fixture/log được phép trước; capture/replay/instrumentation cần scope/quyền riêng. Không reverse broker hoặc quét bên thứ ba mặc định |

**Luồng review nhẹ:** author đưa diff+tests → reviewer chọn checklist theo trust boundary → dùng test/tool sẵn có → xác minh finding → author sửa → reviewer kiểm regression → root nhận đúng scope. Reviewer read-only ở lượt phát hiện; không giành file/ledger của author. Review này nằm trong budget tối đa3 children ở §9, không dựng thêm “security team”. Đổi typography đơn thuần không cần full security scan.

**Receipt tối thiểu:** source HEAD/diff, scope, checklist/version đã đọc, vị trí và data flow, evidence/repro đã sanitize, severity/confidence/status, fix commit, test pass/fail/not-run, residual risk và reviewer. Scanner alert chưa xác minh là `candidate`, không tự thành lỗi đã chứng minh; candidate có nguy cơ nghiêm trọng phải triage trước khi nhận phần liên quan. Lỗi đã xác minh có thể sai lệnh, lộ secret, vượt quyền hoặc hỏng dữ liệu chặn acceptance phần đó. Risk thấp còn lại chỉ được ghi accepted-risk kèm lý do/owner/next action, không im lặng bỏ qua. Không bắt chạy lại toàn suite cho diff không ảnh hưởng boundary.

**Tools theo nhu cầu:** ưu tiên test runner/Playwright và audit dependency đã có. Nếu thiếu coverage có lý do, cân nhắc một tool phù hợp như Semgrep/Bandit cho source, Gitleaks cho secrets hoặc OSV-Scanner cho dependency; CodeQL khi cần data-flow sâu. Chưa verify installed/smoke thì ghi unavailable/not-run, không coi clone repo là cài xong. Kiểm nguồn/license/telemetry và pin rules/version; không upload source/secret ra dịch vụ scan ngoài scope. Thiếu scanner không khóa manual review, nhưng test bắt buộc còn thiếu vẫn là gap.

**Quyền kích hoạt tách riêng:** cập nhật/đọc PLAN và checklist không cho phép chạy script của reverse-skill. Trước bất kỳ repo script nào, đọc [AGENTS](../tooling/reverse-skill/AGENTS.md)/[RULES](../tooling/reverse-skill/RULES.md), công bố exact commands + writes/download/network/services/config effects và xin chấp thuận như package yêu cầu. `master-route` có ghi file, không là read-only probe. Scope/case cũ `work/mk-open` không cấp quyền cho VI/MT5/case mới. Sau khi có quyền cho một batch xác định thì không hỏi lại từng bước; effects/targets mới cần quyền mới. Không global install/MCP/AV exclusion, không quét account/broker/SaaS thật hoặc chạy payload corpus để “đủ plan”. Không sửa upstream package trong iteration này.

**Gate M7:** có risk-based review receipt cho các boundary đã đổi; không critical unresolved; tests chức năng/UI/trading/data vẫn phải đạt riêng. “Scanner PASS” hoặc “đã đọc skill” không phải product/security acceptance. Đây là kế hoạch review **chưa thực thi**, không chứng nhận hệ thống an toàn.

## 11. Acceptance và recovery tối thiểu

| Nhóm | Phải chứng minh |
|---|---|
| Baseline | Findings+untracked reconciliation; old accepted scopes preserved, no duplicate remediation |
| UI/function | Three VI flows + selected MT5 flows; 360/768/1440, VI glyphs, keyboard/focus, zoom, light/dark khi supported; loading/empty/error/stale/denied/unknown; no dead CTA |
| Data/media | Source vs rendition/preview/final đúng; restart/resume bookmarks; alignment; missing/moved file; catalog rebuild giữ user metadata; backup restore |
| Reuse | Contract/component inventory before new build; shared proof cả2 consumers; pin/upgrade/rollback; no duplicate risk/translation services |
| Figma | Actual source→artifact→code→runtime receipt, selected-diff integration, incremental second pass; fallback label không giả round-trip |
| Integration | Actual permitted destination or explicit software-only status; duplicate/timeout-unknown/revoke/out-of-order/cancel, no user-note overwrite |
| Security | §10A receipts cho changed boundaries; no secret/media-private upload ngoài scope; identity/path/URL checks; CSV/export safety; read-only broker/replay isolation; no prompt-to-permission. Scanner không thay functional evidence |
| Operations | Clean supported setup/restore; deterministic evidence locator; owned processes/ports only; source/version/counts correct; restart không duplicate heavy job/export |
| Fresh agent | Từ PLAN+RESUME chỉ ra next task/deps/owner/rights, tests known/not-run, no redoing accepted work; E6 rehearsal |

Reuse [QA kit](../tooling/ui-qa/README.md), app tests và [trading-ui-qa](../projects/mt5-tradingview-backtester/.agents/skills/trading-ui-qa/SKILL.md) khi phù hợp. Kit smoke không full UI proof; Playwright scripts/CLI trước, selective screenshot/trace; computer use chỉ gap thật. Không khởi động production broker/provider từ browser smoke.

## 12. Permission gates và khi nào cần user

Root tự quyết implementation nhỏ/reversible và phân agent trong scope; tự review MT5 aesthetic theo delegation. Cần user khi: OAuth/account/secret/credits mới, sensitive upload/public sharing, package publish/new shared repo authority, production deploy/migration destructive, xóa data, broker/live/holdout, baseline scope waiver, VI/shared visual lock nếu authority chưa có, human listening thật.

Figma manual request gom thành một packet cụ thể: file/link + sanitized attachment + model/mode/budget + thao tác cần + kết quả trả lại. Không bảo user “tự xem docs rồi làm”; không bắt user copy output giữa backend/frontend agents. Chưa quyền thì tiếp task độc lập, không tự cài/chuyển app để né gate.

### 12A. Điểm bàn giao Figma Make cho user — có hướng dẫn và prompt sẵn

**Vòng Make hiện tại đã hoàn tất tại lan4:** không còn chờ user hoặc yêu cầu export mới. Workflow dưới đây giữ cho màn/luồng mới được giao sau này: worker chuẩn bị → user thao tác Make → worker nhận lại và QA đúng scope. Không giả Figma Design MCP/resource read đồng nghĩa có thể tự nhập prompt/chạy Make. Chỉ thay bước thủ công bằng automation khi capability thực tế đã kiểm chứng và quyền/account/budget phù hợp; không tự bật computer use hoặc publish để né bước bàn giao.

1. **Chuẩn bị trước khi gọi user:** chọn đúng màn/slice và source version; lưu một packet dưới checkpoint đang dùng gồm prompt hoàn chỉnh, hướng dẫn, attachments được phép và kỳ vọng output. Reuse template research §10 nhưng **điền hết theo code/contracts hiện hành**, không để placeholder bắt user tự nghĩ. Không gửi toàn repo, secrets, lịch sử chat hoặc dữ liệu tài khoản thật.
2. **Gửi một hướng dẫn có thể làm ngay:** mở trang/file Make nào; chọn model/mode nào còn có trên tài khoản; đính kèm chính xác những file nào; dán **nguyên khối prompt copy–paste** worker đã soạn; thao tác tạo/chỉnh; cách lấy link hoặc export code. Prompt gồm mục tiêu màn, workflow/states, tiếng Việt, components/tokens cần reuse, stack/boundaries cần giữ, tiêu chí chất lượng và đầu ra yêu cầu. Worker tự research cách thao tác hiện hành; nếu chưa thấy UI tài khoản thì nói rõ và chỉ xin ảnh đúng phần cần xác nhận, không bịa tên nút.
3. **Tạm dừng đúng nhánh:** lưu trong RESUME/receipt trạng thái chờ user thao tác Make, packet path/source hash, thông tin cần nhận và next action. Không đóng M2/Y26 bằng code tự làm hoặc screenshot. Có thể tiếp task độc lập theo §4 nhưng không sửa cùng source slice gây stale packet; nếu bắt buộc đổi thì version lại packet trước lần gửi tiếp. Không poll/spawn agents để chờ user; hết việc độc lập thì trả lời và đợi.
4. **Nhận lại và tiếp tục:** nói rõ user cần gửi Make link có quyền truy cập hoặc file export/path theo route đã kiểm chứng; không buộc public sharing. Screenshot chỉ đủ review hình, không thay code/resource evidence. Khi user nói “xong rồi” và cung cấp kết quả, worker đọc checkpoint, kiểm version/quyền/resource, tự lấy phần có thể truy cập, review diff, tích hợp và chạy UI/function QA. Thiếu output thì chỉ hỏi đúng phần thiếu. Nếu cần vòng sửa trong budget, worker viết tiếp prompt sửa cụ thể; không bắt user tự phân tích lỗi hoặc tự quản agent.

Đây là **bàn giao thao tác công cụ**, không khôi phục gate owner duyệt gu MT5 và không chuyển trách nhiệm QA cho user. Quyền upload/credits/OAuth cho lượt mới vẫn theo §6/§12. Owner đã chấp thuận visual skeleton VI+MT5 tại §6A; shared package release/product acceptance vẫn riêng. Prompt repair lan4 chỉ còn là tài liệu tham khảo cho code integration, không là task Make đang chờ.

## 13. Kết thúc mốc mà không làm PLAN phình

Mỗi milestone chỉ cập nhật một dòng status/dependency/evidence ở bảng; logs/timing/screenshots vào checkpoints. Chắt lọc architecture/API/runbook vào docs repo owner, không đổ log vào PLAN.

Review trước compact theo [CONTEXT-LIFECYCLE](CONTEXT-LIFECYCLE.md): `ACTIVE/PARTIAL` giữ open findings/WIP/next; `ACCEPTED-SCOPED` mới archive lịch sử phần đó. Snapshot hash/original path/version/date/review link, giữ anchors và quyết định; update CURRENT-CONTEXT. Archive không COMPLETE. Final record tách local app / shared UI / Make / connector / broker acceptance và chưa-test rõ.

Plan-level review gate trước handoff: links/source authority rõ, every owner-brief phase mapped, mandatory acceptance không bị biến optional, unresolved capability có experiment/fallback và next action. Product execution gates **chưa chạy** tại thời điểm v1.2.

## 14. Lịch sử planning và trạng thái bàn giao

| Brief phases | Đã chuẩn bị | Khi execution |
|---|---|---|
| 0,12 | Compaction applied + archive/context + review-before-compact policy | Reuse, owner compact active plans sau review/resume gates |
| 1,3,8 | Reuse map, shared/domain boundaries, UI candidates, integrations decision | M1/M4/M6 verify/implement đúng scope |
| 2 | VI capability priorities/data/flows | M5, sau prerequisite baseline |
| 4–7,10 | Figma current docs/capability split, mode/model experiment, tools decisions, chọn C | M2/M3/E1–E5; account/runtime unknown không bị giấu |
| 9,11 | Sol+≤3children workflow, dependency/review/recovery và một PLAN path | Chỉ user giao execution mới bắt đầu |

Ở v1.2, planning chưa declaration shared component/product/Make accepted. **Cập nhật v1.3:** owner đã chốt M2/QA Make ở scope UI skeleton theo §6A; M3/M4 product integration/shared release được theo dõi riêng và hiện đã accepted-scoped trong RESUME/closeout. Không sửa flags UI, code app, provider settings hoặc ledger trong lượt cập nhật planning này.

**Planning validation v1.0, 26/09 (historical):** root self-review scope/precedence/dependency (M0 reconcile ≠ M0 full complete), mapped đủ brief phases0–12; 10 documents/84 local links checked, 0 missing/encoding/conflict errors; 3 original archive SHA256 unchanged. Environment audit: 0 errors/0 warnings, active17.700/65.536B, reserve47.836B. Product HEAD/WIP giữ nguyên khi kiểm cuối. Không independent-agent review hoặc fresh product test được claim trong lượt research này; review/tests trước giữ tại WORKER-REVIEW. Runtime experiments/approval/acceptance vẫn pending theo bảng mốc.

**Planning update/validation v1.1, 26/09:** làm rõ Figma cũ/mới và same-scope evidence reuse; thêm §10A reverse-skill reference review; đồng bộ routing PLAN MT5/CURRENT-CONTEXT/workspace AGENTS. Kiểm 5 file/102 local links: không link thiếu hoặc lỗi encoding/conflict; 3 archive hashes giữ nguyên; HEAD và Git status của MT5/VI/reverse-skill không đổi trước/sau. Environment audit 0 errors/0 warnings, active17.953/65.536B, reserve47.583B. Root consistency review, không independent reviewer/product test/scanner/toolkit activation. Vẫn **PLANNING READY / EXECUTION NOT STARTED**.

### Prompt giao worker sau khi user sẵn sàng

> Đọc và thực thi `D:/ANNAM/TradingWorkspace/planning/WORKSPACE-NEXT-STAGE-PLAN.md`. Làm coordinator GPT-5.6 Sol, tối đa 3 subagents đồng thời khi có ích. Bắt đầu M0 từ state/WIP/evidence hiện hành, không làm lại phần accepted. Tự đọc các PLAN/spec liên kết, chia/review/tích hợp và lưu resume ngoài chat; hoàn thiện baseline rồi triển khai các mốc phụ thuộc. Không bỏ qua gate quyền, chi phí, listening, dữ liệu, broker và shared UI; không giả Make/cloud accepted bằng mock hoặc fallback.

Prompt trên là mẫu bàn giao, **không phải lệnh chạy đang được planner thực hiện**.

> **Cleanup authority note · 2026-10-01:** This file is the single cross-project handoff. `CURRENT-CONTEXT.md` routes into it; `checkpoints/workspace-next-stage/RESUME.md` owns current execution summary; project PLANs and runtime ledgers own domain state. Do not copy job status, `STATE.json`, SQLite ledger rows or raw worker chronology here. M2/M3/M4 remain accepted-scoped; current MT5 UI work is owned by `mt5-tradingview-backtester/WMREPLAY-UI-MASTER-PLAN.md`; M5–M7 and external/provider/broker gates remain scope-specific and open where the latest RESUME says so. Future connector/SaaS/multi-user/SDK/distributed-compute/frontier proposals remain reference-only unless a later user brief opens them.
