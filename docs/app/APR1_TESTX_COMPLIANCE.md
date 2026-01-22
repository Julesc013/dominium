# APR1 TESTX Compliance

APR1 keeps all tests CLI-only and avoids GUI/TUI dependencies.

## Tests and coverage
- `tests/app/app_cli_contracts.py`
  - `--help`, `--version`, `--build-info` for all products
  - `--smoke` for all products
  - explicit `--deterministic --smoke` for all products
  - `--interactive --smoke` rejected with clear error text
  - explicit renderer request fails loudly when unavailable
  - launcher capability probe output
  - setup `prepare` creates expected directories

## How to run
- `ctest -R app_cli_contracts -V`

## Invariants enforced
- Deterministic CLI smoke paths remain stable.
- Explicit renderer selection fails without silent fallback.
- Timing mode flags are parsed and validated in CLI-only mode.

## Out of scope (manual verification)
- TUI rendering and input behavior (`--tui` modes).
- Signal handling behavior (Ctrl+C/console close).
- Windowed loop performance and occlusion throttling.
