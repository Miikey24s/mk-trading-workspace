# P4 checkpoint - 17/09/2026

Trạng thái: **P4 COMPLETE. P4A + P4B broker demo happy-path, reconciliation, broker-real reject, timeout-after-accept và restart/fallback đều đã đạt trên account MT5 demo hiện tại. Current EURUSD dùng FOK nên broker-real partial fill là N/A trên path này; partial mapping vẫn được regression-test ở MT5 adapter. Live vẫn khóa.**

## Đã triển khai

- Product repo có `execution_store.py`, `execution_service.py`, `demo_broker.py` và `p4_app.py`.
- Trade Desk `/trade-desk` dùng local demo simulator, hiển thị account/risk/positions/execution journal; không load Advanced Charts và không có live adapter.
- Request journal ghi intent trước side effect, bind request ID với intent, chống duplicate, giữ `unknown` qua restart và hỗ trợ reconcile.
- Risk preview kiểm freshness, lot step, stop direction, estimated stop risk và giới hạn position.
- Execution API local-only, kiểm origin cho request ghi và yêu cầu explicit confirmation header.
- Execution journal schema v2 bind thêm `account_server`; migration v1 backup trước khi alter. DB local đã migrate khi có 0 request.
- Adapter contract hiện có identity/server/mode, connection state và capability map; duplicate trả từ journal trước broker read.
- Failure fixtures bao phủ reject/partial fill, disconnect và timeout sau broker-accept rồi reconcile không resend.
- Có `MT5SocketDemoAdapter` bind cứng demo account + server, map account/quote/contract/positions, broker request lookup và reconnect.
- Request ID durable được hash thành broker-safe comment token ngắn trước khi đi qua socket; symbol/ticket/request token bị chặn delimiter/newline ở transport.
- EA protocol v2 trả execution identity/capability, symbol contract và request lookup; trade response chỉ accepted khi retcode thuộc nhóm success, có partial-fill fields.
- Adapter startup chờ EA reconnect theo timeout hữu hạn nhưng nếu EA chưa có hoặc rớt đúng lúc bind thì app vẫn lên ở degraded/disconnected state; khi EA quay lại adapter mới bind identity và vẫn từ chối non-demo/account-server switch.
- Socket transport bỏ hẳn client socket sau response timeout để response trễ không thể bị request kế tiếp đọc nhầm; request sau phải chờ connection mới.
- Reconcile chỉ đọc broker khi durable request còn `unknown`; kết quả đã biết như `accepted/rejected/partial/closed` không bị broker not-found tạm thời hạ ngược về `unknown`.
- Journal finalization là monotonic compare-and-set trên status `unknown`; late `unknown` từ completion chạy đồng thời không thể ghi đè durable result terminal đã biết.
- Quote freshness trên MT5 path dùng timestamp tick thật (`time_msc` hoặc `time * 1000`) thay vì thời điểm app vừa đọc response.
- State snapshot degrade an toàn nếu transport rớt sau `connected=true` nhưng trước account/positions read; UI vẫn nhận state disconnected thay vì 503.
- Broker request lookup ưu tiên matching history order, cộng volume từ các deal của order để reconstruct `partial`/`closed`; Python adapter giữ `filled_volume` và `remaining_volume` xuyên reconcile.

## Bằng chứng

- Focused P4/P4B + transport recovery: **33/33 pass**; full P1-P4: **73/73 pass**.
- Transport timeout test nạp `mt5_data.py` bằng isolated module load nên không mở listener nền.
- `scripts/p4_verify.py`: PASS; `live/local/replay` đều deny, duplicate không resend dù quote đổi, risk block đúng, restart/timeout unknown + reconcile pass, `mt5_data/app` không import.
- Flask test-client smoke: Trade Desk 200, state 200, preview pass, place accepted trên simulator, duplicate trả cùng kết quả và adapter chỉ được gọi 1 lần.
- Python compile, JS syntax và `git diff --check` pass. Sau hardening, Trade Desk đã restart bằng source mới và EA reconnect lại thành công.
- Read-only MT5 preflight thật: EA nối protocol v2; account xác minh `demo`, identity đầy đủ; `EURUSD` min volume `0.01`, volume step `0.01`, tick size `0.00001`; reconnect pass; lookup request không tồn tại trả not-found. Không gửi `TRADE_*` trong các smoke này.
- Sau khi Algo Trading được bật, `/api/execution/state` trả `connected=true`, `place_market=true`, `close_position=true`, `request_lookup=true`, trong khi `live_execution_enabled=false` giữ nguyên.
- Real demo acceptance đã chạy `EURUSD` ở broker minimum volume `0.01`: preview risk khoảng `$6.65` dưới cap `$100`, place accepted với retcode `10009`, close đưa positions về 0; balance/equity sau round-trip `$9,999.92`.
- Broker-side reconcile theo hai durable request ID tìm được deal thật cho cả place và close; close reconcile trả `closed`, volume `0.01`.
- Broker-real invalid-volume reject trả `retcode 10014` cho EURUSD `0.011` khi step là `0.01`, không mở position.
- Broker-real timeout-after-accept đã chạy min-volume EURUSD: service ghi durable `unknown`, transport đóng socket timed-out, EA reconnect, reconcile tìm thấy position thật, cleanup close pass và final positions = 0.
- FTMO broker clock lệch local/UTC khoảng +3 giờ. Gateway đã bổ sung `time_msc` + `server_time`; adapter tính tick age trên broker clock. MetaEditor compile source EA mới đạt `0 errors, 0 warnings`, runtime đã trả đúng các field mới.
- EURUSD runtime contract trả `filling_mode=3`, `execution_mode=2`; `CTrade::SetTypeFillingBySymbol()` và close path đều ưu tiên FOK trước IOC. Broker-real partial do đó là N/A cho current execution policy; adapter có regression riêng cho `status=partial`, retcode `10010`, `filled_volume` và `remaining_volume` để bảo toàn future IOC support.
- Broker-real reject đã được tái hiện bằng `EURUSD` volume `0.011` trong khi broker step là `0.01`; FTMO-Demo trả `status=rejected`, `retcode=10014` (invalid volume), và không có position mới sau request.
- Immediate close response từng trả `partial` dù position đã 0. Root cause là EA đọc `PositionSelectByTicket()` quá sớm sau `OrderSend()`; source `MacGateway.mq5` đã sửa status theo broker retcode (`DONE` => `closed`, `DONE_PARTIAL` => `partial`).
- Một attempt MetaEditor CLI ở lượt trước từng bị policy chặn; hardening hiện tại đã compile trực tiếp bằng FTMO MetaEditor đạt `0 errors, 0 warnings`, backup bản EA cũ rồi deploy source/binary mới vào terminal.
- `data/execution.sqlite3`: schema v2; journal hiện có durable request của broker demo acceptance thật, dùng để reconcile mà không resend. Backup v1 từ migration vẫn được giữ.
- Một lần full legacy suite trước hardening đạt **50/50**, nhưng `test_session_api` import `app.py` nên mở listener 9000 trong process test và lộ `ResourceWarning` socket cũ. Listener đóng khi process kết thúc. Không dùng ca này làm bằng chứng P4 execution isolation.

## Charting Library

Root `charting_library/` và `static/charting_library/` có **258 file, 258/258 SHA-256 trùng nhau**, package mô tả `CL v23.040`. Runtime/launcher chỉ tham chiếu `static/charting_library/`. `.gitignore` trước đây chỉ ignore bản `static/`, nên root copy xuất hiện `??` khi bắt đầu; đã thêm `/charting_library/` vào ignore và hiện cả hai bản đều ignored để tránh commit nhầm proprietary bundle. Không xóa file của người dùng và không khẳng định license/provenance hợp lệ.

## Gate kế tiếp

P4 đã đóng acceptance. Bước tiếp theo, nếu có, là P5 live-readiness với gate mới về account thật, hạn mức, thao tác và rollback; không tự suy ra live readiness từ demo pass và không tự bật live execution.

Product commits liên quan: `50ce5d5 feat: add mt5 demo execution adapter`, `5549ee8 fix: map mt5 close status from broker retcode`, `0af04df fix: harden mt5 execution recovery`, `9a8f6a6 fix: finalize mt5 demo execution robustness`, `28863ae fix: harden p4 recovery state`, `dfc60f1 fix: make p4 execution results monotonic`.
