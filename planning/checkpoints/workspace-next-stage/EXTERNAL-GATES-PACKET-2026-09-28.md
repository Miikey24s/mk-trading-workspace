# External-gates packet — 2026-09-28

## Quyết định hiện tại

Chưa có external gate nào bắt buộc owner phải thao tác ngay. Các lane offline tiếp tục độc lập. Không lặp login, không resume Job12, không đổi provider/model để né gate.

## Trạng thái đã xác minh

| Gate | Trạng thái | Ai làm tiếp | Điều kiện mở |
|---|---|---|---|
| Dedicated Dubber-WebGPT | Runtime local **ONLINE**, catalog HTTP 200, active turns 0; provider acceptance vẫn lỗi ở assistant turn | Agent/máy giữ health/readiness; owner chỉ login lại nếu session thật hết | Một canary mới có assistant turn hợp lệ và payload schema đúng; sau đó mới resume retained job |
| Job12 | Terminal failed tại translation, progress `0.3711246200607903`; 28/28 ASR, 864 cache IDs | Agent giữ checkpoint/receipt, không tạo worker thứ hai | Provider acceptance + single-lease resume review |
| Human listening / owner QA | Một số gói đã đóng; gate mới vẫn cần người nghe nếu thay đổi media/voice | Owner thực hiện khi có packet cụ thể | File/fixture và ballot packet được chuẩn bị |
| VI→Learn / Drive / Notion / Calendar | Offline contract/fixture có thể tiếp tục; cloud I/O chưa chạy | Agent làm contract, idempotency, revoke, reconcile | Owner chọn account, destination, data scope và cấp OAuth/permission |
| TypeSafe/Jev | Optional shadow path; local/fake unknown-safe đã đủ cho offline | Agent tiếp tục contract/QA | Owner cung cấp `TYPESAFE_API_KEY` nếu muốn semantic QA thật |
| Broker/demo/live/holdout | **Fail-closed / chưa cấp quyền** | Agent làm paper/shadow/risk/reconcile | Owner chọn venue/account + exact risk/action scope; sau đó paper/forward and fault gates |
| Make/public upload/deploy/destructive | Không có gate đang chờ ở skeleton đã đóng | Agent tiếp offline | Owner cấp account/credits/data/public scope cho một lượt mới |

## Quy tắc thực thi

- External gate chỉ mở theo đúng resource, account, destination và action đã ghi trong packet; không suy quyền từ research/UI/login.
- Timeout hoặc kết quả không rõ phải tra receipt/reconcile trước khi retry; không gửi lại request có khả năng đã accepted.
- API key/secret không ghi vào repo, log, chat hoặc config global.
- Khi một gate mở, tạo receipt có source revision, scope, identity, timestamp, outcome, redaction và rollback/revoke path.

## Việc owner sẽ được gọi một lần, theo thứ tự

1. Nếu runtime báo session hết thật: login đúng profile Dedicated Dubber-WebGPT một lần.
2. Khi connector slice sẵn sàng: chọn account/destination/data scope cho OAuth từng connector.
3. Khi paper gate đạt: cung cấp exact broker/account/risk scope nếu muốn mở demo/live; không mở live trực tiếp.
4. Nếu cần semantic QA cloud: đặt `TYPESAFE_API_KEY` server-side trong process/session được chỉ định.

Evidence: `planning/WORKSPACE-NEXT-STAGE-PLAN.md` §8, §12; `planning/checkpoints/workspace-next-stage/RESUME.md`; local runtime health `127.0.0.1:17850/healthz`.
