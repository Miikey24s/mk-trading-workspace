# Sơ đồ / Diagrams

Các sơ đồ dưới đây là bản tái tạo ý nghĩa để dễ chỉnh sửa và nối với evidence matrix. Chúng không phải bản sao pixel của slide gốc.

Quy ước: nhãn quan trọng dùng **Việt (English)** để vừa dễ hiểu vừa giữ đúng thuật ngữ tra cứu.

## 1. Sơ đồ mẹ cho mọi thống kê

```text
AI / Ở ĐÂU? (WHO / WHERE?)
Nhóm mẫu + thị trường + khung thời gian + loại tài khoản
                    |
                    v
ĐANG ĐO CÁI GÌ? (WHAT IS BEING MEASURED?)
lệnh / trader / strategy / account / tháng / challenge
                    |
                    v
KẾT QUẢ NÀO? (WHAT OUTCOME?)
tỷ lệ thắng / EV / lợi nhuận / DD / phá sản / pass / tuân thủ
                    |
                    v
ƯỚC LƯỢNG + ĐỘ BẤT ĐỊNH (ESTIMATE + UNCERTAINTY)
ước lượng điểm + CI/range/độ bất định mô hình
                    |
                    v
CHẤT LƯỢNG BẰNG CHỨNG (EVIDENCE QUALITY)
thiết kế nguồn + sample + khả năng chuyển giao + tái lập
                    |
                    v
CÁCH DÙNG ĐỂ RA QUYẾT ĐỊNH (DECISION USE)
prior -> lọc candidate -> backtest -> holdout -> forward test
```

Mục tiêu: bất kỳ thống kê mới nào cũng phải trả lời được sáu tầng này trước khi được dùng để chọn phương pháp.

---

## 2. Video: The Math of Winning in Trading

Source: `SRC-YT-TRADING-MATH` - Mulham Trading - `BAfRVpKIxZ4`.

### 2.1 Kỳ vọng (Expectancy)

Video: khoảng `01:17-03:17`.

```text
             PHÍA THẮNG (WIN SIDE)
Tỷ lệ thắng (Win rate) ---> x Lời TB (Avg win)
                              |
                              +-----+
                                    |
                                    v
                             EV LÝ THUYẾT (THEORETICAL EV)
                                    ^
                                    |
                              +-----+
                              |
Tỷ lệ thua (Loss rate) ---> x Lỗ TB (Avg loss)
             PHÍA THUA (LOSS SIDE)

EV = (Win rate x Avg win) - (Loss rate x Avg loss)

EV LÝ THUYẾT (THEORETICAL EV)
      |
      - spread
      - commission
      - slippage
      v
KỲ VỌNG THỰC TẾ TRƯỚC CÁC LỖI THỰC THI KHÁC
(REALIZED EXPECTANCY BEFORE OTHER EXECUTION ERRORS)
```

Điểm đưa vào hub: win rate một mình không đủ; payoff và cost phải cùng nằm trong model.

### 2.2 Một lệnh (trade) không nói lên lợi thế (edge)

Video: khoảng `03:17-04:13`.

```text
                    CÙNG KỲ VỌNG (SAME EXPECTANCY)
                         |
          +--------------+--------------+
          |                             |
          v                             v
 chuỗi may mắn sớm                chuỗi xấu sớm
 (early lucky sequence)           (early bad sequence)
          |                             |
          v                             v
 đường vốn nhìn rất đẹp          đường vốn nhìn như bị hỏng
          |                             |
          +--------------+--------------+
                         |
                         v
                sample lớn hơn mới làm rõ
                mức trung bình nền
```

Không dùng mốc `100 trades` trong video như luật đủ mẫu phổ quát. Sample adequacy còn phụ thuộc variance, dependence, payoff distribution và số variants đã thử.

### 2.3 Thiết kế hệ thống (System design): trade-off giữa win rate và reward

Video: khoảng `04:13-06:25`.

```text
WIN RATE CAO                                      REWARD/RISK CAO
     |                                                   |
     |  thường phải trả giá bằng payoff nhỏ hơn          |
     +-------------------- trade-off --------------------+
                                                         |
                     [ vùng cân bằng thực tế / practical sweet spot ]
                                                         |
     +-------------------- trade-off --------------------+
     |  payoff lớn thường đi cùng hit-rate thấp hơn      |
     |                                                   |
REWARD/RISK THẤP                                     WIN RATE THẤP
```

Slide video dùng heatmap để minh họa một vùng "sweet spot". Đây là teaching model; không có một ô sweet spot cố định cho mọi market.

### 2.4 Tỷ lệ thắng hòa vốn (Breakeven win rate)

Video: khoảng `06:25-06:54`.

```text
Giả sử lỗ trung bình (average loss) = 1R

Reward 1R  -> tỷ lệ thắng hòa vốn 50%
Reward 2R  -> tỷ lệ thắng hòa vốn 33.3%
Reward 3R  -> tỷ lệ thắng hòa vốn 25%
Reward 4R  -> tỷ lệ thắng hòa vốn 20%

Formula: BE = 1 / (Reward_in_R + 1)
```

Đây là breakeven trước costs. Khi có costs, win rate cần thiết sẽ cao hơn hoặc average net reward phải lớn hơn.

### 2.5 Phương sai / biến động kết quả (Variance)

Video: khoảng `06:54-08:15`.

```text
 CÙNG RULE + CÙNG KỲ VỌNG (SAME RULES + SAME EXPECTANCY)
             |
       thứ tự kết quả ngẫu nhiên (random/order path)
             |
    +--------+--------+
    |        |        |
    v        v        v
 mượt      trung     drawdown
 (smooth)  bình      nặng
    |        |        |
    +--------+--------+
             |
             v
 trải nghiệm ngắn hạn khác nhau
 dù cùng một model dài hạn
```

Đây là lý do hub tách `edge` khỏi `path risk`.

### 2.6 Ngụy biện con bạc (Gambler's fallacy)

Video: khoảng `08:15-09:19`.

```text
L -> L -> L -> L
             |
             x  "next one HAS to win"
             |
             v
Chỉ hợp lý nếu có bằng chứng rằng P(kết quả kế tiếp | chuỗi trước) đã thay đổi.

Theo mô hình IID:
P(next win | four losses) = P(next win)
```

Lưu ý: real trades có thể cluster theo regime, nên independence là assumption cần kiểm tra.

### 2.7 Kích thước vị thế (Position sizing)

Video: khoảng `09:19-11:30`.

```text
GIÁ TRỊ TÀI KHOẢN (ACCOUNT EQUITY)
     |
     x % rủi ro đã chọn
     v
SỐ TIỀN RỦI RO MỖI LỆNH (DOLLAR RISK PER TRADE)
     |
     +-------------------------------+
     |                               |
     v                               v
stop rộng                         stop hẹp
     |                               |
     v                               v
vị thế nhỏ hơn                   vị thế lớn hơn
     |                               |
     +---------------+---------------+
                     v
            số tiền risk dự kiến tương đương
```

### 2.8 Mức sụt giảm / rủi ro phá sản (Drawdown / Risk of ruin)

Video: khoảng `11:30-12:36`.

```text
rủi ro mỗi lệnh (risk per trade) tăng
          |
          v
đường vốn nhạy hơn với thứ tự chuỗi thắng/thua
          |
          v
xác suất drawdown sâu tăng
          |
          v
khả năng sống sót / phục hồi khó hơn
```

Exact curve in the video remains `pending_reproduction` because the underlying simulation assumptions are not fully documented in the slide alone.

---

## 3. Video: The Math of Winning in Prop Firms

Source: `SRC-YT-PROP-MATH` - Mulham Trading - `vGSpbspmGoM`.

### 3.1 "Tài khoản thật" là phần được phép lỗ (Allowed loss boundary)

Video: `00:22-04:31`.

```text
Quy mô tài khoản danh nghĩa (Nominal account size)
       |
       v
không giống phần vốn thực sự được phép mất

VỐN BAN ĐẦU (START EQUITY)
    |
    +---------------------------+
    |                           |
    v                           v
MỤC TIÊU LỢI NHUẬN          NGƯỠNG THẤT BẠI
(PROFIT TARGET)             (FAILURE BOUNDARY)
pass                         fail

Mô hình pass = chạm mục tiêu trước khi chạm ngưỡng thất bại.
```

Đây là mental model cho challenge, không thay thế exact rules của từng firm.

### 3.2 Lợi thế (Edge) không phải xác suất pass (Pass probability)

Video: `04:31-11:38`.

```text
Tỷ lệ thắng + lời TB + lỗ TB
              |
              v
           KỲ VỌNG (EXPECTANCY)
              |
              +--------------------+
                                   |
Kích thước vị thế (Position size) -+
                                   |
Thứ tự lệnh / variance ------------+
                                   |
Các ngưỡng challenge --------------+
                                   |
                                   v
                         XÁC SUẤT PASS / FAIL
```

Hai strategy có expectancy gần nhau vẫn có thể có pass probability khác nếu payoff distribution và path khác nhau.

Creator example trong video:

```text
same/similar expected value
      |
      +--> Strategy A -> modeled pass ~68%
      +--> Strategy B -> modeled pass ~57%
      +--> Strategy C -> modeled pass ~42%

C: lower hit rate, relies more on larger winners.
```

Các tỷ lệ trên là output của model trong video, chưa phải base rate thực tế.

### 3.3 Ma trận rủi ro x tỷ lệ thắng x reward (Risk x win rate x reward matrix)

Video: khoảng `14:50-16:45` trong phần Risk.

```text
                     TỶ LỆ THẮNG (WIN RATE)
                 40% ... 50% ... 60%
               +-----------------------+
RR 1:1         |                       |
RR 2:1         |   % pass theo model   |  <- lặp bảng cho
RR 3:1         |                       |     risk 0.5%, 1%, 2%
               +-----------------------+

Cách hiểu:
edge + mức risk + thứ tự kết quả -> xác suất chạm target trước failure boundary
```

Hai ví dụ creator dùng để dạy sự khác nhau giữa edge và chance-to-pass:

```text
Ví dụ strategy có EV dương: WR 60%, RR 3:1
risk 0.5% -> ~100% modeled pass
risk 1.0% -> ~95%
risk 2.0% -> ~79%

Ví dụ strategy có EV âm: WR 40%, RR 1:1
risk 0.5% -> ~1% modeled pass
risk 1.0% -> ~7%
risk 2.0% -> ~19%
```

Ý chính: tăng size có thể làm một strategy xấu "lucky-pass" nhanh hơn, nhưng không biến nó thành strategy có edge.

### 3.4 Luật prop firm thêm các ngưỡng ràng buộc (Prop rules add boundaries)

Video: `17:09-20:57`.

```text
ĐƯỜNG ĐI CỦA STRATEGY (STRATEGY PATH)
    |
    + ngưỡng max drawdown
    |
    + ngưỡng lỗ ngày (daily loss)
    |
    + ngưỡng trailing drawdown
    |
    + giới hạn consistency / distribution
    v
ít đường vốn hợp lệ hơn
    |
    v
xác suất pass theo model thấp hơn nếu các yếu tố khác giữ nguyên
```

Visual example shown in the video:

```text
strategy only      100%
      + max DD      72%
      + daily loss  61%
      + trailing DD 49%
      + consistency 42%
```

These are creator-model values only. Do not reuse them as FTMO/Topstep/FundedNext probabilities without reproducing the exact simulation and rules.

### 3.5 Drawdown tĩnh và drawdown bám theo (Static vs trailing drawdown)

Video: khoảng `17:40-19:35`.

```text
NGƯỠNG TĨNH (STATIC FLOOR)

equity     /\/\/\___/\
floor  --------------------  fixed


NGƯỠNG BÁM THEO (TRAILING FLOOR)

equity     /\/\/\___/\
floor  ____/__/__/-----------  ratchets upward with watermark
```

Video tách thêm:

```text
Drawdown bám theo (Trailing drawdown)
      |
      +--> intraday: cập nhật theo đỉnh equity trong ngày
      |
      +--> end-of-day: cập nhật theo balance/equity cuối ngày theo rule
```

Exact implementation must be read from current firm/account rules.

### 3.6 Kinh tế đầy đủ của prop firm (Full prop-firm economics)

Video: `20:57-22:42`.

```text
TỶ LỆ THẮNG + LỜI/LỖ TB
          |
          v
         LỢI THẾ (EDGE)
          |
          +--------- KÍCH THƯỚC VỊ THẾ (POSITION SIZE)
          |                |
          |                v
          |       mỗi lệnh làm tài khoản
          |       biến động mạnh đến đâu
          |
          +--------- LUẬT CHALLENGE (CHALLENGE RULES)
                           |
                           v
                 đường vốn nào còn sống sót
                           |
                           v
                   XÁC SUẤT ĐƯỢC FUNDED
                           |
                    LUẬT PAYOUT (PAYOUT RULES)
                           |
                           v
                     TÀI KHOẢN ĐƯỢC PAYOUT
                           |
             payout - toàn bộ phí thử challenge
                           |
                           v
                      LỢI NHUẬN THỰC (REAL RETURN)
```

Creator's illustrative arithmetic:

```text
100 challenge attempts x $150 fee = $15,000 cost
6 payouts x $2,000                 = $12,000 received
                                      -------
net                                  -$3,000
= -$30 per challenge attempt
```

Đây là ví dụ toán học, không phải thống kê population về prop firms.

---

## 4. Cách nối hai video vào hub thống kê / How the two videos connect

```text
VIDEO 1: TOÁN TRADING CÁ NHÂN / TỔNG QUÁT
(PERSONAL / GENERAL TRADING MATH)

tỷ lệ thắng + payoff
       -> kỳ vọng (expectancy)
       -> chi phí (costs)
       -> variance
       -> position sizing
       -> drawdown / survival

                         |
                         v

VIDEO 2: THÊM RÀNG BUỘC PROP FIRM
(ADD PROP-FIRM CONSTRAINTS)

toán strategy tổng quát
       + ngưỡng target/fail
       + daily/max/trailing DD
       + consistency rules
       + payout rules
       + attempt fees
       -> xác suất pass (pass probability)
       -> xác suất payout (payout probability)
       -> lợi nhuận ròng thực (real net return)
```

Đây là lý do `evidence.csv` tách các metric `expectancy`, `drawdown_probability`, `pass_probability` và `net_return` thay vì gom chúng thành một chữ "win".
