Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# GUI Baseline (Zero-Asset)





The baseline GUI is the default, fully functional mode. It MUST operate with


zero content packs and zero external assets. This baseline is authoritative for


UI behavior and parity.





## Canonical constraints


- CLI, TUI, and GUI are three presentations of the same interface contract.


- The CLI defines commands, flags, and error semantics. TUI and GUI are thin


  shells over CLI-equivalent calls.


- UI is non-authoritative and read-only. It MAY request snapshots, subscribe to


  event streams, and submit intent requests only.


- UI MUST NOT mutate simulation state, bypass authority checks, or infer hidden


  truth.





## Zero-asset requirement


The baseline GUI may use ONLY:


- Vector primitives (rectangles, lines, circles).


- Solid colors (hardcoded constants).


- Text rendered via a built-in vector font or system default font.


- Layout rules.





No textures, images, external fonts, themes, or content packs are permitted.





## Required screens (state machines)


- Loading / splash: engine version, game version, build number, schema/protocol


  versions, TESTX status, pack discovery status, deterministic seed state.


- Title / main menu: Start, Load Save, Inspect Replay, Tools, Settings, Exit.


- Settings: renderer selection, UI scale, palette, input bindings, logging


  verbosity, determinism/debug flags (if exposed).





## Renderer integration


- GUI MUST operate with the Null renderer and Software renderer.


- Renderer selection is capability-driven, explicit, and logged.


- Rendering MUST NOT affect simulation timing or determinism.





## Playable Slice 1 UI support


Baseline UI must support (text + vector only):


- Topology tree view (universe -> body -> patch).


- Patch field summaries (bearing, moisture, slope).


- Agent panel (goals, current plan, beliefs).


- Event log (tick-indexed).


- Intent submission: survey here, extract here, fabricate, build, connect network.


- Failure explanations sourced from events.





## TestX requirements


UI TestX MUST cover:


- Zero-pack GUI boot.


- GUI navigation with Null renderer.


- CLI <-> GUI parity (same command -> same events).


- UI cannot mutate state.


- Headless GUI execution in CI.


- Renderer swap does not affect behavior.





## References


- docs/ui/UI_PHILOSOPHY.md


- docs/ui/CLI_TUI_GUI_PARITY.md


- docs/ui/ZERO_ASSET_GUI.md


- docs/ui/UI_FORBIDDEN_BEHAVIORS.md


- docs/tools/TOOL_UI_GUIDELINES.md


- docs/architecture/INVARIANTS.md
