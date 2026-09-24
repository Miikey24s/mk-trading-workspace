# Tra cứu nhanh — thuật ngữ và phép tính

Chỉ để tra khi học trading, không có bài dịch hay học thuộc English. Quy ước số Việt: 1.000 là một nghìn, 0,01 là một phần trăm; trên nền tảng có thể dùng `1,000` và `0.01`. Phải đọc định dạng trước nhập lệnh.

## Thuật ngữ theo ngữ cảnh

| Thuật ngữ | Hiểu trong course |
|---|---|
| Forex / FX | Giao dịch liên quan tỷ giá giữa hai đồng tiền |
| Base / quote currency | Đồng đứng trước / đồng định giá đứng sau; EUR/USD là USD cho mỗi EUR |
| Bid / ask | Giá bạn bán / giá bạn mua |
| Spread | Chênh ask − bid |
| Long / short | Vị thế hưởng lợi khi giá lên / khi giá xuống, trước chi phí |
| Position size / notional | Khối lượng / giá trị danh nghĩa của toàn bộ vị thế, không phải ký quỹ |
| Margin | Tiền bảo đảm theo yêu cầu; không phải phí hay mức lỗ tối đa |
| Allowed leverage | Tỷ lệ đòn bẩy cho phép dùng để xác định yêu cầu ký quỹ trong mô hình đơn giản |
| Effective leverage | Giá trị vị thế thực tế so với equity; khác mức leverage cho phép |
| Balance / equity | Số dư ghi nhận / giá trị có tính lời/lỗ đang mở |
| Free margin | Equity trừ ký quỹ đang dùng, theo mô hình không có điều chỉnh khác |
| Pip / lot | Đơn vị dịch chuyển giá / đơn vị khối lượng theo hợp đồng |
| Market / limit / stop | Lệnh giao dịch ngay / giới hạn giá / kích hoạt ở một ngưỡng |
| SL / TP | Stop-loss / take-profit: mức hoặc lệnh thoát dự kiến để hạn chế lỗ/chốt lời |
| Commission / swap | Phí môi giới / điều chỉnh tài trợ khi giữ qua mốc quy định |
| Slippage | Giá thực khớp khác giá dự tính, có thể tốt hơn hoặc xấu hơn |
| OHLC / timeframe | Giá mở, cao nhất, thấp nhất, đóng / khung thời gian |
| Drawdown | Mức giảm từ đỉnh theo thước đo đã định nghĩa |
| R / expectancy | Đơn vị ngân sách rủi ro ban đầu / lời-lỗ trung bình kỳ vọng hoặc ước lượng trong mẫu |
| Backtest / forward test | Thử trên dữ liệu quá khứ / quan sát kết quả đến sau khi đã khóa luật |
| Out-of-sample | Dữ liệu chưa dùng để chọn hoặc điều chỉnh phương pháp |
| Prop firm / challenge / payout | Công ty giao dịch vốn riêng / bài đánh giá / khoản trả thưởng theo hợp đồng; không mặc định là tiền bạn sở hữu |

## Công thức có phạm vi

Với EUR/USD, tài khoản USD, hợp đồng tuyến tính và giá thực khớp:

- `Q EUR = lots × 100.000`, chỉ khi hợp đồng quy định standard lot như vậy.
- `Buy P/L USD = Q × (giá đóng − giá mở)`.
- `Sell P/L USD = Q × (giá mở − giá đóng)`.
- `Số pip = độ dịch chuyển giá / 0,0001`; `USD/pip = Q × 0,0001`.
- `Net P/L = P/L từ giá thực khớp − chi phí riêng bị trừ + khoản riêng được cộng`. Không trừ spread/slippage lần nữa nếu đã nằm trong giá khớp.
- `Initial margin USD = notional USD / leverage cho phép` chỉ trong mô hình margin đơn giản. Luật thật có thể khác.
- `Equity = balance + floating P/L`; `free margin = equity − used margin`, nếu không có credit/điều chỉnh khác.
- `% vốn mất = tiền lỗ / equity trước giao dịch × 100%`.
- `Giá trị lệnh USD = ngân sách lỗ USD / khoảng SL dạng tỷ lệ`, giả định chưa phí và khớp đúng SL.
- `Lots = (ngân sách lỗ − phí cố định dự tính) / (SL pip × 10)` cho EUR/USD standard lot trong tài khoản USD. Phí theo lot phải tính riêng đúng cơ chế, không ép vào giả định cố định.
- `Kết quả R = net P/L / ngân sách lỗ ban đầu`.
- `% drawdown = (đỉnh trước đó − giá trị hiện tại) / đỉnh trước đó × 100%`. Phải ghi rõ equity hay balance.

Ví dụ gộp: tài khoản 1.000 USD, Buy 0,01 lot = 1.000 EUR ở 1,1000; notional 1.100 USD. Leverage cho phép 20:1 → margin ban đầu 55 USD. Đóng ở 1,0980 → −20 pip = −2 USD trước phí, không phải −55 và không nhân thêm 20. Margin có thể thay đổi theo định giá/luật thật; bài dùng yêu cầu ban đầu.

**Không suy từ các công thức này:** mức SL chắc chắn, lợi thế một chiến lược, luật mọi quỹ, hay tính hợp pháp của một sản phẩm cho người Việt Nam.
