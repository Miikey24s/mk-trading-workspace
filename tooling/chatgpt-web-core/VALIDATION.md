# Validation — 19/10/2026

Scope: shared source snapshot, tool-free entrypoint và runtime wrapper MT5.
Chưa nghiệm thu provider sinh câu trả lời thật, UI chiến lược hoặc VI Dubber parity.

- Bun1.4.2; `bun install --frozen-lockfile --ignore-scripts` thành công.
- `bun run typecheck`: pass.
- `bun run test`: 9/9, gồm HTTP loopback qua Responses parser/envelope thật với
  synthetic adapter, isolation, auth, forbidden payloads, timeout và single-flight.
- `bun run test:transport`: 173/173 trên6files; giữ browser login, DOM remount,
  model routing/catalog và request-body behavior. Lượt đầu thiếu fixture HTML;
  đã nhập fixture gốc kèm SHA-256 và chạy lại đủ6files thành công.
- Wrapper MT5 `Init`/`Status`: home riêng, port17851, không có login state.
- Smoke process thật: health đúng service, catalog quảng bá2routes trước login,
  request trả503 `login_required`, admin route trả404. Không gửi request sinh
  nội dung ra ChatGPT. Listener được dừng sau smoke.
- Hash config Codex global và VI Dubber không đổi qua smoke.
- Snapshot SHA-256 được test với source manifest. Pattern scan không tìm thấy
  private-key/JWT/provider-key-shaped credentials trong source nhập.
- Git ignore chặn config runtime, node_modules và test log. Không nhập Git
  history, browser login state hoặc dữ liệu runtime của core cũ.
- Export riêng source đã stage từ Git tree, cài lại theo lock, typecheck và
  9/9core tests pass; hash vẫn đúng sau Git normalization. Bản rehearsal local
  ở `.runtime/chatgpt-core-checkout-68f631d8/`, không dùng dependency symlink.
- AI environment audit: 0errors/0warnings; instruction chain20,203bytes,
  còn45,333bytes trong ceiling65,536bytes. Không thêm instruction global.

Smoke receipt/log local nằm trong workspace `.runtime/mt5-chatgpt-web/`, không
commit vì thư mục runtime chứa config/token. Có thể lặp lại các checks offline
từ README. Marker/cached catalog không chứng minh login hoặc model còn dùng
được trên mạng; cần login riêng và một provider smoke khi tiếp slice chiến lược.
