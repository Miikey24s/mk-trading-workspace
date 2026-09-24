# Futures: Binance, OKX, Bybit — 10/09/2026

## Phạm vi

So sánh phí cho người dùng thông thường và quyết định có nên đổi sàn cho ngân sách học tối đa1triệu VND. Không phải audit an toàn sàn, không khuyến nghị nạp tiền hay cho phép giao dịch. Tiếp nối dữ kiện tài khoản Binance đã đọc cùng buổi; không lặp nghiên cứu broker forex.

## Nguồn và dữ kiện

- Binance: tooltip `Mức phí của bạn` trên tài khoản thực, BTCUSDC taker0,0400%, maker0,0000%; BTCUSDT taker0,0500%, maker0,0200%, đã xác minh lượt trước cùng buổi. Chưa kiểm tra ngày hết hạn/điều kiện ưu đãi. BTCUSDC min0,001BTC AND minnotional50USDC; BTCUSDT min0,001BTC AND50USDT. Không xem phí0% là miễn funding/spread/conversion. Không giả định USDC và USDT luôn ngang1USD.
- [OKX fees](https://www.okx.com/vi/fees), chọn Futures trực tiếp: người dùng thông thường maker0,0200%, taker0,0500%. Trang cảnh báo phí tùy khu vực; chưa mở hồ sơ/KYC để xác nhận phí thực tế người dùng, chưa xét rebate/ưu đãi cá nhân. Không mua token/cày volume để lấy VIP.
- [Bybit Trading Fee Structure](https://www.bybit.com/en/help-center/article/Trading-Fee-Structure), cập nhật2026-09-02: VIP0 perpetual/futures taker0,0550%, maker0,0200%. Trang ghi đây là base rates, phí thực tế tùy khu vực và My Fee Rate sau xác minh. URL đầu `/Bybit-Trading-Fee-Structure` báo không hỗ trợ; tìm kiếm một lần dẫn tới URL chính xác trên và đọc bảng trực tiếp. Không dùng snippet làm bằng chứng bảng phí.

## So sánh có điều kiện

Minh họa notional vào và ra đều xấp xỉ77đơn vị stablecoin, hai lượt đều taker: Binance USDC0,0616USDC, Binance USDT/OKX0,077USDT (OKX giả định hợp đồng USDT áp base rate), Bybit0,0847USDT (giả định hợp đồng USDT áp base rate). Chỉ là trading fees, không phép đo tổng chi phí. Phép tính kiểm tra PowerShell decimal.

Binance BTCUSDC rẻ hơn trên mức execution fee đang thấy, không chứng minh rẻ nhất toàn thị trường hoặc tốt nhất/an toàn nhất. Spread/slippage phải so cùng thời điểm/size, funding theo cùng kỳ giữ, nạp-rút/chuyển đổi theo kênh cùng tên và quote thật. Chưa benchmark những mục này hoặc kích thước hợp đồng OKX/Bybit; không dựng bảng điểm giả.

Khuyến nghị: giữ Binance làm nơi học hiện tại, chưa đăng ký thêm sàn chỉ vì phí. Điểm nghẽn là min0,001BTC và SL hợp lý dưới ngân sách dự tính; không tăng leverage/risk hoặc bóp SL cho vừa. Nếu sau này Binance không hỗ trợ size phù hợp, mới so ứng viên khác theo minimum exposure chứ không chỉ phí. 500kBTC hold giữ riêng. Pháp lý/điều kiệnVN chưa được giải quyết; tạm tách theo yêu cầu, không dùng nơi khác làm cách vượt hạn chế.

Không liên hệ support, đăng ký/KYC, chuyển tiền, đặt lệnh, sửa setting hoặc cài plugin.
