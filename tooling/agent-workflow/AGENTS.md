# Agent workflow tooling

Read POLICY.md for the shared execution/review policy. This is a staged CLI runner, not the trading product. Keep changes scoped here; never launch a broker or edit provider credentials.

Run local harness tests with `python -B -m unittest discover -s tooling/agent-workflow/tests -v` from TradingWorkspace. Paid/model smoke calls are separate from local tests; do not run them automatically on every edit.

Do not auto-start work on session load. CLI roles are requested explicitly; startup does not grant permission to launch workers, deploy, merge or change global configuration. Read README.md before changing runner behavior.
