Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# APPSHELL-3 Retro Audit

## Scope

Audit target:

- shared AppShell bootstrap and mode dispatch
- existing console and logging surfaces
- map and inspect artifact availability
- portable TUI constraints across Windows, macOS, and Linux

## Findings

### 1. AppShell already exposes a shared `--mode tui` seam, but it is still a stub

`src/appshell/bootstrap.py` already routes `--mode tui`, but APPSHELL-0 only
returned a stub payload through `src/appshell/tui_stub.py`.

Consequence:

- panel composition is not registry-driven yet
- there is no deterministic panel focus/state model
- no actual TUI backend selection exists

### 2. Structured logs and command dispatch are ready for panel reuse

APPSHELL-1 and APPSHELL-2 already provide the main TUI dependencies:

- registry-backed command dispatch via `src/appshell/commands/command_engine.py`
- deterministic log ring access via `src/appshell/logging/log_engine.py`
- deterministic console-session stub surfaces via `src/appshell/console_repl.py`

This means APPSHELL-3 can build console and log panels without changing product
semantics.

### 3. Derived map and inspect surfaces already exist

Client-facing derived surfaces are already available through:

- `src/client/ui/map_views.py`
- `src/client/ui/inspect_panels.py`

These surfaces already consume derived view artifacts and instrumentation tools,
so the TUI can remain observer-only and avoid direct TruthModel access.

### 4. Windows cannot be assumed to have `curses`

Portable Python environments on Windows may not ship `curses`, and even where it
exists, subprocess-driven shells used in FAST validation are often non-TTY.

Implication:

- AppShell needs a deterministic TUI-lite fallback
- fallback must be explicit and logged
- capability degradation must align with CAP-NEG rather than silently failing

### 5. Product capability declarations lag actual shell support

Before APPSHELL-3, several products could run shared CLI/TUI bootstrap in
practice, but their CAP-NEG defaults and product registries did not consistently
declare `cap.ui.tui` and `cap.ui.cli`.

APPSHELL-3 therefore needs to align descriptor defaults with actual product shell
support so compatibility reports and product descriptors are truthful.

## Audit Conclusion

APPSHELL-3 can be implemented as a shared, registry-driven TUI engine layered on
top of the existing command/logging/view surfaces. The main new work is layout
formalization, deterministic backend fallback, and governance coverage.
