# Glossary Anh-Việt / English-Vietnamese Trading Statistics Glossary

File này chuẩn hoá cách hiểu các thuật ngữ dùng trong `README.md`, `diagrams.md` và `evidence.csv`. Mục tiêu là đọc tiếng Việt dễ hiểu nhưng vẫn nhớ đúng tên English để tra cứu tài liệu gốc.

| English | Tiếng Việt dùng trong hub | Hiểu ngắn gọn |
| --- | --- | --- |
| Win rate | Tỷ lệ thắng | Phần trăm lệnh có lời; không tự nói strategy có lời hay không |
| Loss rate | Tỷ lệ thua | Phần trăm lệnh/tài khoản thua theo đúng đơn vị đang đo |
| Expectancy / EV | Kỳ vọng / giá trị kỳ vọng | Trung bình lời/lỗ kỳ vọng trên mỗi lệnh sau một sample đủ lớn |
| Average win | Lợi nhuận trung bình của lệnh thắng | Mức lời trung bình khi thắng |
| Average loss | Mức lỗ trung bình của lệnh thua | Mức lỗ trung bình khi thua |
| Reward-to-risk / RR | Tỷ lệ lợi nhuận trên rủi ro | Ví dụ 2:1 nghĩa là mục tiêu lời 2R khi rủi ro 1R |
| Breakeven win rate | Tỷ lệ thắng hòa vốn | Win rate tối thiểu để EV bằng 0 theo payoff và cost đã giả định |
| Cost | Chi phí giao dịch | Spread + commission + slippage + các chi phí liên quan |
| Spread | Chênh lệch giá mua-bán | Khoảng cách bid-ask phải vượt qua trước khi lệnh có lợi nhuận thực |
| Commission | Phí hoa hồng | Phí broker/exchange thu theo lệnh hoặc volume |
| Slippage | Trượt giá | Giá khớp thực tế khác giá dự kiến |
| Variance | Phương sai / biến động kết quả | Cùng một edge nhưng thứ tự win/loss khác nhau tạo equity path rất khác |
| Equity curve | Đường vốn | Đồ thị giá trị tài khoản theo thời gian/lệnh |
| Drawdown / DD | Mức sụt giảm | Mức giảm từ đỉnh vốn xuống đáy sau đó |
| Maximum drawdown / Max DD | Sụt giảm tối đa | Drawdown lớn nhất trong giai đoạn đo |
| Risk of ruin | Rủi ro phá sản | Xác suất chạm mức mất vốn/vi phạm ngưỡng khiến không thể tiếp tục |
| Position size | Kích thước vị thế | Khối lượng giao dịch được chọn để biến stop distance thành số tiền rủi ro mong muốn |
| Risk per trade | Rủi ro mỗi lệnh | Phần trăm hoặc số tiền chấp nhận mất nếu lệnh chạm stop |
| Losing streak | Chuỗi thua | Nhiều lệnh thua liên tiếp |
| Base rate | Tỷ lệ nền | Tần suất quan sát được trong population tham chiếu trước khi biết chi tiết riêng của mình |
| Prior | Niềm tin/xác suất ban đầu | Điểm xuất phát trước khi cập nhật bằng dữ liệu cụ thể hơn |
| Sample | Mẫu dữ liệu | Tập quan sát dùng để ước lượng thống kê |
| Sample size | Cỡ mẫu | Số quan sát/lệnh/trader trong sample |
| Confidence interval / CI | Khoảng tin cậy | Khoảng thể hiện độ bất định quanh một estimate |
| Out-of-sample / OOS | Ngoài mẫu | Dữ liệu không dùng để fit/chọn model ban đầu |
| Holdout | Tập dữ liệu giữ lại | Phần data cố tình không đụng tới cho đến bước kiểm chứng |
| Forward test | Kiểm thử tiến về phía trước | Chạy strategy trên dữ liệu mới sau khi rule đã khóa |
| Overfitting | Quá khớp | Strategy fit rất đẹp quá khứ nhưng học cả noise nên dễ hỏng trên dữ liệu mới |
| Robustness | Độ bền | Mức kết quả còn giữ được khi đổi sample, regime, cost hoặc parameter hợp lý |
| Edge | Lợi thế thống kê | Kỳ vọng dương có căn cứ sau cost và validation phù hợp |
| Pass probability | Xác suất vượt challenge | Xác suất chạm profit target trước failure boundary theo một model cụ thể |
| Failure boundary | Ngưỡng thất bại | Mốc mà chạm vào thì account/challenge fail |
| Profit target | Mục tiêu lợi nhuận | Mốc lợi nhuận cần đạt để pass theo rule đã định |
| Static drawdown | Drawdown tĩnh | Ngưỡng fail giữ cố định theo rule |
| Trailing drawdown | Drawdown bám theo | Ngưỡng fail dịch lên theo equity/balance watermark theo rule của firm |
| Consistency rule | Luật nhất quán | Rule hạn chế mức lợi nhuận tập trung vào một ngày/lệnh hoặc một dạng phân phối nào đó |
| Rule adherence | Mức tuân thủ luật | Tỷ lệ trader thực hiện đúng rule đã định |
| Realized expectancy | Kỳ vọng thực tế | EV thật sau cost và sai lệch execution |
| Model uncertainty | Độ bất định của mô hình | Phần không chắc chắn do assumptions/model chứ không chỉ do sample nhỏ |
| Transferability | Khả năng chuyển giao | Mức một kết quả nghiên cứu có thể áp sang market/trader/strategy khác |
| Correlation | Tương quan | Hai biến cùng thay đổi nhưng chưa chứng minh biến này gây ra biến kia |
| Causality | Quan hệ nhân quả | Thay đổi một yếu tố thực sự làm yếu tố kia thay đổi |

## Cách đọc shorthand

- `WR` = tỷ lệ thắng (Win rate).
- `RR` = tỷ lệ lợi nhuận/rủi ro (Reward-to-risk).
- `EV` = kỳ vọng (Expected value / Expectancy).
- `DD` = mức sụt giảm (Drawdown).
- `OOS` = ngoài mẫu (Out-of-sample).
- `IID` = độc lập và cùng phân phối (Independent and identically distributed); chỉ là assumption toán học khi được nêu rõ, không mặc định đúng cho market.
- `R` = một đơn vị rủi ro. Nếu mỗi lệnh risk 100 USD thì `+2R = +200 USD`, `-1R = -100 USD`.
