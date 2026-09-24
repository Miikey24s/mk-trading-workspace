# Phụ lục nền móng — nghiên cứu, quyết định và chuyển tiếp

Ngày **23/09/2026** · v1.6 · **PATH-2 ĐƯỢC USER CHỐT; TIẾN ĐỘ THEO OPERATIONAL LEDGER — CHỈ CẬP NHẬT PLAN.**

**Đồng bộ 23/09:** operational RESUME đọc được ghi r219/FH và các U slices accepted đúng scope; bảng research dưới đây là snapshot review 22/09, không lệnh làm lại hardening. UI owner gate được user thay bằng agent review/QA theo [phụ lục UI/Figma/Prop](UI-AUTONOMY-FIGMA-PROP-PLAN.md). Không đổi ADR hoặc accepted receipts, không chạy lại test trong lượt planning.

Đi qua [PRODUCT-COMPLETION-PLAN.md](PRODUCT-COMPLETION-PLAN.md), không tạo một dự án triển khai song song. Phụ lục này quyết định nền dài hạn; U0–U9 vẫn quản lý hoàn thiện tính năng; cleanup C0–C2 và TypeSafe vẫn đi cùng slice liên quan.

Nguồn yêu cầu độc lập: [LONG-TERM-RESEARCH-BRIEF.md](LONG-TERM-RESEARCH-BRIEF.md). Research trước quyết định: [báo cáo 20/09](LONG-TERM-FOUNDATION-RESEARCH-2026-09-20.md). User đã chốt [ADR PATH-2](FOUNDATION-ADR-0001-PATH2.md) ngày 22/09 sau review của Astra. Luồng hiện tại là **research → chốt PATH-2 → FH hardening → từng lát sản phẩm + tích hợp liên tục → nghiệm thu toàn hệ thống**. Không chạy lại research từ đầu chỉ vì các phần protocol bên dưới dùng thì tương lai.

## 1. Phạm vi và thứ tự

Không chọn công nghệ vì plan cũ đã chọn hoặc vì một worker quen dùng. Câu hỏi đầu tiên là **xây từ số 0 cho 3–5 năm tới thế nào**, mang theo knowledge nhưng không mặc định mang implementation. Tách ba quyết định: **nền đích tốt nhất → PATH-1/2/3 đi tới nền đích → cho phép triển khai**. Architecture B trong báo cáo không đồng nghĩa PATH-2 giữ một phần code.

| Mốc | Đầu ra | Phụ thuộc | Trạng thái hiện tại |
|---|---|---|---|
| F0 | Knowledge pack trung lập, workload và as-is inventory để đối chiếu sau | Được giao research/verification | F0-REFRESH accepted trong run hiện hành; port coverage vẫn theo từng capability |
| F1 | Greenfield target dossier, invariants/contracts và test protocol | F0 knowledge/workload; trước xếp hạng PATH | F1-C2 accepted trong run; dossier ban đầu giữ làm lịch sử |
| F2 | Trading safety, tenant isolation, recovery spikes cách ly | F1; fixtures, không broker thật | F2 r4 accepted trong fixture scope; Astra chạy lại 20 test PASS, không đồng nghĩa product/live safety đã đạt |
| F3 | Performance/storage/runtime/client candidate spikes | F1; workload/budget cố định | F3 r2 và evidence F5 có kết quả; không có claim mọi workload/scale đã benchmark |
| F4 | Một Web GPT coordinator + subagents, durable state/recovery và tích hợp | Specialist runtime findings + F1 cho product rehearsal | Ledger CO-00…06 accepted ở scope đã ghi; core local fixture đạt, native overlap/multi-instance/10 và fresh-root chưa verified |
| F5 | Chọn nền đích và đúng một PATH-1/2/3, ADR + evidence | F2/F3/F4 evidence | **PATH-2 được user chốt 22/09**; chỉ mở lại theo revisit trigger của ADR |
| F6 | Reference slice theo PATH đã chọn, handoff/restore/rollout proof | F5 + giao việc triển khai riêng | Worker đã có local/synthetic reference slice; giữ evidence và WIP, không gọi production-ready |
| F7 | Nghiệm thu baseline đích, knowledge coverage, cập nhật U/Y | F6 acceptance | Baseline r2 PARTIAL_ACCEPTED; **FH-0…FH-3 cần làm tiếp** trước mở rộng capability phụ thuộc |

Luồng phụ thuộc: **F0a/b knowledge + workload → F1 target/contract đầu tiên → F0c đối chiếu implementation → {F2, F3, F4 đủ điều kiện} → F5 → F6 → F7 → các U còn thiếu.** F1 không chờ xếp hạng implementation của F0c. F2/F3 có thể chạy song song trên resource namespaces riêng; F4 đo ngay hai lát độc lập có contract chung, không cần thêm bộ demo lớn.

F0–F5 là nghiên cứu/kiểm chứng; F6–F7 là kế hoạch chuyển tiếp chỉ được chạy sau approval tương ứng. Việc user giao “research” không tự cho phép migrate production, deploy cloud hoặc broker orders.

## 2. F0 — thu knowledge, không đưa implementation thành đề bài

F0a đọc mục tiêu/workflow/bugs/checkpoints và hoàn thiện [Knowledge Preservation Register](KNOWLEDGE-PRESERVATION-REGISTER.md). Tạo knowledge pack theo hành vi, không ép tên class/routes/schema/lang hiện tại. F0b chốt workload/giả định. As-is inventory F0c được dùng **sau khi F1 ghi bản greenfield target đầu tiên**, để so PATH chứ không thiết kế mục tiêu quanh code cũ. Người đã biết repo công khai anchoring; không giả là blind review.

- Ghi HEAD, diff/untracked manifest và hash các file thuộc scope; không gọi HEAD là toàn bộ build khi có WIP. Kiểm phiên khác đang sở hữu phần nào; không stage/commit thay họ.
- Map `requirement → module → persisted state → consumer → tests → runtime evidence`. Phân biệt source hiện có, checkpoint từng chạy và tính năng đã được người dùng nghiệm thu.
- Kiểm kê SQLite/JSON/cache/artifact formats bằng source/schema hoặc bản sao được phép, không mở holdout hay credentials để “audit cho đầy”. Xác định broker/data/chart licenses cần gate.
- Shortlist tối đa 2 phương án kỹ thuật mạnh nhất cho mỗi quyết định cần thử sau desk research; chúng có thể đều mới, không bắt giữ một suất cho incumbent. Ba PATH vẫn đều phải được đánh giá bằng lý do/evidence; không dựng ba app hoàn chỉnh.
- Chốt target release đầu và workload/limits có nhãn giả định; không cần trì hoãn toàn research chỉ vì chưa biết chính xác số user tương lai.

### Workload envelope đề xuất để đo, không phải forecast

| Profile | Mục đích | Fixture ban đầu |
|---|---|---|
| W0 — local | Độ gọn và tương tác | 1 user, 1 máy, 2 clients, 1–3 fake accounts, 2 jobs |
| W1 — collaboration | Ownership và concurrency | 2 tenants, 10 users giả lập, 10 fake accounts, 8 jobs, 2 runtime hosts/process groups nếu được phép |
| W2 — stress | Tìm điểm gãy, không chứng nhận production | Sweep tới 100 clients/32 jobs; tăng dataset 1→10→100 triệu events khi đủ tài nguyên và budget |

Ghi event schema/size, total bytes, order/tick rates, missing/duplicate ratios, number of charts, strategy complexity. Raw số events không so được hai engine khác semantics. Dữ liệu synthetic và licensed fixture được phép; không tự mở all-time holdout hoặc sao chép dữ liệu lên cloud.

**Gate F0:** có knowledge/invariant inventory, budget RAM/disk/runtime/network, test-safe entrypoints và assumptions đủ cho F1. Current source snapshot để preserve/compare, không tự có điểm ưu tiên. Nếu hardware không đủ W2 thì ghi upper bound chưa đo, không tự thuê máy hoặc gọi đã scale.

## 3. F1 — thiết kế greenfield trước, chốt protocol kiểm chứng

Viết target dossier có boundaries, ownership, critical flows, nhỏ→lớn deployment và stack candidates theo D01–D13 dưới đây. Freeze phiên bản đầu **trước bảng điểm PATH**. Đích có thể được sửa sau experiments nhưng phải lưu lý do/version; không điều chỉnh lén chỉ để code cũ khớp hoặc code mới thắng.

| ID | Quyết định bắt buộc | Evidence/prototype cần có trước F5 |
|---|---|---|
| D01 | Kiến trúc tổng thể | E01–E18, fault domains, local ops + topology slice; xác định kiến trúc nào không đạt |
| D02 | Subsystem/data/authority boundaries | Sole-writer/transaction map; thử thay một subsystem không sửa lõi phần khác |
| D03 | Stack từng subsystem | Runtime/typing/toolchain/support/license, representative implementation, DX/performance theo workload |
| D04 | Data architecture | IO/RAM/concurrency/lineage benchmark; schema/export/restore correctness |
| D05 | Broker/execution architecture | Broker capability matrix, fake failure/reconcile suite; MT5 behavior là evidence không ép socket EA là cách duy nhất |
| D06 | Backtest/optimization | Independent ledger oracle; stateful timing/cost parity; deterministic parallel seeds, cancel/resume/budget |
| D07 | Multi-user | Hai tenant across request/jobs/cache/files/AI; authorization và secret isolation |
| D08 | Scale workloads | Saturation/noisy-neighbor/backpressure, resource limits, local→remote placement thử được |
| D09 | Contracts ổn định sớm | Money/time/IDs/events/errors/versioning + breaking/additive compatibility tests |
| D10 | Test/observability/reproducibility | Fault trace→audit→run lineage, fresh-environment replay và recovery proof |
| D11 | Cấu trúc repo | So một repo module/packages với nhiều repo có version; ownership/build graph/context burden qua rehearsal |
| D12 | Git/CI/integration song song | Independent sessions, isolated runtime data, integration queue và semantic conflict detection |
| D13 | Đầu tư ngay/trì hoãn | Hard-to-reverse map, upgrade triggers, 3–5 năm change scenarios; không hứa biết mọi feature tương lai |

Mỗi D có `option → alternative → source/experiment → result/unknown → accept/reject/defer → revisit trigger`. Không đóng bằng danh sách nhiều lựa chọn không quyết định; nếu evidence thiếu thì F5 chưa qua.

Tạo spec/fixtures trong nhánh nghiên cứu cách ly khi được giao; không migrate schema đang dùng chỉ để thử. Contracts cần đủ dùng, không là meta-framework mô tả mọi broker/asset.

1. **Identity/permissions:** principal, workspace/tenant, membership, account/broker/server/mode; verify ownership ở read/write/job/export/realtime/AI. “Default local workspace” là một scope explicit, không `None = all tenants`.
2. **Value semantics:** instrument ID/spec/version, price/quantity/money/currency, rounding, event/received/known-at timestamps, timezone/calendar, nullable/unknown/error meanings.
3. **State machines:** intent/order/deal/position khác nhau; job/attempt/artifact khác nhau; partial/unknown/reconciling/canceled rõ. Retry/cancel/expiry/idempotency scope và retention explicit.
4. **Data/run manifest:** lineage, rights, versions, immutable inputs, dirty-build hash, expected numerical tolerance và holdout controls.
5. **Application seams:** contracts cho client/core/worker/gateway/provider, capability negotiation, additive changes và rejection của unsupported versions. HTTP schema không ép engine nội bộ dùng JSON cho mọi tick.
6. **Ownership:** sole writers theo module, transaction boundaries, account/portfolio authority, compatibility windows và migration owner.
7. **Observability:** trace/job/intent IDs, audit schema, redaction, health/readiness/freshness và recovery evidence.

### SLO/recovery: đặt ngưỡng trước phép thử

Các số dưới đây là **ngưỡng thử đề xuất**, cần xác nhận ở F0/F1; không phải hiệu suất đã đạt hoặc yêu cầu broker:

- W0 metadata API: p95 ≤ 250 ms, không tính một backtest chạy xong; enqueue/ack job p95 ≤ 500 ms.
- Trên máy/browser đã ghi cấu hình: chart fixture 5.000 nến hiển thị, pan/zoom không có main-thread block kéo dài >100 ms lặp lại trong kịch bản; không tải all-time vào client.
- Khi W1 có compute nặng: latency control không quá 2 lần baseline, không starvation execution/reconcile lane; memory có hard budget và overload trả trạng thái rõ.
- Worker crash: job/intent không mất dấu; thử phát hiện trong 30 s ở môi trường fixture. Broker settlement/reconciliation latency có giới hạn riêng theo capability, không hứa luôn ≤30 s.
- Safety/integrity: **0 cross-tenant reads/writes; 0 unauthorized side effects; 0 duplicate broker sends trong các kịch bản đã định; không mất intent đã ACK durable trong fault model đã thử**. Không dùng thống kê p95 để tha một lỗi nghiêm trọng.
- Backup restore target đề xuất cho W0: thao tác phục hồi hoàn tất ≤30 phút; RPO theo lịch backup ghi thực tế. RPO cho disk/host loss khác crash process; không giả định local fsync sống sót khi mất cả máy.

Threshold có thể chỉnh trước đo theo nhu cầu/hardware; sau khi thấy kết quả không được hạ chỉ để phương án ưa thích pass. Ghi lý do nếu đổi protocol, giữ cả kết quả cũ.

## 4. F2 — chứng minh safety và isolation trước performance

Sử dụng deterministic fake broker có accepted/partial/rejected/timeout/event reorder/correction/account switch. Không gọi MT5 initialize/import side effect, không dùng runtime gateway thật, không broker login.

| Thử nghiệm | Fault/invariant | Evidence bắt buộc |
|---|---|---|
| E-SAFE-01 | Hai clients retry cùng intent; khác payload cùng key | Dispatch count, durable record, exact conflict reason |
| E-SAFE-02 | Crash tại các điểm trước/sau commit và send | Fault schedule + restart log + không resend unknown |
| E-SAFE-03 | Hai intents khác key cạnh tranh cùng account/portfolio risk | Atomic reservation, accepted/rejected set, independent sum oracle |
| E-SAFE-04 | Old owner sống lại, network partition, expired lease/intent | Gateway fencing hoặc failover denied; không tuyên bố broker fencing nếu không hỗ trợ |
| E-SAFE-05 | Partial fills, events trùng/trễ/sai thứ tự; cancel/replace races | Ledger/deals/orders reconcile, fees đúng, không suy từ event count |
| E-TENANT-01 | Đổi resource IDs qua API/cache/job/export/websocket/AI | Hai tenant fixtures, deny và không lộ existence nhạy cảm |
| E-TENANT-02 | Connection/worker reused; role bị thu hồi khi job chờ | Context không rò sang tenant sau; dispatch re-authorized |
| E-RESTORE-01 | Metadata + artifacts restore; intent backup cũ | IDs/hashes/counts/oracle đối chiếu; broker reconcile trước bật writes |
| E-DATA-01 | Late/corrected data, future suffix đổi, interrupted publish | Version mới; quyết định cũ không đổi; partial artifact không success |

Fault injection phù hợp sandbox; không kill tiến trình người dùng hoặc cố tạo lỗi/lỗ trên broker. Test concurrency cần nhiều interleavings/seeds và ghi số lần; một happy-path pass không bằng proof mọi lịch chạy.

**Gate F2:** điều kiện loại đạt trong fault model công bố, hạn chế ngoài model rõ; reviewer kiểm spec + oracle + code; không coi fake pass là broker-real acceptance. Nếu thất bại thì sửa scope thiết kế, chưa tối ưu tốc độ.

## 5. F3 — các spike có khả năng đổi quyết định

Chọn candidates từ greenfield dossier; incumbent chỉ là **một đối chứng tùy phù hợp**, không là default winner hoặc bắt buộc finalist. Dùng acceptance corpus từ K register; implementation cũ không là oracle. Khi hai engine khác semantics, xác định semantics đích bằng domain rules rồi mới so tốc độ.

| ID | So sánh | Đo gì | Kết luận cho phép |
|---|---|---|---|
| E-PERF-01 | Hai read/storage layouts từ target shortlist; current path là đối chứng nếu hữu ích | Cold/warm wall time, bytes read, peak RAM, checksum/row count | Chọn storage/layout, không thay đổi dataset semantics |
| E-PERF-02 | Job/runtime candidates xử lý cùng semantics, có saturation đối chứng | Control p50/p95/p99, job throughput, cancel/crash recovery, CPU/RAM | Quyết định compute boundary; không mặc định một scheduler |
| E-PERF-03 | Transactional store candidates từ D04, không bắt SQLite/PostgreSQL vào chung kết | Writer contention, transaction correctness, setup/backup/restore effort | Canonical target và migration/export; benchmark nghiệp vụ tương đương |
| E-PERF-04 | Hai engine/compute finalists, có thể đều mới | Independent ledger/fills/timing/cost oracle rồi runtime/RAM | Adopt/reject engine; semantics đúng trước speed |
| E-CLIENT-01 | Client/chart finalists trên 3 màn và UX lessons đã biết | Contract errors, interaction, chart performance, change effort, license | Chọn UI/chart stack theo nhu cầu đích, không vì số UI code đã viết |
| E-PORT-01 | Cùng contract trên local và topology tách | API/worker/gateway version mismatch, disconnect/resume, storage locator | Khả năng di chuyển từng lane; không gọi cloud-ready từ hai process trên cùng máy |
| E-PATH-01 | PATH-1/2/3 trên một capability đại diện sau khi có target | Knowledge coverage, delta công việc còn lại, coupling, compatibility/coexistence overhead và restore | Bằng chứng xử lý code cũ; không yêu cầu build ba sản phẩm đầy đủ |
| E-CHANGE-01 | Đổi broker fake, thêm client và đổi một contract có version trên candidate | Files/modules chạm, regression, test gaps, rebuild/release scope, handoff effort | Kiểm chi phí thay đổi tương lai; module thay được không chỉ là sơ đồ |

Nếu profile cho thấy HTTP/framework không đáng kể thì bỏ spike đổi framework. Nếu engine semantic parity chưa có thì dừng performance ranking engine; không so thuật toán/fill model khác rồi gọi nhanh hơn.

Ghi hardware/OS/runtime/dependency versions, dataset/schema/seed, concurrent load, test script version, cold/warm, mỗi lần chạy và environment noise. Dùng tối thiểu vài lượt lặp có warmup; report range/distribution, không chỉ lần nhanh nhất. Không dùng khoản benchmark nhỏ để hứa số user production.

Cost chỉ tính phần **từ hôm nay trở đi**: xây/sửa, knowledge/test/data port, local ops, updates, backup/restore, debug, remote-egress/storage nếu có, compatibility/coexistence, AI integration/rework và cơ hội capability còn thiếu. Không tính công/quota đã tiêu thành lý do cứu code. Không có ngân sách trần giả; cũng không bỏ operational cost vì user đủ tài nguyên.

**Gate F3:** có kết luận adopt/keep/defer/reject kèm lý do và dữ kiện có thể bác bỏ; benchmark fixture không có secrets/holdout. Không cần mọi candidate đều thắng hoặc mọi spike đều chạy nếu đã đủ evidence.

## 6. F4 — một coordinator quản agents, state bền vững và recovery

**Yêu cầu mới thay workflow cũ:** user giao một PLAN cho một Codex Web GPT coordinator; coordinator tự phân rã task, delegate subagents, phối hợp parallel khi có lợi, review/validate/integrate và tiếp milestone. Nhiều chat độc lập là optional, không bắt user tự quản/copy kết quả. Codex Web GPT là project `miuuyy/codex-chatgpt-web`; Native2 connector khác MultiAgent V2. Không sửa model/protocol/global config để giả runtime đã đáp ứng.

F4a runtime specialist đã có partial evidence ở run `20260920T233707Z-9b241f0d`; [synthesis](research/webgpt-native-v2/ASTRA-SYNTHESIS-2026-09-21.md) accept P01/P06 hẹp, hạ P04/P09 thành logic demos và giữ P02/P08 chưa đạt. Không có RESULT package complete. [Operating plan CO-00…06](COORDINATOR-OPERATING-PLAN.md) và [entrypoint](EXECUTION-ENTRYPOINT.md) định nghĩa F4b cần thực hiện sau khi được giao. Không retest mọi thứ chỉ vì parent progress file stale; reconcile actual evidence trước.

**Policy user cập nhật 21/09:** speed-first; **trần 10 browser turns tổng trên pool nhiều instance**, gồm root/reviewer/nested children, không phải 10 cho mỗi instance. Source/bundle hiện cap 5 mỗi instance, registry có hai instance riêng. Operating plan mục 2A–2C là nguồn admission/routing/snapshot; số dùng thật theo health, host capability, route và workload. CO-04 kiểm batch ngắn rồi tăng tải tới mức có ích; không biến default cũ 1–2 child thành giới hạn dài hạn, không coi 10 là capacity đã benchmark. Kiểm nhẹ từng task, review/debug sâu theo milestone; bảo toàn state/contracts/safety từ đầu. Không dừng toàn bộ research độc lập để chờ chứng minh mọi lỗi compaction/restart; các acceptance gates liên quan vẫn giữ.

1. Coordinator đọc authoritative PLAN/state, verify runtime capability/model/protocol; freeze contract revision/integration base và chia tasks có dependencies/acceptance. Không giao dựa trí nhớ chat.
2. Mỗi writer task có branch/worktree hoặc isolation đã nghiệm thu; DB/tmp/ports/artifact namespace riêng. Không giả mọi subagent tự có worktree; coordinator cấp và kiểm. Không broker credentials/shared writable data/global UI config.
3. Một integration owner giữ contracts, migration numbering, shared dependency/lockfiles và public schemas. Task cần đổi shared contract phải gửi change proposal, không âm thầm sửa consumer riêng.
4. Author tự test phạm vi mình; reviewer theo quyền được giao; controller hoặc CI chạy checks khi reviewer read-only. Không lấy reviewer model trả “PASS” thay test evidence.
5. Integrate theo base mới nhất; compatibility tests + domain/safety regressions + vertical workflow test. Chỉ thử merge trong nhánh được giao, không tự push/deploy. Persist integration intent trước Git promotion để phục hồi cửa sổ Git đã đổi nhưng ledger chưa finalize.
6. Ghi active time/wall time tới accepted change, integration/rework, conflicts kể cả semantic, failure/attempt counts và quota nếu có telemetry. Coordinator sở hữu scheduling/backpressure/retry budget, không tự mở số agent vượt runtime/account capacity. Không suy quota miễn phí/vô hạn.

**Gate F4:** coordinator tự tổ chức hai phần ghép được theo contract; lỗi một/nhiều child không mất phần đã accepted; fresh coordinator từ state/evidence tiếp đúng phần thiếu; stale/duplicate results không được accept; integrated tests pass trong test scope và quyền. Actual compaction/same-thread resume/new-root recovery có evidence tách riêng, không gọi một loại test là proof tất cả. Một smoke chưa chứng minh speedup hay reliability bền vững.

Không bắt xây orchestrator riêng trước. Native tools, runner/CLI hiện có hoặc lớp durable state mỏng là candidates; chọn sau evidence. Runner v0.2 hiện serialize/tắt MCP/subagents không được mặc định làm nền execution mới. Đổi workflow/config thực tế là task triển khai sau, không nằm trong việc soạn prompt này.

### Durable state và recovery — yêu cầu đầu ra, chưa khóa công nghệ

- State phải nhận diện task/dependency/version/attempt/owner/base revision, inputs/outputs/hashes, dispatch, verification/integration receipts, remaining work/blockers và quyền. `agent returned`/`code written`/`tested`/`integrated`/`accepted` là trạng thái khác nhau.
- Cơ chế atomicity/snapshot/log/transaction, lease/fencing của **coordinator code work**, stale-result rejection và orphan reconciliation phải qua failure tests. Không sao chép broker execution protocol nguyên xi hoặc giả chúng có cùng side effects.
- Coordinator mới kiểm artifacts/process/branch state trước retry: có file chưa chắc task complete; ledger thiếu receipt chưa chắc action chưa xảy ra. Không xóa lock theo tuổi, không merge lại vì chat mất history, không hai coordinators cùng quyết cùng task.
- Review độc lập và deterministic validators không được thay bằng lời tác giả. Nếu child(s) lỗi, bounded retry/quarantine/circuit-breaker, làm phần độc lập còn lại hoặc degraded serial khi được phép; không fallback model/quyền âm thầm.
- Progress ngắn từ state thật: milestone, accepted/total trong scope version, running/blocked/next; logs chi tiết nằm artifact, không nhồi vào context. Checkpoint được ghi ở boundary quan trọng, không đợi chat sắp đầy.
- Khi hết runtime hoạt động, user có thể cần mở chat mới và giao cùng entrypoint; không hứa tự bật lại app. Người dùng không cần prompt nghiệp vụ mới hoặc kể lịch sử lại. Automation nền chỉ xét khi được yêu cầu riêng.

### Repo, Git và CI — protocol cần kiểm, chưa cài cấu hình

- Repo mới hay cũ tách khỏi câu hỏi monorepo/multi-repo. So ownership/package boundaries và release needs; nhiều repo chỉ thắng nếu version/release independence bù chi phí phối hợp. Không coi monorepo là một process hoặc microservices là nhiều repo bắt buộc.
- Nhánh ngắn theo task, mỗi session một worktree; base/contract revision ghi trong packet. Tài liệu đang ngoài repo chỉ là planning source; F5 phải chốt cách version code + contracts + specs để clean clone/CI không lệ thuộc đường dẫn máy cá nhân.
- PR/task checks: format/lint/type/schema/generated-code drift, module dependency rules, unit/contract/negative tests. Fixtures/temp DB/ports riêng; secrets và broker network deny trong test môi trường.
- Integration checks chạy trên **kết quả ghép với base hiện tại**, không chỉ từng branch xanh: consumer/provider, migrations trên copy, E-SAFE/E-TENANT, workflow end-to-end và UI acceptance theo scope. Shared schema/lockfiles có owner và xử lý tuần tự khi cần.
- Nightly/release khi được setup: fault/recovery, representative performance regression, clean setup/restore, dependency/license/security checks. Không kéo tất cả load tests nặng vào mỗi sửa chữ.
- Branch protection/merge queue, CI provider và artifact signing là quyết định triển khai sau; phiên viết plan không tự bật remote actions/push. Một task packet bàn giao phải có evidence của integrated revision, không chỉ câu “tôi test rồi”.

## 7. F5 — chọn nền đích và đúng một hướng codebase

Điều kiện bắt buộc: D01–D13 có kết luận/evidence; acceptance corpus trọng yếu đạt; bảng so ba PATH theo E01–E18 và **future cost**; chốt `Selected path: PATH-1 | PATH-2 | PATH-3`, lý do bác hai hướng còn lại và revisit trigger. Không chọn PATH-2 chỉ vì trông cân bằng, không chọn PATH-3 chỉ vì được phép xây mới.

| PATH | Bằng chứng để chọn | Bằng chứng khiến loại |
|---|---|---|
| 1 — Giữ/phát triển | Nền hiện tại phù hợp target, sửa cần thiết không kéo phụ thuộc sai xuyên hệ thống; thử các gates đạt | Chỉ pass fixture cũ; thêm tenant/authority/job phải vá rộng, failure isolation/operability không đạt |
| 2 — Nền mới + giữ một phần | Phần giữ có boundary sạch và còn phù hợp lâu dài; transitional adapters có expiry; coexistence/port costs đo được | Phải dựng compatibility layer lớn, duplicate writers/authority hoặc phải mang coupling cũ qua |
| 3 — Greenfield hoàn toàn | Thiết kế đích tốt hơn theo evidence; portable knowledge/data corpus đầy đủ; build/cutover feasibility rõ | Làm rơi critical workflows/bugs, demo nhanh nhưng thiếu ops/safety, chỉ thắng trên toy benchmark |

Đánh giá **target fitness trước**, delivery/cutover strategy sau; migration risk không đổi thành veto “phải giữ code”. Greenfield mới hoàn toàn vẫn có thể release capability theo từng lát và giữ hệ cũ read-only/archive trong thời gian kiểm chứng.

Một decision package ngắn cho chủ sản phẩm, chi tiết evidence liên kết:

- Hướng chọn và strongest alternative; E01–E18, các điều kiện loại và các unknown còn lại.
- Stack/runtime/storage/engine/client thực sự cần khóa; release/version/support/license policy.
- Deployment nhỏ nhất; số process/services cần vận hành, startup/shutdown, backup/restore và upgrade owner.
- Boundary/API/schema, repo strategy và triển khai theo PATH đã chọn; code disposition và knowledge/data disposition là hai bảng riêng; estimate theo slices và mức chưa chắc chắn, không bịa ngày hoàn tất.
- Rollback thực hiện được tới đâu; migration nào không thể đảo ngược đơn giản; acceptance và cutover gate.
- SLO/recovery targets; trigger nâng cấp (sustained queue lag, memory pressure, concurrency failures, independent release/security requirement).
- Phạm vi release đầu: local foundation, multi-user software-tested, remote deployment và public product là các trạng thái khác nhau.

ADR cần ghi `proposed/accepted/superseded`, evidence date, options rejected và revisit trigger. Không copy report recommendation thành `accepted` vì worker thích nó. Chủ sản phẩm duyệt chi phí vận hành/kiến trúc/dữ liệu đáng kể trước F6.

Nếu về sau xuất hiện evidence có thể đảo quyết định, mở revisit theo ADR và liệt kê phép thử cần thêm; không tự thay PATH. Protocol nghiên cứu trên đã được dùng để chọn PATH-2, nay user-approved 22/09; phần capability chưa verified không tự biến F5 thành OPEN.

## 8. F6 — reference slice theo hướng đã chọn, sau khi được giao triển khai

**Lát khuyến nghị:** Research job + dataset/run manifest + đọc kết quả bằng client, với hai tenant fixtures; hoặc lát account/intent nếu safety cần ưu tiên. Chọn tại F5. PATH-1 sửa nền hiện tại; PATH-2 xây nền mới và nối phần giữ theo seams; PATH-3 dựng clean reference slice trong repo mới chỉ từ contracts/knowledge corpus/data được phép. Không bắt PATH-3 bọc runtime cũ bằng façade.

1. Capture/backup baseline được duyệt; làm trên copy/sandbox; không đọc holdout ngoài protocol.
2. Với PATH-1/2 có consumers cũ, additive contracts/expand-contract khi phù hợp. PATH-3 có thể dùng schema/API mới; chỉ cần import/export mappings cho data/consumer thực sự phải hỗ trợ, không giả compatibility requirement. Migration idempotent/resumable; không tự gán dữ liệu không rõ chủ.
3. Façade chỉ nếu PATH-2 có lợi ích chứng minh; PATH-1/3 không bị ép dùng. Cả ba giữ một source of truth/canonical writer ở mỗi thời điểm. Shadow reads so được với oracle độc lập; **không dual-send broker** hoặc dùng hai engine ghi ledger authoritative.
4. Backfill/copy có checksums, counts, IDs, foreign keys, decimals/units/time, manifest và reconciliation oracle. Cutover cần write freeze hoặc catch-up có protocol; không rename DB file rồi gọi migration xong.
5. Chạy safety/contracts/consumer tests, canonical metrics diff và interaction test thuộc scope. UI mới không được bỏ trạng thái unknown/stale/mode/account.
6. Rollback rehearsed trên copy. Sau khi có writes mới, rollback phải xử lý chúng; không chép backup cũ đè rồi mất intents/trades. Irreversible migration cần recovery/roll-forward plan và approval trước.
7. Chỉ đưa capability đã đạt vào dùng theo rollout được duyệt; PATH-3 không phải bắt chước toàn bộ endpoint/UI cũ. Old/new coexistence nếu cần có hạn và ownership rõ; archive/decommission riêng sau K coverage/data handoff acceptance. Cleanup C1 cùng lát, không tự xóa repo cũ.

Gate pilot không cho phép broker orders hoặc cloud deploy. Những quyền đó theo U8/deployment gate riêng, sau software/data acceptance.

## 9. F7 — trở lại hoàn thiện sản phẩm trên baseline đã chọn

| Phần cũ | Xử lý sau F5/F6 |
|---|---|
| U0/core acceptance | Giữ lịch sử; lập foundation acceptance mới đúng build/scope, không sửa bằng chứng cũ |
| U1/UI exploration | Giữ research/references; triển khai trên client/contract đã chọn, agents tự duyệt bằng rubric/QA theo quyền 23/09; không chờ owner aesthetics |
| U2/Data | Áp catalog/lineage/entitlement/storage migration; real data QA vẫn cần |
| U3/Playbook-Journal-Learn | Tenant ownership và immutable revision; Learn vẫn core nhỏ |
| U4/Chart-replay | Renderer độc lập; annotate/cutoff/version semantics bảo toàn |
| U5/Research | Durable workers/job lifecycle và engine đã chọn; không coi fixture là production/OOS proof |
| U6/Analytics | Một metric source; data lineage/unknown/tolerance và empirical gates còn giữ |
| U7/AI + TypeSafe | Provider boundary, context/tenant/holdout guards; narrow judgments không nắm execution authority |
| U8/Demo-live | Giữ exact authorization, broker-specific acceptance và live gate; thêm concurrency/recovery contracts |
| U9/C2 | Integrated acceptance, clean setup, portability/restore, docs/license/Miro theo quyền |

Product plan vẫn là đầu mối giao worker. Sau foundation acceptance, cập nhật dependencies và task packets của các U; không ép hoàn tất mọi future capability mới được dùng local.

**Execution checkpoint 22/09/2026 — lịch sử:** F6 PATH-2 reference slice đã được re-verified và accepted trong local/synthetic scope. F7 baseline r2 ghi U0 software-verified; U2/U3/U4/U5/U6/U7/U9 partial; replay/cancel/cost/news/prop/restore có evidence. U1 tại thời điểm đó chờ owner duyệt; từ 23/09 gate này đã đổi thành agent review/QA theo phụ lục, không tự nhận UI pass. U8/demo/live vẫn cần quyền riêng. Xem [F7 checkpoint](F7-FOUNDATION-ACCEPTANCE-2026-09-22.md); operational ledger/RESUME own tiến độ mới hơn. Không suy partial thành full product COMPLETE.

### 9A. FH — gia cố nền móng trước khi mở rộng

**Trạng thái: PLANNED, chưa thực thi trong lượt chốt PATH.** Đây là phần tiếp của cùng product plan, không là dự án hoặc bộ điều phối mới. Astra giữ vai trò planner/reviewer; worker thực thi khi được user giao. Không yêu cầu dùng đủ 10 agents, hoàn thiện mọi recovery scenario hoặc dựng auth cloud trước khi tiếp công việc local an toàn.

Nguồn audit Astra 22/09: ledger SQLite khớp STATE revision 144; 32 research artifacts + 6 source/lock/receipt hashes khớp; chạy lại 16 controller + 20 F2 fixture + 3 product contract tests đều PASS. Không chạy lại toàn bộ PostgreSQL/UI/live. Kiểm method SQL cách ly cho thấy `complete_job` vẫn hoàn tất khi `cancel_requested=true`; đây là regression cần kiểm trên PostgreSQL thật cách ly, không claim đã reproduce mọi lịch chạy đồng thời. API hiện lấy workspace từ client header, chưa là authenticated membership. Worker slice chỉ hỗ trợ `--once`, chưa có đầy đủ recovery cho job mắc ở `running`.

| Task | Worker cần làm | Điều kiện nghiệm thu | Dependency / song song |
|---|---|---|---|
| FH-0 — chốt baseline | Reconcile ledger/owner và WIP thực; ghi exact source manifest/commit có chọn lọc, dependency locks, scope/commands và baseline evidence. Không stage/revert toàn worktree hoặc xóa artifacts cũ | Worker mới tìm đúng code/state/next task; historical accepted không bị sửa; baseline mới tái kiểm được và không dựa riêng HEAD `7c63a2f` vốn chưa chứa code v2 | Trước FH-1/FH-2; chỉ đọc metadata nguồn thật, không rerun F0–F5 |
| FH-1 — job lifecycle | Định nghĩa thứ tự cancel/complete, commit kết quả và trạng thái nhất quán; recovery job khi worker chết, attempt ownership/fencing và xử lý artifact chưa publish. Tái dùng store/worker hiện có | Test PostgreSQL fixture: cancel trước commit, complete trước cancel, crash sau claim/sau ghi artifact/trước finalize, stale worker quay lại, hai worker tranh job; không publish kết quả đã hủy theo contract, không job treo vô hạn hoặc chạy trùng ngoài ý muốn | Sau FH-0; owner riêng cho research/store lifecycle, phối hợp shared schema |
| FH-2 — quyền workspace | Tách trusted identity/membership khỏi workspace client yêu cầu; local identity adapter rõ ràng, authorization phía server. Chưa cần OAuth/IdP trả phí. Trong lúc chưa đạt phải khóa local-only, không công bố multi-user | Test đổi header sang workspace khác, membership revoke, thiếu identity và truy cập API/job/artifact khác tenant đều bị từ chối; UI/API không giả có production auth. App/DB role và RLS claims phải đúng bằng chứng, chưa làm thì ghi chưa hỗ trợ | Có thể song song FH-1 trên ownership/API contract đã thống nhất; không cùng sửa migration/lockfile |
| FH-3 — tích hợp và bàn giao | Ghép FH-1/FH-2 với baseline hiện tại; chạy focused + integrated workflow + restore cần thiết, cập nhật U/Y và resume state; khóa exact candidate được nghiệm thu | Luồng dataset → job → worker → result → UI còn đúng; negative auth/cancel/recovery PASS trên cùng revision; regression hợp lý, lệnh chạy local/rollback rõ; không claim UI owner/live/data thật đã đạt | Sau FH-1/FH-2; một integration owner |

Sau FH-3 (hoặc sau khi reconcile evidence FH đã accepted), worker được giao **full product plan** tiếp các U còn thiếu, không yêu cầu user mở chat chuyên môn. Mỗi slice là **build → focused checks/review → integrate → integrated checks → checkpoint**; nghiệm thu cuối bổ sung E2E/hiệu suất/khôi phục/UX. UI chỉ phát tán sau **agent review + runtime QA**, không cần owner aesthetics từ 23/09. Gates real data/provider/demo-live/holdout/deploy/Miro không bị bỏ; Y25/Y26 đi trong U, không reopen foundation research.

## 10. Quyền, báo cáo và điểm dừng

- Lượt hiện tại chỉ viết/sửa tài liệu. Không migrations, installations, benchmarks, runtime tests, agent launch hoặc execution.
- Worker được giao F0–F5 chỉ làm các spike cách ly trong phạm vi/budget được duyệt; OAuth/chi phí mới/cloud/data nhạy cảm/holdout/broker vẫn cần quyền riêng.
- Không tự sửa global AGENTS, skill, hooks, MCP, auth hoặc AI configuration. Nếu cần về sau, dùng đúng skill quản trị môi trường và audit; prompt không là security boundary.
- Mỗi mốc báo: kết luận, scope/build/data, evidence đã chạy, findings, còn thiếu, ảnh hưởng tới quyết định và bước kế tiếp. Không % hoàn thành khi mẫu số chưa ổn định.
- Dừng research khi đã chọn được phương án qua điều kiện loại, trade-offs được chấp nhận và còn lối đổi; không benchmark vô hạn. Dừng implementation trước chuyển quyền/data lớn nếu chưa approval.

**Định nghĩa thành công:** chủ sản phẩm hiểu nền móng đang đánh đổi gì; có kết luận một PATH dựa trên evidence; worker mới biết làm và kiểm chứng thế nào; knowledge/data không bị mất dù implementation cũ được bỏ; không có claim scale/safety/multi-user vượt quá evidence.
