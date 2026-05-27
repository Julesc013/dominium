# Aggregator Packet — Dominium Workbench, AIDE, Presentation Architecture, Provider Strategy, and Product-Spine Planning

## Packet Metadata

* Chat label: Dominium Workbench, AIDE, Presentation Architecture, Provider Strategy, and Product-Spine Planning
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only unless labelled PROJECT-CONTEXT
* Coverage: Partial-to-broad visible context, not raw full transcript
* Confidence: 4/5 for doctrine; 3/5 for live repo state
* Staleness risk: High for live repo/external software
* Merge priority: High
* Main limitations: verify live repo state and execution of latest prompts.

## Ultra-Condensed Carry-Forward Capsule

This chat is one of the central Dominium architecture-planning conversations. It began with a practical UI problem: the launcher UI was mangled and flickering, and the user wanted a Windows-first UI Editor / Tool Editor. Early turns produced detailed Codex prompts for a Phase A UI Editor, TLV/JSON document handling, layout engine, import/export, CLI ops scripting, and launcher/setup layout tests. That plan was later explicitly superseded. The user said the old UI Editor and Tool Editor were good ideas but bad final products, and they should be abandoned and recycled.

The replacement is Dominium Workbench Platform: a cross-platform rendered, modular, command-driven, agent-aware production environment for building Dominium and Domino artifacts. Workbench is not authority. It is a surface over contracts, commands, services, documents, patches, providers, packs, modules, artifacts, evidence, tests, and AIDE. Domino is the reusable deterministic substrate; Dominium is the game/product family; AIDE is the repo/control-plane harness; Codex is a bounded patch executor.

The chat established that CLI, TUI/text, rendered GUI, OS-native GUI, and headless are projections of the same semantic command/result/refusal/document/view/action spine. Presentation contracts and projection conformance must precede rich Workbench UI. The TUI is first-class. Rendered GUI is a portable, themeable, data-described system, not a native widget replacement. OS-native GUI can exist as optional projection.

AIDE’s workflow doctrine became: development is non-blocking; promotion is evidence-blocked. Task branches/worktrees feed dev, checkpoints prove waves, and main receives evidence-backed promotions. Capability Reality Ledger prevents fixture/stub/planned surfaces from being called implemented.

The chat also produced a third-party provider doctrine: raylib/rlgl/rlsw/raygui/raudio/SDL2/Lua should be used aggressively as replaceable providers, but Dominium owns service contracts, commands, saves, replays, packs, UI documents, provider law, and asset identity. Apps remain generic; profiles select providers; third-party types are fenced from engine/game/contracts/content/saves/replays/public SDK.

Latest user-reported state: PRESENTATION-CONTRACT-01 completed with PASS_WITH_WARNINGS. User wants to generate maintenance prompts first: FULL-GATE-LEGACY-TEST-ROUTE-01, PACK-INTERNAL-LAYOUT-CANON-01, RUNTIME-ENGINE-RESIDUAL-TAXONOMY-01, PUBLIC-HEADER-ABI-PROMOTION-01, STORAGE-PACKAGE-PROVIDER-SPLIT-01, POINTER-WIDTH-SERIALIZATION-AUDIT-01. FULL-GATE-LEGACY-TEST-ROUTE-01 has already been generated in this chat. After that, return to PROJECTION-CONFORMANCE-01 and the read-only Workbench/Universe Explorer/provider sequence.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | Verify live repo state before current-status prompts | Verification | VERIFY-01 | Task queue changed many times. | UNCERTAIN / UNVERIFIED | 3 |
| P0 | Continue targeted maintenance: full-gate/pack/taxonomy/ABI/storage/pointer audits | Task sequence | TASK-01..06 | Current user-selected next path. | FACT | 4 |
| P0 | Preserve Workbench-not-authority doctrine | Decision | DECISION-02 | Prevents GUI drift. | FACT | 5 |
| P0 | Preserve projection-unification doctrine | Decision | DECISION-04 | Unifies CLI/TUI/rendered/native/headless. | FACT | 4 |
| P1 | Provider strategy: raylib/SDL/Lua as fenced providers | Decision | DECISION-11 | Speeds progress without lock-in. | FACT/INFERENCE | 4 |

## Workstream Summaries

See Workstream Register in File 04. Active workstreams: architecture identity, AIDE workflow, product spine, presentation, Workbench, provider strategy, maintenance, Universe Explorer, theme/UI system, long-range simulation doctrine.

## Compact Registers for Merge

Use sections 17–28 in the registers file.

## Possible Cross-Chat Duplicates

Dominium operating environment doctrine, Foundation Lock, AIDE workflow, Workbench, deep primitives, Universe Explorer, provider strategy, and presentation contracts likely overlap other chats.

## Possible Cross-Chat Conflicts

Language baseline C89/C++98 vs C17/C++17; exact current repo queue; whether provider/raylib work starts before or after projection conformance; whether full CTest remains T4 debt.

## Spec Book Integration Guidance

Formalize Workbench/AIDE/presentation/provider doctrine as requirements. Preserve old UI Editor and Tool Editor as superseded context, not current architecture. Verify live repo state before merging current task statuses.

## Aggregator Warnings

Do not treat user-reported repo statuses as eternally current. Do not assume generated prompts were executed. Do not turn conceptual Universe Explorer into current implementation. Do not make raylib the architecture.
