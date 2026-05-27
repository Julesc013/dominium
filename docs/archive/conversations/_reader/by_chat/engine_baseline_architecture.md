Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/engine_baseline_architecture/`
Promotion Status: not_reviewed

# Domino/Dominium Engine Baseline, Architecture, and Feasibility - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was about the architecture, feasibility, state, and future direction of the Domino engine and Dominium game. The user wanted to understand what the project is, whether the engine exists in a meaningful sense, whether it is ready to support a game, how it can become portable and modular enough to be reused for multiple games or even CAD-like tools, and how to sequence the work without being overwhelmed by the enormous scope.

The conversation began with a request to read the project docs and GitHub repository and describe the total project, especially the engine and game. The answer framed Domino as the deterministic simulation substrate, Dominium as the rule/game layer, and XStack/governance as the proof/audit discipline. Repository CMake files were fetched showing real `domino_engine` and `dominium_game` targets, with substantial engine and game source composition. Later, the user pushed beyond description into strategy: how to make the engine better, how to make it do more for less, how to support many hardware/software targets, and how to build something durable for decades.

A major theme emerged: Domino should not try to become a conventional monolithic game engine. It should become a deterministic, contract-driven, capability-negotiated simulation kernel. Dominium should be one product/game built on top, not the reason the engine exists. The engine should define mechanisms such as Work IR, Access IR, scheduling, replay, domains, fields, capabilities, registries, and law gates. The game should define meaning: construction, life, agents, economy, governance, survival, war, CAD-like design, terraforming, and so on. Client/rendering should be projection and intent only. Server/domain authority should own authoritative multiplayer truth.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, simulation, timekeeping, tooling, ui, workbench. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `14` source files. The primary extracted source is `docs/archive/conversations/engine_baseline_architecture/domino_dominium_engine_baseline_architecture__01_human_readable_report.md`.

## What Was Decided

- This corrected the plan. The final sequencing became: first **Milestone 0: Make the baseline path honest**. That means fixing server/runtime circular import, CLI forwarding, `session_create -> session_boot`, missing time-anchor policy registry, and making the strict local playtest validator pass. Only after that should the builder/destruction lab begin.
- The final user action uploaded `Pasted text.txt`, a detailed instruction prompt requiring a full preservation report, structured registers, spec sheet, aggregator packet, self-audit, and downloadable file package for this chat. That request is the current task.
- The central architecture distinction was that Domino should be a reusable deterministic simulation substrate, while Dominium should be one game/product layer built on it. This came up immediately when the user asked for a total description of the project. It mattered because the user wants the code to be reusable for future games and possibly other engine projects.
- The visible conclusion was that the engine has real deterministic substrate pieces, but these must be hardened through small playable slices and proof/replay tests. Determinism is not only a mathematical preference; it enables multiplayer authority, replay, audit, mod compatibility, and long-term artifact preservation.
- This became the practical pivot. The user pasted evidence that the repo has compiled targets and some passing tests but lacks a finished playable path. The final decision was that before game features, the team must create one canonical repo-local playable baseline command that passes strict validation.
- Uncertainty: this remains strategic architecture, not an implemented decision.
- The user explicitly accepted the correction that before a builder/destruction lab, the first deliverable should be one canonical repo-local playable baseline command passing strict validation. This is the most important sequencing decision in the chat.
- This was a recommended architectural conclusion after reading live repo docs. It is not a single user-typed acceptance sentence, but the user continued building on it. It should be treated as a strong strategic direction, not a final immutable spec.
- The assistant recommended a hybrid representation. The user did not explicitly confirm after that response in the visible transcript. Treat as a strong recommendation to preserve, not a final decision.
- The final tradeoff was engine-first versus game-first. The conclusion was neither: build minimal vertical slices that are simultaneously game work and engine proof.
- After Milestone 0, implement one accepted and one refused game action, likely a simple build/place-part action. It should pass through authority/law, Work IR/process, commit, replay/hash, and client projection.
- Show the object/action through null/software/TUI/simple rendered projection. Rendering must not mutate truth.

## What Was Not Decided

- Uncertainty: the repo has many modules and some historical/legacy surfaces, so exact implementation maturity varies by subsystem. The distinction should remain a formal requirement in a master spec.
- Uncertainty: the full determinism envelope across all current modules was not independently re-run in this chat. User-supplied local validation results should be preserved but verified before being used as audit proof.
- Uncertainty: this remains strategic architecture, not an implemented decision.
- Unresolved goals include:
- User wants uncertainty labelled and framing corrected when evidence disagrees.
- UNCERTAIN: whether the user wants Unreal integration at all as a client/editor.
- UNCERTAIN: exact tolerance for using external geometry libraries.
- UNCERTAIN: whether broad repo restructuring will be desired after Milestone 0.
- UNCERTAIN: exact visual style, UI stack, or programming language evolution.

## Ideas Rejected, Superseded, Or Deprioritised

- The answer also rejected recipes/tech trees as the default gameplay model. Instead, it proposed affordances and constraints: materials, tools, machines, capabilities, processes, authority, environment, time, and energy determine what can be made. Recipes, tech trees, levels, or certifications can exist as optional mod/game-mode layers via packs, law, profiles, and capabilities.
- The user explicitly stated they do not want usual gameplay to rely on technology trees, recipes, or experience levels, while wanting the engine to support those for mods/game modes. This is a strong product preference.
- Rejected because it creates an infinite engine project. The better plan is narrow vertical slices that harden the engine.
- Superseded by Milestone 0. CAD/destruction remains important but should not precede playable baseline hardening.
- Rejected/deprioritized because voxels are poor for precise machines, CAD semantics, interfaces, thin surfaces, and network-efficient authoritative objects. Voxels/SDF remain useful for terrain, mining, damage approximation, fluids, and debris.
- Rejected as impossible. The viable plan is full-scale but collapsed multi-resolution fidelity.
- Rejected as a default plan. Unreal may still be useful as a client/editor/rendering shell.
- Rejected by user preference. Still supported as optional mod/game-mode layers.
- Deprioritized because current baseline paths are fragile and v0.0.0/current-reality docs prioritize preserving them.
- Add simple part removal or damage that affects an assembly/support graph. Do not start with full CAD/CSG destruction.

## What Future Work Came From It

- The uploaded preservation prompt requires a maximum-fidelity human-readable handoff, structured registers, spec sheet, aggregator packet, self-audit, and downloadable file package for this chat. That prompt itself is an artifact of this chat and should be preserved. Source: ?filecite?turn44file0?
- The conclusion changed: the project already had more infrastructure than the generic future plan assumed. The recommendation shifted from "invent the architecture" to "converge the architecture." The answer proposed that Dominium should become a **contract-compiled simulation platform**: contracts -> registries -> compiled locks -> capabilities -> Work IR -> deterministic runtime -> proof/replay -> product shells.
- The final user action uploaded `Pasted text.txt`, a detailed instruction prompt requiring a full preservation report, structured registers, spec sheet, aggregator packet, self-audit, and downloadable file package for this chat. That request is the current task.
- The central architecture distinction was that Domino should be a reusable deterministic simulation substrate, while Dominium should be one game/product layer built on it. This came up immediately when the user asked for a total description of the project. It mattered because the user wants the code to be reusable for future games and possibly other engine projects.
- The conversation repeatedly returned to determinism. The project's value depends on identical inputs producing identical outputs, replay equivalence, stable commit ordering, named RNG streams, explicit Work IR/Access IR, and no hidden global scans. The assistant inspected execution model docs and source files such as task graph, access set, scheduler, and work queue.
- The conclusion was that future work should build active-set runtime, capsule/refinement contracts, compatibility edition matrix, golden replay corpus, and toolchain-first authoring. Later, after reading live repo docs, this plan was tightened into "contract-compiled simulation platform."
- This connects to future work because a construction/destruction game cannot rely on one universal representation. Different domains need different data structures.
- how to make the engine portable, modular, reusable, and future-proof;
- how to preserve this chat for future aggregation.
- INFERENCE: the user wants a development doctrine that makes the project less emotionally and technically overwhelming. The repeated questions about impossibility, not knowing how to write engines, and needing future-proof structure indicate a need for practical sequencing as much as architecture.
- INFERENCE: the user wants the engine to outlive Dominium and serve as a platform for multiple future projects.
- The conversation consistently preserved this boundary. The engine should define deterministic mechanisms; the game defines rules and meaning. This affects directory layout, APIs, naming, dependencies, modding, and future reuse. It would be revisited only if the project intentionally stopped trying to make Domino reusable, which contradicts the user's stated goal.

## Important Artifacts

- `handoff`: `1`
- `manifest`: `2`
- `markdown`: `2`
- `primary_report`: `1`
- `prompt`: `2`
- `reader_brief`: `2`
- `registers`: `1`
- `spec_sheet`: `1`
- `verification`: `1`
- `zip`: `1`

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
