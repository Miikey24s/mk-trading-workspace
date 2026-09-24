# mk-trading-workspace

Không gian làm việc nghiên cứu, học tập và phát triển hệ thống giao dịch thuật toán (Algorithmic Trading & Research Workspace).

## 1. Cấu trúc Workspace & Submodules

Workspace tổng thể quản lý các dự án thành phần dưới dạng Git Submodules:

| Dự án | Đường dẫn | Repository nguồn | Mô tả |
| :--- | :--- | :--- | :--- |
| **mt5-tradingview-backtester** | `projects/mt5-tradingview-backtester` | [wuangnv/mt5-tradingview-backtester](https://github.com/wuangnv/mt5-tradingview-backtester) | Hệ thống backtest, replay chart TradingView và kết nối MT5 |
| **mk-ai-dubber** | `projects/vi-dubber` | [Miikey24s/mk-ai-dubber](https://github.com/Miikey24s/mk-ai-dubber) | Công cụ lồng tiếng / dịch video khóa học trading tự động |
| **mk-quant-trading** | `projects/quant-trading` | [Miikey24s/mk-quant-trading](https://github.com/Miikey24s/mk-quant-trading) | Nghiên cứu định lượng, factor model và chiến lược quant |
| **mk-trading-agents** | `projects/TradingAgents` | [Miikey24s/mk-trading-agents](https://github.com/Miikey24s/mk-trading-agents) | Hệ thống đa tác tử AI phân tích thị trường (Fork từ TauricResearch) |

Các thư mục tài liệu & điều phối cốt lõi:
- `planning/`: Kế hoạch chi tiết, tiến độ các mốc, hợp đồng dữ liệu và kiến trúc (PATH-2).
- `education/`: Khóa học trading, tài liệu học tập và nhật ký thực hành.
- `tooling/`: Bộ công cụ điều phối worker, runner và tự động hóa kiểm thử UI QA (Playwright).
- `UI/`: Design system, token giao diện và hợp đồng frontend.
- `miro/`: Bản đồ kiến trúc trực quan.

## 2. Hướng dẫn Clone & Cài đặt

### Cách 1: Clone toàn bộ trong 1 lệnh (Khuyên dùng)
Để clone repository cha và tự động kéo toàn bộ code của 4 submodules về ngay lập tức:

```bash
git clone --recurse-submodules https://github.com/Miikey24s/mk-trading-workspace.git
```

### Cách 2: Nếu đã lỡ clone thông thường
Nếu bạn đã clone mà chưa có cờ `--recurse-submodules`, chỉ cần chạy lệnh sau tại thư mục gốc:

```bash
git submodule update --init --recursive
```

### Cập nhật submodules khi có thay đổi từ remote
```bash
git submodule update --remote --merge
```
