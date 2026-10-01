# Vòng đời context và PLAN

**v1.2 · 01/10/2026 · REVIEW TRƯỚC COMPACTION; convention, không framework/CLI mới.**

## Vì sao chọn cách này

Đọc tài liệu chính thức về [Codex long-running work](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex): state ngoài chat, tool feedback và validation hỗ trợ resume. [AGENTS discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md) nhấn mạnh instruction có scope/size, không nên nhét lịch sử vào đó. Đây là nguyên tắc tham khảo, không chứng minh capability của custom WebGPT runtime.

[ADR của Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) giữ quyết định đã bị thay thế cùng liên kết tới quyết định mới. [Diátaxis](https://diataxis.fr/start-here/) tách how-to/reference/explanation/tutorial; áp dụng chọn lọc, không dựng bốn thư mục trống chỉ để đủ mô hình.

Lựa chọn: index ngắn + living specs/ADR + PLAN active + receipts/history tách riêng. Không vector DB/context generator/second task ledger. Research cũ chỉ refresh khi input/version/capability đổi hoặc có contradiction.

## Authority map sau audit

| Nhóm | Authority còn sống | Cách đọc / giữ |
|---|---|---|
| Workspace routing | AGENTS + CURRENT-CONTEXT | Mỗi file một vai trò, không copy status từng job vào đây |
| MT5 scope | Product Plan/entrypoint/UI autonomy | Còn worker, không compact phá anchor/path/gates |
| MT5 execution | Run ledger/STATE/RESUME + receipts dẫn từ entrypoint | Ledger own task state; historical header không override |
| MT5 architecture/semantics | PATH-2 ADR, Data & Metrics, contracts, knowledge register | Giữ live; freeze/supersede từng decision thay vì chép vào mọi PLAN |
| MT5 master PLAN/research cũ | PLAN.md là index/history hỗn hợp; foundation report/F0–F7 là evidence lịch sử đúng scope | Đọc section cần; chưa di chuyển vì còn caller và active worker |
| VI Dubber | Project PLAN + source/tests/checkpoints | PLAN đang >3.000 dòng, trộn baseline/history; review trước, compact vẫn giữ việc mở và quyền writer |
| Shared UI | UI-Systems docs/contracts + trading UI + project decisions | Layered ownership hiện có; snapshot status chưa chứng minh release |
| Future proposals | Integration/quant-roadmap briefs | Giữ ngắn, chi tiết ở archive; DRAFT không là task được giao |

## Agent mới cần gì?

Read-set tối thiểu: instructions áp dụng → CURRENT-CONTEXT → assigned PLAN → current task/attempt state → đúng contract/test oracle. Archive chỉ mở để giải quyết why/conflict/regression. Không bắt đọc toàn lịch sử chat hay mọi file `.md`.

Context packet cho một task: mục tiêu, baseline/owner, allowed files, contract/version, reuse candidate, acceptance, quyền cấm, next action và evidence locator. Không cần copy nhiều PLAN vào prompt. State phải có changed files, test đã chạy/thất bại/chưa chạy, artifacts và blocker cụ thể.

## Review trước; compact được cả phần đã xong và phần làm dở

1. **Review trước khi rút nội dung:** đọc scope/acceptance, HEAD + dirty tree, trạng thái worker, ledger/checkpoint và receipts. Đối chiếu source/hash; chạy kiểm chứng hẹp phù hợp quyền/rủi ro. Worker ghi PASS là input review, không tự là nghiệm thu. Ghi rõ phần chưa kiểm; chat ngắt không chứng minh code hỏng, cũng không chứng minh hoàn thành.
2. Ghi review có thời điểm, baseline, người/agent review, findings và evidence. Phân loại từng phần: đã accepted đúng scope / còn lỗi hoặc thiếu bằng chứng / chưa review / ngoại lệ được duyệt. Không dùng một dấu xanh cho tất cả.
3. Chọn kiểu compact: **đã đạt** thì chuyển lịch sử chi tiết sang archive; **còn việc** thì rút thành bản tiếp tục có đủ lỗi, acceptance chưa đạt, WIP, dependencies và next action. Chưa đủ review thì chỉ tạo bản điều hướng ngắn, giữ nguyên PLAN nguồn. Không phải đợi full plan xong mới được giảm context.
4. Chắt lọc invariant/decision/runbook còn sống vào tài liệu owner hiện có. Kiểm incoming links/anchors/current writer; không move hoặc thay PLAN mà worker khác có thể đang ghi. Active PLAN cần owner phối hợp; không lấy việc chat báo failed làm quyền giành writer.
5. Snapshot nguyên bản + original path + SHA256 + version/date/review/acceptance reference. **Archived draft** hoặc **snapshot of active plan** không là milestone accepted. Giữ bất biến bản gốc; CRLF/LF và Git-blob hash phải phân biệt khi kiểm source, không tự kết luận code đổi từ line-ending mismatch.
6. Rút gọn canonical giữ mục tiêu/scope/dependencies/milestones/acceptance + link lịch sử. Với việc mở, bắt buộc giữ: ID/owner, lỗi và cách tái hiện, test đã chạy/chưa chạy, file/WIP, blocker/quyền, bước tiếp và gate để đóng. Không xóa negative finding/exception hoặc ghép nhầm phần accepted với candidate.
7. Cập nhật routing và nhãn dưới đây; không tạo ledger cạnh tranh. Checkpoint review là snapshot, ledger/PLAN owner vẫn là authority.
8. Kiểm hash, links/caller/anchor và preservation map. **Resume-read test:** chỉ từ bản ngắn + links, agent phải chỉ ra đúng phần đã đạt, phần chưa đạt, bước tiếp, quyền cấm và rollback; nếu không thì chưa compact đạt. Khi có reviewer độc lập sẵn thì dùng, không bắt tạo agent/framework mới chỉ để đủ thủ tục.

## Nhãn rõ thay cho “đóng dấu đã xong”

Đây là convention của workspace, không phải một chuẩn tên nhãn chung của ngành. Thực hành được reuse là metadata phiên bản + review/acceptance record + lịch sử truy ngược; không cần con dấu ảnh hoặc chữ ký số.

| Trục | Giá trị dùng trong tài liệu | Ý nghĩa |
|---|---|---|
| Công việc | `DRAFT`, `ACTIVE/PARTIAL`, `COMPLETE` | Trạng thái scope sản phẩm; COMPLETE phải có acceptance đúng scope |
| Review | `NOT_REVIEWED`, `REVIEWED-PARTIAL`, `ACCEPTED-SCOPED` | Review có giới hạn hoặc nghiệm thu một scope cụ thể; ghi findings mở ngay cạnh |
| Tài liệu | `FULL`, `COMPACTED`, `COMPACTED-RESUMABLE`, `ARCHIVED-SNAPSHOT` | Hình thức lưu/context; không thay trạng thái sản phẩm |

Header tối thiểu: phiên bản/ngày; ba trạng thái trên; baseline; link review; link archive/source; next action nếu còn mở. `REVIEWED-PARTIAL` không có nghĩa không còn lỗi. Đổi HEAD/contract/scope sau review thì cần kiểm delta, không tiếp tục coi stamp cũ là bằng chứng cho code mới. Review tài liệu draft ghi `DOCUMENTATION-ONLY`, không gán product acceptance. Không thêm chữ ký của người dùng khi họ chưa nghiệm thu.

Ví dụ phần làm dở: `WORK: ACTIVE/PARTIAL | REVIEW: REVIEWED-PARTIAL, open findings | DOC: COMPACTED-RESUMABLE` cùng HEAD/date/review/next action. Review, acceptance và hash đều giúp truy vết nhưng hash **không chứng minh chất lượng**.

Budget định hướng: current context khoảng 1–2 trang; active PLAN vài trăm dòng tùy scope; milestone history không nối vô hạn. Đây là review trigger, không quota cho phép bỏ spec/acceptance cần thiết.

## Archive policy

Archive là bất biến; sửa quan điểm bằng tài liệu mới, không sửa bằng chứng cũ. Với byte-identical snapshot, relative links dùng **original base** ghi trong archive record; file canonical có link hoạt động. Không giả mọi link trong bản snapshot di chuyển vẫn resolve tại vị trí mới. Không xóa cache/data/test fixtures cùng với dọn tài liệu.

Kiểm tra 01/10/2026 xác nhận workspace gốc và bốn repo sản phẩm đều có Git. Git history giữ được nội dung đã commit; WIP, file untracked và dữ liệu ignored cần bản phục hồi riêng trước compact hoặc xoá. Snapshot phải ghi nguồn là Git blob hay file trên đĩa để tránh nhầm CRLF/LF. Không tự init repo; chỉ stage/commit đúng phạm vi người dùng đã giao.

## Áp dụng lần này / để owner làm sau

Đã compact hai research draft trước yêu cầu bổ sung review worker; giữ full bytes và source citations ở archive, không coi đó là product review. [Review worker 26/09](WORKER-REVIEW-2026-09-26.md) đối chiếu lại source/ledger và có focused tests; kết luận **chưa full acceptance, còn findings**. Active MT5/Dubber PLAN, ledger và product code giữ nguyên. Bản review là handoff ngắn cho việc mở; owner vẫn cần cập nhật/tách lịch sử trong PLAN nguồn sau khi reconcile trạng thái và quyền writer.

Lượt mới: **current context → review việc trước → compact giữ việc mở → reuse audit → targeted research → decision → executable plan → implement → review/acceptance → compact → cập nhật context**. Research nền mới có thể tiếp dựa trên scope đã biết, nhưng implementation phụ thuộc capability nào thì phải chờ gate capability đó. Thêm skill/CLI chỉ khi lần lặp chứng minh convention không đủ.

## Quy trình dọn toàn workspace — đối chiếu tài liệu 01/10/2026

Phần này ghi kết quả nghiên cứu và quy trình áp dụng; không xác nhận việc di chuyển/xoá đã diễn ra, không huỷ hạng mục sản phẩm hoặc thay authority của worker. Tái sử dụng convention này và [phụ lục cleanup MT5](mt5-tradingview-backtester/REPO-CLEANUP-PLAN.md), không mở một master PLAN hoặc task ledger mới.

### Nguồn tham khảo và quyết định áp dụng

Các nguồn dưới đây được đọc trực tiếp ngày 01/10/2026. Cách bố trí workspace là đề xuất dựa trên code và ownership hiện có; các nguồn không quy định một cây thư mục bắt buộc.

| Nguồn chính thức / tác giả gốc | Điều áp dụng |
|---|---|
| [GitHub: About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) | README giải thích dự án và cách bắt đầu; nội dung dài dẫn sang tài liệu đúng chủ đề. Link cùng repo ưu tiên tương đối. Link vượt repo phải kiểm riêng trong checkout workspace và trên GitHub. |
| [Diátaxis: Start here](https://diataxis.fr/start-here/) | Phân biệt hướng dẫn học, hướng dẫn làm việc, tra cứu và giải thích. Áp dụng theo nội dung có thật, không tạo bốn thư mục trống hoặc chuyển mọi file chỉ để khớp mẫu. PLAN và trạng thái chạy có vai trò riêng. |
| [Michael Nygard: Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) | Quyết định cũ vẫn giữ lý do và hệ quả; khi bị thay thế thì ghi trạng thái và link quyết định mới. Không sửa lịch sử thành quan điểm hiện tại. |
| [Git: worktree](https://git-scm.com/docs/git-worktree) | Worktree có metadata riêng. Sau khi bảo toàn thay đổi, dùng cơ chế quản lý worktree thay vì xoá thư mục trực tiếp; remove thông thường yêu cầu cây sạch, kể cả file untracked. |
| [Git: submodules](https://git-scm.com/docs/gitsubmodules) | Repo con có lịch sử riêng; repo cha giữ gitlink và khai báo `.gitmodules`. Gỡ checkout và bỏ submodule khỏi sản phẩm là hai quyết định khác nhau. |
| [Git: gitignore](https://git-scm.com/docs/gitignore) | Ignore không tác động tới file đã tracked. Ngừng theo dõi, giữ file local và xoá dữ liệu là các thao tác riêng; không dùng `.gitignore` như bằng chứng file có thể bỏ. |
| [Google Engineering Practices: Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html) | Mỗi thay đổi có một mục đích dễ review/rollback. Tách dọn tài liệu, gỡ bản thử và retire code; không trộn đổi hành vi với di chuyển hàng loạt. |
| [SQLite: Online Backup API](https://www.sqlite.org/backup.html) | Database đang hoạt động cần snapshot nhất quán bằng cơ chế backup phù hợp, rồi kiểm tra bản khôi phục. Một bản copy file thông thường không tự chứng minh backup dùng được. |

### Một nguồn chính cho mỗi loại thông tin

| Loại thông tin | Nơi giữ quyền quyết định | Các nơi khác chỉ làm gì |
|---|---|---|
| Điểm vào workspace | `README.md` | Dẫn tới project và tài liệu; không giữ thêm bảng tiến độ chi tiết. |
| Điều phối liên project | `WORKSPACE-NEXT-STAGE-PLAN.md` | Giữ phạm vi/dependency giữa các project; các mốc tổng hợp phải dẫn về nguồn trạng thái của domain. |
| Phạm vi và tiêu chí MT5 | `mt5-tradingview-backtester/PRODUCT-COMPLETION-PLAN.md` cùng phụ lục được nó dẫn tới | WMREPLAY là phần UI theo scope, không thay Product Plan hoặc ledger backend. `PLAN.md` cũ vẫn giữ các section còn authority/caller cho tới khi được thay thế rõ ràng. |
| Trạng thái các task thuộc run MT5 | `ledger.sqlite3` của run được entrypoint dẫn tới | `STATE.json` là bản export; `.sha256` kiểm integrity; `RESUME.md` giải thích cách tiếp tục. Không sửa tay snapshot để tuyên bố task đã đạt. |
| Phạm vi và tiến độ phát triển VI | `projects/vi-dubber/PLAN.md` | Checkpoint chứa bằng chứng chi tiết; không để `frontend/UI-FIX-PLAN.md` trở thành một tracker cạnh tranh sau reconcile. |
| Trạng thái một job VI | State/artifact của chính job theo source runtime | PLAN chỉ dẫn tới bằng chứng. Hoàn tất xử lý, đạt QA và nghiệm thu sản phẩm là các kết luận riêng. |
| Kiến trúc, contract và công thức | ADR/spec/code owner hiện hành | PLAN/README dẫn link; không copy thành định nghĩa hoặc công thức thứ hai. |
| Lịch sử và bằng chứng | Receipt gốc hoặc snapshot có locator/hash | Index ngắn giúp tra cứu; không diễn giải archive thành việc đã hoàn tất. |

Bằng chứng producer MT5: trong run `mt5-tradingview-backtester/research/foundation-validation/20260921T115933Z-315e8ddd/`, `controller.py::export_snapshot` xuất snapshot và hash; `record_post_r283_candidates.py` kết nối `ledger.sqlite3`, cập nhật task rồi gọi export. Đây là authority của các task trong run đó, không suy tất cả UI checkpoint hoặc job media đều có cùng ledger.

### Cấu trúc đích tối thiểu

- `README.md`: cửa vào duy nhất cho người đọc.
- `planning/`: phạm vi liên project, PLAN/spec MT5 đang có, checkpoint và `archive/`. Giữ đường dẫn canonical khi còn caller; đưa lịch sử khỏi luồng đọc hằng ngày theo từng nhóm đã review.
- `projects/<repo>/`: code, môi trường và tài liệu riêng của repo. Giữ bốn repo độc lập, không nhân bản `planning/` workspace vào repo con. Nội dung đặt nhầm phải so sánh và nhập phần duy nhất trước khi xoá bản sao.
- `education/`, `UI/`, `tooling/`: tiếp tục giữ đúng chức năng hiện có. Không lập hệ tài liệu hoặc framework mới để dọn hệ cũ.
- Runtime, cache, model và media tiếp tục theo path/config của project; phân loại bằng owner và khả năng tái tạo. Chưa đổi đường dẫn dữ liệu chỉ vì muốn cây thư mục đồng đều.

### Thứ tự thực hiện và điều kiện kết thúc

1. **Lập danh sách theo nhóm:** đường dẫn đã resolve, repo/worktree sở hữu, trạng thái Git, caller, writer/process, phần nội dung duy nhất, đề xuất giữ/lưu trữ/gỡ/xoá và cách phục hồi. Thiếu bằng chứng về consumer thì ghi chưa rõ. Quyết định bỏ chức năng phải rõ trước khi loại code của chức năng đó.
2. **Lưu bản phục hồi phù hợp:** Git history cho bản đã commit; giữ riêng WIP/untracked cần thiết. Với database dùng backup nhất quán và kiểm tra restore. Không gom cache/job/dữ liệu người dùng vào gói xoá file tạm.
3. **Rút tài liệu trước:** giữ mục tiêu, scope, việc mở, negative findings, dependencies và bước tiếp theo ở đúng nguồn. Nguồn khác chỉ link hoặc snapshot có revision/ngày. Di chuyển lịch sử kèm mapping đường cũ → đường mới và xử lý link/anchor.
4. **Dọn từng nhóm độc lập:** file sinh lại được, bản thử đã hết dùng, worktree đã bảo toàn, sau cùng mới retire code có dependency. Worktree/submodule dùng đúng cơ chế Git. Không dùng force hoặc xoá hàng loạt để vượt qua cảnh báo cây chưa sạch.
5. **Kiểm tra sau mỗi nhóm:** link local và link xuyên repo, anchors, import/caller, launcher/config và focused test/build phù hợp. Người đọc mới phải từ README tìm được đúng scope, nguồn trạng thái, việc tiếp theo và điều kiện còn thiếu. Archive phải tra ngược được; nguồn trạng thái không bị nhân đôi.
6. **Lưu Git sau dọn và review:** theo thứ tự người dùng yêu cầu, commit coherent trong từng repo rồi push; repo gốc cập nhật các mốc repo con sau. Kiểm tra hash remote và báo chính xác những file local không được đưa lên Git. Không dùng working tree sạch làm tiêu chí duy nhất cho task hoàn tất.

Tiêu chí đạt là tìm đúng thông tin nhanh, mỗi thay đổi có một owner, phần mềm giữ hành vi đã chấp nhận và nội dung cần thiết khôi phục được. Số dòng hoặc số file giảm chỉ là số liệu phụ. Research này chưa thay kiểm tra thực tế cho từng mục dự kiến xoá.
