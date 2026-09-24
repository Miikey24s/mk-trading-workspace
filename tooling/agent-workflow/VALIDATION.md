# Kiểm chứng runtime — 17/09/2026

Kết luận: **vòng smoke Web GPT → verifier Python → Web GPT reviewer đã chạy được**. Chỉ chứng minh luồng CLI trên fixture nhỏ; chưa chứng nhận triển khai sản phẩm, an toàn toàn máy hoặc hiệu quả trading.

## Bằng chứng chính

Job: `runs/20260917-044156-smoke-fixture-db8554`.

| Phần | Kết quả kiểm tra |
|---|---|
| Worker | `chatgpt-web/high`, effort `high`; đọc source/test bằng shell chỉ đọc, sửa đúng `src/risk.py` bằng file edit; không thay test |
| Reuse | `loss_streak_probability` gọi helper `probability_power`, không chép phép tính/validation |
| Verifier | AST khớp forwarding implementation đã duyệt; test fixture giữ nguyên; `unittest`: 3/3 đạt |
| Reviewer | Phiên mới, cùng `chatgpt-web/high` / `high`, sandbox read-only; đã đọc TASK/code/test bằng lệnh thực tế; verdict **PASS** với giới hạn static review |
| Phạm vi | Worker đổi một file được giao; reviewer đổi 0 file; `unexpected_changes=[]` cho hai lượt thành công |
| MCP | Preflight lấy catalog hiệu lực từ đúng staging, tắt từng server và kiểm tra lại; logs hai lượt thành công không còn startup MCP không liên quan |
| Runner tests | 14/14 đạt: đường dẫn, giữ source, model mặc định, parse output, quyền review, evidence cũ, MCP preflight, attempt cap và lock |

Đọc `03-worker.report.txt`, `04-reviewer.report.txt`, `smoke.verification.txt`, `state.json` trong job trên. `review_returned` không tự có nghĩa được tích hợp; supervisor đã đọc lại report, source và evidence cho smoke này. Không có thay đổi nào được đẩy về repo sản phẩm.

## Những lỗi đã gặp và cách xử lý

1. Reviewer cũ bị prompt cấm cả đọc file bằng shell. Đã cho phép lệnh chỉ đọc trong staging; vẫn cấm sửa/chạy source/test/script khi review. Không xem report cũ là pass.
2. `-c mcp_servers={}` không xóa MCP kế thừa vì TOML merge. Lượt đầu bị controller dừng khi thấy Unity MCP khởi động không liên quan. Không có thay đổi staging ở lượt đó.
3. Không dựng override từ danh sách trong project gốc: cấu hình project có thể không được trust ở staging, dẫn tới entry chỉ có `enabled` mà thiếu transport. Giờ dùng `codex mcp list --json` tại đúng cwd với cùng feature flags, rồi tắt các entry hiệu lực.
4. CLI phiên bản này coi dấu quote trong dotted override key là ký tự trong tên; preflight đã chặn trước khi model chạy. Chỉ nhận tên MCP đơn giản đã kiểm tra; không tự tìm cách bypass khi format lạ.
5. Codex phải trả completed turn + nội dung; CLI exit 0 không đủ. Với AGY phải kiểm tra status, response và denied_actions.

Job lưu đủ cả hai lượt lỗi rồi hai lượt thành công, không xóa lịch sử hoặc tăng cap để che lỗi. Hai lượt thành công dùng tổng khoảng 130 giây thời gian CLI tại thời điểm thử; không phải benchmark hoặc ETA cho task thật. Usage trong state là số provider báo, chưa xác minh cách tính/cache, không quy đổi thành quota.

## Antigravity và các role khác

- Job cũ `runs/20260917-005757-smoke-fixture-bcc96a`, lượt `02-ui-worker`: `gemini-3.8-flash-medium` đã sửa đúng file, reuse helper, controller 3/3 đạt. Report/verification cũ đã được đọc lại; không chạy thêm AGY model trong lượt 17/09 này.
- Không mặc định dùng AGY thay Web GPT. `ui-reviewer`, `ui-designer` và `sol-worker` chưa có bài thử vai trò đầy đủ. Sol reviewer cũ đã trả lời được nhưng review bị chặn do prompt; không dùng nó làm bằng chứng review đạt.
- Đã thêm bridge tại TradingWorkspace `.agents/rules/trading-workspace.md` theo docs Antigravity. Chưa mở IDE để kiểm chứng auto-discovery; nếu cần, yêu cầu agent đọc file trực tiếp. Không dùng computer/browser automation.

## Giới hạn còn giữ nguyên

- Một worker và một reviewer cùng model có thể cùng bỏ sót lỗi. Tests/đối soát độc lập và nghiệm thu mốc vẫn cần thiết.
- General task chưa có verifier đăng ký: pipeline dừng sau worker để kiểm tra và chạy test có phạm vi. Không tự chạy command tùy ý trong task packet; không có auto-accept/merge/deploy.
- Staging + sandbox + hash không phải cách ly bảo mật toàn máy. Chưa chứng nhận chặn mọi network/process; không gửi secrets, raw dataset hay broker credentials. CLI vẫn chịu hook/rule local; warning cấu hình hooks trùng của máy không được sửa global trong task này.
- Không thay provider/auth Cockpit, không cài service, không đổi model picker, không thêm quyền broker. Repo MT5 vẫn có thay đổi của người dùng `?? charting_library/`, không bị đụng tới.
- Model alias `chatgpt-web/high` gọi được qua route hiện có. Không chứng minh model nền hay cam kết “quota vô hạn”.

## Audit instructions

`ai-environment-maintainer`: TradingWorkspace **ok**, 0 lỗi/0 cảnh báo; active 14.113/65.536 byte, dự trữ 51.423 byte. Audit scope tooling: **ok**, active 12.505/65.536 byte, dự trữ 53.031 byte. Đây là kết quả từng scope do script báo, không phải phép đo toàn bộ prompt của model.

Bước sản phẩm tiếp theo vẫn là P0 audit nền theo PLAN v0.7. Setup CLI không tự duyệt code mới hoặc làm P0 hoàn thành.
