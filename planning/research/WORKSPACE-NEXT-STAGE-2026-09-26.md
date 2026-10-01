# Research giai đoạn tiếp theo — Reuse Engine, VI Dubber, UI và Figma

**v1.1 · khảo sát 26/09/2026 · RESEARCH FOR PLANNING, không product/runtime acceptance.**
Đề bài: [OWNER-BRIEF](../archive/2026-09-26-context/OWNER-BRIEF.md). Đầu ra thực thi: [WORKSPACE-NEXT-STAGE-PLAN](../WORKSPACE-NEXT-STAGE-PLAN.md). Review đầu vào: [WORKER-REVIEW](../WORKER-REVIEW-2026-09-26.md). Không sửa source, chạy model trong Figma, cấp OAuth, publish hoặc khởi động worker trong research này.

## 1. Kết luận và mức bằng chứng

Chọn **C có reuse: nền tối thiểu hiện có → Make exploration có giới hạn → chứng minh ở hai sản phẩm → consolidate → production**. Không tạo workspace monolith, không đổi PATH-2, không dựng lại pipeline Dubber. Figma là công cụ cải thiện thiết kế, repo và contracts vẫn giữ authority.

| Loại bằng chứng | Đã có | Chưa có |
|---|---|---|
| Workspace | Đọc manifest/source/contracts/PLAN/QA kit; review trước có 40 VI + 22 MT5 tests hẹp | Không chạy UI sản phẩm hoặc toàn pipeline trong research này |
| Primary docs | Mở trực tiếp Figma Help/Developer, DTCG, Radix, shadcn, React Aria, MUI, Playwright, SQLite, OpenAI docs | Tài liệu không chứng minh entitlement/capability trên tài khoản user |
| UI user cung cấp | Ảnh Figma Community và menu Make: Default, Sonnet 4.6, Opus 4.8, Gemini 3.6 Flash, Gemini 3.1 Pro, GPT-5.6; brief xác nhận Plan/Build | Không có benchmark cùng đề giữa sáu model; không biết credit balance/seat |
| Plugin | Search Figma trả entry `installed=false`; phiên này không expose Figma tools | Chưa auth, chưa fetch Make resource, chưa test round-trip; không suy từ phiên trước |

Các kết luận về hiệu suất/UI quality dưới đây là lựa chọn thiết kế cần experiment, không số đo giả. Các docs Figma có chỗ không đồng bộ phiên bản/entitlement; preflight phải kiểm đúng surface, OS, account và mode.

## 2. Reuse audit — thứ thực sự đã tồn tại

| Tài sản / evidence locator | Đã có | Reuse / adapt / không share |
|---|---|---|
| `D:/ANNAM/UI-Systems/ui-platform.json`, README, docs, templates | `0.1.0-dev`, `systemFamilies=[]`; file scan chỉ thấy docs/manifests/templates/tooling README, chưa có code component/token release | **Reuse architecture/contract/migration policy**, không coi thư mục trống là thư viện accepted |
| `TradingWorkspace/UI/domain-ui.json`, `docs/TRADING-UI-CONTRACT.md` | Trading meanings, chưa có supported family | Giữ profit/loss/replay/live/precision tại trading layer; không kéo media UI qua đây |
| MT5 `foundation_v2/web/package.json`, `src/styles.css`, `src/PropWorkspace.jsx`, `ui/project-ui.json` | React 19/Vite 7, CSS riêng, chart/prop/replay UI thật; config exploration chưa approved propagation | Reuse screens, patterns và safety states; không copy cả màn vào global system; config/acceptance cần reconcile |
| VI `frontend/package.json`, `src/App.tsx`, `src/index.css` | React 18.3/TS/Vite 6/Tailwind 3.4, CSS variables và nhiều màu inline; player/reviewer/preview/Engineer drawer thật | Reuse toàn app shell và domain controls; adapt token mapping dần, không ép React/Tailwind upgrade |
| VI `ThemeContext.tsx`, `I18nContext.tsx`, `JobContext.tsx` | Theme/mode localStorage, VN/EN UI, job/segment/time state; theme mặc định dark, mode engineer | UI prefs/i18n pattern là candidate; state job/translation không global. Watch position hiện state trong phiên không là library resume bền vững |
| VI `VideoPlayer.tsx`, `WaveformPlayer.tsx`, `SegmentReviewer.tsx`, `LongformPreviewRail.tsx` | Media thật, time anchors, A/B, preview/final và selective editing | Phát triển Watch/Review từ đây; không xây player/waveform mới. Audit fallback duration `184.5`/mock telemetry để unknown không thành dữ liệu thật |
| VI `src/vi_dubber/api.py`, `jobs.py`, `longform_state.py`, `pipeline.py`, `types.py` | Job listing/control, version/hash/chunk manifests, ASR/TTS/QA, resume | Là authority media; thêm library projection, không thêm scheduler dịch thứ hai |
| VI `frontend/UI-FIX-PLAN.md` | Plan dài có lịch sử mock UI, các phần đã có source mới | Knowledge/reference, **không chạy lại mọi checkbox**; W0 map requirement→source→test trước compact |
| MT5 `foundation_v2/trading_workspace_v2/learn.py` | LearnCatalog read-only qua workspace allowlist, course/progress authority ngoài app | Mở rộng link artifact học theo contract; không ghi progress hoặc đưa answer keys ra ngoài |
| MT5 PATH-2 ADR, Data & Metrics, knowledge register, current ledger | Nền/semantics đã quyết định, accepted slices có bằng chứng; current full product chưa xong | Reuse nguyên authority; không dùng task UI/integration để research lại stack/risk engine |
| `tooling/ui-qa`, MT5 `run_*ui*_acceptance.mjs`, VI `tests/test_web_e2e_playwright.py` | CLI/test tooling và product checks hiện có | Reuse; fixture PASS khác app PASS. UI kit hiện route MT5, không gọi doctor với plan mới rồi mặc định hỗ trợ mọi app |
| `.agents/skills/ui-platform-workflow`, MT5 `trading-ui-qa`, environment-maintainer | Scoped instructions và audit có sẵn | Mở rộng nhỏ nếu cần; không thêm skill, browser MCP hoặc orchestration framework trùng |
| `tooling/agent-workflow` | Legacy runner/policy, browser bị cấm trong staged roles | Reuse packet/checkpoint ideas, **không** cho runner đó chạy Figma/Playwright hoặc bỏ guard |
| [Integrations brief](../WORKSPACE-INTEGRATIONS-RESEARCH-DRAFT.md) + archive | SaaS/ownership/recovery/Notion Education/E1–E7 đã research trong cùng đợt | Reuse findings, chỉ refresh entitlement khi execution; không nghiên cứu lại từ đầu |
| [Context lifecycle](../CONTEXT-LIFECYCLE.md) + archive | Review trước compact, snapshot hash, dấu trạng thái riêng, resumable handoff | Dùng convention này; không vector DB/context-generator/custom CLI |

**Shared thật:** token semantics, generic controls đã chứng minh, accessibility, QA conventions, artifact reference contract và eventually connector mechanics. **Không share bằng cách copy:** account/risk/evaluator, ASR/TTS scheduler, media playback timelines, credentials, runtime model pool, operational ledgers, app database.

## 3. UI ecosystem — so sánh và xếp hạng phù hợp workspace

Đây là ranking cho hai app hiện tại, không bảng xếp hạng thư viện toàn thị trường.

| Hạng | Hướng | Ưu điểm | Nhược điểm / quyết định |
|---|---|---|---|
| 1 | **Hybrid: assets hiện có + semantic tokens + native controls + headless primitive khi thiếu + Make** | Reuse nhiều nhất, giữ domain UX, CSS không khóa Tailwind, hai stack dùng dần | Cần contracts/QA, không copy AI code thẳng; **chọn** |
| 2 | shadcn/ui chọn lọc | Open code, dễ đọc/sửa bằng AI, nhiều mẫu | Code nhận về là mình bảo trì; hai project copy riêng sẽ drift. Không chạy CLI wholesale hoặc nâng Tailwind chỉ để cài |
| 3 | React Aria cho interaction phức tạp | Accessibility/internationalization, table/selection/forms phong phú | API/learning cost; chỉ thay lựa chọn headless khi workload thật cần, không trộn với Radix cho cùng control |
| 4 | Full MUI hoặc design system opinionated | Nhanh có bộ UI đồng bộ và tài liệu lớn | Chuyển style/interaction toàn hai app tốn; dashboard generic chưa giải quyết media/chart. Không chọn migrate wholesale |
| 5 | Figma Community kit hoặc AI-generated foundation làm nền chính | Khám phá visual nhanh | License/attribution, code parity, state/a11y chưa chắc; chỉ làm reference hoặc donor có chọn lọc |
| 6 | Tự code mọi primitive / xây platform UI lớn trước | Toàn quyền | Tốn kiểm focus/keyboard/edge case và dễ overbuild; loại |

Radix là default candidate cho dialog/menu/popover thiếu hoặc sai a11y vì unstyled, hỗ trợ adopt dần [S12]. Button/input thông thường ưu tiên native và component đã có. Không thêm cả Radix, React Aria, MUI cùng lúc “cho đủ”. shadcn có thể cung cấp implementation tham khảo [S13], không phải một package tự động cập nhật mọi component của mình.

**DNA chung**: typography hỗ trợ tiếng Việt, spacing, focus, density, control states, error language, unit/time conventions; neutral visual roles. **Domain khác**: trading dùng dense chart/evidence/risk; media ưu tiên Watch/Review, video lớn và transcript. Không ép cùng sidebar, cùng card layout hay một theme mặc định.

### Release đầu nên nhỏ

- Reuse cấu trúc UI-Systems; portable token source dạng DTCG 2025.10-compatible → CSS variables → adapters cho từng app. DTCG là Community Group specification, **không gọi là W3C Standard** [S11].
- Đầu tiên semantic color/type/spacing/focus và các controls thật sự trùng. Chưa phát hành global trước khi tối thiểu một luồng ở **mỗi app** chứng minh cùng contract; nếu chỉ một consumer thì giữ candidate/project-local.
- React 18/19 và Tailwind 3/plain CSS là compatibility matrix, không lý do rewrite. Shared behavior candidate phải test cả hai; không bundle React riêng vào shared code.
- UI-Systems hiện không có Git repo: release đầu có thể là source + manifest/hash và generated CSS snapshot được commit trong từng consumer, không runtime import từ `D:/...`. Snapshot là bản build read-only, không fork authority. Component package/tarball/versioned repo chỉ tạo khi M4 chứng minh cần; tạo repo/publish theo quyền riêng, không `git init` workspace cha.
- Consumer pin release/hash. Upgrade qua branch/tests/screenshot, rollback bằng pin cũ; không sửa global rồi silently lan sang mọi project. Đừng đồng nhất “dùng lại source” với “luôn dùng latest”.

## 4. Figma: ba luồng khác nhau, không trộn capability

| Capability | Make prototype thông thường | Make trong local codebase | Design MCP / Code Connect |
|---|---|---|---|
| Sửa repo GitHub hiện có | Push integration **không import/push repo do mình tạo** | Có open local/clone repo rồi sửa code | Code Connect đọc/map component, không có nghĩa Make sửa repo |
| Code ra GitHub | Tạo repo riêng cho mỗi Make file; push default branch | Local commits/branch, push và PR GitHub | Không suy từ permission app thành workflow đã ship |
| Code từ GitHub quay về | **Không two-way sync**; lần push Make có thể overwrite edit ngoài | Git workflow thực trong beta | Make→MCP có resource read để coding agent tái sử dụng |
| Branch/PR | Không branch management trong Push UI | Docs hỗ trợ, không auto-merge | GitHub app permission PR còn được ghi “in development” ở trang tổng quan: khác product scope/version |
| Windows | Workflow prototype hiện có thể dùng trên máy user | **Mac-only closed beta; Windows planned**, waitlist [S2–S3] | Client/account/resources support phải probe, không mặc định |
| Phù hợp hiện tại | **Chọn prototype lane + selected extraction** | Watch/revisit, không dependency release | Optional tăng độ chính xác/giảm copy tay |

Nguồn [S1–S6]. Repo sản phẩm đã push lên GitHub **không** làm nó tự import được vào Make prototype. “Code ↔ Figma” ở đây là vòng bàn giao có kiểm soát, không đồng bộ database/code hai chiều tự động.

### Windows workflow được chọn

1. Worker lấy một UI slice đã chạy + screenshot + states + fixture đã sanitize + component map/token version từ repo. Không upload source toàn repo, `.env`, broker info, video riêng, voice refs hoặc dataset.
2. Chuẩn bị Make file riêng cho experiment; guidelines và phần code cần thiết qua capability input thực sự hỗ trợ. Nếu paste/attachment không mang đủ code thì dùng screenshot/frames + contract làm design reference; ghi **reconstruction**, không gọi import repo thành công.
3. Figma Make refinement trên scope nhỏ; giữ artifact URL/version/model/mode/source commit. Manual user prompt/Build click được phép khi agent không có Make prompting capability, không cần tự xây MCP bridge.
4. Lấy code/resources qua official Make MCP khi client hỗ trợ, hoặc code export/Make-created GitHub repo. Repo export là sandbox **không** production authority. Nếu export UI chưa có trong account thì direct code extraction theo capability; không đánh dấu completed từ screenshot.
5. Coding worker diff và map kết quả vào existing components trên product branch; không copy package.json/backend/mock services wholesale. Fix behavior/token drift trong code rồi runtime/visual QA.
6. Vòng incremental: xuất context mới từ integrated commit, Make xử lý delta; không sửa export repo rồi kỳ vọng push về Make. Mỗi vòng ghi accepted/rejected và changelist.

**Fallback:** coding agent tiếp UI Autonomy với Playwright khi Make/auth/credits unavailable. App không bị khóa, nhưng requirement Make round-trip vẫn **BLOCKED/PENDING**, không lấy fallback PASS để đóng Y26. Một lần nghiệm thu thực có thể dùng cho cả U1/Y26 và plan mới nếu đúng same scope/revision; không tạo hai vòng nghiệm thu trùng.

Local-codebase beta chỉ revisit nếu Windows hỗ trợ hoặc user có Mac+access và muốn dùng. Khi đó thử isolated worktree, synthetic backend, explicit ports; review `.figma/make` scripts vì chúng có thể install/start services và auto-commit. Không chạy trên checkout có worker hoặc broker connection, không làm theo docs generic để auto-approve DB migration.

### Make kits / Community / tools

- Make kits bundle code package, library styles và guidelines [S9]; workspace chưa có shared package đủ chín nên **guidelines nhỏ + code slice trước**, kit sau M4 nếu có reuse thật.
- Package phải chạy standalone với Vite, không `workspace:*` hoặc path máy mình. Docs private registry có mô tả paid plans ở đầu nhưng organization/enterprise ở phần publish [S10]; quyền thực chưa xác minh. Không publish code public để né thiếu entitlement.
- Community free design files thường CC BY 4.0, không public domain; paid files/plugins/widgets có điều kiện riêng [S16]. Make tạo `Attributions.md` khi dùng Community context [S17]; worker vẫn phải kiểm asset/font/icon/license và giữ attribution khi đưa code về.
- Ảnh Community có Skills/Weave không là bằng chứng skill đó giúp dashboard. Không cài “xray”, shader, animation hoặc Weave chỉ vì hiện trong trang; không trong critical path hiện tại.
- Official MCP docs nay có read lẫn Design/Slides/FigJam write tools; không nói mọi MCP read-only. Nhưng **write Design ≠ tự prompt/điều khiển Make** [S5]. Plan chỉ dùng capability đã exposed/auth/probe.
- Code Connect là mapping design component→real code và hỗ trợ MCP, không đồng bộ app tự động. Xem seat/plan thực trước chọn [S6]. Không mua thêm chỉ để tạo mapping khi bảng contract nhỏ đủ.

## 5. Plan/Build và model: chốt cách dùng, chưa bịa benchmark

| Lựa chọn thật trong ảnh | Vai trò đề xuất | Đánh đổi / độ chắc |
|---|---|---|
| **Claude Opus 4.8 + Build** | Candidate đầu cho màn Watch/Review phức tạp với brief đã chuẩn bị | Hợp lý với ưu tiên first-pass của user; Figma khuyên Opus cho complexity/exactness. **Chưa chứng minh thắng Default** hoặc tiết kiệm tổng credits |
| Default | Mốc so sánh và đường dùng Plan an toàn theo docs | Model nền có thể thay, không biết là model nào; ghi ngày/file/label, không giả cố định |
| Claude Sonnet 4.6 | Iteration vừa, component/state fixes | Docs mô tả cân bằng versatility/efficiency, không cam kết credit ratio |
| Gemini 3.6 Flash | Chỉnh nhỏ/iteration nhanh | Docs khuyên Flash cho task đơn giản; không dùng “rẻ” để nhận output sai; code edit nhỏ có thể không cần AI |
| Gemini 3.1 Pro | Một đối chứng creative nếu finalist chưa tốt | Không benchmark thêm khi đã đạt; chưa có chứng cứ đẹp hơn mọi model |
| GPT-5.6 | Iteration/code-oriented candidate khi có gap cụ thể | Không đồng nhất chất lượng trong Make với Codex; harness/context khác |

**Build ngay** khi đã có screen brief, boundaries/states và reusable component map; đây là default cho lát đầu vì planner đã làm phần định hướng. **Plan rồi Build** khi scope chưa rõ, đổi navigation/state model hoặc task nhiều màn cần cân nhắc; không yêu cầu Make lập lại toàn PLAN Astra.

Docs Plan mode [S7] hiện ghi Default/Opus 4.7, không Gemini; ảnh user lại có **Opus 4.8**. Vì thế **không hứa Opus 4.8 + Plan**, không thay menu user bằng Opus 4.7. Preflight combo thực; cần Plan thì Default là documented fallback nếu user account hỗ trợ. Docs nói Plan thêm credits; [S8] nói non-default consumption biến động, không có bảng quy đổi cố định cho task này.

**Experiment E2:** một representative screen, cùng sanitized inputs/viewport/tasks. Chạy Opus 4.8+Build trước nếu entitlement/credit budget đã được phép. Nếu chưa đạt hoặc cần kiểm giả thuyết, duplicate baseline và thử Default+Build; không cho model sau xem kết quả model trước trong comparison. Ghi credits trước/sau, wall time, số vòng, pass gates, component reuse và công integration. Tối đa candidate đầu + một đối chứng + hai vòng sửa có mục tiêu; đây là budget thực nghiệm đề xuất, không permission mua credits. Dừng chọn khi đạt rubric, không thi đấu sáu model. Chưa đủ budget thì một candidate có nhãn **not comparative**.

Rubric reuse UI autonomy: workflow, đọc dữ liệu, states, accessibility, hierarchy, consistency, domain ergonomics, integration maintainability. Mục tiêu mỗi mục ≥4/5 là ngưỡng nội bộ, không thống kê khách quan; hard failures không bù bằng điểm đẹp. QA thực đi qua real app service; model không được tự nhận “production-ready”.

## 6. VI Dubber: đưa giá trị sử dụng lên trước thêm tính năng

| Ưu tiên | Capability | Reuse và mục đích | Chưa cần |
|---|---|---|---|
| P0 | Library local + Continue watching | Job/manifests/player hiện có; tìm lại video, biết bản nào xem được, resume | Plex/Jellyfin replacement, streaming cloud đầy đủ |
| P0 | Watch tách Review | Watch gọn video + subtitle/transcript; Review giữ sửa segment/A-B/QA; Engineer opt-in | Một cockpit kỹ thuật cho mọi lúc xem |
| P0 | Artifact/version rõ | Source, preview, final, QA pending, language, rendition; missing/stale khác ready | Tạo pipeline thứ hai hoặc đổi chất lượng bằng UI |
| P1 | Tìm transcript + bookmark/time link | Segment IDs/timestamps đã có; exact/text search trước, bookmark không đồng nghĩa đã học | Vector DB/RAG/chat với tất cả video |
| P1 | Export local / Drive opt-in | MP4 + SRT, transcript theo version, checksum; local vẫn hoạt động khi Drive lỗi | Gộp database/move nguồn lên cloud hoặc Drive streaming mặc định |
| P2 | Learn nhận link media | MT5 LearnCatalog nhận resource ref có quyền; citations/time anchors | Auto-generated strategy/trade hay tự ghi course completion |
| Later | Nhiều target languages | Dùng BCP-47 language tags và rendition/version từ đầu | Cam kết model TTS/QA hiện có hỗ trợ mọi ngôn ngữ |

**Media ≠ job:** một source có nhiều jobs/renditions; một job retry không tạo “video mới” giả. Trường tối thiểu: `media_id`, `source_fingerprint`, `job_id`, `artifact_id/revision/hash`, `source_language`, `target_language`, `duration`, `qa_status`, `preview/final`, `authorized_locator`, `availability`. Watch progress/bookmarks gắn identity + rendition/version; đổi transcript/audio cần mapping hoặc báo reset, không mang timestamp bừa sang bản khác.

**Data choice đề xuất:** manifests tiếp tục own pipeline artifacts. Media catalog/index và watch/bookmark metadata thuộc VI Dubber; ưu tiên store hiện có nếu đáp ứng, nếu chưa có thì project-local SQLite cho dữ liệu nhỏ có transaction/index [S20]. Không đưa media bytes vào DB, không dùng MT5 PostgreSQL như shared authority. Index rebuild được từ manifests; progress/bookmarks là dữ liệu user phải backup/restore, không coi là cache. Một repository interface nhỏ chỉ cho catalog, không ORM/framework plugin mới. SQLite file không đặt trong folder Drive sync đang live; dùng backup API/snapshot nhất quán [S21]. Server DB chỉ khi multi-machine writers/team được yêu cầu thực.

Playback reuse HTML media/browser support + backend range delivery đã kiểm, không tự viết streaming framework. Vì media dài, transcript phân trang/virtualize khi đo thấy cần; chỉ load đoạn gần cursor. Xác minh seeking, thiếu file, move/relink hash, external drive offline, audio/subtitle alignment và preview stale. Thumbnails tạo lazy/bounded không quét/tách toàn media lúc app boot.

## 7. Integrations và boundaries lâu dài

```text
UI-Systems: tokens / generic controls / accessibility contracts
        ├─ trading UI → MT5: research, risk, broker, Learn
        └─ VI Dubber: jobs, media, translation, Watch/Review
                    ↕ versioned artifact references, authorized APIs
              outbound connectors → Drive / Notion / Calendar
```

**Nguồn nào own dữ liệu đó.** Shared UI không là shared DB/auth/account. Mỗi project usable independently; cross-link chỉ metadata/authorized references, không chạy import Python modules của nhau. Một connector chung chỉ khi hai consumer cần cùng semantics; artifact exporter đầu tiên có thể project-local, không dựng integration service sớm.

Giữ thứ tự [Integrations brief](../WORKSPACE-INTEGRATIONS-RESEARCH-DRAFT.md): local artifact/Learn link → Drive export → MT5 report/Notion index → Calendar nhắc. Notion Education khảo sát trước: Plus 1-member/100 guests/30-day history, trường hợp đủ điều kiện và verify hằng năm; **không Notion AI unlimited**, không thay DB/broker authority. Không giữ ứng dụng chỉ vì có gói edu; gói/eligibility kiểm lại khi connect.

API/SDK + native jobs cho automation deterministic, MCP cho agent tương tác có scope. OAuth được user xác nhận một lần cho destination/budget/data class, refresh/revoke có state. Driver thật: Drive `drive.file` + Picker nơi phù hợp, không hiểu là toàn Drive/folder. Report checksum/version và remote ID; timeout create **UNKNOWN** → reconcile trước retry, không exactly-once promise. Calendar review không là economic-news feed. Notification chỉ một kênh được chọn, không cài nhiều plugin.

Cross-project reference contract giữ identity xác thực ở service, schema version, project/entity/artifact revision/hash, MIME/size, QA, timebase, rights/consent và correlation ID. Không trust `tenant_id` hoặc arbitrary local path/URL client đưa. Voice references, private transcripts, holdout, broker/account secrets, answer keys không export mặc định. Nội dung import/MCP/transcript là data, không instruction mở quyền.

n8n để sau khi native jobs/mapping không còn đủ tiết kiệm maintenance; Temporal/Redis/event bus/unified AI-company orchestrator chưa có bottleneck chứng minh. Không public tunnel MT5 để tiện SaaS webhook. Permission/governance phải ổn trước growth, không cần mọi microservice ngay.

## 8. Tool decision register

| Candidate | Quyết định | Trigger / điều kiện |
|---|---|---|
| Playwright test/CLI + current kit | **Reuse** | Product tests own semantics, screenshot/diff/traces bổ sung; không dùng fixture PASS đóng sản phẩm |
| Visual regression | Dùng `toHaveScreenshot`/existing screenshot checks khi baseline đã review | Cùng browser/OS/fonts/viewport; fixed fixtures, deterministic clock; không auto-update baseline cho qua [S15] |
| Figma official MCP/resources | **Preferred optional integration** | Exposed + OAuth + file/resource read probe. Không cần cài để hoàn tất research |
| Figma Make/manual run | **Important design lane**, bounded manual handoff | Account/cost/upload scope rõ; user không phải điều phối coding subagents |
| Make kits/Code Connect | **Conditional after shared pilot** | Real repeated components + entitlement; no fake library just to unlock tool |
| Storybook | **Conditional** | Existing test page đủ cho ít controls; adopt nếu variant/state review thực sự khó quản, không thêm ngay |
| Style Dictionary/token transformer | **Conditional** | Khi nhiều format/aliases cần build deterministic; initial supported token subset/CSS snapshot đủ thì không custom transformer/framework |
| New MCP/CLI/skill/context generator | **Không tạo trong vòng này** | Workflow lặp có lỗi/cost chứng minh, existing native/skill/tool không đủ |
| AI environment / UI skills | **Reuse, scoped adapt nếu cần** | Audit khi đổi instructions; không clone global/project rule |

## 9. Experiments trước promotion — chưa chạy trong research

| ID | Câu hỏi / nhỏ nhất có ích | Pass / hành động nếu không đạt |
|---|---|---|
| E0 | Current WIP + review R1–R7 còn đúng không? | Reproduce/fix/retest theo owning PLAN; scoped acceptance, không reset mọi việc |
| E1 | Windows Make extraction có usable code/resources không? | Một dialog/state-rich slice → Make → repo diff → UI QA; giữ URL/version/commit. Không được thì manual export hoặc autonomy, Make requirement pending |
| E2 | Opus Build đáng tổng credits hơn Default? | Rubric + integration correctness, credits/time/rework; không đo thì không tuyên bố winner |
| E3 | Library/progress store đủ nhanh/bền không? | Fixtures 1.000 media metadata/100.000 transcript segments; paginate/search/seek/restart/missing/restore; không nạp cả video. Mục tiêu đề xuất p95 local list/search ≤500ms, metadata initial load ≤2s, seek đúng segment trong tolerance chốt trước. Ghi máy/cold-warm; không đánh tráo thành network SLA |
| E4 | Shared token/control dùng được ở cả app? | React18/Tailwind3 + React19/plainCSS, keyboard/focus/VI/light-dark/states và screenshot; không đạt giữ project-local/adapt, không ép nâng stack |
| E5 | Drive/export có chịu mất mạng/duplicate/revoke? | Consented test destination; restart/reconcile/checksum/user content preserved; local path tiếp dùng được; chưa quyền thì mocks chỉ software-verified |
| E6 | Fresh coordinator đọc bản ngắn có tiếp đúng? | Locate baseline/status/owner, pending action, forbidden scope; artifact complete được kiểm, attempt uncertain không chạy lại side effect; repair docs nếu cần |

## 10. Packet Figma nhỏ, không copy nguyên PLAN

Worker điền packet sau vào một file theo slice trong repo/test sandbox, chỉ sau gate export:

> Cải thiện giao diện [màn cụ thể] của [VI Dubber/MT5], không viết lại backend hoặc stack. Đây là prototype sử dụng fixture đã gắn nhãn. Nguồn được phép: [source commit + selected files/frame], component map [path], token version [version]. Luồng chính [3–5 thao tác], states [empty/loading/ready/error/stale/denied], viewport [360/768/1440], nội dung tiếng Việt và unit/time đúng. Reuse [components] trước; chỉ đề xuất component mới khi thiếu. Flat-first, không nested cards vô nghĩa. Không thêm login/database/payment/AI provider mới; không bật network ngoài allowlist hoặc dùng tài khoản thật. Giữ preview/final hoặc replay/demo/live rõ. Output runnable code, file-change list, component/token mapping, dependencies/licenses/attribution, known gaps. Chỉ làm slice này; không tuyên bố production accepted. [Model/mode/budget đã chọn].

Giữ `Guidelines.md` ngắn, links có phạm vi, ví dụ pattern đúng/sai. Đây là template handoff, chưa gửi sang Figma và không là product runtime prompt.

## 11. Primary sources đã mở

Research qua HTTP read-only vì phiên này không có web-search tool; help search chính thức dùng để tìm đúng bài, rồi mở nội dung bài. Endpoint Help API search 404 không được dùng làm bằng chứng app thiếu tính năng. Không đưa credentials vào requests.

| ID | Nguồn | Điều được dùng |
|---|---|---|
| S1 | [Make → GitHub](https://help.figma.com/hc/en-us/articles/35463818346647-Push-from-Figma-Make-to-GitHub) | One-way, Make-created repo/default branch, overwrite, không branch management |
| S2 | [Make in your local codebase](https://help.figma.com/hc/en-us/articles/40775535020695-Make-in-your-local-codebase) | Local repo/commits/branch/PR, closed beta Mac |
| S3 | [Local setup/gotchas](https://help.figma.com/hc/en-us/articles/40789739982871-Make-in-your-local-codebase-Setup-gotchas-and-troubleshooting) | Windows planned; config/bootstrap/ports; pricing/seat chưa final |
| S4 | [Make resources to agent](https://developers.figma.com/docs/figma-mcp-server/bringing-make-context-to-your-agent/) | Resource fetch và reuse components; requires client resources support |
| S5 | [MCP tools](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/) | Distinguish read/write/file types, không suy Make prompting |
| S6 | [Code Connect](https://developers.figma.com/docs/code-connect/) / [GitHub permissions](https://developers.figma.com/docs/github-permissions/) | Mapping ≠ sync; permission table ≠ availability mọi surface |
| S7 | [Plan mode](https://help.figma.com/hc/en-us/articles/40830441709719-Use-plan-mode-in-Figma-Make) | Optional alignment trước build, model compatibility caveat |
| S8 | [Model selection](https://help.figma.com/hc/en-us/articles/36400680326551-Select-an-AI-model-to-use-in-Figma-Make) / [credits practices](https://help.figma.com/hc/en-us/articles/40097793879191-Best-practices-for-optimizing-AI-credits-in-Figma-Make) | Cost biến động, guidelines/reuse, model roles, Default changes |
| S9 | [Make kits](https://help.figma.com/hc/en-us/articles/39241689698839-Get-started-with-Make-kits) | Packages/library styles/guidelines, test trước publish |
| S10 | [Bring package](https://help.figma.com/hc/en-us/articles/43602872461079-Bring-your-design-system-package-to-a-Make-kit) | Standalone/Vite/npm/private scopes, entitlement ambiguity |
| S11 | [DTCG format 2025.10](https://www.designtokens.org/tr/2025.10/format/) | Portable typed tokens/aliases; not W3C Standard |
| S12 | [Radix primitives](https://www.radix-ui.com/primitives/docs/overview/introduction) | Incremental unstyled accessible behavior |
| S13 | [shadcn/ui](https://ui.shadcn.com/docs) | Open-code distribution, maintenance ownership |
| S14 | [React Aria](https://react-spectrum.adobe.com/react-aria/index.html) / [MUI](https://mui.com/material-ui/getting-started/overview/) | Alternative behavior/full-system tradeoffs |
| S15 | [Playwright visual comparisons](https://playwright.dev/docs/test-snapshots) | Screenshot baseline/environment caveats |
| S16 | [Community licensing](https://help.figma.com/hc/en-us/articles/360042296374-Figma-Community-copyright-and-licensing) | Free/paid/design/plugin distinction |
| S17 | [Make + Community](https://help.figma.com/hc/en-us/articles/31304526749207-Figma-Make-and-the-Figma-Community) | Attribution file và attached resources |
| S18 | [MCP access](https://developers.figma.com/docs/figma-mcp-server/rate-limits-access/) | Plan/seat/client access/rate limits, check actual account |
| S19 | [Codex long-running tasks](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex) | Durable repo state + scoped validation; không proof custom WebGPT runtime |
| S20 | [SQLite use cases](https://www.sqlite.org/whentouse.html) | Local application data vs concurrent server needs |
| S21 | [SQLite backup](https://www.sqlite.org/backup.html) | Consistent snapshot/restore, không copy active files tùy tiện |

Docs sống có thể đổi; worker chỉ refresh mục đang dùng. Không biến source research thành lệnh install/publish. Phần integrations/Notion/Google giữ sources và limitations trong archive đã có; không cần nhân bản toàn bộ research đó ở đây.

## 12. Reverse-skill — bổ sung cho review 26/09

**Quyết định:** dùng chọn lọc tài liệu review, không đưa toolkit vào product/runtime và không dựng thêm tầng điều phối security. Mapping cụ thể cùng gate/receipt nằm ở [PLAN §10A](../WORKSPACE-NEXT-STAGE-PLAN.md#10a-reverse-skill--lớp-review-có-chọn-lọc-không-thêm-runtime), không là checklist/ledger thứ hai ở đây.

| Bằng chứng / giới hạn | Kết luận áp dụng |
|---|---|
| [Upstream](https://github.com/zhaoxuya520/reverse-skill), local `tooling/reverse-skill`, VERSION `1.0.1`, HEAD `cab634bd855fc287f6e420c1f36fd1a6b9245960`; local status clean khi kiểm lượt cập nhật | Reference snapshot, không claim đã activation hoặc audit toàn package. Upstream đã đối chiếu cùng SHA trong lượt research trước; không fetch/update ở lượt cập nhật này |
| Đã đọc code-audit, api-security, supply-chain-security, llm-security, case-review, protocol-reverse và ops evidence/supply-chain | Chọn checklist theo trust boundary. Các mệnh lệnh NOW/ACT trong playbook không vượt yêu cầu planning hoặc gate activation |
| [AGENTS](../../tooling/reverse-skill/AGENTS.md) và [RULES](../../tooling/reverse-skill/RULES.md) yêu cầu approval exact commands/effects trước repo scripts | Đọc/checklist-only được tách khỏi execution; không cần kích hoạt package để review code/test của project theo quyền task hiện hành |
| [master-route.ps1](../../tooling/reverse-skill/skills/scripts/master-route.ps1): tạo thư mục ở line137, ghi route-scope.md ở line169 tại SHA trên | Không chạy router như bước read-only. Hướng dẫn workspace “auto-run/unlocked mk-open” đã được sửa thành scoped consent, không đổi source upstream |
| Lượt research trước: tool-index chưa có; các tên Semgrep/CodeQL/Gitleaks/OSV-Scanner/Bandit không tìm thấy trên PATH, không phải inventory toàn máy | Không đồng nhất repo clone với tools installed; worker verify capability khi có nhu cầu thật. Không tạo bootstrap setup làm prerequisite của mọi task |
| Main repo MIT; nghiên cứu trước ghi CTF-Sandbox-Orchestrator GPLv3 và external tools có license riêng | Không dùng license root để suy mọi tool/asset được redistribute; kiểm file/tool cụ thể nếu đưa vào sản phẩm. CTF toolkit không nằm trong scope iteration |
| case-review kiểm schema riêng work/case; project đã có ledger/receipts | Reuse nguyên tắc evidence→finding→fix/regression, không chuyển cả product ledger thành case database để khớp script |

**Giá trị:** checklist phát hiện thiếu sót sớm ở CSV/export, input/process, resource permissions, dependency và AI-content boundary. **Đánh đổi:** nạp/chạy cả package sẽ tăng context, tool/install maintenance và quyền ngoài nhu cầu. Các số liệu tỷ lệ phát hiện/khai thác trong playbook chưa có bằng chứng cho project này nên không dùng để chấm điểm hoặc tuyên bố an toàn.

**Verification đề xuất, chưa chạy:** M0 có CSV regression; M5 có resource/path/owner fixtures; M2/M6 có nội dung giả chỉ dẫn đổi quyền/destination; dependency change có provenance/license review; M7 đối chiếu findings với fix/tests/not-run. Scanner là bổ sung, không oracle duy nhất. Functional/UI/trading tests giữ authority riêng; manual triage không được biến gap thành PASS.

Lượt này chỉ đọc local source/docs và cập nhật tài liệu/instruction routing. Không chạy repo scripts, scan target, cài tools, sửa global MCP/config, capture mạng, gọi provider hoặc broker. Full code-security audit của reverse-skill và runtime effectiveness vẫn **NOT RUN**.
