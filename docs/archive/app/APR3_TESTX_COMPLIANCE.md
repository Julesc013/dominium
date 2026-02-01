Status: HISTORICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: docs/architecture/CANON_INDEX.md

This document is archived.
Reason: Superseded by docs/architecture/CANON_INDEX.md.
Do not use for implementation.

This document is archived.
Reason: Superseded by docs/architecture/CANON_INDEX.md.
Do not use for implementation.

This document is archived.
Reason: Superseded by unknown.
Do not use for implementation.

# ARCHIVED: APR3 TESTX Compliance

Archived: point-in-time compliance snapshot.
Reason: APR compliance snapshot; current enforcement supersedes it.
Superseded by:
- `docs/app/TESTX_COMPLIANCE.md`
- `docs/ci/CI_ENFORCEMENT_MATRIX.md`
Still useful: background on TESTX coverage in APR3.

# APR3 TESTX Compliance

TESTX remains CLI-only. No GUI/TUI paths are used by tests.

## Tests
- `tests/app/app_cli_contracts.py`
  - `--help`, `--version`, `--build-info`
  - `--smoke` / `--deterministic --smoke`
  - `--ui=none --smoke` for all products
  - GUI stubs for non-client products return non-zero with a clear error

## Run
```
ctest -R app_cli_contracts
```

## Invariants covered
- CLI-only behavior remains deterministic.
- Explicit UI mode selection never silently falls back.
- GUI remains optional and does not affect CLI smoke paths.