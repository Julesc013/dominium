# AuditX

AuditX is the semantic audit pipeline for Dominium.

## Commands

- `python tools/auditx/auditx.py scan --repo-root .`
- `python tools/auditx/auditx.py scan --repo-root . --changed-only`
- `python tools/auditx/auditx.py verify --repo-root .`
- `python tools/auditx/auditx.py enforce --repo-root .`

## Outputs

Running `scan` writes deterministic artifacts to `docs/audit/auditx/`:

- `FINDINGS.json` (`CANONICAL`)
- `INVARIANT_MAP.json` (`CANONICAL`)
- `RUN_META.json` (`RUN_META`)
- `FINDINGS.md` (`DERIVED_VIEW`)
- `SUMMARY.md` (`DERIVED_VIEW`)

`enforce` is reserved and currently returns `refuse.not_enabled`.
