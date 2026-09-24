# TradingWorkspace shared UI

This directory contains reusable trading-domain UI contracts. Parent instructions in `D:\ANNAM\TradingWorkspace\AGENTS.md` still apply.

## Scope

- Keep trading semantics here: chart/replay controls, PnL/risk presentation, trading tables, analytical views, order/position/fill display contracts.
- Keep generic controls and visual foundations in `D:\ANNAM\UI-Systems`.
- Keep project-only flows in the owning project repository.

## Safety semantics

Visual styling must never blur these distinctions:

- replay vs demo vs live;
- planned order vs broker-submitted order vs fill;
- unknown/unavailable vs zero;
- gross vs net and currency/unit scope;
- stale/partial data vs current/complete data;
- warning vs failure.

Shared UI must not introduce broker actions or permissions. Backend capability checks remain authoritative.

## Promotion

Promote a project component here only after reuse is demonstrated and its domain contract is stable. Avoid copying a project screen wholesale into shared UI.

## AI generation

AI may generate visual candidates from an approved theme and domain contract, but generated screens are not accepted until semantics, states, data density, and interaction are checked against a real consumer.

