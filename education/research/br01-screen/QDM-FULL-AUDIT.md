# QDM EURUSD 2018–2024 — kiểm tra toàn CSV

**Checkpoint mới nhất:** người dùng đã duyệt cơ sở mô phỏng archive/chi phí. Hai episode nghiên cứu đã chạy và kiểm chứng; xem [RESEARCH-RESULTS.md](RESEARCH-RESULTS.md). Giá không sửa; “chưa chạy/chờ duyệt” bên dưới là lịch sử audit trước đó.

Ngày 13/09/2026. **Đã kiểm tra toàn file; chưa chạy baseline BR-01.** Không sửa bộ luật, raw, QDM/MT5, không mở quote holdout 2025. Không suy dữ liệu chưa đạt nghĩa là chiến lược kém.

**Cập nhật sau yêu cầu mới:** người dùng đã chấp nhận các sai lệch nhỏ của dữ liệu giá và yêu cầu sửa phần còn lại. Dừng nhánh sửa giá, giữ nguyên các phát hiện audit dưới đây. Engine tick/lot/margin/equity/lịch và adapter QDM đã triển khai, 95 tests đạt; dữ liệu lịch trước phiên và cơ sở phí vẫn chưa xác minh/chốt. Xem trạng thái hiện hành trong [status.md](status.md). Các đề xuất tiếp tục truy tìm gap và mô tả engine chưa có ở checkpoint cũ không còn là hành động hiện tại.

## Kiểm tra ngoại lệ tiếp theo — 13/09/2026

Đã hoàn tất các kiểm tra có mục tiêu, không lặp quét toàn file:

- `probe_qdm_exceptions.py` tìm đúng cửa sổ bằng byte seek trên CSV đã kiểm tra thứ tự; kiểm thử so với linear scan ở đầu/cuối/đúng timestamp/giữa timestamp đạt. Đọc 5 cửa sổ bất thường, kiểm giá và dựng OHLC độc lập bằng pandas. **0 khác biệt với bộ dựng H1 numpy**: loại trừ lỗi aggregate/chunk ở các cửa sổ đó, không chứng minh QDM archive hoặc cache nào đúng tuyệt đối.
- Ngày **26/05/2019 21:00–24:00 UTC chỉ có 1 tick**, lúc 23:59:59.984. Hai giờ đầu trống và giờ thứ ba gần như trống; không coi là sai số làm tròn. Mẫu này được chọn từ audit trước khi xem kết quả chiến lược.
- 20/08/2018 12h có 3.470 tick, tái hiện khoảng trống 364,013 giây. 02/09/2019 11h: 2.229 tick, cuối 11:59:57.961. 02/12/2019 11h: 3.164 tick, cuối 11:56:11.107. 04/02/2020 22h: 2.106 tick, cuối 22:59:44.268. Không bù giá hay sửa cache.
- Một yêu cầu đọc chính xác `https://datafeed.dukascopy.com/datafeed/EURUSD/2019/04/26/21h_ticks.bi5` vẫn trả **HTTP429, không Retry-After**. Dừng sau một request; không đổi IP/proxy hoặc lặp endpoint.
- Log local QDM đang có không ghi được provenance CDN/fallback theo từng giờ cần kiểm tra. Không gọi UI Completed là bằng chứng CDN đã phục vụ đủ mọi file.
- Đọc [CLI hiện hành](https://strategyquant.com/doc/cli-command-line/introduction-to-cli/) sau khi [trang CLI cũ](https://strategyquant.com/doc/quantdatamanager/quant-data-manager-command-line-interface-help/) dẫn sang: qdmcli khởi động engine riêng. **Chưa chạy engine thứ hai trên database đang mở**, chưa sửa profile/cache hay đóng QDM. Tài liệu CLI không tự giải quyết archive khác nhau.
- [Lịch FTMO](https://ftmo.com/en/calendar/) hiện ghi nguồn **ForexFactory** và hiển thị được sự kiện tuần hiện tại. Truy cập mẫu 08–14/01/2018 qua dateFrom/dateTo: trang nhận đúng ngày nhưng hiển thị no events; Reset filters vẫn không có sự kiện. Không khẳng định lịch cũ không tồn tại ở mọi nơi, không coi trống là không có tin. ForexFactory là đầu mối hợp lý nhưng snapshot lịch cuối cùng không chứng minh trạng thái lịch được biết trước phiên ở 2018–2020.
- Đọc metadata demo MT5 đang chạy, không orders: connected demo USD, leverage30, EURUSD contract100000 EUR/lot, min/step0,01lot, max50lot, stop/freezelevel0, profitUSD. Thông số **hiện tại**, không suy là lịch sử FTMO 2018–2020; Python symbol metadata không xác minh commission cả vòng. Không xuất login hoặc credentials.

Bằng chứng mới: `quality-data/qdm/exception-probes-962f8dece360.json.gz`, SHA256 file `531af4f259cbbe35270b96fb5d787c4f7be9887cfa87755e0b0a0574c6c0e40f`. 8 tests QDM đạt (thêm seek regression). Cộng 44 tests cũ đã đạt ở lượt trước =52 ca distinct trong corpus; lượt này chỉ chạy lại 8 QDM tests.

**Điểm cần quyết định, không tiếp tục hứa full v0 mà không đổi điều kiện:** tái dựng chính xác lịch FTMO biết trước phiên và toàn bộ điều kiện khớp lịch sử chưa khả thi với bằng chứng/đường truy cập hiện có. Đây là giới hạn của phép thử được viết quá chặt cho một baseline đầu tiên, không phải bằng chứng chiến lược không có edge.

Khuyến nghị chờ người dùng duyệt: tách một **nhánh screening nghiên cứu** (giữ logic mẫu hình, không tối ưu; không gọi full v0) với chi phí giả định công khai/stress, lịch tin là kịch bản riêng và báo riêng vùng dữ liệu không đánh giá được. Kết quả chỉ sàng lọc mức đáng nghiên cứu, không bằng chứng pass/payout hoặc bản demo được phép trade. Giữ nguyên v0 gốc. Người dùng từng từ chối baseline bỏ tin nên **chưa triển khai hoặc chạy nhánh này khi chưa đồng ý rõ**. Không mua nguồn tin/Pro, không liên hệ support. Không có job nền.

## Kết quả

- File xuất: `D:/ANNAM/Tools/QuantDataManager/export/2018_2024_utc_EURUSD_sample-TICK-No Session.csv`, 8.679.322.550 bytes, SHA256 `af7e4be87b5dc60a355e98cadff560e26fba4241dfe52890aa61d6fe7c0a5d56`.
- **189.979.417 tick**, từ 01/01/2018 22:00:08.661 đến 31/12/2024 21:59:58.249 UTC. Dựng **43.656 nến H1**, không điền giá/nến thiếu. Nguồn không thay size/mtime trong lượt quét.
- Toàn bộ file qua kiểm tra schema, timestamp trong phạm vi, trường số hữu hạn, Bid > 0, Ask >= Bid, volume >=0, bước giá 0,00001 và thời gian không đi lùi.
- Không timestamp trùng. Có **1.589 tick spread bằng 0**: được ghi nhận, không xóa hoặc tự coi là lỗi; chưa xác minh nguyên nhân.
- Có 587 khoảng giữa tick >5 phút; 222 khoảng có điểm giữa nằm trong lịch tuần giả định đang mở. Ngưỡng 5 phút chỉ dùng tìm đầu mối, không chứng minh tất cả là mất dữ liệu.

| Năm | Tick |
|---|---:|
| 2018 | 26.048.775 |
| 2019 | 29.186.310 |
| 2020 | 32.763.638 |
| 2021 | 16.797.607 |
| 2022 | 36.946.763 |
| 2023 | 27.549.175 |
| 2024 | 20.687.149 |

## Độ phủ và đối chiếu cùng nguồn

Lịch tuần tham chiếu: Chủ nhật 17:00 đến thứ Sáu 17:00 America/New_York, có US DST. Không có H1 ngoài lịch tuần này. Trong cửa sổ UTC danh nghĩa 2018–2024 có 192 giờ thường mở nhưng không có tick:

- 180 giờ rơi đúng 01/01 hoặc 25/12; thêm 8 giờ vào tối 24/12 hoặc 31/12. Đây là **ứng viên đóng cửa dịp lễ**, chưa có lịch nhà cung cấp theo từng năm để tự duyệt.
- 2 giờ cuối 31/12/2024 (22–23 UTC) nằm ngoài biên export dự kiến do chọn ngày theo EETUS trước đổi UTC. Không dùng làm bằng chứng nguồn bị mất dữ liệu.
- **26/05/2019 21:00 và 22:00 UTC** là 2 giờ cần xem lại rõ nhất. Cache H1 Dukascopy có cả Bid và Ask ở hai giờ này; QDM tick-derived H1 không có.

Đối chiếu 51 bucket tháng/side có sẵn trong cache 2018–đầu 2020 (không tải lại mạng):

- 26.438 bản ghi H1-side tham chiếu, tất cả geometry hợp lệ.
- 26.434 bản ghi cùng timestamp có trong QDM, **26.427 khớp toàn bộ OHLC**.
- 4 bản ghi tham chiếu không có QDM = 2 giờ x 2 side ngày 26/05/2019.
- 7 bản ghi lệch OHLC tại 4 giờ UTC: 26/05/2019 23:00; 02/09/2019 11:00; 02/12/2019 11:00; 04/02/2020 22:00. Lệch lớn nhất trong các trường so sánh: 48 point (4,8 pip). Chưa xác định khác biệt do archive, download, export hay cache; không ghép feed hoặc sửa giá theo H1.
- Cùng nhà cung cấp, hai đường cung cấp khác nhau: kiểm tra này hỗ trợ clock/giá, **không phải nguồn giá độc lập** và không phủ toàn kỳ.

Trong 2018–2020, phép sàng lọc khoảng >5 phút giao cửa sổ 07–16 UTC, Mon–Thu, tìm được một khoảng ngoài 25/12: **20/08/2018 12:03:50.728 → 12:09:54.741 UTC (364,013 giây)**. Chưa kết luận chắc là mất tick; không tự loại ca này khỏi hiệu suất.

## Quyết định về baseline và công sức

**Không chạy `screen.py` rồi gắn nhãn BR-01 v0.** Script hiện có là partial H1 screen: bỏ lịch tin, giả commission 7 USD/lot cả vòng, chưa lot/margin/equity stop, dùng SL-first/TP-first thay thứ tự tick. Người dùng đã yêu cầu không hạ mục tiêu thành baseline bỏ tin. Giữ nguyên v0 và full-execution gate false.

Các bước bắt buộc còn lại trước baseline nguyên bản:

1. Kiểm tra có mục tiêu những đoạn QDM khác cache/gap; không tải lại cả 8,68 GB hoặc mặc định mua Pro/đổi nguồn.
2. Xác minh lịch tin lịch sử và chi phí/thông số thực thi. Snapshot ForexFactory cộng đồng hiện chưa được duyệt thay lịch FTMO point-in-time; không coi thiếu lịch là không có tin.
3. Kiểm chứng bộ máy khớp tick và giới hạn tài khoản theo v0 trước chạy 2018–2020. Chưa tối ưu tham số hoặc xem P/L 2021–2024.

Phần đã làm tái sử dụng được: CSV bất biến → kiểm tra streaming 1 triệu dòng/lượt → H1 cùng nguồn + manifest/hash → báo cáo gap và đối chiếu. Không gửi raw vào AI, không sửa hoặc xóa tick. Nếu BR-01 bị bỏ, dữ liệu và phép kiểm tra vẫn dùng cho ứng viên sau.

## Bằng chứng và kiểm thử

- `quality-data/qdm/full-csv-audit-8ad43ce95658.json.gz` — toàn kỳ, SHA256 file `936b74063d0e7244ea4c911380f8bee8caf18fe4f705edd9c462642bd124b3dc`.
- `quality-data/qdm/h1-3e801686a6f9.npz` — Bid/Ask H1 và tick counts, SHA256 file `a05625bb8a29e334590b11c7d9b24dfa4df0a635e16cbe7b789f121effb8ab48`.
- `quality-data/qdm/h1-crosscheck-b16aac54c581.json.gz` — từng tháng và toàn bộ khác biệt, SHA256 file `58d8249b707e67032534543a0dde23b45742c3fb19ce9d5e3a65e5d54b537cfb`.
- Code: `audit_qdm_csv.py` dùng lại `tick_audit.aggregate(normalize_utc=False)`; `crosscheck_qdm_h1.py` dùng lại `decode_duka`.
- 7 kiểm thử QDM mới đạt (precision, reject holdout, crossed quote/missing/grid, chunk boundary, weekly DST). 44 kiểm thử cũ đạt trong venv MT5. Lần discover toàn bộ bằng bundled runtime lỗi import MetaTrader5; không phải lỗi dữ liệu, đã chạy lại suite cũ đúng runtime. Tổng **51 ca distinct đạt**, không cài thêm dependency.
- Đã sửa lỗi đường dẫn tương đối của script crosscheck và chạy lại CLI thành công; output là report mới, không thay input.

Toàn bộ tiến trình quét đã kết thúc, không có download hoặc job nền đang chạy.
