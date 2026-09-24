# BR-01: protocol khóa trước khi xem kết quả

## Mở rộng theo yêu cầu 13/09/2026

Xem [STUDY-PLAN.md](STUDY-PLAN.md) cho phânvai2018–2025, thay phạm vi thu thập hai năm bằng nghiên cứu nhiều khối thời gian. [HISTORY-EXTENSION-REPORT.md](HISTORY-EXTENSION-REPORT.md) ghi dữ liệu đã nhận và giới hạn. Đây không phải thay tham sốv0 hoặc mởholdout2025. Các protocolSCREEN bên dưới là phiên bản/nhánh kỹ thuật, không tự trở thành fullbacktest.

## Bổ sung nguồn dữ liệu trước performance — 2026-09-12

Theo yêu cầu làm chuẩn dữ liệu, góiFTMO2023–2024 rawticks và derivedBid/Ask được tạo riêng; đọc DATA-REPORT.md, DATA-SOURCES.md và quality-data/LATEST.json trước sử dụng. Không sửa v0, không mở holdout, không chạy/so lợi nhuận để chọn nguồn. Dukascopy là nguồn đối chiếu, tháng10/2024 quarantine. Full-execution gate hiệnchưađạt vì tickthiếu, lịch vàcost/news. SCREEN-01 bên dưới là thiết kế ban đầu, không tự coi đã tích hợp datasetmới.

## Protocol ban đầu

Ngày 2026-09-12. Yêu cầu: backtest, cân nhắc tối ưu và đánh giá edge. Không đặt lệnh.

## Phạm vi lượt đầu

- Giữ nguyên tài liệu BR-01 v0; không sửa tham số để tạo lợi nhuận.
- Development: 2023-01-01 đến hết 2024-12-31, liên tục. 2025 là holdout dành riêng: chưa tải/chạy/xem kết quả trong lượt sàng lọc.
- Nguồn: Dukascopy public H1 BID/ASK, UTC bucket. API schema tham chiếu source MIT dukascopy-node (Leo4815162342), data-normaliser và url-generator; không cài/chạy package đó. Không sinh nến phẳng cho khoảng trống cuối tuần. Lưu dữ liệu gốc và SHA256.
- Đây là SCREEN-01, **không phải backtest đầy đủ BR-01**: chỉ luật mẫu hình, lịch UTC+7 Mon–Thu 14–20, entry Ask nến sau, SL Low retest−1pip, TP khoảng cách2:1, thoát23h, một vị thế, tối đa2lệnh/ngày, lọc spread như v0.
- Chưa có lịch tin FTMO lưu trước phiên: bỏ bộ lọc tin trong screening và ghi sai khác, tuyệt đối không coi thiếu tin là không có tin. Không mô phỏng margin, tài khoản drawdown, equity stop và buffer; chưa đánh giá pass/payout. Không gọi kết quả này là vốn10k thực tế.
- R cố định bằng ngân sách lý thuyết mỗi lệnh; không làm tròn lot. Commission giả định7USD/standard lot cả vòng; reserve1pip dùng trong mẫu số R; không trừ reserve như phí thực tế. Stress thêm1pip spread lúc entry và0.5pip slippage mỗi chiều; không dùng tham số stress để chọn winner.
- H1 Ask Open và Bid Open không bảo đảm đồng thời tick: mô hình spread xấp xỉ. Cùng H1 chạm SL/TP: báo cả SL-first/TP-first. Gap SL: giá Bid Open xấu hơn; TP không tốt hơn mức TP. Nếu không có nến thoát23h hoặc bị thiếu giờ trong lúc chờ/giữ: fail closed, không gán hòa vốn.
- Thống kê số lệnh, win rate, tổng/mean R, profit factor, realized-R drawdown (không phải equity drawdown), số nến mơ hồ; 95% bootstrap theo tuần, chỉ là bất định trong sample development, không xác nhận edge.
- Không tối ưu v1 và không mở holdout trước khi hoàn thiện bộ lọc tin, dữ liệu thực thi và kiểm thử đầy đủ. Kết quả âm hoặc chưa đủ bằng chứng đều được chấp nhận. Đây là checkpoint chứ không hứa hoàn thành kiểm chứng trước ngày mai.

## Nguồn kỹ thuật

- https://github.com/Leo4815162342/dukascopy-node
- https://raw.githubusercontent.com/Leo4815162342/dukascopy-node/master/src/data-normaliser/index.ts
- https://raw.githubusercontent.com/Leo4815162342/dukascopy-node/master/src/url-generator/index.ts
- https://jetta.dukascopy.com/v1/candles/hour/EUR-USD/BID/2024/1

Ngày2024-01 chỉ kiểm tra schema/count trước khóa protocol, chưa xem kết quả chiến lược. Source upstream mutable; dữ liệu tải thực tế được hash trong manifest.

Data-quality gate trước kết quả: JSON endpoint có bản ghi2024-10-10T20:00Z Close thấp hơn Low1tick sau decode, nên không dùng JSON để tính kết quả. Đối chiếu bằng archive BI5 cùng Dukascopy (không phải nguồn độc lập), schema `>5If`, thứ tự sec/open/close/low/high/volume, tháng0-based, từ source tag v1.46.0. Không sửa giá hoặc loại tháng; nếu archive cũng không hợp lệ thì dừng. JSON tải trước giữ nguyên để audit.
