# P03 Failure Attempt 2

- Canonical task: P03 bounded retry attempt 2 and final attempt
- UTC time: 2026-09-20T23:55:28.7721138Z
- Expected failure: `Get-Content -ErrorAction Stop` on absent `fixtures\work\p03-intentionally-missing.txt`; the file must remain absent.
- Observed error class: `System.Management.Automation.ItemNotFoundException`
- Observed error message: `Cannot find path '.\fixtures\work\p03-intentionally-missing.txt' because it does not exist.`
- Target path: `fixtures\work\p03-intentionally-missing.txt`
- Receipt path: `fixtures\receipts\p03-failure-attempt2.md`
- Missing file exists after attempt: `false`
- Status: `failed_expected`
- Retry note: This was the final allowed retry; no further attempts are permitted.
