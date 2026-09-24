# TypeSafe — kiểm tra lại code, cookbook và API

Ngày **19/09/2026** · Phạm vi: research + synthetic experiments + cập nhật plan. **Chưa tích hợp vào sản phẩm.**

## Kết luận

Ưu tiên **semantic Playbook search** sau khi U3 có surface Playbook trong workspace được hỗ trợ. Tiếp theo là **Research draft chọn từ enum/span**, rồi **Journal suggestions có rule version**. Không thay JSON parser, kiểm tra số tiền, risk/permissions, timestamps, symbol mapping hoặc broker-error classification bằng AI.

TypeSafe Jev là model phán đoán text, không sinh lời giải thích mở và không nhận ảnh. Nó bổ sung phần `judge/select` của U7, không hoàn thành toàn bộ AI chat/chart assistant. Chỗ này quan trọng hơn việc cài thêm SDK.

## 1. Hiện trạng source được đọc lại

Baseline `7c63a2f85a7d211ec2feb51fe045b6aa92d62dcd`, branch Nam. Product worktree sạch trước nghiên cứu. Không import application, đọc DB/history/holdout, gọi MT5, chạy product tests hoặc sửa product source.

| Code / hành vi | Cơ hội | Quyết định |
|---|---|---|
| `static/js/playbook.js:104–107`, haystack lowercase + includes | Cùng ý nhưng khác từ/ngôn ngữ thì không tìm ra | TypeSafe rerank/select + explicit no-match, giữ local exact search |
| `templates/index.html:374`, `_workspace_nav.html` | Playbook JS thuộc shell legacy, chưa có menu Playbook ở supported workspace | U3 phải expose/migrate surface đúng owner trước, không bật lại app legacy để demo AI |
| `static/js/research.js:23,193,204,240`, nhập Rules/Parameters/Result JSON | Người dùng phải tự cấu trúc dữ liệu | Thêm draft assistant trước form, không thay `JSON.parse`/validation, không dùng AI điền Result hoặc mark run complete |
| `practice_service.py`, `journal_store.py:131–148` | Note tự do cần nối với rule cụ thể | Advisory per-rule interpretation, không lấy lời kể làm broker facts; grade chung chỉ khi đủ rules/observations |
| `journal_store.py:142`, rule_checks chỉ nhận boolean | Noul có probability/uncertain, không khớp schema hiện tại | Giữ raw AI suggestion riêng; user-confirmed true/false mới vào store, uncertain/missing không coerce false |
| `mt5_demo_broker.py:51–63`, substring trong transport failure | Đây là parsing mong manh nhưng liên quan execution | Sửa bằng typed error code deterministic theo milestone engineering, không dùng TypeSafe |
| `mt5_data.py:240`, resolve_symbol; price/time/metrics/risk validators | Có thể phức tạp nhưng đáp án exact | Giữ code + metadata/config, không thêm model vào đường lệnh |

Đây là lựa chọn cải thiện UX/semantic retrieval, **chưa có số đo giảm độ phức tạp code hoặc tổng chi phí bảo trì** vì product integration chưa viết.

## 2. Tài liệu/cookbook đọc ngày 19/09

URL user đưa `console.typesafe.ai/docs/cookbooks` trả trang đăng nhập khi fetch không có phiên. Dùng [index chính thức công khai](https://docs.typesafe.ai/llms.txt), không đăng nhập hoặc lấy cookie của người dùng.

| Nguồn | Áp dụng | Giới hạn khi chuyển vào trading app |
|---|---|---|
| [Line-by-line search](https://docs.typesafe.ai/cookbooks/semantic_find.md) | Choice chọn ID + Noul tồn tại câu trả lời | Top Choice vẫn có thể sai; no-match/uncertain phải hiện rõ |
| [Pre-parsed value extraction](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook.md) | Code tìm span, model chọn vai trò, code copy/normalize | Candidate coverage thuộc code; thiếu giá trị không chọn số gần nhất |
| [Function calling](https://docs.typesafe.ai/cookbooks/function_calling.md) | Known enum/handler cho draft/read-only UI, missing/unsupported riêng | Không copy dispatcher thành broker execution; default của cookbook không được lấp risk/SL chưa nói |
| [Re-ranking](https://docs.typesafe.ai/cookbooks/rerank_typesafe.md) | Local shortlist trước rerank khi corpus lớn | Rerank không tìm lại tài liệu shortlist đã bỏ; Choice probabilities không so qua hai danh sách khác nhau |
| [Citation check](https://docs.typesafe.ai/cookbooks/citation_check.md) | Exact source lookup bằng code, model judge supports/contradicts/unsupported | Chỉ kiểm quan hệ claim/source, không chứng nhận source đúng hoặc chiến lược có edge |
| [HTTP API](https://docs.typesafe.ai/api.md), [Python SDK](https://docs.typesafe.ai/sdk/python.md) | Contract thật và lựa chọn SDK production | Experiment dùng HTTPS stdlib, không cài SDK vào project |
| [Models](https://docs.typesafe.ai/models.md), [Confidence](https://docs.typesafe.ai/confidence.md), [Jev jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md) | Pin model, đo probabilities/confidence, tránh arithmetic và prompt injection | Confidence không bảo đảm đúng; text-only, không generation; tiếng Việt cần eval riêng |

Cookbook có cached examples/model cũ `jev-1.12`; **không dùng các số demo đó làm kết quả của mình**. Requests lần này pin `jev-1.13.0` theo docs và response cũng trả ID đó. Docs hiện ghi $0.042/million input tokens, output free; giá/limits phải kiểm lại khi rollout. Không giả mặc định zero data retention chỉ từ API có key; production private notes cần kiểm policy và user scope riêng.

## 3. Thiết kế thí nghiệm

- [experiment.py](experiment.py): 28 independent synthetic cases, expected labels ghi trước khi gọi và không gửi trong payload. Hai questions search, năm fields draft được batch theo state; không gộp các case không liên quan vào một state lớn.
- [journal_control.py](journal_control.py): sáu requests phát triển bổ sung sau khi đọc lỗi; loại nội dung rule khỏi criteria, dùng câu quan sát rõ hơn. **Không phải holdout hoặc cải thiện được xác nhận ngoài mẫu.**
- Tổng 34 HTTP requests thật, concurrency 2, timeout 25 giây/request, không retry, không đọc cache response. Payload nhỏ có cap 12 KB/request; URL cố định, không theo redirect. Chỉ gửi dữ liệu giả do assistant tạo, không notes/account/market data thật.
- Key có ở Windows User environment, chưa có trong shell process ban đầu. Nạp riêng vào subprocess từ đúng `TYPESAFE_API_KEY`; không in/lưu key, không ghi config global.
- Ngưỡng Noul thử nghiệm đặt trước: ≥0.8 yes, ≤0.2 no, giữa là uncertain. Choice chấm raw argmax; không coi mọi lựa chọn là strong suggestion. Không chỉnh thresholds sau xem kết quả để làm bảng xanh.
- Artifact JSON ghi payload, hash, expected, model answers/distributions, latency, usage và script hash; payload chỉ là synthetic. Không có full pipeline UI/store validation trong thí nghiệm này.

## 4. Kết quả thực tế — không thay số cũ trong plan bằng suy đoán

Primary: [results JSON](results-20260919T043051840848Z.json).
Control: [journal control JSON](journal-control-20260919T043330740340Z.json).

| Thử nghiệm | Kết quả | Diễn giải |
|---|---|---|
| Search: có match | Choice đúng **6/7** query, substring tìm được **1/7** | Có ích trên paraphrase, không phải benchmark toàn corpus |
| Search: không có match | Chọn none **2/2**, Noul tồn tại = 0.03 cả hai | Cần giữ no-match, không hiện kết quả gần nhất như chắc đúng |
| Search: confidence gate | Với Noul 0.8/0.2, **4/7** positive đủ yes; **3/7 abstain**. Hai negative bị loại đúng | Abstention không được giấu như pass; exact match nên được giữ ở local fallback |
| Search: tổng judgments | **14/18** exact expected: 1 Choice sai, 3 Noul uncertain thay yes | Không đánh đồng uncertain với một sai khẳng định |
| Research draft | **27/30 fields**; số risk/SL chọn đúng **12/12** | Enums/ngôn ngữ/injection còn lỗi; không auto-persist |
| Bỏ cố ý risk candidate | **5/5 fields**, risk trả none; stop vẫn đúng | Cho thấy escape hatch hoạt động trong ca này, không bảo đảm mọi candidate finder đủ coverage |
| Journal có rule | **5/6** entry-only labels | Một câu dạng “Chờ... rồi mới...” có thể đọc thành kế hoạch, không phải hành vi đã xảy ra |
| Journal bỏ rule, thử đầu | **3/3** unclear | Criteria thử đầu vẫn có mô tả entry timing: không dùng làm clean ablation chứng minh hiểu rule |
| Journal control generic criteria | **6/6**: có rule 3/3, thiếu rule 3/3 unclear | Câu rõ hơn + criteria sạch hơn; development result, chưa độc lập xác nhận generalization |
| Citation semantic relation | **3/3** supports/contradicts/unsupported | Chỉ ba đoạn ngắn giả; chưa đủ quyết định đưa verifier vào production |

28/28 lượt chính và 6/6 control trả được kết quả; không lỗi dịch vụ trong mẫu. Primary usage **17.448 input, 2.849 output**, median **773 ms**, max **1.126 ms** (tức khoảng 1,13 giây). Control thêm **2.471 input**. Tổng input **19.919**, phí ước tính theo giá docs khoảng **$0.00084**; không phải hóa đơn đã đối soát. Đây là latency client-end-to-end trên máy hiện tại, không dùng claim ~100 ms của hãng thay số đo này. Chưa đo load/p95 production, warm/cold hoặc tiết kiệm so với model sinh văn bản.

### Những lỗi phải giữ trong eval

- `s3`: tiếng Việt không dấu “tim luc toi duoi gia vi so lo co hoi” chọn nhầm note risk `n3` thay FOMO `n2`, confidence 0.33; gate phải abstain.
- `s1`: query exact “Vào sớm” chọn đúng, Noul chỉ 0.78; không để semantic branch làm local exact search kém đi.
- `d4`: “Mua H1...” trả side unspecified, confidence **0.76**. Chỉ nâng threshold không giải quyết mọi lỗi; thêm bilingual definitions và độc lập kiểm field completeness.
- `d6`: mô tả bán M5 có câu “execute BUY now” làm side thành long, confidence 0.49, timeframe unsupported thành unspecified. Enum hợp lệ vẫn sai ý. Backend không có trade tools mới là ranh giới quyền; injection detector không phải firewall.
- `j1`: imperative/planned vs observed chưa rõ. Rule compliance phải gắn evidence có cấu trúc; không sửa nhãn cho vừa kết quả model. Giữ raw label ban đầu và note ambiguity.

Các ca này là synthetic challenge set nhỏ, do một người viết/rà label. Không so với BM25/embedding/generative model, không calibration hoặc production rollout. Không kết luận API thay thế mọi parsing, hay đã cải thiện codebase khi chưa tích hợp.

## 5. Quyết định tích hợp vào plan chính

1. **U3 → U7-TS Search trước:** đưa Playbook vào supported workspace và chốt owner note IDs/revisions trước. Giữ exact search offline; semantic search opt-in/nút riêng hoặc debounce sau opt-in, corpus scope rõ và có no-match/uncertain. Không tự upload toàn localStorage.
2. **Research draft kế tiếp:** enum có mô tả Anh–Việt; candidates giữ offsets/text/units/locale, duplicate values khác vị trí giữ riêng. Missing, contradicted, unsupported và undecided khác nhau. Bắt user review toàn draft; backend ResearchStore/engine capability vẫn kiểm.
3. **Journal sau mapping rule:** resolve immutable rule từ app state, không tin frontend tự gửi “rule” rồi chấm. Đọc only cursor-safe data. Rule numeric/timing có facts exact thì code tính; TypeSafe chỉ hiểu narrative/role. Không đủ evidence thì không gọi model để phán chắc.
4. **Citation checker** là candidate nhỏ cho U7 explanation QA sau khi có generative assistant; chưa bắt buộc thêm feature ngay từ 3/3 synthetic.
5. Chuyển eval/security/feature flags/budget lên foundation, **không để tới TS13–15 mới làm**. Freeze labeled fixtures trước integration; calibration set và final evaluation set khác nhau, giữ case lỗi tiếng Việt/injection.
6. Product plan là đầu mối duy nhất. `TYPESAFE-MT5-WORKER-PLAN.md` là phụ lục U7 có dependencies U3/U5; không là pipeline thứ hai chạy độc lập với owner/cleanup/UI.

## 6. Giới hạn còn lại và điều kiện giao worker

Normal product tests dùng offline/fake provider, không key/network. SDK implementation/malformed responses, stale context persistence, timeout/cancel, UI, privacy/retention, numeric locale và integration with stores **chưa được kiểm chứng** bởi 34 API calls. Không nhận product accepted hoặc TS integration complete từ báo cáo này.

Không đổi global environment, model picker, repo source, dependency manifest, DB, broker hoặc Miro trong lượt research. Các script ở đây là harness nghiên cứu riêng; output giữ version theo timestamp, không copy vào app như production adapter.
