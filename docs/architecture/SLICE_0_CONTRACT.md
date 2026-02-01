Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# SLICE-0 Contract





Purpose: deliver the product shell MVP. This is a runnable, shippable shell


that proves declarative world creation, lawful navigation, and save/load/replay


work with zero packs and zero hardcoded world assumptions.





Scope (binding for SLICE-0):


- client/, launcher/, tools/, docs/architecture/, docs/ui/, tests/


- Documentation and tests may be added/updated; engine/game simulation is untouched.





Non-goals (binding for SLICE-0):


- No new simulation behavior.


- No new schemas or schema reinterpretation.


- No hardcoded world topology, bodies, or spawn locations.


- No privileged templates; built-in and pack templates are peers.





Required behaviors:


1) Boot with zero packs installed.


2) Loading screen shows, at minimum:


   - engine version, game version, build number


   - protocol/schema versions


   - determinism status


   - pack discovery summary


   - template registry status


3) Main menu options:


   - New World, Load World, Inspect Replay, Tools, Settings, Exit


   - CLI/TUI/GUI parity with identical refusal semantics.


4) World creation:


   - Templates enumerated from registry (includes built-ins).


   - Parameter editing limited to template-declared parameters.


   - Policy layer selection (movement/authority/mode/debug).


   - Generates a WorldDefinition and writes it into a save file.


5) Navigation:


   - Spawn is defined only by WorldDefinition.


   - Navigation modes are policy-layered and law-governed.


   - Mode changes emit events and are replayable.


6) HUD/Console/Debug:


   - HUD is minimal: world id, topology node, frame/position, policy layers, tick.


   - Console is unified; CLI is canonical; GUI/TUI are shells over the same commands.


   - Debug overlay is read-only by default; mutations require lawful policy.


7) Save/Load/Replay:


   - Saves embed full WorldDefinition.


   - Unknown fields are preserved on round-trip.


   - Replay inspection works without packs.


   - Missing capabilities yield explicit refusal or degraded modes.





Replaceability rules:


- All shell behavior is state-machine driven.


- All content assumptions are routed through WorldDefinition, template registry,


  and policy/law/capability systems.


- UI is non-authoritative and text/vector-only.





SLICE-0 completion is defined by the acceptance checklist in


`docs/roadmap/SLICE_0_ACCEPTANCE.md`.
