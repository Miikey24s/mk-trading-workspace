# Autonomous trading trong giai đoạn vắng chủ 2 năm — feasibility research

Ngày: 2026-09-28
Trạng thái: **RESEARCH / PREP-ONLY**
Phạm vi: đánh giá 2–3 tháng chuẩn bị trước khi chủ sở hữu thực hiện nghĩa vụ quân sự tại Việt Nam, với giả định không thể thao tác hệ thống thường xuyên trong khoảng 24 tháng.

Memo này không cấp quyền mở broker, API, OAuth, ví, giao dịch live hay chuyển tiền. Không có phần nào là cam kết lợi nhuận. Mục tiêu phù hợp để ra quyết định là **hệ thống có thể vận hành an toàn trong điều kiện owner vắng mặt**, không phải “AI tự in tiền”.

## 1. Kết luận điều hành

Trong 2–3 tháng có thể làm được một **autonomous pilot bị giới hạn**: strategy deterministic, forward/paper evidence, risk engine fail-closed, reconciliation, monitoring, restart/recovery và nếu mọi gate đạt thì live pilot vốn nhỏ. Không đủ thời gian để chứng minh hệ thống sẽ kiếm “rất nhiều tiền” bền vững trong 24 tháng.

Khả năng một solo owner để bot AI chạy không người trong 2 năm và vẫn sinh lời ổn định là **thấp/không xác định**. Các tổ chức systematic/algorithmic trading có automated execution, nhưng mô hình vận hành bình thường vẫn có risk controls, testing, monitoring, incident response và người chịu trách nhiệm. “Một bot AI chạy 2 năm không cần can thiệp” không phải bằng chứng của edge.

Quyết định khuyến nghị: **GO cho chuẩn bị và shadow/paper; chỉ GO live có giới hạn sau khi qua gate; NO-GO cho vốn lớn, đòn bẩy cao, prompt-to-order hoặc AI tự sửa strategy/quyền tiền.**

## 2. Bối cảnh nghĩa vụ quân sự và các giả định

Luật Nghĩa vụ quân sự 2015, Điều 21 quy định thời hạn phục vụ tại ngũ thời bình là 24 tháng; luật có cơ chế kéo dài tối đa 6 tháng trong các trường hợp được luật định. Bản PDF đã ký trên Cổng thông tin điện tử Chính phủ: [Luật Nghĩa vụ quân sự 2015 (PDF)](https://datafiles.chinhphu.vn/cpp/files/vbpq/2015/05/3887.signed.pdf).

Đây chỉ xác nhận khung pháp lý của thời hạn; các chi tiết cá nhân như ngày giao nhận quân, lịch huấn luyện, quyền dùng điện thoại/internet, khả năng giữ OTP/MFA và khả năng xin phép xử lý tài khoản là **unknown**. Kế hoạch phải giả định không có quyền truy cập thường xuyên, không có thao tác thủ công khẩn cấp và không có bảo đảm kết nối.

## 3. Mức độ chắc chắn của research

### Đã xác minh hoặc có primary source

- Thời hạn 24 tháng và văn bản luật: PDF Chính phủ ở trên.
- FINRA Regulatory Notice 15-09 đã truy cập được và mô tả năm nhóm kiểm soát cho algorithmic strategies: risk assessment/response, code development/implementation, testing/system validation, trading systems và compliance. Văn bản còn nêu việc theo dõi lỗi hệ thống, review tham số risk control, capacity, access/entitlement, downstream market impact và giới hạn khả năng bypass controls: [FINRA Regulatory Notice 15-09](https://www.finra.org/rules-guidance/notices/15-09). Đây là benchmark kỹ thuật/quản trị của Mỹ, không tự biến thành luật Việt Nam.
- NIST AI Risk Management Framework là nguồn chính thức cho governance, đo lường rủi ro, monitoring và quản lý vòng đời AI: [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework). Nó không trao execution authority cho AI.
- SEC Market Access Rule là tham chiếu primary về pre-trade risk limits, erroneous-order prevention và kiểm soát truy cập đối với market access: [17 CFR 240.15c3-5](https://www.ecfr.gov/current/title-17/chapter-II/part-240/section-240.15c3-5). Tính áp dụng trực tiếp phụ thuộc venue/broker và pháp luật liên quan.

### Suy luận kỹ thuật có điều kiện

- Trong môi trường owner vắng, failure mode quan trọng hơn thêm model: mất data, stale price, API reject, clock drift, duplicate order, position mismatch, provider outage, account lock, key expiry, disk full, model drift và không có người xử lý.
- Một system có thể chạy 24/7 chưa đồng nghĩa với system có thể giữ edge 24 tháng. Reliability, risk containment và capital preservation phải được chứng minh riêng với profitability.
- AI nên làm research/ranking/regime/anomaly/advisory; execution intent phải qua schema, deterministic risk engine, broker adapter và reconciliation. AI trade authority là một công tắc quyền hạn riêng và phải fail-closed.

### Chưa thể kết luận trong memo này

- Thuế, tư cách pháp lý và điều kiện giao dịch cụ thể của từng broker/exchange/asset tại Việt Nam.
- Việc broker có chấp nhận delegated recovery, power of attorney, alternate MFA hay không.
- Dữ liệu, vốn, phí, đòn bẩy, thanh khoản và strategy cụ thể của hệ thống có tạo edge sau chi phí hay không.
- Khả năng liên lạc và hỗ trợ thực tế trong đơn vị quân đội; cần xác nhận từ nguồn có thẩm quyền, không suy đoán.

## 4. Feasibility matrix

| Hạng mục | Trong 2–3 tháng? | Điều kiện tối thiểu | Quyết định |
|---|---:|---|---|
| Data contract, provenance, known-at/cutoff | Có | Replay prefix, hash, duplicate/late-data policy | **Must-have** |
| Một baseline deterministic | Có | Cost/slippage/latency model, OOS/WFO, null/baseline | **Must-have** |
| Paper/forward soak 30–60 ngày | Có nếu bắt đầu ngay | Không look-ahead, receipt đầy đủ, reconciliation zero drift | **Must-have** |
| Risk/kill switch/restart/reconciliation | Có | Hard limits, stale/gap/mismatch pause, idempotency, recovery drill | **Must-have** |
| 24/7 hosting và observability | Có | Auto-restart, healthcheck, logs/metrics, backup, alert route | **Must-have** |
| Capped live pilot | Có điều kiện | Mọi gate đạt, vốn nhỏ tách biệt, không withdrawal permission | **Conditional GO** |
| Multi-strategy diversification | Có sau baseline | Từng sleeve có evidence riêng, correlation/portfolio risk | **P1** |
| LLM/Typesafe AI advisory | Có | Typed output, abstain, model/weight hash, không gọi order | **P1** |
| RL/GNN/TDA/chaos/SOC/MEV | Không nên là critical path | Fixture, OOS, null, cost và ops benchmark | **Defer/P1 sandbox** |
| HFT tick engine, QPU, SNN, MuZero, self-evolving live agent | Không | Hardware/data/ops và evidence chưa có | **Defer/NO-GO** |
| “Thu nhập lớn, đều, không giám sát 24 tháng” | Không thể chứng minh | Không có test thay thế cho tương lai | **NO-GO claim** |

## 5. Thứ tự quan trọng cho AI/bot trade

1. **Risk containment và reconciliation:** max position/notional, daily/weekly loss, order count, leverage, stale-data/price-gap/clock-gap halt, position mismatch, duplicate/idempotency, emergency pause.
2. **Data correctness và causal timing:** source completeness, `known_at <= decision_at`, corporate-action/rollover/fee/slippage, hash/provenance, late/duplicate handling.
3. **Edge sau chi phí và OOS:** walk-forward/purged split, locked holdout, cross-symbol/regime, stress fee/slippage/gap/latency, sensitivity/ablation/null.
4. **Operations và recovery:** process supervision, auto-restart, state snapshot, deterministic replay, backup/restore, provider/API outage, disk/clock/secret expiry.
5. **Security và account continuity:** least-privilege API, withdrawal disabled, IP allowlist, separate account/capital, secret rotation, KYC/MFA/recovery plan và lawful delegate.
6. **Capital/risk budget:** vốn chịu mất được, 24-month burn reserve, max drawdown/ruin constraint, no high leverage, pause policy.
7. **AI advisory:** regime classification, anomaly/OOD, research ranking, journal/explanation, local fallback; uncertainty/abstain phải là output hợp lệ.
8. **UI và advanced research:** giúp kiểm tra/điều hành nhưng không thay risk gate; chỉ promote công nghệ khi thắng incumbent trên cùng fixture về correctness, OOS, latency, memory, cost và rollback.

## 6. Critical path 90 ngày

### Ngày 1–14 — đóng contract và continuity

- Chọn một strategy deterministic và một venue được pháp lý/broker xác minh; không mở nhiều venue để “đa dạng” sớm.
- Chốt risk budget bằng VND, max drawdown, max exposure, leverage = 0 hoặc rất thấp ở pilot.
- Viết owner-absence runbook: key expiry, account lock/KYC, provider outage, incorrect position, kill switch, restore và điều kiện kết thúc.
- Kiểm tra lawful account recovery/MFA/delegate với broker/ngân hàng; nếu không xác nhận được thì live gate không đạt.

### Ngày 15–35 — evidence offline

- Canonical data receipt, cost/slippage/latency model, replay prefix và causal cutoff.
- Baseline, null, WFO/purged OOS, locked holdout; report net-of-fee, drawdown, turnover, tail loss.
- Không dùng backtest đẹp hoặc in-sample Sharpe làm quyền live.

### Ngày 36–60 — paper/forward và fault injection

- Chạy paper/forward tối thiểu 30 ngày (tốt hơn 60 ngày), mọi intent/fill/reconciliation có receipt.
- Diễn tập restart, duplicate event/order, stale data, disconnect, bad quote, rejected order, clock drift, disk full, provider timeout và restore.
- Alert phải tới được một kênh có người chịu trách nhiệm; nếu không ai có thể phản ứng trong 24 tháng, alert chỉ có giá trị quan sát, không phải recovery.

### Ngày 61–75 — shadow 24/7 và owner-absence rehearsal

- Chạy không can thiệp thủ công trong nhiều chu kỳ thị trường; kiểm tra memory leak, state growth, log rotation, clock và backup restore.
- Mô phỏng owner unavailable; chỉ cho phép actions đã định nghĩa trước, không prompt-to-order.

### Ngày 76–90 — quyết định

- Nếu mọi gate đạt: capped live pilot vốn nhỏ, tách reserve, withdrawal permission tắt, hard auto-pause; tiếp tục paper mirror.
- Nếu bất kỳ gate nào thất bại: **paper/research only**, không để vốn live chờ “may mắn”.

## 7. Go/no-go gates trước khi để chạy trong thời gian vắng

- [ ] Có evidence forward/paper 30–60 ngày, net-of-cost, qua ít nhất các regime đã thấy; không look-ahead.
- [ ] Mọi lệnh/fill/position có idempotency và reconciliation; không có mismatch chưa giải thích.
- [ ] Max loss, max exposure, order rate, stale/gap/mismatch/clock kill switch đã test bằng fault injection.
- [ ] Restart/restore và provider/API outage drill pass; không mất state hoặc nhân đôi lệnh.
- [ ] Uptime, logs, metrics, disk/CPU/memory/clock/secret-expiry được giám sát; alert route có người chịu trách nhiệm hoặc system auto-pause.
- [ ] API key trade-only, withdrawal off, IP allowlist, account/capital tách biệt; secrets không nằm trong repo/log/receipt.
- [ ] KYC/MFA/account lock/2FA/recovery/delegate đã được venue xác nhận bằng văn bản; nếu không, NO-GO live.
- [ ] Có reserve vốn cho 24 tháng và stop policy; không cần rút lợi nhuận để sống trong thời gian owner vắng.
- [ ] AI không tự thay model/strategy/risk limit hoặc tự mở quyền execution; mọi thay đổi đi qua versioned artifact và promotion gate.
- [ ] Có phương án legal/tax/account review sau khi trở về; giữ audit trail.

## 8. Trading so với nguồn thu khác

Trading bot có thể là nguồn tự động hóa chính nhưng có variance, tail risk, regime shift và operational risk cao. Trong 2–3 tháng, mục tiêu hợp lý là **preserve capital + thu thập evidence**, không đặt kế hoạch tài chính 2 năm dựa trên một mức lợi nhuận giả định.

Nguồn thu phụ như bán công cụ, research/data product hoặc dịch vụ phần mềm có thể giảm phụ thuộc vào market edge, nhưng cũng cần customer support, billing, pháp lý và người xử lý. Không nên mở thêm business lane trước khi trading engine đạt contract/ops baseline; nếu có làm thì chỉ static/digital product không cần owner online.

## 9. “Có ai làm như thế không?”

Có các quỹ và công ty systematic/algorithmic trading vận hành automated strategies ở quy mô lớn. Nguồn FINRA ở trên chính là tài liệu giám sát các firm dùng algorithmic strategies và mô tả các lớp testing/control cần có. Điều đó chứng minh automated trading là một mô hình có thật; nó **không** chứng minh một cá nhân có thể bỏ hệ thống 24 tháng không giám sát mà kiếm lợi nhuận ổn định. Mô hình institutional thường có nhiều người, redundancy, compliance, on-call và vốn/limits khác hẳn một solo deployment.

Các quảng cáo “AI bot passive income”, “lợi nhuận đều không cần kinh nghiệm” không được xem là evidence. Chỉ chấp nhận track record có timestamp, gross/net costs, fills, drawdown, account statement hoặc third-party audit có thể kiểm tra; screenshot/testimonial không đủ.

## 10. Recommendation

Đặt mục tiêu trước ngày nhập ngũ là **“survivable autonomous research/pilot”**. Không đặt mục tiêu “tự kiếm tiền chắc chắn”. Nếu owner không thể đảm bảo continuity hợp pháp và response/recovery, hệ thống nên tự động **không giao dịch** và tiếp tục thu thập paper evidence. Bảo toàn vốn và auditability là thành công; lợi nhuận chỉ là kết quả có điều kiện, không phải acceptance criterion độc lập.

### Nguồn primary đã đối chiếu

- [Luật Nghĩa vụ quân sự 2015 — Cổng thông tin điện tử Chính phủ (PDF đã ký)](https://datafiles.chinhphu.vn/cpp/files/vbpq/2015/05/3887.signed.pdf)
- [FINRA Regulatory Notice 15-09 — Guidance on Effective Supervision and Control Practices for Firms Engaging in Algorithmic Trading Strategies](https://www.finra.org/rules-guidance/notices/15-09)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [17 CFR § 240.15c3-5 — Risk management controls for market access](https://www.ecfr.gov/current/title-17/chapter-II/part-240/section-240.15c3-5)

Ghi chú nguồn: trang eCFR và SEC/CFTC có rate-limit/anti-automation trong phiên research này; không dùng bản fetch lỗi làm evidence. Các nhận định pháp lý Việt Nam về venue, crypto, thuế, broker TOS và ủy quyền tài khoản vẫn là **unknown** cho đến khi kiểm tra đúng cơ quan/venue.

**Không có guarantee profit, không có claim edge, không có quyền execution được cấp bởi memo này.**
