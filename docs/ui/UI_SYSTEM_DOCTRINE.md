Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# UI System Doctrine

The UI is a deterministic projection of state and commands.

## Core Rules

- UI code does not mutate authoritative state.
- CLI is canonical; TUI and GUI render the same command graph.
- Layout, panel composition, and bindings are data.
- UI packs may extend presentation only through validated schemas.
- Refusal paths and capability checks are explicit and deterministic.

## Data Boundaries

- UI reads snapshots, capability views, and command metadata.
- UI does not read privileged authority internals directly.
- UI does not bypass command dispatch for behavior.

## Modularity

- Layouts are declarative and loadable per product profile.
- Panels are composable and may be added/removed by packs.
- Themes are presentation-only and cannot alter command behavior.

## Safety

- Invalid UI data must refuse with explicit codes.
- Unknown fields are preserved in open maps where declared.
- Missing optional UI fragments degrade to deterministic fallback views.

