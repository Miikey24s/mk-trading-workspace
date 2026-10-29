# P4 Contract - pre-broker execution gate

Ngày: **17/09/2026**

P4 được chia thành hai gate. **P4A** là execution contract + Trade Desk chạy hoàn toàn bằng local demo simulator. **P4B** mới được phép nối tài khoản MT5 demo thật sau khi người dùng duyệt account/mode/phạm vi thử cụ thể. Live vẫn ngoài phạm vi P4.

## 1. Boundary hiện tại

- `p4_app.py` kế thừa P1-P3 nhưng không import `app.py` hoặc `mt5_data.py`.
- Adapter mặc định là `DemoBrokerSimulator`; không mở TCP 9000, không gọi MT5 và không có live adapter.
- Execution API chỉ cho `mode=demo`, `account_id` phải khớp backend và mọi request ghi lệnh phải có `request_id` bền vững.
- `live`, `local` và `replay` bị từ chối trước khi adapter được đọc/gọi.
- Trade Desk chỉ là simulator; không được mô tả kết quả simulator là broker fill hoặc bằng chứng strategy edge.

## 2. Request lifecycle

Luồng P4A:

`draft -> risk preview -> explicit confirmation -> durable unknown record -> adapter -> accepted/rejected/unknown -> reconcile`

SQLite `execution.sqlite3` giữ request intent và kết quả. `request_id` được bind với mode + account + **server** + operation + fingerprint payload. Fingerprint chỉ dùng intent ổn định của người dùng, không chứa quote/entry preview biến động. Cùng ID/cùng intent trả lại kết quả đã biết **trước khi đọc broker lại**; cùng ID/intent khác bị conflict. Nếu app rơi sau khi ghi `unknown` nhưng trước khi biết kết quả adapter, restart không được gửi lại mù; phải reconcile. Reconcile chỉ lookup broker khi durable status còn `unknown`; kết quả đã biết không được hạ ngược thành `unknown` do broker lookup tạm not-found.

Schema execution hiện là v2. Migration v1 -> v2 backup SQLite trước khi thêm `account_server`. Record v1 không có server được giữ với server rỗng và không đủ điều kiện để thực thi/reconcile như request đã xác minh server.

## 3. Risk preview

Risk preview dùng snapshot account/quote do adapter cung cấp và từ chối dữ liệu stale. Với simulator hiện tại:

- volume phải nằm trong min/max và đúng `volume_step`;
- stop loss bắt buộc nằm đúng phía entry;
- estimated stop risk = khoảng cách stop theo tick x `tick_value_per_lot` x volume;
- limit mặc định là min(`1% balance`, `100 USD`);
- tối đa 3 position mở trong simulator.

Các giá trị này là fixture P4A, chưa phải broker/account policy thật. P4B phải lấy contract/quote/account limits từ adapter demo thật và recheck ngay trước send. Trên MT5 path, freshness của quote dùng timestamp tick thật từ gateway, không dùng thời điểm app nhận response làm đại diện.

## 3A. P4B preflight contract

Trước khi nối broker thật, simulator hiện kiểm được các semantics mà adapter demo phải giữ:

- backend bind `account_id + server + mode=demo`; server/account sai bị deny trước side effect;
- adapter công bố capability (`place_market`, `close_position`, protective SL/TP, partial-fill reporting, request lookup) và capability thiếu thì route tương ứng bị khóa;
- connection state tách khỏi account state; disconnect làm preview unavailable nhưng state endpoint vẫn đọc được để phục hồi UI, kể cả khi transport rớt giữa lần check connection và account/positions read;
- startup MT5 được phép ở degraded/disconnected state khi EA chưa nối hoặc rớt trong bind window; app không crash, và adapter chỉ bind identity khi một demo account hợp lệ thật sự quay lại;
- reject và partial fill là kết quả explicit, partial giữ `filled_volume`, `remaining_volume`, position và deal/fee mapping;
- timeout sau khi broker đã accept để local request ở `unknown`; reconcile lấy broker result và duplicate sau đó không resend;
- socket timeout phải invalidate connection trước request kế tiếp để response trễ không thể làm lệch command/response sequencing;
- quote thay đổi sau request đầu không làm đổi identity của request cũ.

## 4. Local request protection

- Execution API chỉ nhận loopback client/host.
- State-changing request kiểm `Origin` nếu browser gửi origin.
- Place/close/reconcile yêu cầu header xác nhận `X-Execution-Intent: confirmed`.
- Không đặt credential hoặc secret trong frontend; P4A không có broker credential.

## 5. Chart/license boundary

Trade Desk P4A không load TradingView Advanced Charts. Bộ `static/charting_library/` tiếp tục là local proprietary dependency bị Git ignore. Bản `charting_library/` ở repo root được xác minh byte-for-byte giống bản `static/` và không được runtime tham chiếu; nó cũng được ignore để tránh commit nhầm. Quyền sử dụng/provenance của Advanced Charts vẫn chưa được suy ra từ MIT license của repo.

## 6. Acceptance P4A + P4B preflight

1. Local/replay/live và account mismatch bị deny trước adapter.
2. Place yêu cầu confirmation + request ID; risk vượt limit bị block.
3. Duplicate cùng intent không resend; reuse ID cho intent khác bị conflict.
4. Durable `unknown` sống qua restart; reconcile cập nhật kết quả mà không blind retry.
5. Trade Desk/state/preview/place chạy end-to-end trên simulator.
6. Import P4 không load legacy app/MT5; port 9000 không được mở bởi P4 path.
7. P1-P3 regression tương thích tiếp tục pass trên test set không import legacy MT5 shell.
8. Account server và demo mode được bind; execution journal v2 giữ server qua restart.
9. Partial/reject/timeout/disconnect/capability fixtures có trạng thái rõ và timeout reconcile không resend.
10. Duplicate cùng intent không phụ thuộc quote mới hoặc broker read mới.
11. Transport timeout không giữ socket cũ; known reconcile result không downgrade; stale broker tick bị risk gate từ chối; disconnected startup và mid-snapshot disconnect vẫn cho state endpoint phục hồi khi EA quay lại.

## 7. P4B closure

Người dùng đã duyệt dùng account MT5 **demo** hiện tại, đúng server, với minimum broker volume cho place/close/reconnect/reconcile; live không được phép. Real demo happy-path đã đạt: min-volume place/close, broker-side request lookup/reconcile, position về 0 và deal mapping đều được xác minh; live vẫn khóa.

Process restart/fallback ở software boundary đã được harden: timeout socket reset, degraded startup/rebind, monotonic durable result và broker freshness đều có regression test. Broker-real reject đã được tái hiện an toàn bằng volume lệch step `0.011`; broker trả `retcode 10014` và không mở position. Broker-real timeout-after-accept cũng đã đạt: min-volume EURUSD request rơi vào durable `unknown`, socket timed-out bị bỏ, EA reconnect, request lookup tìm đúng broker position và cleanup close đưa positions về 0 mà không resend request gốc.

Freshness dùng tuổi tick tính trên cùng broker clock (`server_time` với `time/time_msc`) rồi mới quy đổi về local snapshot age; không so epoch local trực tiếp với broker server time. Runtime FTMO hiện trả broker clock lệch local/UTC khoảng +3 giờ, nên đây là correctness requirement chứ không chỉ tolerance.

Current EURUSD contract trả `filling_mode=3`, và cả place path (`CTrade::SetTypeFillingBySymbol`) lẫn close path ưu tiên FOK khi FOK khả dụng. Vì vậy broker-real partial fill không phải trạng thái chủ động tái hiện được trên current P4 execution path; P4 không đổi policy sang IOC chỉ để tạo test. Với future IOC symbols, request lookup ưu tiên matching history order, cộng volume các deal thuộc order để suy ra `partial`/`closed`, rồi trả `filled_volume`/`remaining_volume`; `MT5SocketDemoAdapter` giữ nguyên hai field này khi reconcile. Regression bao phủ cả direct partial response và unknown-request → partial reconcile.

**P4 COMPLETE.** Demo pass không được dùng để suy ra live readiness; live tiếp tục khóa và thuộc gate P5 riêng.
