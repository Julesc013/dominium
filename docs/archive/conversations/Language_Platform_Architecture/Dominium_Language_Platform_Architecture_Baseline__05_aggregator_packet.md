# Aggregator Packet — Dominium Language, Platform, and Architecture Baseline

## Packet Metadata

* Chat label: Dominium Language, Platform, and Architecture Baseline
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: this chat only, repo/project context labelled
* Coverage: partial-to-high for visible chat
* Confidence: 4/5
* Staleness risk: medium
* Merge priority: high
* Main limitations: external toolchain facts need verification; other old chats not fully reconstructed here

## Ultra-Condensed Carry-Forward Capsule

This chat was a design-decision and architecture-baseline discussion for Dominium, focused on language standards, platform floors, binary architecture, portability strategy, and the project’s long-term modular structure. The user began by asking whether Dominium would gain performance or features by moving beyond the earlier C89 engine and C++98 game plan. Over the conversation, the topic expanded into a full re-evaluation of what should be written in C versus C++, what standards should define the mainline, which operating systems should still count as full native targets, and how old or exotic systems should be supported without distorting the modern architecture.

The most important evolution was away from the crude split “engine = C, game = C++.” The better rule that emerged was semantic: C should own stable law, ABI, fixed-width data, serialization, replay, packets, renderer command IR, and deterministic primitives; C++ should own resource-heavy machinery, runtime services, providers, apps, game orchestration, tools, Workbench, and composition. This is the central idea to preserve. The project does not need pure C, pure C++, or a language ideology. It needs stable contracts at the boundaries and modern implementation power internally.

The user initially considered staged old-to-new plans: versions 0.x/1.x using C89/C++98 and later versions moving to C11/C++17. That plan was superseded as the user accepted a more decisive baseline: C17 and C++17 across the mainline, with 64-bit source-native builds and little-endian assumptions. The old C89/C++98 goal moved from active mainline law into retro/projection/archive thinking. The current repo state discussed in the chat supports this: root and engine CMake were observed as already requiring C17/C++17, while the repository still contains documentation and comments that should be updated to match the new doctrine.

The chat also clarified portability. The user wanted future support for Windows XP, Windows 98, Mac OS X 10.6, Mac OS 9.2, Android, iOS, PS5, Xbox, and Switch. The answer was not to pretend one primitive binary can execute everywhere. The correct model is one canonical project with contracts, content, tests, deterministic law, C-compatible ABI, and renderer/platform/provider interfaces, then multiple products or projections: full 64-bit source-native builds for modern supported systems, constrained native builds for some older environments, contract projections for extreme legacy systems, and archive/emulator lanes for museum targets.

Another major thread was modularity. The user wanted code, data, modules, packs, tools, apps, and Workbench to integrate cleanly and be reusable. The answer became a contract-centered composition model: apps compose modules; modules require services; services are implemented by providers; providers declare capabilities; packs provide data/modules/content; profiles select packs/settings; contracts define compatibility; lockfiles make composition reproducible; commands invoke behavior; artifacts record results; tests prove it; Workbench operates it; AIDE governs it. This is the most future-proof part of the design, but it also revealed missing pieces: a composition resolver, lockfiles, compatibility corpus, trust/permission model, virtual filesystem/root model, performance budgets, and a public-surface promotion protocol.

The final state of the chat was not “done.” It reached a coherent architecture direction, but the latest project state said Foundation Lock was blocked by dependency-direction strict validation failures: 358 violations and 38 warnings. Therefore, the immediate next step is not more Workbench UI, renderer work, or gameplay expansion. It is FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01: classify and repair those dependency-direction violations, then rerun Foundation Closeout. Only after that should WORKBENCH-VALIDATION-SLICE-01 begin.

The top aggregation message is: Dominium should formalize C17 + C++17 + 64-bit + little-endian as its source-native mainline, while preserving C-compatible ABI/data contracts and deterministic law. This chat is the strongest source for the language/platform/ABI/portability decision sequence and for the semantic split between C and C++. It also contributes the integration model where apps compose modules, modules require services, services are implemented by providers, packs provide data/modules/content, profiles select packs/settings, contracts define compatibility, lockfiles make selection reproducible, commands invoke behavior, artifacts record results, tests prove it, Workbench operates it, and AIDE governs it.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | Repair dependency-direction strict blocker | task | TASK-01 | Foundation Lock and Workbench authorization depend on it. | FACT | 5 |
| P0 | C17 + C++17 mainline | decision | DECISION-01 | Sets source baseline and supersedes old C89/C++98/pure C99/pure C++11 directions. | FACT/INFERENCE | 4 |
| P0 | C-compatible ABI forever | decision | DECISION-04 | Keeps implementation replaceable and tools/providers/projections viable. | FACT | 5 |
| P0 | C law / C++ machinery split | decision | DECISION-05 | Prevents arbitrary language/folder choices. | FACT/INFERENCE | 4 |
| P1 | Composition resolver + lockfiles | missing system | WORKSTREAM-07 | Needed for real modularity/reproducibility. | INFERENCE | 4 |

## Workstream Summaries

| ID | Name | Objective | Current state | Desired end state | Priority | Status |
| --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Language and architecture baseline | Set the active implementation language and machine baseline for the mainline project. | C17/C++17 and 64-bit source-native direction accepted in the discussion; repo CMake now reflects C17/C++17. | Clear mainline baseline: C17/C++17, x86_64/arm64, little-endian, C-compatible ABI. | P0 | active |
| WORKSTREAM-02 | C/C++ responsibility split | Define what belongs in C and what belongs in C++. | Repeatedly refined from engine=C/game=C++ to law=C and machinery=C++. | C17 owns stable law and ABI; C++17 owns orchestration, providers, apps, Workbench, and tools. | P0 | active |
| WORKSTREAM-03 | ABI and public surface governance | Prevent C++ implementation details from becoming permanent binary/data contracts. | Existing ABI header is POD/extern-C/return-code oriented but old wording remains. | C-compatible ABI, POD-only, versioned, no STL/classes/exceptions/RTTI across stable boundaries. | P0 | active |
| WORKSTREAM-04 | Determinism and scheduler law | Preserve replayable, platform-independent simulation behavior. | Specs already define stable IDs, canonical order, fixed-point, no OS time/thread timing as truth. | Language migration does not weaken determinism; rules remain enforced by tests/contracts. | P0 | active |
| WORKSTREAM-05 | Repository boundaries and Foundation Lock | Clean dependency direction and prove the foundation before product work. | Foundation Lock is blocked by dependency-direction strict failures: 358 violations and 38 warnings. | Dependency-direction validator green; Foundation Lock closed; Workbench slice authorized. | P0 | blocked |
| WORKSTREAM-06 | Provider/capability runtime model | Make render/platform/storage/network/audio/input backends replaceable and explicit. | Component matrices exist; many backends are available/stub/planned/research. | Providers declare capabilities, refusals, fallback, conformance tests, and determinism impact. | P1 | active |
| WORKSTREAM-07 | Composition resolver and lockfiles | Make modular packs/modules/providers/apps reproducible instead of manually wired. | Identified as the major missing integration layer. | One resolver selects packs/modules/providers and emits lockfiles/evidence/refusals. | P1 | missing |
| WORKSTREAM-08 | Packs/modules/content/trust | Support extensible authored data and modules without unsafe plugin sprawl. | Vocabulary clarified: pack, module, provider, service, component, workspace, app, artifact. | Packs and modules have descriptors, trust/permission rules, validation fixtures, and overlay/conflict law. | P1 | active |
| WORKSTREAM-09 | Workbench and AIDE operating model | Use Workbench as command/evidence surface and AIDE as repo control-plane. | Plan says Workbench is not authority and must use same command/service/result/refusal spine as CLI/tests. | Workbench validates via registered commands; AIDE governs with task/evidence packets and validators. | P1 | active |
| WORKSTREAM-10 | Legacy and platform support tiers | Support older systems without letting them govern mainline architecture. | Windows 98/Mac OS 9/old 32-bit systems moved to projection/constrained/archive tiers. | Source-native 64-bit mainline; legacy systems use thin clients, replay viewers, snapshots, or generated subsets. | P1 | active |
| WORKSTREAM-11 | Performance and efficiency contracts | Make optimization measurable and compatible with determinism. | Performance discussed as data layout, arenas, command buffers, batching, budgets, provider conformance. | Benchmarks and budgets for tick, replay, rendering, load, allocation, Workbench latency. | P1 | planned |

## Compact Registers for Merge

See files `04_registers.md` and `03_spec_sheet.yaml` for full register contents. Core compact registers are: decisions DECISION-01 through DECISION-10; tasks TASK-01 through TASK-12; constraints CONSTRAINT-01 through CONSTRAINT-10; risks RISK-01 through RISK-08; verification items VERIFY-01 through VERIFY-07.

## Possible Cross-Chat Duplicates

Language baseline, platform/renderer lanes, C/C++ split, Workbench/AIDE governance, package/module/provider architecture, and support-tier doctrine likely overlap with other Dominium chats.

## Possible Cross-Chat Conflicts

Older chats may still assert C89/C++98 mainline, C++98 apps, 32-bit/retro-first assumptions, or platform-specific directory structures. Treat those as superseded unless the user explicitly reopens them.

## Spec Book Integration Guidance

This chat should feed chapters on language baseline, ABI/public surfaces, deterministic simulation, architecture/platform support tiers, runtime providers, pack/module composition, Workbench/AIDE, and validation/release gates. Do not merge external toolchain support claims as final requirements without verification.

## Aggregator Warnings

Do not reduce this chat to “use C++17.” The design is C17 + C++17 with strict boundaries. Do not treat Workbench as authority. Do not bypass Foundation Lock. Do not merge assistant recommendations as accepted decisions without status labels.
