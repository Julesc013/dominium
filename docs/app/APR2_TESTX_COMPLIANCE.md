# APR2 TESTX Compliance

## Covered tests
- `app_cli_contracts` (ctest): validates `--help`, `--version`, `--build-info`,
  and `--smoke` for client/server/launcher/setup/tools.
- `app_cli_contracts` also checks:
  - explicit renderer failure (`client --renderer=missing --smoke`)
  - launcher capability output tokens (`platform_backend=`, `renderer_auto=`,
    `renderer=`, `platform_ext_dpi=`, `platform_ext_window_mode=`)

## How to run
- `ctest -R app_cli_contracts`
- `ctest` (full suite)

## APR2 invariants enforced
- CLI-only tests: no GUI/TUI dependencies.
- Deterministic smoke paths remain wall-clock independent.
- Explicit renderer selection fails loudly when unavailable.
- Capability output exposes DPI/window-mode extension availability.

## Out of scope
- GUI/TUI behavior is not validated by tests.
- Multi-window UX and GPU backends are not exercised in TESTX.
