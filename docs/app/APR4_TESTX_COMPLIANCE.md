# APR4 TESTX Compliance

APR4 adds CLI-only observability tests. No TUI/GUI paths are required or
invoked by tests.

## Tests
- `app_observability`: `tests/app/app_observability_tests.py`
- `app_cli_contracts`: existing CLI contract coverage

## How to run
- `ctest -R app_observability`
- `ctest -R app_cli_contracts`

## Invariants enforced
- CLI-only execution, deterministic output paths
- `client --topology` emits stable text/JSON fields
- `tools inspect` and `tools validate` emit stable text/JSON fields
- Unsupported `--snapshot`, `--events`, and `tools replay` fail loudly
- `--expect-*` mismatch returns non-zero with explicit diagnostics

## Out of scope
- GUI/TUI validation
- Replay/snapshot content validation (not implemented)
