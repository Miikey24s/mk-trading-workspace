# Lịch sử EURUSD trước2023 — kiểm tra 13/09/2026

**FTMO đã cung cấp31.096nến H1 cho2018–2022.** Phạm vi2023–2024 trước đây là lựa chọn nghiên cứu, không phải giới hạn lịch sử thực tế đã kiểm chứng của broker. Chưa có performance BR-01, chưa tải tick5năm cũ, chưa mở2025.

## Đã lấy và kiểm tra

| Năm | FTMO H1 | Dukascopy đối chiếu |
|---|---:|---|
| 2018 | 6.203 | Đã nhận12tháng Bid/Ask; basic geometry/range/order đạt |
| 2019 | 6.197 | Đã nhận12tháng Bid/Ask; basic geometry/range/order đạt |
| 2020 | 6.248 | Tháng1 đủ hai bên; tháng2 mới có Bid |
| 2021 | 6.240 | Chưa tải đối chiếu |
| 2022 | 6.208 | Chưa tải đối chiếu |

Các nến FTMO qua kiểm tra range yêu cầu, timestamp tăng và OHLC hợp lệ. Khoảng cách không liên tiếp vẫn được giữ để phân loại, không fill. `error_code=1` trong metadata là mã success của SDK, không phải1lỗi. Dữ liệu chỉ có Bid OHLC và trường spread của nến, không phải lịch sử Ask/tick đồng bộ đủ cho thực thi.

Dukascopy: nhận51/120bucket tháng/side dự kiến;51bucket đã nhận qua kiểm tra cơ bản, chưa đủ xác nhận độ phủ mọi phiên. Có13.459BID và12.979ASK rows trong các bucket đó, **không phải cùng một tập timestamp** vì tháng2/2020 thiếuASK.

HTTP429 tại ASK tháng2/2020: đã dừng cả lượt tải, không retry hoặc đổi proxy/IP. Endpoint BI5 cũng trả429 ở probe ban đầu; không tiếp tục truy cập endpoint đó. Collector đã kết thúc, không có lịch chạy nền. Lần resume do người dùng yêu cầu sau này reuse các file đã có; không tải lại51bucket thành công.

## Kiểm tra clock ban đầu, chưa chuẩn hóa bộ cũ

Đối chiếu Close FTMO với Dukascopy Bid, thử offset0–4giờ cho mỗi ngày có ít nhất12nến match mỗi offset; chỉ phân tích giá/timestamp, không tính chiến lược:

- 2018:259ngày đủ đối chiếu; offset tốt nhất+2h ở104ngày,+3h ở155ngày; không có hòa điểm; median sai khác Close theo median ngày là1point (0,1pip).
- 2019:259ngày; +2h ở109ngày,+3h ở150ngày; không có hòa; median3points (0,3pip).
- 2020:42ngày đầu có nguồn đối chiếu;+2h tốt nhất ở42ngày; median1point.
- 2021–2022:chưa có nguồn đối chiếu trong lượt này.

Đây là bằng chứng clock không được gắn nhãnUTC trực tiếp; **chưa xác minh lịch chuyển offset từng ngày hoặc quy tắcDST chung cho toàn2018–2022**. Không mở rộng hàm `server_offset`2023–2024 sang bộ cũ bằng cách bỏ range guard. Giữ raw clock đúng nhãn chưa xác minh cho tới khi hoàn thiện mapping.

## Cách chia giai đoạn

Đã ghi trước kết quả tại [STUDY-PLAN.md](STUDY-PLAN.md):2018–2020 development;2021–2022 kiểm tra tiếp;2023–2024 kiểm tra giai đoạn gần/đối chiếuFTMO;2025holdout cuối. Chạy liên tục bên trong từng khối, phân tích theo năm/quý; không chọn khoảng có lời hoặc resetstate theo tháng. Nếu điều chỉnh dựa trên tập kiểm tra thì phải ghi tập đó đã tham gia phát triển, không còn độc lập.

## Code/validation và phần còn lại

- Đã tái hiện và sửa lỗi screening cũ tái sử dụng nến thoát làm breakout mới; bộ luật BR-01 không đổi.
-31unit tests dữ liệu/chuỗi tín hiệu qua kiểm tra. Test synthetic không phải lệnh lịch sử hoặc bằng chứng edge.
- `ftmo_screen.py` chuẩn bị adapter và ledger ngoại lệ cho dữ liệu2023–2024; **chưa chạy performance**. Không gọi việc có script là đã backtest.
- Còn: hoàn tất nguồn đối chiếu sau khi hết rate limit; audit lịch/gaps và timezone bộ cũ; chọn dữ liệu thực thi M1/tick; historical news/cost/fill/account rules. Gate2023–2024 và gate bộ cũ đều chưa đạt full-execution.
- Không sửa repo `mt5-tradingview-backtester`, configMCP hoặc quyềnMT5 trong lượt này; không đặt lệnh, không tối ưu, không mởholdout, không trả phí.

## Bằng chứng local và nguồn

- FTMO receipt: `quality-data/history-extension/ftmo-availability-9063d3501642.json.gz`, SHA256file `f4b8ac3a8c96dbc72237cb6fe3be344b9714cad051abea3df8015b9636a3e05a`.
- Dukascopy receipt: `quality-data/history-extension/availability-94ba461c5f28.json.gz`, SHA256file `69e25baecadf8b7c7f0361ad1eca9e14e96c1711ddf00114edb7268b215b66e9`.
- Mỗi receipt chỉ tới raw theo năm/tháng với hash; số tài khoản và key không lưu vào báo cáo.
- [Dukascopy Historical Data Feed](https://www.dukascopy.com/swiss/english/marketwatch/historical/): trang chính thức đã truy cập HTTP200.
- Endpoint đã nhận dữ liệu: `https://jetta.dukascopy.com/v1/candles/hour/EUR-USD/BID/2018/1`; logic decode reuse `data_pipeline.decode_duka`, không cài/chạy package mới.

Luồng dữ liệu: hai nguồn → raw riêng cóhash → audit hình học/range/clock → phạm vi kiểm tra khóa trước → sau này mới chạy luật. Không ghép dữ liệu hai feed để che khoảng thiếu. Dữ liệu chỉ phục vụ nghiên cứu local, không xác nhận quyền tái phân phối.
