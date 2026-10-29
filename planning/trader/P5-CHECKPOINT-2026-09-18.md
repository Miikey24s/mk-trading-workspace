# P5 checkpoint — 18/09/2026

Trạng thái: **P5A COMPLETE · P5B demo preflight PASS, place → close → reconcile còn chờ explicit execution · P5C0 live check-only IMPLEMENTED, runtime BLOCKED bởi quyền trading của account · P5C1 live execution chưa mở**

## Đã triển khai

- `live_readiness.py`: policy + probe chỉ đọc cho live account.
- `ExecutionJournal.list_unknown()`: truy durable request `unknown` theo mode/account/server.
- `p5_app.py`: `GET /api/live-readiness/state`, loopback-only, backend mặc định disabled.
- Exact account/server/mode mismatch fail-closed.
- Thiếu/sai risk limits, actions, symbols hoặc max positions fail-closed; boolean/fractional limit không được coercion thành giá trị hợp lệ.
- Symbol scope bắt buộc cho mọi live action, phải là token hợp lệ và được MT5 xác nhận read-only qua symbol contract.
- Positions payload thiếu/sai kiểu fail-closed thay vì bị hiểu là 0 vị thế.
- Durable live request `unknown` chặn readiness.
- P4 execution service vẫn demo-only; không có POST live mới.
- `p5b_demo_rehearsal.py`: harness exact-bound reuse P4 demo adapter/service, mặc định read-only và chỉ `--execute` mới chạy một cycle demo place → close → reconcile.
- P5B không hard-code account vào source; account ID/server phải truyền runtime và mismatch fail trước trade.
- `MacGateway.mq5` protocol v3 thêm `CHECK_ORDER` dùng `OrderCheck()` và trả `MqlTradeCheckResult`; không gọi `OrderSend` trong command này.
- `mt5_data.py` thêm `check_order()` riêng; `p5c_live_check.py` chỉ cho live/real preflight + broker check, snapshot positions trước/sau phải không đổi.
- `mt5_data.py` xử lý heartbeat ngoài luồng và nhiều frame newline trên socket, tránh coi heartbeat là response của request.
- Gateway v3 đã compile `0 errors, 0 warnings`, backup bản cũ và deploy vào terminal generic.

## Bằng chứng

- Focused P5A + P5B harness trước delta broker-lookup cuối: **20/20 pass**.
- Full regression trước delta broker-lookup cuối: **95/95 pass**.
- Delta broker-lookup cuối: local simulator smoke PASS cho place lookup `accepted`, close lookup `closed`, cleanup 0 position; `py_compile` PASS.
- Full regression rerun sau delta cuối đã chạy tới khi process kết thúc nhưng runtime safety chặn việc đọc output cuối, nên không tính lượt đó là PASS.
- P5C0 + MT5 transport focused: **7/7 pass**.
- Full regression hiện hành sau P5C0: **101/101 pass**.
- `MacGateway.mq5` protocol v3: **0 errors, 0 warnings**.
- `scripts/p4_verify.py`: PASS sau remediation; `live/local/replay` vẫn deny và `live_execution_enabled=false`.
- MT5 demo account `416382260` trên `Exness-MT5Trial14`: whitelist `127.0.0.1` đã được lưu qua UI; MQL5 journal ghi nhận `Successfully connected to Python server on port 9000`.
- P5B demo preflight read-only: identity đúng account/server/mode, protocol v3, capabilities place/close/request lookup đều có, `0 positions`; order preview pass với volume `0.01` và estimated stop risk `0.20 USD` dưới limit `10 USD`.
- App socket server đã được bật lại sau preflight; `/api/status` báo `connected=true`, positions hiện vẫn rỗng.
- Account real `429159350` trên `Exness-MT5Real18` đã được kiểm tra read-only: protocol v3, terminal connected, balance/equity/free margin `0.00 USD`, `0 positions`; account trả `trade_allowed=false` dù terminal và `EURUSDm` vẫn có quote/contract.
- `CHECK_ORDER` read-only cho `EURUSDm` volume `0.01` trả retcode `10019`, comment `No money`, margin `5.74 USD`; positions trước/sau vẫn `[]`, không gọi `OrderSend`.
- Preflight sau khi sửa socket dừng đúng tại blocker `MT5 account does not allow trading`, thay vì lỗi giả `execution context failed` do heartbeat.
- `git diff --check`: không có whitespace error; chỉ warning line-ending LF/CRLF trên các file P4 đã sửa trước đó.

Independent review read-only đã bắt các fail-open ở symbol scope, numeric coercion, missing positions và malformed mapping scope; các finding đều đã được sửa và có regression. Confirmation review cuối trên `P5-CONTRACT.md` + `live_readiness.py` trả **PASS** cho ba remediation còn mở: strict numeric limits, explicit positions payload và strict/broker-validated symbol scope. Reviewer không chạy test; controller đã xác minh riêng bằng focused/full suite ở trên.

## Chưa làm / gate kế tiếp

P5B broker-demo acceptance trên account Exness đã qua preflight nhưng chưa hoàn tất: cần một lượt được cho phép rõ ràng để chạy demo place → close → broker lookup → reconcile và xác nhận cleanup `0 positions`. Không được dùng kết quả demo để suy ra P5C.

Runtime re-check ngày 18/09 trước đó đã xác nhận account Exness real `authorized` + `terminal synchronized`, trạng thái ban đầu `0 positions, 0 orders`, nhưng broker log trả **`trading has been disabled - disabled on server`**; P5C0 vẫn dừng trước `OrderCheck`, chưa có live-readiness runtime pass.

Lần kiểm tra account `429159350` hiện tại xác nhận nguyên nhân cụ thể hơn: account/server không cho trading (`trade_allowed=false`) và broker-side check trả `10019 / No money`. Đây là blocker từ trạng thái account, không phải lỗi gateway hay lý do để mở live execution.

Đối với demo account, lỗi `4014 Function not allowed` đã được xử lý bằng whitelist `127.0.0.1` trong `Tools → Options → Expert Advisors`, sau đó còn một `MT5Gateway` trên chart và socket đã kết nối. Không chạy `--execute`, không gửi lệnh demo trong lượt này.

Gate kế tiếp là account/server phải được broker cho phép trading và có đủ margin; sau đó mới chạy lại P5C0 OrderCheck. P5C1 live execution vẫn cần exact account/server, risk/action/symbol scope, live trial scope, điều kiện broker/quỹ và rollback riêng; số dư 0 không tự biến một `OrderSend` live thành thao tác an toàn.
