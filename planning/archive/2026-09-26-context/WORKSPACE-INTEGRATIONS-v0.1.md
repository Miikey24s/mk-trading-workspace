# Kết nối ứng dụng và nhiều project — research cho giai đoạn hậu-PLAN

**v0.1 · 26/09/2026 · ĐANG LẬP KẾ HOẠCH / DRAFT / CHƯA DUYỆT TRIỂN KHAI.**

## 0. Kết luận ngắn và phạm vi

Đề xuất: **mỗi project tiếp tục sở hữu nghiệp vụ và dữ liệu của nó; dùng một lớp kết nối nhỏ để phối hợp workflow. MCP phục vụ AI thao tác; API/jobs phục vụ automation lặp lại.** Không gộp MT5 và VI Dubber thành một backend/database, không xây một hệ điều phối AI mới, không bắt mọi việc đi qua LLM.

Đây là research cho giai đoạn sau khi các PLAN hiện hành được nghiệm thu đúng phạm vi. Không sửa code sản phẩm, operational ledger, PLAN của hai worker, cấu hình, tài khoản, credentials hoặc quyền; không cài/kết nối dịch vụ, gửi tin, upload dữ liệu hay triển khai hạ tầng.

Nguồn nội bộ đã đối chiếu:

- [Product Plan MT5 v2.2](mt5-tradingview-backtester/PRODUCT-COMPLETION-PLAN.md), đặc biệt U2/U3/U7/U8/U9 và Y13/Y16/Y24.
- [PLAN tổng MT5, mục 5.5](mt5-tradingview-backtester/PLAN.md): giảm trùng lặp ứng dụng; không thêm Notion chỉ để đủ công cụ.
- [Roadmap hậu-PLAN đang draft](mt5-tradingview-backtester/POST-COMPLETION-ROADMAP-DRAFT.md): mở rộng research/portfolio/automation; không research lại PATH-2.
- [Research tích hợp cũ](mt5-tradingview-backtester/PRODUCT-RESEARCH-AND-INTEGRATIONS.md): giữ adapter, tách execution authority.
- [VI Dubber PLAN](../projects/vi-dubber/PLAN.md) và [README](../projects/vi-dubber/README.md): media pipeline, artifacts, resume, QA, runtime dịch riêng. Header PLAN là snapshot, không tự thay evidence mới.
- Đã đọc hai task người dùng chỉ định: [Tiếp tục plan MT5 trading](codex://threads/01a0db89-2066-7653-b35c-499f382dcf38) và [Tiếp tục thread Codex](codex://threads/01a0db78-2732-7510-9db4-9163798f8db2). Cả hai đang hoạt động tại lúc đọc; một bên xử lý MT5/research/Prop, bên kia VI Dubber/preview/autotune. Không coi đây là final acceptance, không gửi chỉ đạo mới cho họ.

Phương pháp: đọc kế hoạch và trạng thái task; kiểm tra catalog plugin; đối chiếu tài liệu chính thức/upstream. **Chưa benchmark connector, chưa gọi API tài khoản thật, chưa chứng minh tích hợp end-to-end.** Ranking là đánh giá phù hợp nhu cầu, không phải thống kê thị phần hay số người sử dụng.

## 1. Already covered / Partially covered / Missing

“Covered” dưới đây là **PLAN đã có yêu cầu**, không phải code đã nghiệm thu.

| Mức | Đã có trong kế hoạch | Việc còn cần cho nhánh này |
|---|---|---|
| Already covered | PATH-2, data provenance, quyền, broker guards, jobs/recovery, review | Reuse; không đổi nền hoặc mở lại research foundation |
| Already covered | Playbook, Journal, Learn nền; export; AI provider/MCP boundary U7 | Dùng các service đã có, không tạo journal/metrics/learn tracker thứ hai |
| Already covered | Figma/Miro/UI workflow và agent UI acceptance | Không thêm bản sao cùng nội dung vào mọi công cụ |
| Already covered | VI Dubber nhận media, dịch/lồng tiếng, QA/artifacts/resume | Giữ workflow riêng; machine QA không thay listening gate còn tồn tại |
| Partially covered | Provider thay được, API/MCP có quyền | Chưa là bộ connector Notion/Drive/Calendar được kiểm chứng |
| Partially covered | Multi-user, observability, dữ liệu phiên bản | Cần áp dụng identity/scope/trace sang ranh giới giữa các project |
| Missing | MT5 Learn nhận kết quả từ VI Dubber | Asset/course-item contract, deep link, version, lỗi và sửa bản dịch |
| Missing | Đồng bộ báo cáo/tài liệu sang SaaS | Mapping IDs, quyền ghi từng trường, chống trùng, refresh/reconcile, revoke/delete |
| Missing | Một nơi nhìn các công việc liên project | Bảng trạng thái đọc từ hệ thống gốc; không thay ledger của từng project |
| Missing | Hồ sơ connector và nghiệm thu vận hành | Owner, quyền, chi phí, giới hạn, auth, health, retries, rollback, exit/export |

## 2. Ba loại kết nối khác nhau

| Loại | Ví dụ | Cách đề xuất | Không nên hiểu nhầm |
|---|---|---|---|
| AI dùng app | “Tìm ghi chú Notion và tạo bản nháp tổng kết” | Plugin/MCP chính thức, quyền có phạm vi | Cài plugin cho coding agent không tự tích hợp vào sản phẩm |
| Sản phẩm dùng dịch vụ | Run xong thì xuất báo cáo, lưu link, nhắc lịch | API/SDK chính thức + job có trạng thái; có thể orchestration qua n8n | Không cần LLM suy nghĩ cho mỗi thao tác đã có luật rõ |
| Project dùng capability của project khác | MT5 mở video VI Dubber đã xử lý | API/action contract + artifact reference + status | Không import trực tiếp toàn source hoặc sửa database của nhau |

MCP chuẩn hóa giao tiếp với tools; không thay scheduler, database, identity, retry policy hay quyền nghiệp vụ. Một MCP headless vẫn có thể dùng cho automation nếu auth/capability phù hợp; **không cấm MCP**, nhưng lựa chọn cho từng workflow phải dựa vào hành vi đã kiểm chứng.

Catalog plugin hiện báo Google Drive và Google Calendar `installed=true`; Notion, GitHub và Slack `installed=false`. Đây chỉ là trạng thái cài trong catalog, **không chứng minh OAuth còn hiệu lực, đúng tài khoản, đủ quyền hoặc sản phẩm đã nối được**. Chưa đọc dữ liệu riêng của các tài khoản. Không cần cài thêm để hoàn tất lượt research này.

## 3. Nên kết nối gì trước?

| Hạng đề xuất | App/capability | Công việc có ích | Ưu điểm | Chi phí/rủi ro và giới hạn |
|---|---|---|---|---|
| 1 | **Notion** | Thư viện kiến thức, research briefs, index nhiều project, weekly review | Dễ đọc/sửa, một nơi tổng hợp | Không là nguồn số tiền, task ledger của agent hay kho tick; đồng bộ một chiều trước |
| 2 | **Google Drive + Docs/Sheets** | Nhận video/tài liệu được chọn, lưu report/subtitle/export để dùng trên máy khác | Phù hợp trao đổi và chia sẻ file | Quota/quyền/share links; không đồng bộ thư mục DB đang chạy; Sheets chỉ là bản xuất, không tính lại P/L làm nguồn gốc |
| 3 | **Google Calendar** | Hẹn học, review tuần, nhắc mốc research | Có ích mà không cần thêm một UI lịch | Calendar cá nhân khác economic-news calendar U2; dùng lịch riêng, không đụng toàn bộ lịch cá nhân |
| 4 | **Một kênh thông báo** | Báo render xong, research lỗi, cần xử lý | Không phải ngồi canh app | Chọn kênh đang dùng; không cài đồng thời Slack/Discord/Telegram. V1 gửi link/tóm tắt, không nhận lệnh trade từ chat |
| 5 | **GitHub** | Nối bug/report tới issue/PR/CI, xem trạng thái release | Evidence gần code | Dùng CLI sẵn có nếu đủ; không cần MCP chỉ vì có integration. Không tạo tracker cạnh tranh với plan/ledger |
| 6 | **Figma/Miro** | Design system/bản đồ kiến trúc có link về bản nguồn | Đã phù hợp workflow đang có | Reuse kế hoạch UI hiện tại; không research/xây lại trong nhánh này |
| Sau | **Email, RSS, Zotero/nguồn nghiên cứu** | Thu thập tài liệu, tổng hợp research inbox | Có thể giảm công nhập | Chỉ nhận khi có workflow thật; email tăng PII/injection risk. Chưa audit từng connector |
| Theo nhu cầu | **Linear/Jira/CRM/công cụ team** | Điều phối nhiều người thực | Hợp khi có team/vận hành tương ứng | Chưa có lý do để thêm cả Notion + GitHub Projects + Linear/Jira ngay |

Đây là thứ tự lựa chọn cho người dùng này, không khẳng định ai chuyên nghiệp cũng dùng đúng bộ app trên. Có thể bỏ Notion nếu cuối cùng người dùng không đọc nó: native workspace + Markdown/report vẫn hoạt động.

### Notion Education/“Edu Plus”: được gì, không được gì?

| Nội dung | Theo tài liệu Education ngày 26/09/2026 |
|---|---|
| Cá nhân đủ điều kiện | Miễn phí; 1 member, tối đa 100 guests |
| Nội dung | Pages/blocks và uploads không giới hạn số lượng; history 30 ngày |
| Duy trì | Trường được công nhận; email trường là email chính; xác minh mỗi năm |
| Hết điều kiện | Chuyển Free; không thiết kế hệ thống phụ thuộc ưu đãi tồn tại mãi |

Nguồn: [Notion Education](https://www.notion.com/help/notion-for-education). Gói student organization là chương trình riêng, không tự suy áp dụng cho nhóm/project thương mại. Chưa kiểm entitlement của tài khoản người dùng.

**AI là mục riêng:** pricing hiện ghi Plus có AI trial, không phải AI đầy đủ; upload còn giới hạn kích thước từng file. [Notion pricing](https://www.notion.com/pricing). AI Connectors vào các app thường cần Business/Enterprise; tài liệu nêu ngoại lệ Gmail personal. [Notion AI Connectors](https://www.notion.com/help/notion-ai-connectors). Không suy quyền này từ việc có Edu hoặc dùng MCP.

Phân biệt: **AI bên ngoài đọc/ghi Notion bằng MCP/API** khác **mua AI của Notion để đọc các dịch vụ khác**. Chưa có lý do mua AI Notion chỉ để lưu/tìm tài liệu cho agent hiện có.

Notion hosted MCP dùng OAuth, làm việc với nội dung user có quyền; tài liệu hiện yêu cầu authorization tương tác, không hỗ trợ khởi tạo auth hoàn toàn headless. Package MCP local cũ được ghi không còn actively maintained. Chọn hosted MCP cho agent; automation nền cân nhắc Notion API connection riêng có scope phù hợp. Không giả OAuth một lần = hoạt động vĩnh viễn. [Notion MCP](https://developers.notion.com/guides/mcp/overview), [connection/auth và tình trạng package](https://developers.notion.com/guides/mcp/get-started-with-mcp).

## 4. Liên kết MT5 + VI Dubber mà không làm hai app phụ thuộc chặt

Đề xuất chuyên môn cho hệ thống này: **gắn kết theo capability**, không theo bảng dữ liệu hoặc folder source. Tư duy boundary theo nghiệp vụ được mô tả trong [Microsoft domain analysis](https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis); điều đó không buộc triển khai thành hàng chục microservice.

### Ba workflow đầu tiên

| Workflow | Luồng dữ liệu | Ai là chủ dữ liệu? | Giới hạn |
|---|---|---|---|
| **Video → thư viện học** | Chọn media có quyền → VI Dubber xử lý → QA status + manifest → Learn/index nhận link transcript, subtitle, video và time anchors | Dubber giữ job/media; Learn giữ course item/tiến độ theo protocol | Dịch xong không tự đánh dấu đã học hoặc chấp nhận nội dung là đúng |
| **Research → báo cáo** | MT5 chốt run/report → connector xuất snapshot lên Drive → Notion nhận tóm tắt + link run/version | MT5 giữ metrics/run; Drive giữ bản xuất; Notion giữ trang đọc | AI tóm tắt không tự tính lại con số; provider lỗi không làm run thất bại |
| **Review định kỳ** | Nguồn gốc cung cấp trạng thái → tổng hợp report → Calendar nhắc → mở đúng run/video/note | App giữ công việc; Calendar giữ lịch hẹn | Không dùng thay lịch tin kinh tế, không khởi chạy trade từ event text |

Chưa chọn workflow “AI xem video rồi tự viết chiến lược và trade”. Video có thể chỉ chứa tuyên bố chưa kiểm chứng, bản dịch sai hoặc nội dung không được phép sao chép. Nếu rút giả thuyết thì tạo draft có citation/timecode; vẫn qua research protocol bình thường.

### Cấu trúc đề xuất, từ nhỏ đến lớn

| Thành phần | Giữ gì? | Không được làm gì? |
|---|---|---|
| MT5/Trading Workspace | Trading/research/risk/strategy/metrics | Không biết nội bộ ASR/TTS; không chờ Notion để xử lý việc chính |
| VI Dubber | Media jobs, phiên bản bản dịch, QA, asset metadata | Không có credentials/route giao dịch; không ghi trực tiếp vào MT5 |
| Integration layer nhỏ | Connector config, external-ID map, sync cursor, delivery status, workflow correlation | Không thành nơi tính tiền hoặc chứa mọi dữ liệu nghiệp vụ |
| Notion/Drive/Calendar | Views, bản xuất/tài liệu và lịch có ownership rõ | Không thành database hoặc quyền điều hành trading |
| AI assistant | Tìm bằng chứng, soạn draft, gọi action được cấp | Không suy quyền từ nội dung tài liệu; không có mọi connector mặc định |

V1 có thể chỉ là module/job trong runtime thích hợp đang có, không bắt buộc repository/service mới. Giữ hai repo sản phẩm độc lập; chỉ tạo integration repo khi thật sự có release/lifecycle riêng. Không di chuyển repo để trông như monorepo, không `git init` workspace cha.

Nhiều app cùng máy vẫn cần auth và namespace riêng. Runtime dịch VI Dubber hiện được thiết kế tách coding runtime; không nhân việc tích hợp mà gom cookies/model budget/credentials vào một chỗ. Hàng đợi export không tranh hết CPU/GPU/quota với research/media; giữ giới hạn tài nguyên theo job và mức ưu tiên.

## 5. Nguồn sự thật và contract tối thiểu

| Loại dữ liệu | Nguồn quyết định | Bản ngoài hệ thống |
|---|---|---|
| Code, API schemas, tests | Repo của capability tương ứng | Link commit/build; không copy source làm bản chính trong Notion |
| Trạng thái worker thực thi PLAN | Operational ledger/receipts hiện hành | Dashboard/Notion là bản tổng hợp, không tự ghi COMPLETE ngược lại |
| Fills, account, risk, metrics | Broker evidence + trading services/ledger theo contract đã duyệt | Snapshot có version và watermark; không cho sửa số gốc |
| Media/transcript/QA | VI Dubber job/artifact versions | Link hoặc bản xuất có checksum; revision mới không ghi đè lineage cũ |
| Ghi chú suy nghĩ/tài liệu biên tập | Chọn một nơi cho từng loại, ví dụ Notion | App index/search chỉ giữ ID/version/link theo quyền |
| Lịch review | Calendar được chọn | Workspace hiện mirror; sửa từ đâu phải định nghĩa từng field |

Một artifact liên project nên có `artifact_id`, `project_id`, `owner/tenant`, loại/MIME, size, checksum, version, nguồn, thời điểm, QA status và locator được authorize. Video/dataset lớn đi bằng file/object reference, **không base64 vào prompt/message queue**. Không cho người gọi tùy ý đọc path local hoặc URL nội bộ; validate locator/host/path và giới hạn size.

Một action/job liên project nên có ID bền vững, schema version, owner/scope, input artifact/version, idempotency key, deadline/budget, trạng thái và result/error reference. Status/cancel/progress phải rõ; `cancel_requested` không giả bằng `cancelled`.

Một event nên có `event_id`, `event_type`, `schema_version`, nguồn/project, entity ID/revision, `occurred_at`, `correlation_id`, actor và references tối thiểu. Identity phải lấy từ session/credential đã xác thực, không tin `tenant_id` do client gõ. Đây là contract đề xuất để map với nền đã có, không lệnh tạo một framework event chung từ đầu.

MCP tools phía workspace nếu thực sự cần: `find_artifacts`, `read_report`, `request_dub`, `get_job_status`, `draft_review`. Tools theo nhiệm vụ; tránh `execute_anything`, SQL tùy ý, unrestricted filesystem. Đây là tên minh họa chưa implement. MCP/UI/CLI/API dùng cùng application service và permissions, không tạo đường tắt.

## 6. Automation: mua/dùng cái có sẵn hay tự build?

| Lựa chọn | Ưu điểm | Nhược điểm | Khuyến nghị |
|---|---|---|---|
| **API/SDK + job nhỏ trong nền hiện có** | Ít hệ thống mới; test/version gần code; AI worker dễ review diff | Phải viết mapping và error handling | **Mặc định cho 1–3 workflow ổn định đầu tiên**; con số là phạm vi thử, không giới hạn kiến trúc |
| **n8n** | Workflow trực quan, nhiều adapter, chạy ngoài app chính | Thêm vận hành, secrets, upgrades, giấy phép; workflow vẫn cần tests | Ứng viên số 1 khi nhu cầu SaaS tăng và thường xuyên đổi luồng |
| **Make hoặc SaaS automation tương tự** | Bớt quản lý máy chủ, dễ thử luồng | Dữ liệu qua bên thứ ba, phí và semantics phụ thuộc gói | Cân nhắc nếu tiết kiệm vận hành quan trọng hơn self-host; chưa audit giá/connector hoặc thử head-to-head |
| **Temporal** | Có durable workflow/history/recovery cho chuỗi dài | Thêm platform, học semantics và vận hành | Hoãn; chỉ thử khi workload liên project vượt khả năng jobs/recovery hiện có |
| **AI agent cho tất cả thao tác** | Linh hoạt khi đầu vào mơ hồ | Tốn inference, khó dự đoán/replay, có thể chọn sai hành động | Không dùng làm mặc định cho thao tác deterministic |

Theo [license n8n](https://github.com/n8n-io/n8n/blob/master/LICENSE.md), không được coi nó là MIT/Apache dùng thương mại theo mọi cách; personal/internal khác việc nhúng hay bán dịch vụ cho người khác. [Queue mode](https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/enable-queue-mode.md) có Redis/workers/database: không cần bật chỉ để nối hai app.

[Temporal workflow execution](https://docs.temporal.io/workflow-execution) có cơ chế phục hồi theo history; không từ đó suy mọi side effect SaaS đạt exactly-once. [Make blueprints](https://help.make.com/blueprints) là điểm khảo sát export workflow, chưa chứng minh migration không tốn công.

**Chia việc:** thư viện chính thức xử lý API/auth; hệ thống của mình định nghĩa ownership/quyền/data contracts; orchestration tool nối các bước ngoài đường trading. Không tự viết một “n8n mini” có canvas/plugin marketplace. Không đưa FFmpeg/ASR hoặc backtest engine vào code node của automation tool.

## 7. Failure/recovery và bảo mật: chuẩn vừa đủ

Các hàng dưới là acceptance đề xuất, không phải capability đã có:

| Tình huống | Hành vi cần có |
|---|---|
| Run lưu xong nhưng app crash trước khi xuất báo cáo | Lưu ý định export bền vững cùng commit nghiệp vụ nếu có transaction; worker gửi sau. Nếu nguồn chỉ có artifact files, atomic manifest + reconciliation thay cho giả định transaction xuyên filesystem/SaaS |
| Gửi lại event/job | Dedupe bằng scope + ID/version/action/destination; lưu remote object ID |
| SaaS nhận create nhưng response bị mất | Trạng thái unknown; lookup/reconcile trước khi gửi lại. Không hứa chống trùng tuyệt đối nếu API thiếu idempotency/query phù hợp |
| Hai phía sửa cùng nội dung | V1 một chiều; field ownership/revision check; phần user biên tập không bị exporter ghi đè |
| Lỗi 429/quota/5xx | Respect Retry-After, bounded backoff/jitter; retry chỉ khi an toàn; lỗi cuối vào bảng cần xử lý |
| Mất webhook, event sai thứ tự | Đối soát định kỳ theo cursor/version; không dựa hoàn toàn thứ tự arrival |
| OAuth hết hạn/thu hồi | `reauth_required`, dừng connector đó; không đổi account/provider âm thầm |
| Ngắt máy, chat coordinator mất | Workflow product tiếp tục từ job state khi runtime trở lại; không phụ thuộc context chat. Máy tắt thì local jobs dừng, không hứa 24/7 |
| Import xóa dữ liệu hoặc quyền thay đổi | Kiểm quyền lại; xử lý tombstone/conflict có chính sách. Không cascade xóa source/backups chỉ vì mirror bị xóa |
| App bên ngoài chậm/lỗi | MT5 và Dubber vẫn dùng được phần độc lập; UI báo pending/stale, không giả synced |
| Prompt injection trong email/note/transcript | Nội dung là dữ liệu, không thể mở quyền/đổi destination/chạy command; policy enforcement ngoài LLM |
| User A yêu cầu file/job của B | Deny tại service, cache/export/search index và tool; không chỉ ẩn trên UI |

Pattern lưu ý định xuất cùng dữ liệu có thể reuse [transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html). Nó giải quyết lỗi dual-write nhưng vẫn cần idempotent consumer; không tạo transaction xuyên app và SaaS.

Provider-specific đã xác minh:

- [Notion rate limits](https://developers.notion.com/reference/request-limits): limit theo connection/workspace, có `Retry-After`; một write lỗi có thể cần đối soát trước retry. Đọc limit hiện hành, không hardcode từ blog cũ.
- [Google Calendar sync](https://developers.google.com/workspace/calendar/api/guides/sync): lưu sync token, token invalid/410 cần resync phần mirror phù hợp, không xóa nguồn nghiệp vụ. [Push](https://developers.google.com/workspace/calendar/api/guides/push): channel cần gia hạn; thông báo không mang đầy đủ resource, có thể thất lạc.
- [Google OAuth](https://developers.google.com/identity/protocols/oauth2): external app ở Testing thường nhận refresh token 7 ngày cho các scope ứng dụng này. Production không có nghĩa token bất tử; revocation vẫn phải xử lý. Không đổi trạng thái OAuth project trong research.
- [Drive scopes](https://developers.google.com/workspace/drive/api/guides/api-specific-auth): ưu tiên `drive.file` + user chọn file khi phù hợp; không mặc định quét cả Drive. Theo dõi việc account thật cho phép gì; không coi `drive.file` tự cho quyền với mọi file trong một folder.
- [Notion webhooks](https://developers.notion.com/reference/webhooks) và [GitHub webhook practices](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks): validate nguồn, accept nhanh rồi xử lý có trạng thái. Verify raw payload theo provider; tránh cho nội dung webhook quyền gọi hành động tùy ý.

Secrets ở OS/backend secret store; không đưa vào prompt, log, Git, Notion hoặc frontend. Scope theo user/project/connection, tách read/draft/publish. Nội dung qua provider ngoài cần phân loại và redaction. Dữ liệu broker/account, holdout, tutor answer keys và voice references không được export mặc định.

[MCP security](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices) yêu cầu kiểm token/audience và cấm token passthrough theo kiểu chuyển bừa bearer token xuống dịch vụ khác. [Notion MCP security](https://developers.notion.com/guides/mcp/mcp-security-best-practices) cũng lưu ý prompt injection và việc client có thể gửi nội dung ra ngoài Notion. Tự chủ agent không đồng nghĩa mọi write/share được phép.

**Giảm micromanagement:** khi triển khai, owner cấp policy một lần cho từng workflow: được xuất loại gì, tới folder/database/calendar nào, budget nào, không được gì. Agent được tự chạy việc thấp rủi ro trong policy; ngoại lệ tiền, public share, credentials, chi phí mới, xóa dữ liệu và mở quyền vẫn cần quyết định riêng.

Local V1 ưu tiên outbound calls/polling có giới hạn; không public tunnel vào MT5 terminal để nhận webhook. Khi thật sự cần always-on, có thể dùng relay/cloud worker tối thiểu cho metadata với local worker kéo job đã authorize. Không expose broker/desktop vì lý do tiện webhook.

## 8. UI, debug và đo hiệu quả

Không cần thêm “siêu dashboard” ngay. Bổ sung trong Cài đặt/Connections và những hành trình đang dùng:

- Thấy rõ provider, account/workspace, quyền, destination, last sync, pending/failed/reauth và revoke.
- Chọn “Mở transcript”, “Xem bản dịch”, “Xuất báo cáo”, “Lên lịch review” ngay đúng run/video.
- Mọi bản mirror có link nguồn + thời điểm/version; báo cáo thiếu data giữ nhãn thiếu.
- Có danh sách lỗi cần xử lý và retry đúng bước, không nút “chạy lại toàn bộ” làm render/trade/export trùng.
- Dùng pattern UI/design system và Playwright-first QA đã chuẩn bị; UI autonomy không mở quyền publish/connect.

Correlation ID xuyên project, structured logs và trace giúp trả lời “report này từ run nào, mắc ở đâu”. Reuse [OpenTelemetry context propagation](https://opentelemetry.io/docs/concepts/context-propagation/) khi cần instrumentation; đừng đưa PII/token vào trace baggage.

Đo trên cùng workload trước/sau: thời gian thao tác của user, thời gian tới kết quả đúng, số bản trùng/sai scope, sync lag, số lần phải sửa tay, recovery sau crash, số API calls/inference, bandwidth, storage và thời gian bảo trì. Chưa có số liệu tiết kiệm token hoặc SLA; không tự cam kết phần trăm.

## 9. Thử nghiệm trước khi chốt implementation plan

Chỉ chạy khi được giao execution và có quyền phù hợp. Không thử tài khoản/dữ liệu thật trong lượt research này.

| ID | Thử nghiệm | Tiêu chí quyết định |
|---|---|---|
| E1 | Một report synthetic → Notion + Drive, chạy lại cùng ID/version, mô phỏng lost response | Đúng destination, không ghi đè note user, reconcile ambiguity; ghi khả năng chống trùng thực của từng API |
| E2 | Một video có quyền → Dubber artifacts → Learn/index, sửa transcript rồi resume | Stable ID/version/time anchors; stale preview không thành bản cuối; sửa một phần không chạy lại vô ích |
| E3 | Lịch review trên calendar thử riêng | Đúng Asia/Saigon; test DST nếu timezone khác; update/cancel đúng event; không invite người khác |
| E4 | Sai tenant/destination, malicious note, token revoke, missing file, 429, outage | Deny đúng chỗ; app chính còn hoạt động; không leak hoặc silent fallback |
| E5 | Kill/restart worker tại trước/sau external write và trước lưu receipt | Resume từ state, lookup khi unknown; không giả exactly-once |
| E6 | Native API job so với n8n trên cùng hai workflow | So effort, debug, tests, recovery, runtime overhead và upkeep; không benchmark chỉ tốc độ HTTP |
| E7 | Export/restore và chuyển provider | Đọc được artifact/manifest khi disconnect SaaS; backup restore được, không chỉ thấy file trên Drive |

## 10. Lộ trình đề xuất sau nghiệm thu hiện tại

| Mốc | Kết quả | Dependencies / song song |
|---|---|---|
| I0 — chốt use case/quyền | Chọn 2–3 workflow, map capability accepted thật, sources/owner/contract | Đọc acceptance cuối của hai worker; không yêu cầu họ dừng để theo research này |
| I1 — nối tri thức | E2: Dubber → Learn/index; Notion chỉ là view/notes tùy chọn | Cần media/learn contract ổn; không cần Calendar hoặc broker |
| I2 — report outbound | E1: MT5 report → Drive/Notion; receipts, retry/reconcile | Làm song song I1 sau freeze envelope/identity/artifact contract |
| I3 — lịch/thông báo | E3, một kênh alert, policy định trước | Reuse delivery status; không sửa pipeline domain |
| I4 — tích hợp/khôi phục | E4/E5/E7, tests UI, independent review, runbook ngắn | Một integration owner ghép; contract changes qua review chung |
| I5 — tăng sức khi có bottleneck | E6 n8n; nhiều máy/relay; federated search theo nhu cầu | Chỉ adopt khi tốt hơn baseline; không tự mở lại foundation |

Mỗi packet tương lai có allowed files, owner, contract version, fixture, negative cases, acceptance/rollback. Hai repo có thể làm song song, nhưng bên sửa shared contract chỉ có một owner tại một thời điểm. Consumer tests kiểm tương thích version N/N-1 theo policy, không đồng loạt ép update mọi project.

Coding coordinator/ledger hiện có quản việc xây phần mềm; **không dùng ledger của coding agent làm runtime state cho workflow sản phẩm**. Có thể reuse thư viện/pattern đã kiểm chứng, nhưng state/authority riêng. Chat mới đọc checkpoint tiếp được; không mở thêm một “AI company framework” chỉ để nối app.

## 11. Phản biện và các quyết định chưa chốt

| Ý tưởng | Phản biện / phương án phù hợp hơn |
|---|---|
| Có MCP thì kết nối hết | Thêm quyền, surface lỗi và data egress; chỉ bật tools cho workflow cần |
| Dùng Notion quản lý toàn bộ hệ thống | Hợp tri thức/tổng quan, không hợp price data/trading/job authority |
| Tự động đồng bộ hai chiều mọi thứ | Khó ownership/conflict/delete; một chiều trước, hai chiều theo từng field khi có nhu cầu |
| Gộp project để reuse nhanh | Dễ buộc deploy/dependencies đi cùng nhau; giữ contract sạch, share phần thật sự chung |
| Tạo core chung cho tất cả từ đầu | Dễ thành nút thắt; chỉ tách library khi ít nhất hai consumer có nhu cầu trùng thật |
| Đợi cuối cùng mới xử lý security/recovery | Có thể đã lộ dữ liệu hoặc tạo trùng side effect; test lỗi tại connector ngay từ lát đầu |
| Drive sync là backup | Đồng bộ có thể lan cả xóa/sửa; cần bản backup/versioned + restore test độc lập |
| Vì nhiều project nên phải Kubernetes/Kafka/Temporal | Số project không đủ để chứng minh nhu cầu; cần workload/bottleneck cụ thể |

Chưa biết: entitlement/account Notion thực; Drive quota và dữ liệu nào cho phép upload; lịch/kênh thông báo người dùng thực sự dùng; nhu cầu always-on; phạm vi nhiều user/commercial; ngân sách dịch vụ. Không cần chặn research vì các câu này. Trước execution mới resolve những câu ảnh hưởng quyền/chi phí/phạm vi.

**Đề xuất chốt cho vòng thảo luận:** giữ MT5 + VI Dubber độc lập; làm Dubber→Learn và report outbound trước; Notion + Drive + Calendar là bộ ứng viên nhỏ. Dùng connectors chính thức, bổ sung glue tối thiểu; thử n8n nếu workflow tăng; chưa mua Notion AI, chưa dựng platform điều phối mới. Tài liệu này vẫn DRAFT cho tới khi owner giao phạm vi thực thi.
