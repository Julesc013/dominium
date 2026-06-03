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

# Architecture And System Model

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

# Determinism, replay, evidence, and provenance

This theme gathers 802 source block(s) from 171 source file(s). It is advisory conversation evidence unless the current repo independently supports the same claim.

## What The Sources Suggest

The archive repeatedly returns to replay, proof, deterministic ordering, provenance, and validation as architectural necessities rather than test-only concerns.

## Strongest Recurring Signals

- The highest-priority tasks are TASK-01 through TASK-05: verify repo, compare existing refactor plan, formalize placement spec, choose deterministic frame math, and audit grid assumptions. Implementation should then follow TASK-06 through TASK-14.
- The user stated that the project had transitioned to C17 and C++17 and raised minimum systems to Windows 7 SP1, Mac OS X 10.9.5, and Linux. The visible conclusion was to use C17 for ABI-facing law-like structures, packets, fixed-width types, deterministic math, save/replay records, and low-level facades; C++17 for runtime machinery, provider implementations, Workbench, apps, resource ownership, and orchestration. Pub...
- The central tradeoff was speed versus purity. Raylib, SDL2, Lua, raygui, rlgl, rlsw, and related libraries can accelerate visible progress, but if they leak into game law, UI documents, saves, replays, or public contracts, they become architectural capture. The chosen compromise is to use them as providers behind Dominium-owned services and conformance tests.
- - Whether all recommended structural tasks should be implemented now is not established. - Whether the proposed build tuple naming scheme should become official is not yet established. - Whether the current top-level structure is final-final or merely best current target remains subject to user decision and repo evidence.
- This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-floor binaries are mandatory and that support cannot be claimed...
- 1. User's canon: C89 engine, C++98 game, determinism, per-floor artifacts, no CRT mixing, no silent API creep. 2. Build complexity comes from many machines and historical toolchains. 3. More hand-written presets are not the optimal solution. 4. Build truth should live in tuple contracts. 5. Local machine probes should generate local `CMakeUserPresets.json`. 6. CMake remains build authority. 7. AIDE should probe/expla...
- C89/C++98 canon, deterministic/no hidden behavior, per-floor artifacts, no CRT mixing, tuple-driven builds, public surface registry, replacement protocol, schema compatibility harness, and the warning that recommendations are not accepted canon yet.
- 1. **User confirmation:** identify which recommendations in this chat should become binding Dominium canon. 2. **Repo verification:** check current HEAD, CI status, build presets, CMake configure/build/CTest, layout validators, component matrix validators, and product/projection proof status. 3. **Choose first structural task:** either: - `STRUCTURE-01: Public Surface Registry`, or - `BUILD-CONTRACT-01: Tuple Build C...

## Decision And Review Shape

- decision: The highest-priority tasks are TASK-01 through TASK-05: verify repo, compare existing refactor plan, formalize placement spec, choose deterministic frame math, and audit grid assumptions. Implementation should then follow TASK-06 through TASK-14.
- decision: The user stated that the project had transitioned to C17 and C++17 and raised minimum systems to Windows 7 SP1, Mac OS X 10.9.5, and Linux. The visible conclusion was to use C17 for ABI-facing law-like structures, packets, fixed-width types, deterministic math, save/replay records, and low-level facades; C++17 for runtime machinery, provider implementations,...
- decision: The central tradeoff was speed versus purity. Raylib, SDL2, Lua, raygui, rlgl, rlsw, and related libraries can accelerate visible progress, but if they leak into game law, UI documents, saves, replays, or public contracts, they become architectural capture. The chosen compromise is to use them as providers behind Dominium-owned services and conformance tests...
- decision: - Whether all recommended structural tasks should be implemented now is not established. - Whether the proposed build tuple naming scheme should become official is not yet established. - Whether the current top-level structure is final-final or merely best current target remains subject to user decision and repo evidence.
- decision: This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-flo...
- decision: 1. User's canon: C89 engine, C++98 game, determinism, per-floor artifacts, no CRT mixing, no silent API creep. 2. Build complexity comes from many machines and historical toolchains. 3. More hand-written presets are not the optimal solution. 4. Build truth should live in tuple contracts. 5. Local machine probes should generate local `CMakeUserPresets.json`. ...
- decision: C89/C++98 canon, deterministic/no hidden behavior, per-floor artifacts, no CRT mixing, tuple-driven builds, public surface registry, replacement protocol, schema compatibility harness, and the warning that recommendations are not accepted canon yet.
- decision: 1. **User confirmation:** identify which recommendations in this chat should become binding Dominium canon. 2. **Repo verification:** check current HEAD, CI status, build presets, CMake configure/build/CTest, layout validators, component matrix validators, and product/projection proof status. 3. **Choose first structural task:** either: - `STRUCTURE-01: Publ...
- decision: 1. Which recommendations here should become binding canon? 2. Which should remain advisory until more evidence exists? 3. Write the implementation prompt for `STRUCTURE-01: Public Surface Registry`. 4. Write the implementation prompt for `BUILD-CONTRACT-01: Tuple Build Contracts and Machine Probe`. 5. Verify the current repo state and compare it to the older...
- decision: **Chat label:** Dominium Build and Future-Proofing Architecture **Date anchor:** 2026-05-27 Australia/Melbourne **Scope:** This report covers the visible conversation and the preservation task that produced the accompanying handoff files. It does **not** claim complete access to any earlier hidden or retired chats. **Epistemic note:** Items marked **FACT** w...

## Representative Source Block References

- PVCB-00106: `docs/archive/conversations/advanced_simulation_infrastructure/dominium_advanced_simulation_infrastructure_architecture__05_reader_brief.md`
- PVCB-00112: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-01075: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-00476: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- PVCB-00477: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- PVCB-01092: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md`
- PVCB-00114: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md`
- PVCB-00482: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md`
- PVCB-00483: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md`
- PVCB-00486: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md`
- PVCB-01100: `docs/archive/conversations/_reader/by_chat/advanced_simulation_infrastructure.md`
- PVCB-01102: `docs/archive/conversations/_reader/by_chat/advanced_simulation_infrastructure.md`
- PVCB-01105: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01106: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01107: `docs/archive/conversations/_reader/by_chat/app_testx_codehygiene.md`
- PVCB-01115: `docs/archive/conversations/_reader/by_chat/architecture_ui_providers.md`
- PVCB-00492: `docs/archive/conversations/_reader/by_chat/build_and_future_proofing.md`
- PVCB-00493: `docs/archive/conversations/_reader/by_chat/build_and_future_proofing.md`

## Block Type Counts

- `constraint`: 78
- `decision`: 206
- `design_goal`: 123
- `explanation`: 42
- `prerequisite`: 4
- `prohibition`: 3
- `rationale`: 1
- `requirement`: 273
- `risk`: 4
- `roadmap`: 62
- `unresolved_question`: 6

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

# Law, authority, capability, and refusal

This theme gathers 635 source block(s) from 156 source file(s). It is advisory conversation evidence unless the current repo independently supports the same claim.

## What The Sources Suggest

Authority is framed as constrained permission under law. Refusal is a lawful, auditable outcome, not a failure path to hide.

## Strongest Recurring Signals

- The highest-priority tasks are TASK-01 through TASK-05: verify repo, compare existing refactor plan, formalize placement spec, choose deterministic frame math, and audit grid assumptions. Implementation should then follow TASK-06 through TASK-14.
- - APP0 scope is application/runtime/platform/render only. - Engine + game remain authoritative. - Applications are orchestrators, not decision-makers. - Rendering never affects simulation. - Client is non-authoritative. - Server is authoritative and headless-capable. - Launcher must not install content or alter simulation state. - Setup owns install/version/integrity responsibilities. - Tools must obey authority/law ...
- The user stated that the project had transitioned to C17 and C++17 and raised minimum systems to Windows 7 SP1, Mac OS X 10.9.5, and Linux. The visible conclusion was to use C17 for ABI-facing law-like structures, packets, fixed-width types, deterministic math, save/replay records, and low-level facades; C++17 for runtime machinery, provider implementations, Workbench, apps, resource ownership, and orchestration. Pub...
- The central tradeoff was speed versus purity. Raylib, SDL2, Lua, raygui, rlgl, rlsw, and related libraries can accelerate visible progress, but if they leak into game law, UI documents, saves, replays, or public contracts, they become architectural capture. The chosen compromise is to use them as providers behind Dominium-owned services and conformance tests.
- - 00 manifest: package map. - 01 human-readable report: sections 0-16. - 02 context transfer packet: future-chat handoff. - 03 spec sheet: YAML-style aggregation data. - 04 registers: workstreams, decisions, tasks, constraints, questions, artifacts, risks, verification, timeline, spec contributions. - 05 aggregator packet: compact merge packet. - 06 reader brief: shorter guide. - 07 verification and audit: self-audit...
- This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-floor binaries are mandatory and that support cannot be claimed...
- The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
- 1. User's canon: C89 engine, C++98 game, determinism, per-floor artifacts, no CRT mixing, no silent API creep. 2. Build complexity comes from many machines and historical toolchains. 3. More hand-written presets are not the optimal solution. 4. Build truth should live in tuple contracts. 5. Local machine probes should generate local `CMakeUserPresets.json`. 6. CMake remains build authority. 7. AIDE should probe/expla...

## Decision And Review Shape

- decision: The highest-priority tasks are TASK-01 through TASK-05: verify repo, compare existing refactor plan, formalize placement spec, choose deterministic frame math, and audit grid assumptions. Implementation should then follow TASK-06 through TASK-14.
- decision: - APP0 scope is application/runtime/platform/render only. - Engine + game remain authoritative. - Applications are orchestrators, not decision-makers. - Rendering never affects simulation. - Client is non-authoritative. - Server is authoritative and headless-capable. - Launcher must not install content or alter simulation state. - Setup owns install/version/...
- decision: The user stated that the project had transitioned to C17 and C++17 and raised minimum systems to Windows 7 SP1, Mac OS X 10.9.5, and Linux. The visible conclusion was to use C17 for ABI-facing law-like structures, packets, fixed-width types, deterministic math, save/replay records, and low-level facades; C++17 for runtime machinery, provider implementations,...
- decision: The central tradeoff was speed versus purity. Raylib, SDL2, Lua, raygui, rlgl, rlsw, and related libraries can accelerate visible progress, but if they leak into game law, UI documents, saves, replays, or public contracts, they become architectural capture. The chosen compromise is to use them as providers behind Dominium-owned services and conformance tests...
- decision: - 00 manifest: package map. - 01 human-readable report: sections 0-16. - 02 context transfer packet: future-chat handoff. - 03 spec sheet: YAML-style aggregation data. - 04 registers: workstreams, decisions, tasks, constraints, questions, artifacts, risks, verification, timeline, spec contributions. - 05 aggregator packet: compact merge packet. - 06 reader b...
- decision: This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-flo...
- decision: The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the author...
- decision: 1. User's canon: C89 engine, C++98 game, determinism, per-floor artifacts, no CRT mixing, no silent API creep. 2. Build complexity comes from many machines and historical toolchains. 3. More hand-written presets are not the optimal solution. 4. Build truth should live in tuple contracts. 5. Local machine probes should generate local `CMakeUserPresets.json`. ...
- decision: - The answer reframed this as a platform/runtime problem, not just a rendering problem. A visible window requires OS event loops, resize events, close handling, timing, native surface handles, and presentation. Those responsibilities do not belong inside the renderer itself. This led to the proposal of a dedicated **platform runtime layer**. - The key conclu...
- decision: - The central topic was APP0: the application/runtime/platform/renderer layer of Dominium. This topic came up because the user provided a formal prompt defining what APP0 should do. - The most important conclusion was that APP0 must remain outside the core simulation rules. **FACT:** the user explicitly forbade redesigning simulation rules, altering content ...

## Representative Source Block References

- PVCB-00106: `docs/archive/conversations/advanced_simulation_infrastructure/dominium_advanced_simulation_infrastructure_architecture__05_reader_brief.md`
- PVCB-01058: `docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__05_reader_brief.md`
- PVCB-00112: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-01075: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-00856: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__09_in_chat_reader.md`
- PVCB-00477: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- PVCB-00859: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- PVCB-01092: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md`
- PVCB-00865: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01105: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01106: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01107: `docs/archive/conversations/_reader/by_chat/app_testx_codehygiene.md`
- PVCB-01115: `docs/archive/conversations/_reader/by_chat/architecture_ui_providers.md`
- PVCB-00492: `docs/archive/conversations/_reader/by_chat/build_and_future_proofing.md`
- PVCB-00493: `docs/archive/conversations/_reader/by_chat/build_and_future_proofing.md`
- PVCB-01118: `docs/archive/conversations/_reader/by_chat/canonical_structure_and_framework.md`
- PVCB-01121: `docs/archive/conversations/_reader/by_chat/canonical_structure_and_framework.md`
- PVCB-00866: `docs/archive/conversations/_reader/by_chat/documentation_standards_readme.md`

## Block Type Counts

- `constraint`: 43
- `contradiction`: 1
- `decision`: 188
- `design_goal`: 69
- `explanation`: 11
- `prerequisite`: 3
- `prohibition`: 3
- `requirement`: 256
- `risk`: 2
- `roadmap`: 57
- `unresolved_question`: 2

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

# Engine/game/runtime/product boundaries

This theme gathers 961 source block(s) from 167 source file(s). It is advisory conversation evidence unless the current repo independently supports the same claim.

## What The Sources Suggest

Many conversations test where engine, game, runtime, client, server, and product layers should meet without collapsing ownership.

## Strongest Recurring Signals

- - APP0 scope is application/runtime/platform/render only. - Engine + game remain authoritative. - Applications are orchestrators, not decision-makers. - Rendering never affects simulation. - Client is non-authoritative. - Server is authoritative and headless-capable. - Launcher must not install content or alter simulation state. - Setup owns install/version/integrity responsibilities. - Tools must obey authority/law ...
- The user stated that the project had transitioned to C17 and C++17 and raised minimum systems to Windows 7 SP1, Mac OS X 10.9.5, and Linux. The visible conclusion was to use C17 for ABI-facing law-like structures, packets, fixed-width types, deterministic math, save/replay records, and low-level facades; C++17 for runtime machinery, provider implementations, Workbench, apps, resource ownership, and orchestration. Pub...
- The central tradeoff was speed versus purity. Raylib, SDL2, Lua, raygui, rlgl, rlsw, and related libraries can accelerate visible progress, but if they leak into game law, UI documents, saves, replays, or public contracts, they become architectural capture. The chosen compromise is to use them as providers behind Dominium-owned services and conformance tests.
- The immediate game-design plan is to formalize the robotic seed-civilisation doctrine into a spec chapter and choose a first gameplay loop, likely survey -> mine -> refine -> fabricate -> build simple power/logistics/spawn infrastructure.
- The Robot OS and robotic seed-civilisation decisions are the most important design decisions. They are explicit user statements, not merely assistant proposals. They should be formalized as product/game requirements. They affect UI, fog-of-war, spawning, respawn, automation, industry, tutorial/planner design, and MMO anti-cheat.
- This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-floor binaries are mandatory and that support cannot be claimed...
- 1. User's canon: C89 engine, C++98 game, determinism, per-floor artifacts, no CRT mixing, no silent API creep. 2. Build complexity comes from many machines and historical toolchains. 3. More hand-written presets are not the optimal solution. 4. Build truth should live in tuple contracts. 5. Local machine probes should generate local `CMakeUserPresets.json`. 6. CMake remains build authority. 7. AIDE should probe/expla...
- - This topic matters because it defines the game's construction ambition. The engine must be flexible enough to represent real infrastructure, but the UI must not become a full CAD system. - The rationale is portability and deterministic low-level control. It affects every future implementation prompt. Code generated for the engine must not use C99 features, C++ features, compiler extensions, platform APIs, or undefi...

## Decision And Review Shape

- decision: - APP0 scope is application/runtime/platform/render only. - Engine + game remain authoritative. - Applications are orchestrators, not decision-makers. - Rendering never affects simulation. - Client is non-authoritative. - Server is authoritative and headless-capable. - Launcher must not install content or alter simulation state. - Setup owns install/version/...
- decision: The user stated that the project had transitioned to C17 and C++17 and raised minimum systems to Windows 7 SP1, Mac OS X 10.9.5, and Linux. The visible conclusion was to use C17 for ABI-facing law-like structures, packets, fixed-width types, deterministic math, save/replay records, and low-level facades; C++17 for runtime machinery, provider implementations,...
- decision: The central tradeoff was speed versus purity. Raylib, SDL2, Lua, raygui, rlgl, rlsw, and related libraries can accelerate visible progress, but if they leak into game law, UI documents, saves, replays, or public contracts, they become architectural capture. The chosen compromise is to use them as providers behind Dominium-owned services and conformance tests...
- decision: The immediate game-design plan is to formalize the robotic seed-civilisation doctrine into a spec chapter and choose a first gameplay loop, likely survey -> mine -> refine -> fabricate -> build simple power/logistics/spawn infrastructure.
- decision: The Robot OS and robotic seed-civilisation decisions are the most important design decisions. They are explicit user statements, not merely assistant proposals. They should be formalized as product/game requirements. They affect UI, fog-of-war, spawning, respawn, automation, industry, tutorial/planner design, and MMO anti-cheat.
- decision: This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-flo...
- decision: 1. User's canon: C89 engine, C++98 game, determinism, per-floor artifacts, no CRT mixing, no silent API creep. 2. Build complexity comes from many machines and historical toolchains. 3. More hand-written presets are not the optimal solution. 4. Build truth should live in tuple contracts. 5. Local machine probes should generate local `CMakeUserPresets.json`. ...
- decision: - This topic matters because it defines the game's construction ambition. The engine must be flexible enough to represent real infrastructure, but the UI must not become a full CAD system. - The rationale is portability and deterministic low-level control. It affects every future implementation prompt. Code generated for the engine must not use C99 features,...
- decision: - The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The user's question directly made arbitrary placement a major topic. [INFERENCE] The answer was accepted as the current design direction because the user then asked for a Codex prompt ...
- decision: - The answer reframed this as a platform/runtime problem, not just a rendering problem. A visible window requires OS event loops, resize events, close handling, timing, native surface handles, and presentation. Those responsibilities do not belong inside the renderer itself. This led to the proposal of a dedicated **platform runtime layer**. - The key conclu...

## Representative Source Block References

- PVCB-01058: `docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__05_reader_brief.md`
- PVCB-00112: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-01075: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-01076: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-01078: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-00477: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- PVCB-01092: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md`
- PVCB-01100: `docs/archive/conversations/_reader/by_chat/advanced_simulation_infrastructure.md`
- PVCB-01102: `docs/archive/conversations/_reader/by_chat/advanced_simulation_infrastructure.md`
- PVCB-00865: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01104: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01105: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01106: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01107: `docs/archive/conversations/_reader/by_chat/app_testx_codehygiene.md`
- PVCB-01113: `docs/archive/conversations/_reader/by_chat/architecture_ui_providers.md`
- PVCB-01115: `docs/archive/conversations/_reader/by_chat/architecture_ui_providers.md`
- PVCB-00493: `docs/archive/conversations/_reader/by_chat/build_and_future_proofing.md`
- PVCB-00495: `docs/archive/conversations/_reader/by_chat/build_and_future_proofing.md`

## Block Type Counts

- `constraint`: 111
- `contradiction`: 2
- `decision`: 250
- `design_goal`: 117
- `explanation`: 46
- `prerequisite`: 7
- `prohibition`: 2
- `rationale`: 1
- `requirement`: 333
- `risk`: 5
- `roadmap`: 79
- `unresolved_question`: 8
