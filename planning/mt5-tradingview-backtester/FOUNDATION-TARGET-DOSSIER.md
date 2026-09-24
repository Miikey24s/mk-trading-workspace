# Target dossier — thiết kế để kiểm chứng trước F5

v0.1 · 21/09/2026 · **HISTORICAL F1 DESIGN DRAFT**.

**Cập nhật điều hướng 22/09:** user đã chốt [ADR PATH-2](FOUNDATION-ADR-0001-PATH2.md) sau evidence và review. File này giữ giả thuyết F1 ban đầu; trạng thái hiện hành là [FH hardening](FOUNDATION-RESEARCH-PLAN.md#9a-fh--gia-cố-nền-móng-trước-khi-mở-rộng), không đọc câu “chưa chốt” bên dưới như một gate chưa được giải quyết.

Đây là câu trả lời cụ thể cho “nếu xây mới hôm nay”: một baseline để thử, không danh sách mọi công nghệ. Mình đã biết code cũ nên không gọi đây là blind review. Các quyết định dưới đây là đề xuất cho vòng kiểm chứng, không đổi F5 thành PASS. Mục tiêu/knowledge không đổi; [E01–E18 và nguồn nghiên cứu](LONG-TERM-FOUNDATION-RESEARCH-2026-09-20.md) vẫn áp dụng.

## 1. Kiến trúc đích đề xuất

Một repo sản phẩm chia domain/packages; API/control core tổ chức theo module. Compute jobs và broker gateway có execution/resource/credential boundaries riêng. Khi nhỏ chạy cùng máy; khi lớn có thể chuyển compute/data services ra máy khác. Không biến mỗi domain thành microservice ngay.

| Subsystem | Baseline chọn để thử | Contract/invariant cần giữ | Alternative mạnh nhất / phép thử đổi quyết định |
|---|---|---|---|
| Client | TypeScript + React + Vite; routing/data-fetching/state conventions thống nhất | UI chỉ draft/presentation, không own risk hoặc auth; account/mode/stale/unknown rõ | Typed Vue client nếu representative UX/DX tốt hơn; E-CLIENT-01 |
| API/control | Python + FastAPI/schema validation; domain không import framework | API contracts/version/error/auth context; job không gắn lifetime request | .NET control nếu typed/runtime/ops evidence thắng; E-PERF-02 + D03 |
| Transactional metadata | PostgreSQL, module-owned tables; tenant-scoped constraints; RLS defense-in-depth | User/workspace/account/intent/reservation/job/audit identities rõ | Embedded DB nếu workload/ops thật cho thấy hợp lý hơn nhưng vẫn có target migration; E-PERF-03 |
| Historical data/artifacts | Parquet/Arrow, immutable manifests, filesystem adapter local | Source/license/version/checksum/known-at/QA/holdout không mất | Object storage khi remote workers cần; E-PERF-01/E-PORT-01 |
| Analytics | Một metric core có schemas/units/basis; columnar query adapter, DuckDB candidate | Canonical ledger/metric oracle, N/A, numerical tolerance, provenance | PostgreSQL read model cho queries nhỏ; benchmark mới quyết đường query nặng |
| Research/backtest | Isolated worker processes + durable job records; engine adapter với một engine chủ lực | Deterministic input, fills/cost/timing, cancel/checkpoint/budget, no broker credential | Narrow reference engine vs Nautilus/LEAN finalist sau semantic parity; không adopt hai engine production cùng lúc |
| Optimization/simulation | Scheduler theo run budget/seed/task attempts; partition inputs giảm copy | Kết quả không phụ thuộc retry count; OOS/holdout không leak | Native kernel/distributed compute chỉ khi profile chứng minh hot path |
| Execution/risk | Một execution authority/account; portfolio reservation authority nếu tổng risk nhiều account; gateway riêng | Durable intent + unknown/reconcile + capability/epoch binding; không retry send mù | Adapter trực tiếp API broker hoặc MT5 bridge theo capability; E-SAFE matrix bắt buộc |
| Broker integration | MT5 là adapter đầu tiên cần đánh giá, không là domain model | Instrument/order/deal/position account-bound; netting/hedging/fees/clock theo broker | Socket EA hiện có vs supported Python terminal API; bên nào đạt safety/ops mới chọn |
| Chart/replay | Renderer sau license/capability spike; anchors time/price riêng | No-future-leak, layouts/revisions, planned khác actual, VN labels | Lightweight Charts/KLineChart hoặc licensed existing; chưa chọn renderer bằng popularity |
| Product AI | Provider-neutral context/capability/eval boundary; offline default | No broker send; permission/tenant/holdout guard | TypeSafe narrow judgment là optional, không bắt entire AI stack |

Các runtime/package major versions chỉ pin sau compatibility/lifecycle check tại F3; không đưa một version mới nhất hôm nay thành yêu cầu 5 năm. Chọn ít languages/platforms; không tự tạo Rust/Go service trước khi có hot path hoặc safety/operability evidence.

React docs nêu trade-off app-from-scratch: routing/data-fetching conventions phải giải quyết có chủ đích. Workspace không có nhu cầu SEO/SSR đã xác lập, nên Vite là candidate nhỏ gọn, **không license để mỗi agent tự chọn router/query/state library**. F3 chốt một bộ conventions sau representative slice. Nếu requirement đổi cần framework SSR, client contracts vẫn độc lập.

## 2. Luồng state/data và boundaries

| Luồng | Authority | Khi crash/retry |
|---|---|---|
| User request → auth/account scope → command | API/domain service; server verifies identity | Không tin client tenant/policy snapshot vô thời hạn |
| Research run → queued job → worker → staged artifact → publish manifest | Job/manifest owner; immutable inputs | Attempt output chưa verify không thành success; duplicate attempts không ghi đè accepted run |
| User-confirmed intent → risk reservation → gateway → broker | Execution authority + broker evidence | Không có atomic DB+broker transaction; unknown giữ reservation và reconcile |
| Fill/evidence → analytics → chart/journal | Original fills/ledger immutable; annotations riêng | Corrections có linkage/version; không sửa historical result âm thầm |
| Local/cloud boundary | Một state authority hiện hành mỗi loại dữ liệu | Không active-active tự gửi lệnh khi disconnected; offline research khác offline trading |

Trước multi-user release: authn/authz, RLS application role không bypass, worker/exports/cache/realtime tenant boundaries, secret ownership, quotas/noisy-neighbor và audit. Trước user-uploaded code: sandbox threat model riêng; separate process không tự an toàn cho arbitrary code.

## 3. Repo và AI development

Repo mới hay cũ chưa chốt. Target logical layout đề xuất: `apps/web`, `apps/api`, `workers/research`, `gateways/mt5`, `packages/contracts`, `packages/domain`, `tests/acceptance`, `docs/decisions`. Tên có thể đổi; dependency boundaries và owners mới là contract.

Canonical specs/decision/task state phải version cùng code khi đi vào implementation; không để clean clone phụ thuộc absolute path riêng ở `D:\ANNAM\TradingWorkspace\planning`. Việc chuyển ownership specs thực hiện một lần có index/version, không duy trì hai bản writable.

Một coordinator + scoped subagents theo [operating plan](COORDINATOR-OPERATING-PLAN.md); shared contracts/migrations/lockfiles do integration owner kiểm. Typecheck/schema/codegen drift + negative tests + integrated-revision verification. Không cần microservices hoặc nhiều repos để có parallel coding.

## 4. Đối chiếu implementation cũ sau target

| Bằng chứng source hiện có (read-only 21/09) | Giá trị giữ lại | Giới hạn chưa giải quyết |
|---|---|---|
| `evidence_metrics.py`, `risk_lab.py` có phần tính toán không phụ thuộc Flask (imports hẹp quan sát) | Domain logic/test candidates có thể extract hoặc rederive | Chưa audit toàn dependency graph/numerical semantics; không mặc định port nguyên |
| `workspace_app.py` ráp phase factories và nhiều file SQLite | Workflows/ownership lessons; factory patterns có ích | Chưa có multi-tenant authority/data model đã được nghiệm thu |
| HTTP route gọi research runner đồng bộ | Narrow executable reference/oracle candidate | Job lifetime/recovery/scale khác target |
| Execution durable request/account/server + P4/P5 fixtures | Safety knowledge và observed broker behavior có giá trị cao | Chưa chứng minh multi-account authority/reservation/cross-process recovery target |
| UI/annotation/replay contracts và WIP U1–U9 | K01–K17 và user feedback; không mất các negative cases | UI approved chưa có; chart license/provider/runtime evidence riêng |

PATH-1 có lợi nếu refactor core/data boundaries nhỏ và đạt target; PATH-2 có lợi nếu pure modules extract sạch, coexistence nhỏ; PATH-3 có lợi nếu compatibility làm nền mới mang coupling cũ và clean rebuild thắng trên representative slice. **Chưa đủ experiment để chọn một PATH cuối.** Không dùng lựa chọn một coordinator làm lý do chọn PATH-3; vấn đề đó không bắt app rewrite.

## 5. Phép thử còn quyết định trước F5

1. Engine/ledger semantics + data provenance/cost/point-in-time oracle; không đổi outcome để tăng speed.
2. Two-tenant/access-path isolation và concurrent risk/intent/fault tests trên target authority.
3. Metadata/IO/compute SLO trên workload W0/W1 và budget W2; measure setup/backup/restore, không chỉ requests/s.
4. Một capability cùng acceptance corpus so effort/coupling/integration của ba PATH; desktop UI/API/data contracts có representative slice, không xây ba app hoàn chỉnh.
5. Coordinator durable-state/new-root recovery và (nếu muốn bật) genuine tool parallelism; failed capability có degraded mode rõ.

F1 draft này chốt **baseline cần thử**, chưa đánh dấu F1 toàn bộ/F2/F3/F4/F5 đạt. Khi evidence đủ, F5 phải ghi một PATH + ADR accepted và lý do loại hai hướng còn lại. Không đổi định nghĩa gate để né phép thử chưa làm.

## 6. Nguồn bổ sung và scope

- [FastAPI features](https://fastapi.tiangolo.com/features/): OpenAPI/schema/type-based validation; không performance proof trên repo.
- [React app from scratch](https://react.dev/learn/build-a-react-app-from-scratch): Vite và trade-off với framework; không nói React đẹp hơn mọi framework.
- [PostgreSQL RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html): role/owner/bypass caveats.
- Nguồn data/engine/MT5/security trong báo cáo research ngày 20/09 vẫn là evidence tham khảo; runtime/versions cần pin khi adopt.

Không tạo repo/DB, không cài dependencies/framework, không prototype hoặc migration trong lượt lập dossier này.
