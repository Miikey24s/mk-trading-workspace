# Bản nháp hỏi FTMO — chưa gửi

Không chứa số tài khoản, mật khẩu, MCP key, vị thế hoặc thông tin cá nhân. Nếu cần FTMO tra tài khoản, người dùng tự cung cấp qua kênh support chính thức.

**Subject: EURUSD historical tick coverage and backtesting metadata — MT5 FTMO-Demo**

Hello FTMO Support,

I am preparing an internal EURUSD backtest with historical quotes from the FTMO-Demo MT5 server (terminal build6191). Could you please clarify the following?

1. H1 bars are available for2018–2022, but `copy_ticks_range(COPY_TICKS_ALL)` returned no data for monthly ranges throughout2018–2019. Is tick history before2020 available from your archive or another supported export method?
2. The following server-clock intervals have native H1 bars but return zero quote ticks in both daily and separate hourly requests:
   - 2021-10-01 00:00–13:59:59
   - 2022-06-27 23:00–23:59:59
   - 2022-07-07 23:00–23:59:59
   - 2024-05-07 00:00–21:59:59
   Can these intervals be restored/exported, or are they known archive gaps? We re-requested all four days and each of their 24 hours, with successful API error codes and matching repeated snapshots. After correcting Python datetime endpoint truncation (requesting through the boundary then filtering time_msc to a half-open interval), the hourly concatenation matches the full-day retrieval. The 38 hourly gaps remain. Native Terminal MCP also returns no ticks for sampled gaps and reports EURUSD tick data_available_from as 2020.01.02 00:00:00. A control interval on 2024-05-08 returns ticks normally. No cache files have been deleted or reset.
3. Native Bid H1 and H1 reconstructed from downloaded ticks disagree for122bars in2021 and1,202bars in2022. Example: server2021-04-22 11:00 native/derived Close differs by2points; 12:00 Open differs by2points. Are native bars and tick archives sourced or revised differently? Which dataset should be treated as authoritative for retrospective research?
4. Please confirm server timezone and DST transition rules for2018–2024, and any historical EURUSD session changes relevant to the gaps above, including2024-03-11 00:00.
5. Your current symbol page displays EURUSD commission5USD/lot. Is that per side or roundtrip, and can you provide the commission schedule/effective dates for2018–2024, or confirm whether those historical conditions can be reconstructed?
6. Is an export of your EUR/USD high-impact economic calendar for2018–2024 available, including timezone, scheduled timestamp and impact classification? The public FTMO calendar returned no events for2018-01-01 to2018-01-07, while its stated source Forex Factory has events for that week. Can historical publication-time versions be obtained, or only the currently revised archive?

This is for local education/research only, not redistribution. No account credentials or trading access are requested. Thank you.
