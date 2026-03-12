Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# APPSHELL-0 Bootstrap Baseline

## Lifecycle Summary

APPSHELL-0 standardizes the outer product shell lifecycle:

1. parse AppShell args
2. resolve product descriptor
3. resolve config and profile inputs
4. run offline compatibility or pack verification when requested
5. dispatch CLI, TUI stub, rendered client mode, or headless mode
6. exit through deterministic refusal and exit-code surfaces

The shared bootstrap lives in `src/appshell/bootstrap.py` and is bound to
`contract.appshell.lifecycle.v1`.

## Products Adopted

The following product-facing surfaces now route through `appshell_main(...)`:

- client via `tools/mvp/runtime_entry.py` and `dist/bin/dominium_client`
- server via `tools/mvp/runtime_entry.py`, `src/server/server_main.py`, and `dist/bin/dominium_server`
- setup via `tools/setup/setup_cli.py` and `dist/bin/setup`
- launcher via `tools/launcher/launch.py` and `dist/bin/launcher`
- engine via `dist/bin/engine` + `tools/appshell/product_stub_cli.py`
- game via `dist/bin/game` + `tools/appshell/product_stub_cli.py`
- tool attach-console stub via `dist/bin/tool_attach_console_stub` + `tools/appshell/product_stub_cli.py`

Alias wrappers `dist/bin/client` and `dist/bin/server` remain thin aliases to the
AppShell-aware product wrappers.

## Shared Surfaces

APPSHELL-0 now provides:

- deterministic root commands: `help`, `version`, `descriptor`, `compat-status`, `profiles`, `packs`, `verify`, `diag`
- mode normalization for `cli`, `tui`, `rendered`, and `headless`
- deterministic TUI and rendered stubs where the real product surface is deferred
- offline pack-verification adapter hooks
- CAP-NEG descriptor/version adapter hooks
- structured exit-code and refusal registries

## Readiness

APPSHELL-0 is the required bootstrap baseline for:

- APPSHELL-1 command/refusal refinement
- APPSHELL-2 structured logging sinks
- APPSHELL-3 TUI panels and console multiplexing
- APPSHELL-4 attach/detach IPC console sessions

Known limitation:

- product-specific legacy command trees still exist behind delegated `_legacy_main(...)`
  surfaces; APPSHELL-0 intentionally standardizes the shared outer shell first and
  leaves deeper subtree normalization to later APPSHELL phases.
