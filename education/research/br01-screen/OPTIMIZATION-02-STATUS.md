# BR-01 optimization 02 — trạng thái

Đối chiếu ngày 02/10/2026 từ receipt của vòng đã khóa ngày 16/09/2026.

**H2_B_BODY_5P bị reject; chưa tạo v1, chưa có bằng chứng edge.**
Protocol [vòng 02](OPTIMIZATION-02-PROTOCOL.md) giữ v0 và chỉ thêm điều kiện thân nến
breakout ≥ 5 pip, không ghép filter H1 đã bị reject. 2021 đã được chuyển thành
development trước test; không còn là independent validation. Receipt ghi
`validation_2022_accessed=false`, `holdout_2025_accessed=false`.

Nguồn kết quả là
`quality-data/br01-engine/optimization-02-3453a10625a4.json.gz`, file SHA-256:
`cb5515126488ded98d423751a37d5c291d3fb0c33b69bdd05bcc75dbd96bbe1c`.
Protocol, engine và code vòng 02 vẫn khớp hash trong receipt. Đây là kết quả đã lưu,
không phải performance mới chạy ngày 02/10.

| Scenario | Shadow v0 | H2_B_BODY_5P | Gate |
|---|---|---|---|
| Conservative | 10 trades, 1 winner, −5,05R | 10 trades, 1 winner, −5,05R | Reject |
| Stress | 10 trades, 1 winner, −5,7452R | 10 trades, 1 winner, −5,7452R | Reject |

Candidate đạt ngưỡng 10 trades nhưng thiếu 3 winner, net R không dương và không tốt
hơn shadow v0. Hai scenario có trade records hoàn toàn giống baseline. Shadow dùng
Q cố định 25 USD/trade, tắt daily/total account-loss gate và reset synthetic capital;
đây không phải equity curve của BR-01 v0 hoặc bằng chứng pass/payout/challenge.

## Đính chính bộ đếm filter

Receipt gốc ghi `candidate_filtered_signals=0`. Sổ events thực tế có **2**
`candidate_breakout_body_filter` mỗi scenario. Hàm summary cũ chỉ đếm
`candidate_retest_body_filter` của H1 nên bỏ sót H2; summary hiện nhận cả hai status.
H2 loại hai breakout mà baseline sau đó cancel, nên không thay trades, P/L hoặc
quyết định reject.

[Receipt đính chính](quality-data/br01-engine/optimization-02-summary-correction-8623b5e08d3d.json.gz),
file SHA-256 `0fca46b0e1fba320cd6c6d85510ffc3bc17eea3f1da57e0c33bca7302f6d4939`,
pin hash receipt gốc, code summary mới, các số trước/sau và kiểm tra giữ nguyên mọi
metric còn lại cùng decision/gate. Receipt gốc không sửa. Synthetic regression tái
hiện lỗi 1 thay vì 3 trên mixed filter events, rồi pass sau sửa; bộ 49 test engine,
runner và optimization dùng fixture giả định cũng pass, với Python socket bị chặn.

Việc đính chính chỉ đọc receipt kết quả đã lưu; không đọc raw quote/H1/calendar hoặc
holdout, không chạy lại performance 2021–2025, không sửa luật/risk và learner state.
Không mở 2022 trong vòng H2 đã fail. Bước tiếp theo là chẩn đoán bằng chứng development
đã xem trước khi khóa một hypothesis/protocol mới.
