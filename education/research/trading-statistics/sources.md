# Danh mục nguồn / Source Registry

Mỗi source có một ID ổn định để `evidence.csv` tham chiếu. Source registry chỉ mô tả nguồn; đánh giá claim nằm ở từng record trong `evidence.csv`.

## Nguồn video / Video sources

### SRC-YT-TRADING-MATH

- Title: *The Math of Winning in Trading*
- Creator: Mulham Trading
- URL: https://www.youtube.com/watch?v=BAfRVpKIxZ4
- Upload date from YouTube metadata: 2026-05-31
- Duration: 14:14
- Các chương chính (Main chapters): Kỳ vọng (Expectancy), Thiết kế hệ thống (System Design), Phương sai (Variance), Rủi ro (Risk)
- Dùng trong hub (Use in hub): sơ đồ giảng giải, công thức và ví dụ của creator
- Cách xử lý bằng chứng (Evidence treatment): công thức có thể kiểm chứng độc lập; chart/simulation vẫn là creator model cho tới khi tái lập
- Timestamp quan trọng: 01:17 expectancy; 04:13 system design; 06:25 breakeven; 06:54 variance; 08:15 gambler's fallacy; 09:19 risk; 10:09 sizing; 11:30 risk of ruin

### SRC-YT-PROP-MATH

- Title: *The Math of Winning in Prop Firms*
- Creator: Mulham Trading
- URL: https://www.youtube.com/watch?v=vGSpbspmGoM
- Upload date from YouTube metadata: 2026-09-09
- Duration: 22:53
- Các chương chính (Main chapters): Tài khoản (Account), Lợi thế (Edge), Rủi ro (Risk), Luật (Rules), Lợi nhuận (Returns)
- Dùng trong hub (Use in hub): mô hình ngưỡng prop challenge, ví dụ xác suất pass, sơ đồ chồng rule và kinh tế payout
- Cách xử lý bằng chứng (Evidence treatment): creator simulation/model cho tới khi assumptions và calculation được tái lập; không dùng làm tỷ lệ pass phổ quát cho prop firm
- Important timestamps: 00:22 account; 04:31 edge; 11:38 risk; 17:09 rules; 20:57 returns

## Nguồn học thuật / quản lý đã dùng trong audit

### SRC-ESMA-2018

- European Securities and Markets Authority (ESMA), 2018
- *Additional information on the agreed product intervention measures relating to contracts for differences and binary options*
- URL: https://www.esma.europa.eu/sites/default/files/library/esma35-43-1000_additional_information_on_the_agreed_product_intervention_measures_relating_to_contracts_for_differences_and_binary_options.pdf
- Use: retail CFD loss-rate base rate

### SRC-CHAGUE-2020

- Fernando Chague, Rodrigo De-Losso, Bruno Giovannetti
- *Day Trading for a Living?*, 2020 revision
- URL: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3423101
- Use: persistence and profitability base rate for Brazilian equity-futures day traders

### SRC-BARBER-2014

- Brad M. Barber, Yi-Tsung Lee, Yu-Jane Liu, Terrance Odean
- *The Cross-Section of Speculator Skill: Evidence from Day Trading*, Journal of Financial Markets 18, 2014
- DOI: https://doi.org/10.1016/j.finmar.2013.05.006
- Use: persistence of skill and rarity of predictably positive net abnormal returns

### SRC-BARBER-ODEAN-2001

- Brad M. Barber, Terrance Odean
- *Boys Will Be Boys: Gender, Overconfidence, and Common Stock Investment*, QJE 116(1), 2001
- DOI: https://doi.org/10.1162/003355301556400
- Use: gender/turnover/cost mechanism in one historical brokerage sample

### SRC-FENG-SEASHOLES-2008

- Lei Feng, Mark S. Seasholes
- *Individual investors and gender similarities in an emerging stock market*, Pacific-Basin Finance Journal 16(1-2), 2008
- DOI: https://doi.org/10.1016/j.pacfin.2007.04.003
- Use: counter-evidence against a universal gender-performance rule

### SRC-DEMIGUEL-2009

- Victor DeMiguel, Lorenzo Garlappi, Raman Uppal
- *Optimal Versus Naive Diversification: How Inefficient Is the 1/N Portfolio Strategy?*, Review of Financial Studies 22(5), 2009
- DOI: https://doi.org/10.1093/rfs/hhm075
- Use: estimation-error example for simple vs complex models

### SRC-BARBER-ODEAN-2000

- Brad M. Barber, Terrance Odean
- *Trading Is Hazardous to Your Wealth*, Journal of Finance 55(2), 2000
- DOI: https://doi.org/10.1111/0022-1082.00226
- Use: turnover and net performance

## Nguồn tự tính / local (Derived / local sources)

### SRC-DERIVED-MATH

- Internally derived calculations with assumptions stated in each evidence row.
- Use only when formula and assumptions are explicit.
- Examples: Wilson interval, IID losing-streak probability, breakeven win-rate formula.

### SRC-LOCAL-BR01

- Local TradingWorkspace candidate: EURUSD H1 breakout-first-retest `BR-01 v0`.
- Current state: candidate only; edge not established.
- Use: candidate-specific evidence once data gate, costs, rules and validation protocol are sufficient.

## Báo cáo audit dài liên quan / Related long-form audit

- `../strategy-probability-framework-2026-09-15.md`
- This is the narrative methodology/evidence audit that preceded this structured hub.
