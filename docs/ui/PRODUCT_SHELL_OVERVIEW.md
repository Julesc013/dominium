# Product Shell Overview

This document describes the SLICE-0 product shell UI across CLI/TUI/GUI.
All modes are state machines and share the same commands and refusal semantics.
UI is non-authoritative: it requests intent and displays results.

Screens (conceptual, not hardcoded content):
1) Loading
   - Shows build/protocol/schema versions, determinism, pack discovery, template registry.
   - Zero assets; text/vector only.
2) Main Menu
   - New World, Load World, Inspect Replay, Tools, Settings, Exit.
3) World Creation
   - Template selection from registry.
   - Parameter editing (seed, policy layers).
   - Generates a WorldDefinition and writes a save.
4) World View
   - Minimal HUD: world id, topology node, frame/position, active policies, tick.
   - Navigation via policy-governed modes and lawful intent.
5) Replay Inspection
   - Read-only; shows event tail and summary metadata.
6) Tools
   - Headless-safe inspectors (world/snapshot/replay/template/pack).
7) Settings
   - Renderer selection, UI scale, palette/theme, logging verbosity, input bindings.

Parity rules:
- CLI is canonical.
- TUI and GUI must call the same command paths and surface the same refusal codes.
- No UI may infer missing data or “fix” WorldDefinitions.

Replaceability:
- Templates, policies, and UI descriptors are replaceable by future packs.
- No screen or control assumes a specific world, era, or asset.
