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

# World And Simulation

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

# World model, time, space, and scale

This theme gathers 665 source block(s) from 160 source file(s). It is advisory conversation evidence unless the current repo independently supports the same claim.

## What The Sources Suggest

World, time, scale, and existence themes point toward a simulation model that can refine detail while preserving authoritative truth.

## Strongest Recurring Signals

- - APP0 scope is application/runtime/platform/render only. - Engine + game remain authoritative. - Applications are orchestrators, not decision-makers. - Rendering never affects simulation. - Client is non-authoritative. - Server is authoritative and headless-capable. - Launcher must not install content or alter simulation state. - Setup owns install/version/integrity responsibilities. - Tools must obey authority/law ...
- The user stated that the project had transitioned to C17 and C++17 and raised minimum systems to Windows 7 SP1, Mac OS X 10.9.5, and Linux. The visible conclusion was to use C17 for ABI-facing law-like structures, packets, fixed-width types, deterministic math, save/replay records, and low-level facades; C++17 for runtime machinery, provider implementations, Workbench, apps, resource ownership, and orchestration. Pub...
- - 00 manifest: package map. - 01 human-readable report: sections 0-16. - 02 context transfer packet: future-chat handoff. - 03 spec sheet: YAML-style aggregation data. - 04 registers: workstreams, decisions, tasks, constraints, questions, artifacts, risks, verification, timeline, spec contributions. - 05 aggregator packet: compact merge packet. - 06 reader brief: shorter guide. - 07 verification and audit: self-audit...
- This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-floor binaries are mandatory and that support cannot be claimed...
- - The answer reframed this as a platform/runtime problem, not just a rendering problem. A visible window requires OS event loops, resize events, close handling, timing, native surface handles, and presentation. Those responsibilities do not belong inside the renderer itself. This led to the proposal of a dedicated **platform runtime layer**. - The key conclusion is that the launcher must not install content or alter ...
- This chat was mainly about the **Dominium / Domino project's application and runtime layer**, referred to throughout as **APP0**. The user began by giving a large implementation-oriented prompt titled **"PROMPT APP0 - RUNTIMES, APPLICATIONS, PLATFORMS & RENDERERS."** That prompt defined a strict scope: work on the **client, server, launcher, setup/installer, tools, renderers, and platform support**, while not redesig...
- - The central topic was APP0: the application/runtime/platform/renderer layer of Dominium. This topic came up because the user provided a formal prompt defining what APP0 should do. - The most important conclusion was that APP0 must remain outside the core simulation rules. **FACT:** the user explicitly forbade redesigning simulation rules, altering content definitions, changing life/civilization/economy logic, and i...
- - The user then added a newer versioning model from another chat: product SemVer is manual; build kind is dev/ci/beta/rc/release/hotfix; global build number is only for distributed beta/rc/release/hotfix; build instance ID always exists for dev/ci; channels are separate; all products in a release share the same GBN. This superseded the earlier simpler "build number increments whenever tests pass" model. - The user pr...

## Decision And Review Shape

- decision: - APP0 scope is application/runtime/platform/render only. - Engine + game remain authoritative. - Applications are orchestrators, not decision-makers. - Rendering never affects simulation. - Client is non-authoritative. - Server is authoritative and headless-capable. - Launcher must not install content or alter simulation state. - Setup owns install/version/...
- decision: The user stated that the project had transitioned to C17 and C++17 and raised minimum systems to Windows 7 SP1, Mac OS X 10.9.5, and Linux. The visible conclusion was to use C17 for ABI-facing law-like structures, packets, fixed-width types, deterministic math, save/replay records, and low-level facades; C++17 for runtime machinery, provider implementations,...
- decision: - 00 manifest: package map. - 01 human-readable report: sections 0-16. - 02 context transfer packet: future-chat handoff. - 03 spec sheet: YAML-style aggregation data. - 04 registers: workstreams, decisions, tasks, constraints, questions, artifacts, risks, verification, timeline, spec contributions. - 05 aggregator packet: compact merge packet. - 06 reader b...
- decision: This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-flo...
- decision: - The answer reframed this as a platform/runtime problem, not just a rendering problem. A visible window requires OS event loops, resize events, close handling, timing, native surface handles, and presentation. Those responsibilities do not belong inside the renderer itself. This led to the proposal of a dedicated **platform runtime layer**. - The key conclu...
- decision: This chat was mainly about the **Dominium / Domino project's application and runtime layer**, referred to throughout as **APP0**. The user began by giving a large implementation-oriented prompt titled **"PROMPT APP0 - RUNTIMES, APPLICATIONS, PLATFORMS & RENDERERS."** That prompt defined a strict scope: work on the **client, server, launcher, setup/installer,...
- decision: - The central topic was APP0: the application/runtime/platform/renderer layer of Dominium. This topic came up because the user provided a formal prompt defining what APP0 should do. - The most important conclusion was that APP0 must remain outside the core simulation rules. **FACT:** the user explicitly forbade redesigning simulation rules, altering content ...
- decision: - The user then added a newer versioning model from another chat: product SemVer is manual; build kind is dev/ci/beta/rc/release/hotfix; global build number is only for distributed beta/rc/release/hotfix; build instance ID always exists for dev/ci; channels are separate; all products in a release share the same GBN. This superseded the earlier simpler "build...
- decision: - Packs are distributable authored payloads. The preferred pack layout became category-based, such as `content/packs/<category>/<pack_id>/`. Pack IDs must not depend on paths. Saves and replays must use stable IDs, schema versions, canonical serialization, deterministic hashes, and explicit migration/refusal policies. Backward compatibility must be a compati...
- decision: - INFERENCE: The user wanted a durable method for deciding future structure changes, not just a one-time layout. They also wanted the assistant to become more rigorous: distinguish decisions from brainstorms, stop over-planning without execution, and preserve uncertainty. The user also wanted a structure that supports other Domino-based games and possibly di...

## Representative Source Block References

- PVCB-01058: `docs/archive/conversations/app_runtime_platform_renderers/dominium_app0_runtime_platform_renderers__05_reader_brief.md`
- PVCB-00112: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-00856: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__09_in_chat_reader.md`
- PVCB-00477: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- PVCB-00865: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01104: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01105: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01107: `docs/archive/conversations/_reader/by_chat/app_testx_codehygiene.md`
- PVCB-01118: `docs/archive/conversations/_reader/by_chat/canonical_structure_and_framework.md`
- PVCB-01121: `docs/archive/conversations/_reader/by_chat/canonical_structure_and_framework.md`
- PVCB-01122: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- PVCB-01123: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- PVCB-01124: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- PVCB-01125: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- PVCB-01126: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- PVCB-01127: `docs/archive/conversations/_reader/by_chat/development_routes.md`
- PVCB-00866: `docs/archive/conversations/_reader/by_chat/documentation_standards_readme.md`
- PVCB-01131: `docs/archive/conversations/_reader/by_chat/dominium_architecture_i.md`

## Block Type Counts

- `constraint`: 64
- `contradiction`: 2
- `decision`: 155
- `design_goal`: 124
- `explanation`: 34
- `prerequisite`: 5
- `prohibition`: 4
- `requirement`: 224
- `risk`: 1
- `roadmap`: 49
- `unresolved_question`: 3

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

# Worldgen, planets, celestial systems, and domains

This theme gathers 227 source block(s) from 91 source file(s). It is advisory conversation evidence unless the current repo independently supports the same claim.

## What The Sources Suggest

Worldgen and celestial systems are long-horizon domain ambitions that need source verification and contract scoping before implementation.

## Strongest Recurring Signals

- - The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The user's question directly made arbitrary placement a major topic. [INFERENCE] The answer was accepted as the current design direction because the user then asked for a Codex prompt plan to implement changes necessary to achieve it. - Finally...
- - The conclusion was that inhabited or operationally important bodies may have local calendars or clocks, but those calendars should still be renderers over physical time. Gas giants and the Sun do not get ordinary civil calendars, because civilizations do not live on their surfaces. Habitats around them may define their own standards. - The player initially has no time/date HUD because they do not possess clocks, ca...
- - The final state is that this chat became both a design discussion and a packaged source document for future aggregation. - What remains unresolved is the exact mathematical implementation of these frames and how much relativistic fidelity should exist in phase one. - The user asked how to extend calendars beyond planets. The answer was that the larger the scale, the less ordinary calendar structure survives. Sol ca...
- A central design theme emerged: not everything should be simulated at the same fidelity. The Sol system should be represented in great detail because the user explicitly said most playtime will happen there. The Milky Way should have a backbone of real, named systems and sites, plus procedural expansion. The universe should mostly be parametric or abstract, using large-scale structures like filaments, voids, horizons...
- - This reinforced the core celestial-content rule: locations should exist explicitly when they change player decisions. - This became the spatial foundation for later time/calendar decisions because every major body or region could potentially have its own local time, calendar, or operational standard. - The assistant formalized this as the Perfect Earth Calendar, later called HPC-E. The final structure is clear, tho...
- - The assistant formalized this as the Perfect Earth Calendar, later called HPC-E. The final structure is clear, though the exact leap rule remains unresolved. - What remains uncertain is the exact verified object list. The assistant generated a real Milky Way system list, but that list must be checked before becoming data. - The unresolved issue is exact fidelity. The chat specified what should exist conceptually, b...
- - The conclusions were clear: future code must not bypass dsys or dgfx, deterministic sim must not use host floating-point, product code should not directly call OS APIs, and old content must not silently break. These are not just preferences; they are the governing rules of the project. - The most important rejected idea was trying to build the entire architecture at once. It was not rejected because it was wrong; i...
- - FACT:** The Domino engine must be ISO C89. The Dominium UI/tools layer must be portable C++98. Engine code must not use OS APIs. Determinism matters, so floats are disallowed in deterministic paths. The engine must avoid platform-dependent behavior and hardcoded game semantics. Everything should be content-driven. - Once the architecture stabilized, the user asked for a plan of prompts to give Codex. The assistant ...

## Decision And Review Shape

- decision: - The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The user's question directly made arbitrary placement a major topic. [INFERENCE] The answer was accepted as the current design direction because the user then asked for a Codex prompt ...
- decision: - The conclusion was that inhabited or operationally important bodies may have local calendars or clocks, but those calendars should still be renderers over physical time. Gas giants and the Sun do not get ordinary civil calendars, because civilizations do not live on their surfaces. Habitats around them may define their own standards. - The player initially...
- decision: - The final state is that this chat became both a design discussion and a packaged source document for future aggregation. - What remains unresolved is the exact mathematical implementation of these frames and how much relativistic fidelity should exist in phase one. - The user asked how to extend calendars beyond planets. The answer was that the larger the ...
- decision: A central design theme emerged: not everything should be simulated at the same fidelity. The Sol system should be represented in great detail because the user explicitly said most playtime will happen there. The Milky Way should have a backbone of real, named systems and sites, plus procedural expansion. The universe should mostly be parametric or abstract, ...
- decision: - This reinforced the core celestial-content rule: locations should exist explicitly when they change player decisions. - This became the spatial foundation for later time/calendar decisions because every major body or region could potentially have its own local time, calendar, or operational standard. - The assistant formalized this as the Perfect Earth Cal...
- decision: - The assistant formalized this as the Perfect Earth Calendar, later called HPC-E. The final structure is clear, though the exact leap rule remains unresolved. - What remains uncertain is the exact verified object list. The assistant generated a real Milky Way system list, but that list must be checked before becoming data. - The unresolved issue is exact fi...
- decision: - The conclusions were clear: future code must not bypass dsys or dgfx, deterministic sim must not use host floating-point, product code should not directly call OS APIs, and old content must not silently break. These are not just preferences; they are the governing rules of the project. - The most important rejected idea was trying to build the entire archi...
- decision: - FACT:** The Domino engine must be ISO C89. The Dominium UI/tools layer must be portable C++98. Engine code must not use OS APIs. Determinism matters, so floats are disallowed in deterministic paths. The engine must avoid platform-dependent behavior and hardcoded game semantics. Everything should be content-driven. - Once the architecture stabilized, the us...
- decision: - The topic came up because the project needed a model that could support world simulation, modding, tooling, Workbench, release, portability, and future games without repeating endless refactors. The conclusion was that stable contracts and semantic IDs must be separated from replaceable private implementation. - Workbench is a future product surface, not t...
- decision: An assistant initially rewrote that prompt into a cleaner Codex-ready form. The user then corrected the process: **before generating prompts, the group needed to discuss the design.** That changed the status of the rewritten prompt. It became a useful draft, not an accepted final artifact. The later discussion identified several conceptual holes in CONTENT0 ...

## Representative Source Block References

- PVCB-01102: `docs/archive/conversations/_reader/by_chat/advanced_simulation_infrastructure.md`
- PVCB-01122: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- PVCB-01123: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- PVCB-01124: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- PVCB-01125: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- PVCB-01126: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- PVCB-01153: `docs/archive/conversations/_reader/by_chat/dominium_domino_codex_planning.md`
- PVCB-01165: `docs/archive/conversations/_reader/by_chat/domino_engine_refactor_prompts.md`
- PVCB-01175: `docs/archive/conversations/_reader/by_chat/foundation_workbench_codex.md`
- PVCB-00150: `docs/archive/conversations/_reader/by_chat/gui_binary_content.md`
- PVCB-00868: `docs/archive/conversations/_reader/by_chat/gui_binary_content.md`
- PVCB-00156: `docs/archive/conversations/_reader/by_chat/os_interface_repo_architecture.md`
- PVCB-01206: `docs/archive/conversations/_reader/by_chat/os_interface_repo_architecture.md`
- PVCB-01245: `docs/archive/conversations/_reader/by_chat/world_architecture.md`
- PVCB-01247: `docs/archive/conversations/_reader/by_chat/xstack_lab_galaxy.md`
- PVCB-01279: `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md`
- PVCB-00226: `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md`
- PVCB-01324: `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md`

## Block Type Counts

- `constraint`: 15
- `decision`: 55
- `design_goal`: 57
- `explanation`: 13
- `rationale`: 1
- `requirement`: 64
- `risk`: 3
- `roadmap`: 16
- `unresolved_question`: 3

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

# Civilization, economy, logistics, institutions, and signals

This theme gathers 105 source block(s) from 51 source file(s). It is advisory conversation evidence unless the current repo independently supports the same claim.

## What The Sources Suggest

Civilization, economy, logistics, institutions, and signals are recurring target phenomena for emergent lawful simulation.

## Strongest Recurring Signals

- The immediate game-design plan is to formalize the robotic seed-civilisation doctrine into a spec chapter and choose a first gameplay loop, likely survey -> mine -> refine -> fabricate -> build simple power/logistics/spawn infrastructure.
- - The central topic was APP0: the application/runtime/platform/renderer layer of Dominium. This topic came up because the user provided a formal prompt defining what APP0 should do. - The most important conclusion was that APP0 must remain outside the core simulation rules. **FACT:** the user explicitly forbade redesigning simulation rules, altering content definitions, changing life/civilization/economy logic, and i...
- - The conclusion was that inhabited or operationally important bodies may have local calendars or clocks, but those calendars should still be renderers over physical time. Gas giants and the Sun do not get ordinary civil calendars, because civilizations do not live on their surfaces. Habitats around them may define their own standards. - The player initially has no time/date HUD because they do not possess clocks, ca...
- - The second central decision is that CLI, TUI, rendered GUI, OS-native GUI, and headless automation must be **projections of the same command/result/refusal/document/view spine**. A GUI button, a TUI hotkey, a CLI command, a headless JSON job, and a future OS-native widget action should route through the same command/service path and produce the same typed result, diagnostics, refusals, logs, and evidence. - The res...
- An assistant initially rewrote that prompt into a cleaner Codex-ready form. The user then corrected the process: **before generating prompts, the group needed to discuss the design.** That changed the status of the rewritten prompt. It became a useful draft, not an accepted final artifact. The later discussion identified several conceptual holes in CONTENT0 that would need resolving before any final prompt should dri...
- - For a future assistant or human reader, the key thing to understand is that the chat did not reject Unreal. It rejected the idea that Unreal or UE6 could be the complete solution. The direction is hybrid: custom simulation and backend as the real engine, Unreal as the first high-quality client, UE6 as a possible future upgrade, and Domino as a possible later frontend/runtime if the core remains portable. - Conclusi...
- - This changed the future plan from "eventually implement everything" to "first prove seamless lawful inspection/materialization at universe scale." - The current preservation task then asked for this full chat package. - A major theme was that useful local inventions must become portable, standardized, industrialized, and institutionally adopted. The repo now has a Formalization Chain spec and Player Desire Acceptan...
- - Foundation lock status signal: `PASS_WITH_WARNINGS`. - Current blocked queue scopes: `broad_workbench_ui`, `gameplay`, `native_gui`, `package_runtime`, `provider_runtime`, `release_publication`, `renderer_implementation`, `runtime_module_loader`. - Safe now: archive reading, decision review, promotion review, reconciliation crosswalks, docs-only microtask preparation, and validators. - Not safe now: implementation ...

## Decision And Review Shape

- decision: The immediate game-design plan is to formalize the robotic seed-civilisation doctrine into a spec chapter and choose a first gameplay loop, likely survey -> mine -> refine -> fabricate -> build simple power/logistics/spawn infrastructure.
- decision: - The central topic was APP0: the application/runtime/platform/renderer layer of Dominium. This topic came up because the user provided a formal prompt defining what APP0 should do. - The most important conclusion was that APP0 must remain outside the core simulation rules. **FACT:** the user explicitly forbade redesigning simulation rules, altering content ...
- decision: - The conclusion was that inhabited or operationally important bodies may have local calendars or clocks, but those calendars should still be renderers over physical time. Gas giants and the Sun do not get ordinary civil calendars, because civilizations do not live on their surfaces. Habitats around them may define their own standards. - The player initially...
- decision: - The second central decision is that CLI, TUI, rendered GUI, OS-native GUI, and headless automation must be **projections of the same command/result/refusal/document/view spine**. A GUI button, a TUI hotkey, a CLI command, a headless JSON job, and a future OS-native widget action should route through the same command/service path and produce the same typed ...
- decision: An assistant initially rewrote that prompt into a cleaner Codex-ready form. The user then corrected the process: **before generating prompts, the group needed to discuss the design.** That changed the status of the rewritten prompt. It became a useful draft, not an accepted final artifact. The later discussion identified several conceptual holes in CONTENT0 ...
- decision: - For a future assistant or human reader, the key thing to understand is that the chat did not reject Unreal. It rejected the idea that Unreal or UE6 could be the complete solution. The direction is hybrid: custom simulation and backend as the real engine, Unreal as the first high-quality client, UE6 as a possible future upgrade, and Domino as a possible lat...
- decision: - This changed the future plan from "eventually implement everything" to "first prove seamless lawful inspection/materialization at universe scale." - The current preservation task then asked for this full chat package. - A major theme was that useful local inventions must become portable, standardized, industrialized, and institutionally adopted. The repo n...
- decision: - Foundation lock status signal: `PASS_WITH_WARNINGS`. - Current blocked queue scopes: `broad_workbench_ui`, `gameplay`, `native_gui`, `package_runtime`, `provider_runtime`, `release_publication`, `renderer_implementation`, `runtime_module_loader`. - Safe now: archive reading, decision review, promotion review, reconciliation crosswalks, docs-only microtask ...
- decision: - Decision docket items: `30`. - `Workbench/AIDE/Codex/tooling`: `6`. - `architecture/boundaries`: `12`. - `provider/content/packs`: `5`. - `release/setup/launcher`: `2`. - `renderer/UI/platform`: `3`. - `world/time/civilization simulation`: `2`.
- decision: - Source promotion/claim IDs: `blocked_scope:broad_workbench_ui` - Source conversations: `current queue plus conversation audit findings` - Question: Should `broad_workbench_ui` remain blocked for all conversation-derived work until a future reviewed queue phase opens it? - Why it matters: The current queue marks `broad_workbench_ui` as `BLOCKED` and the cor...

## Representative Source Block References

- PVCB-01076: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__01_human_readable_report.md`
- PVCB-01105: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01122: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- PVCB-01163: `docs/archive/conversations/_reader/by_chat/domino_dominium_workbench.md`
- PVCB-00150: `docs/archive/conversations/_reader/by_chat/gui_binary_content.md`
- PVCB-01233: `docs/archive/conversations/_reader/by_chat/ue6_domino_deterministic_universe.md`
- PVCB-00872: `docs/archive/conversations/_reader/by_chat/universe_explorer_planning.md`
- PVCB-01288: `docs/archive/conversations/_synthesis/CURRENT_PROJECT_ATLAS_v0.md`
- PVCB-01871: `docs/archive/conversations/_synthesis/CURRENT_PROJECT_ATLAS_v0.md`
- PVCB-00204: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`
- PVCB-00205: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`
- PVCB-00206: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`
- PVCB-00207: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`
- PVCB-00208: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`
- PVCB-00209: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`
- PVCB-00210: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`
- PVCB-01295: `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`
- PVCB-01297: `docs/archive/conversations/_decision/DECISION_SUMMARY_v0.md`

## Block Type Counts

- `constraint`: 13
- `decision`: 31
- `design_goal`: 16
- `explanation`: 2
- `prerequisite`: 1
- `requirement`: 34
- `roadmap`: 7
- `unresolved_question`: 1
