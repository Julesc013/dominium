Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none

# APPSHELL TUI Baseline

## Panel Set

APPSHELL-3 baseline panels:

- `panel.console`
- `panel.logs`
- `panel.status`
- `panel.map`
- `panel.inspect`

All panels are registry-backed and rendered in deterministic layout order.

## Layouts

Baseline layouts:

- `layout.default`: console + logs + status
- `layout.server`: status + logs + console
- `layout.viewer`: map + inspect + logs + console + status

Product defaults:

- engine/game/setup/launcher -> `layout.default`
- server -> `layout.server`
- client -> `layout.viewer`

## Keybindings

Stable baseline bindings:

- `F1`
- `Tab`
- `Ctrl+L`
- `Ctrl+C`
- `Ctrl+S`
- `Ctrl+M`
- `Ctrl+I`
- `:`

## Fallback Behavior

If curses is unavailable or a TTY is not present, APPSHELL-3 falls back to a
deterministic TUI-lite text surface.

Fallback effects:

- compatibility mode surfaces as degraded
- `cap.ui.tui` is locally disabled
- `cap.ui.cli` is treated as the substitute output capability
- fallback is logged with explicit explain keys

## Derived-Only Surfaces

Observer-facing panels remain derived-only:

- logs panel uses the AppShell log ring
- map panel uses `src/client/ui/map_views.py`
- inspect panel uses `src/client/ui/inspect_panels.py`

No APPSHELL-3 panel reads TruthModel directly.

## Readiness

This baseline is sufficient for:

- APPSHELL-4 attach/detach console sessions over IPC
- supervisor-driven console multiplexing
- richer TUI panel actions and selection state
