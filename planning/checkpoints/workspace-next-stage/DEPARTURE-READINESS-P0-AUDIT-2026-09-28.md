# Departure readiness P0 audit — 2026-09-28

**Scope:** kiểm tra khả năng để owner rời workspace ngay ngày mai trong khi hệ thống tiếp tục chạy an toàn. Audit chỉ đọc/offline; không mở provider, broker, OAuth, wallet, holdout, live execution và không đụng process Job12.

**Verdict:** chưa đạt `DEPARTURE_READY`. Nền fail-closed đã tốt ở mức contract/reducer, nhưng chưa có một host-level supervisor thực sự khởi động, lưu state, renew lease, fence process, khôi phục và cảnh báo xuyên các project. Vì vậy trạng thái an toàn khi owner biến mất phải là `research`/`paper`/`advisory` hoặc `paused`, không phải live trading.

## Đã xác minh

| Lớp | Bằng chứng | Kết luận |
|---|---|---|
| Owner-absence policy | `projects/mt5-tradingview-backtester/foundation_v2/trading_workspace_v2/owner_absence_safety.py` | `execution_capability` bị khóa literal `False`; kill switch mặc định bật; thiếu/hết hạn lease, heartbeat, resource, data freshness hoặc cutoff lỗi thì stop |
| Fence/restart reducer | `.../owner_absence_supervisor.py`, `tests/test_owner_absence_supervisor.py` | `start → continue`; fence sai thì stop; restart bắt buộc fence mới; restart budget hết thì quarantine; reducer không side effect |
| Paper admission | `admit_owner_absence_paper` + paper bridge | Bind run/fence/intent/risk hash; chỉ nhận `paper`; không cấp broker/provider capability |
| Research worker | `store.py`, `worker.py`, `research.py` | PostgreSQL có job lease, expiry recovery, checkpoint/progress, cancel và stale-attempt guard |
| Artifact integrity | `artifacts.py`, `test_artifacts_security.py` | Artifact có containment, digest và atomic candidate/publish/quarantine path |
| AI advisory | TradingAgents checkpoint/run identity/atomic report wave | Có resume/run identity ở project riêng; không phải execution engine |
| Job12 | retained VI job receipt/checkpoint | Đang chạy đúng một process tree; audit không restart/kill/delete lock |

Các điểm trên là **offline/PREP_ONLY**, không phải chứng minh paper soak, live readiness hay lợi nhuận.

## P0 gaps nếu owner phải rời ngày mai

1. **Chưa có host-level startup supervisor.** `owner_absence_supervisor` là pure reducer; chưa có process nào đọc snapshot khi boot, kiểm PID/child ownership, chạy tick, persist `next_snapshot`, hoặc thực hiện stop/restart an toàn. Một reducer pass không đồng nghĩa job sẽ tự chạy sau crash/reboot.
2. **Lease/fence chưa được nối vào một persistence boundary chung.** Policy nhận lease/heartbeat như evidence input; chưa có acquire/renew/release + compare-and-swap cho supervisor state, nên hai host/process có thể cùng tin rằng mình là owner nếu lớp vận hành gọi sai.
3. **Chưa có durable cross-project run registry/event journal.** MT5, Quant, TradingAgents và VI có các identity/checkpoint riêng; chưa có một `run_id`/attempt/fence/event lineage nối chúng để replay, phát hiện duplicate và đối soát một phiên unattended.
4. **Chưa có cold-start/readiness gate dùng được một lệnh.** Boot chưa chứng minh: default mode là research, kill switch đang bật, DB/artifact root đúng, schema/migration đã kiểm, clock/data freshness hợp lệ, không có active run cũ và không tự tạo duplicate.
5. **Backup/restore chưa được nghiệm thu cho toàn bộ state.** Có artifact digest và vài restore seam, nhưng chưa có drill kết hợp PostgreSQL metadata + artifact root + supervisor/run journal + config/version; chưa có hash/consistency check sau restore, RPO/RTO và rollback packet.
6. **Không có watchdog/alert/escalation đã nối.** Stop/quarantine chỉ là state; chưa có kênh cảnh báo owner/delegate, dedup, retry policy và xác nhận sự cố. “Có stop reason” không đảm bảo con người biết để xử lý.
7. **Runbook departure/incident chưa đủ executable.** Chưa có packet ngắn chứa supported startup, status, recovery, backup, restore, quarantine/reset, log paths, expected exit codes và quy tắc tuyệt đối không restart Job12 duplicate.
8. **Paper soak và controlled AI-trade gate chưa đạt.** Đây là gap cố ý: AI chưa được quyền tự trade/live. Không được hạ gate để kịp “ngày mai”.

## Thứ tự P0 nên làm ngay

1. **Durable supervisor seam:** một state record append-only hoặc CAS có `run_id`, `attempt_no`, `fence_token`, `lease_expiry`, `heartbeat`, `mode`, `kill_switch`, `last_checkpoint`, `artifact root/hash`, `state`; boot đọc và fail closed.
2. **Offline supervisor CLI/entrypoint:** `status`, `start-research`, `start-paper`, `tick`, `stop`, `recover`, `quarantine`; mặc định `research`; không có command live/broker. Mỗi restart phải tạo fence mới và reject stale writer.
3. **Crash/reboot drill:** child chết, host boot lại, lease stale, duplicate start, partial artifact, clock/data stale, corrupted snapshot; expected result lần lượt là recover mới fence hoặc `paused/quarantined`, không resend/duplicate.
4. **Backup/restore drill:** backup transactionally consistent DB + artifact manifest + supervisor journal; restore vào disposable root; verify every digest, foreign-key/lineage and latest safe state before allowing research.
5. **Departure runbook + alert contract:** one-page exact commands, paths, health states, no-secret logs, owner/delegate escalation and manual reset rule; attach evidence to M7.
6. **Paper soak:** chỉ sau 1–5, chạy 30–60 ngày forward/paper with reconciliation and pause-on-health-failure; live remains an explicit owner gate.

## Acceptance criteria cho “có thể để máy chạy khi owner vắng”

- Cold start không có token/provider/broker/OAuth và không tạo duplicate process.
- Missing/stale lease, heartbeat, resource, data, clock, checkpoint hoặc artifact hash ⇒ `paused`/`quarantined`.
- Crash recovery chỉ chạy với fence mới; old fence write bị reject.
- Every output has deterministic `run_id`, attempt, input/code/config/artifact digests and redacted event trail.
- Restore từ backup vào máy sạch được kiểm tra bằng hash trước khi chạy tiếp.
- Health/stop/quarantine gửi một alert deduplicated; nếu alert unavailable thì state vẫn fail closed.
- No paper/liveness claim is promoted to live automatically; `execution_capability` vẫn `False`.

**Remaining external gates:** provider/OAuth/login, real media/6h+ Job12 acceptance, human listening, broker/demo/live, holdout và lawful delegate/account controls. Không audit nào ở đây thay thế các gate đó.

**Rollback:** file này chỉ là additive planning evidence; xóa/revert riêng file không chạm code hoặc process.
