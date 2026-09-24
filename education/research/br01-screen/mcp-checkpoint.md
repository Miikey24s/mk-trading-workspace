# MT5 MCP — kiểm tra 2026-09-12

## Cập nhật sau khi đổi port/key — trạng thái mới nhất

- Terminal ở `http://127.0.0.1:22344/mcp` đã initialize/tools-list thành công (57 tools). Native Terminal tools chưa được expose trong phiên; dùng helper cục bộ `mcp_readonly.py` với allow-list đọc, không chứa secret. Helper đọc config project; phép thử âm gọi order bị từ chối trước network. Không coi helper là lớp bảo mật toàn máy hoặc giới hạn quyền của chính server.
- Đã gọi get_workspace_info, list_open_charts, get_marketwatch_symbols, get_time_information, get_chart_history, get_chart_ticks_history. Chưa gọi tool chạy tester; tester_get_configuration cần run_id thật nên không bịa ID để gọi.
- Python riêng tại `education/.venv-mt5`, MetaTrader5 5.0.6180 + numpy 2.5.3, binary wheels từ PyPI, package MetaTrader5 tác giả MetaQuotes/MIT; pip check pass. Không cài global. `mt5_readonly.py` kiểm tra FTMO-Demo và demo mode trước đọc dữ liệu, không login hoặc order_send. Terminal algo trading đang false theo Python; không đổi trạng thái này.
- Xuất 12.455 H1 bars: 6.216 năm2023 + 6.239 năm2024; đầu2023-01-02, cuối2024-12-31. File `mt5-data/eurusd-h1-2023-2024.json`, SHA256 `2ff21c7a1fd10412a73ce9ee19cecd7196836662453ed1a4150e051c7f786309`. OHLC/thứ tự/giới hạn năm hợp lệ; 105 khoảng gián đoạn chưa đối chiếu lịch giao dịch. Không gọi dữ liệu đã kiểm chứng đầy đủ.
- Lần MCP lấy dài đầu chỉ trả6.407bars từ2023-12-20 dù request bắt đầu2023-01-01; query riêng đầu2023 có120bars, Python sau đó lấy đủ phạm vi hai năm. Có nguy cơ lịch sử tải chưa xong khi trả kết quả; luôn kiểm tra coverage/count, không tin isError=false. Giữ file partial gốc để audit.
- 120bars tuần2024-10-07: MCP/Python khớp OHLC theo point0.00001, spread và tick_volume khớp. So sánh float tuyệt đối có14sai khác~1e-16, không phải sai giá theo tick. Cả hai cùng feed FTMO, không phải xác minh nguồn độc lập.
- Tick query2024-10-07 10:00–10:01 lần đầu trống; recheck trả253ticks Bid/Ask, thứ tự không giảm và Ask>=Bid. Recent probe2026-09-11 trả125ticks. Chưa có tick đầy đủ2023–2024; 2025 holdout chưa đọc.
- MCP EURUSD tick_size/value trả0; Python trả0.00001 và1USD/tick/lot. Không lấy trường0 từ MCP để tính lot. Time tool vẫn trả offset_minutes0 trong khi local_time lệch UTC7h; timezone lịch sử/server/DST cần đối chiếu trước áp bộ lọc phiên.
- list_open_charts thấy MacGateway trên hai chart EURUSD đã có sẵn; không cài, sửa, gỡ hay sử dụng gateway này. Chưa thêm chú thích chart, chưa chạy code trên chart. Các tool chart có mở/đóng/template/script, không thấy tool vẽ object riêng trong57tools.
- Python compile, read-only negative test, data smoke checks và education/check_setup.py pass. Audit môi trường0errors0warnings; active13539/65536B, reserve51997B.

### Cách tiếp tục

1. Dùng `education/.venv-mt5/Scripts/python.exe education/research/br01-screen/mt5_readonly.py` để smoke-test; thêm `--export-development` cho2023–2024. Terminal phải đang chạy, không cần mật khẩu/key mới. Bản export khác hash được giữ riêng.
2. `python education/research/br01-screen/mcp_readonly.py schemas` đọc schema; helper chỉ cho phép các tác vụ đọc đã duyệt. Không cài thêm MCP, không làm cầu nối giao dịch.
3. Phân loại gaps/calendar/timezone, chi phí và news; hoàn thiện engine/kiểm thử rồi mới chạy baseline. Đã có dữ liệu không đồng nghĩa BR-01 có edge.
4. Backtest tester và native chart annotation chưa smoke-test end-to-end. Không coi toàn bộ setup đã hoàn tất; không mở holdout để thử công cụ.

Nguồn SDK: https://www.mql5.com/en/docs/python_metatrader5 ; https://www.mql5.com/en/docs/python_metatrader5/mt5copyratesrange_py .

## Lịch sử trước khi khắc phục kết nối

## Kết quả thực tế

- Project đã cấu hình hai server `metaeditor` (22345) và `terminal` (22346). Không tạo cấu hình Claude trùng, không cài thêm plugin/package, không đổi key.
- MetaEditor đã có công cụ native trong phiên Codex. `get_workspace_info` và `get_time_information` gọi thành công. HTTP initialize/tools-list cũng thành công: 23 tools, chủ yếu đọc/ghi source, compile, tìm kiếm, thời gian và web request.
- Workspace báo compiler MQL5 build 6191 và `can_run_backtest=true`, nhưng danh sách tools thực tế chưa có tool chạy tester hoặc xuất rates/ticks. Không coi metadata là smoke-test backtest.
- Terminal initialize với Authorization từ project config vẫn trả HTTP 401. Không thử key khác, không vượt xác thực. Cần đối chiếu key đang áp dụng trong đúng terminal với config local; không gửi key vào chat.
- Time tool trả UTC 12:23 và local 19:23 cùng ngày nhưng offset_minutes=0; không dùng trường offset này làm timezone backtest khi chưa đối chiếu. Kết quả không có thời gian trade server.
- Chưa lấy lịch sử, chưa chạy strategy, chưa tạo/sửa/đóng lệnh.

## Khuyến nghị

Chưa cài MCP thứ ba. Hoàn thành xác thực Terminal, đọc tools/list, rồi smoke-test đọc EURUSD metadata/rates trước. Chỉ bổ sung thư viện Python MetaTrader5 chính thức hoặc exporter MQL5 nếu tools thực tế thiếu khả năng cần thiết. Chart annotation, đầy đủ lịch sử Bid/Ask/tick và Strategy Tester vẫn là các capability chưa được xác minh end-to-end.

## Nguồn

- https://developers.openai.com/codex/mcp/ — project config, HTTP headers, tool allow/deny lists.
- https://www.metatrader5.com/en/releasenotes/terminal/2464 — công bố mở rộng AI Assistant/tester; không đồng nghĩa mọi capability đã expose qua MCP trên máy này.

Audit môi trường: 0 errors, 0 warnings; active 13539/65536 B, reserve 51997 B. Không lưu secret trong ghi chú này.
