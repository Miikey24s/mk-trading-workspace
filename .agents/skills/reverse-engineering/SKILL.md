---
name: reverse-engineering
description: Inspect binaries, EA algorithms, undocumented network protocols or suspicious dependencies in TradingWorkspace when reverse engineering or a security audit is requested. Not for ordinary source review, API integration or UI debugging.
---

# Reverse engineering and security investigation

Start from the requested target and question: binary/EA logic, undocumented
protocol, or suspicious code/dependency. Identify ownership/authorization and
the smallest read-only evidence needed. Normal engineering review does not
require activating the reverse toolkit.

## Reuse the toolkit without inheriting its case permissions

Read `tooling/reverse-skill/AGENTS.md` and `RULES.md` before using that package.
Use its existing references selectively:

- Binary/EA: `skills/ida-reverse/`, `skills/radare2/`, `skills/reverse-engineering/`.
- Undocumented JS/protocol: `skills/js-reverse/`, `skills/browser-automation/`.
- Suspicious code: `skills/malware-analysis/`, `skills/supply-chain-security/`.

Resolve these from `tooling/reverse-skill/`, checking paths exist. Reading
checklists/source is not permission to run the package. Its router writes files:
before any package script, disclose the exact command and its file/network/service
effects, then follow the package's explicit-approval gate. Existing session
authorization counts only when it covers those effects and the current target.

`work/mk-open` and any older granted scope belong to that case; they are never
blanket authorization. Do not alter scope flags to bypass the guard, launch the
full toolkit by default, or change global MCP/client/AV settings as a side effect.

## Findings and integration

Separate observed behavior, inferred algorithm and unknowns. Keep sample hashes,
reproduction steps and limitations with the existing task evidence owner.
Recovered pseudocode/design is a candidate for reuse, not verified trading logic.
Validate it against authorized fixtures before integrating. External/broker
effects and licenses retain their own gates.
