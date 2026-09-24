# BR-01 v0 — EUR/USD H1: phá lên và retest lần đầu

Soạn ngày 11/09/2026. Đây là **ứng viên nghiên cứu do gia sư đề xuất**, chưa được backtest, chưa chứng minh edge hay phù hợp để mua challenge. Chỉ Buy để giới hạn số nhánh trong lượt thử đầu; không phải dự báo EUR/USD tăng. Không phải bản nâng cấp đã kiểm chứng của LAB-01. Không khôi phục bài toán LAB-01 đã ngừng theo yêu cầu học viên.

## Tờ luật đọc chart

1. **Dữ liệu:** EUR/USD, H1, OHLC Bid, chỉ nến đã đóng. 1 pip = 0,0001. Dùng một feed nhất quán; ảnh screenshot hiện tại không đủ lấy chính xác 20 High. Trước thực hành cần xác minh loại giá và ánh xạ timestamp sang UTC+7; không đoán giờ server.
2. **Mốc H20:** khi không có vị thế/setup đang chờ, lấy High lớn nhất của đúng 20 nến liền trước nến vừa đóng B, không gồm B. Tạo zone từ H20 − 1 pip đến H20 + 1 pip. Đây là vùng quanh cực trị nhìn lại, KHÔNG khẳng định đã là vùng cản được nhiều lần kiểm chứng.
3. **Phá lên:** Close B phải lớn hơn zone High. Bằng thì không đạt. Nếu đạt, đóng băng H20 và hai biên zone; ghi lại B. Không vào ngay và không dịch zone theo nến mới.
4. **Retest:** chỉ xét 6 nến H1 tiếp theo B (B+1 đến B+6). Nến chạm zone khi Low <= zone High và High >= zone Low. Xét đúng lần chạm đầu tiên. Nến đó chỉ thành tín hiệu R khi đã đóng, Close > zone High và Close > Open. Nếu lần chạm đầu không đáp ứng, hủy setup, không đợi một nến đẹp hơn cho cùng setup. Nếu trước đó có Close <= zone Low (kể cả gap không chạm) thì hủy. Low xuyên zone Low nhưng Close hồi lên vẫn có thể đạt; không nhầm Low với Close. Hết 6 nến không chạm thì hủy. Đang chờ thì bỏ qua các breakout mới.
5. **Điểm vào dự kiến:** Buy tại Ask khả dụng đầu tiên của nến kế sau R; không lấy Close R làm giá khớp. Thực hành thủ công phải kiểm tra ở đầu giờ; nếu không thể lập phiếu/nhập trong 60 giây đầu thì ghi bỏ lỡ, không đuổi giá. Không dùng High/Low/Close hoàn chỉnh của nến đang vào để quyết định.
6. **SL và thoát:** SL Bid = Low R − 1 pip. Gọi d = Entry Ask − SL Bid; d phải dương. TP Bid = Entry Ask + 2d. Đây là tỷ lệ khoảng cách giá 2:1, không cam kết +2R ròng sau phí. Không dời/nới SL, không dời TP, không chốt từng phần, không gồng thêm vị thế. Thoát sớm ở mốc thời gian nội bộ dưới đây nếu SL/TP chưa khớp.
7. **Vòng lặp:** chỉ một setup chờ hoặc một vị thế; không đồng thời. Sau hủy/bỏ lỡ/đóng lệnh, bắt đầu xét H20 mới từ nến H1 đóng tiếp theo. Không tái sử dụng chính nến hủy/thoát làm breakout mới. Không bổ sung Sell trong cùng mẫu thử v0.

Tham số 20 nến, ±1 pip, 6 nến, tỷ lệ giá 2:1 là lựa chọn khởi đầu để luật kiểm tra được, không phải tham số tối ưu, chuẩn price action hay điều kiện FTMO.

Vòng phát triển/tối ưu không nằm trong core rule này. Giữ v0 bất biến và dùng [BR-01 development loop](../research/br01-screen/DEVELOPMENT-LOOP.md) để thu bằng chứng, chẩn đoán, tạo version mới, validation, holdout và forward demo. Checklist trade tay có thể rút gọn cách trình bày nhưng không được bỏ điều kiện của rule đã test.

## Lịch quan sát và điều kiện không vào — đề xuất cho demo

- Các mốc quyết định/đầu nến từ **14:00 đến 20:00, thứ Hai–thứ Năm, giờ Việt Nam UTC+7**. Nến B và R đều phải đóng trong cửa sổ này. Mốc 20:00 cho phép vào nếu R vừa đóng, không tạo B mới; hủy setup còn chờ sau mốc này.
- Đây là cửa sổ thử về lịch sinh hoạt, không tuyên bố trùng chính xác một phiên quốc tế quanh năm. Không quét ngược cơ hội ngoài giờ để tăng số lệnh. Không có chỉ tiêu ngày nào cũng phải giao dịch.
- Không có lệnh mới thứ Sáu; không giữ qua đêm trong v0. Nếu chưa chạm SL/TP, đóng ở Bid khả dụng đầu tiên lúc **23:00 UTC+7**. Đây là quy tắc thử hẹp, không phủ nhận tài khoản Swing cho phép giữ lâu hơn.
- Lưu lịch kinh tế **trước phiên** từ lịch FTMO; không vào nếu có sự kiện EUR hoặc USD được lịch đó xếp mức tác động cao trong khoảng từ 30 phút trước đến 60 phút sau thời điểm vào (bao gồm hai đầu). Nếu đang giữ lệnh thì đóng 5 phút trước sự kiện tác động cao đã ghi trước. Không đổi lịch quá khứ để loại lệnh thua; sự kiện bất ngờ được ghi nhận, không giả vờ đã biết.
- Không lấy được lịch/giờ đúng, thiếu báo giá, thiếu tham số hợp đồng/chi phí hoặc không thể theo dõi mốc thoát: chỉ nhận diện setup trên giấy, không thực thi. Không tự giả phí bằng 0.
- Trước vào: spread Ask−Bid <= 1,5 pip và đồng thời <= 20% khoảng cách Entry Ask−SL. Đây là bộ lọc thực thi khởi đầu chưa chứng minh có lợi, không phải spread FTMO đã đo.

## Rủi ro và chi phí — đề xuất, chưa cho phép đặt lệnh

- Sổ demo tham chiếu vốn ban đầu 10.000 USD. Ngân sách Q/lệnh = 0,25% × min(10.000 USD, Balance hiện tại), tối đa 25 USD. Q gồm phần lỗ theo giá tới SL, commission cả vòng và dự phòng slippage tương đương 1 pip trên khối lượng đó. Khoản dự phòng không bảo đảm chống mọi gap/slippage.
- Size = làm tròn xuống bước khối lượng của tài khoản sao cho tổng lỗ dự tính <= Q. Nếu chưa xác minh contract size, tick/pip value, min/step, commission hai chiều, stop distance và margin: chưa có lệnh hợp lệ để thực thi. Không mặc định các thông số LAB-01 hoặc Binance sang FTMO.
- Với contract size C EUR/lot đã xác minh: phần lỗ theo giá = lots × C × (Entry Ask − SL Bid). Spread đã nằm trong giá mua Ask/giá bán Bid; không cộng spread lần hai. Tính phí và dự phòng riêng; kiểm tra equity sau spread và đủ free margin trước vào.
- Tối đa **2 lệnh/ngày**, một vị thế; không tăng lot để gỡ. Nếu Equity giảm **50 USD so với đầu ngày UTC+7**, đóng vị thế nếu có và không mở mới hôm đó. Nếu Equity giảm **150 USD so với Equity đầu đợt v0**, dừng đợt để rà soát; không reset mốc để xóa lỗ. Mốc đầu đợt phải được ghi thực tế khi bắt đầu, không tự gán hôm nay.
- Trước mỗi lệnh, Q còn phải nhỏ hơn cả phần đệm còn lại đến hai ngưỡng nội bộ trên. Nếu bằng/vượt thì bỏ. Lệnh thắng không tăng trần Q trên 25 USD; quy tắc này không loại bỏ nguy cơ vượt ngưỡng do khớp giá xấu.
- Các ngưỡng trên là giới hạn NỘI BỘ thử nghiệm, không thay thế luật FTMO. Trước thực thi phải đọc lại cách tính Daily Loss/Max Loss, tính cả floating P/L/chi phí, giờ reset CE(S)T và kiểm tra phần đệm thực tế của tài khoản. Dùng điều kiện chặt hơn; không suy ngày UTC+7 là ngày tính lỗ của quỹ.
- Không coi đồng ý viết v0 là quyền gia sư đặt/hủy/đóng lệnh, kể cả demo. Không mua challenge, nạp tiền hay tác động khoản BTC Spot.

## Ví dụ minh họa — dữ kiện giả định, không phải chart hiện tại

Giả sử High lớn nhất trong 20 nến trước B = **1,1000**. Zone cố định: **1,0999–1,1001**.

| Nến | Open Bid | High Bid | Low Bid | Close Bid | Ý nghĩa |
|---|---|---|---|---|---|
| B | 1,0996 | 1,1008 | 1,0995 | 1,1005 | Close > zone High: ghi breakout, chưa Buy |
| R = B+1, ca A | 1,1004 | 1,1006 | 1,0997 | 1,1005 | Chạm zone, Close trên zone và > Open: tín hiệu giá đạt |
| R = B+1, ca B độc lập | 1,1004 | 1,1006 | 1,0997 | 1,1000 | Chạm nhưng Close trong zone: hủy setup |

Hai ca R là hai kịch bản khác nhau, không phải các nến liên tiếp trên một chart. Ca A chưa là lệnh đủ điều kiện nếu chưa qua lọc thời gian, tin, spread, khối lượng và margin.

Nếu ca A qua mọi lọc, giả sử nến kế tiếp có Bid 1,1005 và Ask 1,1006: Entry 1,1006; SL 1,0996; khoảng cách 10 pip; TP 1,1026. Chưa biết kết quả. Không vẽ thêm nến tương lai thắng để tạo cảm giác tín hiệu chắc chắn.

Ví dụ kiểm tra size riêng, KHÔNG phải thông số FTMO: giả sử C = 100.000 EUR/lot, commission cả vòng 7 USD/lot, min/step 0,01 lot, dự phòng slippage 1 pip. Với Q = 25 USD và khoảng cách 10 pip, lot thô = 25/(100 + 7 + 10), làm tròn xuống 0,21 lot; lỗ dự tính gồm dự phòng = 24,57 USD. TP theo giá cho lời gộp 42 USD, nhưng kết quả ròng/R phải trừ chi phí thực tế. Dự phòng không phải khoản phí đã phát sinh.

## Kiểm tra và nhật ký

- Bước đầu chỉ 3 tình huống để kiểm tra hiểu luật (đạt tín hiệu, không đạt, hết hạn); không dùng chúng để ước lượng edge. Gia sư làm mẫu, học viên giải thích một ca mới không gợi đáp án; không giao lại cả loạt phép tính.
- Nhật ký dùng sổ hiện có, nhãn BR-01 v0. Mỗi cơ hội ghi timestamp/feed/zone chốt trước, thời điểm B và lần chạm đầu, đạt/bỏ/lý do, giá dự kiến/thực thi, Q/size/SL/TP, phí, kết quả ròng theo Q, lỗi thực thi. Ghi cả phiên không có setup và ca bỏ lỡ; không biến ca bỏ lỡ thành trade có lợi nhuận.
- Khi chuyển backtest, chốt khoảng ngày liên tục và phần dữ liệu giữ riêng TRƯỚC khi xem kết quả. Tính mọi tín hiệu theo máy trạng thái trên, không lấy riêng chart đẹp. Nếu lịch sử không có Ask, phải công bố mô hình spread/phí và kiểm tra kịch bản chi phí xấu hơn.
- Cùng nến H1 chạm SL/TP: dùng dữ liệu nhỏ hơn để xác định nếu có; nếu không, báo cả hai kịch bản, dùng SL trước cho tổng thận trọng. Gap qua SL khớp ở giá khả dụng xấu hơn; không giả đúng SL. TP mô hình thận trọng không lấy tốt hơn mức TP. Thiếu dữ liệu thoát/lịch thì ghi thiếu, không gán 0.
- Tách hiệu suất theo đúng luật và lỗi người thực hiện. Không sửa sau một lần thua. Mọi thay đổi ý nghĩa tạo v1 và dùng dữ liệu mới; không gộp phiên bản để đẹp kết quả.
- Lượt viết này chỉ kiểm tra logic, ví dụ số và trình bày; chưa có dữ liệu backtest, chưa ước tính win rate, edge, độ phù hợp hay xác suất payout.

## Nguồn và quan hệ với course

- Khung viết luật và cách kiểm tra: [M05](../modules/05-phuong-phap.md), [M06](../modules/06-demo.md). Giữ LAB-01 là lịch sử riêng; không đổi đáp án cũ.
- Mục tiêu mới nhất: payout quỹ theo lời học viên. Ảnh học viên trong hội thoại xác nhận FTMO Free Trial, 2-Step, Swing, 10.000 USD, MT5 và chưa có lệnh ở thời điểm ảnh; không phải xác minh tài khoản thời gian thực.
- Tham số BR-01 là đề xuất gia sư, không lấy từ một chiến lược công bố có thành tích.
