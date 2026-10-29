# P2 Checkpoint — 17/09/2026

Trạng thái: **COMPLETE theo P2-CONTRACT sau review remediation; P3 cũng đã COMPLETE, demo/live chưa mở**.

## Đã làm

- Thêm `ResearchStore` với DB riêng `data/research.sqlite3`.
- Lưu immutable research chain: hypothesis -> strategy version -> protocol -> run.
- Run có planned budget, deterministic `repro_key` và state machine `planned/running/completed/failed/cancelled`.
- Research schema v2 thêm `dataset_sha256`; `repro_key` bỏ local database IDs khỏi hash và gắn content fingerprint dataset.
- Fixture runner chuẩn hóa đúng đơn vị: bar Unix seconds, protocol cutoff milliseconds; future bar không đi vào checksum.
- Thêm P2 Flask shell `/research` + research API; Evidence P1 vẫn ở `/`.
- Không thêm MT5/broker/order capability.

## Bằng chứng

- P2 focused suite: **13/13 pass**.
- P2/P3 focused review suite: **21/21 pass**.
- Full repo regression: **42/42 pass**.
- `scripts/p2_verify.py`: PASS; production-style seconds/ms timestamps, same repro key/checksum, future bar excluded, future completion blocked, completed/cancelled explicit, budget preserved, MT5 modules absent.
- Regression riêng xác minh cùng semantic spec ở DB IDs khác cho cùng `repro_key`, còn đổi `dataset_sha256` làm key đổi.
- Migration regression xác minh v1 -> v2 tạo backup trước khi thêm fingerprint.
- Python compile: pass.
- `node --check static/js/research.js`: pass.

## Ghi chú migration local

Trong lượt sửa review, import-driven test đã mở DB mặc định và nâng `data/research.sqlite3` từ v1 lên v2 trước khi backup hook mới được thêm. Kiểm tra ngay sau đó cho thấy DB có **0 protocol và 0 run**, nên không có research artifact bị mất hoặc biến đổi. Từ code hiện tại, mọi migration v1 -> v2 còn lại sẽ tạo `*.v1.bak` trước khi `ALTER TABLE`.

## Chưa coi là bằng chứng

- Không dùng Browser/Computer Use theo plan hiện tại, nên chưa claim visual polish/responsive runtime.
- Fixture QA chỉ nghiệm thu contract phần mềm, không phải bằng chứng edge hay hiệu quả strategy.
- Demo/live vẫn chưa được cấp quyền.
