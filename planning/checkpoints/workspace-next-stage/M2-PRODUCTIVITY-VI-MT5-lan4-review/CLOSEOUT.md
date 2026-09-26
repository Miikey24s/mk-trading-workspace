# M2 — chốt khung UI và hoàn thành QA Figma Make

26/09/2026 · **WORK: COMPLETE · REVIEW: ACCEPTED-SCOPED — UI skeleton · DOC: HANDOFF**.

**Authority:** sau khi xem kết quả lan4 và làm rõ mục tiêu ban đầu là khung xương, owner đồng ý chốt và yêu cầu: “oke, thế bạn update PLAN đi, bạn xong nhiệm vụ QA figma make rồi nha”. Quyết định này kết thúc nhiệm vụ QA Make của task `01a0dd8a-b5f5-75e3-94ef-3eb2b6b28673`. [PLAN v1.3 §6A](../../../WORKSPACE-NEXT-STAGE-PLAN.md#6a-m2-đã-đóng-đúng-scope--bàn-giao-sang-code-integration) là nguồn điều phối; receipt này ghi chi tiết scope/evidence, không là ledger sản phẩm mới.

## Đã chốt

- `lan4` là baseline UI khung xương: hướng productivity, shared shell/navigation/semantic tokens, light/dark; state VI và MT5 tách riêng.
- Bốn màn đại diện: **VI Jobs, VI Review, MT5 Chart & Replay, MT5 Report**. Destination khác giữ placeholder đúng phạm vi.
- VI dùng inline preview/fullscreen. **Không xây Watch riêng trong vòng này**; Watch/course player đi cùng MT5 Learn ở giai đoạn sau.
- Hướng frontend thử nghiệm: React 19 + TypeScript + Tailwind 4, toolchain Vite tương thích; dùng selected diff/reuse khi tích hợp, không bắt giữ React 18/Tailwind 3 của draft cũ.
- **Không cần thêm Figma Make, không chờ lan5, không tiếp tục prompt repair cũ.** Chỉ mở lại Make khi owner giao màn/luồng mới hoặc đổi thiết kế có chủ đích.

## Bằng chứng được giữ nguyên

- Export: `E:\WIN-MEDIA\Downloads\Figma_Make_M2_VI_Dubber\lan4`.
- Bản source QA cô lập: `D:\ANNAM\TradingWorkspace\tooling\ui-qa\artifacts\m2-lan4-20260926\candidate`.
- [Manifest source](../../../../tooling/ui-qa/artifacts/m2-lan4-20260926/input-manifest.json): 64 file; SHA-256 `84bda6692a859f0bd5ad4cd838d54b7fd4d3f73584d1b1e66f4ee3e1cd740f9b`. Tại QA export và copy có 0 khác biệt.
- [Kết quả runtime](../../../../tooling/ui-qa/artifacts/m2-lan4-20260926/effective-results.json): build/typecheck PASS, browser **29 PASS / 3 FAIL**. Không sửa raw test receipt thành PASS vì scope được chốt.
- [Review chi tiết](REVIEW.md): screenshots, lỗi/tái hiện, clip tổng hợp VP8 thật để kiểm decode/play/pause/offset/resume. Không chứng minh pipeline dịch/lồng tiếng, mọi codec, audio hoặc nhiều job thật.
- Lan1–lan4 là chuỗi export owner gửi từ Make; không có native round-trip product commit/Make artifact IDs hoặc benchmark credit/model đầy đủ được claim trong receipt này.

## Ba việc chuyển sang code integration

Owner đồng ý sửa sau; đây là **deferred from skeleton scope**, không phải “đã sửa” hoặc production accepted-risk. Owner thực hiện: coordinator M3 giao writer VI frontend khi tích hợp.

| ID tại PLAN | Việc và acceptance cần giữ |
|---|---|
| M3-VI-01 | Download chunk kiểm availability thật/unknown/error độc lập codec; không bật chỉ bằng http/blob prefix; giữ revision/stale/QA gates |
| M3-VI-02 | Native fullscreen → Import: chờ exit hoàn tất rồi focus dialog; kiểm Tab/Shift+Tab/Escape/restore |
| M3-VI-03 | Chuyển segment lúc phát: seek chủ động tới source time/chunk-local time đúng, không vòng lặp với timeupdate; giữ play/pause |

[Ghi chú kỹ thuật để sửa](01-REMAINING-FIXES.txt) và các scripts trong QA artifact được reuse ở lượt code integration; không cần trả lại Make chỉ để xử lý chúng. Hoàn tất các việc này trước nghiệm thu luồng media sản phẩm liên quan.

## Bước kế tiếp và ranh giới

Nhiệm vụ QA Figma Make hiện tại **đã xong**. Khi được giao tích hợp, coordinator lấy lan4 làm baseline, map components/tokens/selected diff vào repo thật, sửa ba lỗi trên và nối API/domain theo contracts. Reconcile M3/M4 và E1/Y26/FM với cùng evidence để không làm lại khám phá thiết kế hoặc QA khung đã chốt.

M2 skeleton complete không tự đóng MT5 U1d/Y26/FM full round-trip, M3 product integration, M4 shared release, VI listening/P14/production media hoặc broker/cloud gates. Các phần tích hợp của E1 còn thiếu tiếp tục ở M3. Không chạy worker, sửa app, publish, dùng Make credits hoặc mở broker/provider trong lượt cập nhật PLAN này.
