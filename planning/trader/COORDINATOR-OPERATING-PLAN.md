# Một coordinator — điều phối, nghiệm thu và phục hồi công việc

v1.4 · 24/09/2026 · **SPEED-FIRST · POOL CEILING 10 · PLAYWRIGHT-FIRST UI CHECKS · FULL RUNTIME CAPABILITY PARTIAL**.

Nguồn: [Astra synthesis](research/webgpt-native-v2/ASTRA-SYNTHESIS-2026-09-21.md), Y22 và F4. File này không quyết định foundation app trading; dev orchestration và broker execution là hai hệ có quyền/side effects riêng.

**UI authority 23/09:** coordinator/reviewer tự chọn và nghiệm thu UI trong scope Product Plan v2.1, không xin owner từng màn. [Phụ lục UI/Figma/Prop](UI-AUTONOMY-FIGMA-PROP-PLAN.md) quy định rubric, vòng Make, packets và real-connection evidence; permissions không thay nghiệm thu. Lưu `agent-accepted`, không ghi user đã approve; giữ gate tiền/dữ liệu/OAuth/chi phí/deploy. Figma async round phải có baseline/hash/owner để không ghi đè kết quả worker khác. Lượt planning không launch agents.

**Tooling 24/09 / Product Plan v2.2:** coordinator dùng [Playwright kit](../../tooling/ui-qa/README.md) trực tiếp cho UI work được giao, không qua staged legacy runner có policy cấm browser. Mỗi agent/task có session + artifacts riêng, không kill-all/cookie/profile reuse. Chỉ đọc summary rồi trace/screenshots khi cần; integrated product assertions + visual reviewer vẫn bắt buộc. Kit chỉ ghi evidence, không launch models hoặc sửa ledger; controller hiện hành own acceptance. Figma tools đã expose không tự chứng minh Make auth/round-trip.

**Quyết định user 21/09:** ưu tiên throughput/tốc độ, chấp nhận lỗi agent có thể phục hồi; nâng trần PLAN lên **10 browser turns tổng cộng trên pool nhiều instance**. Chính sách này thay default một child / ban đầu tối đa hai child trong synthesis cũ, không sửa kết quả các probes lịch sử thành PASS. Không đổi code/config/runtime trong lượt cập nhật plan.

## 1. Cách user sử dụng cuối cùng

User giao PLAN cho **một Codex Web GPT coordinator**. Coordinator đọc entrypoint và state, tự chọn task đủ dependencies, cấp việc, thu artifact, kiểm tra, tích hợp và tiếp milestone đủ quyền. User không cần mở backend/frontend/test chats, copy outputs hoặc nhớ task nào done.

Khi coordinator mất context hoặc không còn chạy, mở một chat mới với cùng entrypoint là thao tác tối thiểu có thể cần. Chat mới không cần lịch sử đầy đủ: reconcile state/artifacts rồi tiếp phần thiếu. Không hứa app tự bật lại, model hoạt động vô hạn hoặc retry là miễn phí.

Entry hiện tại: [EXECUTION-ENTRYPOINT.md](EXECUTION-ENTRYPOINT.md). PATH-2 đã user-approved; lần giao execution tiếp theo đi FH hardening trước các U phụ thuộc. Quyết định ở planning thread không tự khởi chạy worker.

**Reconciliation 22/09:** run `research/foundation-validation/20260921T115933Z-315e8ddd` có ledger revision 144, CO-00…06 accepted theo scope từng receipt; Astra đã kiểm DB/snapshot/hash và chạy lại 16 controller tests PASS. Core là thư viện/controller local có fixture proof, không chứng nhận end-to-end autonomous coordinator. CO-04 r4 có local process overlap, nhưng native Web GPT overlap/multi-instance/10 vẫn false/unverified; CO-05 là fresh OS process, không fresh Web GPT root. Các mô tả “để thử/chưa xây” bên dưới là design intent lịch sử; trạng thái thực dùng reconciliation này và receipt, không sửa evidence cũ thành claim rộng hơn.

## 2. Những lựa chọn đã quyết cho prototype vận hành

| Thành phần | Chọn để thử | Lý do / giới hạn |
|---|---|---|
| Coordinator | Một authority local cho một execution run | Giảm conflict state; root mới phải takeover có kiểm tra |
| Agent route | Web GPT qua Codex/Native2 tools đã discover ở turn hiện tại | Không giả tên tools, không giữ turn token trên đĩa; không fallback Astra/Sol/provider khác |
| Parallel policy | **Speed-first, trần 10 browser turns toàn pool/toàn task tree** | Tính coordinator, writer, reviewer, nested children và lượt control/recovery thực sự chiếm browser; không phải 10 child cộng root |
| Phân bổ thực tế | Work-conserving theo task sẵn sàng, host slots, từng instance và resource budget | Hai instance × 5 là sức chứa thiết kế 10; healthy/route/khả năng overlap phải kiểm riêng; không khóa lâu dài ở 1–2 child |
| Task ledger local | **SQLite single-writer controller**, artifacts ở file bất biến | Đã có prototype trong validation run; local storage tests đạt, không tự là end-to-end autonomous scheduler |
| Portable state | Versioned export snapshot + manifest/receipt có checksum | Snapshot để đọc/restore; không có hai writable sources of truth |
| Progress cho người | Markdown sinh từ ledger, ngắn, đúng state revision | Không sửa bảng tiến độ tay để đánh dấu accepted |
| Repo isolation | Worktree hoặc sandbox riêng cho mỗi writer task | Không mặc định native subagent được cấp sẵn; DB/tmp/ports riêng |

SQLite ở đây là **state điều phối AI trên một máy**, không là quyết định database multi-user của app trading. Không đặt WAL DB lên network share hoặc dùng cho nhiều host cùng ghi. Nếu điều phối đa host thực sự cần, đổi authority/store qua migration có test; không lấy sự tiện hiện tại để giới hạn product architecture.

Nguồn [SQLite atomic commit](https://www.sqlite.org/atomiccommit.html) và [WAL](https://www.sqlite.org/wal.html) đã đối chiếu ngày 21/09. Controller chọn durability settings rõ, backup bằng cơ chế DB hỗ trợ; không chỉ copy `.db` khi WAL đang active. DB transaction không làm Git/network/tool calls trở thành một atomic transaction.

### 2A. Trần tổng, giới hạn từng instance và admission

Một coordinator vẫn là đầu mối duy nhất. Cockpit sở hữu chọn provider/instance; coordinator sở hữu task graph, admission và integration. Không xây router tài khoản thứ hai trong Trading Workspace hoặc tự sửa Cockpit để ép phân phối.

| Đại lượng | Quy tắc |
|---|---|
| `plan_pool_ceiling` | **10** browser turns đồng thời, tổng trên các instance cho execution run này |
| `instance_cap[i]` | Đọc/kiểm bản runtime thực tế; snapshot hiện tại là **5 mỗi instance**, không tự đổi thành 10 mỗi instance |
| Instance đủ điều kiện | Enabled + healthy + route/model/tool capability phù hợp + không có protection/cooldown; enabled trong registry chưa đủ |
| Capacity ngoài run | Trừ các lượt khác đang chiếm chỗ trên từng instance; nhiều run không được mỗi run tự nhận cả 10 slot |
| Host agent capacity | Giới hạn native collaboration của coordinator là lớp riêng; discover live. Phiên Astra lúc lập plan chỉ expose 4 agents tổng, không phải bằng chứng Web GPT execution chat tương lai chỉ có 4 |
| Parent/control headroom | Tính ít nhất một chỗ cho Web coordinator; nếu parent đã chiếm chỗ thì không trừ hai lần. Tăng reserve khi compaction/recovery thật sự cần; không có invariant bắt bỏ trống thêm một slot mãi mãi |
| Worker tối đa | Khi host cho phép và đủ hai instance: **1 coordinator + tối đa 9 children active**; reviewer thay chỗ writer đã xong, không mở thành child thứ 10 ngoài ngân sách |
| Nhiều instance hơn sau này | Inventory động, không hard-code hai port; trần PLAN vẫn 10 cho tới quyết định thay đổi mới, không tự nhân 10 theo N |

Tính capacity toàn run từ `min(10, host capacity quy đổi cùng đơn vị, tổng instance capacity còn dành được cho run, local resource budget)`. Khi dispatch, kiểm lại chỗ trống từng instance và số task độc lập ready; không lấy một health counter cũ làm reservation. Nếu host trả slots cho **children** thì cộng/đối chiếu root riêng, không nhầm với total agents. Task tồn tại/idle không tự bằng active browser turn, nhưng vẫn có thể chiếm host slot theo runtime.

Ví dụ khi hai instance thực sự sẵn sàng và mỗi cái cap 5: instance A có coordinator + 4 children, B có 5 children = tổng 10. Đây là phân bổ hợp lệ để kiểm chứng, không ép Cockpit phải phân đúng sơ đồ này hoặc bảo đảm nhanh gấp 10. Pool config không chứng minh một task tree đã route qua cả hai instance.

**Chạy nhanh, kiểm chứng vừa đủ:** CO-04 dùng một batch ngắn có công việc/receipt thật để kiểm overlap, route và integration. Có thể thử 4 total trước, rồi tăng tới sức chứa khả dụng (tối đa 10) khi còn task độc lập; không bắt buộc đi qua mọi mức 2/4/6/8/10 hay chạy stress test dài trước mọi milestone. Với build/route chưa kiểm, batch tăng tải là experiment cách ly, chưa phải production-certified concurrency. Lưu mức đã thử và faults; đo thời gian tới **accepted output**, gồm retry/rework/merge, thay vì chọn số agent đông nhất. Không đợi hoàn tất mọi bài crash/compaction trước read-only research độc lập trong scope; vẫn phải đạt safety/acceptance gates liên quan trước tích hợp/rollout.

### 2B. Instance routing và lỗi không được làm mất ownership

- Attempt có `instance_id`/route identity khi runtime cung cấp, task/child/session locator và input/base hashes. Chỉ lưu locator không nhạy cảm; không ghi account email/token/cookie. Nếu chưa thấy route thực thì ghi `unknown`, không suy nó từ instance đang được chọn trong UI.
- Cần kiểm sticky routing hoặc cơ chế state reconstruction tương đương: các continuation/tool callbacks của cùng attempt đi đúng owner. Không round-robin mù giữa hai instance sau khi prompt đã được nhận, không chuyển in-flight attempt để né timeout/cooldown.
- Các task mới độc lập có thể được phân vào các instance user đã bật theo routing hợp lệ. Instance lỗi chỉ loại capacity đó; giữ phần đã accepted và reconcile attempt chưa rõ trước retry. Đổi instance cho một attempt chỉ sau khi owner cũ đã settle/fence, state handoff được kiểm và lỗi không phải tín hiệu hạn chế tài khoản cần dừng.
- Tôn trọng rate limit/cooldown/protection. Dừng gửi thêm tới phạm vi bị ảnh hưởng; không chuyển tải của attempt bị giới hạn sang tài khoản khác để vượt hạn chế, không đổi account/model hay tạo instance để né protection. Khi chưa rõ phạm vi ảnh hưởng, tạm ngừng fan-out liên quan và xác minh trước.
- Tách browser partitions/core homes/ports giúp cô lập session, không chứng minh hai đăng nhập là hai tài khoản/quota độc lập. User báo hai tài khoản; không đọc credentials để kiểm. CO-00 ghi phần đã xác nhận qua metadata an toàn và phần còn unknown.
- Broker account/risk scope của sản phẩm trading hoàn toàn độc lập với account chạy AI. Pool 10 không thay quyền trade, authorization hay safety gates.

### 2C. Snapshot read-only 21/09/2026, khoảng 15:56 +07

| Nguồn kiểm | Đã thấy | Chưa chứng minh |
|---|---|---|
| Local Web GPT checkout | HEAD `ac1144dd416dd0bbde8a5aaf32447a437927f21b`, clean; `src/adapters/chatgpt-web/concurrency.ts` vẫn cap 5 | Không phải benchmark 10 turns |
| Installed artifact | App 5.0.8, bundle `ff3674c87da19b243c8b7212484dc2223bdae3aae0bfc40693ba46441b6fdb25`; browser-worker guard trong `app/cli.js` vẫn cap 5 | Không chứng nhận mọi runtime process cùng cấu hình/đăng nhập |
| Launcher registry | `primary:17841` và `instance-2:17842`, đều enabled; core homes và browser partitions khác nhau | Enabled không bằng service online/auth/tools usable |
| Cockpit provider metadata/source | Có hai provider URL trên với `chatgpt-web/high`; `syncCockpitPoolRoutingRules` và launcher instance lifecycle đã có | Chưa chạy routed child calls để chứng minh balancing/affinity/capacity của một task tree |
| Health tại lần đọc | `17842`: ok, Full 5.0.8, accepting, 0 active browser turns; `17841`: connection refused | **Chưa đủ cơ sở ghi available capacity = 10 lúc kiểm**; chưa chẩn đoán/khởi động lại primary |

Registry đọc từ `C:/Users/MIIKEY/AppData/Roaming/Codex Web GPT/instances.json`; source từ `D:/ANNAM/AI/codex-chatgpt-web-cockpit`. Không đọc cookie/token hoặc gọi generation. Snapshot là evidence theo thời điểm; CO-00 phải refresh, không ghim primary là hỏng vĩnh viễn. Phần routing/health chưa đạt không làm giảm **trần PLAN 10**, chỉ giảm capacity được phép sử dụng ở thời điểm chạy.

## 3. Ownership, state và acceptance

Chỉ controller code được ghi task ledger. Child tạo candidate artifact/receipt trong scope riêng; reviewer tạo review evidence, không tự chuyển task sang accepted. Prompt không phải sandbox: còn phải giới hạn filesystem/tool capability và kiểm diff thực tế; không đưa secrets/broker vào development sandbox.

### Các record tối thiểu

| Record | Fields chính |
|---|---|
| Plan/run | plan revision/hash, policy/authorization scope, run ID, repo identity, protected paths, pool ceiling và capacity evidence revision |
| Coordinator owner | owner generation, host/process/session locator, acquired/heartbeat, current authority state |
| Task | task ID, milestone/Y/K/D IDs, dependencies và versions, acceptance spec/hash, allowed files, status |
| Attempt | attempt ID, owner generation, input hashes/base commit, assigned worktree, dispatch ID, child locator, instance/route locator hoặc unknown, timestamps, status/error |
| Candidate | paths/patch/commit + hashes, schema/version, dependency versions, provenance; missing fields không dùng mặc định permissive |
| Verification | verifier/version, exact candidate+test+input hashes, exit/results, test scope, independent expected outcomes |
| Review | findings, severity, resolution evidence; role/attempt không phải bằng chứng độc lập nếu cùng context làm sai |
| Integration intent | target ref/base, candidate revision, required checks, prepared/promotion-observed/finalized |
| Acceptance/event | exact integrated revision, checks/review decisions, owner generation, reason, sequence/time |

Không lưu token/API key/cookie trong record. Thread/child IDs giúp lookup, không thay task/attempt identity. Timestamp không là thứ tự tuyệt đối cho event giữa nhiều host.

### State machine

`planned → ready → dispatch_prepared → running → candidate → verifying → integration_pending → accepted`.

Nhánh `failed`, `blocked`, `uncertain`, `canceled`, `superseded` là explicit; chỉ controller transitions có expected prior state/revision. `accepted` không bị late response hạ ngược. Thay spec/input/dependency tạo task revision hoặc invalidate verification có ghi reason, không sửa quá khứ cho đẹp.

Accepted phải có **candidate đúng + verifier đúng scope + review bắt buộc + integrated revision đúng**. Dữ liệu/spec/fixtures sai thì tests xanh chưa đủ. `DONE`, exit=0, file tồn tại, Git merge sạch hoặc hash đúng một mình không đủ.

## 4. Vòng làm việc của coordinator

1. Đọc authoritative entrypoint, state schema/version và authorization. Discover tools/model/protocol hiện hành. Không chạy startup hooks/script chưa audit hoặc đọc secrets để lấy context.
2. Reconcile in-flight trước scheduling mới. Unknown ownership, dirty shared worktree hoặc missing evidence phải được giải quyết trong scope, không ghi đè.
3. Chọn task dependencies đã accepted ở đúng revision; ưu tiên critical path, fill capacity theo mục 2A–2B khi có ích. Read-only research có thể chạy song song với writer cách ly; shared schema/lockfiles/execution authority có owner rõ. Không tạo task giả/chia vụn chỉ để đủ 10 lượt.
4. Ghi `dispatch_prepared` transaction trước dispatch. Cấp packet gồm goal/non-goals, inputs/contracts/versions, allowed files, resource namespace, test oracle, output paths, deadline/budget và handoff format.
5. Discover native spawn/wait/followup/interrupt contracts thay vì hard-code API của một protocol. Wait/poll phải nhả resource theo tool schema đang dùng; không giữ một tool call khiến children không chạy được.
6. Thu output/receipt, controller đọc/re-hash và kiểm ownership/scope. Báo lỗi child được giữ; không nuốt stream errors thành success hoặc lặp vô hạn.
7. Chạy validators đã duyệt và reviewer fresh context theo risk. Money/auth/execution/ledger/data migration luôn cần failure/negative cases và independent oracle, không chỉ review prose.
8. Integrate trong staging ref/worktree, chạy checks **sau ghép với current base**. Nếu base/contract đã đổi, invalid receipts liên quan và revalidate thay vì cherry-pick mù.
9. Ghi acceptance cùng exact integrated revision; publish progress snapshot tại task/milestone boundary. Tiếp task khác đủ quyền, không hỏi user mọi việc nhỏ.

Được tiếp an toàn không có nghĩa được mua dịch vụ, đổi global auth/provider, public push/deploy, mở holdout, đổi dữ liệu gốc hoặc bật broker/live. Human gate theo PLAN vẫn giữ.

## 5. Retry, backpressure và degradation

- Default max **2 attempts/task trên cùng input revision**, không tính lại budget bằng đổi tên task. Cùng root cause không tiến triển thì circuit-break và ghi blocking evidence.
- Timeout/disconnect không suy ra không có side effect. Kiểm child lifecycle + artifact/worktree/process trước retry. Nếu child còn active, không dispatch trùng writer.
- Chỉ retry khi đã xác định attempt cũ ngừng hoặc đã bị tước khả năng publish; generation cũ không được controller accept. Child cũ còn ghi trong sandbox riêng có thể quarantine, không được merge.
- Failure một task không hủy phần accepted; tiếp nhiệm vụ độc lập khi không vi phạm dependencies/risk. Giảm concurrency ở instance/lane bị lỗi trước; chỉ giảm toàn pool khi lỗi chung hoặc chưa xác minh được phạm vi. Serial là degraded mode, không mặc định lâu dài.
- Pool dispatch task mới theo routing đã được user bật không phải model/provider fallback. Không automatic fallback ngoài pool, không đổi quyền/model, restart bridge, tạo account/profile hoặc reroute attempt chưa rõ kết quả để “cứu task”; tôn trọng protection theo mục 2B.
- Slot thu hồi dựa lifecycle thực; `wait` timeout không có nghĩa child đã tắt. Tính root/control reserve theo mục 2A, không để workers chiếm slot cần cho collect/recover. Test/backtest CPU/RAM jobs có budget riêng, không tự tăng thành 10 compute jobs vì có 10 browser slots.
- Trước compaction/turn dài: ghi progress và receipt tới boundary gần nhất, giảm context bằng references/hashes; không dựa compaction summary bảo toàn authority/ownership.

## 6. Phục hồi khi coordinator mới bắt đầu

| Tình huống | Hành động bắt buộc |
|---|---|
| Task đã accepted, artifacts/checks còn khớp | Giữ accepted; không rerun chỉ vì chat mới |
| Ledger accepted nhưng hash/revision lệch | Quarantine/needs-verification; không tự regenerate expected |
| Dispatch prepared, chưa có receipt | Tra cứu child/process/artifact bằng IDs; unknown thì chưa redispatch |
| File đã xuất nhưng chưa verified | Candidate/uncertain, không accepted |
| Child cũ còn sống | Theo dõi/takeover trong scope hoặc chờ; không dispatch cùng write namespace |
| Old coordinator còn active | Không lấy quyền vì heartbeat cũ; stop takeover, kiểm exact owner/OS lock; user chỉ cần can thiệp nếu thật sự không xác minh được |
| Coordinator cũ chết sau Git promotion trước ledger finalize | Đọc integration intent và current ref: candidate đúng thì finalize sau check; base cũ thì tiếp bước an toàn; ref khác thì reconcile, không merge lại |
| JSON export ghi cụt | DB còn đúng thì dựng lại read-model; DB mất/hỏng thì phục hồi backup đã verify, không import partial snapshot |
| State/DB mới restore từ backup cũ | Quét actual refs/candidate receipts/owners trước dispatch; stale snapshot không là quyền làm lại action |
| Tool/protocol/build thay đổi | Re-run capability preflight liên quan, giữ completed product evidence đúng revision; không reuse turn tokens |
| Không có runtime/provider hoạt động | Persist blocker/progress khi còn có thể; không hứa tự resurrection |

Coordinator ownership phải có cơ chế loại trừ và compare-and-set generation; lease TTL chỉ là tín hiệu kiểm tra, không chứng minh old process chết. Tool/action ngoài DB không tự exactly-once. Chính vì vậy có `uncertain` và integration-intent reconciliation.

## 7. Git/CI, review và context tối thiểu

- Một task packet không chứa toàn bộ chat. Sources: mục tiêu/constraints, relevant contracts, knowledge K IDs, task dependencies và acceptance cases.
- Writer không sửa verifier/expected outputs để pass; thay oracle cần review semantics và task riêng. Reviewer đọc contract+diff+test evidence trước author narrative.
- Coordinator sở hữu shared schema/dependency locks/migration numbering; feature children không tự thêm framework/fallback song song.
- Worktree không chia sẻ temp DB/ports, broker creds hoặc writable app state. Shared read-only fixture cần hash pinned; mutation làm invalidate tất cả candidates dùng fixture đó.
- Fast checks cho mỗi candidate; integration checks trước acceptance; heavier fault/performance/restore checks tại milestone. Không full suite cho mỗi sửa chữ, không bỏ tests tiền/quyền vì quota.
- Throughput-first không phải “đợi cuối project mới test”: focused checks ngay ở task/contract boundary, review sâu và debugging tích hợp theo milestone; cosmetic/low-risk polish có thể gom cuối. Khi không cần reviewer riêng cho lát ít rủi ro, coordinator có thể review để giảm dispatch/context overhead.
- Archive receipt gồm plan/task/attempt + integrated commit + actual test result. `PROGRESS.md` sinh từ ledger; Git history giữ code, ledger giữ coordination, receipt nối hai thứ.
- Product-specific AGENTS/skill/hook nếu cần tạo khi triển khai phải theo `ai-environment-maintainer` và audit; không sửa global instructions trong planning turn này.

## 8. Các task validation nối tiếp, do một coordinator tự quản

| ID | Scope | Phụ thuộc | Gate |
|---|---|---|---|
| CO-00 | Pin plan/build/spec/authority và scope; refresh instance inventory/health, per-instance cap, host slots, pool route metadata; import historical receipts read-only | User giao validation entrypoint | Phân biệt trần 10, configured capacity và usable capacity; không claim pool/child capability từ registry hoặc specialist-complete |
| CO-01 | Prototype local controller ledger + schema + claim/accept/integration intent API trên fixture | CO-00 | Unique/CAS/atomicity tests, child không own authoritative state |
| CO-02 | Failure and recovery: prepared dispatch, late results, controller interruption, torn export, stale snapshot, promotion-before-finalize | CO-01 | Không double-dispatch/promote/accept; phần accepted được giữ; tests kiểm actual implementation, không `Sort-Object` demo |
| CO-03 | Native Web GPT capability + one-child loop, independent verifier/reviewer | CO-00/01 | Actual tools/artifacts accepted đúng protocol; ghi limits/errors |
| CO-04 | Batch overlap/integration thật; routing/affinity qua hai instance nếu available; tăng tải tới trần tổng 10 khi có lợi; một lane unavailable/uncertain trên fixture | CO-00/01/03; có thể chạy song song CO-02 trên namespace khác | Ghi mức thực sự thử, per-instance attribution, accepted-output time/rework; không vượt host/per-instance cap, không dispatch trùng/cross-talk. Nếu mới thử được mức thấp thì cap 10 vẫn giữ, capacity 10 chưa VERIFIED; không chặn phần việc dùng mức đã đạt |
| CO-05 | Fresh coordinator từ files, same-thread/compaction phân loại riêng, resource cleanup | CO-02/03 | New-root proof nếu khả dụng an toàn; thiếu thì ghi conditional và giữ human restart gate |
| CO-06 | Dùng workflow đã kiểm chạy F1–F3 validation packets và trình F5 evidence | CO-02/03, các F dependencies | Không nhảy sang F6 trước approved decision |

CO-00…06 đã có accepted attempts trong run revision 144; **acceptance có giới hạn**, không toàn runtime COMPLETE. Không rerun tất cả để đồng bộ một câu trạng thái cũ. Giữ CO-04 native parallel/pool và CO-05 fresh-root/compaction là capability còn thiếu; không bắt đủ 10 mới làm FH/product trong scope. Không ngầm launch agents trong lượt Astra viết plan.

## 9. Acceptance và output cho người dùng

Mỗi update ngắn: `milestone/scope revision · accepted x/y · running · blocked · next`; thêm `ceiling / usable / active` và phân bổ instance khi capacity thay đổi. Chỉ có mẫu số task khi task graph/version đã freeze. Nêu ngoại lệ một lần có next action, không spam polling.

Definition of done cho orchestration: CO02/03/05 evidence đủ trong fault model; integrated fixture acceptance; output/state/recovery readable; scope limitations rõ. Parallel readiness là dòng riêng CO04. Product F5/U và broker/live readiness vẫn dòng riêng, không cộng tất cả thành “plan complete”.
