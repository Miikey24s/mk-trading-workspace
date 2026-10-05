# Visual QA

Every production UI migration should define stable fixtures and render targets.

Minimum checks for dense desktop applications:

- primary desktop viewport and at least one constrained width;
- supported light/dark themes;
- default and compact density when both exist;
- long Vietnamese labels and numeric precision;
- loading, empty, partial, stale, error, unavailable/permission states;
- keyboard focus and visible selected state;
- chart/table overflow and no incoherent overlap;
- screenshot diff against an approved baseline.

Large diffs require review even when tests pass.
