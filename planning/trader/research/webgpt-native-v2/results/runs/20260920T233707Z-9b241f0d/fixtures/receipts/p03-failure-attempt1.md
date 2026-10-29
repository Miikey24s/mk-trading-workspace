# P03 Failure Attempt 1

- Canonical task: P03 failure lane attempt 1
- UTC time: 2026-09-20T23:51:34.7808576Z
- Expected failure: `Get-Content -ErrorAction Stop` on `fixtures\work\p03-intentionally-missing.txt`; the file must remain absent.
- Observed error class: `System.Management.Automation.ItemNotFoundException`
- Observed error message: `Cannot find path '.\fixtures\work\p03-intentionally-missing.txt' because it does not exist.`
- Tools: PowerShell `Get-Content`, `Get-Date`, `Test-Path`; Codex apply_patch
- Target path: `fixtures\work\p03-intentionally-missing.txt`
- Receipt path: `fixtures\receipts\p03-failure-attempt1.md`
- Missing file exists after attempt: `false`
- Status: `failed_expected`
