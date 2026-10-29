# Sổ bảo toàn knowledge — không bắt buộc giữ implementation

Ngày **20/09/2026** · v1.0 · **Danh mục ban đầu từ tài liệu; chưa trích xuất/port test hoặc sao chép dữ liệu.**

Phụ lục của [F0–F7](FOUNDATION-RESEARCH-PLAN.md). Dùng cho cả PATH-1/2/3. Mục tiêu: implementation có thể bỏ, nhưng yêu cầu/hành vi đúng/bài học có evidence phải được đánh giá và chuyển tiếp có chủ đích.

## 1. Cách đọc và phân loại

Mỗi K-ID có: yêu cầu/bài học → nguồn/phiên bản/phạm vi evidence → invariant hay observed behavior → fixture/oracle độc lập cần tạo → vị trí/owner bên đích → retain/rederive/retire/defer có lý do → verification. Bảng này mới là seed inventory, không phải kiểm kê hết project.

- **Invariant:** hành vi an toàn/nghiệp vụ cần giữ, không giữ nguyên code hoặc wire format.
- **Observation:** hành vi đã thấy ở một broker/build/account/config; cần xác minh khi context đổi.
- **Product knowledge:** workflow, nhu cầu và UX lessons; cần user acceptance tương ứng.
- **Asset candidate:** test/fixture/data/source có thể tái sử dụng sau kiểm license/provenance/semantics.

Evidence checkpoint là bằng chứng lịch sử đúng phạm vi; không phải test vừa chạy lại và không suy ra broker/live/account hiện tại vẫn như cũ.

## 2. Danh mục khởi đầu

| K-ID | Knowledge phải xem xét giữ | Loại / nguồn hiện có | Cách chuyển kiểm chứng độc lập implementation |
|---|---|---|---|
| K01 | Ba hành trình research → result; chart/replay → journal; account → preview/confirm → reconcile | Product · [plan sản phẩm](PRODUCT-COMPLETION-PLAN.md) mục 3 | Scenario/acceptance flow không phụ thuộc route hoặc framework cũ |
| K02 | Tiếng Việt chính; chart time/price/zone rõ; unknown/stale/planned không giả thành executed | Product · [design baseline](DESIGN-SYSTEM.md), [U1 checkpoint](U1-DESIGN-CHECKPOINT-2026-09-19.md) | Lưu UX feedback/negative cases; style preview chưa user-approved không biến thành bắt buộc |
| K03 | Startup/import/test không tự nối broker; replay/read-only/AI không có đường trade bypass | Invariant · [R0](R0-CHECKPOINT-2026-09-19.md), [P1 contract](P1-CONTRACT.md) | Port negative capability tests; so side-effect count, không assertion theo tên file cũ |
| K04 | Durable intent bind account/server/mode/payload; duplicate không resend, khác payload phải conflict | Invariant · [P4 contract](P4-CONTRACT.md), [P4 checkpoint](P4-CHECKPOINT-2026-09-17.md) | Fixture request/response/dispatch ledger, independent expected outcomes |
| K05 | Timeout-after-accept phải unknown rồi reconcile; response trễ không bị request sau nhận nhầm | Invariant + transport observation · P4 checkpoint | Fault schedule tái tạo correlation lỗi; transport mới có thể giải quyết khác socket-reset cũ |
| K06 | Late unknown không ghi đè evidence chắc chắn; partial fill/cancel cần đầy đủ filled/remaining | Invariant · P4 checkpoint | Concurrent completion/reorder/correction oracle; không đóng băng state machine đơn giản cũ cho mọi broker |
| K07 | Freshness dựa tick timestamp/source clock; account đổi phải bị phát hiện | Invariant + broker observation · P4 checkpoint, [plan lịch sử](PLAN.md) v0.20 | Clock skew/DST/delayed quote/account-switch fixtures; không hard-code offset broker từng thấy |
| K08 | EURUSD path từng FOK; partial broker-real không được giả là đã test; retcodes phải theo semantics | Observation · P4 checkpoint | Ghi broker/build/date/fill policy, fake partial fixture; retest adapter đích trong quyền riêng |
| K09 | Guarded demo acceptance khác live acceptance; balance 0 không là sandbox | Invariant/observation · [P5 contract](P5-CONTRACT.md), [L checkpoint](L-CHECKPOINT-2026-09-19.md) | Software checks giữ fail-closed; không copy credentials hoặc tự lặp broker trade |
| K10 | Replay cursor, bar-close và multi-timeframe không dùng tương lai; holdout không lộ qua UI/AI | Invariant · [P3 contract](P3-CONTRACT.md), [Data/Metrics](DATA-AND-METRICS.md) | Future-suffix metamorphic tests và point-in-time fixtures độc lập renderer |
| K11 | P&L/R/DD/cost basis, N/A, mẫu số và units phải nhất quán | Invariant · [Data/Metrics](DATA-AND-METRICS.md), [R2](R2-CHECKPOINT-2026-09-19.md) | Hand-calculated/golden ledger, oracle không import metric function bên candidate |
| K12 | Provenance từ server/data, không tin metadata client; 20 trades/5 days là software gate, không proof edge | Invariant + empirical limitation · [R3b](R3B-CHECKPOINT-2026-09-19.md) | Tampered manifest/missing data/insufficient sample cases; method assumption review |
| K13 | Dataset raw/normalized/QA/used/holdout, instrument/calendar/cost/news versions không dùng lẫn | Invariant/asset · [U2](U2-DATA-FOUNDATION-CHECKPOINT-2026-09-19.md) | Inventory locator/hash/license/schema trên scope được phép; chưa copy hoặc đọc holdout |
| K14 | Rule revisions/fill immutability/journal annotation ownership; Learn giữ core nhỏ | Product/invariant · [U3](U3-PLAYBOOK-BACKEND-CHECKPOINT-2026-09-19.md) | Portable revision/fill linkage scenarios; không copy tutor answer key vào client |
| K15 | Chart anchors/layout versions, deterministic run, kill-switch semantics, backup lineage | Asset/invariant · [U4–U9](U4-U9-LOCAL-SOFTWARE-CHECKPOINT-2026-09-19.md) | Tách cái đã software-test khỏi UI/provider/runtime pending; thử lại bên đích |
| K16 | AI typed output vẫn có thể sai; missing/uncertain không thành false/0; AI không own risk/execute | Research evidence · [TypeSafe report](../typesafe-research-2026-09-19/REPORT.md) | Giữ failed cases/eval semantics; TypeSafe/provider không bắt buộc nếu nền mới chọn khác |
| K17 | License chart/data không suy từ license repo; build/source/version phải truy được | Invariant/asset · [Core acceptance](CORE-ACCEPTANCE-2026-09-19.md), [cleanup](REPO-CLEANUP-PLAN.md) | Asset entitlement manifest; không vendor/upload bundle thiếu quyền |

## 3. Không port lỗi thành “tương thích”

Test cũ có thể assert theo implementation, thiếu case quan trọng hoặc có expected sai. Mỗi test chọn `portable nguyên trạng`, `viết lại harness giữ invariant`, `đổi expectation sau review semantics`, hoặc `retire có lý do`. Không giữ API/DB/wire protocol cũ chỉ để số tests pass không giảm.

Khi old/new khác kết quả, không mặc định old đúng: so với domain rule, dữ liệu gốc được phép và oracle độc lập; giữ discrepancy record cùng quyết định. Nếu sửa semantic bug, ghi version break và cách trình bày kết quả cũ/mới, không âm thầm ghi đè lịch sử.

Dữ liệu/fixture phải có checksum, origin, license, QA limitations, expected observations và safety classification. Không đổi historical zeros/unknown thành số đo thật. Broker capture cần redact account/secret theo quyền; reference file không cho phép upload.

## 4. Gate trước bỏ implementation hoặc đưa hệ mới vào dùng

1. F0 hoàn thiện K inventory cho Y01–Y24 và ghi unresolved gaps; không bắt copy mọi file.
2. F1 tạo acceptance corpus trung lập cho các invariant quan trọng; lưu version/hash để cả ba PATH dùng cùng chuẩn.
3. F2/F3 kiểm corpus trên candidates; failed/unsupported không ẩn; mapping từng K sang verification.
4. F5 chọn một PATH, ghi asset/code disposition riêng. Knowledge retained không có nghĩa runtime code retained.
5. F6/F7 xác minh mọi K quan trọng có nơi nhận hoặc quyết định scope rõ; user data/IDs/provenance được bảo toàn theo migration/export plan. Chưa kiểm chứng thì không retire hệ cũ hoặc tuyên bố parity.

**Không xóa/di chuyển repo, module, tests, datasets hoặc artifact trong lượt lập sổ này.** Archive/decommission có approval/retention riêng, dù PATH-3 cuối cùng được chọn.
