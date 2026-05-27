Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/Build_and_Future_Proofing/`
Promotion Status: not_reviewed

# Dominium Build and Future-Proofing Architecture - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat centered on how to make Dominium durable as a serious long-term software project rather than a one-off game prototype. The user first provided a prior technical assessment about Dominium's Windows build floors, Visual Studio toolchains, XP/Win7/Win10 support, CMake presets, static CRT policy, and runtime testing requirements. That pasted material treated Dominium's canon as strict: engine in C89, game layer in C++98, deterministic fixed-point behavior, no hidden capability creep, separate artifacts per OS floor, no CRT mixing, and proof through RepoX/TestX-style governance.

The user's first active question then reframed the problem around build-system complexity. They were concerned that different machines would have different IDEs and compilers: one Windows 10 laptop might use VS2017, a desktop might carry VS2022/VS2026 plus XP toolchains, while old VMs or old hardware might host VS2010, VS2005, VC6, VC1.5, Xcode 9, CodeWarrior Pro 9, and other historical toolchains. The user asked for the best way to design CMake, CI, presets, distribution, sync, and AIDE/XStack support so Dominium could manage those varied machines and outputs without becoming chaotic.

The response treated that as a build orchestration problem, not merely a preset list. The key recommendation was that CMake should remain the canonical build executor, but `CMakePresets.json` should stop acting as a single giant catch-all for host machines, IDE names, toolchains, OS floors, renderers, distribution variants, and release status. The proposed approach was tuple-driven: declare build tuples in contracts, probe the local machine, generate local user presets, execute CMake/CTest, collect TestX/RepoX evidence, then generate distribution/package manifests. AIDE would not replace CMake; it would detect local capabilities, generate local presets, run tuple verification, and preserve evidence. XStack would remain an orchestration/governance layer, while RepoX/TestX would supply repository-policy and deterministic-runtime proof.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, simulation, tooling, ui, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `13` source files. The primary extracted source is `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`.

## What Was Decided

- Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions.
- The final uploaded prompt requested a complete preservation package for this chat: a human-readable explanation, structured registers, context transfer packet, spec sheet, aggregator packet, self-audit, and files/ZIP package. This response completes that export task and creates downloadable files for later reading and aggregation.
- The final explicit goal was preservation: create a maximum-fidelity package for this chat so the user can understand it later, ask questions in this chat, merge it with other old-chat reports, and eventually build a master project spec book.
- The most important caution is that only DECISION-01 is clearly a user-stated constraint in this visible chat. The other items are strong recommendations produced in response to the user's requests for best practice; they should not be merged into canon unless the user later accepts them.
- Manual drag-and-drop repo moves were rejected in earlier context and preserved here as a general risk; moves must go through migration maps, validators, shims, and proof.
- 10. **Feed this report into the master spec book aggregator.** Preserve uncertainty labels and avoid merging suggestions as decisions.
- Determinism, fixed-point behavior, and no hidden behavior are central constraints.
- Multi-floor builds must be separate artifacts.
- The preservation output must distinguish FACT, INFERENCE, UNCERTAIN/UNVERIFIED, and PROJECT-CONTEXT.
- Whether the current top-level structure is final-final or merely best current target remains subject to user decision and repo evidence.
- No pre-existing downloadable files from this chat were available before this task. The downloadable files listed in the final section were created by the preservation task.
- 6. Which code surfaces must be reusable for non-Dominium future engine projects?

## What Was Not Decided

- Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions.
- The unresolved goals are implementation goals: deciding which recommendations become canon, adding public-surface/dependency/build contracts, validating the current live repo state, and applying the proposed cleanup tasks. The preservation package is complete, but the engineering work it describes remains pending.
- 2. **Verify current repo state.** Confirm the actual current HEAD, build proof, smoke tests, and outstanding warnings before acting.
- 10. **Feed this report into the master spec book aggregator.** Preserve uncertainty labels and avoid merging suggestions as decisions.
- The preservation output must distinguish FACT, INFERENCE, UNCERTAIN/UNVERIFIED, and PROJECT-CONTEXT.
- A future assistant may rely on stale repo state. Mitigation: verify live HEAD, docs, and CI before implementation.
- What live repo facts should I verify before implementing these tasks?
- The final uploaded prompt asked for this preservation package. The key thing to preserve is that most architecture proposals are recommendations, not accepted user decisions yet. The next best action is to decide which recommendations become canon, then implement either `STRUCTURE-01: Public Surface Registry` or the build tuple contract work, after verifying the current live repo state.

## Ideas Rejected, Superseded, Or Deprioritised

- Plain-language limitation: this package is reliable as a preservation of the current visible chat. It should not be treated as a complete archive of every Dominium discussion in other chats. Where the report uses project or repository context, it is labelled as such. The most important caveat is that many items are recommendations, not final user decisions.
- More hand-written CMake presets were deprioritised. The better path is generated local presets from declared build contracts.
- One universal binary or one universal preset was rejected because it violates per-floor artifacts, CRT isolation, SDK pinning, and explicit floor proof.
- AIDE replacing CMake was rejected. AIDE should orchestrate, probe, and preserve evidence; CMake remains build authority.
- Manual drag-and-drop repo moves were rejected in earlier context and preserved here as a general risk; moves must go through migration maps, validators, shims, and proof.
- Freezing implementation files/directories was rejected in favor of freezing contracts, public surfaces, protocols, schemas, IDs, and compatibility semantics.
- Generic active-source names such as `common`, `misc`, `helpers`, `old`, `new`, `legacy`, `stub`, and status-coded paths were deprioritised for canonical code.
- The user constraints around C89/C++98, determinism, no CRT mixing, per-floor artifacts, and no silent API creep must not be diluted.
- Do not merge assistant recommendations into canon without user acceptance.

## What Future Work Came From It

- The user then pushed beyond build mechanics. They asked what else they were missing about portability, modularity, extensibility, replacement, rewriteability, and reuse across future games and engines. They explicitly wanted Dominium to be developed like a proper OS or game-engine platform, not a one-off indie project.
- The final uploaded prompt requested a complete preservation package for this chat: a human-readable explanation, structured registers, context transfer packet, spec sheet, aggregator packet, self-audit, and files/ZIP package. This response completes that export task and creates downloadable files for later reading and aggregation.
- The user wanted reusable code for different games on the Domino engine and possibly unrelated future engine/game projects. The answer was to freeze contracts rather than implementations. Stable ABI/API/data/protocol surfaces should be explicitly versioned and tested; implementations should be replaceable behind black-box conformance tests. This is the basis for future rewrites without breaking compatibility.
- The uploaded prompt requested a complete chat preservation package with human report, registers, handoff packet, spec sheet, aggregator packet, audit, and downloadable files. This output creates that package and labels its limitations.
- The user explicitly wanted to design a robust Dominium build system that could handle many machines, IDEs, compilers, OS floors, CMake presets, CI lanes, distribution outputs, and historical toolchains. The user also explicitly wanted Dominium's codebase to be portable, modular, extensible, reusable across future games and engines, and refactorable at the level of whole files and directories.
- INFERENCE: The user is trying to prevent Dominium from accumulating accidental architecture. They want mechanical governance rather than relying on memory or assistant recommendations. They also want future assistants to stop repeating conceptual advice and instead preserve actionable structure, constraints, risks, and next tasks.
- The unresolved goals are implementation goals: deciding which recommendations become canon, adding public-surface/dependency/build contracts, validating the current live repo state, and applying the proposed cleanup tasks. The preservation package is complete, but the engineering work it describes remains pending.
- The user wants future assistants to preserve tentative status and not over-canonize recommendations.
- Whether all recommended structural tasks should be implemented now is not established.
- No pre-existing downloadable files from this chat were available before this task. The downloadable files listed in the final section were created by the preservation task.
- 6. Which code surfaces must be reusable for non-Dominium future engine projects?
- 7. How should future master spec aggregation reconcile overlap with earlier Dominium chats?

## Important Artifacts

- `handoff`: `1`
- `manifest`: `1`
- `markdown`: `1`
- `primary_report`: `2`
- `prompt`: `2`
- `reader_brief`: `2`
- `registers`: `1`
- `spec_sheet`: `1`
- `verification`: `2`

## Verification Needed

- Verify every implementation, platform, tooling, release, and queue claim against current repo artifacts.
- Treat external platform or SDK claims as stale until independently checked.
- Treat old language-baseline claims as historical unless they match current `README.md` and current contracts.
- Do not infer current authority from the existence of this archive package.

## Candidate Promotions

Candidate promotions, if any, are recorded in `_promotion/PROMOTION_QUEUE.md`. This page does not promote claims.

## Do Not Assume

- Do not assume this conversation established current repo truth.
- Do not assume generated package reports are canonical.
- Do not assume old prompts were executed.
- Do not assume unresolved items are safe to implement.
- Do not use this package to open blocked work without stronger current authority.
