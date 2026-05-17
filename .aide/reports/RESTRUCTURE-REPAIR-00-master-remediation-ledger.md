# RESTRUCTURE-REPAIR-00 Master Remediation Ledger

Generated: `2026-05-17T19:03:54Z`.

Result: PARTIAL.

## Fixed In Repair Follow-Up

- frozen contract hash evidence refreshed from current frozen surfaces.
- expired locklist overrides retired instead of extended.
- performance replay fixture hashes refreshed from current replay stubs.
- AuditX graph/cache scans now ignore local/generated evidence roots.
- AuditX archive-policy analyzers use existing archive-policy report in static scan mode.
- incomplete tracked AuditX JSON and root inventory noise kept out of the commit.

## Deferred Or Blocked

- 23 excepted former bad roots remain with 1764 tracked files.
- full CTest is not green.
- slice0_hardcoded_ids still fails on current hardcoded domain/source/tool/test identifiers.
- slice1_hardcoded_constants still fails on current atmosphere/gravity/oxygen assumptions.
- tools_auditx still exceeds the 300 second CTest timeout.
- tracked large AIDE file-quality ledger policy remains unresolved.
- prior repair commits 51257dfdb and 0a579e3c remain commit-policy warning history and were not amended.

## Issue Ledger

The machine-readable ledger is `.aide/reports/RESTRUCTURE-REPAIR-00-master-remediation-ledger.json` and contains `59` classified issues. Root exceptions remain deferred rather than force-moved. The repaired frozen-hash, override-policy, and replay-hash issues are marked fixed. AuditX wall-time and hardcoded identifier/constant lint gates remain blocked.
