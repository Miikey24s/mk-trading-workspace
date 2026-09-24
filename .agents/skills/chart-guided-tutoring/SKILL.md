---
name: chart-guided-tutoring
description: Teach candle patterns and zones through annotated platform charts or clearly hypothetical candlestick diagrams. Use for candle-reading lessons, chart-location confusion and replay walkthroughs; not trade execution, arithmetic-only lessons or standalone predictions.
---

# Chart-guided tutoring

Make the concept identifiable on a visible candlestick chart before asking the learner to reason about it. This skill owns visual teaching and chart-state continuity; the course tutor protocol owns assessment and financial boundaries.

Read [browser mechanics](references/browser-mechanics.md) before browser operations. For research rationale, capability decisions and validation limits, read [the project research note](../../../education/research/chart-guided-tutoring.md) only when reviewing or changing this workflow.

## Visual-first course default — learner request 2026-09-12

- For candle, zone, breakout/retest and entry/SL-location explanations or exercises, include or reuse a clearly visible, relevant candlestick illustration in the reply. Do not substitute an OHLC table, numeric inequalities or prose-only directions for the picture. Short confirmations need not redraw an unchanged picture.
- Use ordinary trading-platform candle geometry: chronological bars, consistent price scale, visible High/Low and Open/Close endpoints, rising/falling distinction. Anchor labels and arrows to the precise feature; label the zone boundaries. Keep numbers secondary, showing only values needed to distinguish close cases or execute safely. A flowchart can supplement, not replace, the candle picture when price location is the question.
- Existing chart discussion: preserve its actual candles and follow sections 1–4. Concept-only or synthetic exercise: use the available visualize skill to draw a deterministic, clearly labelled hypothetical candle diagram; no account or browser connection needed. Do not fabricate a broker screenshot, price history or future winning candles. Read visualize instructions before authoring its output.
- For a worked example, annotate the decisive feature and explain briefly. For an unattempted exercise, label candles/zone but do not mark the correct answer. Keep the learner's decision as the one question; no repeated OHLC arithmetic unless that is the requested objective.
- Reuse the current example before inventing another. Check geometry against supplied values, legibility and label overlap; distinguish source/geometry checks from rendered UI verification. Never claim a visual passed inspection without inspecting it. This presentation preference does not change strategy rules or upgrade mastery.

## 1. Establish one shared chart state (actual chart/replay)

- Read the course's pending activity, learner evidence and latest screenshot before teaching. Identify platform/session, instrument/feed, timeframe, timezone when visible, replay versus live, current replay clock and the referenced candle(s).
- Get a fresh chart screenshot and UI state before drawing. Screenshot pixels, hover OHLC and the last-traded-price label are different evidence: crosshair OHLC can describe an older candle. Verify which candle the numbers belong to before quoting them.
- If the chart has advanced since the learner's image, explicitly separate the old referenced object from the new candle. Keep stable labels such as A/B plus date/time when verified; do not silently move "new peak" to the newest bar.
- Keep replay paused for explanation. Never rewind to conceal already-seen outcomes. For a fair new decision, use the current known-data boundary or a genuinely unexposed sample.
- If the learner controls the chart while drawing, refresh the view and relocate anchors. Do not apply screenshot coordinates from before zoom, pane resize, fullscreen change or pan.

## 2. Explain through anchored marks

- Pick one learning objective, not a complete market analysis. For an unfamiliar term, show one concrete example and its defining feature before a question.
- Use a **Callout/price note** for a particular candle, wick, Close or swing; an **Arrow/path** for a move; a **Rectangle** for a zone. A horizontal zone alone does not identify which historical peak the explanation means.
- Keep labels short and local: identifier + concept + relevant price/time or reason. Point the leader to the exact feature, not merely the nearby body. Mark approximate values with `≈`; do not imply exact OHLC from pixel estimation.
- Distinguish a price region from the candle used to justify it. State why the region was chosen and whether it is discretionary or rule-defined. No unearned support/resistance reliability or trading signal claims.
- Label two compared peaks symmetrically (A, B). If explaining a rebound, show its start and end; a straight arrow denotes overall direction, not an uninterrupted price path.
- Use readable contrast and labels as well as color. Put boxes in nearby empty space, avoiding the studied candles, price axis and replay buttons. Start with a few relevant marks; add another only if it resolves an actual ambiguity.
- Prefer platform-native drawings anchored to price/time. Do not generate or repaint historical price candles to make an explanation clearer. A separate schematic must be explicitly hypothetical and must not masquerade as the user's chart.
- If the existing mark is wrong, correct the geometry transparently. If the mark is valid but the explanation is unclear, improve the label without relocating the zone to fit later outcomes. Record meaningful interpretation changes.

## 3. Verify before handing back

1. Check anchor and price bounds against the fresh chart; use the drawing's Coordinates fields when precision matters.
2. Inspect a screenshot after edits: correct target, readable text, no material overlap, no clipped labels, original data intact. A created object or successful click does not prove a useful picture.
3. Save through the observed UI and verify its saved-state indicator when available. If persistence is unverified, say so; do not reload merely to prove saving when that may lose replay state.
4. Check that the replay clock, original fixed zones and order/account state have not changed unexpectedly. Stop unrelated mutations if state changed; re-establish what happened.
5. Use the visible labels in the explanation. The learner should not need to translate vague "over there" directions into chart coordinates.

## 4. Give a bounded learner action

- Demonstrate the controls once, then give one coherent batch: exact control/location, action count or stop condition, what to observe, what to report. Do not ask for a screenshot after every click when a short batch suffices.
- Distinguish Play from Next candle, chart timeframe from replay step, historical observations from forecasts, and no-trade observation from an order setup.
- Do not promise a useful reaction within an arbitrary three bars. If a zone is far away, explain that no contact is a valid observation; use a bounded observation interval with a no-contact stop, not "keep going until it works".
- When new screenshots already show the requested time advance, do not repeat the same task. Log what is visible and what remains unverified; correct platform use is not independent market-reading mastery.
- Reduce help gradually: tutor labels an example → learner identifies another case → learner explains a choice without pre-labeled answers. Do not turn "I understand" or tutor-drawn annotations into a passed assessment.

## Scope and fallback

Use available scoped browser tools first. Drawing permission does not authorize orders (even demo orders), live accounts, deposits, challenges, paid subscriptions, API keys, global permissions or background monitoring. Preserve user drawings; do not use Remove all, reset layout or delete sessions.

If native chart drawing is unavailable, explain the precise gap and use the supported alternative with the user's source clearly identified. Do not present an edited screenshot as a saved platform drawing. Do not install another MCP solely because UI automation needs a few interactions.

Write minimal evidence and the next checkpoint into the existing course progress, not a new tracker. Report the artifact and its visible meaning first; retain the requested short course-progress footer without a mastery percentage.
