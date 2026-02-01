Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Client Out-Of-Game Scope (P3)

Status: binding for P3. Applies to CLI, TUI, and GUI client shells.

## Purpose

Define the complete, zero-asset, out-of-game experience so the client is usable,
explainable, and deterministic before any in-game content is required.

## Scope (Out-Of-Game)

The client out-of-game UX includes:

- Splash / loading screen.
- Main menu (New World, Load World, Replay, Tools, Settings, Exit).
- World creation flow (built-in templates only).
- Load world selection.
- Replay selection and inspect-only playback.
- Settings (presentation, input, accessibility, debug).
- Inspect / debug access and console (CLI canonical).

## Zero-Asset Rule

The client MUST be fully usable with zero content packs installed.

- The splash and menus render using text/vector fallback only.
- No assets, fonts, or audio are required to reach menus or tools.
- Missing content is explained explicitly; nothing is hidden.

## Determinism and Parity

- CLI is canonical. TUI/GUI invoke CLI intents with identical semantics.
- Outputs and refusal messages are deterministic and consistent across modes.
- UI does not introduce UI-only behavior or hidden side effects.

## Compatibility and Visibility

- The splash must show engine version, game version, build number,
  install_root, instance_root, data_root, pack list, and compat summary.
- Refusals are always visible and explainable.

## Out-Of-Scope (P3)

This scope does NOT include:

- Gameplay mechanics, activities, or progression.
- Content-pack dependent flows.
- Changes to simulation semantics or engine behavior.