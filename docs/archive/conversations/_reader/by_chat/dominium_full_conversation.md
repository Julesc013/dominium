Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/dominium_full_conversation/`
Promotion Status: not_reviewed

# Dominium Workbench, AIDE, Presentation Architecture, Provider Strategy, Product-Spine Planning, and Preservation Companion - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This conversation records a major architectural transition in the Dominium project. It began with an immediate practical concern: the existing Windows launcher UI looked broken, flickered, and needed a better way to design UIs. The initial direction was to create a Windows-first UI Editor and eventually a Tool Editor that could visually design pixel-perfect UIs and generate TLV-based layouts/code. That early plan was explored in depth: TLV schemas, UI IR, deterministic JSON mirrors, layout engines, Win32/DGFX/null backends, action code generation, import/export, CLI scripting, native widget previews, and launcher/setup redesign tests were all discussed and turned into prompt plans.

Over the course of the chat, the user corrected the direction. The old UI Editor/Tool Editor path was judged useful as an idea but wrong as a final architecture. OS-native GUI design can rely on first-party tools such as Visual Studio and Xcode where appropriate. Dominium's real internal tooling should instead prove and reuse the same runtime, command, rendering, UI, package, and diagnostic systems that the client and other products need. This led to the replacement concept: **Dominium Workbench Platform**.

Workbench is the central product concept of this chat. It is not a monolithic IDE and not an authority over the project. It is a cross-platform rendered, modular, command-driven, agent-aware production environment. It should eventually let the user and agents build the entire project: code scaffolds, packs, modules, UI/HUD documents, themes, renderer tests, release artifacts, diagnostics, evidence packets, AIDE/Codex work units, and product compositions. Its design doctrine is: Workbench designs artifacts; runtime executes artifacts; contracts constrain artifacts; content packages artifacts; apps consume artifacts; tests prove artifacts; AIDE governs changes; Codex patches code.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, setup_launcher, simulation, timekeeping, tooling, ui, workbench, worldgen, xstack_aide. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `nested_package_collection` with `62` source files. The primary extracted source is `docs/archive/conversations/dominium_full_conversation/companion_report/dominium_full_conversation_companion_report__01_complete_human_report.md`.

## What Was Decided

- A future assistant must understand that this chat is not simply about UI. It records the architecture for how Dominium should build itself: through contracts, commands, services, providers, documents, patches, modules, packs, apps, workspaces, diagnostics, evidence, AIDE, Codex, and eventually Workbench.
- The user then redirected the entire plan. They argued that native OS widget GUI tools already exist through Visual Studio, Xcode, etc. The project needed a cross-platform rendered tool environment that uses the same CLI, TUI, and rendered GUI systems as the client. The old UI Editor and Tool Editor were good exploratory ideas but bad final products. This produced the Dominium Workbench concept.
- The discussion then moved into AIDE. The user wanted to automate as much as possible through Codex and AIDE. We developed a task operating model: AIDE creates WorkUnits, tracks attempts, blockers, evidence, repairs, resumes, checkpoints, and promotion decisions. Codex executes bounded tasks. Development can continue with classified partials and repairable blockers; promotion to main requires evidence.
- The final part of the conversation dealt with repo status and task queue. The user pasted status reports indicating that `PRESENTATION-CONTRACT-01` completed with warnings, and then chose to generate six maintenance prompts before replanning. `FULL-GATE-LEGACY-TEST-ROUTE-01` was generated. This preservation task followed.
- The early UI Editor plan was a structured attempt to fix the launcher UI and build a tool for UI authoring. It covered DUI/TLV, native widgets, Win32 preview, deterministic TLV/JSON, layout, validation, codegen, `ops.json`, import/export, and launcher/setup generation. The conclusion was that these are useful components but not the final product architecture. They should become Workbench modules and services.
- Workbench became the central product concept. It is a cross-platform rendered production environment, not a monolithic editor. It hosts workspaces and modules over contracts, commands, documents, patches, services, providers, packs, artifacts, evidence, and tests. It eventually self-hosts by editing its own safe artifacts first, then product UIs, packs, modules, apps, and AIDE work units.
- The rendered GUI must be backend-agnostic. Layouts, controls, widgets, themes, styles, views, and workspaces should be modular and extensible. Themes include first-party primitive-only profiles and OEM+ mimic profiles. The GUI should be task-first, command-backed, evidence-visible, and projection-neutral.
- Preserve all decisions, tasks, prompts, constraints, files, and artifacts in a downloadable package.
- The live repo state must be verified before executing future prompts. Full-gate debt remains. Workbench shell is not implemented. Provider runtime, package runtime, module loader, renderer, native GUI, gameplay, and Universe Explorer remain future work.
- The Workbench decision was the largest architectural correction. The old UI Editor plan could have solved the immediate launcher problem, but it would not have proven the client/runtime stack. Workbench makes the tools use the same systems they help produce.
- The AIDE decision was driven by the scale of the project. Once many Codex tasks run in parallel, stale queues, dirty worktrees, partial branches, and unclear blockers become first-order risks. AIDE gives those states names and evidence requirements.
- The projection decision was driven by portability and reuse. If CLI, TUI, rendered GUI, and native GUI are implemented separately, they will drift. If they are projections of the same command/result/view system, all products share semantics.

## What Was Not Decided

- Verify live repo state, then review/run `FULL-GATE-LEGACY-TEST-ROUTE-01`, then generate `PACK-INTERNAL-LAYOUT-CANON-01` if the queue/status supports the maintenance lane.
- Preserve uncertainty labels.
- Future chats could easily misunderstand this conversation by treating Workbench as a GUI framework, treating raylib as the engine, resuming broad structure cleanup, skipping projection conformance, or assuming live repo status from stale pasted reports. The mitigation is to verify repo state first, preserve the contract/service/projection/provider distinctions, and follow the task queue.
- The best next action is to verify live repo state, then review or run `FULL-GATE-LEGACY-TEST-ROUTE-01`, then generate `PACK-INTERNAL-LAYOUT-CANON-01` if status supports it.

## Ideas Rejected, Superseded, Or Deprioritised

- This prompted a provider structure: `runtime/<service>/providers/<provider>`, `contracts/provider`, `contracts/capability`, `contracts/schema/runtime/<service>`, `release/profiles`, `content/profiles`, and `external/upstream`. The plan explicitly rejected `runtime/raylib/render`, `apps/client/rendered/raylib`, `contracts/raylib`, top-level `profiles`, and top-level `labs`.
- AIDE should govern work; Codex should execute bounded patches. The chat designed branch roles, lifecycle states, WorkUnit schemas, blocker taxonomy, dirty worktree policy, dev/main promotion, checkpoint loops, and capability reality ledger. The key doctrine is non-blocking dev and evidence-blocked promotion.
- Do not turn brainstorms into decisions.
- Do not treat assistant suggestions as accepted decisions unless the user accepted them.
- Do not restart settled doctrine unnecessarily.
- Formal requirements candidates include: Workbench is not authority; third-party providers are fenced; CLI/TUI/rendered/native/headless are projections; development non-blocking/promotion evidence-blocked; every visual edit becomes a document patch; provider capabilities require evidence.
- The old UI Editor/Tool Editor plan is superseded.
- AIDE became the governance system. Codex is a bounded patch executor. AIDE is the scheduler, context compiler, blocker classifier, evidence ledger, repair/resume generator, checkpoint coordinator, and promotion gatekeeper. The central doctrine is: development is non-blocking, promotion is evidence-blocked. Dev and task branches can hold classified partials and warnings; main requires evidence-backed checkpoints.
- The provider strategy became service-first. Raylib, rlgl, rlsw, raygui, raudio, SDL2, and Lua can be used aggressively, but only as replaceable providers. Dominium owns service contracts, provider law, commands, saves, replays, packs, UI documents, and asset identity. Third-party types must not leak into stable law or public SDK surfaces.

## What Future Work Came From It

- A future assistant must understand that this chat is not simply about UI. It records the architecture for how Dominium should build itself: through contracts, commands, services, providers, documents, patches, modules, packs, apps, workspaces, diagnostics, evidence, AIDE, Codex, and eventually Workbench.
- The conversation began with the user wanting a product designer/software architect/prompt engineer to help design an internal graphical UI creation tool. The immediate pain point was the Dominium Windows launcher UI: it looked mangled and flickered. The user wanted a tool that could visually design pixel-perfect UIs and broad-strokes functionality for setup, launcher, game, and tools.
- A large prompt plan followed: repo scaffolding, canonical UI IR, TLV I/O, capability system, layout engine, splitter/tabs/scroll widgets, action codegen, Phase A UI Editor, Tool Editor bootstrap, Win32 batching/flicker fixes, tests, docs, and capability tests through launcher/setup redesigns.
- The discussion then moved into AIDE. The user wanted to automate as much as possible through Codex and AIDE. We developed a task operating model: AIDE creates WorkUnits, tracks attempts, blockers, evidence, repairs, resumes, checkpoints, and promotion decisions. Codex executes bounded tasks. Development can continue with classified partials and repairable blockers; promotion to main requires evidence.
- This led to generated prompts: `STATUS-RECONCILE-02`, `AIDE-WORKFLOW-LAW-01`, `AIDE-WORKUNIT-SCHEMA-01`, `AIDE-DEV-MAIN-POLICY-01`, `AIDE-CHECKPOINT-LOOP-01`, and `AIDE-CAPABILITY-REALITY-LEDGER-01`. The user wanted to run AIDE workflow, WorkUnit schema, and dev/main policy concurrently on the same machine via separate Codex tasks.
- This prompted a provider structure: `runtime/<service>/providers/<provider>`, `contracts/provider`, `contracts/capability`, `contracts/schema/runtime/<service>`, `release/profiles`, `content/profiles`, and `external/upstream`. The plan explicitly rejected `runtime/raylib/render`, `apps/client/rendered/raylib`, `contracts/raylib`, top-level `profiles`, and top-level `labs`.
- The final part of the conversation dealt with repo status and task queue. The user pasted status reports indicating that `PRESENTATION-CONTRACT-01` completed with warnings, and then chose to generate six maintenance prompts before replanning. `FULL-GATE-LEGACY-TEST-ROUTE-01` was generated. This preservation task followed.
- The rendered GUI must be backend-agnostic. Layouts, controls, widgets, themes, styles, views, and workspaces should be modular and extensible. Themes include first-party primitive-only profiles and OEM+ mimic profiles. The GUI should be task-first, command-backed, evidence-visible, and projection-neutral.
- The chat concluded not to restart broad structure cleanup. Active structure is good enough; remaining issues should be targeted maintenance. The immediate generated maintenance prompt was `FULL-GATE-LEGACY-TEST-ROUTE-01`.
- Universe Explorer became a future north-star: a read-only product/Workbench/Client slice for seamless inspection of universe-scale data, reference frames, materialization, streaming, fidelity degradation, and provenance. It should start contract-first and headless before visual implementation or embodiment.
- Build tools that can help create setup, launcher, game, and future tools.
- Preserve all decisions, tasks, prompts, constraints, files, and artifacts in a downloadable package.

## Important Artifacts

- `handoff`: `2`
- `json`: `1`
- `manifest`: `4`
- `markdown`: `9`
- `png`: `10`
- `primary_report`: `3`
- `prompt`: `4`
- `reader_brief`: `5`
- `registers`: `3`
- `source_input`: `1`
- `spec_sheet`: `2`
- `text`: `1`
- `unknown`: `10`
- `verification`: `3`
- `zip`: `4`

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
