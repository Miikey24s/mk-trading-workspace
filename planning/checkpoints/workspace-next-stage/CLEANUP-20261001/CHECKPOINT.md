# Workspace cleanup — 01/10/2026

**Scope:** hoàn tất cleanup đã được owner duyệt ở chat `01a0f5d5-b360-7a33-b1f7-27c83d3e8659`, tiếp nối tại phiên này. Đây là receipt dọn repo và lưu WIP, không phải product acceptance hoặc một PLAN mới.

## Cấu trúc và authority sau cleanup

- README là cửa vào bốn repo. CURRENT-CONTEXT dẫn tới workspace RESUME và PLAN đúng domain.
- Product Plan giữ scope MT5; WMREPLAY giữ các gate UI; ledger giữ attempt state và xuất STATE.json. Cleanup không sửa ledger hoặc tự nâng acceptance.
- VI PLAN giữ queue và các gate hiện hành; UI-FIX-PLAN chỉ đối chiếu source. PLAN giảm 3.522 → 127 dòng; bản gốc vẫn có checksum tại archive của VI.
- Các hướng SaaS/cloud/frontier và exploration đã bị thay thế ra khỏi việc phải hoàn thành hiện tại; giữ implementation/knowledge có ích và code legacy còn được PATH-2 gọi.
- AGENTS và hai skill UI trỏ về nền chính, không tự tái tạo các checkout prototype đã bỏ. Execution override 27/09 vẫn được ghi với đúng phạm vi và ngày, không thành model mặc định cho cleanup.

## Đã dọn và đường phục hồi

| Nhóm | Kết quả | Phục hồi |
|---|---|---|
| Bốn `_ps02*_accept_*` | Phiên trước đã stash rồi gỡ bằng Git; phiên này xác nhận không còn checkout | ZIP đã kiểm hash và stash IDs trong `.artifacts/workspace-cleanup-20261001/`; evidence riêng nằm ở [retired-worktree-evidence](retired-worktree-evidence/) |
| Figma Make / Gemini sketch | Thư mục đã biến mất trước khi phiên trước hoàn tất backup; phiên này sao lưu metadata rồi prune đúng hai đăng ký stale | Nhánh local `codex/figma-make-mt5-context` ở `e055a592`, `codex/mt5-gemini-sketch` ở `f294f55`; **chưa xác nhận khôi phục được WIP chưa commit của sketch** |
| `projects/planning` và MT5-local `planning` | Chuyển ra khỏi cây sản phẩm sau khi đối chiếu 6 file và không có file lạ | [recovered-notes.json](recovered-notes.json), [bản lưu byte gốc](recovered-notes/); nguyên thư mục còn local trong `retired-trees/` bên dưới |
| Bản website `projects/app.fxreplay.com` | Chuyển 893 file ra khỏi cây dự án; không publish source/capture/account payload bên thứ ba | `.artifacts/workspace-cleanup-20261001/retired-trees/app.fxreplay.com/` |
| 14 script MT5 tạm và 1 ảnh trùng | Đã bỏ khỏi runtime tree, không thấy source/test consumer còn dùng | `.artifacts/workspace-cleanup-20261001/mt5/manifest.json` và 15 snapshot khớp hash |
| Gitlink `p05-repo` không khai báo | Bỏ khỏi index, ignore đúng fixture; giữ local fixture | `.artifacts/workspace-cleanup-20261001/worktree-metadata/fixture-gitlink.txt`; Git history giữ gitlink cũ |

Đường `.artifacts/` tính từ workspace root, là backup **local-only**, không nằm trong Git remote. Bốn stash cũng là local. Các snapshot tài liệu và evidence được chọn trong `planning/` vẫn được lưu Git. Cleanup này không tuyên bố giải phóng toàn bộ dung lượng các bản phục hồi.

## Review và kiểm chứng

- Bốn thư mục sót chỉ chứa junction `node_modules` được chuyển cùng volume vào `.artifacts/workspace-cleanup-20261001/retired-dependency-links/`, không đi xuyên junction hoặc sửa dependency target. Không thấy tiến trình Node/Python sử dụng các đường dẫn này; `projects/` sau đó chỉ còn bốn repo sản phẩm.
- 65 link local trong 11 tài liệu hiện hành pass. README dùng URL repo đích cho liên kết xuyên submodule để đọc được cả trên GitHub.
- Independent review: MT5 source/docs, VI docs/Job12, workspace authority/link/archive. Đã sửa 5 locator sai sau compact, giữ compatibility anchor, khôi phục failed heap gate và execution override còn thiếu.
- MT5: web **57/57**, build pass (71 modules, cảnh báo bundle 722,97 kB); AI **30/30**; contracts/analytics **9/9**. PowerShell launcher parse sạch, 25 link docs MT5 pass. Không chạy API/PostgreSQL integration, browser QA hoặc provider/broker trong cleanup.
- VI: 29 link trực tiếp pass; 4 snapshot khớp bytes/hash và baseline content; artifact Job12 giữ `qa.passed=false`, `full_track_skipped=true`, `final_failed=122`. Không chạy lại media/provider hoặc full suite.
- Full staged diff retains historical Markdown hard-break spaces and trailing blank lines in 45 pre-existing checkpoint/capture files. These receipts/scripts are preserved rather than rewritten during cleanup; active cleanup docs pass a separate diff check.
- Workspace: 4 snapshot archive và 6 recovered notes khớp hash; STATE.json khớp sidecar SHA-256. Archive dùng `-text -diff` để giữ nguyên byte/whitespace lịch sử; active docs vẫn được kiểm diff.
- Scan 358 file văn bản thay đổi bằng các mẫu token/private key/JWT không có finding; đây là kiểm tra theo mẫu, không phải chứng nhận security toàn lịch sử.
- AI environment audit: root active 20.200/65.536 B, MT5 active 15.499/65.536 B; không lỗi/cảnh báo. Audit MT5 chỉ cộng global + repo của nó; nếu nạp cả root lẫn nested thì tổng 23.842 B, còn 41.694 B dự phòng.
- `git submodule status` chạy thành công sau sửa fixture. Quant ref validation không còn object-missing; Quant/TradingAgents đã khớp remote trong lần kiểm tra này.

## WIP đã lưu không đồng nghĩa accepted

MT5 docs `e6fde95`, AI guard `efb0a34`, Replay contrast `a90526c`, CSV header `d8dbcd2`; VI cleanup `674eec2`. Replay CSS trước cleanup đã được checkpoint, không còn cần giữ một dirty tree làm bằng chứng. Tiếp tục kiểm browser/route matrix từ commit đó, không quay lại hoặc ghi đè thay đổi.

Giữ mở: Replay/native zoom/axe/golden/full-bleed, Dashboard semantics và heap gate. Soak 74,3 phút đã trượt ngưỡng heap; reconcile harness trước rerun. VI giữ lỗi fixture-order, Job12 failed QA và P23 whole-job/whole-pipeline. Broker/provider/OAuth/holdout/deploy không được mở bởi các commit cleanup.

Quy trình: review/stage theo nhóm → push repo con → cập nhật gitlink workspace → push workspace → đối chiếu hash remote. Kết quả hash cuối được báo tại chat; không sửa snapshot để tự nhận sản phẩm hoàn thành.
