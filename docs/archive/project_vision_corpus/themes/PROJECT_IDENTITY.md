Status: DERIVED
Last Reviewed: 2026-06-03
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

# Project Identity

Status: DERIVED
Last Reviewed: 2026-06-03
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

# Project identity and purpose

This theme gathers 621 source block(s) from 162 source file(s). It is advisory conversation evidence unless the current repo independently supports the same claim.

## What The Sources Suggest

Across the archive, Dominium reads as a layered project rather than a single executable: deterministic substrate, official domain/game layer, product surfaces, tools, and a long-horizon simulation vision.

## Strongest Recurring Signals

- - APP0 scope is application/runtime/platform/render only. - Engine + game remain authoritative. - Applications are orchestrators, not decision-makers. - Rendering never affects simulation. - Client is non-authoritative. - Server is authoritative and headless-capable. - Launcher must not install content or alter simulation state. - Setup owns install/version/integrity responsibilities. - Tools must obey authority/law ...
- 4. "Which decisions in this chat were explicit user decisions versus assistant synthesis?" 5. "Which renderer/platform decisions are final, and which are still provisional?" 6. "Which parts of the robotic seed-civilisation design are hard requirements?"
- The central tradeoff was speed versus purity. Raylib, SDL2, Lua, raygui, rlgl, rlsw, and related libraries can accelerate visible progress, but if they leak into game law, UI documents, saves, replays, or public contracts, they become architectural capture. The chosen compromise is to use them as providers behind Dominium-owned services and conformance tests.
- The immediate game-design plan is to formalize the robotic seed-civilisation doctrine into a spec chapter and choose a first gameplay loop, likely survey -> mine -> refine -> fabricate -> build simple power/logistics/spawn infrastructure.
- The Robot OS and robotic seed-civilisation decisions are the most important design decisions. They are explicit user statements, not merely assistant proposals. They should be formalized as product/game requirements. They affect UI, fog-of-war, spawning, respawn, automation, industry, tutorial/planner design, and MMO anti-cheat.
- 1. User's canon: C89 engine, C++98 game, determinism, per-floor artifacts, no CRT mixing, no silent API creep. 2. Build complexity comes from many machines and historical toolchains. 3. More hand-written presets are not the optimal solution. 4. Build truth should live in tuple contracts. 5. Local machine probes should generate local `CMakeUserPresets.json`. 6. CMake remains build authority. 7. AIDE should probe/expla...
- - This topic matters because it defines the game's construction ambition. The engine must be flexible enough to represent real infrastructure, but the UI must not become a full CAD system. - The rationale is portability and deterministic low-level control. It affects every future implementation prompt. Code generated for the engine must not use C99 features, C++ features, compiler extensions, platform APIs, or undefi...
- - The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The user's question directly made arbitrary placement a major topic. [INFERENCE] The answer was accepted as the current design direction because the user then asked for a Codex prompt plan to implement changes necessary to achieve it. - Finally...

## Decision And Review Shape

- decision: - APP0 scope is application/runtime/platform/render only. - Engine + game remain authoritative. - Applications are orchestrators, not decision-makers. - Rendering never affects simulation. - Client is non-authoritative. - Server is authoritative and headless-capable. - Launcher must not install content or alter simulation state. - Setup owns install/version/...
- decision: 4. "Which decisions in this chat were explicit user decisions versus assistant synthesis?" 5. "Which renderer/platform decisions are final, and which are still provisional?" 6. "Which parts of the robotic seed-civilisation design are hard requirements?"
- decision: The central tradeoff was speed versus purity. Raylib, SDL2, Lua, raygui, rlgl, rlsw, and related libraries can accelerate visible progress, but if they leak into game law, UI documents, saves, replays, or public contracts, they become architectural capture. The chosen compromise is to use them as providers behind Dominium-owned services and conformance tests...
- decision: The immediate game-design plan is to formalize the robotic seed-civilisation doctrine into a spec chapter and choose a first gameplay loop, likely survey -> mine -> refine -> fabricate -> build simple power/logistics/spawn infrastructure.
- decision: The Robot OS and robotic seed-civilisation decisions are the most important design decisions. They are explicit user statements, not merely assistant proposals. They should be formalized as product/game requirements. They affect UI, fog-of-war, spawning, respawn, automation, industry, tutorial/planner design, and MMO anti-cheat.
- decision: 1. User's canon: C89 engine, C++98 game, determinism, per-floor artifacts, no CRT mixing, no silent API creep. 2. Build complexity comes from many machines and historical toolchains. 3. More hand-written presets are not the optimal solution. 4. Build truth should live in tuple contracts. 5. Local machine probes should generate local `CMakeUserPresets.json`. ...
- decision: - This topic matters because it defines the game's construction ambition. The engine must be flexible enough to represent real infrastructure, but the UI must not become a full CAD system. - The rationale is portability and deterministic low-level control. It affects every future implementation prompt. Code generated for the engine must not use C99 features,...
- decision: - The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The user's question directly made arbitrary placement a major topic. [INFERENCE] The answer was accepted as the current design direction because the user then asked for a Codex prompt ...
- decision: This chat was mainly about the **Dominium / Domino project's application and runtime layer**, referred to throughout as **APP0**. The user began by giving a large implementation-oriented prompt titled **"PROMPT APP0 - RUNTIMES, APPLICATIONS, PLATFORMS & RENDERERS."** That prompt defined a strict scope: work on the **client, server, launcher, setup/installer,...
- decision: - The central topic was APP0: the application/runtime/platform/renderer layer of Dominium. This topic came up because the user provided a formal prompt defining what APP0 should do. - The most important conclusion was that APP0 must remain outside the core simulation rules. **FACT:** the user explicitly forbade redesigning simulation rules, altering content ...

## Representative Source Block References

- PVCB-01058: `docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__05_reader_brief.md`
- PVCB-01069: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-01075: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-01076: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-01078: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-01092: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md`
- PVCB-01100: `docs/archive/conversations/_reader/by_chat/advanced_simulation_infrastructure.md`
- PVCB-01102: `docs/archive/conversations/_reader/by_chat/advanced_simulation_infrastructure.md`
- PVCB-01104: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01105: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01106: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01107: `docs/archive/conversations/_reader/by_chat/app_testx_codehygiene.md`
- PVCB-01113: `docs/archive/conversations/_reader/by_chat/architecture_ui_providers.md`
- PVCB-01115: `docs/archive/conversations/_reader/by_chat/architecture_ui_providers.md`
- PVCB-01118: `docs/archive/conversations/_reader/by_chat/canonical_structure_and_framework.md`
- PVCB-01121: `docs/archive/conversations/_reader/by_chat/canonical_structure_and_framework.md`
- PVCB-01122: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- PVCB-01123: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`

## Block Type Counts

- `constraint`: 72
- `contradiction`: 1
- `decision`: 148
- `design_goal`: 82
- `explanation`: 46
- `prerequisite`: 8
- `prohibition`: 2
- `rationale`: 1
- `requirement`: 199
- `risk`: 1
- `roadmap`: 57
- `unresolved_question`: 4

Status: DERIVED
Last Reviewed: 2026-06-03
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

# Domino/Dominium relationship

This theme gathers 672 source block(s) from 174 source file(s). It is advisory conversation evidence unless the current repo independently supports the same claim.

## What The Sources Suggest

The recurring distinction is that Domino supplies reusable deterministic mechanisms while Dominium gives those mechanisms official domain meaning, authored content, and product interpretation.

## Strongest Recurring Signals

- DECISION-01 through DECISION-12 above are the decision set that should carry forward. The strongest accepted formulation is service-first, provider-backed, profile-selected, contract-governed, and third-party-fenced. This decision matters because it reconciles the user's desire to use raylib/SDL/Lua now with the deeper requirement that Dominium remain portable and replaceable. It supersedes vendor-shaped architecture...
- The central tradeoff was speed versus purity. Raylib, SDL2, Lua, raygui, rlgl, rlsw, and related libraries can accelerate visible progress, but if they leak into game law, UI documents, saves, replays, or public contracts, they become architectural capture. The chosen compromise is to use them as providers behind Dominium-owned services and conformance tests.
- Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions.
- - Whether all recommended structural tasks should be implemented now is not established. - Whether the proposed build tuple naming scheme should become official is not yet established. - Whether the current top-level structure is final-final or merely best current target remains subject to user decision and repo evidence.
- This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-floor binaries are mandatory and that support cannot be claimed...
- 1. User's canon: C89 engine, C++98 game, determinism, per-floor artifacts, no CRT mixing, no silent API creep. 2. Build complexity comes from many machines and historical toolchains. 3. More hand-written presets are not the optimal solution. 4. Build truth should live in tuple contracts. 5. Local machine probes should generate local `CMakeUserPresets.json`. 6. CMake remains build authority. 7. AIDE should probe/expla...
- 1. **User confirmation:** identify which recommendations in this chat should become binding Dominium canon. 2. **Repo verification:** check current HEAD, CI status, build presets, CMake configure/build/CTest, layout validators, component matrix validators, and product/projection proof status. 3. **Choose first structural task:** either: - `STRUCTURE-01: Public Surface Registry`, or - `BUILD-CONTRACT-01: Tuple Build C...
- 1. Which recommendations here should become binding canon? 2. Which should remain advisory until more evidence exists? 3. Write the implementation prompt for `STRUCTURE-01: Public Surface Registry`. 4. Write the implementation prompt for `BUILD-CONTRACT-01: Tuple Build Contracts and Machine Probe`. 5. Verify the current repo state and compare it to the older POST-CONVERGE-09 state. 6. Turn the candidate requirements ...

## Decision And Review Shape

- decision: DECISION-01 through DECISION-12 above are the decision set that should carry forward. The strongest accepted formulation is service-first, provider-backed, profile-selected, contract-governed, and third-party-fenced. This decision matters because it reconciles the user's desire to use raylib/SDL/Lua now with the deeper requirement that Dominium remain portab...
- decision: The central tradeoff was speed versus purity. Raylib, SDL2, Lua, raygui, rlgl, rlsw, and related libraries can accelerate visible progress, but if they leak into game law, UI documents, saves, replays, or public contracts, they become architectural capture. The chosen compromise is to use them as providers behind Dominium-owned services and conformance tests...
- decision: Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions.
- decision: - Whether all recommended structural tasks should be implemented now is not established. - Whether the proposed build tuple naming scheme should become official is not yet established. - Whether the current top-level structure is final-final or merely best current target remains subject to user decision and repo evidence.
- decision: This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-flo...
- decision: 1. User's canon: C89 engine, C++98 game, determinism, per-floor artifacts, no CRT mixing, no silent API creep. 2. Build complexity comes from many machines and historical toolchains. 3. More hand-written presets are not the optimal solution. 4. Build truth should live in tuple contracts. 5. Local machine probes should generate local `CMakeUserPresets.json`. ...
- decision: 1. **User confirmation:** identify which recommendations in this chat should become binding Dominium canon. 2. **Repo verification:** check current HEAD, CI status, build presets, CMake configure/build/CTest, layout validators, component matrix validators, and product/projection proof status. 3. **Choose first structural task:** either: - `STRUCTURE-01: Publ...
- decision: 1. Which recommendations here should become binding canon? 2. Which should remain advisory until more evidence exists? 3. Write the implementation prompt for `STRUCTURE-01: Public Surface Registry`. 4. Write the implementation prompt for `BUILD-CONTRACT-01: Tuple Build Contracts and Machine Probe`. 5. Verify the current repo state and compare it to the older...
- decision: **Chat label:** Dominium Build and Future-Proofing Architecture **Date anchor:** 2026-05-27 Australia/Melbourne **Scope:** This report covers the visible conversation and the preservation task that produced the accompanying handoff files. It does **not** claim complete access to any earlier hidden or retired chats. **Epistemic note:** Items marked **FACT** w...
- decision: - This topic matters because it defines the game's construction ambition. The engine must be flexible enough to represent real infrastructure, but the UI must not become a full CAD system. - The rationale is portability and deterministic low-level control. It affects every future implementation prompt. Code generated for the engine must not use C99 features,...

## Representative Source Block References

- PVCB-00471: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-01075: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-00473: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- PVCB-00476: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- PVCB-00477: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- PVCB-01092: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md`
- PVCB-00482: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md`
- PVCB-00483: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md`
- PVCB-00486: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md`
- PVCB-01100: `docs/archive/conversations/_reader/by_chat/advanced_simulation_infrastructure.md`
- PVCB-01102: `docs/archive/conversations/_reader/by_chat/advanced_simulation_infrastructure.md`
- PVCB-01104: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01105: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01113: `docs/archive/conversations/_reader/by_chat/architecture_ui_providers.md`
- PVCB-01115: `docs/archive/conversations/_reader/by_chat/architecture_ui_providers.md`
- PVCB-00492: `docs/archive/conversations/_reader/by_chat/build_and_future_proofing.md`
- PVCB-00493: `docs/archive/conversations/_reader/by_chat/build_and_future_proofing.md`
- PVCB-00495: `docs/archive/conversations/_reader/by_chat/build_and_future_proofing.md`

## Block Type Counts

- `constraint`: 76
- `contradiction`: 1
- `decision`: 168
- `design_goal`: 83
- `explanation`: 69
- `prerequisite`: 6
- `prohibition`: 1
- `rationale`: 1
- `rejection`: 1
- `requirement`: 183
- `risk`: 3
- `roadmap`: 78
- `unresolved_question`: 2
