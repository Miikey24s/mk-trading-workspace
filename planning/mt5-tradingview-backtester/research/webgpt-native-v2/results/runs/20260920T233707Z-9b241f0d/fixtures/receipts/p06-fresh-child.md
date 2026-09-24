# Fresh-context recovery receipt

- Canonical agent id: `/root/p06_fresh_recovery`
- Canonical task id: `p06-recovery-next`
- `fork_turns`: `none` (fresh-context task setup; no parent history was provided)
- Accepted dependency `p01`: expected `3d57633b12cfae7915b3b71eac881128d2e4db66fc619decc76c7fee347ffc3a`; observed `3d57633b12cfae7915b3b71eac881128d2e4db66fc619decc76c7fee347ffc3a`
- Accepted dependency `p03-good`: expected `7d14d40515651e5c80dbe84f36774b7ddd25ad210db876ec2476a7b85005764c`; observed `7d14d40515651e5c80dbe84f36774b7ddd25ad210db876ec2476a7b85005764c`
- Pending task chosen: `p06-recovery-next`
- Uncertain task left untouched: `p07-partial`
- Output: `fixtures/work/p06-recovered.txt`
- Output SHA256: `41dd4e2a31e38e9becd0efa0c8071eba8bc91352dfef9510f2864e54bf4681be`
- Tools: `exec_command` for checkpoint/read/hash/time verification; `apply_patch` for both created files
- Paths read: `fixtures/recovery-checkpoint.json`, `fixtures/work/p01-output.txt`, `fixtures/work/p03-good.txt`, `fixtures/work/p06-recovered.txt`
- Paths written: `fixtures/work/p06-recovered.txt`, `fixtures/receipts/p06-fresh-child.md`
- UTC finish: `2026-09-20T23:58:21.0599994Z`
