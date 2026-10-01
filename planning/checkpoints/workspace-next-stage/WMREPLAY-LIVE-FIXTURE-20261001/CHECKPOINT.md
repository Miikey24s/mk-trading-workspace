# WMREPLAY live offline fixture — 2026-10-01

## Mục đích

Chạy UI Vite hiện tại với một API fixture local, in-memory, để review behavior và visual có dữ liệu replay. Fixture không phải backend sản phẩm và không mở broker, provider, OAuth, secret, holdout hay external network.

## Đã làm

- Thêm `fixture-server.mjs` dùng Node built-in `http` tại `127.0.0.1:8010`.
- Fixture cung cấp overview, dataset catalog, session catalog, replay GET/create/step/branch và các read-only owner-lock status tối thiểu.
- `vite.config.js` đã có proxy `/api` tới `TW_V2_API_TARGET` và mặc định `http://127.0.0.1:8010`; không cần sửa product source.
- Vite frontend đang chạy tại `http://127.0.0.1:5173/`.

## Runtime evidence (2026-10-01)

- Fixture PID: `3304` (`fixture-server.pid`), log không có stderr.
- `GET http://127.0.0.1:8010/health` trả `status=ok`, `fixture=true`, `execution_capability=false`.
- Browser-visible dashboard đã load overview fixture: `1 datasets`, `1 research jobs`, `6 saved records`; trạng thái không còn `Failed to fetch`.
- Browser-visible replay đã load `EURUSD · M1`, dataset `ui-live-fixture`, cutoff `#4`, `5 nến`, `broker locked`; chart chỉ render prefix và ghi rõ nến tương lai bị ẩn.
- One-off Playwright smoke: `PASS`; 4 checks (overview/replay × 1440/390), overflow `0` ở mọi viewport, replay visible rows `5`, không có console error ngoài filter favicon/fixture-not-found.
- Screenshots: [dashboard-1440.png](dashboard-1440.png), [dashboard-390.png](dashboard-390.png), [replay-1440.png](replay-1440.png), [replay-390.png](replay-390.png).

## Safety boundary

- In-memory only; restart là mất state.
- `execution_capability=false`, broker/live/OAuth/provider/holdout đều khóa.
- Các mutation ngoài replay-local trả `403 fixture_mutation_blocked`.
- Đây là review fixture, không được dùng làm product/backend acceptance.

## Cách chạy / dừng

```powershell
node .\planning\checkpoints\workspace-next-stage\WMREPLAY-LIVE-FIXTURE-20261001\fixture-server.mjs
```

Dừng bằng `Ctrl+C` hoặc dừng đúng process Node đã ghi trong process audit. Không dùng `Stop-Process` theo tên chung.

## Validation cần ghi bổ sung

- Health endpoint trả `status=ok`, `fixture=true`, `execution_capability=false`.
- Browser review dashboard và replay ở 1440/768/390.
- Kiểm tra chart chỉ hiển thị prefix trước cutoff, không lộ row tương lai.
- Kiểm tra route matrix và console/runtime errors sau khi fixture chạy.

## Rollback / resume

Rollback chỉ cần dừng fixture process; xóa thư mục checkpoint nếu owner yêu cầu. Vite vẫn có thể chạy ở trạng thái error-safe khi fixture tắt. Resume bằng cách chạy lại lệnh trên, rồi mở:

`http://127.0.0.1:5173/?workspace=tenant-a&view=overview`

