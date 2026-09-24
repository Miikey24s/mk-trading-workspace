# P2 Contract — Research Workspace

Ngày: **17/09/2026**

Trạng thái: **implementation + review remediation + focused verification complete; không cấp quyền demo/live**.

## 1. Mục tiêu

P2 lưu được chuỗi nghiên cứu có thể truy ngược và tái hiện:

`hypothesis -> strategy version -> protocol -> research run`.

Mỗi run phải có budget trước khi start, trạng thái terminal rõ, reproducibility key ổn định và cutoff dữ liệu được kiểm soát. P2 không chứng minh strategy có edge.

## 2. Ownership và storage

- Evidence/replay artifact P1 tiếp tục nằm ở `data/sessions.sqlite3` và đường P1 vẫn read-only.
- Research state dùng DB riêng `data/research.sqlite3`; P2 không ghi vào `sessions.sqlite3`.
- `hypothesis`, `strategy version` và `protocol` không có update/delete route trong P2. Muốn thay luật tạo strategy version mới; muốn thay test setup tạo protocol mới.
- `research run` chỉ đổi qua state machine được định nghĩa ở mục 4.

## 3. Contract dữ liệu

### Hypothesis

- `title`
- `thesis`

### Strategy version

- `hypothesis_id`
- `strategy_key`
- `version`
- `rules` JSON
- cặp `strategy_key + version` là duy nhất.

### Protocol

- `strategy_version_id`
- `name`
- `dataset_id`
- `dataset_sha256`: SHA-256 của đúng nội dung dataset dùng cho protocol.
- `data_start_ms`
- `cutoff_ms`
- `seed`
- `parameters` JSON

`cutoff_ms` phải lớn hơn `data_start_ms`.

### Research run

- `protocol_id`
- `budget.max_bars`
- `budget.max_runtime_ms`
- optional `budget.note`
- `repro_key`: SHA-256 của semantic snapshot hypothesis + strategy version + protocol + budget. Local database IDs không tham gia hash; `dataset_sha256` có tham gia.

Budget được lưu lúc tạo run và không có route sửa budget sau đó.

## 4. Lifecycle

State hợp lệ:

- `planned -> running`
- `planned -> failed | cancelled`
- `running -> completed | failed | cancelled`

`completed`, `failed`, `cancelled` là terminal. Chuyển state sai trả conflict thay vì âm thầm ghi đè.

## 5. Future-leak boundary

- Market-history bar dùng Unix **seconds**, còn contract protocol dùng `cutoff_ms`; fixture runner đổi cutoff milliseconds sang seconds trước khi lọc.
- Chỉ bar `time <= cutoff_ms / 1000` được đưa vào checksum/result; `observed_until_ms` luôn trả milliseconds.
- Thay nội dung bar sau cutoff không được làm đổi fixture checksum.
- Khi complete run, `observed_until_ms > cutoff_ms` bị từ chối.

Ranh giới này chứng minh contract fixture/storage của P2. Nó **không** tự chứng minh một strategy engine ngoài P2 không nhìn dữ liệu tương lai; engine thực tế về sau vẫn phải đi qua data adapter/cutoff contract tương ứng.

## 6. Execution boundary

- P2 app kế thừa Evidence Explorer P1 nhưng chỉ thêm route research local.
- Không import `mt5_data` hoặc legacy `app.py` trên đường P2.
- Không có broker route, order route, demo/live permission hoặc auto execution.
- Không dùng Computer Use/Browser Use cho acceptance P2 hiện tại; UI được kiểm tra bằng HTML/API contract + JavaScript syntax, còn visual runtime polish chưa được coi là bằng chứng.

## 7. Acceptance P2

1. Lưu và đọc được hypothesis, strategy version, protocol, run.
2. Strategy version duy nhất theo `strategy_key + version`; không có mutation route cho spec đã lưu.
3. Budget bắt buộc được ghi trước khi run start.
4. Cùng semantic spec + budget cho cùng `repro_key` kể cả khi recreate/import làm database IDs khác; đổi `dataset_sha256` phải đổi `repro_key`. Cùng fixture/cutoff/seed cho cùng fixture checksum.
5. Bar sau cutoff không ảnh hưởng fixture checksum; completion vượt cutoff bị chặn.
6. `failed` và `cancelled` là trạng thái explicit, terminal.
7. Research write không làm đổi Evidence DB và đường P2 không load MT5/execution.
8. Focused tests, syntax checks và `scripts/p2_verify.py` pass trên fixture cô lập.

## 8. Rollback

- Code P2 nằm ở module/file mới và có thể revert độc lập khỏi P1.
- Research DB tách riêng nên rollback code không cần migration/rewrite `sessions.sqlite3`.
- Không xóa `research.sqlite3` nếu đã có research artifact thật. Migration v1 -> v2 tự tạo SQLite backup `research.sqlite3.v1.bak` trước khi thêm dataset fingerprint.
- Protocol legacy v1 không có `dataset_sha256` vẫn đọc được, nhưng không được tạo run mới; phải tạo protocol mới có fingerprint.

## 9. Giới hạn còn lại

- P2 hiện quản lý research contract/lifecycle và deterministic fixture envelope, chưa phải backtest engine chiến lược hoàn chỉnh.
- `dataset_sha256` là content identity do data adapter/caller cung cấp; P2 kiểm format và đưa nó vào reproducibility contract, nhưng chưa tự resolve mọi `dataset_id` để tính hash độc lập.
- Chưa visual-smoke bằng browser theo ranh giới plan hiện tại.
- P3 đã nối statistical trade -> chart/replay/journal và tiếp tục giữ cutoff/data provenance xuyên luồng.
