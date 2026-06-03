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

# Product And Tooling

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

# UI, renderer, native GUI, and presentation

This theme gathers 1188 source block(s) from 190 source file(s). It is advisory conversation evidence unless the current repo independently supports the same claim.

## What The Sources Suggest

Renderer and UI ambitions are broad, but the stable rule is that presentation must project truth rather than own or mutate it.

## Strongest Recurring Signals

- - APP0 scope is application/runtime/platform/render only. - Engine + game remain authoritative. - Applications are orchestrators, not decision-makers. - Rendering never affects simulation. - Client is non-authoritative. - Server is authoritative and headless-capable. - Launcher must not install content or alter simulation state. - Setup owns install/version/integrity responsibilities. - Tools must obey authority/law ...
- - Save this report package. - Inspect actual repository state. - Start Path D new chat using the bootstrap prompt. - Verify whether prompts have been implemented. - Choose/verify GUI backend. - Define Path D solver architecture and fixed-point ranges. - Avoid duplicate systems if old code exists.
- DECISION-01 through DECISION-12 above are the decision set that should carry forward. The strongest accepted formulation is service-first, provider-backed, profile-selected, contract-governed, and third-party-fenced. This decision matters because it reconciles the user's desire to use raylib/SDL/Lua now with the deeper requirement that Dominium remain portable and replaceable. It supersedes vendor-shaped architecture...
- 4. "Which decisions in this chat were explicit user decisions versus assistant synthesis?" 5. "Which renderer/platform decisions are final, and which are still provisional?" 6. "Which parts of the robotic seed-civilisation design are hard requirements?"
- The central tradeoff was speed versus purity. Raylib, SDL2, Lua, raygui, rlgl, rlsw, and related libraries can accelerate visible progress, but if they leak into game law, UI documents, saves, replays, or public contracts, they become architectural capture. The chosen compromise is to use them as providers behind Dominium-owned services and conformance tests.
- The immediate game-design plan is to formalize the robotic seed-civilisation doctrine into a spec chapter and choose a first gameplay loop, likely survey -> mine -> refine -> fabricate -> build simple power/logistics/spawn infrastructure.
- The Robot OS and robotic seed-civilisation decisions are the most important design decisions. They are explicit user statements, not merely assistant proposals. They should be formalized as product/game requirements. They affect UI, fog-of-war, spawning, respawn, automation, industry, tutorial/planner design, and MMO anti-cheat.
- The language baseline decision matters because it changes what old renderers and toolchains matter. C17/C++17 reduces the need to design around C89/C++98 constraints but does not remove the need for C-compatible ABI boundaries. The system floor decision similarly moves many older renderers and OS targets into research/back-port categories.

## Decision And Review Shape

- decision: - APP0 scope is application/runtime/platform/render only. - Engine + game remain authoritative. - Applications are orchestrators, not decision-makers. - Rendering never affects simulation. - Client is non-authoritative. - Server is authoritative and headless-capable. - Launcher must not install content or alter simulation state. - Setup owns install/version/...
- decision: - Save this report package. - Inspect actual repository state. - Start Path D new chat using the bootstrap prompt. - Verify whether prompts have been implemented. - Choose/verify GUI backend. - Define Path D solver architecture and fixed-point ranges. - Avoid duplicate systems if old code exists.
- decision: DECISION-01 through DECISION-12 above are the decision set that should carry forward. The strongest accepted formulation is service-first, provider-backed, profile-selected, contract-governed, and third-party-fenced. This decision matters because it reconciles the user's desire to use raylib/SDL/Lua now with the deeper requirement that Dominium remain portab...
- decision: 4. "Which decisions in this chat were explicit user decisions versus assistant synthesis?" 5. "Which renderer/platform decisions are final, and which are still provisional?" 6. "Which parts of the robotic seed-civilisation design are hard requirements?"
- decision: The central tradeoff was speed versus purity. Raylib, SDL2, Lua, raygui, rlgl, rlsw, and related libraries can accelerate visible progress, but if they leak into game law, UI documents, saves, replays, or public contracts, they become architectural capture. The chosen compromise is to use them as providers behind Dominium-owned services and conformance tests...
- decision: The immediate game-design plan is to formalize the robotic seed-civilisation doctrine into a spec chapter and choose a first gameplay loop, likely survey -> mine -> refine -> fabricate -> build simple power/logistics/spawn infrastructure.
- decision: The Robot OS and robotic seed-civilisation decisions are the most important design decisions. They are explicit user statements, not merely assistant proposals. They should be formalized as product/game requirements. They affect UI, fog-of-war, spawning, respawn, automation, industry, tutorial/planner design, and MMO anti-cheat.
- decision: The language baseline decision matters because it changes what old renderers and toolchains matter. C17/C++17 reduces the need to design around C89/C++98 constraints but does not remove the need for C-compatible ABI boundaries. The system floor decision similarly moves many older renderers and OS targets into research/back-port categories.
- decision: - 00 manifest: package map. - 01 human-readable report: sections 0-16. - 02 context transfer packet: future-chat handoff. - 03 spec sheet: YAML-style aggregation data. - 04 registers: workstreams, decisions, tasks, constraints, questions, artifacts, risks, verification, timeline, spec contributions. - 05 aggregator packet: compact merge packet. - 06 reader b...
- decision: - Whether all recommended structural tasks should be implemented now is not established. - Whether the proposed build tuple naming scheme should become official is not yet established. - Whether the current top-level structure is final-final or merely best current target remains subject to user decision and repo evidence.

## Representative Source Block References

- PVCB-01058: `docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__05_reader_brief.md`
- PVCB-01833: `docs/archive/conversations/architecture_codex_prompts/dominium_domino_architecture_codex_prompts__05_reader_brief.md`
- PVCB-00471: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-01069: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-01075: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-01076: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-01078: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-01838: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-00856: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__09_in_chat_reader.md`
- PVCB-00476: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- PVCB-00477: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- PVCB-00859: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- PVCB-01841: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- PVCB-01843: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- PVCB-01092: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md`
- PVCB-00114: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md`
- PVCB-01845: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md`
- PVCB-00482: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md`

## Block Type Counts

- `constraint`: 108
- `contradiction`: 2
- `decision`: 304
- `design_goal`: 179
- `explanation`: 68
- `prerequisite`: 13
- `prohibition`: 4
- `rejection`: 2
- `requirement`: 388
- `risk`: 7
- `roadmap`: 103
- `unresolved_question`: 10

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

# Workbench, AIDE, Codex, automation, and governance

This theme gathers 676 source block(s) from 159 source file(s). It is advisory conversation evidence unless the current repo independently supports the same claim.

## What The Sources Suggest

Workbench, AIDE, and Codex recur as governed operator and repo-control surfaces that expose evidence and actions without becoming canon.

## Strongest Recurring Signals

- The user stated that the project had transitioned to C17 and C++17 and raised minimum systems to Windows 7 SP1, Mac OS X 10.9.5, and Linux. The visible conclusion was to use C17 for ABI-facing law-like structures, packets, fixed-width types, deterministic math, save/replay records, and low-level facades; C++17 for runtime machinery, provider implementations, Workbench, apps, resource ownership, and orchestration. Pub...
- The Robot OS and robotic seed-civilisation decisions are the most important design decisions. They are explicit user statements, not merely assistant proposals. They should be formalized as product/game requirements. They affect UI, fog-of-war, spawning, respawn, automation, industry, tutorial/planner design, and MMO anti-cheat.
- 1. User's canon: C89 engine, C++98 game, determinism, per-floor artifacts, no CRT mixing, no silent API creep. 2. Build complexity comes from many machines and historical toolchains. 3. More hand-written presets are not the optimal solution. 4. Build truth should live in tuple contracts. 5. Local machine probes should generate local `CMakeUserPresets.json`. 6. CMake remains build authority. 7. AIDE should probe/expla...
- 1. **User confirmation:** identify which recommendations in this chat should become binding Dominium canon. 2. **Repo verification:** check current HEAD, CI status, build presets, CMake configure/build/CTest, layout validators, component matrix validators, and product/projection proof status. 3. **Choose first structural task:** either: - `STRUCTURE-01: Public Surface Registry`, or - `BUILD-CONTRACT-01: Tuple Build C...
- - The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The user's question directly made arbitrary placement a major topic. [INFERENCE] The answer was accepted as the current design direction because the user then asked for a Codex prompt plan to implement changes necessary to achieve it. - Finally...
- - The user then added a newer versioning model from another chat: product SemVer is manual; build kind is dev/ci/beta/rc/release/hotfix; global build number is only for distributed beta/rc/release/hotfix; build instance ID always exists for dev/ci; channels are separate; all products in a release share the same GBN. This superseded the earlier simpler "build number increments whenever tests pass" model. - The user pr...
- - The user then said the latest docs and code were live at `julesc013/dominium`. The assistant treated the repo as an implementation baseline and observed that AppShell, UI mode resolution, distribution doctrine, and component matrices already existed. This changed the task from inventing a GUI strategy from scratch to reconciling the transfer brief with existing repository doctrine. - INFERENCE: The user wants to tu...
- - The language baseline decision matters because it changes what old renderers and toolchains matter. C17/C++17 reduces the need to design around C89/C++98 constraints but does not remove the need for C-compatible ABI boundaries. The system floor decision similarly moves many older renderers and OS targets into research/back-port categories. - The Robot OS and robotic seed-civilisation decisions are the most importan...

## Decision And Review Shape

- decision: The user stated that the project had transitioned to C17 and C++17 and raised minimum systems to Windows 7 SP1, Mac OS X 10.9.5, and Linux. The visible conclusion was to use C17 for ABI-facing law-like structures, packets, fixed-width types, deterministic math, save/replay records, and low-level facades; C++17 for runtime machinery, provider implementations,...
- decision: The Robot OS and robotic seed-civilisation decisions are the most important design decisions. They are explicit user statements, not merely assistant proposals. They should be formalized as product/game requirements. They affect UI, fog-of-war, spawning, respawn, automation, industry, tutorial/planner design, and MMO anti-cheat.
- decision: 1. User's canon: C89 engine, C++98 game, determinism, per-floor artifacts, no CRT mixing, no silent API creep. 2. Build complexity comes from many machines and historical toolchains. 3. More hand-written presets are not the optimal solution. 4. Build truth should live in tuple contracts. 5. Local machine probes should generate local `CMakeUserPresets.json`. ...
- decision: 1. **User confirmation:** identify which recommendations in this chat should become binding Dominium canon. 2. **Repo verification:** check current HEAD, CI status, build presets, CMake configure/build/CTest, layout validators, component matrix validators, and product/projection proof status. 3. **Choose first structural task:** either: - `STRUCTURE-01: Publ...
- decision: - The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The user's question directly made arbitrary placement a major topic. [INFERENCE] The answer was accepted as the current design direction because the user then asked for a Codex prompt ...
- decision: - The user then added a newer versioning model from another chat: product SemVer is manual; build kind is dev/ci/beta/rc/release/hotfix; global build number is only for distributed beta/rc/release/hotfix; build instance ID always exists for dev/ci; channels are separate; all products in a release share the same GBN. This superseded the earlier simpler "build...
- decision: - The user then said the latest docs and code were live at `julesc013/dominium`. The assistant treated the repo as an implementation baseline and observed that AppShell, UI mode resolution, distribution doctrine, and component matrices already existed. This changed the task from inventing a GUI strategy from scratch to reconciling the transfer brief with exi...
- decision: - The language baseline decision matters because it changes what old renderers and toolchains matter. C17/C++17 reduces the need to design around C89/C++98 constraints but does not remove the need for C-compatible ABI boundaries. The system floor decision similarly moves many older renderers and OS targets into research/back-port categories. - The Robot OS a...
- decision: - Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions...
- decision: - Packs are distributable authored payloads. The preferred pack layout became category-based, such as `content/packs/<category>/<pack_id>/`. Pack IDs must not depend on paths. Saves and replays must use stable IDs, schema versions, canonical serialization, deterministic hashes, and explicit migration/refusal policies. Backward compatibility must be a compati...

## Representative Source Block References

- PVCB-00112: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-01078: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-01092: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md`
- PVCB-00482: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md`
- PVCB-01102: `docs/archive/conversations/_reader/by_chat/advanced_simulation_infrastructure.md`
- PVCB-01107: `docs/archive/conversations/_reader/by_chat/app_testx_codehygiene.md`
- PVCB-01113: `docs/archive/conversations/_reader/by_chat/architecture_ui_providers.md`
- PVCB-01115: `docs/archive/conversations/_reader/by_chat/architecture_ui_providers.md`
- PVCB-00492: `docs/archive/conversations/_reader/by_chat/build_and_future_proofing.md`
- PVCB-01118: `docs/archive/conversations/_reader/by_chat/canonical_structure_and_framework.md`
- PVCB-01121: `docs/archive/conversations/_reader/by_chat/canonical_structure_and_framework.md`
- PVCB-01123: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- PVCB-01695: `docs/archive/conversations/_reader/by_chat/documentation_standards_readme.md`
- PVCB-01131: `docs/archive/conversations/_reader/by_chat/dominium_architecture_i.md`
- PVCB-01138: `docs/archive/conversations/_reader/by_chat/dominium_architecture_iii.md`
- PVCB-01143: `docs/archive/conversations/_reader/by_chat/dominium_architecture_iv.md`
- PVCB-01154: `docs/archive/conversations/_reader/by_chat/dominium_domino_codex_planning.md`
- PVCB-01158: `docs/archive/conversations/_reader/by_chat/dominium_full_conversation.md`

## Block Type Counts

- `constraint`: 47
- `contradiction`: 1
- `decision`: 175
- `design_goal`: 105
- `explanation`: 53
- `prerequisite`: 10
- `prohibition`: 2
- `rationale`: 1
- `rejection`: 1
- `requirement`: 213
- `risk`: 4
- `roadmap`: 59
- `unresolved_question`: 5

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

# Setup, launcher, release, and platform

This theme gathers 733 source block(s) from 159 source file(s). It is advisory conversation evidence unless the current repo independently supports the same claim.

## What The Sources Suggest

Setup, launcher, release, and version identity appear as later product/control-plane concerns with current queue limits.

## Strongest Recurring Signals

- - APP0 scope is application/runtime/platform/render only. - Engine + game remain authoritative. - Applications are orchestrators, not decision-makers. - Rendering never affects simulation. - Client is non-authoritative. - Server is authoritative and headless-capable. - Launcher must not install content or alter simulation state. - Setup owns install/version/integrity responsibilities. - Tools must obey authority/law ...
- The user stated that the project had transitioned to C17 and C++17 and raised minimum systems to Windows 7 SP1, Mac OS X 10.9.5, and Linux. The visible conclusion was to use C17 for ABI-facing law-like structures, packets, fixed-width types, deterministic math, save/replay records, and low-level facades; C++17 for runtime machinery, provider implementations, Workbench, apps, resource ownership, and orchestration. Pub...
- 4. "Which decisions in this chat were explicit user decisions versus assistant synthesis?" 5. "Which renderer/platform decisions are final, and which are still provisional?" 6. "Which parts of the robotic seed-civilisation design are hard requirements?"
- The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the authority itself.
- 1. User's canon: C89 engine, C++98 game, determinism, per-floor artifacts, no CRT mixing, no silent API creep. 2. Build complexity comes from many machines and historical toolchains. 3. More hand-written presets are not the optimal solution. 4. Build truth should live in tuple contracts. 5. Local machine probes should generate local `CMakeUserPresets.json`. 6. CMake remains build authority. 7. AIDE should probe/expla...
- - This topic matters because it defines the game's construction ambition. The engine must be flexible enough to represent real infrastructure, but the UI must not become a full CAD system. - The rationale is portability and deterministic low-level control. It affects every future implementation prompt. Code generated for the engine must not use C99 features, C++ features, compiler extensions, platform APIs, or undefi...
- - The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The user's question directly made arbitrary placement a major topic. [INFERENCE] The answer was accepted as the current design direction because the user then asked for a Codex prompt plan to implement changes necessary to achieve it. - Finally...
- - The answer reframed this as a platform/runtime problem, not just a rendering problem. A visible window requires OS event loops, resize events, close handling, timing, native surface handles, and presentation. Those responsibilities do not belong inside the renderer itself. This led to the proposal of a dedicated **platform runtime layer**. - The key conclusion is that the launcher must not install content or alter ...

## Decision And Review Shape

- decision: - APP0 scope is application/runtime/platform/render only. - Engine + game remain authoritative. - Applications are orchestrators, not decision-makers. - Rendering never affects simulation. - Client is non-authoritative. - Server is authoritative and headless-capable. - Launcher must not install content or alter simulation state. - Setup owns install/version/...
- decision: The user stated that the project had transitioned to C17 and C++17 and raised minimum systems to Windows 7 SP1, Mac OS X 10.9.5, and Linux. The visible conclusion was to use C17 for ABI-facing law-like structures, packets, fixed-width types, deterministic math, save/replay records, and low-level facades; C++17 for runtime machinery, provider implementations,...
- decision: 4. "Which decisions in this chat were explicit user decisions versus assistant synthesis?" 5. "Which renderer/platform decisions are final, and which are still provisional?" 6. "Which parts of the robotic seed-civilisation design are hard requirements?"
- decision: The major build-system conclusion was that `CMakePresets.json` should not carry every human, host, IDE, renderer, OS floor, and release concern directly. The proposed design is contract-driven: define build tuples, detect machine capabilities, generate local user presets, then run CMake. This makes presets projections of contract truth rather than the author...
- decision: 1. User's canon: C89 engine, C++98 game, determinism, per-floor artifacts, no CRT mixing, no silent API creep. 2. Build complexity comes from many machines and historical toolchains. 3. More hand-written presets are not the optimal solution. 4. Build truth should live in tuple contracts. 5. Local machine probes should generate local `CMakeUserPresets.json`. ...
- decision: - This topic matters because it defines the game's construction ambition. The engine must be flexible enough to represent real infrastructure, but the UI must not become a full CAD system. - The rationale is portability and deterministic low-level control. It affects every future implementation prompt. Code generated for the engine must not use C99 features,...
- decision: - The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The user's question directly made arbitrary placement a major topic. [INFERENCE] The answer was accepted as the current design direction because the user then asked for a Codex prompt ...
- decision: - The answer reframed this as a platform/runtime problem, not just a rendering problem. A visible window requires OS event loops, resize events, close handling, timing, native surface handles, and presentation. Those responsibilities do not belong inside the renderer itself. This led to the proposal of a dedicated **platform runtime layer**. - The key conclu...
- decision: This chat was mainly about the **Dominium / Domino project's application and runtime layer**, referred to throughout as **APP0**. The user began by giving a large implementation-oriented prompt titled **"PROMPT APP0 - RUNTIMES, APPLICATIONS, PLATFORMS & RENDERERS."** That prompt defined a strict scope: work on the **client, server, launcher, setup/installer,...
- decision: - The central topic was APP0: the application/runtime/platform/renderer layer of Dominium. This topic came up because the user provided a formal prompt defining what APP0 should do. - The most important conclusion was that APP0 must remain outside the core simulation rules. **FACT:** the user explicitly forbade redesigning simulation rules, altering content ...

## Representative Source Block References

- PVCB-01058: `docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__05_reader_brief.md`
- PVCB-00112: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-01069: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-00859: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
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
- PVCB-01118: `docs/archive/conversations/_reader/by_chat/canonical_structure_and_framework.md`
- PVCB-01121: `docs/archive/conversations/_reader/by_chat/canonical_structure_and_framework.md`
- PVCB-01127: `docs/archive/conversations/_reader/by_chat/development_routes.md`
- PVCB-00866: `docs/archive/conversations/_reader/by_chat/documentation_standards_readme.md`

## Block Type Counts

- `constraint`: 67
- `contradiction`: 2
- `decision`: 168
- `design_goal`: 118
- `explanation`: 55
- `prerequisite`: 6
- `prohibition`: 3
- `rejection`: 2
- `requirement`: 238
- `risk`: 4
- `roadmap`: 63
- `unresolved_question`: 7

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

# Content, packs, modding, and providers

This theme gathers 1182 source block(s) from 201 source file(s). It is advisory conversation evidence unless the current repo independently supports the same claim.

## What The Sources Suggest

The archive preserves a strong preference for data-driven packs, registries, compatibility, and explicit refusal over hidden fallback or executable content magic.

## Strongest Recurring Signals

- - APP0 scope is application/runtime/platform/render only. - Engine + game remain authoritative. - Applications are orchestrators, not decision-makers. - Rendering never affects simulation. - Client is non-authoritative. - Server is authoritative and headless-capable. - Launcher must not install content or alter simulation state. - Setup owns install/version/integrity responsibilities. - Tools must obey authority/law ...
- - Save this report package. - Inspect actual repository state. - Start Path D new chat using the bootstrap prompt. - Verify whether prompts have been implemented. - Choose/verify GUI backend. - Define Path D solver architecture and fixed-point ranges. - Avoid duplicate systems if old code exists.
- The user stated that the project had transitioned to C17 and C++17 and raised minimum systems to Windows 7 SP1, Mac OS X 10.9.5, and Linux. The visible conclusion was to use C17 for ABI-facing law-like structures, packets, fixed-width types, deterministic math, save/replay records, and low-level facades; C++17 for runtime machinery, provider implementations, Workbench, apps, resource ownership, and orchestration. Pub...
- DECISION-01 through DECISION-12 above are the decision set that should carry forward. The strongest accepted formulation is service-first, provider-backed, profile-selected, contract-governed, and third-party-fenced. This decision matters because it reconciles the user's desire to use raylib/SDL/Lua now with the deeper requirement that Dominium remain portable and replaceable. It supersedes vendor-shaped architecture...
- The central tradeoff was speed versus purity. Raylib, SDL2, Lua, raygui, rlgl, rlsw, and related libraries can accelerate visible progress, but if they leak into game law, UI documents, saves, replays, or public contracts, they become architectural capture. The chosen compromise is to use them as providers behind Dominium-owned services and conformance tests.
- - 00 manifest: package map. - 01 human-readable report: sections 0-16. - 02 context transfer packet: future-chat handoff. - 03 spec sheet: YAML-style aggregation data. - 04 registers: workstreams, decisions, tasks, constraints, questions, artifacts, risks, verification, timeline, spec contributions. - 05 aggregator packet: compact merge packet. - 06 reader brief: shorter guide. - 07 verification and audit: self-audit...
- Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions.
- The final uploaded prompt asked for this preservation package. The key thing to preserve is that most architecture proposals are recommendations, not accepted user decisions yet. The next best action is to decide which recommendations become canon, then implement either `STRUCTURE-01: Public Surface Registry` or the build tuple contract work, after verifying the current live repo state.

## Decision And Review Shape

- decision: - APP0 scope is application/runtime/platform/render only. - Engine + game remain authoritative. - Applications are orchestrators, not decision-makers. - Rendering never affects simulation. - Client is non-authoritative. - Server is authoritative and headless-capable. - Launcher must not install content or alter simulation state. - Setup owns install/version/...
- decision: - Save this report package. - Inspect actual repository state. - Start Path D new chat using the bootstrap prompt. - Verify whether prompts have been implemented. - Choose/verify GUI backend. - Define Path D solver architecture and fixed-point ranges. - Avoid duplicate systems if old code exists.
- decision: The user stated that the project had transitioned to C17 and C++17 and raised minimum systems to Windows 7 SP1, Mac OS X 10.9.5, and Linux. The visible conclusion was to use C17 for ABI-facing law-like structures, packets, fixed-width types, deterministic math, save/replay records, and low-level facades; C++17 for runtime machinery, provider implementations,...
- decision: DECISION-01 through DECISION-12 above are the decision set that should carry forward. The strongest accepted formulation is service-first, provider-backed, profile-selected, contract-governed, and third-party-fenced. This decision matters because it reconciles the user's desire to use raylib/SDL/Lua now with the deeper requirement that Dominium remain portab...
- decision: The central tradeoff was speed versus purity. Raylib, SDL2, Lua, raygui, rlgl, rlsw, and related libraries can accelerate visible progress, but if they leak into game law, UI documents, saves, replays, or public contracts, they become architectural capture. The chosen compromise is to use them as providers behind Dominium-owned services and conformance tests...
- decision: - 00 manifest: package map. - 01 human-readable report: sections 0-16. - 02 context transfer packet: future-chat handoff. - 03 spec sheet: YAML-style aggregation data. - 04 registers: workstreams, decisions, tasks, constraints, questions, artifacts, risks, verification, timeline, spec contributions. - 05 aggregator packet: compact merge packet. - 06 reader b...
- decision: Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions.
- decision: The final uploaded prompt asked for this preservation package. The key thing to preserve is that most architecture proposals are recommendations, not accepted user decisions yet. The next best action is to decide which recommendations become canon, then implement either `STRUCTURE-01: Public Surface Registry` or the build tuple contract work, after verifying...
- decision: 1. User's canon: C89 engine, C++98 game, determinism, per-floor artifacts, no CRT mixing, no silent API creep. 2. Build complexity comes from many machines and historical toolchains. 3. More hand-written presets are not the optimal solution. 4. Build truth should live in tuple contracts. 5. Local machine probes should generate local `CMakeUserPresets.json`. ...
- decision: C89/C++98 canon, deterministic/no hidden behavior, per-floor artifacts, no CRT mixing, tuple-driven builds, public surface registry, replacement protocol, schema compatibility harness, and the warning that recommendations are not accepted canon yet.

## Representative Source Block References

- PVCB-01058: `docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__05_reader_brief.md`
- PVCB-01833: `docs/archive/conversations/architecture_codex_prompts/dominium_domino_architecture_codex_prompts__05_reader_brief.md`
- PVCB-00112: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-00471: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-01075: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-00856: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__09_in_chat_reader.md`
- PVCB-00473: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- PVCB-01843: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- PVCB-01092: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md`
- PVCB-00114: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md`
- PVCB-01845: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md`
- PVCB-00482: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md`
- PVCB-00483: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md`
- PVCB-01100: `docs/archive/conversations/_reader/by_chat/advanced_simulation_infrastructure.md`
- PVCB-01102: `docs/archive/conversations/_reader/by_chat/advanced_simulation_infrastructure.md`
- PVCB-00865: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01105: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01106: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`

## Block Type Counts

- `constraint`: 102
- `contradiction`: 3
- `decision`: 286
- `design_goal`: 158
- `explanation`: 109
- `prerequisite`: 10
- `prohibition`: 3
- `rationale`: 1
- `rejection`: 2
- `requirement`: 364
- `risk`: 10
- `roadmap`: 123
- `unresolved_question`: 11
