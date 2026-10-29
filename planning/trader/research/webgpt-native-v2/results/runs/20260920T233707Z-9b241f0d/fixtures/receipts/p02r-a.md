# P02 retry lane A receipt

- Canonical task / agent id: `/root/p01_single_fresh`
- Barrier target UTC: `2026-09-20T23:46:03.6700386Z`
- Actual start UTC: `2026-09-20T23:46:41.8271990Z`
- Actual end UTC: `2026-09-20T23:46:56.8861753Z`
- Measured duration: `15.0589763` seconds
- Source/input hash: `not applicable` (task specified a fixed literal output; no input file was read)
- Output SHA256: `a3037a4ba9e9c213f9c3b19fc9810d0626fcd27cf2dbcd843c2d9118eac6dbb5`
- Tools actually used: `Codex_Native2.codex_exec`, `Codex_Native2.codex_apply_patch`
- Paths read: `fixtures\work\p02r-a-output.txt` (post-write verification only)
- Paths written: `fixtures\work\p02r-a-output.txt`, `fixtures\receipts\p02r-a.md`
- Verification: output was re-read from disk after writing and SHA256 was measured from that file.
- Timing note: the requested barrier had already passed when this retry's shell command began; this receipt records the measured actual start rather than treating the barrier target as the start.
