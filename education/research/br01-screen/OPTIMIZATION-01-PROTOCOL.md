# BR-01 optimization 01 — retest body screen

Khóa trước khi đọc performance mới ngày 16/09/2026. Đây là vòng tối ưu đầu tiên theo
`DEVELOPMENT-LOOP.md`; không sửa `BR-01 v0`, không mở 2021–2025 và không đặt lệnh.

## Discovery đã biết

Episode conservative đầu tiên dừng ngày 21/11/2019 sau 21 lệnh, tổng `-5,8983R`.
Phân tích 21 lệnh này chỉ dùng để **sinh giả thuyết**, không dùng để xác nhận nó:

- 5 lệnh thắng có thân nến retest bullish từ 5,3 pip trở lên.
- Rule hiện tại chỉ yêu cầu `Close R > Open R`, nên vẫn nhận các nến gần doji.
- Ngưỡng tròn 5 pip trên chính sample discovery giữ 5/5 lệnh thắng, loại 10/16 lệnh
  thua và còn `+2,6751R`. Con số này là in-sample/post-hoc, không phải edge.

Không quét grid để tìm threshold tốt nhất. Chọn **5 pip** vì đây là một mức tròn,
dễ áp dụng tay và trực tiếp siết điều kiện bullish-body đang quá lỏng.

## H1 khóa trước test

Giữ toàn bộ BR-01 v0, chỉ thêm một điều kiện sau khi first retest đã thỏa rule v0:

`Close R - Open R >= 5 pip` (`>= 50` price points ở precision 0,00001).

Tên trong vòng này: `H1_R_BODY_5P`. Chưa gọi `BR-01 v1` trước khi qua screen mới.

## Test mới chưa xem P/L

- Window: **25/11/2019 07:00 UTC đến 01/01/2021 00:00 UTC**.
- Đây là phần development nằm sau thời điểm episode conservative cũ đã dừng; trước
  vòng này chưa chạy strategy P/L trên phần đó.
- Chạy song song shadow `v0` và `H1_R_BODY_5P` trên cùng window, cả conservative và
  stress cost profile.
- Shadow runner giữ pattern, H20/zone, first touch, 6 bars, lịch, news, spread,
  commission, slippage, entry, SL, TP, time exit, một vị thế và tối đa 2 lệnh/ngày.
- Chỉ tắt daily/total account loss gate và dùng `Q=25 USD` độc lập cho mỗi trade để
  tách chất lượng setup khỏi việc một episode tài khoản hết risk buffer. Sau mỗi trade
  shadow capital quay về 10.000 USD. Vì vậy đây **không phải equity curve BR-01 v0**,
  không dùng để mô phỏng pass/payout hay drawdown tài khoản.

## Gate của vòng 01

H1 chỉ được **đi tiếp để thiết kế v1**, chưa được gọi có edge, khi ở cả conservative
và stress:

1. có ít nhất 10 trade sau filter;
2. có ít nhất 3 trade thắng;
3. tổng net R > 0;
4. tổng net R cao hơn shadow v0 cùng window.

Nếu thiếu mẫu thì kết luận `inconclusive`. Nếu đủ mẫu mà fail một điều kiện thì reject
H1. Không đổi threshold sau khi xem kết quả này. Một H1 đi tiếp vẫn phải được test bằng
protocol versioned trên development/validation tiếp theo; 2021–2022 chưa được mở trong
vòng này.

