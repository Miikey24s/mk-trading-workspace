# Trading Statistics Hub / Kho thống kê Trading

Đây là source of truth để gom mọi thống kê dùng trước khi chọn phương pháp trading. Mục tiêu là có một cấu trúc đủ rộng để thêm hoặc bỏ dữ liệu mà không phải viết lại toàn bộ báo cáo.

## Cách dùng

- `evidence.csv`: mỗi dòng là một claim/thống kê độc lập. Đây là phần dễ thêm, xoá, lọc và sau này có thể import vào spreadsheet/database.
- `diagrams.md`: các sơ đồ giúp hiểu quan hệ giữa các biến; gồm cả sơ đồ tái tạo từ hai video YouTube của Mulham Trading.
- `sources.md`: registry nguồn, phạm vi, loại bằng chứng và lưu ý transfer.
- `glossary.md`: từ điển Anh-Việt cho các thuật ngữ thống kê/trading dùng trong hub.
- `../strategy-probability-framework-2026-09-15.md`: methodology audit dài, giải thích tại sao không được biến mọi claim thành một xác suất cá nhân.

## Quy ước song ngữ / Bilingual convention

- Nội dung dành cho người đọc dùng dạng **Việt (English)** ở lần xuất hiện quan trọng đầu tiên: `Kỳ vọng (Expectancy)`, `Tỷ lệ thắng (Win rate)`, `Mức sụt giảm (Drawdown)`.
- Tên source/paper/video giữ nguyên English để tra cứu chính xác.
- Các field kỹ thuật trong `evidence.csv` như `category`, `metric`, `status` giữ English ổn định để dễ filter, sort và xử lý bằng code.
- Khi một thuật ngữ chưa rõ, xem `glossary.md`; file này là nơi chuẩn hoá nghĩa tiếng Việt dùng xuyên suốt hub.

### Cách đọc cột trong `evidence.csv`

| Field trong CSV | Nghĩa tiếng Việt |
| --- | --- |
| `category` | nhóm thống kê |
| `question` | câu hỏi mà record đang trả lời |
| `unit` | đơn vị đang đo |
| `metric` | chỉ số được đo |
| `estimate` | kết quả/ước lượng quan sát được |
| `uncertainty` | độ bất định và assumption quan trọng |
| `evidence_grade` | cấp bằng chứng |
| `source_id` | mã nguồn tham chiếu trong `sources.md` |
| `scope` | population/market/phạm vi áp dụng |
| `transfer_to_user` | khả năng áp dụng sang trường hợp của mình |
| `decision_impact` | mức ảnh hưởng tới quyết định chọn strategy |
| `status` | trạng thái kiểm chứng |
| `notes` | lưu ý để tránh hiểu sai |

## Quy tắc cốt lõi

Không có một cột duy nhất tên là `xác suất thắng` áp cho mọi thứ. Mỗi record phải nói rõ:

1. **Đơn vị đang đo**: trade, trader, account, tháng, strategy, prop challenge, v.v.
2. **Kết quả đo (Outcome)**: tỷ lệ thắng (win rate), kỳ vọng (EV/expectancy), lợi nhuận (return), mức sụt giảm (drawdown), xác suất vượt challenge (pass probability), khả năng sống sót (survival), mức tuân thủ luật (rule adherence), v.v.
3. **Nhóm áp dụng / thị trường / khung thời gian (Population / market / timeframe)**: claim áp cho ai và ở đâu.
4. **Ước lượng (Estimate)**: con số hoặc kết luận quan sát được.
5. **Độ bất định (Uncertainty)**: khoảng tin cậy (CI), range, model uncertainty hoặc `unknown`.
6. **Cấp bằng chứng (Evidence grade)**: độ mạnh của bằng chứng.
7. **Khả năng áp dụng cho mình (Transfer to user)**: mức có thể dùng làm prior cho trường hợp của mình.
8. **Tác động lên quyết định (Decision impact)**: claim này có ảnh hưởng đến việc chọn strategy không.
9. **Trạng thái (Status)**: fact đã kiểm tra, creator model, hypothesis, pending reproduction, v.v.

## Bảng mẹ

| Nhóm | Ví dụ biến | Đo cái gì | Outcome phù hợp | Dùng để chọn strategy? |
| --- | --- | --- | --- | --- |
| Tỷ lệ nền (Base rate) | retail CFD, day trader | trader/account | loss rate, survival, profitable rate | Có, làm prior |
| Nhân khẩu học (Demographic) | giới tính (gender), tuổi (age) | trader | return, turnover, behavior | Thấp, chỉ khi có cơ chế rõ |
| Kinh nghiệm (Experience) | số năm, số lệnh | trader | persistence, return, error rate | Trung bình |
| Hành vi (Behavior) | turnover, leverage, rule breaks | trader | net return, error, drawdown | Cao |
| Họ phương pháp (Method family) | trend, mean reversion, breakout | strategy family | EV, Sharpe, drawdown | Cao |
| Setup / mẫu vào lệnh | breakout-retest, pullback | trade/strategy | win rate, payoff, EV | Rất cao khi rule rõ |
| Thiết kế hệ thống (System design) | win rate, RR, filters | strategy | expectancy, robustness | Rất cao |
| Rủi ro (Risk) | risk/trade, position size | account | drawdown, ruin/pass probability | Rất cao |
| Chi phí (Cost) | spread, commission, slippage | trade/strategy | EV after costs | Rất cao |
| Biến động kết quả (Variance) | thứ tự thắng/thua | path/account | streak, DD, pass/fail | Rất cao |
| Luật prop firm (Prop rules) | max DD, daily loss, trailing DD | account/challenge | pass probability | Rất cao nếu trade prop |
| Độ bền (Robustness) | OOS, holdout, parameter sensitivity | strategy | performance decay, DSR/PBO | Rất cao |
| Khả năng thực thi cá nhân (Personal execution) | adherence, missed/extra trades | trader + strategy | realized EV vs model EV | Rất cao |

## Sơ đồ tổng

```text
EXTERNAL EVIDENCE / BASE RATES
          |
          v
  METHOD FAMILY PRIOR
          |
          v
 CANDIDATE RULESET ---------> COMPLEXITY / OVERFIT RISK
          |                            |
          v                            v
 WIN RATE + PAYOFF + COST ------> EXPECTANCY / EDGE
          |
          +----------------------+
          |                      |
          v                      v
       VARIANCE             POSITION SIZE
          |                      |
          +-----------+----------+
                      v
               ACCOUNT PATH
                      |
          +-----------+-----------+
          |                       |
          v                       v
   PERSONAL ACCOUNT          PROP RULES
   DD / survival             pass / fail
          |                       |
          +-----------+-----------+
                      v
               REAL OUTCOME
                      |
                      v
      OOS / HOLDOUT / FORWARD / ADHERENCE
                      |
                      v
             CONFIDENCE + DECISION
```

## Cấp bằng chứng / Evidence grade

| Grade | Ý nghĩa | Cách dùng |
| --- | --- | --- |
| A | Rule khóa trước, dữ liệu đúng instrument/venue, realistic costs, untouched holdout/forward | Có thể dùng trực tiếp nhất cho candidate |
| B | Nghiên cứu lớn, thiết kế rõ, market/population khá tương đồng | Prior mạnh |
| C | Proxy khác market/timeframe hoặc transfer còn xa | Gợi ý hướng |
| D | Survey nhỏ, self-report, creator simulation chưa tái lập | Hypothesis / illustration |
| E | Testimonial, screenshot, claim marketing không raw data | Không dùng để chọn strategy |

## Trạng thái chuẩn / Standard status

| Status | Ý nghĩa |
| --- | --- |
| `verified_external` | Claim khớp nguồn gốc đã đọc |
| `derived_math` | Tính từ công thức/giả định đã ghi rõ |
| `video_model_example` | Ví dụ/mô hình do video trình bày; không phải xác suất phổ quát |
| `pending_reproduction` | Có claim/mô hình nhưng chưa tự tái lập calculation/simulation |
| `candidate_specific_pending` | Chờ backtest đúng candidate của mình |
| `unknown` | Không đủ evidence để gán số |

## Nguyên tắc thêm một thống kê mới

Thêm một dòng vào `evidence.csv`. Nếu nguồn mới chưa có, thêm một entry vào `sources.md`. Chỉ thêm sơ đồ vào `diagrams.md` khi nó giải thích một quan hệ mới; không tạo sơ đồ riêng cho mỗi con số.

Khi xoá một claim, xoá record khỏi `evidence.csv`; chỉ xoá source nếu không còn record nào tham chiếu tới source đó.

## Trạng thái hiện tại

- Hub mới là cấu trúc sống, không phải bảng xếp hạng strategy cuối cùng.
- `BR-01` vẫn là candidate, chưa có edge được chứng minh.
- Hai video YouTube đã được đưa vào dưới dạng **creator model / teaching diagram**, tách khỏi academic/external evidence.
- Các con số pass probability từ video prop firm chưa được tự tái lập bằng simulation, nên không dùng như xác suất thật cho FTMO hay tài khoản cụ thể.
