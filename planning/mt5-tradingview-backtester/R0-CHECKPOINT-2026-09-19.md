# R0 checkpoint — khóa bypass + cách ly test

Ngày: **19/09/2026** · Baseline project: branch `Nam`, commit `1de617df1fb9fc01702fb52ec8f5164282434b91` · Trạng thái: **R0 COMPLETE theo S01-S06; live execution vẫn khóa**.

## Thay đổi đã thực hiện

- `mt5_data.py`: import không còn tự mở listener `127.0.0.1:9000`; transport chỉ khởi động qua lifecycle explicit.
- `app.py`: bỏ auto-init MT5 cho mọi request; `/api/trade/place` và `/api/trade/close` trả `410 LEGACY_EXECUTION_DISABLED`; local write bị chặn theo remote/Host/Origin; web bind mặc định về loopback.
- `static/js/trade_desk.js`: giữ durable request ID qua double-click/timeout/reload bằng session storage; trạng thái `unknown` phải reconcile trước khi tạo intent khác.
- `MT5Gateway.mq5` source v1.21: execution mặc định tắt; chỉ demo + explicit opt-in + exact login/server + request ID + trade permissions mới đi tới handler trade. `CHECK_ORDER` vẫn read-only.
- `p5_app.py`: backend readiness MT5 chỉ mở transport khi người vận hành explicit chọn `mt5-readonly`.
- Test R0 cô lập được thêm; test session legacy bỏ phụ thuộc vào private auto-init state đã retire.

Đã backup source/binary gateway đang chạy, deploy source v1.21 vào đúng data folder MT5 đang hoạt động, compile tại chỗ bằng MetaEditor và restart terminal một lần bằng `CloseMainWindow()` để nạp binary mới. Runtime probe chỉ mở listener loopback tạm thời và gửi hai command phải bị deny tại EA boundary; không gửi broker order và không mở nhánh live.

## Evidence theo S01–S06

| Gate | Evidence hiện tại | Trạng thái |
|---|---|---|
| S01 · Import/default init | Test patch `threading.Thread` xác nhận import `mt5_data` không start thread/listener; full test chạy xong port 9000 không listen | Pass source/test |
| S02 · Legacy write | Body trống/sai/đúng đều 410; fake fetcher xác nhận init/place/close call count = 0 | Pass |
| S03 · Mode/account/origin | P4 verifier deny `live/local/replay`; existing tests deny wrong account/server/missing confirmation; R0 test deny remote/cross-origin | Pass software |
| S04 · Duplicate/timeout/reload | Execution journal tests giữ idempotency/reconcile; Trade Desk giữ request ID qua session storage và không cho đổi intent khi request cũ unresolved | Pass source/test; browser interaction chưa chạy |
| S05 · Entrypoint/script/EA | Legacy route retire; P4 default simulator; P5B cần exact identity + `--execute`; EA v1.21 compile/deploy sạch. Runtime trên account `trade_mode=real`: `TRADE_BUY` và `TRADE_CLOSE` đều trả `EXECUTION_DISABLED` với lý do demo execution disabled; positions trước/sau đều rỗng | **Pass runtime deny-only** |
| S06 · Regression/data | Full Python regression pass; P4 verifier pass; `data/` aggregate SHA-256 trước/sau test không đổi | Pass |

## Validation

Các command an toàn đã chạy trong project repo:

```text
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts\p4_verify.py
node --check static\js\trade_desk.js
```

Full suite final: **108/108 pass**. `p4_verify.py` PASS với `live/local/replay` đều bị deny, duplicate/timeout không resend và `live_execution_enabled=false`; `node --check static/js/trade_desk.js` PASS. Aggregate SHA-256 của toàn bộ file dưới `data/` trước/sau: `4DDEC0B7FC53435E74AE7AC19E27D4F2FE62E9E83451801F4866B5C0CCCEEC96`. Kiểm tra listener sau suite không thấy process listen port 9000.

MetaEditor compile source `MT5Gateway.mq5` v1.21 trong active terminal data folder: **0 errors, 0 warnings** (`3634 ms`, `X64 Regular`). Source deploy khớp SHA-256 repo `ECAFCDAF34905373B7D006FB8F13F18FAFB702B0AE1D6D749A5A1297A0DDD526`; binary mới SHA-256 `D9DA34497C3101CCD573F6F77F3CF133A85506DA627EDF10D458380877C8DC5A`. Backup v1.20 được giữ với suffix `pre-r0-v121-20260919-065729.bak`.

Runtime deny-only probe sau restart:

```text
GET_EXECUTION_CONTEXT -> success=true, trade_mode=real
GET_POSITIONS         -> []
TRADE_BUY             -> success=false, error=EXECUTION_DISABLED
TRADE_CLOSE           -> success=false, error=EXECUTION_DISABLED
GET_POSITIONS         -> []
RUNTIME_DENY_ONLY     -> PASS
```

Gateway từ chối ở `DemoExecutionAllowed()` trước `HandleTradeOrder()` / `HandleTradeClose()`, nên hai command test không tới `CTrade`/`OrderSend`. Listener test được đóng sau probe; live execution không được enable.

## Kết luận R0

S01-S06 đều có bằng chứng source/test hoặc runtime phù hợp và không còn finding tiền/quyền mở trong phạm vi R0. **R0 đóng gate ngày 19/09/2026.** R1 được phép bắt đầu ở lượt tiếp theo theo `NEXT-ITERATION-PLAN.md`; trạng thái này không suy ra live-ready hay cho phép nhánh L.
