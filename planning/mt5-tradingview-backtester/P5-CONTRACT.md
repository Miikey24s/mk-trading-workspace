# P5 contract — live readiness và dùng giới hạn

Ngày: **18/09/2026**

P5 chỉ được mở từ nền P4 đã COMPLETE. Demo pass không phải bằng chứng live-safe, strategy edge hay quyền dùng broker/quỹ.

## P5A — read-only live readiness

Mục tiêu của lát đầu là xác minh điều kiện trước live mà **không gửi, sửa, hủy hoặc đóng lệnh**:

- đọc identity account/server/mode và trạng thái terminal trực tiếp từ MT5;
- yêu cầu account/server được duyệt phải khớp chính xác backend;
- yêu cầu cấu hình rõ và đúng kiểu `max_risk_pct`, `max_risk_amount`, `max_positions`, action và symbol được phép; không coercion boolean/fractional thành limit hợp lệ;
- symbol scope là bắt buộc cho mọi live action, token malformed phải fail-closed và từng symbol phải được MT5 xác nhận bằng broker-read symbol contract;
- positions payload phải hiện diện đúng kiểu; state không rõ không được suy thành 0 vị thế;
- chặn khi còn durable request `live` ở trạng thái `unknown`;
- chặn mở exposure mới nếu position count đã chạm giới hạn;
- chỉ expose `GET /api/live-readiness/state` trên loopback;
- readiness luôn báo `execution_enabled=false`.

P5A không có live execution adapter, không có route POST live và không gọi thao tác broker ghi trạng thái. Backend readiness mặc định là `disabled`; chỉ khi cấu hình `P5_READINESS_BACKEND=mt5-readonly` mới đọc MT5 qua fetcher hiện có.

## P5B — demo live-like rehearsal

P5B dùng một account MT5 **demo** do người dùng duyệt để rehearsal luồng gần live mà không mở quyền live thật. Đây là lớp nghiệm thu execution/recovery bổ sung cho P4, không phải bằng chứng broker-live:

- reuse nguyên `MT5SocketDemoAdapter` + `ExecutionService` demo-only của P4; không tạo `live mode` giả và không đổi `live_execution_enabled=false`;
- bind exact account ID + server ở runtime, yêu cầu `trade_mode=demo`, terminal connected và capability place/close/request lookup đều có;
- bắt đầu khi account đang 0 position, chỉ dùng symbol được duyệt và minimum broker volume;
- risk preview phải pass trước send, journal giữ request ID bền vững và place/close đều được reconcile;
- acceptance tối thiểu là `preflight → minimum-volume place → close → reconcile → final positions = 0`;
- nếu identity/capability/connection/risk/cleanup không rõ thì fail-closed và không suy từ simulator thành broker pass.

`p5b_demo_rehearsal.py` là harness exact-bound cho lớp này. Mặc định chỉ preflight/read-only; chỉ `--execute` mới gửi một cycle demo place → close. Account ID không được hard-code vào source hay plan, phải truyền ở runtime.

Demo live-like có thể kiểm chứng protocol, idempotency, journal, reconnect/reconcile và broker response path. Nó **không** thay thế bằng chứng về liquidity/slippage/reject/partial fill/commission/swap hoặc điều kiện quỹ trên account live thật.

## P5C0 — live broker check-only

Trước khi có bất kỳ `OrderSend` nào trên account real, P5 có một lớp broker validation riêng dùng **MT5 `OrderCheck()`**:

- gateway protocol v3 thêm `CHECK_ORDER`; command này dựng `MqlTradeRequest` rồi gọi `OrderCheck`, không gọi `OrderSend`;
- Python chỉ expose `check_order()` và `p5c_live_check.py`; không tạo live execution adapter, route place/close hay đổi `ExecutionService` demo-only;
- preflight yêu cầu account đang kết nối là `real/live`, terminal/account cho phép MQL trading và protocol v3;
- có thể exact-bind account/server khi chạy; mismatch fail trước `OrderCheck`;
- dùng broker minimum volume + protective stop hợp lệ để lấy `retcode`, comment và margin projection;
- snapshot positions trước/sau phải giống hệt; nếu thay đổi thì fail-closed;
- kết quả `OrderCheck` pass không được diễn giải thành đảm bảo `OrderSend` sẽ được broker chấp nhận.

P5C0 được phép chạy trên account real vì không tạo order/position và giữ `live_execution_enabled=false`. Nó cung cấp broker-real evidence về identity, contract, margin/risk validation và request shape, nhưng không phải live execution acceptance.

## Gate trước P5C1 live execution

Trước khi có bất kỳ live side effect nào, cần đủ bằng chứng:

1. account ID + server + mode thật được người dùng duyệt rõ;
2. hạn mức tiền/%/số vị thế và symbol/action được duyệt;
3. điều kiện sử dụng broker/quỹ và quyền dùng cách kết nối hiện tại được xác minh ở thời điểm chạy;
4. không còn request `unknown`, state broker/positions được đối soát;
5. rollback/manual fallback bằng MT5 được ghi rõ và app không tự update khi đang có lệnh;
6. live trial scope được chốt riêng; P5B demo pass không tự cấp quyền cho minimum lot hay một lệnh live thử.

## P5C1 trở đi

Chỉ sau gate trên mới thiết kế adapter live exact-bound và acceptance broker thật. Mọi đường live phải reuse durable request journal, recheck quote/account/risk ngay trước send, broker reconciliation, local-only/origin guard và failure semantics của P4. Không nới `ExecutionService` P4 để đổi `demo` thành `live`.

## P5C1 preparation scope (account real pending)

Trong giai đoạn chưa có account real được broker authorize, P5C1 chỉ triển khai contract, validation và execution boundary; không mở `OrderSend`.

- `BrokerIdentityGate`: chuẩn hóa account/server/mode/capability contract, giữ trạng thái `pending_authorization` khi chưa có broker evidence.
- `RiskPolicyGate`: khóa limit risk, exposure, symbol, action, volume và protective order trước mọi execution request.
- `ExecutionIntent`: tách request intent khỏi broker action; mọi request phải có durable ID, journal entry và policy result.
- `ExecutionGate`: chuỗi kiểm tra bắt buộc trước broker call: identity -> risk -> state -> broker validation.
- `AuditJournal`: ghi lại request, validation result, broker response và recovery state.
- `Recovery/KillSwitch`: fail-closed khi mất kết nối, mismatch identity, stale state hoặc reconciliation không xác định.

P5C1 chỉ chuyển từ preparation sang live execution khi có đủ broker authorization, risk approval và live trial scope riêng. Account real sau này chỉ mở khóa adapter/broker evidence; không thay đổi contract của P5C1.

Definition of Done của P5 vẫn theo mục 7 `PRODUCT-RESEARCH-AND-INTEGRATIONS.md`: sai account/mode, request source, duplicate/retry, restart/recovery, reject/partial, stale risk, protective order failure, emergency stop, app-down fallback, analytics reconciliation và update/rollback đều phải có contract + bằng chứng phù hợp. P5A chỉ là gate đầu, chưa phải P5 COMPLETE.
