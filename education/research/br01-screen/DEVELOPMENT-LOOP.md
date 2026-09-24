# BR-01 — vòng lặp phát triển chiến lược

Khóa ngày 16/09/2026. Tài liệu này mô tả cách phát triển BR-01 từ candidate thành một hệ thống có bằng chứng tốt hơn. Nó **không thay đổi BR-01 v0**, không mở holdout 2025 và không tự cho phép giao dịch demo/live.

## Trạng thái xuất phát

- Core hiện tại: Price Action breakout → first retest trên EUR/USD H1; không dùng ICT/SMC.
- BR-01 v0 đã có rule đủ chặt để engine và người đọc cùng áp dụng.
- Hai episode development đầu tiên đã chạy đúng protocol: conservative 21 lệnh, stress 18 lệnh; cả hai âm và dừng sớm vì account-risk gate. Mẫu này chưa đủ để kết luận edge.
- Một bài áp dụng rule của học viên còn sai ở điều kiện `Close > Open`; manual consistency vẫn cần luyện song song.

## Hai loop chạy song song

### Loop A — Strategy evidence

Mục tiêu: tìm xem **setup có edge sau chi phí hay không**, rồi mới cân nhắc thay rule.

1. **Freeze v0** — giữ nguyên H20, zone, first retest, 6 nến, entry, SL, TP và các định nghĩa hiện tại.
2. **Tăng bằng chứng development** — thu đủ mẫu theo protocol nghiên cứu đã chốt; không chọn chart đẹp, không reset account rồi ghép P/L để cứu kết quả.
3. **Chẩn đoán trước khi tối ưu** — tách ba nguyên nhân: chất lượng signal, cost/fill và account-risk gate. Không sửa signal chỉ vì account hết room.
4. **Đặt đúng một giả thuyết thay đổi** — ví dụ chỉ thay một nhóm: entry/retest, exit, time filter hoặc execution filter. Ghi lý do trước khi xem kết quả mới.
5. **Tạo version mới** — mọi thay đổi có ý nghĩa thành `v1`, `v2`...; không ghi đè v0 và không trộn kết quả giữa version.
6. **So trên development** — đo expectancy sau chi phí, số lệnh, drawdown, losing streak, stability theo năm/quý, sensitivity với cost và độ phức tạp/manual burden.
7. **Freeze candidate tốt hơn** — chỉ giữ thay đổi nếu cải thiện có lý do và không phụ thuộc một đoạn ngắn hoặc một tham số quá chính xác.
8. **Chronological validation 2021–2022** — luật đã khóa; nếu sửa dựa trên kết quả này thì giai đoạn đó trở thành development, không còn independent validation.
9. **Robustness 2023–2024** — kiểm tra giai đoạn gần hơn và đối chiếu FTMO; đây không phải holdout hoàn toàn vì đã dùng cho audit kỹ thuật.
10. **Pre-register final test** — khóa rule, cost model, engine và tiêu chí đọc kết quả trước khi mở 2025.
11. **Holdout 2025 một lần** — không nhìn rồi đổi tiêu chí để pass; fail thì coi là bằng chứng chống lại version đó.
12. **Forward demo** — dùng đúng rule đã kiểm định để đo execution thật, spread/slippage và adherence; không coi vài lệnh demo thắng là xác nhận edge.

Sau forward demo, chỉ khi có bằng chứng phù hợp và người dùng yêu cầu riêng mới bàn tới quy mô rủi ro thực tế hoặc challenge. Course không tự kích hoạt bước tiền thật.

### Loop B — Manual execution

Mục tiêu: trade tay với cùng một strategy nhưng checklist ngắn, không overload.

1. Replay/unseen case → quyết định `trade / skip / cancel` theo đúng v0.
2. So với rule engine → ghi lỗi phân loại, không ghi thành lỗi “tâm lý” nếu chưa có bằng chứng.
3. Luyện lại đúng lỗi vừa gặp; không thêm concept mới.
4. Khi rule application ổn định, dùng checklist live ngắn: `setup → retest → execution filter → size/SL/TP`.
5. Ghi riêng `strategy outcome` và `execution/adherence error` để không đổ lỗi cho strategy khi người vận hành phá rule, hoặc ngược lại.

Loop B không tối ưu P/L. Nó tối ưu **độ nhất quán thực thi**.

## Gate trước khi được sửa rule

Không tạo version mới chỉ vì 1–3 lệnh thua. Trước mỗi thay đổi cần có đủ bốn câu trả lời:

1. Vấn đề quan sát được là gì?
2. Nó thuộc signal, execution/cost hay risk/account policy?
3. Thay đổi nào nhỏ nhất có thể xử lý đúng vấn đề đó?
4. Data nào sẽ dùng để phát triển và data nào vẫn còn độc lập để kiểm tra?

Thiếu một câu trả lời thì tiếp tục thu bằng chứng, chưa tối ưu.

## Scorecard cho mỗi version

Không dùng win rate một mình. Mỗi version phải báo tối thiểu:

| Nhóm | Chỉ tiêu |
|---|---|
| Edge | net expectancy/R, profit factor, avg win/loss |
| Risk | max drawdown, losing streak, tail loss/gap cases |
| Robustness | theo năm/quý, cost stress, parameter sensitivity |
| Sample | số opportunity, số trade, phần không đánh giá được |
| Manual fit | số rule deviations, thời gian quyết định, số điều kiện phải nhớ |
| Complexity | số rule/filter mới và lý do tồn tại |

Version mới chỉ được xem là mạnh hơn khi **bằng chứng tốt hơn mà complexity/manual burden không tăng vô lý**.

## Loop tổng

`Freeze → thu data → đo → chẩn đoán → thay tối thiểu → version mới → test development → freeze → validation → robustness → holdout → forward demo → monitor`

Nếu forward/demo về sau cho thấy suy giảm có bằng chứng, quay lại **chẩn đoán** bằng dữ liệu mới; không tái sử dụng holdout cũ như dữ liệu mới và không sửa rule sau từng lệnh.

## Bước hiện tại

BR-01 đã chuyển từ **thu bằng chứng development → chẩn đoán** sang vòng tối ưu đầu tiên.
`H1_R_BODY_5P` đã được khóa trước dữ liệu mới trong
[OPTIMIZATION-01-PROTOCOL.md](OPTIMIZATION-01-PROTOCOL.md); core Price Action v0 vẫn khóa.
Unseen screen 25/11/2019–2020 đã chạy xong. `H1_R_BODY_5P` cải thiện tổng R so với shadow
v0 nhưng vẫn âm ở cả conservative và stress, nên fail gate đã khóa và bị reject. Xem
[OPTIMIZATION-01-STATUS.md](OPTIMIZATION-01-STATUS.md). Chưa tạo v1; bước kế tiếp quay về
**chẩn đoán** để đặt một hypothesis mới có lý do, không chỉnh threshold 5 pip sau kết quả.

Nguồn trạng thái: [RESEARCH-RESULTS.md](RESEARCH-RESULTS.md), [STUDY-PLAN.md](STUDY-PLAN.md), [BR-01 v0](../../practice/eurusd-breakout-retest-v0.md).
