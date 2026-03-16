Status: CANONICAL
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Version: 1.0.0
Stability: provisional
Future Series: UI/APPSHELL
Replacement Target: release-pinned standalone/native/rendered adapter contract for PLATFORM-FORMALIZE-0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/appshell/UI_MODE_RESOLUTION.md`, `docs/appshell/COMMANDS_AND_REFUSALS.md`, and `docs/release/FROZEN_INVARIANTS_v0_0_0.md`.

# UI Adapter Contract

## Purpose

UI adapters are thin bindings over:

- command descriptors from AppShell
- derived view artifacts
- structured logs and diagnostics
- validated LIB manifests and selections

They do not own business logic, pack loading, negotiation, or truth mutation.

## Inputs

UI adapters may consume:

- command registry rows
- `src/ui/ui_model.py` state
- derived view artifacts from GEO, EARTH, SOL, and related domain view engines
- structured log events
- validated LIB manifest summaries and manifest refs

## Outputs

UI adapters may emit:

- AppShell command invocations with arguments
- selection events such as selected instance/save/object id
- local presentation state

## Forbidden Responsibilities

UI adapters must never:

- perform pack loading or pack verification directly
- perform capability negotiation directly
- call worldgen engines as an authority path
- call truth mutation paths directly
- start simulation or IPC before AppShell bootstrap validation

## Shared Model Rule

- Rendered menu flows and TUI menu flows must share `src/ui/ui_model.py`.
- Native adapters, when present, must bind button/menu actions through the same command and selection surfaces.
- View rendering must consume derived artifacts only.

## Virtual Path Rule

- UI-visible manifest references must remain repo-relative or install-relative virtual refs.
- UI adapters must not persist host-specific absolute paths into governed artifacts.

## Native Adapter Rule

- Native adapters are optional in MVP.
- If a governed native adapter is absent, capability probing must disable it and the product must degrade deterministically through rendered, TUI, or CLI surfaces.
- If a governed native adapter is present, it must remain a thin binding over AppShell commands and shared UI model state.

## Rendered UI Rule

- The rendered client menu surface must bind through `src/ui/ui_model.py`.
- The rendered client session/view surface must consume derived GEO/EARTH/SOL view artifacts only.
- Rendered UI must always preserve a console or IPC attach path for command fallback.
