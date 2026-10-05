# UI automation

Automation is allowed to accelerate repeatable work, not to silently redefine product UI.

Target pipeline:

```text
approved system + project contract
  → generate or migrate candidate
  → static/type/lint checks as applicable
  → project tests
  → render fixture screens
  → screenshot/visual diff
  → accessibility and state checks
  → reviewable change set
```

Automation must stop on semantic mismatch, missing data/state contracts, failing tests, or large unexplained visual diffs.
