# P3 Checkpoint — 17/09/2026

Trạng thái: **COMPLETE**.

## Đã triển khai

- `ReadOnlyHistoryReader`: đọc trực tiếp chunk cache, không gọi migration/rechunk.
- `PracticeService`: map evidence run/trade sang chart cursor với **bar-closed semantics**.
- Practice API/UI: prev/next theo bar availability, không preload OHLC của bar chưa đóng; trade và journal fill outcome đều bị che tới khi exit bar đóng.
- `JournalStore`: DB riêng `journal.sqlite3`, intended review tách khỏi backend fill snapshot; update tạo revision mới.
- Journal create lưu `decision_time_ms` từ replay cursor hiện tại; create/update response không lộ exit trước close.
- Provenance history dùng content hash của `meta.json` + chunk contents.

## Bằng chứng

- P3 focused: **8/8 pass**.
- P2/P3 focused review suite: **21/21 pass**.
- P3 verifier: PASS — exact mapping, future OHLC hidden, trade + journal outcome masked, current decision cursor preserved, fill spoof blocked, revision history preserved, Evidence/history unchanged, MT5 not loaded.
- Regression P1 + P2 + P3: **42/42 pass**.
- Real DB/cache smoke: Run `1/100001` và `2/100002` đều HTTP 200, map đúng `EURUSD/H1`; default cursor là lúc entry bar đóng; outcome ban đầu hidden.
- Hash `data/sessions.sqlite3`, `data/chunks/EURUSD/H1/meta.json` và sampled chunk không đổi sau real smoke.
- `/api/trade/place` trên P3 trả 404; port 9000 không có listener.
- Full legacy regression vẫn có test cũ mở listener 9000 và EA local có thể chạm vào trong lúc test; sau suite đã xác minh **không còn listener**. Đây không phải đường P3/verifier.

## Quyết định timing quan trọng

Legacy replay dùng `bar.close` nhưng ghi position timestamp bằng `bar.time`. Vì OHLC bar thường mang timestamp đầu bar, P3 không dùng rule `bar.time <= cursor` cho native timeframe. P3 chỉ trả bar khi `bar.time + timeframe_seconds <= cursor`; với H1, nến 04:00 chỉ được xem là hoàn tất ở 05:00. Điều này tránh within-bar look-ahead ở đường P3.

## Giới hạn còn lại

- Candlestick canvas P3 là shell workflow tối thiểu; chart engine dài hạn chưa khóa.
- Không chạy Browser/Computer Use theo constraint hiện hành, nên chưa claim visual polish/runtime screenshot acceptance.
- QA artifacts không chứng minh strategy edge.
- P4 Trade Desk demo chưa khởi chạy; không có quyền demo/live nào được mở từ P3.
