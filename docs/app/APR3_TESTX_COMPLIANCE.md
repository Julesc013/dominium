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
