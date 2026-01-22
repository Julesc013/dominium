# TESTX Compliance (APR0)

This document summarizes the CLI-focused TESTX checks added for APR0.

## Tests added
- `app_cli_contracts` (`tests/app/app_cli_contracts.py`):
  - Verifies `--help` and `--version` output for client/server/launcher/setup/tools.
  - Verifies `--build-info` output includes required key/value lines.
  - Runs `--smoke` for each product to ensure deterministic CLI-only exit.
  - Ensures explicit renderer selection fails loudly (`client --renderer=missing --smoke`).
  - Checks `launcher capabilities` output for platform/renderer reporting.
  - Runs `setup prepare` into a temp root and verifies layout dirs.

## How to run
- Full suite: `ctest`
- Targeted: `ctest -R app_cli_contracts`

## Invariants enforced
- Build-info prints product, engine/game, build metadata, protocol, and ABI/API lines.
- Explicit renderer selection fails with non-zero exit code when unavailable.
- CLI smoke paths run without GUI/TUI or content packs.
- Launcher capability probe surfaces platform backend and renderer availability.
- Setup prepare creates a zero-pack directory layout.

## Out of scope (APR0)
- GUI/TUI flows, renderer performance, and asset pipeline validation.
- GPU backend correctness (stubs allowed where documented).
