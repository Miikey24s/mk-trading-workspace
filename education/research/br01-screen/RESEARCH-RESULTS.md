# BR-01 — kết quả chạy đầu tiên với lịch archive và chi phí giả định

Ngày 13/09/2026. **Pipeline nghiên cứu đã chạy xuyên suốt; ứng viên chưa có bằng chứng edge.** Hai kịch bản đã khóa trước P/L theo [protocol](RESEARCH-RUN-PROTOCOL.md), không sửa luật mẫu hình sau kết quả. Đây không phải tái dựng chính xác tài khoản FTMO quá khứ.

| Chỉ tiêu | Thận trọng | Stress chi phí cao hơn |
|---|---:|---:|
| Lệnh đầu (ngày UTC) | 24/01/2018 | 24/01/2018 |
| Lệnh cuối (ngày UTC) | 21/11/2019 | 01/05/2019 |
| Số lệnh | 21 | 18 |
| Thắng / thua sau phí | 5 / 16 | 5 / 13 |
| Lãi/lỗ ròng USD | −146,98 | −138,93 |
| Balance cuối USD | 9.853,02 | 9.861,07 |
| Tổng R (mỗi lệnh chia Q riêng) | −5,8983 | −5,5717 |
| Profit factor | 0,5124 | 0,5157 |
| Drawdown equity lớn nhất USD | 146,98 | 138,93 |
| Chuỗi thua liên tiếp dài nhất | 7 | 4 |
| Phiên VN có dữ liệu trong phần quan sát | 394 | 277 |
| Phiên bị chặn vì tin không rõ giờ trong phần quan sát | 7 | 5 |
| Lệnh có khoảng tick >5 phút từ entry đến exit | 0 | 0 |

**Cả hai dừng vì không còn đủ phần đệm tổng cho Q**, chưa phải chạm −150 USD. Ví dụ thận trọng: còn 3,02 USD tới ngưỡng, trong khi Q mới khoảng24,63USD; luật không cho vào. Không reset balance, không giảm Q tùy ý và không tiếp tục tính năm2020. Stress có tổng lỗ nhỏ hơn vì dừng sớm hơn, khác số lệnh/lot/đường khớp; không suy phí cao làm chiến lược tốt hơn. Khoảng chỉ có18–21lệnh không đủ ước lượng edge đáng tin cậy.

## Đầu vào và hành vi mới

- Giá QDM 2018–2024 được giữ nguyên. Hash toàn CSV kiểm tra lại ở mỗi run khớp audit: `af7e4be87b5dc60a355e98cadff560e26fba4241dfe52890aa61d6fe7c0a5d56`. Không đọc2025; không chạy performance2021–2024. Không đọc raw QDM proprietary All time.
- Lịch riêng chuẩn hóa từ36tháng archive:628phiên Mon–Thu trong2018–2020;21sự kiện không rõ giờ khiến11phiên bị chặn trong toàn khoảng. Giả định New York/DST dựa trên36NFP cùng clock08:30. Không giả đây là lịch biết trước phiên; `known_at_utc=null`, `coverage_verified=false`, basis=`archive_proxy`, chỉ profile được duyệt mới sử dụng.
- Commission thận trọng5USD/lot/chiều (10cảvòng), stress7USD/lot/chiều (14cảvòng). Đây là giả định nghiên cứu, **không tuyên bố đó là phí FTMO thực thu**. Slippage lần lượt0,2/0,3pip và0,5/1pip cho entry/marketexit. Spread thực trong tick không cộng lại, TP limit không hưởng gap giá tốt hơn, reserve1pip chỉ dùng sizing.
- Luồng chạy: nến H1 đã đóng → B/R/zone → lịch phiên + budget → tick đầu vào Ask → lot/margin → tick đầu thỏa điều kiện thoát Bid → sổ USD/R/equity. Chặn tin không rõ giờ được ghi rõ, không âm thầm xóa giá hoặc lệnh đã biết kết quả.

## Kiểm chứng

**104 tests distinct đạt** (60 offline/QDM +44 regression MT5). Bao gồm proxy phải được duyệt riêng, từ chối thiếu tháng/hash sai, winter/summer UTC, DST mơ hồ, không bịa giờ All Day, chặn cả phiên và phân biệt hết phần đệm với chạm ngưỡng lỗ. `education/check_setup.py` dùng để kiểm tra state giáo dục; không biến test kỹ thuật thành học lực.

Đã kiểm tra độc lập mọi21+18trade bằng `verify_research_episode.py`: lấy lại tick, duyệt tuần tự bằng vòng lặp scalar, đối chiếu first exit, commission, lot, netUSD, balance và equity drawdown. Đồng thời đối chiếu từng B/R với20nến trước B, lần chạm đầu và SL theo LowR. **Tất cả khớp**. Đây là kiểm chứng code trên cùng nguồn, không chứng minh nguồn đầy đủ tuyệt đối hoặc xác nhận tất cả cơ hội ngoài sổ đã được engine tìm đúng.

Không đổi tham số chiến lược, không mua/chạy challenge, không đặt lệnh demo/live, không tạo service nền. Hai job đã kết thúc.

## Bằng chứng chạy

- Calendar: `quality-data/br01-engine/news-archive-proxy-2be1efab804c.json.gz`, fileSHA `778a468f0e9a783cd24c1f46fa030e9df88b582a11f7ed16c1f85d0e1af03806`.
- Conservative: `quality-data/br01-engine/episode-39022ce6bacd.json.gz`, fileSHA `e8c245140159126f2aa3e7e4835f41fbeddc89300d7727520ea5dd11e2c88e84`.
- Stress: `quality-data/br01-engine/episode-ced2f56848ef.json.gz`, fileSHA `7a5b5cb169ea37d6a4611f7cb8ff10bf90cb0e735a698c81bd88ae659af1ea54`.
- Kiểm chứng conservative: `quality-data/br01-engine/scalar-verification-9478efb372de.json.gz`.
- Kiểm chứng stress: `quality-data/br01-engine/scalar-verification-ce2931093509.json.gz`.

Mỗi episode giữ profile, hashes code/luật/protocol/lịch, receipt truy vấn tick, từng trade/event/session. Các receipt verification cũ vẫn giữ như lịch sử, không ghi đè.

## Bước tiếp theo đề xuất

Setup đủ cho phép thử nghiên cứu đã thống nhất. Không mua challenge hoặc đưa v0 lên live dựa trên kết quả này. Trước tối ưu, xem nguyên nhân ít tín hiệu và chất lượng đầu vào của mẫu hình, phân biệt luật tín hiệu với chính sách dừng đợt. Muốn tiếp tục lấy mẫu sau khi episode dừng cần một protocol nghiên cứu riêng được chốt trước, không tự reset tài khoản rồi ghép lợi nhuận. Không dùng2021–2024 để cứu kết quả vừa thấy.
