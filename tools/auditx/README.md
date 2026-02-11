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
- `PROMOTION_CANDIDATES.json` (`CANONICAL`)
- `TRENDS.json` (`CANONICAL`)
- `RUN_META.json` (`RUN_META`)
- `FINDINGS.md` (`DERIVED_VIEW`)
- `SUMMARY.md` (`DERIVED_VIEW`)

Canonical artifacts are hash-stable and exclude run metadata fields (timestamps/scan IDs/host IDs).
Run metadata is isolated in `RUN_META.json`.

## Incremental Engine

- Cache root: `tools/auditx/cache/<WS_ID>/`
- Cache key inputs:
  - git `HEAD` hash (or `nogit`)
  - registry hash
  - analyzer version hash
  - config hash
  - content hash
- Full cache hit: reuse cached canonical findings payload.
- Partial changes: recompute only affected analyzers using watch-prefix routing.

## Self-Contained Execution

- AuditX canonicalizes environment internally using `scripts/dev/env_tools_lib.py`.
- Works from arbitrary CWD.
- Works with empty caller `PATH` for non-git scans.

`enforce` is reserved and currently returns `refuse.not_enabled`.
