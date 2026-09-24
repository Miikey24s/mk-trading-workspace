# Bộ công cụ FTMO / MT5 cho TradingWorkspace

Kiểm chứng ngày 12/09/2026. Dùng **FTMO MT5 desktop + MetaEditor + hai MCP hiện có + Python local** làm bộ công cụ chính. Không cần TradingView Premium, MCP thứ ba hoặc dịch vụ trả phí cho phạm vi hiện tại. TradingView/FX Replay là tùy chọn cho các bài cũ, không là nguồn dữ liệu thực thi FTMO mặc định.

## Dùng với gia sư

Bạn mở FTMO MT5 desktop và MetaEditor (F4 từ MT5). Sau đó chỉ cần yêu cầu:

- “Kiểm tra môi trường rồi cùng mình xem EURUSD H1.”
- “Vẽ zone và chỉ rõ nến đang nói đến trên chart RoadMap.”
- “Tính lot theo entry, SL và ngân sách lỗ này, gồm phí.”
- “Chạy backtest theo bộ luật và phạm vi dữ liệu đã duyệt, đọc báo cáo.”

Gia sư kiểm tra tài khoản demo, lệnh tồn, chart và dữ liệu trước mỗi thao tác. Không phải gửi ảnh mỗi bước khi kết nối đang hoạt động. Bạn vẫn tự quyết định giao dịch; yêu cầu setup không cấp quyền đặt lệnh. Không có bot hay giám sát chạy nền sau lượt chat.

## Khả năng đã kiểm chứng

| Nhu cầu | Kết quả thực tế | Giới hạn |
|---|---|---|
| Đọc terminal, chart và dữ liệu | Terminal MCP trực tiếp qua loopback; Python SDK đọc FTMO demo và thông số EURUSD | Native Terminal MCP chưa xuất hiện trong registry của phiên Codex này; đường HTTP trực tiếp đang dùng được |
| Vẽ trực tiếp | `RoadMapAnnotate.ex5` tạo rectangle, mũi tên, nến A và nhãn Zone High/Low theo đúng giá/thời gian; ảnh và template đã lưu | Cần xem ảnh sau mỗi lần vẽ; không suy `ok=true` là hình đúng. Script không xác định tín hiệu |
| Viết và biên dịch MQL5 | Native MetaEditor MCP biên dịch hai nguồn RoadMap: 0 errors / 0 warnings | Chỉ compile thành công không chứng minh luật chiến lược đúng |
| Strategy Tester và báo cáo | Run `7684646101493876814`: EURUSD H1, real ticks, 07–08/10/2024; 24 bars, 123.264 ticks; đã dừng; 0 trades | Probe không có logic giao dịch, chỉ kiểm tra đường chạy. Không phải backtest BR-01 |
| Tính lot, rủi ro và ký quỹ | SDK `order_calc_profit` / `order_calc_margin`, làm tròn xuống bước lot; 8 unit tests và smoke test trên FTMO demo | Phí/chi phí dự phòng do người dùng cung cấp; chưa tự lấy phí hợp đồng/lịch tin. SL không bảo đảm giá khớp |
| Lưu và tiếp nối | Reuse `education/progress.json`, sổ demo, dữ liệu và báo cáo local | Setup không nâng trạng thái học viên hoặc chứng minh edge |

## Luồng dữ liệu và phạm vi

MT5 đã đăng nhập demo → MCP loopback/SDK → file nghiên cứu local → kiểm tra dữ liệu → code chiến lược → Strategy Tester → báo cáo → demo có quan sát. Nội dung chart/báo cáo được đọc vào ngữ cảnh AI khi cần; không upload toàn bộ lịch sử hay thông tin tài khoản sang dịch vụ mới.

Hai MCP dùng key trong `.codex/config.toml`; không chép key vào tài liệu, log hoặc lệnh ví dụ. Cổng hiện tại: MetaEditor `22345`, Terminal `22344`, chỉ `127.0.0.1`. Key trong chat trước đây nên được người dùng đổi khi tiện; không tự xoay key hay sửa quyền hệ thống trong lượt này.

Config project đã thêm `disabled_tools` cho sáu thao tác đặt/sửa/hủy/đóng lệnh và `chart_add_expert`. Danh sách này **chưa được xác nhận nạp lại trong runtime hiện tại**; có hiệu lực sau khi Codex nạp config và phải kiểm tra tool registry. Đây là bộ lọc công cụ, **không phải sandbox** cho SDK, MQL5, HTTP hoặc code tùy ý. Helper `toolkit.py` chỉ cung cấp doctor, size và annotation; không có nhánh giao dịch tài khoản.

Không bật Algo Trading, không gắn EA mới lên chart tài khoản, không thay hai MacGateway đã tồn tại. Không trả phí hoặc bật MQL5 Cloud. Probe dùng `UseLocal=1`, `UseRemote=0`, `UseCloud=0`, `ShutdownTerminal=0`.

## Các lệnh bảo trì cho gia sư

Chạy từ `D:\ANNAM\TradingWorkspace`, khi FTMO desktop đang mở:

```powershell
education/.venv-mt5/Scripts/python.exe education/tools/mt5/toolkit.py doctor
education/.venv-mt5/Scripts/python.exe education/tools/mt5/toolkit.py doctor --run-id 7684646101493876814
education/.venv-mt5/Scripts/python.exe -m unittest discover -s education/tools/mt5 -p test_toolkit.py -v
education/.venv-mt5/Scripts/python.exe education/check_setup.py
```

Ví dụ tính số **giả định**, không phải giá vào hiện tại hay phí FTMO đã xác nhận:

```powershell
education/.venv-mt5/Scripts/python.exe education/tools/mt5/toolkit.py size --side buy --entry 1.1052 --stop 1.1012 --risk 10 --commission-per-lot 6 --reserve 1
```

`--commission-per-lot` là USD/lot **cả vòng**; `--reserve` là USD dự phòng tổng cho lệnh (ví dụ trượt giá/swap/chi phí cố định), không là mức tối đa được bảo đảm. Hai giá là giá khớp dự tính; không trừ spread lần hai nếu đã phản ánh trong chúng. Hàm làm tròn xuống và trả 0 lot nếu lot tối thiểu vượt ngân sách. Kết quả minh họa đã kiểm tra: 0,02 lot, lỗ dự tính gồm dự phòng 9,12 USD, ký quỹ 73,68 USD theo cấu hình tài khoản lúc kiểm tra. Đủ ký quỹ không đồng nghĩa được phép vào lệnh hoặc không vi phạm drawdown quỹ.

Chú thích chart: lấy `chart_id` mới bằng doctor; quan sát ảnh trước. Chỉ dùng chart EURUSD H1 riêng, không có EA. Lệnh dưới là ví dụ tái tạo vùng **minh họa công cụ**, không phải setup BR-01:

```powershell
education/.venv-mt5/Scripts/python.exe education/tools/mt5/toolkit.py annotate --chart-id 45954224258428 --start 2026-09-11T16:00:00 --end 2026-09-11T23:00:00 --high 1.16135 --low 1.15985 --tag SETUP_20260912 --label Minh_hoa_cong_cu_KHONG_la_tin_hieu
```

Giờ nhập là **giờ server trên chart**, không phải giờ Việt Nam hay UTC. Tag mới tạo nhóm đối tượng mới; tag cũ chỉ được cập nhật nhãn khi các anchor không đổi. Kiểm tra thời gian sửa file, nội dung log và ảnh mới, vì lỗi script có thể để lại ảnh cũ. Không dùng tag cũ để di chuyển zone theo kết quả tương lai. `InpPresentation=true` chỉ dùng riêng chart RoadMap để tạo khoảng trống bên phải và bỏ grid; mặc định không đổi bố cục.

### Biên dịch và tester

1. Gọi `get_workspace_info` trước mỗi phiên; lấy `mql5_folder`, không đoán đường dẫn terminal.
2. Native MetaEditor `compile_file` với `Scripts\RoadMap\RoadMapAnnotate.mq5` hoặc `Experts\RoadMap\RoadMapSetupProbe.mq5`. Probe từ chối chạy ngoài tester và không có hàm giao dịch.
3. Kiểm tra `MQL5\Profiles\Tester\RoadMapSetupProbeLocal.ini` trước khi dùng. Đây là config probe một ngày, **không dùng thay config kiểm chứng chiến lược**.
4. Terminal `tester_run_backtest` với `config_path` tuyệt đối và `wait=false`; giữ run_id trả về. Đọc status/report theo đúng run_id, không nhầm tester cũ. Chỉ dừng run do mình tạo nếu cần.
5. Với backtest chiến lược thật: version hóa luật/config, kiểm tra phí/khớp lệnh, quyết định dữ liệu được phép dùng trước khi chạy; lưu báo cáo cùng provenance. Không có runner tự tối ưu tham số hoặc tự mở holdout.

## File trên máy và cách nối lại

MQL5 root đã xác minh:
`C:\Users\MIIKEY\AppData\Roaming\MetaQuotes\Terminal\81A933A9AFC5DE3C23B15CAB19C63850\MQL5`

- `Experts\RoadMap\RoadMapSetupProbe.mq5/.ex5`: kiểm tra tester.
- `Scripts\RoadMap\RoadMapAnnotate.mq5/.ex5`: chú thích, không đặt lệnh.
- `Profiles\Tester\RoadMapSetupProbeLocal.ini`: tester local, không cloud.
- `Profiles\Templates\RoadMap_SETUP_20260912.tpl`: template đã lưu, chưa thử đóng/mở terminal để xác nhận phục hồi toàn phiên.
- `Files\RoadMap_SETUP_20260912.png/.txt`: ảnh và anchor log.
- `education/tools/mt5/evidence/`: báo cáo probe và nghiệm thu setup.

Nếu mất kết nối: mở đúng FTMO terminal và MetaEditor/F4, chạy doctor. HTTP 401: kiểm tra key đang hiển thị trong app so với config **không in key ra chat**. Connection refused: kiểm tra app có mở và cổng có đúng không. Không suy mọi lỗi là do key. Nếu native Terminal chưa xuất hiện, nối lại MCP/reload Codex khi tiện; đường HTTP trực tiếp đã được kiểm tra nên không cần cài server trùng chức năng. Không dừng terminal hoặc đổi tài khoản khi còn công việc đang chạy.

Rollback chỉ cần bỏ filter mới nếu muốn phục hồi danh sách tool, và bỏ riêng nhóm file/đối tượng `RoadMap` do setup tạo sau khi xác nhận. Không xóa toàn bộ MQL5/profile/chart hay thay MacGateway. Không có service mới phải gỡ.

## Phần nghiên cứu còn lại — không phải thiếu công cụ

Kho dữ liệu: [DATA-REPORT.md](../../research/br01-screen/DATA-REPORT.md); gate hiện hành: [LATEST.json](../../research/br01-screen/quality-data/LATEST.json). Đã có khoảng 54,7 triệu ticks FTMO cho 2023–2024, nhưng chưa duyệt backtest thực thi không điều kiện trên toàn kỳ: còn giờ thiếu, OHLC lệch, gap cần đối chiếu và mô hình chi phí/lịch tin chưa duyệt. Holdout 2025 vẫn chưa dùng. Không lấy smoke test thành bằng chứng bộ dữ liệu hoặc BR-01 có edge.

Bước tiếp theo của nghiên cứu là xử lý/phân định dữ liệu được phép dùng và hoàn thiện engine BR-01 theo luật cố định, rồi baseline ngoài chi phí, kiểm tra độ bền và holdout. Không cài thêm MCP để thay thế các kiểm tra này.

## Nguồn chính thức

- [Codex MCP](https://developers.openai.com/codex/mcp/): config HTTP, enabled/disabled tools và tool registration.
- [MT5 Python integration](https://www.mql5.com/en/docs/python_metatrader5): SDK đọc account/symbol, tính profit/margin.
- [MT5 release notes](https://www.metatrader5.com/en/releasenotes/terminal/2464): đối chiếu tính năng MCP; hành vi ở trên được kiểm tra trực tiếp trên build 6191.

Không có phép đo cho thấy bộ công cụ này tự cải thiện lợi nhuận hoặc hiệu quả học. Quyết định giữ hai MCP và helper nhỏ nhằm giảm phần phải bảo trì; bằng chứng hiện tại là thao tác thực tế, compile, tester, ảnh và tests.
