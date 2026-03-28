Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/appshell/APPSHELL_CONSTITUTION.md`, `docs/appshell/COMMANDS_AND_REFUSALS.md`, `docs/appshell/LOGGING_AND_TRACING.md`, and `docs/contracts/CAPABILITY_NEGOTIATION_CONSTITUTION.md`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# TUI Framework

## Purpose

APPSHELL-3 defines the shared text user interface framework for Dominium
products.

The framework provides:

- deterministic panel composition
- shared console and log surfaces
- product-specific default layouts
- deterministic fallback when full curses support is unavailable

## Core Concepts

Shared panel ids:

- `panel.menu`
- `panel.console`
- `panel.logs`
- `panel.status`
- `panel.map`
- `panel.inspect`

Shared layouts:

- `layout.default`
- `layout.viewer`
- `layout.server`

Panels are presentational only. They must not mutate truth and must not bypass
lens, law, or epistemic gating.

## Layout Rules

Layout composition is registry-driven through:

- `data/registries/tui_panel_registry.json`
- `data/registries/tui_layout_registry.json`

Panel render order is deterministic:

1. sort by layout `order`
2. tie-break by `panel_id`

panel focus is deterministic:

1. use the explicit active panel if valid
2. otherwise use the product default focus panel
3. otherwise use the first rendered panel

## Keybindings

Stable APPSHELL-3 keybindings:

- `F1` help
- `F2` menu focus
- `Tab` cycle panels
- `Ctrl+L` logs focus
- `Ctrl+C` console focus
- `Ctrl+S` status focus
- `Ctrl+M` map focus
- `Ctrl+I` inspect focus
- `:` command prompt

These bindings are part of the AppShell UX contract and must remain stable unless
the AppShell command contract version changes.

## Multiplexed Console Sessions

Console sessions are logical AppShell sessions, not operating-system terminals.

The TUI must support:

- multiple logical sessions
- deterministic tab ordering by `session_id`
- deterministic session history ordering

Attach/detach of remote or external sessions is deferred to a later IPC phase,
but the APPSHELL-3 TUI must already model sessions as attachable logical tabs.

## Panel Semantics

### Console panel

- runs AppShell commands through the registered command engine
- does not bypass command refusal handling
- records deterministic command history per logical session

### Menu panel

- renders the shared `ui/ui_model.py` state machine
- shows validated instance/save/profile selections and command actions
- emits only AppShell command invocations or selection events

### Logs panel

- tails the structured AppShell log ring
- sorts by deterministic `event_id`
- may filter by category without altering log order

### Status panel

- shows descriptor/build/layout/backend status
- shows pack/compat/session summary only from derived shell/runtime metadata

### Map panel

- uses derived GEO projection view artifacts only
- must not read TruthModel directly
- is optional per product and capability set

### Inspect panel

- uses derived inspection/scanner/provenance artifacts only
- must not read TruthModel directly
- is optional per product and capability set

## Backend Selection And Fallback

Preferred backend:

- curses / ncurses when available and attached to a TTY

Fallback backend:

- deterministic TUI-lite surface rendered through CLI presentation

Fallback behavior is mandatory when curses is unavailable or not attachable.

When fallback occurs:

- `cap.ui.tui` is treated as disabled for the local presentation attempt
- `cap.ui.cli` is treated as the substitute presentation capability
- degradation is logged and surfaced through compat status / explain keys

No silent degradation is allowed.

## Determinism Rules

- panel registry and layout registry are the only authority for panel ordering
- render ordering must not depend on wall-clock timing
- refresh is event-driven or fixed-iteration driven, never wall-clock paced
- serialization of TUI snapshots must sort keys deterministically
- map and inspect panels must consume derived view artifacts only

## Product Defaults

Default layout binding:

- engine -> `layout.default`
- game -> `layout.default`
- server -> `layout.server`
- setup -> `layout.default`
- launcher -> `layout.default`
- client -> `layout.viewer`

Users may override layout selection with `--tui-layout <layout_id>`.

## Non-Goals

APPSHELL-3 does not:

- add OS-native widget GUIs
- change simulation semantics
- expose direct truth access to shell panels
- add IPC attach/detach transport beyond the logical tab model
