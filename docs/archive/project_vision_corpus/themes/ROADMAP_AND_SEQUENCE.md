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

# Roadmap And Sequence

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

# Roadmap and sequencing

This theme gathers 664 source block(s) from 174 source file(s). It is advisory conversation evidence unless the current repo independently supports the same claim.

## What The Sources Suggest

The clean path is inventory, source selection, theme synthesis, decision triage, targeted promotion, and only then scoped implementation.

## Strongest Recurring Signals

- - 00 manifest: package map. - 01 human-readable report: sections 0-16. - 02 context transfer packet: future-chat handoff. - 03 spec sheet: YAML-style aggregation data. - 04 registers: workstreams, decisions, tasks, constraints, questions, artifacts, risks, verification, timeline, spec contributions. - 05 aggregator packet: compact merge packet. - 06 reader brief: shorter guide. - 07 verification and audit: self-audit...
- The most important thing future readers must not lose is the distinction between **constraints**, **recommendations**, and **accepted canon**. The visible chat clearly establishes the user's desired direction and hard constraints, but many specific implementation mechanisms remain assistant recommendations until accepted.
- **Chat label:** Dominium Build and Future-Proofing Architecture **Date anchor:** 2026-05-27 Australia/Melbourne **Scope:** This report covers the visible conversation and the preservation task that produced the accompanying handoff files. It does **not** claim complete access to any earlier hidden or retired chats. **Epistemic note:** Items marked **FACT** were explicitly present in this conversation or in the provid...
- - This topic matters because it defines the game's construction ambition. The engine must be flexible enough to represent real infrastructure, but the UI must not become a full CAD system. - The rationale is portability and deterministic low-level control. It affects every future implementation prompt. Code generated for the engine must not use C99 features, C++ features, compiler extensions, platform APIs, or undefi...
- - The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The user's question directly made arbitrary placement a major topic. [INFERENCE] The answer was accepted as the current design direction because the user then asked for a Codex prompt plan to implement changes necessary to achieve it. - Finally...
- - The central topic was APP0: the application/runtime/platform/renderer layer of Dominium. This topic came up because the user provided a formal prompt defining what APP0 should do. - The most important conclusion was that APP0 must remain outside the core simulation rules. **FACT:** the user explicitly forbade redesigning simulation rules, altering content definitions, changing life/civilization/economy logic, and i...
- - What remains uncertain is whether the current repository already enforces these boundaries mechanically. The actual code needs inspection. - The unresolved issue is sharding semantics. APP0 requires sharding hooks, but the chat did not decide whether shards are spatial, logical, temporal, jurisdictional, or something else. The report preserved the idea that APP0 can provide sharding plumbing without inventing simul...
- - The user then added a newer versioning model from another chat: product SemVer is manual; build kind is dev/ci/beta/rc/release/hotfix; global build number is only for distributed beta/rc/release/hotfix; build instance ID always exists for dev/ci; channels are separate; all products in a release share the same GBN. This superseded the earlier simpler "build number increments whenever tests pass" model. - The user pr...

## Decision And Review Shape

- decision: - 00 manifest: package map. - 01 human-readable report: sections 0-16. - 02 context transfer packet: future-chat handoff. - 03 spec sheet: YAML-style aggregation data. - 04 registers: workstreams, decisions, tasks, constraints, questions, artifacts, risks, verification, timeline, spec contributions. - 05 aggregator packet: compact merge packet. - 06 reader b...
- decision: The most important thing future readers must not lose is the distinction between **constraints**, **recommendations**, and **accepted canon**. The visible chat clearly establishes the user's desired direction and hard constraints, but many specific implementation mechanisms remain assistant recommendations until accepted.
- decision: **Chat label:** Dominium Build and Future-Proofing Architecture **Date anchor:** 2026-05-27 Australia/Melbourne **Scope:** This report covers the visible conversation and the preservation task that produced the accompanying handoff files. It does **not** claim complete access to any earlier hidden or retired chats. **Epistemic note:** Items marked **FACT** w...
- decision: - This topic matters because it defines the game's construction ambition. The engine must be flexible enough to represent real infrastructure, but the UI must not become a full CAD system. - The rationale is portability and deterministic low-level control. It affects every future implementation prompt. Code generated for the engine must not use C99 features,...
- decision: - The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The user's question directly made arbitrary placement a major topic. [INFERENCE] The answer was accepted as the current design direction because the user then asked for a Codex prompt ...
- decision: - The central topic was APP0: the application/runtime/platform/renderer layer of Dominium. This topic came up because the user provided a formal prompt defining what APP0 should do. - The most important conclusion was that APP0 must remain outside the core simulation rules. **FACT:** the user explicitly forbade redesigning simulation rules, altering content ...
- decision: - What remains uncertain is whether the current repository already enforces these boundaries mechanically. The actual code needs inspection. - The unresolved issue is sharding semantics. APP0 requires sharding hooks, but the chat did not decide whether shards are spatial, logical, temporal, jurisdictional, or something else. The report preserved the idea tha...
- decision: - The user then added a newer versioning model from another chat: product SemVer is manual; build kind is dev/ci/beta/rc/release/hotfix; global build number is only for distributed beta/rc/release/hotfix; build instance ID always exists for dev/ci; channels are separate; all products in a release share the same GBN. This superseded the earlier simpler "build...
- decision: - The user then said the latest docs and code were live at `julesc013/dominium`. The assistant treated the repo as an implementation baseline and observed that AppShell, UI mode resolution, distribution doctrine, and component matrices already existed. This changed the task from inventing a GUI strategy from scratch to reconciling the transfer brief with exi...
- decision: - Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions...

## Representative Source Block References

- PVCB-00856: `docs/archive/conversations/architecture_ui_providers/dominium_architecture_ui_providers_robot_os_strategy__09_in_chat_reader.md`
- PVCB-00085: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md`
- PVCB-00486: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md`
- PVCB-01100: `docs/archive/conversations/_reader/by_chat/advanced_simulation_infrastructure.md`
- PVCB-01102: `docs/archive/conversations/_reader/by_chat/advanced_simulation_infrastructure.md`
- PVCB-01105: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01106: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01107: `docs/archive/conversations/_reader/by_chat/app_testx_codehygiene.md`
- PVCB-01113: `docs/archive/conversations/_reader/by_chat/architecture_ui_providers.md`
- PVCB-00493: `docs/archive/conversations/_reader/by_chat/build_and_future_proofing.md`
- PVCB-00495: `docs/archive/conversations/_reader/by_chat/build_and_future_proofing.md`
- PVCB-01118: `docs/archive/conversations/_reader/by_chat/canonical_structure_and_framework.md`
- PVCB-01121: `docs/archive/conversations/_reader/by_chat/canonical_structure_and_framework.md`
- PVCB-01123: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- PVCB-01125: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- PVCB-01126: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- PVCB-01127: `docs/archive/conversations/_reader/by_chat/development_routes.md`
- PVCB-00866: `docs/archive/conversations/_reader/by_chat/documentation_standards_readme.md`

## Block Type Counts

- `constraint`: 67
- `decision`: 211
- `design_goal`: 83
- `prerequisite`: 3
- `prohibition`: 1
- `requirement`: 146
- `risk`: 2
- `roadmap`: 146
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

# Open decisions

This theme gathers 173 source block(s) from 91 source file(s). It is advisory conversation evidence unless the current repo independently supports the same claim.

## What The Sources Suggest

Open decisions mostly concern scope, sequencing, renderer/UI boundaries, provider/package runtime, domain promotion, and future queue authorization.

## Strongest Recurring Signals

- - never reuse numeric IDs; - never reuse deleted field IDs; - reserve deleted names/fields; - add fields rather than renumbering; - unknown fields round-trip unchanged; - old saves load or explicitly refuse with reason; - new artifacts are not silently accepted by old binaries unless compatible.
- - The answer reframed this as a platform/runtime problem, not just a rendering problem. A visible window requires OS event loops, resize events, close handling, timing, native surface handles, and presentation. Those responsibilities do not belong inside the renderer itself. This led to the proposal of a dedicated **platform runtime layer**. - The key conclusion is that the launcher must not install content or alter ...
- - The central topic was APP0: the application/runtime/platform/renderer layer of Dominium. This topic came up because the user provided a formal prompt defining what APP0 should do. - The most important conclusion was that APP0 must remain outside the core simulation rules. **FACT:** the user explicitly forbade redesigning simulation rules, altering content definitions, changing life/civilization/economy logic, and i...
- - What remains uncertain is whether the current repository already enforces these boundaries mechanically. The actual code needs inspection. - The unresolved issue is sharding semantics. APP0 requires sharding hooks, but the chat did not decide whether shards are spatial, logical, temporal, jurisdictional, or something else. The report preserved the idea that APP0 can provide sharding plumbing without inventing simul...
- - Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions. - The unresolved goals are implementation goals: deciding ...
- - The final state is that this chat became both a design discussion and a packaged source document for future aggregation. - What remains unresolved is the exact mathematical implementation of these frames and how much relativistic fidelity should exist in phase one. - The user asked how to extend calendars beyond planets. The answer was that the larger the scale, the less ordinary calendar structure survives. Sol ca...
- - This reinforced the core celestial-content rule: locations should exist explicitly when they change player decisions. - This became the spatial foundation for later time/calendar decisions because every major body or region could potentially have its own local time, calendar, or operational standard. - The assistant formalized this as the Perfect Earth Calendar, later called HPC-E. The final structure is clear, tho...
- - The assistant formalized this as the Perfect Earth Calendar, later called HPC-E. The final structure is clear, though the exact leap rule remains unresolved. - What remains uncertain is the exact verified object list. The assistant generated a real Milky Way system list, but that list must be checked before becoming data. - The unresolved issue is exact fidelity. The chat specified what should exist conceptually, b...

## Decision And Review Shape

- decision: - never reuse numeric IDs; - never reuse deleted field IDs; - reserve deleted names/fields; - add fields rather than renumbering; - unknown fields round-trip unchanged; - old saves load or explicitly refuse with reason; - new artifacts are not silently accepted by old binaries unless compatible.
- decision: - The answer reframed this as a platform/runtime problem, not just a rendering problem. A visible window requires OS event loops, resize events, close handling, timing, native surface handles, and presentation. Those responsibilities do not belong inside the renderer itself. This led to the proposal of a dedicated **platform runtime layer**. - The key conclu...
- decision: - The central topic was APP0: the application/runtime/platform/renderer layer of Dominium. This topic came up because the user provided a formal prompt defining what APP0 should do. - The most important conclusion was that APP0 must remain outside the core simulation rules. **FACT:** the user explicitly forbade redesigning simulation rules, altering content ...
- decision: - What remains uncertain is whether the current repository already enforces these boundaries mechanically. The actual code needs inspection. - The unresolved issue is sharding semantics. APP0 requires sharding hooks, but the chat did not decide whether shards are spatial, logical, temporal, jurisdictional, or something else. The report preserved the idea tha...
- decision: - Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions...
- decision: - The final state is that this chat became both a design discussion and a packaged source document for future aggregation. - What remains unresolved is the exact mathematical implementation of these frames and how much relativistic fidelity should exist in phase one. - The user asked how to extend calendars beyond planets. The answer was that the larger the ...
- decision: - This reinforced the core celestial-content rule: locations should exist explicitly when they change player decisions. - This became the spatial foundation for later time/calendar decisions because every major body or region could potentially have its own local time, calendar, or operational standard. - The assistant formalized this as the Perfect Earth Cal...
- decision: - The assistant formalized this as the Perfect Earth Calendar, later called HPC-E. The final structure is clear, though the exact leap rule remains unresolved. - What remains uncertain is the exact verified object list. The assistant generated a real Milky Way system list, but that list must be checked before becoming data. - The unresolved issue is exact fi...
- decision: - The key thing to remember: this chat produced the standards and prompts for future work; it did not verify or change the project. The next assistant must inspect the actual repository before writing repo-specific docs, README content, platform claims, license claims, or subsystem descriptions. - `FACT:` The chat established that public API contracts should...
- decision: - The key thing to remember: this chat produced the standards and prompts for future work; it did not verify or change the project. The next assistant must inspect the actual repository before writing repo-specific docs, README content, platform claims, license claims, or subsystem descriptions. - The chat began with the user asking how to have Codex generat...

## Representative Source Block References

- PVCB-00086: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md`
- PVCB-00865: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01105: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01106: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-00495: `docs/archive/conversations/_reader/by_chat/build_and_future_proofing.md`
- PVCB-01123: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- PVCB-01125: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- PVCB-01126: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- PVCB-00866: `docs/archive/conversations/_reader/by_chat/documentation_standards_readme.md`
- PVCB-01695: `docs/archive/conversations/_reader/by_chat/documentation_standards_readme.md`
- PVCB-01131: `docs/archive/conversations/_reader/by_chat/dominium_architecture_i.md`
- PVCB-01141: `docs/archive/conversations/_reader/by_chat/dominium_architecture_iii.md`
- PVCB-01143: `docs/archive/conversations/_reader/by_chat/dominium_architecture_iv.md`
- PVCB-01147: `docs/archive/conversations/_reader/by_chat/dominium_architecture_iv.md`
- PVCB-00506: `docs/archive/conversations/_reader/by_chat/dominium_complete_conversation.md`
- PVCB-01154: `docs/archive/conversations/_reader/by_chat/dominium_domino_codex_planning.md`
- PVCB-01159: `docs/archive/conversations/_reader/by_chat/dominium_setup.md`
- PVCB-00145: `docs/archive/conversations/_reader/by_chat/domino_engine_refactor_prompts.md`

## Block Type Counts

- `constraint`: 8
- `decision`: 95
- `design_goal`: 19
- `prohibition`: 2
- `requirement`: 27
- `unresolved_question`: 22

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

# Contradictions and stale claims

This theme gathers 210 source block(s) from 105 source file(s). It is advisory conversation evidence unless the current repo independently supports the same claim.

## What The Sources Suggest

Drift appears when older ambition sounds implementation-ready or authoritative despite current queue and authority constraints.

## Strongest Recurring Signals

- This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-floor binaries are mandatory and that support cannot be claimed...
- 1. Which recommendations here should become binding canon? 2. Which should remain advisory until more evidence exists? 3. Write the implementation prompt for `STRUCTURE-01: Public Surface Registry`. 4. Write the implementation prompt for `BUILD-CONTRACT-01: Tuple Build Contracts and Machine Probe`. 5. Verify the current repo state and compare it to the older POST-CONVERGE-09 state. 6. Turn the candidate requirements ...
- - This topic matters because it defines the game's construction ambition. The engine must be flexible enough to represent real infrastructure, but the UI must not become a full CAD system. - The rationale is portability and deterministic low-level control. It affects every future implementation prompt. Code generated for the engine must not use C99 features, C++ features, compiler extensions, platform APIs, or undefi...
- - The answer reframed this as a platform/runtime problem, not just a rendering problem. A visible window requires OS event loops, resize events, close handling, timing, native surface handles, and presentation. Those responsibilities do not belong inside the renderer itself. This led to the proposal of a dedicated **platform runtime layer**. - The key conclusion is that the launcher must not install content or alter ...
- - The user then added a newer versioning model from another chat: product SemVer is manual; build kind is dev/ci/beta/rc/release/hotfix; global build number is only for distributed beta/rc/release/hotfix; build instance ID always exists for dev/ci; channels are separate; all products in a release share the same GBN. This superseded the earlier simpler "build number increments whenever tests pass" model. - The user pr...
- - Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions. - The unresolved goals are implementation goals: deciding ...
- - Packs are distributable authored payloads. The preferred pack layout became category-based, such as `content/packs/<category>/<pack_id>/`. Pack IDs must not depend on paths. Saves and replays must use stable IDs, schema versions, canonical serialization, deterministic hashes, and explicit migration/refusal policies. Backward compatibility must be a compatibility corpus plus tests, not intention. - The framework-bou...
- - INFERENCE: The user wanted a durable method for deciding future structure changes, not just a one-time layout. They also wanted the assistant to become more rigorous: distinguish decisions from brainstorms, stop over-planning without execution, and preserve uncertainty. The user also wanted a structure that supports other Domino-based games and possibly different engine implementations. - A persistent uncertainty i...

## Decision And Review Shape

- decision: This topic came up because the user needed Dominium to build across many Windows floors and historical toolchains without accidental capability drift. The chat discussed VS2022 as a host for older toolsets, v141/v141_xp, Windows SDK pinning, XP and Win7 runtime proof, and later archival toolchains such as VC7.1 or VC6. The visible conclusion was that per-flo...
- decision: 1. Which recommendations here should become binding canon? 2. Which should remain advisory until more evidence exists? 3. Write the implementation prompt for `STRUCTURE-01: Public Surface Registry`. 4. Write the implementation prompt for `BUILD-CONTRACT-01: Tuple Build Contracts and Machine Probe`. 5. Verify the current repo state and compare it to the older...
- decision: - This topic matters because it defines the game's construction ambition. The engine must be flexible enough to represent real infrastructure, but the UI must not become a full CAD system. - The rationale is portability and deterministic low-level control. It affects every future implementation prompt. Code generated for the engine must not use C99 features,...
- decision: - The answer reframed this as a platform/runtime problem, not just a rendering problem. A visible window requires OS event loops, resize events, close handling, timing, native surface handles, and presentation. Those responsibilities do not belong inside the renderer itself. This led to the proposal of a dedicated **platform runtime layer**. - The key conclu...
- decision: - The user then added a newer versioning model from another chat: product SemVer is manual; build kind is dev/ci/beta/rc/release/hotfix; global build number is only for distributed beta/rc/release/hotfix; build instance ID always exists for dev/ci; channels are separate; all products in a release share the same GBN. This superseded the earlier simpler "build...
- decision: - Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions...
- decision: - Packs are distributable authored payloads. The preferred pack layout became category-based, such as `content/packs/<category>/<pack_id>/`. Pack IDs must not depend on paths. Saves and replays must use stable IDs, schema versions, canonical serialization, deterministic hashes, and explicit migration/refusal policies. Backward compatibility must be a compati...
- decision: - INFERENCE: The user wanted a durable method for deciding future structure changes, not just a one-time layout. They also wanted the assistant to become more rigorous: distinguish decisions from brainstorms, stop over-planning without execution, and preserve uncertainty. The user also wanted a structure that supports other Domino-based games and possibly di...
- decision: - The conclusion was that inhabited or operationally important bodies may have local calendars or clocks, but those calendars should still be renderers over physical time. Gas giants and the Sun do not get ordinary civil calendars, because civilizations do not live on their surfaces. Habitats around them may define their own standards. - The player initially...
- decision: - The current user request refines that again. The user now explicitly says they do not want another machine-readable handoff, YAML spec sheet, register dump, or file index. They want a human-readable narrative report explaining the whole chat in plain language. That is the purpose of this report. - The first was **content-first development**. This means bui...

## Representative Source Block References

- PVCB-00477: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- PVCB-00483: `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md`
- PVCB-01100: `docs/archive/conversations/_reader/by_chat/advanced_simulation_infrastructure.md`
- PVCB-00865: `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md`
- PVCB-01107: `docs/archive/conversations/_reader/by_chat/app_testx_codehygiene.md`
- PVCB-00495: `docs/archive/conversations/_reader/by_chat/build_and_future_proofing.md`
- PVCB-01118: `docs/archive/conversations/_reader/by_chat/canonical_structure_and_framework.md`
- PVCB-01121: `docs/archive/conversations/_reader/by_chat/canonical_structure_and_framework.md`
- PVCB-01122: `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- PVCB-01127: `docs/archive/conversations/_reader/by_chat/development_routes.md`
- PVCB-01852: `docs/archive/conversations/_reader/by_chat/documentation_standards_readme.md`
- PVCB-01131: `docs/archive/conversations/_reader/by_chat/dominium_architecture_i.md`
- PVCB-01137: `docs/archive/conversations/_reader/by_chat/dominium_architecture_iii.md`
- PVCB-01142: `docs/archive/conversations/_reader/by_chat/dominium_architecture_iv.md`
- PVCB-01143: `docs/archive/conversations/_reader/by_chat/dominium_architecture_iv.md`
- PVCB-01147: `docs/archive/conversations/_reader/by_chat/dominium_architecture_iv.md`
- PVCB-01153: `docs/archive/conversations/_reader/by_chat/dominium_domino_codex_planning.md`
- PVCB-01158: `docs/archive/conversations/_reader/by_chat/dominium_full_conversation.md`

## Block Type Counts

- `constraint`: 7
- `contradiction`: 3
- `decision`: 100
- `design_goal`: 37
- `explanation`: 2
- `prerequisite`: 2
- `prohibition`: 1
- `rejection`: 2
- `requirement`: 50
- `risk`: 1
- `roadmap`: 5
