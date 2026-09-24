# P3 Contract — Chart/Replay + Journal

Ngày: **17/09/2026**

Trạng thái: **implementation + review remediation + focused/real-data verification complete; không cấp quyền demo/live**.

## 1. Mục tiêu

P3 nối một trade đã có trong Evidence Explorer tới đúng market-data window để review/replay và lưu journal có provenance:

`evidence run -> trade -> chart cursor -> intended decision -> immutable fill snapshot -> journal revisions`.

P3 phục vụ review/thực hành replay. Nó không gửi lệnh broker và không biến kết quả QA thành bằng chứng edge.

## 2. Data ownership

- Evidence DB `data/sessions.sqlite3` tiếp tục read-only.
- Research DB `data/research.sqlite3` giữ ownership P2, P3 không dual-write vào đó.
- Market history được đọc trực tiếp từ `data/chunks/<symbol>/<timeframe>` bằng reader read-only; không gọi `HistoryStore.ensure_chunked()` vì path đó có thể migrate/rewrite cache.
- Journal dùng DB riêng `data/journal.sqlite3`.

## 3. Trade -> chart mapping

- Symbol/timeframe lấy từ evidence run, không nhận tùy ý từ client.
- Trade lấy theo `run_id + trade_id` từ canonical EvidenceStore.
- Evidence timestamp được coi là **bar label/open timestamp**, không phải bằng chứng rằng OHLC của bar đó đã biết tại đầu bar.
- Bar anchor là bar gần nhất tại hoặc trước evidence timestamp; lệch quá một timeframe là mapping error.
- P3 dùng **bar-closed cursor semantics**: bar chỉ được trả khi `bar.time + timeframe_seconds <= cursor`. Cursor mặc định là thời điểm close/availability của bar chứa entry.
- Client không preload OHLC của bar chưa đóng. Đây là ranh giới chặt hơn legacy replay native-timeframe hiện có.
- Outcome (`close price`, `close time`, `net P/L`) chỉ được trả khi cursor đã đạt thời điểm close/availability của bar chứa exit. Journal gắn trong practice context cũng phải mask `fill.exit` và `fill.close_time_ms` trước mốc đó.

## 4. Intended và fill

- `intended_entry`, `intended_stop`, `intended_target`, rule checks, grade và notes là dữ liệu review do người dùng nhập.
- `fill_entry`, `fill_exit`, side, quantity và fill timestamps lấy từ evidence trade ở backend khi tạo journal; client không được quyền ghi đè.
- `decision_time_ms` lấy từ replay cursor đang hiển thị lúc tạo journal, không cố định ở entry cursor. Cursor phải khớp một closed-bar boundary và không được trước entry hoặc sau recorded close boundary.
- Journal luôn gắn `source_kind=replay`, `evidence_run_id`, `trade_id`, symbol/timeframe và `data_source_id` của history snapshot.

## 5. Journal history

- Một trade có tối đa một journal entry trong P3.
- Chỉnh review tạo revision mới; fill/provenance bất biến.
- Có API đọc revision history để audit thay đổi.
- Không có delete route trong P3.

## 6. Execution boundary

- P3 kế thừa P1/P2 local shell nhưng không import `mt5_data` hoặc legacy `app.py`.
- Không có `/api/trade/place`, `/api/trade/close`, broker account route hoặc demo/live permission trên P3 app.
- Port MT5 `9000` không được mở bởi P3.

## 7. Acceptance P3

1. Từ run/trade evidence mở đúng symbol, timeframe và cursor theo trade timestamp.
2. Market-history read path không sửa cache và không gọi migration/rechunk.
3. Practice context chỉ trả bar đã đóng theo cursor; trade outcome và journal fill outcome đều bị che trước khi exit bar đóng, kể cả response create/update journal.
4. Step replay tiến/lùi theo bar timestamp và vẫn không preload giá tương lai.
5. Journal tách intended khỏi fill; fill/provenance do backend snapshot từ evidence/history; `decision_time_ms` phản ánh replay cursor thực tế lúc lưu.
6. Update journal tạo revision mới, không ghi đè lịch sử.
7. Evidence DB không đổi khi dùng chart/journal; P3 không load MT5/execution.
8. Focused tests, syntax checks và verifier P3 pass trên fixture cô lập.

## 8. Rollback

- P3 code nằm ở module/file mới và có thể revert độc lập khỏi P1/P2.
- `journal.sqlite3` tách riêng; không xóa file nếu đã có journal thật.
- History reader chỉ đọc nên rollback P3 không cần migration market cache.

## 9. Giới hạn

- P3 dùng candlestick canvas local tối thiểu để kiểm tra workflow; chưa khóa chart engine dài hạn.
- Không dùng Computer Use/Browser Use theo constraint hiện hành; visual runtime polish chưa được coi là đã nghiệm thu bằng screenshot.
- Demo/live vẫn thuộc P4/P5 và cần gate riêng.
