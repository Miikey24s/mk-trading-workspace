# Phụ lục dọn repo — tích hợp trong U0 / U1–U8 / U9

Phiên bản **1.2 · 20/09/2026** · **PHỤ LỤC, CHƯA DI CHUYỂN/XÓA FILE**.

**Greenfield gate:** cleanup không được ép giữ repo hoặc implementation. F5 trong [foundation plan](FOUNDATION-RESEARCH-PLAN.md) chọn PATH-1/2/3; scope đường dẫn/code disposition cập nhật theo quyết định đó. [Knowledge register](KNOWLEDGE-PRESERVATION-REGISTER.md) và data handoff phải đạt trước retire. Quyền nghiên cứu xây mới không là quyền xóa repo cũ ngay.

Tài liệu con của [PRODUCT-COMPLETION-PLAN.md](PRODUCT-COMPLETION-PLAN.md). Mục đích: một entrypoint rõ, code dễ tìm/reuse, cài lại được, không có dữ liệu cá nhân lẫn source và không phá phần đang dùng. Không đo thành công bằng số file/dòng code đã xóa.

**Không giao hoặc chạy riêng tài liệu này.** Worker đọc theo mục 15 plan chính: U0 gọi C0; mỗi U1–U8 gọi C1 cho phần vừa thay đổi; U9 gọi C2. Người dùng chỉ cần giao plan chính. Kết quả cleanup nằm trong checkpoint của mốc U, không mở pipeline/tracker/agent dọn song song. Dọn lớn ở cuối, không trì hoãn việc cập nhật caller/launcher hoặc retire đường bypass bị thay thế.

## 1. Phạm vi và ba thời điểm

| Đợt | Khi nào | Được chuẩn bị/làm khi được giao | Không làm |
|---|---|---|---|
| C0 · Kiểm kê | U0 trước tính năng mới | Read-only file/consumer/license/data ownership map; đề xuất cleanup manifest | Không đổi cây thư mục lớn, không xóa cache/data, không “git clean” |
| C1 · Dọn theo lát | Khi U1–U8 thay hoặc mở rộng module | Refactor phần liên quan; update callers/tests/docs; bỏ dead code đã chứng minh sau replacement pass | Không kéo module khác vào rewrite, không đồng thời đổi logic tiền và chuyển hàng loạt file |
| C2 · Đóng gói | U9 sau acceptance các tính năng | Dọn các mục đã duyệt, kiểm clean setup/backup/restore, release inventory | Không xóa lịch sử run/checkpoint hoặc bundle user để repo trông đẹp |

Repo hiện có trong inventory: `D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester`. Nếu F5 chọn repo mới, chốt đường dẫn/scope ở lúc giao F6, không tự tạo trong research này. Plan ở `D:/ANNAM/TradingWorkspace/planning/mt5-tradingview-backtester`. `quant-trading`, `TradingAgents`, `vi-dubber`, course và AI tooling ngoài scope **không tự thuộc cleanup**. Không `git init` workspace cha hoặc đổi ownership repo.

## 2. Những gì đã thấy — danh sách để kiểm tra, không phải danh sách xóa

| Nhóm | Ví dụ trong baseline | Quyết định mặc định |
|---|---|---|
| Entrypoint | `workspace_app.py`, `app.py`, `p1_app.py`–`p5_app.py` | Workspace là entrypoint được hỗ trợ; các phase files có thể vẫn là factory phụ thuộc nhau, không xóa theo tên |
| Core/domain | evidence/research/practice/risk/execution modules | Tìm duplicate thật về hành vi; giữ một owner và contract, không gộp chỉ vì tên giống |
| Legacy UI/assets | `templates/index.html`, replay/trading/analytics JS cũ | Có thể còn replay save và provenance consumer; chỉ retire sau migration parity và route inventory |
| Chart library | `charting_library/`, `static/charting_library/` | Bản local có vấn đề license/duplication cần kiểm; không xóa, publish hay đưa vào git tự động |
| Broker configs | `p5b-*.ini`, `p5c-*.ini`, `.bak` tương ứng | Có thể chứa account/server/settings; kiểm caller và phân loại private trước; không in giá trị nhạy cảm |
| Source/binary/log MT5 | `MT5Gateway.mq5`, `MacGateway.ex5`, compile logs | Source mới không chứng minh binary cũ thừa; map terminal/path/version/hash trước khi đề xuất archive |
| Dữ liệu/giao dịch | `data/`, SQLite, chunks, journal/history | Giữ nguyên và backup; không xem file gitignored là rác |
| Fixtures/QA | `r3b_qa_fixture.py`, scripts QA, tests | Giữ regression oracle/synthetic provenance labels; fixture không đưa lẫn production |
| Scratch | `scratch_position.py` | Chưa biết consumer/side effect; đọc source trước, không chạy thử để xem tác dụng |
| Caches/môi trường | `__pycache__`, `.pytest_cache`, `.venv` | Có thể tái tạo nhưng không mặc định xóa; chỉ dọn khi có lợi ích, đường dẫn và rebuild rõ |
| Tài liệu/checkpoints | PLAN, iteration plans, P/R/L checkpoints | Giữ bằng chứng lịch sử, thêm index/current-status pointer; không xóa vì nội dung cũ |

Mỗi item phải có consumer map: import, route, template/static URL, scripts/launcher, scheduled task/hook, config, test, serialized class/schema reference và external tool nếu có. `rg` không thấy tên chỉ là một bằng chứng, chưa chứng minh dynamic/runtime consumer không tồn tại.

## 3. Cleanup manifest — lập trước thao tác

Worker bổ sung manifest vào checkpoint của lát đang làm, không tạo tracker riêng cạnh tranh. Mỗi dòng gồm:

`ID | resolved source path | loại dữ liệu/owner | tracked/untracked/ignored | consumers | lý do | keep/refactor/move/archive/delete | target path | backup/hash | ảnh hưởng | test | rollback | quyền/decision`.

- **Keep:** còn dùng hoặc chưa biết; mặc định khi thiếu evidence.
- **Refactor:** có duplication/coupling cụ thể, test mô tả hành vi trước/sau.
- **Move:** có lợi ích tìm kiếm/ownership; update mọi consumer, không tự đổi public API/IDs.
- **Archive:** chưa còn trong đường dùng chính nhưng còn bằng chứng/rollback value; một nơi archive có index, không copy vô hạn.
- **Delete:** chỉ file đã chứng minh không dùng, đã có replacement/backup nếu cần, nằm trong scope được duyệt. Dữ liệu/material deletion phải hỏi riêng.

File user/untracked không phải quyền sở hữu của agent. Không dùng baseline cũ để ghi đè thay đổi mới; kiểm Git diff/status ngay trước patch. Nhánh hiện tại chưa push không cho phép force-push hoặc rewrite lịch sử.

## 4. Cây thư mục: tiến hóa vừa đủ

Không bắt giữ repo hiện tại hoặc cây thư mục cũ. F5 quyết định repo topology theo target và nhiều AI sessions; C0 inventory chỉ hỗ trợ mapping/retire/knowledge, không khóa thiết kế. PATH-1 có thể chỉnh layout tại chỗ; PATH-2/3 có thể tạo layout mới. Không bắt chuyển thành `src/` hoặc bê toàn cấu trúc phase cũ qua chỉ để có map old→new.

Các quy tắc bất kể layout:

- Một launcher/entrypoint công bố cho daily workspace; legacy commands phải hướng dẫn rõ và không thể mở lại bypass.
- Business logic không phụ thuộc DOM/route; một read model/công thức chính, annotations khác execution intent.
- Test/unit và broker acceptance tools tách; default test không start listener/MT5, không đọc holdout hoặc ghi data gốc.
- Generated output, private config, runtime DB/log và dependency environment ngoài phần source phân phối. `.gitignore` chỉ chặn tracking mới, không xóa thứ đã commit hoặc scrub lịch sử.
- Giữ dependency nhỏ và version reproducible; rà Python version README/venv/import requirements, JS build/test command. Chỉ thêm lock/dev manifest thích hợp toolchain đã chọn, không đổi package manager cho đẹp.
- Symlink/junction phải được nhận diện trước move; đường dẫn data theo config/path resolver dùng chung, không hardcode máy của agent.

Nếu sửa `AGENTS.md`, skill, MCP/config/hook trong lúc triển khai, worker phải dùng skill quản trị môi trường hiện có và audit. Đừng biến cleanup thành cập nhật persistent global settings. Lượt lập plan này không sửa các file môi trường.

## 5. Dữ liệu, secrets, license và an toàn Windows

### Dữ liệu cần bảo vệ

Raw giá/tin, holdout, journal/fills, protocol/strategy versions, QA baselines/oracles, chart annotations/layout, backups, model evaluation logs và source-license notices có ownership/retention riêng. Không deduplicate dữ liệu chỉ theo timestamp hoặc tên file. SQLite đang mở/WAL cần snapshot/backup đúng cách, không copy một file DB đơn lẻ rồi khẳng định restore được.

Sao lưu phải có kiểm tra integrity/schema/count/checksum và restore thử trên thư mục mới; giữ IDs và liên kết run/trade/source. Không overwrite data directory đang dùng. Giữ bản tốt ít nhất tới khi bản mới nghiệm thu và user duyệt bỏ bản cũ; không tự đặt TTL ngắn cho lịch sử trading.

### Secrets/private config

Scan chỉ báo loại/đường dẫn, không đổ key/password/login ra log. Config account cụ thể nên chuyển về private runtime config khi workflow mới đã kiểm; public template dùng placeholders. Nếu phát hiện secret đã commit: dừng công bố, báo riêng, xin xử lý rotation/revoke và history remediation; xóa file hoặc thêm ignore không sửa được lộ lọt quá khứ. Không tự revoke/đổi account/password.

### License và third-party

Giữ LICENSE/NOTICE/attribution và provenance upstream. Không gộp giấy phép MIT project với Advanced Charts hoặc dataset vendor. Không publish proprietary binaries/data chỉ vì nằm local. Fork/adapt phải ghi nguồn/commit và update policy.

### Thao tác file

Trước recursive delete/move, resolve đường dẫn tuyệt đối, kiểm nằm trong đúng subtree đã duyệt và không đi qua junction ra ngoài. Dùng một shell xuyên suốt, ưu tiên PowerShell literal paths; không ghép danh sách path sang cmd/batch để xóa. Không dùng `git clean -fdx`, broad wildcard, `reset --hard` hoặc recursive operation nhắm workspace/repo root.

Ưu tiên archive/trash có đường phục hồi. Ngừng thao tác khi process đang dùng file/terminal có vị thế hoặc owner chưa rõ; không tự kill process để dọn. Sau material deletion phải báo chính xác thứ đã bỏ và phục hồi bằng cách nào.

## 6. Quy trình C1 cho một nhóm file

1. Chụp baseline commit/status/diff và file inventory; bảo toàn edits của user/worker khác.
2. Chỉ ra replacement/helper có sẵn và consumers; lập manifest/rollback.
3. Có test behavior/parity chạy trong môi trường tách biệt trước. Không viết test chỉ assert file biến mất.
4. Sửa/move/refactor một mục đích nhỏ. Tách mechanical rename khỏi thay đổi semantics nếu có thể; update imports/assets/templates/launchers/docs cùng scope.
5. Focused tests → regression bị ảnh hưởng → smoke supported entrypoint. Migration/data shape đổi phải thử trên bản sao.
6. Review mới kiểm API/route/mode/data/provenance không đổi ngoài phần đã duyệt; chỉ retire đường cũ sau replacement đạt.
7. Ghi commit/diff, commands/results, manifest trước/sau và cách rollback. Push/release/deploy vẫn theo quyền giao việc, không suy từ cleanup pass.

Rollback không được mở lại execution bypass đã khóa. Nếu revert phần UI/layout gây phải quay về entrypoint cũ không an toàn, giữ fail-closed và phục hồi data/path qua bước riêng, không dùng một revert lớn thiếu kiểm tra.

## 7. Gate dọn repo và đóng gói

| ID | Bằng chứng | Điều kiện đạt |
|---|---|---|
| C01 | Manifest và ownership | Mỗi file thay/di chuyển/xóa có lý do, consumers, target và rollback; unknown được giữ |
| C02 | Imports/routes/assets/commands | Không broken links/imports; navigation, launchers và supported scripts dùng đúng đường mới |
| C03 | Safety regression | Không tái mở legacy/live bypass; default startup/test không nối broker |
| C04 | Data continuity | Raw/hash/IDs/records/provenance giữ nguyên; restore bản sao đạt, không đọc holdout để thử |
| C05 | Clean setup | Checkout/package mới chạy với sample có nhãn và dependencies khai báo; không dựa vào global package/private file cũ |
| C06 | Hygiene/security/license | Không secret/PII không cần/generated/proprietary payload lẫn source; notices còn đủ; whitespace/encoding đúng |
| C07 | Bàn giao | README phân biệt current/legacy, commands đã test, runtime support, blockers và quyết định giữ archive |

Mức độ gọn không thay tiêu chí software/product. Nếu C0 cho thấy file phase vẫn là factory hữu ích thì giữ, không ép xóa. Không đánh đổi khả năng audit/thống kê/khôi phục lấy một cây thư mục ít file.
