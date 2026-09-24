# Hoàn thiện dữ liệu — lượt tiếp tục 13/09/2026

**Cập nhật hiện hành:** người dùng chấp nhận sai lệch nhỏ của giá QDM; nhánh khôi phục giá dừng tại đây, không sửa raw. Engine tick/lot/margin/equity/calendar đã triển khai, dữ liệu lịch và cơ sở chi phí chưa đủ để chạy baseline. Xem [status.md](status.md); nội dung thu thập/khôi phục phía dưới là lịch sử.

Yêu cầu là tìm đủ dữ liệu, **không hạ mục tiêu thành chỉ có H1 hoặc baseline bỏ tin**. Lượt này tiếp tục tải tick, tìm nguồn thay thế, dựng M1/H1 và xác định phần cần nhà cung cấp trả lời. Chưa chấp nhận full BR-01 execution dataset.

**Trạng thái nguồn hiện tại:** TrueFX trực tiếp không đáp ứng catalog cần thiết. Người dùng đã tải QDM/Dukascopy và xuất CSV 2018–2024; đã quét 189.979.417 tick. Xem [QDM-FULL-AUDIT.md](QDM-FULL-AUDIT.md) và [DATA-SOURCE-DECISION.md](DATA-SOURCE-DECISION.md). Độ phủ/khác biệt một số giờ còn cần đối chiếu, full BR-01 chưa được duyệt. Không mua tool, không gửi support, không thay raw. Các đề xuất liên hệ FTMO phía dưới là lịch sử, không còn là hành động tiếp theo được yêu cầu.

## Giá đã nhận

### Sửa lỗi truy vấn và thử khôi phục — 13/09/2026

- Đã tái hiện và sửa lỗi endpoint của Python MT5: `end - 1 ms` bị cắt xuống giây, làm mất tick trong phần lẻ của giây cuối. Ví dụ giờ 14:00 ngày 01/10/2021: cách cũ trả 1.571 tick, cách đúng trả 1.572 tick; tick 14:59:59.214 bị bỏ trước sửa. Cách mới yêu cầu tới boundary rồi lọc `[start, end)` bằng `time_msc`, giữ nguyên các tick cùng millisecond.
- `stable_tick_range` dùng chung cho collector và recovery: kiểm tra mã lỗi trước khi nhận snapshot; phân biệt `retrieval_unresolved`, `stable_empty` và `stable_nonempty`. Không còn coi API lỗi/timeout là một tháng không có tick. Đây là sửa độ tin cậy của truy vấn, không chứng minh archive đầy đủ.
- Đã kiểm tra boundary của **1.299/1.299 file ngày** hiện có: **0 tick cần bổ sung, 0 file sửa đổi, 0 truy vấn chưa giải quyết**. Không suy lỗi chia giờ đã làm hỏng các file ngày trước đó.
- Sau sửa, tải lại cả ngày và 24 khoảng giờ cho 01/10/2021, 27/06/2022, 07/07/2022, 07/05/2024: kết quả bằng nhau và bằng bản raw đã lưu. **0 giờ khôi phục; vẫn thiếu lần lượt 14 + 1 + 1 + 22 = 38 giờ có H1**. Các bản thử trước sửa vẫn giữ để audit, không dùng thay bản sau sửa.
- MCP Terminal báo `data_available_from = 2020.01.02 00:00:00` cho tick EURUSD; mẫu thiếu 2021/2024 trả rỗng qua cả Python và MCP, mẫu đối chứng 08/05/2024 trả tick. Đây là giới hạn được endpoint hiện tại báo, chưa khẳng định mọi archive FTMO đều không có dữ liệu trước 2020.
- Thử warm-up M1 qua Python trả một nến năm 2026 ngoài khoảng yêu cầu; chỉ timestamp diagnostic được ghi, không chấp nhận/xuất nến sai kỳ. Validator đã chặn case này trong recovery. MCP M1 cho mẫu 07/05/2024 cũng trả rỗng. Không dùng M1 đó để lấp tick, không yêu cầu dữ liệu 2025.
- Không xóa/reset cache, đóng terminal, sửa chart, thay tài khoản hoặc gửi support. Trạng thái trước/sau: demo, 0 vị thế, 0 lệnh chờ, Algo Trading tắt. Nguyên nhân sâu phía server/cache chưa được phân biệt hoàn toàn; bước phù hợp tiếp theo là xin FTMO kiểm tra archive trước khi can thiệp cache đang dùng.

Bằng chứng mới trong `quality-data/recovery/`:

- `boundary-reproduction-94e653d5a55c.json.gz`: tái hiện lỗi phần lẻ giây.
- `boundary-repair-efc330f8ff5c.json.gz`: audit 1.299 boundary, không thay raw.
- `ftmo-recovery-689c57f56424.json.gz`: bản sau sửa, 4 ngày/96 giờ, 38 giờ vẫn thiếu.
- `native-mcp-crosscheck-3d3d042bb61e.json.gz`: tick metadata và đối chứng MCP.
- `initial-resync-3837e0dd771a.json.gz`, `m1-mcp-crosscheck-037598e32f52.json.gz`: lỗi range M1 và kết quả warm-up.

Kiểm chứng: **44 unit tests đạt**, gồm 12 test retrieval/recovery (timeout, response sai kỳ, boundary, giữ tick trùng, chặn yêu cầu holdout, không làm mất tick cũ). `education/check_setup.py` đạt; 56 lượt trả lời học viên giữ nguyên. Các collector/recovery đã kết thúc, không còn tải nền.

Full-execution gate vẫn **false**. Không có backtest lợi nhuận hoặc edge mới; các tổng tick trong bảng dưới không thay đổi.

| Nguồn / giai đoạn | Đã nhận | Bằng chứng / giới hạn |
|---|---:|---|
| FTMO 2018–2019 | H1 đã có; tháng tick truy vấn trả rỗng | Đã thử toàn24tháng; không suy cóH1 thì cótick.518ngày cóH1 chưa cóFTMOtick |
| FTMO 2020 | 13.788.303tick,261ngày | Raw hash và quote geometry đã kiểm tra; chưa xác nhận UTC của bộ cũ |
| FTMO 2021 | 10.596.752tick,260ngày | 122H1 không khớp rawtick; ngày01/10 thiếu14giờ |
| FTMO 2022 | 28.291.653tick,259ngày | 1.202H1 không khớp rawtick;27/06 và07/07 mỗi ngày thiếu1giờ |
| FTMO 2023–2024 | 54.738.521tick,519ngày từ lượt trước | Giữ gate cũ:false;07/05/2024 thiếu22giờ và1H1 lệch |
| HistData 2018–2019 | 47.546.043tick trong24/24gói | Đã audit tất cả:23tháng quaquote/order checks,2019-10 có1lần timestampđi lùi. UTCchưa duyệt do mâu thuẫndocs/thực nghiệm; không gán thànhFTMO |

Tổng FTMO2020–2024 đang có **107.415.229tick**. Bộ mới2020–2022 raw nén408.043.730bytes, derived33.647.978bytes; dựng1.110.123M1 và18.680H1, giữ clockserver gốc, không tự gắnUTC.32unit tests đạt; test không xác nhận nguồn đủ/đúng.

## Lỗi FTMO tái hiện lại

Truy vấn từng giờ vẫn trả0tick đúng những giờ đã phát hiện:

-2021-10-01 server00:00–13:59:59.
-2022-06-27 server23:00–23:59:59.
-2022-07-07 server23:00–23:59:59.
-2024-05-07 probe10:00–10:59:59 tiếp tục trả0; thiếu22giờ đã ghi trongaudittrước.

Không sửa nến hoặc nối giá nguồn khác vàoFTMO. LệchOHLC/tick có thể đến từ archive/feed khác nhau hoặc sửa lịch sử; chưa có bằng chứng xác định nguyên nhân. Bản nháp [hỏi FTMO](FTMO-DATA-SUPPORT-DRAFT.md) nêu mẫu cụ thể, chưa gửi.

## Nguồn thay thế và tin/phí

- [HistData](https://www.histdata.com/download-free-forex-historical-data/?/ascii/tick-data-quotes/eurusd/2018): đã tải24gói2018–2019 qua form download công khai, không muaFTP/góiGoogleDrive. [Spec chính thức](https://www.histdata.com/f-a-q/data-files-detailed-specification/) xác nhận tickCSV có timestamp millisecond,Bid,Ask,Volume,clockESTcố định khôngDST. DựngUTC bằng+5giờ; chưa gọi khác biệt vớiFTMO là lỗi HistData. RawZIP giữ nguyên.
- Dukascopy: probe đúng endpointASK2020-02 vẫnHTTP429, khôngRetry-After. Không retry thêm hoặc đổiIP để vượt hạn mức;51/120bucket H1 đã có vẫn giữ.
- [Lịch FTMO](https://ftmo.com/en/calendar/?dateFrom=2018-01-01&dateTo=2018-01-07): giao diện đúng tuần nhưng không trảevent, trong khi tuần hiện hành cóevent. Chỉ chứng minh querytuần đó rỗng, không chứng minh năm2018không cótin. Trang ghi nguồnForexFactory.
- [Forex Factory archive](https://www.forexfactory.com/calendar?week=jan1.2018): browser xác nhận cóevent2018; dữ liệuHTTP riêng timeout. Archivehiện hành có thể đổi tên/reviseevent; không giả point-in-time snapshot.
- [Kho lịch cộng đồng](https://github.com/EPSOFT/dataset-forexfactory/tree/a36d5270a1fb74b627420df413ca2c6c0069c839): đã lưu60tháng2018–2022 ở`news-candidate`, chưa dùng làmfilter. README nói chỉ tới03/2023; múi giờ và độ phủ chưa duyệt. Không tải hoặc chạy code scraper, không upload dữ liệu tài khoản. LicenseGPL-3.0 củarepo không chứng minh quyền phân phối dữ liệuForexFactory.
- [FTMO symbols](https://ftmo.com/en/symbols/): trang hiện hànhEURUSD ghicontract100.000,leverageSwing1:30,commission5USD/lot. Chưa xác nhận per-side/roundtrip và lịch thay đổi phí2018–2024. Không biến5hiện tại hoặc7USD/lotgiả định cũ thành phí lịch sử đã kiểm chứng. Không đặt lệnh để đo phí.

## Những gì vẫn cần để gọi đủ

**Cảnh báo bổ sung từ đối chiếu thực nghiệm HistData:** áp+5h theo docs cho sai lệchClose trung vị tới vài pip vào nhiều thángmùa hè. Thửdịch−1h cho các ngày đó khớp hơn rõrệt: lần kiểm tra453ngày có301ngày cần−1h,152ngày giữ0h; các mốc thayđổi quan sát2018-03-12,2018-11-05,2019-04-01. Không suy đây là lịchDSTđồng nhất hoặc tự sửa. Toàn bộ derivedHistData hiện **chưa duyệt UTC**, dù fieldcũ tên`utc_time`; chỉ được dùng cùng cảnhbáo này, không cho engine tiêu thụ. RawZIP không đổi. Bằngchứng `quality-data/histdata/clock-review-3a6dfedec20b.json.gz` và `crossfeed-7a7a29eb6b25.json.gz`.

1. Chọn/kiểm chứng feed cho2018–2019, hoàn thiện auditHistData và so giá/clock; không che việcFTMOkhông cung cấptick.
2. Xác nhận/khôi phục khoảng thiếu và mâu thuẫnH1/tickFTMO; nếu không thể, phải thống nhất mô hình ngoại lệ **trước** khi gọi kết quảbacktest.
3. Hoàn thiện news2018–2024 có timezone/impact/timestamp và ghi rõ point-in-time hay revised archive.
4. Phí lịch sử/cách tính hiện hành và mô hìnhslippage. Dữ liệu quote dù đầy đủ cũng không thể cho biết chính xác giá lệnh giả định sẽ khớp; cần mô hình công khai, không kiếm một file rồi gọi làkhớp thực tế chắc chắn.

Không mởholdout2025, không tối ưu hoặc chạyP/L; không sửa repoUI/MCP/quyềnMT5. Không mua dữ liệu hoặc tự gửi support. Giữ nguyên bộ luậtv0 và dữ liệu học viên.

## Bằng chứng

- `quality-data/history-extension/tick-collection-742ee066b7b0.json.gz`:780ngày tick mới;518ngàyH1thuộc2018–2019 không cóticktrongquerytháng.
- `quality-data/history-extension/tick-audit-d3423fcf56c4.json.gz`:audit đầy đủ bộ mới,hashfile `775cd4795aa3333505e5435d80d8e004b8b3218785d2717272f3db951a4ada81`.
- `quality-data/history-extension/exact-gap-reprobes-1de4213417dd.json.gz`:16giờ thiếu bộmới đều tái hiện0rows.
- `quality-data/histdata/acquisition-58c75190caed.json.gz`:24gói ZIP,hashfile `4d5f8e89e9f9412faf55ee347408483ae4ea8d3593debebe7e865a0a2a8f643d`.
- `quality-data/news-candidate/manifest-183182236f17.json.gz`:60tháng lịch cộng đồng,`approved_for_filtering=false`.
- `quality-data/histdata/audit-summary-51bf2775d7ae.json.gz`:24tháng47.546.043ticks;23tháng qua kiểm tra basic, khôngđồngnghĩaUTCđạt. `quality-data/histdata/APPROVAL.json` chặn dùngchoexecution.

Collector vàaudit của lượt này đều đã kếtthúc, không còn tải nền. Tài khoản saukiểmtra:FTMOdemo,positions0,pendingorders0,AlgoTradingfalse. Có thể tiếp tục nghiên cứu/audit local, nhưng việc lấy phiênbảnarchiveFTMOchuẩn/cost/news từnhàcungcấp cần phối hợp bên ngoài. Bảnnhápchưagửi,khôngmặcđịnhquyềngửitừyêucầutìmdữliệu.

Luồngdata:MT5/nguồnpublic → rawimmutable cóhash → audit → derivedriêng → cổng chấp nhậndữliệu. Bộ lọc chất lượng không cho phép biến unknown thành0. Chưa có kết quảđầu tư hoặc bằng chứngedge.
