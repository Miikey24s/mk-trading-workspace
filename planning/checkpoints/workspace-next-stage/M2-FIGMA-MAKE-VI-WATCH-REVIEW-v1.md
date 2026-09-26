# M2 Figma Make packet — VI Dubber Watch/Review v1

Status: **READY FOR MANUAL MAKE RUN / BLOCKED-MAKE until the user runs it**.

This packet freezes one representative M2 slice from the current VI Dubber UI. It is a design candidate exercise only. It does not change backend/API behavior, accept the VI visual lock, or satisfy M2 until the Make artifact can be reviewed and integrated back into runnable code.

## Frozen source

- Repository: `D:\ANNAM\TradingWorkspace\projects\vi-dubber`
- Source commit: `94d984c00fce5c1692e3f584f18abb7e3c3e7e07`
- Stack: React `18.3.1`, TypeScript `5.7.3`, Vite `6.1.0`, Tailwind CSS `3.4.17`, Lucide React `0.475.0`.
- Representative slice: current Watch + progressive preview rail + bilingual Review workspace, with a future return-to-Library affordance represented only as navigation intent. Do not invent a Library backend or persistence layer in this Make run.

### Allowed attachments

Attach only these text/code files. Do not attach media, work artifacts, credentials, config files, account data, logs, or the whole repository.

| File | SHA-256 |
|---|---|
| `frontend/src/App.tsx` | `e5a96a56edd4baf60cef1c7b2d222484497c933bf385cfbc09993b56088bc2d1` |
| `frontend/src/components/header/Header.tsx` | `48b0a6ddd43d4b411d7727987ba771766e6a3d79f6ecdfc5988b0926192edfc8` |
| `frontend/src/components/monitor/VideoPlayer.tsx` | `ec0b6b344665608c4d3420435a9bf74c94a5b601edc8adcdb9aa2497f9db385a` |
| `frontend/src/components/monitor/LongformPreviewRail.tsx` | `096799bc7e8e10f9c38525125563a35fa636fe35ecacd8927134a2bc08fe54ef` |
| `frontend/src/components/review/SegmentReviewer.tsx` | `ee7909ba79652031f9d791cb9298d3c70d3ce83dc07ae18fd63907a57db2fd1f` |
| `frontend/src/types/index.ts` | `38d56f99d2c374c370623283eb85584d0fe2ef481af8115f458bf453ffc72fa6` |
| `frontend/PRODUCT-UI-CONTRACT.md` | `d22ce930b3c60a16530b1ebb159adc47b574f4be26a973e5080ac3d6f887366e` |
| `frontend/package.json` | `b2bf1937eac7d1ca1410174ae0f2c26ca62a0a54736fa66ae995b834bd716851` |

If any listed hash changes before Make is run, this packet is stale and must be versioned again before using its output for M2 evidence.

## Model, mode and budget

- Preferred first candidate: **Opus 4.8 + Build** if that exact option is available in the user's current Make account.
- If unavailable, use the strongest current **Build** option exposed by the account and record the exact model name shown by Make with the returned artifact.
- This packet authorizes one initial candidate only. It does not authorize buying credits, upgrading an account, public publishing, or uploading anything outside the allowlist above.
- Do not run a comparison candidate unless the first result reveals a concrete design gap that warrants one.

## Copy-paste prompt for Make

Paste the following block unchanged after attaching the allowlisted files:

```text
Refine the attached VI Dubber Watch/Review screen into a production-quality daily-use workspace while preserving the existing React 18 + TypeScript + Vite + Tailwind stack and the existing product behavior.

Product context:
- VI Dubber turns a source video into Vietnamese dubbing and lets the user watch progressive previews, review bilingual segments, edit a segment, selectively rerender invalidated output, and download valid artifacts.
- This iteration covers one representative Watch/Review slice. A future Library exists only as navigation intent. Do not invent a database, API, media catalog, bookmark service, router framework, or fake backend.
- The attached PRODUCT-UI-CONTRACT.md is authoritative for media/rendition identity, time, preview readiness/staleness, navigation state, and invalidation semantics.

Keep these functional semantics exactly:
- ready preview: can play/download and shows its exact chunk/time context;
- queued/processing: cannot be presented as final media;
- stale preview: cannot play/download as current output and must explain that an edit invalidated it;
- blocked preview: cannot play/download and must show a QA/block reason or next action;
- missing/unknown data: never invent duration, readiness, file path, or successful state;
- Watch -> Review -> Watch must preserve the same media/rendition and source-media time conceptually;
- editing a segment invalidates only dependent lineage; unaffected ready chunks stay usable;
- final/download controls only advertise artifacts valid for the selected revision;
- preserve existing keyboard/focus behavior and bilingual review ergonomics.

Design goals:
- Make the screen easier to understand at a glance for someone using it for hours: clear hierarchy between media playback, progressive preview state, and segment review.
- Use flat-first composition. Prefer spacing, typography, alignment and state emphasis before adding cards, borders, backgrounds or shadows. Remove unnecessary nested surfaces.
- Keep high information density without feeling like a developer dashboard. Engineering telemetry should remain secondary to Watch/Review work.
- Make READY / PROCESSING / STALE / BLOCKED visually and textually distinct. Color alone is insufficient.
- Preserve strong visible keyboard focus, disabled states, loading/error/empty states, and readable contrast in both light and dark themes.
- Vietnamese copy should be natural and concise; keep established technical terms where useful.
- Support desktop 1440px, compact 768px, and a narrow approximately 390px layout without hiding the core Watch/Review workflow.

Technical constraints:
- Reuse the attached components and state shape. Do not add a UI framework, component library, router, data store, backend endpoint, dependency, or package.
- Keep React 18. Do not upgrade React, Vite, Tailwind or TypeScript.
- Keep Lucide icons where icons are useful.
- Do not replace real media/state behavior with mock success states, fake duration, simulated progress, or static screenshots.
- Do not weaken stale/blocked preview safeguards.
- Do not introduce cloud, account, OAuth, sharing, analytics, broker/trading, or unrelated product concepts.

Please produce:
1. one coherent refined Watch/Review screen direction using the supplied files as the source;
2. runnable/exportable code for the affected UI slice, keeping edits as localized as practical;
3. a brief change summary grouped by hierarchy/layout, preview-state clarity, review ergonomics, responsive behavior, and accessibility;
4. note any place where you could not preserve an existing behavior from the source instead of silently replacing it.

Do not treat visual polish as acceptance. The returned code will be reviewed against the source commit, state contract, and runtime tests before integration.
```

## Manual Make steps

1. Open Figma Make in the account you want to use for this experiment.
2. Start a new Make task/project for this VI Dubber slice. Select **Opus 4.8 + Build** if it is actually available; otherwise use the current Build model shown by your account and note its exact name.
3. Attach exactly the eight files in the allowlist above. Do not attach source video/audio, `config.yaml`, `.env`, work/benchmark folders, logs, credentials, or the full repository.
4. Paste the full prompt block above and run one candidate.
5. Return either a Make link that this Codex task can access, or the exported code/archive/file path from Make. A screenshot can accompany the result for visual review but does not replace the code/resource artifact.

Do not make the result public just to share it back. If Make asks for a paid upgrade or extra credits, stop at that point; this packet does not authorize a purchase.

## Evidence expected back

M2 can proceed only after the return artifact records:

- the actual Make model/mode used;
- source commit `94d984c00fce5c1692e3f584f18abb7e3c3e7e07` and this packet version;
- accessible Make artifact/link or exported code;
- selected diff against the frozen source;
- runnable UI verification after root review;
- responsive/state/a11y evidence for the integrated slice.

Until then, M2 is `BLOCKED-MAKE`. The source files listed above should remain frozen for this packet; if they must change for unrelated work, create packet v2 before reviewing a later Make output against them.
