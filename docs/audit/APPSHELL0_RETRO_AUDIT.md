Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# APPSHELL-0 Retro Audit

## Scope

Audit target:

- product entrypoints and wrappers
- argument parsing behavior
- descriptor/version surfaces
- pack verification hooks
- shell-related shared-code candidates

## Findings

### 1. Product startup is fragmented

Current product startup is split across:

- `tools/mvp/runtime_entry.py`
- `src/server/server_main.py`
- `tools/setup/setup_cli.py`
- `tools/launcher/launch.py`
- `dist/bin/*` wrapper scripts

This creates duplicated handling for:

- `--descriptor`
- product boot messages
- descriptor file emission
- wrapper-level refusal paths

### 2. Product wrappers already define the stable executable surface

`dist/bin/` already provides the portable product names:

- `engine`
- `game`
- `client`
- `dominium_client`
- `server`
- `dominium_server`
- `setup`
- `launcher`
- `tool_attach_console_stub`

This is the correct adoption seam for AppShell bootstrap behavior because it is the
user-visible executable surface for portable/source-distribution use.

### 3. CAP-NEG and PACK-COMPAT primitives already exist

Existing shared runtime-compatible surfaces:

- CAP-NEG descriptor emission via `src.compat`
- offline pack verification via `src.packs.compat`
- server/local orchestration via SERVER-MVP-0/1 runtime code

This means APPSHELL-0 can be implemented as a shared shell bootstrap that calls
existing adapters instead of rewriting product logic.

### 4. No `src/appshell/` package existed

Before APPSHELL-0 there was no shared shell library under `src/`.

Consequence:

- no unified root command registry
- no shared mode normalization
- no shared deterministic console/logging surface
- no single product-shell lifecycle implementation

### 5. Current product CLIs are inconsistent

Examples observed during audit:

- `src/server/server_main.py` directly owns descriptor handling and command parsing
- `tools/setup/setup_cli.py` owns a large custom CLI with no common shell layer
- `tools/launcher/launch.py` duplicates descriptor handling
- `tools/mvp/runtime_entry.py` uses `--ui` instead of a product-shell `--mode`

APPSHELL-0 therefore needs a compatibility wrapper that:

- owns common shell flags
- translates shell mode into legacy product arguments where needed
- delegates to existing product handlers without semantic change

### 6. Runtime-independence risk is in adapters, not in shell mechanics

The deterministic shell mechanics themselves can live under `src/appshell/` with
standard-library-only behavior. Existing descriptor and pack verification code may
still reach older compat/pack modules, but the shell core can remain free of
direct `tools.xstack` imports.

## Shared-Code Candidates

The following shared surfaces are justified:

- `args_parser`
- `command_registry`
- `mode_dispatcher`
- `logging_sink`
- `console_repl`
- `config_loader`
- `compat_adapter`
- `pack_verifier_adapter`
- `tui_stub`
- `rendered_stub`

## Adoption Plan

Minimal-risk APPSHELL-0 adoption path:

1. Add `src/appshell/` shared bootstrap and common command surface.
2. Route product entrypoints through `appshell_main(...)`.
3. Keep product-specific handlers intact as delegated legacy runners.
4. Replace wrapper-level descriptor special cases with AppShell bootstrap usage.

## Risks

- Regressing existing product CLI flags if common-arg stripping is not careful.
- Accidentally changing client/server runtime behavior if shell mode translation is
  not isolated from authoritative logic.
- Reintroducing repo/XStack coupling into the shell core if adapters import dev-only
  code directly.

## Audit Conclusion

APPSHELL-0 can be implemented safely as a thin shared shell bootstrap layered over
existing product handlers. No canon conflict was found, and no existing product
surface requires semantic change to adopt a common shell lifecycle.
