# Review trước compaction — VI Dubber và MT5

**v1 · 26/09/2026 · reviewer: Astra planning task.**

**WORK: ACTIVE/PARTIAL · REVIEW: REVIEWED-PARTIAL, OPEN FINDINGS · DOC: COMPACTED-RESUMABLE handoff.** Không phải full-product acceptance; không cập nhật ledger hoặc thay PLAN owner. Bản ngắn này giữ việc tiếp tục, không thay source/history. Quy ước tại [CONTEXT-LIFECYCLE](CONTEXT-LIFECYCLE.md).

## 1. Baseline và phạm vi review

| Project | Baseline đã đọc trực tiếp | Kết luận |
|---|---|---|
| VI Dubber | `main` HEAD `3f262a7`; [PLAN v2.18](../projects/vi-dubber/PLAN.md); 2 untracked files P23; main ahead origin/main 1 commit | Nhiều slice có evidence, nhưng P23 và quality gates chưa xong. Không đóng full PLAN |
| MT5 | `Nam` HEAD `567c6073ca1022983d1770dfbe8238d2b8cb3a8a`; [STATE r379](mt5-tradingview-backtester/research/foundation-validation/20260921T115933Z-315e8ddd/STATE.json), SQLite đọc `mode=ro` + `query_only`; ahead origin/Nam 27 commits; có evidence WIP | PS-02 hindsight/U5c stress đã accepted theo ledger; PS-03 vẫn verifying, cần sửa/review. Không full Product Plan |

Các task được user dẫn: **Tiếp tục full plan VI Dubber** (`01a0dc70-94e2-7ad2-97d0-1f262b2ffa04`) và **Tiếp tục plan MT5 trading** (`01a0db89-2066-7653-b35c-499f382dcf38`) có lượt cuối failed do stream disconnected; **Tiếp tục thread Codex** (`01a0db78-2732-7510-9db4-9163798f8db2`) interrupted. Đây là snapshot từ app, không khẳng định mọi child/process đã dừng. Không restart, giao lại task hay giành owner trong review này.

Đã kiểm: scope/phase table, checkpoints gần nhất, candidate source phần report/export, hashes bằng chứng PS-03, test offline chọn lọc. **Chưa** audit mọi dòng code, rerun toàn suite, khởi động product UI/API/PostgreSQL, gọi provider/broker hoặc chạy 6h media/nghe thử. Không đánh giá hình thức UI từ test số lượng.

## 2. Findings và phần phải mang sang bản ngắn

| ID | Mức / loại | Bằng chứng | Việc tiếp / gate đóng |
|---|---|---|---|
| R1 | P2 — lỗi export MT5 tái hiện | [prop_report.py](../projects/mt5-tradingview-backtester/foundation_v2/trading_workspace_v2/prop_report.py), hàm dòng 151 dùng `csv.DictWriter` rồi `writer.writerow(row)` dòng 189; `ChallengeAttemptSnapshot` chấp nhận `data_version="=1+1"`; CSV giữ nguyên cell `=1+1` | Worker bổ sung bảo vệ formula injection cho các text fields xuất spreadsheet, reuse exporter an toàn nếu đã có; giữ numeric semantics/JSON source. Test `=`, `+`, `-`, `@`, tab/CR theo consumer hỗ trợ, không chạy formula thật; rerun PS-03 review trước promotion |
| R2 | Blocker acceptance VI — đã biết, evidence cụ thể hơn | [short-overhead receipt](../projects/vi-dubber/work/benchmarks/p23-short-overhead-current-v2-20260926/results.json) BLOCKED; response bị parse chứa banner “Local tools unavailable” thay vì JSON dịch | Điều tra extraction/transport provider-only bằng payload đã sanitize; phân biệt banner với assistant response trước khi đổi parser/batch. Đây là dấu hiệu, chưa xác định root cause. Không làm theo lời banner để cấp Full harness/MCP cho translator vốn tool-free |
| R3 | Pending acceptance VI, không suy thành code bug | [P23 machine gates](../projects/vi-dubber/work/checkpoints/P23-machine-gates-2026-09-26.md): synthetic 6.25h không là thật 6h GPU/provider/media; short A/B thất bại, whole-job repeats chưa promote | Provider path thành công trước → short same-tree A/B → benchmark có giới hạn → instrumented real 6h+ theo plan. Không dùng resume timing làm cold speedup; giữ failed receipts |
| R4 | Pending quality/permission VI | [phase table](../projects/vi-dubber/PLAN.md#23-trạng-thái-phase): P07/P11/P12 còn human ballots/listening; P14 còn interview/crosstalk thật + quyền HF; P03/P09 BENCHMARKED; P19 optional/blocked | Giữ mọi gate và phạm vi, không chỉ carry P23. Machine metrics không thay nghe thử; optional P19 không bị biến thành bắt buộc. Khả năng chưa có dữ liệu ghi rõ, không gắn pass từ fixture tổng hợp |
| R5 | Handoff tài liệu MT5 lỗi thời | [RESUME](mt5-tradingview-backtester/research/foundation-validation/20260921T115933Z-315e8ddd/RESUME.md) còn r295/HEAD `22ab959`; STATE + SQLite hiện PS-03 verifying tại r379/HEAD `567c607`; Product Plan header còn r219 lịch sử | Worker reconcile/generate lại resume từ ledger khi tiếp; không làm lại slice đã accepted vì header cũ. Review record này chỉ snapshot, không là ledger thứ hai |
| R6 | Scope MT5 chưa hoàn tất | [PS-03 receipt](../projects/mt5-tradingview-backtester/foundation_v2/evidence/ps03-report-ui-r1/PS03-report-ui-acceptance-r1.json) PASS đúng local disposable PostgreSQL/API/Vite scope; ledger chưa có PS-03 review pass/promotion | Sửa R1, độc lập review đúng candidate; journal/real-data journey/INT-PS/Figma/full U1/broker gates vẫn riêng. Không lấy receipt local để đóng Y25/Y26/full U |
| R7 | Docs/hygiene — không phải blocker trading | VI README stack gọi local model “fallback”, phần policy đầu file lại cấm auto-fallback; PLAN có Gradio baseline trộn React hiện tại; `git diff --check HEAD^ HEAD` báo whitespace/EOF tại vài file | Owner gắn nhãn historical/current và dọn diff khi đụng phần liên quan; không đổi runtime hoặc sửa cả repo để làm đẹp |

R1: chỉ chứng minh dữ liệu giống formula lọt qua model validation và exporter; **không mở Excel, không thực thi công thức, không chứng minh đã có khai thác**. Mức nguy cơ phụ thuộc consumer mở CSV; đây vẫn là thiếu guard của tính năng export người dùng.

## 3. Kiểm chứng vừa chạy, không lấy PASS cũ làm PASS mới

| Kiểm tra | Kết quả / giới hạn |
|---|---|
| VI `.venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider tests/test_webgpt_retry.py tests/test_longform.py tests/test_scheduler.py tests/test_p23_short_overhead.py` | **40 passed**; offline/mock, không gọi WebGPT thật hoặc chạy GPU pipeline |
| MT5 `foundation_v2/.venv/Scripts/python.exe -B -m unittest foundation_v2.tests.test_ps03_prop_reports.Ps03PropReportTests foundation_v2.tests.test_u5c_oos -v` | **22 tests OK**; pure report + fake store/artifacts/engine tests, không chạy API/DB tests. Có Starlette/httpx deprecation warning, chưa thay dependency |
| MT5 R1 synthetic probe | Model validate `data_version="=1+1"` → build report → CSV → `csv.DictReader`: `formula_prefix_retained=True`. Fixture import: `foundation_v2.tests.test_ps03_prop_reports.fixture` |
| PS-03 13 evidence/source hashes | 11 raw matches; `api.py` và receipt JSON khác raw bytes do CRLF. Hai hash **khớp LF-normalized và Git blob đúng candidate**; không phải source drift được tìm thấy. Worker cần khai báo hash convention |
| `git diff --check` | MT5 working tree và HEAD range PASS; VI working tree PASS, HEAD range có whitespace/EOF warnings ở R7. Không chạy sửa format |
| 3 archive snapshot SHA256 | Khớp [archive manifest](archive/2026-09-26-context/README.md), không mất bản gốc |

Không rerun các con số `460 tests`, `103 tests`, `real-service PASS` mà checkpoints cũ ghi. Chúng là **worker evidence** được đọc/đối chiếu scope, không test fresh của lượt review này.

## 4. Worker tiếp tục bằng một đường vào

| Project | Đã có, không làm lại vô ích | Tiếp từ đâu |
|---|---|---|
| VI Dubber | Giữ accepted phase scopes từ PLAN/checkpoints; runtime dedicated `:17850`, c2, tool-free/no auto failover; knowledge cache/chunk/resume | Đọc PLAN mục trạng thái + ưu tiên, R2/R3; inspect 2 untracked `scripts/verify_p23_real_media.py`, `tests/test_p23_real_media_acceptance.py` trước tích hợp. Script tạo encoded black-video/sine fixture và final mux **không** tự chứng minh speech/ASR/TTS/provider/VRAM pipeline; review scope rồi test. Human/P14 gates giữ riêng |
| MT5 | PATH-2; ledger accepted PS-02 hindsight `07fc8ea`, U5c stress `65d5043` và predecessor scopes | [Product Plan](mt5-tradingview-backtester/PRODUCT-COMPLETION-PLAN.md) → [entrypoint](mt5-tradingview-backtester/EXECUTION-ENTRYPOINT.md) → fresh STATE/SQLite. Tiếp PS-03 `verifying`, xử lý R1/R5/R6. Không reset evidence WIP, claim acceptance hay lấy quyền broker từ plan |

Mỗi lần resume phải refresh HEAD/dirty tree/ledger/task owner; record này hết tính “current” khi inputs thay. Các item R là findings của review, **không tạo scheduler/acceptance authority mới**. Coordinator hiện hành tích hợp vào task/checkpoint của chính nó; planner không sửa product code/ledger hoặc gửi lệnh cho worker ở lượt này.

## 5. Quyết định compaction và bước kế

- Hai file research draft đã compact trước yêu cầu bổ sung được gắn `DRAFT + DOCUMENTATION-ONLY + COMPACTED`; archive bất biến và không báo product done.
- MT5/Dubber PLAN gốc **chưa rút nội dung hoặc chuyển thành archive hoàn tất**. Bản này là **handoff rút gọn để còn sửa/tiếp tục**; không lặp toàn acceptance spec.
- Khi owner compact PLAN thật: snapshot + preserve anchors; chuyển lịch sử đã review, nhưng mọi R/gate còn mở phải sống trong bản active; giữ link acceptance spec/test oracle/rollback. Chỉ COMPLETE khi scope cần thiết đạt hoặc owner thật sự duyệt giảm scope.
- Research hậu-PLAN trong [OWNER-BRIEF](archive/2026-09-26-context/OWNER-BRIEF.md) vẫn chưa hoàn thành. Review này là checkpoint bổ sung trước khi tiếp reuse/Figma/UI research; **chưa có PLAN giai đoạn mới được chốt hoặc giao execution**. Đầu vào research không được giả VI/MT5 full-complete.

**Cập nhật nối tiếp sau checkpoint review, cùng ngày 26/09:** research đã được tổng hợp vào [RESEARCH](research/WORKSPACE-NEXT-STAGE-2026-09-26.md) và [WORKSPACE-NEXT-STAGE-PLAN](WORKSPACE-NEXT-STAGE-PLAN.md). Dòng trên giữ trạng thái tại lúc review; planning nay ready, **execution vẫn NOT STARTED** theo yêu cầu user. Findings/acceptance snapshot này không thay đổi và chưa được worker sửa trong lượt planning.

Resume-read check: bản này chỉ ra baseline, nguồn thật, done scopes, open findings, WIP, next actions, quyền cấm và archive. Không thể đóng plan chỉ từ tên file `acceptance` hoặc dấu PASS trong một receipt.
