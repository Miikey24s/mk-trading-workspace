# Nền móng dài hạn — kết quả research và đề xuất có điều kiện

Khởi tạo **20/09/2026**, nội dung research v1.4 ngày 21/09; cập nhật điều hướng **22/09/2026** · **HISTORICAL RESEARCH — PATH-2 NOW OWNER-APPROVED**.

**Quyết định hiện hành:** [ADR PATH-2](FOUNDATION-ADR-0001-PATH2.md) đã được user chốt 22/09 sau validation/review. [FH hardening](FOUNDATION-RESEARCH-PLAN.md#9a-fh--gia-cố-nền-móng-trước-khi-mở-rộng) là bước tiếp. Các đoạn research-open/proposal bên dưới giữ để truy lý do, không mở lại PATH hoặc yêu cầu rerun experiments đã accepted khi input không đổi.

**Đọc tiếp hiện hành:** [Astra synthesis 21/09](research/webgpt-native-v2/ASTRA-SYNTHESIS-2026-09-21.md), [target dossier](FOUNDATION-TARGET-DOSSIER.md) và [coordinator operating plan](COORDINATOR-OPERATING-PLAN.md). Đây là tiến độ mới, không thay evidence desk research thành benchmark đã chạy.

Đọc nhanh: mục 1, 4, 10 và 13. Đề bài trung lập nằm riêng tại [LONG-TERM-RESEARCH-BRIEF.md](LONG-TERM-RESEARCH-BRIEF.md); giao file đó trước nếu muốn người research khác đánh giá độc lập. Tác giả báo cáo này đã biết hệ thống hiện tại, không tự nhận đây là một blind review độc lập.

**Bổ sung của chủ sản phẩm:** được thiết kế mới hoàn toàn cho 3–5 năm, kể cả repo/language/framework/data/chart/broker integration. Không tính sunk cost thành ưu điểm của code cũ. Các recommendation v1.0 dưới đây được giữ như **giả thuyết cần so lại từ greenfield target**, không là kết luận buộc worker tiếp tục. [Knowledge register](KNOWLEDGE-PRESERVATION-REGISTER.md) giữ bài học; [F1 D01–D13 và F5](FOUNDATION-RESEARCH-PLAN.md) quy định cách chốt target và một trong ba PATH.

## 1. Kết luận có ích ngay

**Giả thuyết kiến trúc có cơ sở từ vòng 1:** hệ thống có ranh giới nghiệp vụ rõ, một lõi ứng dụng tổ chức theo module; tác vụ tính toán nặng và đường thực thi broker có ranh giới chạy riêng. Khi nhỏ, các phần ở cùng máy và được khởi động/quan sát thống nhất. Khi nhu cầu tăng, di chuyển hoặc nhân bản đúng phần cần tăng tải. Greenfield target có thể giữ hoặc bác hướng này; không cần chứng minh code cũ không cứu được mới được nghiên cứu hướng khác.

Đây là **modular core + isolated workers/gateways**, không phải tất cả trong một tiến trình, cũng không phải mỗi module thành một microservice. Ranh giới code, ranh giới dữ liệu, ranh giới quyền và ranh giới triển khai là bốn thứ khác nhau.

Đầu tư sớm nhất nên vào **định danh/quyền/ownership, semantics tiền và thời gian, lifecycle lệnh/tác vụ, provenance và migration**, rồi mới tối ưu hot path. Chọn ngôn ngữ nhanh nhất không chữa được gửi sai account hoặc double order.

Vòng 1 đã nêu candidate **typed Python/TypeScript/PostgreSQL/columnar storage/broker gateway**. Theo câu hỏi greenfield mới, candidate này **không có quyền ưu tiên do giống code hiện tại**; phải so stack theo từng subsystem với lựa chọn mạnh nhất khác. Không buộc incumbent vào chung kết, cũng không loại vì cũ. HTTP/client framework, engine, broker path và repo topology đều chưa được khóa.

Không hứa “không bao giờ phải viết lại”. Mục tiêu kiểm chứng được là: đổi UI không đổi execution semantics; thêm broker không sửa UI theo tên broker; chuyển compute sang máy khác không đổi run identity; thay storage không làm mất provenance; thêm user không phải vá `user_id` qua mọi đường dữ liệu.

## 2. Bằng chứng hiện tại và giới hạn

Kiểm read-only ngày 20/09: repo `projects/mt5-tradingview-backtester`, HEAD `7c63a2f85a7d211ec2feb51fe045b6aa92d62dcd`, branch `Nam`, ahead local `origin/Nam` 2 commit. **Worktree bẩn:** 19 tracked files đã sửa và nhiều module/test/UI mới chưa commit. Đây là công việc đang làm, không hoàn tác/stage/commit nó. HEAD không đại diện đủ cho source đang có.

Plan sản phẩm v1.4/checkpoints ngày 19/09 ghi U0 đạt; U1 chưa duyệt; U2–U9 có nhiều foundation phần mềm nhưng UI/provider/data/broker acceptance còn thiếu. Checkpoint ghi 197 tests pass; **lượt research này không chạy lại tests**, không import ứng dụng, không đọc DB/account/holdout, không dùng API key.

| Quan sát source | Hàm ý cho hướng dài hạn | Không được suy ra |
|---|---|---|
| `workspace_app.py:22` quản lý nhiều SQLite path và ráp app từ phase factories | Có factory/store để reuse; cần làm ownership nghiệp vụ rõ hơn trước khi phân tán | Không mặc định code hiện tại phải bỏ |
| `workspace_research_engine.py:32` gọi `runner.execute()` trực tiếp trong HTTP request | Job dài còn gắn request; cần lifecycle bền vững và worker độc lập | Chưa đo được mức tải gây chậm |
| `research_engine.py:75` đọc JSONL, gom bars rồi sort; có budget cap | Foundation tốt cho fixture; RAM/copy/scan cần benchmark dữ liệu lớn | Chưa kết luận Python là bottleneck chính |
| `execution_store.py:88` có durable request/fingerprint/account/server; control là singleton | Giữ idempotency và account binding; mở rộng explicit tenant/account/control scope | Chưa có chứng nhận multi-user hoặc multi-host |
| `execution_service.py` preview risk trước dispatch; journal giữ unknown | Cần thử aggregate risk reservation khi nhiều intent khác nhau cạnh tranh | Đây là rủi ro cần thử, chưa phải bug concurrency đã tái hiện |
| `mt5_data.py:25` có socket/request lock trong process | Có thể isolate gateway; lock trong process không tự là quyền sở hữu account toàn cụm | Không tự tăng web workers rồi coi broker path vẫn an toàn |
| UI/chart state đã tách time/price và revision khỏi renderer | Tài sản đáng reuse khi đổi client/chart engine | Chưa nghiệm thu renderer/license/visual interaction |

Không dùng dữ liệu từ account để làm research này. Không chạy số liệu hiệu suất rồi thiếu mô tả hardware. Nguồn web được đọc qua HTTP; không dùng Browser/Computer Use. Nguồn lỗi/không tải được ghi ở mục 14, không dùng search snippet làm bằng chứng.

## 3. Đặt điều kiện loại trước khi chấm công nghệ

Các hướng đều phải chứng minh:

1. Không vượt tenant/account/mode/permission boundary; không gửi lại một intent chưa rõ kết quả.
2. Không mất/mập mờ durable intent đã được xác nhận lưu; phục hồi có đối soát broker.
3. Risk invariant giữ đúng dưới thao tác cạnh tranh; account/user/version không chỉ nằm ở UI.
4. Dữ liệu/run/artifact kiểm được lineage và không lộ tương lai; restore/migration kiểm được IDs và số liệu.
5. Không chạy code chiến lược hoặc AI tool không tin cậy cùng quyền với broker secrets.

Chưa qua các điều kiện này thì performance cao không cứu được phương án. “Fail closed” có nghĩa từ chối mở rủi ro mới khi không đủ thông tin; không có nghĩa âm thầm đóng mọi vị thế hoặc chặn vĩnh viễn đường xử lý khẩn cấp đã được cấp quyền.

## 4. So sánh bốn hướng kiến trúc

- **A — ứng dụng tự chứa, một process chính:** module có thể rõ, storage local, compute/broker gắn runtime ứng dụng. Không mặc định A viết kém hoặc không thể có user auth; vấn đề là failure/resource coupling.
- **B — lõi module + compute workers + execution gateway tách:** API/control, tính toán và quyền broker tách; ban đầu cùng máy, cùng repo/release nếu có lợi.
- **C — microservices phân tán từ đầu:** nhiều service tự deploy và own data, giao tiếp qua network/events.
- **D — managed/serverless-first:** tận dụng backend/durable workflow/cloud services; local broker vẫn cần bridge. Không mặc định một vendor cụ thể.

Bảng là **nhận định định tính từ đặc thù workload**, không phải benchmark hay điểm 9,7/10. “Tốt” luôn cần implementation đúng.

| Tiêu chí | A | B — giả thuyết vòng 1 | C | D |
|---|---|---|---|---|
| E01 Mở rộng dài hạn | Có trần một runtime | Scale đúng lane trước | Độc lập cao, có phí phối hợp | Scale tốt trong capability dịch vụ |
| E02 Hiệu suất | Ít IPC; cạnh tranh tài nguyên | CPU/IO/trade được tách tải | Thêm network/serialization | Phụ thuộc limits, cold start, data locality |
| E03 Ổn định | Crash ảnh hưởng rộng | Cô lập compute/broker có chủ đích | Cô lập tốt nhưng nhiều partial failure | Managed giảm một phần ops, còn outage/provider |
| E04 Trading safety | Dễ transaction local; crash chung | Một owner/account, recovery rõ | Khó phối hợp distributed side effects | Retry mặc định có thể nguy hiểm |
| E05 Security | Ít bề mặt; quyền dễ dồn chung | Tách credentials và tenant context | Nhiều service identities/policies | IAM tốt nếu cấu hình đúng, thêm egress |
| E06 Maintainability | Tốt khi nhỏ/kỷ luật module | Cân bằng domain và số runtime | Version/dependency khó hơn | Ít infra code, logic dễ dính dịch vụ |
| E07 Thay thành phần | Dễ nếu boundaries thật | Ports/contracts tập trung ở seams | Được thay riêng; protocol migration | Bị giới hạn API/export vendor |
| E08 Nhỏ tới lớn | Rất nhẹ → cần tách tải | Local đơn giản → mở từng phần | Gánh ops trước khi cần | Local/offline thường khó hơn |
| E09 DX | Setup/debug dễ | Thêm worker nhưng có entrypoint chung | Cần dev environments nhiều service | Tooling/permissions/emulation phụ thuộc cloud |
| E10 AI agents | Context dễ phình nếu không chia | Packet/module/contract rõ | Nhiều ngữ cảnh phân tán | AI dễ dùng sai SDK/quyền/chi phí |
| E11 Nhiều AI sessions | File trung tâm dễ conflict | Ownership module, contracts trước | Ownership mạnh nhưng ghép khó | Còn conflict schema/API/infra |
| E12 Testability | Unit dễ, runtime coupling khó | Pure core + adapter/failure tests | Cần contract/integration toàn mạng | Emulation không thay provider test |
| E13 Debug | Một process dễ theo | Correlation qua ba lane | Distributed tracing là bắt buộc | Quyền truy cập/log giới hạn tùy dịch vụ |
| E14 Truy vết | Phải tự thiết kế | IDs xuyên app/job/broker | Nhiều hop dễ đứt context | Native trace không thay audit nghiệp vụ |
| E15 Integrity | ACID local tương đối đơn giản | Một transactional authority + artifact manifest | Cross-service transaction phức tạp | Dễ dual-write qua nhiều dịch vụ |
| E16 Reproducibility | Có thể tốt nếu pin inputs | Engine/job contract + immutable inputs | Thêm version/topology cần pin | Runtime dịch vụ có thể khó pin/export |
| E17 Chi phí đổi sau | Rẻ UI; đắt nếu dữ liệu gắn local | Có đường migration từng lát | Đổi sai service boundary rất đắt | Exit cost dữ liệu/workflow/IAM cần đo |
| E18 Phức tạp ngay | Thấp nhất | Vừa, dùng cho rủi ro có thật | Cao nhất trước khi có team/ops | Thấp vài phần, không chắc thấp toàn hệ thống |

**Vì sao B đáng kiểm chứng:** nhu cầu đã có cả compute dài và side effect tài chính; tách hai vùng đó có lý do hiện tại, không chỉ dự đoán scale. Nhưng chưa có bằng chứng cần service riêng cho Journal, Playbook, Learn, mỗi metric hoặc mỗi broker feature. Nguồn [S01–S02] cũng nêu khó khăn khi xác định boundary sớm; không coi monolith-first là chân lý áp dụng mọi nơi hoặc B là target đã được chốt.

**Khi cần xem lại:** có yêu cầu độ trễ cứng/HFT; tổ chức nhiều team tự release; compliance bắt buộc isolation vật lý; workloads/tenant nhiều tới mức không đạt SLO dù đã profile/index/partition; hoặc một managed platform chứng minh được đường local/cloud, safety và exit cost tốt hơn.

## 5. Ranh giới nền móng đề xuất

| Khối/owner | Own gì | Không được làm |
|---|---|---|
| Identity/Workspace | Principal, membership, role, policy, account ownership | Tin `tenant_id` do client tự khai mà không kiểm |
| Data catalog | Dataset/version, instrument identity, entitlement, manifest, QA | Sửa raw đã dùng rồi giữ nguyên version |
| Research | Strategy version, protocol, experiment/run/job lifecycle | Gửi lệnh broker hoặc đánh dấu edge vì test xanh |
| Execution/Risk | Intent, reservation, order lifecycle, account reconciliation | Nhận size/quyền từ UI/AI như kết quả authoritative |
| Evidence/Analytics | Ledger/read model, metric definitions, provenance | Sửa fill gốc hoặc dùng balance thay equity mà không ghi basis |
| Journal/Playbook/Learn | Annotation/rule revision/learning links | Làm owner thứ hai của fills hoặc trạng thái order |
| AI assistance | Context phạm vi nhỏ, provider capability, draft/eval/cost | Có credentials gửi lệnh hoặc vượt tenant/holdout boundary |
| Client/UI | Presentation, interaction, draft và cache cục bộ | Quyết định authorization/risk hoặc ghi DB trực tiếp |

Một module own tables/schema; module khác dùng contract/service hoặc read model được quy định. **Không nhất thiết một DB cho mỗi module.** Transaction cần atomic giữa risk reservation và intent nên gần cùng authority trước; tránh tách chúng thành distributed transaction chỉ để code “độc lập”.

### Luồng local/cloud và nhiều client

- UI web/desktop/CLI/AI client đều qua cùng application contracts; mode/account scope rõ. Desktop wrapper là quyết định phân phối về sau, không là nơi giữ nghiệp vụ duy nhất.
- Control app nhận command, kiểm quyền và lưu intent/job; compute worker đọc immutable input, xuất artifact rồi publish kết quả đã kiểm; client theo dõi progress có ID bền vững.
- Execution gateway chỉ giữ quyền account/broker đã cấp. Khi control ở cloud và terminal ở local: kết nối outbound có xác thực, device enrollment/revocation, freshness/expiry và policy snapshot; không mở socket terminal ra Internet.
- Mỗi loại state có **một authority hiện hành**, không để cloud/local đều tự sửa account state khi mất mạng. Offline research/annotation có thể hỗ trợ; lệnh offline không tự xếp hàng để reconnect rồi gửi muộn.
- Gateway mất control connection: mặc định không nhận rủi ro mới; protective orders đã ở broker vẫn là việc broker xử lý. Chiến lược tự chạy lúc offline chỉ là capability tương lai có policy/risk/expiry và quyền riêng.

## 6. Công nghệ: shortlist sau mục tiêu, không trước mục tiêu

### Runtime và codebase

| Hướng | Lợi ích | Giá phải trả | Quyết định đề xuất |
|---|---|---|---|
| Typed Python nghiệp vụ/research + TypeScript client | Hợp nghiên cứu, nhiều thư viện native, ít cầu nối giữa strategy và analytics | Cần strict type/schema checks; pure Python loop không tự nhanh | Candidate; không phụ thuộc Flask hoặc việc repo cũ dùng Python |
| C#/.NET core + Python research | Types/runtime/tooling mạnh; LEAN là ví dụ ecosystem trading | Hai backend runtimes; schema/packaging interop thêm công | Candidate ngang quyền ở bước đầu; kiểm execution/control/research boundary |
| TypeScript server/client + Python workers | Một ngôn ngữ cho UI/API, contract reuse tiện | Money/precision phải explicit; compute vẫn cần lane khác | Candidate ngang quyền; cần chứng minh DX, precision và worker semantics |
| Rust core hoặc Go services + research runtime | Runtime compiled; có thể hợp execution/compute/control theo yêu cầu khác nhau | Interop/packaging/toolchain và review; Rust và Go cần đánh giá riêng | Không loại vì migration cost quá khứ; không chọn chỉ vì danh tiếng performance |

Không có bằng chứng trong lượt này rằng AI viết đúng hơn X% với một ngôn ngữ/model. Static types giảm một lớp lỗi, không kiểm được semantics tiền, thứ tự event hay permissions.

**HTTP layer:** chọn sau domain/runtime/clients requirements, không bắt đầu từ “giữ Flask rồi xem có cần thay không”. Flask hiện có là đối chứng; nếu greenfield target không dùng Python thì không bắt so thêm framework Python. [S15] xác nhận async Flask vẫn chiếm một worker/request và không tự tăng CPU performance; [S27] phân biệt concurrency/parallelism. Tách job dài khỏi request là yêu cầu lifecycle dù framework nào, không chọn framework bằng “hello world”.

**Client:** TypeScript + một hệ component có contract rõ là hướng dài hạn đề xuất. React/Vue/Svelte hoặc vanilla hiện có phải so trên ba màn thật và state semantics; chưa có bằng chứng chọn framework nào tốt nhất. Core không phụ thuộc component framework. Design system là token/meaning/state/component contract, không là yêu cầu copy cùng style ở mọi project. Chart renderer sau license/performance/correctness spike; data adapter và annotation time/price độc lập renderer.

### Storage

| Dữ liệu | Hướng đề xuất | Vì sao / điều kiện |
|---|---|---|
| User/account/permission/intent/job/provenance metadata | PostgreSQL làm candidate chuẩn cho nền nhiều user/writer | Transaction/concurrency và RLS hỗ trợ; RLS không tự bảo vệ owner/superuser [S03,S19] |
| DB local đang có | Nguồn kiểm kê/export/knowledge, không bắt giữ ở nền đích | SQLite vẫn là candidate nếu phù hợp yêu cầu, không được ưu tiên do data hiện nằm ở đó [S04] |
| Market history và run artifacts lớn | Columnar files, manifest/version/checksum; local store trước, object storage adapter sau | Chọn cột/range thay tải toàn bộ; không nhét mọi tick vào DB giao dịch [S18] |
| Analytical query | Thử embedded columnar query engine trước distributed warehouse | DuckDB là candidate, chưa xác minh được trang concurrency trong lượt này; không dựa vào giả định multi-writer của nó |
| Lakehouse/table catalog | Để sau khi có nhiều writers, schema/partition evolution hoặc snapshot demand thật | Iceberg giải quyết những vấn đề này [S26], nhưng catalog/maintenance là chi phí cần chứng minh |

Không duy trì hai backend storage production đầy đủ ngay để “linh hoạt”. Chọn một canonical target sau F5; format export + migration có test là lối thoát. Generic repository che mọi tính năng DB thường chỉ dời complexity và làm khó dùng transaction đúng.

Mỗi DB candidate cần tính backup/upgrade/monitor/setup local theo **chi phí tương lai**. Nếu PostgreSQL không phù hợp, chọn phương án thắng trên target requirements, không tự rơi về SQLite chỉ vì đang dùng. **Tenant/IDs/semantics/ownership phải thiết kế ngay**; storage đích có thể hoàn toàn mới.

### Engine: reuse có chọn lọc

| Candidate | Điều đã có nguồn | Cần thử trước nhận |
|---|---|---|
| Engine hiện tại | Bar-breakout + fixture/reconciliation trong checkpoint | Semantics, workload lớn, strategy coverage; không biến prototype một luật thành universal engine |
| NautilusTrader | Rust/Python, event-driven, backtest/live, adapters [S16,S24]; upstream LICENSE LGPLv3 | Khả năng broker thực dùng, Windows build, fills/recovery, tính tương thích ledger và nghĩa vụ phân phối |
| LEAN | Modular trading engine, C#/Python [S17]; upstream LICENSE Apache-2.0 | Brokerage/data support, local packaging, model semantics và chi phí tích hợp |

Upstream tự mô tả “production-grade” không phải nghiệm thu cho sản phẩm này. License engine không thay license dữ liệu/chart/connector. Không giả định có MT5 adapter phù hợp, không fork cả engine về rồi giữ một bản sửa riêng khó cập nhật. Chỉ chọn một engine chính; giữ fixture/oracle độc lập để có thể đổi engine.

## 7. Trading safety phải thành contract và bài thử

### Quyền, identity và account ownership

Principal → workspace membership → account binding gồm broker/server/login/mode → action permission → risk policy/version. Kiểm lại khi dispatch, không chỉ lúc preview. Idempotency key có namespace owner/account; cùng key khác payload phải conflict, không trả nhầm kết quả cũ.

Mỗi account có một execution authority tại một thời điểm. Hàng đợi theo account không có nghĩa mọi read cũng phải serialize. Với risk liên account, invariant thuộc portfolio authority, không chỉ lock từng account.

Lease chỉ hữu ích nếu command có generation/fencing và gateway từ chối owner cũ trước khi gửi. Broker có thể không hiểu fencing: khi không chứng minh owner cũ đã mất quyền, **không automatic failover quyền gửi lệnh**. Process lock, distributed lock hoặc replica count không tự giải quyết split brain.

### Luồng command

1. Nhận intent có actor/account/mode/policy version, payload, idempotency key, confirmation context và expiry.
2. Validate quyền, instrument/capability, quote freshness và risk. Hai intent khác ID cũng phải reserve tổng risk/margin trong cơ chế atomic phù hợp.
3. Persist intent và reservation trước side effect. ACK “đã lưu” không phải “đã gửi/đã khớp”. Không giữ DB transaction mở suốt broker network call.
4. Gateway kiểm owner/policy/expiry/account thực, dispatch có broker request tag khi hỗ trợ, ghi các evidence nhận được.
5. Timeout/crash giữa send và response → **unknown**, giữ exposure reservation bảo thủ và đối soát. Không tự retry send chỉ vì queue/workflow chạy lại.
6. Đối soát broker orders/deals/positions; partial fills, cancel remaining, fees và thay đổi ngoài app giữ riêng. Event cũ không xóa evidence mới; correction hợp lệ tạo record sửa có liên kết.
7. Nếu broker không có idempotency/query đủ tin cậy: chặn intent liên quan, hiển thị cần can thiệp, không tuyên bố exactly-once end-to-end.

[S08] nêu `OrderSend=true` không đồng nghĩa khớp lệnh; [S09] nêu thứ tự trade transactions không bảo đảm và queue có thể mất events nếu xử lý chậm. Vì vậy event stream không thay reconciliation. [S06,S07,S20] hỗ trợ outbox/idempotency/retry, **không cung cấp transaction atomic giữa DB của ta và broker**.

### Failure matrix tối thiểu

| Ca lỗi | Kết quả bắt buộc |
|---|---|
| Double-click/retry cùng intent | Trả record cũ; không gửi thêm |
| Cùng key, khác account/payload | Deny/conflict, không lộ record bên khác |
| Crash trước/sau commit, trước/sau send | Recovery phân biệt chắc chắn/chưa biết; không resend mù |
| Hai lệnh cùng vượt tổng risk nếu cộng lại | Chỉ nhận tổ hợp trong hạn mức, không cùng pass từ snapshot cũ |
| Owner cũ sống lại sau lease expiry | Gateway deny epoch cũ; không chứng minh được thì failover bị khóa |
| Fill trễ, event trùng/sai thứ tự, partial rồi cancel | Ledger đúng phần đã fill + phần canceled; không nhân đôi hoặc mất fill |
| Quote cũ/clock skew/data gap | Không mở risk mới từ stale input; giữ reason/version |
| Account bị đổi trong terminal | Binding mismatch → khóa dispatch, báo đúng account |
| UI/AI/research worker lỗi hoặc quá tải | Không tự tạo broker action; execution lane còn budget tài nguyên |
| Restore backup cũ | Bắt buộc broker reconciliation; không replay pending send từ snapshot |

Kill switch tách block-new / cancel-pending / close/reduce; không ngụ ý stop-loss bảo đảm giá khớp. Safety ở đây không loại rủi ro thị trường, broker hoặc thanh khoản.

## 8. Dữ liệu, số tiền và khả năng tái hiện

**Định danh:** tenant/workspace, principal, broker account, instrument, strategy version, dataset version, job/run, artifact, intent/order/deal/position không dùng lẫn nhau. Symbol hiển thị không phải instrument ID. Tenant ownership khác user ownership; một workspace có thể có nhiều thành viên.

**Số và thời gian:** price/quantity/money/currency/unit/rounding explicit. Execution/accounting dùng fixed-point hoặc decimal theo contract; thống kê có thể float với sai số công bố. JSON boundary không làm mất chính xác integer/decimal trong client. Lưu UTC cùng source timezone/calendar/version khi cần; phân biệt event time, received time và known-at. Broker time không tự được xem là UTC.

**Data lifecycle:** raw immutable → normalize/version → QA/manifest → publish → pinned run inputs → artifact kiểm checksum → catalog. Publish artifact chỉ sau write/verify hoàn tất; orphan/partial files không thành run success. File/object atomicity khác nhau, cần protocol riêng; checksum đơn lẻ không ngăn kẻ có quyền sửa cả file và manifest.

Manifest tối thiểu: schema, content hashes/row counts/ranges, source/entitlement, calendar/instrument snapshot, transforms/version, gaps/corrections/known-at, storage locator không khóa vào đường dẫn máy. Dữ liệu sửa sau tạo version mới; dedupe/correction không âm thầm đổi run cũ.

Run manifest tối thiểu: strategy source/config hash, engine/build/dependency version, data manifests, split/holdout policy, cost/fill/risk assumptions, seed/random stream partitioning, timezone/calendar, numerical mode, resource limits và relevant environment. Dirty source cần snapshot hash riêng; Git SHA một mình chưa đủ.

Ba mức tái hiện: (1) cùng inputs/build cho deterministic ledger; (2) khác hardware/engine so invariants và sai số định trước; (3) live chỉ tái dựng quyết định từ evidence, không chạy lại thị trường để bảo đảm cùng fills. Gọi lại model AI không bảo đảm cùng output: lưu output đã dùng, context/version và human confirmation trong quyền retention/PII.

Backups phải phục hồi **metadata + artifacts + compatible code/config** cùng recovery point. Phải có restore rehearsal, RPO/RTO theo loại dữ liệu; RPO=0 trong mọi sự cố không phải cam kết mặc định của ổ đĩa local. Artifact/market data có thể dựng lại khác với intent/account audit không thể tùy tiện bỏ.

## 9. Multi-user security và khả năng quan sát

### Rủi ro lớn nhất khi thành sản phẩm

Không chỉ thiếu login: đó là **nhầm tenant/account hoặc thực thi code của user với quyền quá rộng**. OWASP [S10] nêu isolation phải đi qua cache/session/async work/storage; hậu quả trading là lộ dữ liệu và có thể gửi lệnh bằng credentials của người khác.

Thiết kế ngay RequestContext và JobContext được server xác thực, tenant-scoped keys/foreign keys, authorize mỗi read/write/export/subscription. Job dùng service identity giới hạn; thu hồi user/account permission trước dispatch phải có hiệu lực. Connection pooling không được giữ nhầm tenant context giữa request.

RLS nếu chọn PostgreSQL là defense-in-depth: role ứng dụng không owner/superuser/BYPASSRLS; test cả worker, connection reuse và admin maintenance [S03]. Không lấy một header tenant từ client làm authorization. Nếu quy định cần isolation mạnh hơn thì schema/database/compute riêng là quyết định riêng, không mặc định shared-table là đủ mọi khách hàng.

Secrets chỉ ở server/gateway scope; reference trong config, không ở prompts/logs/browser/localStorage. Encryption/rotation/revocation, CSRF/CORS/origin, local-device access và remote auth được kiểm theo topology. Loopback giảm exposure, không thay toàn bộ local threat model.

Code chiến lược không tin cậy cần sandbox OS/container/VM và hạn CPU/RAM/files/network; process tách riêng **không tự là security sandbox**. Chưa có sandbox được nghiệm thu thì chỉ trusted code; không quảng cáo upload arbitrary Python an toàn.

Multi-user commercial gate gồm quyền phân phối dữ liệu/chart, điều khoản broker/prop, privacy/retention và trách nhiệm vận hành; khả năng kỹ thuật không thay review pháp lý/kinh doanh.

### Debug/trace/audit

| Loại evidence | Dùng để trả lời | Đặc tính |
|---|---|---|
| Structured log + trace | Request/job đi đâu, chậm ở đâu? | Correlation IDs qua process/network; redact secrets |
| Metrics | Queue lag, reconciliation age, latency, RAM, error rate? | Labels có cardinality được khống chế; không mỗi user một label |
| Business audit | Ai đổi policy, xác nhận/gửi lệnh gì? | Actor/tenant/account/intent/version/reason; retention và quyền rõ |
| Data lineage | Con số/kết quả lấy từ đâu? | Manifest, transforms, ledger/run links |

OpenTelemetry [S11] là candidate chuẩn trace để đổi backend quan sát được; không bắt mua dịch vụ. Trace được sampling không thay audit bắt buộc. Nếu cần chống sửa audit bởi admin, thiết kế anchoring/immutable storage và threat model riêng; “append-only trong code” không đủ.

## 10. Performance: đầu tư đúng chỗ

| Workload | Bottleneck khả dĩ | Chuẩn bị sớm | Chỉ tối ưu thêm khi đo thấy |
|---|---|---|---|
| Lịch sử lớn | IO/decompress/parse/copy/sort/RAM | Columnar/range reads, manifest, partition hợp lý, bounded batches | Catalog phân tán, cache nhiều tầng, warehouse |
| Backtest/optimization | Stateful loop, candidate explosion, data copies | Job budget/cancel/checkpoint, process isolation, deterministic inputs | Native kernels/GPU/distributed execution nếu đúng loại workload |
| Replay/chart | Tải all-time, render/GC main thread, nhiều series | Viewport windows, aggregation/LOD có nhãn, bounded cache | Web worker/GPU renderer sau profiling |
| Realtime | Fan-out, slow consumer, reconnect storm | Backpressure, sequence/gap detection, resync, TTL | Dedicated streaming infrastructure khi backlog/SLO yêu cầu |
| Account execution | IO broker, stale state, contention | Per-account authority, bounded dispatch, reconciliation | Tách fleet gateway theo account groups, không scale send vô tội vạ |
| Analytics | Scan nhiều run/trades, repeated compute | Canonical metrics, projection/read model, incremental computation có oracle | Materialized views/column store riêng khi đo có lợi |
| API/control | DB queries/auth/cold paths | Pagination/indexes/timeouts/cancellation | Framework/language swap nếu layer này thật sự là bottleneck |

Không gộp “realtime market data” với “realtime hệ điều khiển độ trễ cứng”. Chưa có yêu cầu HFT/sub-millisecond. Nếu xuất hiện, mở lại execution/network/hardware design; kiến trúc này chưa chứng nhận điều đó.

Không drop order/fill events như tick để giữ UI mượt. Market updates có thể coalesce cho display nếu semantics cho phép; broker event mất/trễ phải detect và reconcile. User chạy tối ưu nặng không được chiếm hết CPU/RAM của execution/recovery.

Chưa có benchmark dự án chứng minh runtime/storage thắng. Protocol đo và trigger nâng cấp nằm trong [FOUNDATION-RESEARCH-PLAN.md](FOUNDATION-RESEARCH-PLAN.md), không dùng số marketing upstream thay đo local.

## 11. Một coordinator, nhiều agents và continuity

**Yêu cầu hiện hành:** một Codex Web GPT coordinator tự tổ chức execution thay user quản nhiều chats. Run specialist mới có [partial evidence đã thẩm định](research/webgpt-native-v2/ASTRA-SYNTHESIS-2026-09-21.md) cho đúng repo `miuuyy/codex-chatgpt-web`. Single-child và artifact recovery khả thi ở phạm vi đã thử; genuine tool parallelism, durable controller transaction và full restart/compaction recovery chưa được chứng minh. User đã chọn **speed-first, trần 10 browser turns tổng trên pool** ngày 21/09, thay default serial trước đó. [Operating plan mục 2A–2C](COORDINATOR-OPERATING-PLAN.md#2a-trần-tổng-giới-hạn-từng-instance-và-admission) tách policy ceiling, cap từng instance, host slots và capacity đã kiểm; dùng batch ngắn có ích để đánh giá, không coi 10 là benchmark đạt. Giữ state/contracts/isolation và gate liên quan, không cần hoàn thiện mọi tình huống recovery trước research độc lập trong scope.

Đề xuất **một repo sản phẩm với module boundaries được kiểm tra**, không tách repos/microservices chỉ để chia agent. Worker ngoài Codex vẫn dùng cùng Git/contracts; không cần nền tảng điều phối tự viết trước.

Coordinator cấp cho mỗi writer task isolation/branch/worktree phù hợp → data root/DB/ports/artifact dir riêng → packet có owner/dependency/acceptance; không giả subagent tự được cấp isolation. Git worktrees cách ly checkout, **không cách ly DB, ports, credentials hay global config** [S12,S13]. Không cho test dùng shared `execution.sqlite3` hoặc account thật.

Durable state là yêu cầu nền: task/attempt IDs, versions, artifact hashes, verification/integration receipts và pending/uncertain work. Coordinator mới reconcile actual files/process/branch state trước retry. Chat summary/compaction và child IDs không thay ledger project. Chọn cách lưu/atomicity/leases/dispatch sau specialist failure evidence; không mặc định phải dùng service điều phối lớn.

| Làm trước, có owner tuần tự | Sau đó có thể song song | Khi tích hợp |
|---|---|---|
| Domain IDs, money/time semantics, API/error/job/event schema, migration policy | UI đọc contracts; Data provider; Research worker; Analytics fixtures | Rebase/cập nhật contract version, chạy producer-consumer suite |
| Quyền/account/execution invariants | Adapter fake và fault tests có owner riêng | Safety reviewer + deterministic tests, không chỉ tác giả tự duyệt |
| Shared dependency/schema/design token thay đổi | Feature modules không sửa shared core tùy ý | Một integration owner/merge queue xử lý shared changes |

Task packet tối thiểu: mục tiêu/non-goal, base commit **và trạng thái WIP**, ADR/contracts đọc, allowed files/owners, dependencies, reuse map, acceptance examples + negative cases, test commands, resource namespace, rollback và handoff evidence. Chỉ cấp context liên quan, không đổ lịch sử chat vào mọi session.

Contract có một nguồn canonical; generated clients không được sửa tay. Type checks, schema validation, dependency-boundary checks, golden fixtures, property/failure tests và compatibility tests phát hiện lệch. OpenAPI [S22] mô tả giao diện, không chứng minh semantics; consumer/provider tests bổ sung [S23], chưa cần tự dựng Pact Broker ngay.

Rủi ro lớn nhất của AI code: cùng một assumption sai được lặp trong implementation **và test tự viết**, tạo cảm giác an toàn giả. Giữ oracle độc lập, negative fixtures, review risk-based và targeted mutation/fault injection cho tiền/quyền/ledger; không dùng cùng helper để tạo cả expected và actual rồi gọi là đối chiếu độc lập.

Rủi ro lớn nhất nhiều sessions: **semantic conflict** không hiện trong Git merge — cùng tên field nhưng khác units/meaning, stale schema, cùng own một account/DB, mỗi agent tạo một fallback. Contract/version và integration tests quan trọng hơn chỉ chia file.

Đo throughput bằng thời gian tới accepted integrated change, integration/rework time, escaped defects và quota; không số dòng code/số sessions. Khởi đầu rehearsal 2–3 sessions trên các lát độc lập; chỉ tăng nếu kết quả đo cải thiện. Không dự báo speedup tuyến tính.

Giữ workflow/tooling hiện có làm dữ kiện; source policy hiện dùng staging và reviewer read-only, không tự đổi nó trong lượt này. Nếu sau này thay AGENTS/skills/hooks/config cần workflow `ai-environment-maintainer` và audit được yêu cầu. Tài liệu OpenAI [S14] hỗ trợ context theo scope, nhưng prompt không phải cơ chế cưỡng chế quyền.

## 12. Thay đổi nào đắt, thay đổi nào có thể đợi?

| Quyết định | Chi phí đổi muộn | Nên làm bây giờ | Phần có thể đợi |
|---|---|---|---|
| Tenant/account/instrument identity | Rất cao, có thể sửa mọi dữ liệu | Chốt semantics, ownership và invariants | Identity provider/UI tổ chức phức tạp |
| Money/time/fill/order/ledger semantics | Rất cao, thay đổi ý nghĩa kết quả | Golden fixtures và contract version | UI editor nâng cao |
| Data lineage/immutability/entitlement | Cao, mất provenance không dựng lại được | Manifest/version/retention phân lớp | Lakehouse catalog lớn |
| Execution authority/recovery | Rất cao, risk tài chính | Unknown/idempotency/reservation/account scope | Active-active account execution |
| Module/data ownership | Cao nếu mọi module ghi chung | Dependency direction và sole writers | Nhiều independently deployed services |
| Storage engine | Vừa tới cao tùy data/SQL coupling | Canonical target và migration protocol | Replication/sharding đa vùng |
| API/event public contracts | Cao khi có nhiều consumers | Version/error/compatibility policy | Nhiều protocol/gateway framework |
| UI framework/chart renderer | Vừa nếu state/semantics độc lập | License, state contract, representative spike | Native mobile hoặc nhiều renderer đồng thời |
| HTTP framework | Thấp-vừa nếu domain tách | Không để request own job/broker lifecycle | Chuyển framework vì xu hướng |
| AI provider/model | Thấp-vừa nếu context/evals riêng | Capabilities, budgets, privacy, fallback rõ | Router tự động nhiều vendor |
| Orchestration/hosting | Vừa nếu config/state portable | One-command local, health/shutdown/backup | Kubernetes/service mesh/multi-region |

Đáng trì hoãn: full event sourcing mọi module, CQRS service riêng cho mọi read, custom distributed scheduler, plugin ABI đa ngôn ngữ tổng quát, offline sync tất cả state, tự viết message broker, nhiều DB production song song “phòng hờ”. Audit ledger/event history cần sớm **không đồng nghĩa** phải áp toàn bộ event sourcing.

## 13. Greenfield-first: nền đích và hướng codebase là hai quyết định

Không bắt đầu từ nâng cấp local/single-user hiện có. Thu knowledge và yêu cầu → thiết kế target cho 3–5 năm → kiểm chứng candidates → so PATH-1/2/3. Có thể bỏ phần lớn/toàn bộ implementation. Tuy nhiên kết luận tốt hơn dài hạn phải có evidence, không suy từ quyền được rewrite.

**Mức đầu tư hợp lý:** clean reference slice chứng minh `hai tenant → hai client → job/intent → artifact/audit → crash/restart/restore` theo knowledge corpus và broker fake; không import runtime sản phẩm cũ trong greenfield prototype. So finalists có thể đều mới; sau đó dùng cùng corpus đo route giữ/cải tạo/xây mới. Không build đầy đủ U0–U9 ba lần.

### Ba hướng phải được kết luận ở cuối research

| Hướng | Lợi ích có thể có | Chi phí/rủi ro tương lai phải đo |
|---|---|---|
| PATH-1 giữ/phát triển | Ít handoff/runtime cần thay nếu target đã phù hợp | Coupling/schema/authority cũ, effort sửa các thiếu sót và khả năng đổi sau |
| PATH-2 giữ một phần/nền mới | Giữ capability có boundary tốt, đưa cái mới vào dùng theo phần | Compatibility façade, hai runtime, migration kéo dài và ownership sai; không mặc định là điểm cân bằng |
| PATH-3 greenfield hoàn toàn | Thiết kế theo target không mang phụ thuộc cũ; repo/CI/schema có thể thống nhất từ đầu | Mất hidden requirements nếu knowledge chưa đủ, phát sinh lỗi đã từng sửa, build-to-usability và data/acceptance handoff |

Không dùng số LOC/tests đã viết hoặc quota đã tiêu làm tiêu chí giữ code. **Future transition cost không phải sunk cost**: effort port data/knowledge, residual safety risk, coexistence, vận hành và time-to-capability vẫn phải ghi, nhưng không tự động thắng long-term fitness.

[S28] nhấn mạnh outcome và knowledge khi thay hệ thống; [S29] nêu chuyển dần có thể không phù hợp nếu hệ nhỏ và thay toàn bộ đơn giản. Vì vậy không có luật “strangler luôn tốt hơn greenfield”. Đây là kinh nghiệm thiết kế, không chứng minh PATH nào đã thắng ở repo này.

Trước khi triển khai nền được chọn cần approval release scope/SLO/recovery/isolation/operability và data handoff. Researcher phải giải quyết D01–D13 trong plan, không đẩy câu hỏi chọn framework lại cho user khi đủ bằng chứng tự quyết.

**Giả thuyết B bị bác bỏ nếu:** không đạt safety/integrity; ops local không chấp nhận được; workload mục tiêu không đạt; hoặc thiết kế greenfield khác đạt cùng yêu cầu với long-term fitness tốt hơn. B có thể được thực hiện theo bất kỳ PATH nào; không dùng B để ngầm chốt PATH-2.

**Trạng thái kết luận:** chưa có final PATH verdict vì chưa chạy các phép thử quyết định. Báo cáo này là desk evidence + protocol, **không phải research đã chốt nền tốt nhất**. F5 phải chọn đúng một PATH khi đủ evidence; nếu chưa đủ, giữ research open và chỉ rõ experiment thiếu.

## 14. Nguồn đã đối chiếu và cách dùng

Truy cập ngày 20/09/2026; “current/latest/main/develop” có thể đổi. Khi adopt phải pin release/commit, license và dependency lock; ngày đọc docs không thay runtime acceptance.

| ID | Nguồn | Dùng cho |
|---|---|---|
| S01 | [Martin Fowler — Monolith First](https://martinfowler.com/bliki/MonolithFirst.html) | Kinh nghiệm/đối trọng về boundary và microservice premium; bài 2015, không benchmark hiện hành |
| S02 | [Microsoft — Microservices architecture](https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/microservices) | Scale độc lập, data consistency, testing và operational complexity |
| S03 | [PostgreSQL — Row security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) | Default deny khi bật; owner/superuser/BYPASSRLS caveats |
| S04 | [SQLite — Appropriate uses](https://www.sqlite.org/whentouse.html) | Embedded phù hợp; concurrent writers/network filesystem limits |
| S06 | [AWS — Transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) | Dual write, duplicate events và consumer idempotency |
| S07 | [AWS Builders Library — Safe retries](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) | Intent IDs, late requests, same key/different intent |
| S08 | [MQL5 — OrderSend](https://www.mql5.com/en/docs/trading/ordersend) | Return true khác executed; retcodes/events |
| S09 | [MQL5 — OnTradeTransaction](https://www.mql5.com/en/docs/event_handlers/ontradetransaction) | Không bảo đảm arrival order; queue 1024; reconciliation cần thiết |
| S10 | [OWASP — Multi-tenant security](https://cheatsheetseries.owasp.org/cheatsheets/Multi_Tenant_Security_Cheat_Sheet.html) | Context, IDOR, cache/jobs/files/noisy neighbors |
| S11 | [OpenTelemetry — Traces](https://opentelemetry.io/docs/concepts/signals/traces/) | Trace/span/correlation; không thay business audit |
| S12 | [Git — worktree](https://git-scm.com/docs/git-worktree) | Checkout độc lập, shared repository metadata |
| S13 | [OpenAI — Git worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees) | Nhiều task độc lập; trang developers.openai.com/codex/app/worktrees chuyển hướng tới đây |
| S14 | [OpenAI — AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | Instruction discovery theo scope; không là sandbox |
| S15 | [Flask — async/await](https://flask.palletsprojects.com/en/stable/async-await/) | Worker/request, background task lifetime và CPU-bound caveat |
| S16 | [NautilusTrader — Architecture](https://nautilustrader.io/docs/latest/concepts/architecture/) | Trading runtime components, messaging và recovery boundaries |
| S17 | [LEAN — source README](https://github.com/QuantConnect/Lean/blob/master/readme.md) và [LICENSE](https://github.com/QuantConnect/Lean/blob/master/LICENSE) | Engine candidate, C#/Python, Apache-2.0; đọc raw chính chủ |
| S18 | [Apache Arrow — Parquet](https://arrow.apache.org/docs/python/parquet.html) | Column selection, datasets, metadata; memory map không mặc định giải quyết RAM |
| S19 | [PostgreSQL — Transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html) | Concurrency anomalies/serializable retries; retry DB không phải retry broker |
| S20 | [Temporal — Activity definition](https://docs.temporal.io/activity-definition) | Activity retry vẫn cần idempotency |
| S21 | [MQL5 Python — initialize](https://www.mql5.com/en/docs/python_metatrader5/mt5initialize_py) | Terminal/account binding; defaults có thể chọn last account; không gọi trong research |
| S22 | [OpenAPI specification](https://spec.openapis.org/oas/latest.html) | Language-agnostic API description, contract/codegen foundation |
| S23 | [Pact — Can I Deploy](https://docs.pact.io/pact_broker/can_i_deploy) | Consumer/provider version compatibility; không bắt cài Pact |
| S24 | [NautilusTrader README](https://github.com/nautechsystems/nautilus_trader/blob/develop/README.md) và [LICENSE](https://github.com/nautechsystems/nautilus_trader/blob/develop/LICENSE) | Python/Rust candidate và LGPLv3; chưa xác nhận adapter/account của user |
| S25 | [PostgreSQL — Numeric types](https://www.postgresql.org/docs/current/datatype-numeric.html) | Exact decimal/integer khác floating representation |
| S26 | [Apache Iceberg — Evolution](https://iceberg.apache.org/docs/latest/evolution/) | Schema/partition evolution; lý do cân nhắc về sau |
| S27 | [FastAPI — Concurrency/parallelism](https://fastapi.tiangolo.com/async/) | IO concurrency khác CPU parallelism; không bằng chứng thắng Flask tại repo |
| S28 | [Patterns of Legacy Displacement](https://martinfowler.com/articles/patterns-legacy-displacement/) | Outcome-led replacement và pitfalls của thay hệ thống; đọc bổ sung cho greenfield review |
| S29 | [Microsoft — Strangler Fig](https://learn.microsoft.com/en-us/azure/architecture/patterns/strangler-fig) | Coexistence/transition overhead; có thể không phù hợp khi hệ nhỏ/thay toàn bộ đơn giản |

**Nguồn không dùng làm bằng chứng:** trang DuckDB concurrency trả trang ngắn/403, raw path thử 404; URL QuantConnect docs ban đầu chuyển 404 nên dùng upstream README/LICENSE; MT5 install URL thử 404, thay bằng docs initialize cho claim hẹp; OpenAI `/index.md` thử 404 nhưng trang HTML chính thức đã đọc được. Search Google chỉ trả redirect shell. Không suy diễn nội dung các trang lỗi.

**Phân biệt:** facts source/local inspection ở mục 2/14; architecture/stack ở mục 4–6 là đề xuất; throughput/safety/failover/tenant readiness cần test trong plan tiếp theo. Báo cáo không đổi trạng thái nghiệm thu sản phẩm hoặc broker.
