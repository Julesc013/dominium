Status: DERIVED
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Entrypoint Unify Final

## Before

```text
product main -> appshell_main -> legacy_main fallback -> product-local validation/startup
runtime multiplexer -> direct _legacy_main bypass (client/server script path)
```

## After

```text
product main -> appshell_main -> bootstrap context -> appshell_product_bootstrap -> product-local runtime logic
AppShell owns mode resolution, negotiation preflight, legacy flag migration, logging, and IPC endpoint startup.
```

## Unified Products

- `7` governed product surfaces are compliant.
- `client` via `tools/mvp/runtime_entry.py`
- `engine` via `tools/appshell/product_stub_cli.py`
- `game` via `tools/appshell/product_stub_cli.py`
- `launcher` via `tools/launcher/launch.py`
- `server` via `src/server/server_main.py`
- `setup` via `tools/setup/setup_cli.py`
- `tool.attach_console_stub` via `tools/appshell/product_stub_cli.py`

## Deprecated Flags

- `client` `--ui gui|cli` -> `--mode rendered|cli`
- `server` `--ui headless|cli` -> `--mode headless|cli`

## Validation Unification Readiness

- Product mains no longer delegate through `legacy_main=` directly.
- Launcher and setup pack verification flow through `src.appshell.pack_verifier_adapter.verify_pack_root`.
- Runtime multiplexer dispatch now re-enters AppShell for `client` and `server` instead of bypassing it.
- AppShell now emits bootstrap context and only starts IPC after negotiation preflight context construction.
