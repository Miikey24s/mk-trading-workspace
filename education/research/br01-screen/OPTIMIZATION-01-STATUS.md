# BR-01 optimization 01 — trạng thái

Ngày 16/09/2026.

## Đã khóa trước dữ liệu mới

- Protocol: [OPTIMIZATION-01-PROTOCOL.md](OPTIMIZATION-01-PROTOCOL.md).
- Hypothesis: `H1_R_BODY_5P` — giữ BR-01 v0 và thêm `Close R - Open R >= 5 pip`.
- Discovery basis: 21 trade conservative đã biết; body 5 pip là hypothesis post-hoc từ
  sample này, không phải edge. Trên discovery nó giữ 5/5 winner, loại 10/16 loser và
  còn `+2,6751R` so với `-5,8983R` baseline.
- Window khóa để screen mới: 25/11/2019 07:00 UTC đến 01/01/2021 00:00 UTC.
- 2021–2025 vẫn chưa dùng trong optimization 01; holdout 2025 chưa mở.

## Implementation

- `optimize_br01.py` là shadow diagnostic tách riêng khỏi `br01_engine.run`.
- Shadow giữ pattern, news, spread, cost, slippage, entry, SL/TP, time exit, một vị thế
  và tối đa 2 trade/ngày; chỉ bỏ daily/total account-loss gate và reset synthetic capital
  sau mỗi trade để đo setup bằng Q cố định 25 USD.
- Shadow result, nếu chạy được, không phải BR-01 v0 equity curve và không dùng làm bằng
  chứng pass/payout/challenge.
- `test_br01_optimization.py` kiểm tra v0 shadow, filter dưới 5 pip và boundary đúng 5 pip.
- Toàn bộ backtester suite hiện đạt **107 tests**: 63 offline/QDM + 44 data/MT5.

## Kết quả unseen development

Blocker của lượt trước không tái hiện khi chạy trực tiếp bằng bundled Python đã dùng cho
backtester. Runner hoàn tất và lưu receipt:
`quality-data/br01-engine/optimization-01-432324d7383d.json.gz`.

| Scenario | Shadow v0 | H1_R_BODY_5P | Gate |
|---|---:|---:|---|
| Conservative | 19 trades, 6 wins, `-5,8788R` | 14 trades, 4 wins, `-5,0700R` | Fail |
| Stress | 19 trades, 5 wins, `-9,2288R` | 14 trades, 4 wins, `-5,7928R` | Fail |

H1 có cải thiện tổng R so với shadow v0 ở cả hai scenario, nhưng **net R vẫn âm**. Theo
gate đã khóa trước dữ liệu mới, hypothesis bị reject; không đổi threshold sau kết quả này.

Trạng thái H1: `rejected_after_unseen_development_screen`. Chưa tạo v1; 2021–2025 vẫn
chưa dùng trong optimization 01 và holdout 2025 vẫn chưa mở.
