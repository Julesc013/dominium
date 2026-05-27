Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/OS_Interface_Repo_Architecture/`
Promotion Status: not_reviewed

# Dominium OS-like Architecture, Repository Convergence, and Interface Operating Layer - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was about rethinking Dominium from a conventional game project into a much broader, more modular, deterministic, extensible software environment. The user repeatedly asked whether the current plan was the best possible version, and the discussion evolved from GUI/binary planning, to repository restructure, to release/package strategy, to code-vs-data analysis, to an "OS-like" deterministic simulation operating environment, and finally to a unified Interface Operating Layer and Workbench platform.

The user's underlying objective was not simply to clean folders or choose GUI frameworks. The larger goal was to preserve the long-term ambition of Dominium: a deterministic, moddable, inspectable, replayable universe platform where client, server, launcher, setup, tools, Workbench, packs, validation, release, and agent workflows all share common contracts. The user was concerned that the existing code and docs were extensive but not yet aligned with the vision, and that early wrong decisions could create brittle product architectures, GUI drift, duplicated command systems, or a repo that looked cleaner while remaining conceptually confused.

The conversation began from an earlier baseline: CLI should always work, TUI should be expected, and multiple native or rendered GUI shells should be thin, replaceable frontends over a stable backend/UI contract. Windows, macOS, Linux, and Android lanes were discussed, including legacy/modern toolchains and compatibility floors. The chat then moved into repository convergence: the user wanted to know whether a generic `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `tools/` style structure was enough. The answer became more nuanced: the repository should be organized by architectural ownership and contract boundaries, not by topic folders or temporary product categories. The key split became contracts, engine/kernel, game/domains, runtime/services/drivers, apps/userland products, content/packs, tools/dev tooling, and release/distribution.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, setup_launcher, simulation, tooling, ui, workbench. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `15` source files. The primary extracted source is `docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__01_human_readable_report.md`.

## What Was Decided

- DECISION-01 - CLI mandatory, TUI expected, GUI modular.** This was part of the initial architecture baseline and was repeatedly reaffirmed. It matters because every product must remain operable in recovery/headless/automation contexts. GUI is allowed but not authoritative.
- DECISION-02 - Thin GUI shells over shared contracts.** The chat consistently rejected GUI families becoming separate product architectures. This affects client, launcher, setup, server admin, tools, and Workbench modules.
- DECISION-03 - Repo ownership layout.** The user pushed for repository convergence; the discussion established that folders should map to ownership and contract boundaries. This decision is final enough to guide work, but details remain subject to machine-readable layout contracts.
- DECISION-04 - Current post-CONVERGE authority.** The final audit and layout target docs define current roots and authority stack. Older docs remain context but not current physical-layout authority.
- DECISION-05 - OS-like deterministic operating environment.** The user proposed this framing and the assistant endorsed it. It is not a literal OS decision; it is a conceptual architecture decision. It should be formalized before implementation.
- DECISION-06 - Workbench modular host.** The user explicitly accepted the idea of one integrated environment with many focused modules. This supersedes the old UI Editor / Tool Editor final-product plan.
- DECISION-07 - Interface Operating Layer.** The final UI discussion generalized Workbench into a cross-product interface platform. This is a strong direction, but it should be formalized as doctrine and contract work before being treated as implemented.
- DECISION-08 - Rendered mode product-declared.** This was an assistant correction based on AppShell docs. It is necessary because current AppShell docs say rendered mode is client-only. User has not yet separately confirmed the doctrine change, so treat it as a required proposed decision.
- DECISION-09 - Keep shipped modules out of repo-only `tools/`.** This follows repo ownership rules. The Workbench's shipped modules should live under `apps/tools/modules/` or equivalent, while developer validators/codegen/audit tooling remains under `tools/`.
- DECISION-10 - No-assets GUI floor.** The UI baseline doc already requires a zero-asset GUI floor. The chat expanded this into a product-grade primitive UI system.
- DECISION-11 - Deterministic layered packaging.** The chat recommended component packages, install profiles, distribution trees, thin installer wrappers, release manifests and indexes. This aligns with release/distribution docs.
- DECISION-12 - Avoid arbitrary native plugins early.** This is a risk-management choice. Early modules should be built-in or data-described; later IPC/WASM/script/native extensions require trust and sandbox policy.

## What Was Not Decided

- The unresolved goals are implementation-level. The repo still needs command dispatch unification, product boot proof, portable projection proof, AppShell rendered-mode law update, Workbench module contracts, document/patch/result/refusal schemas, and a boot-to-replay MVP. It also needs continued exception retirement, CTest/RepoX remediation, and verification of current build status.
- 2. Repair canonical verify test discovery.
- The user wants uncertainty labels and correction of incorrect framing.
- This preservation task specifically required FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels, stable IDs, registers, spec sheets, an aggregator packet, self-audit, and downloadable files if tools are available.
- UNCERTAIN: Whether the user wants to rename `engine` conceptually to `kernel` in code, or only use kernel as a conceptual layer.
- UNCERTAIN: Whether the final public product name should be Dominium Workbench, Dominium Studio, Domino Workbench, or something else.
- UNCERTAIN: How aggressive the next actual code refactor should be versus staged adapters and codegen.

## Ideas Rejected, Superseded, Or Deprioritised

- DECISION-02 - Thin GUI shells over shared contracts.** The chat consistently rejected GUI families becoming separate product architectures. This affects client, launcher, setup, server admin, tools, and Workbench modules.
- 1. **One universal GUI framework for all hosts.** Rejected because long-lived Dominium needs native/near-native families and compatibility lanes.
- 2. **One GUI per OS version.** Rejected as matrix explosion. The better model is compatibility lanes and visual profiles.
- 3. **Generic game repo layout without Dominium-specific ownership rules.** Superseded by ownership-root and domain-split doctrine.
- 4. **Old UI Editor -> Tool Editor as final product.** Superseded by modular Dominium Workbench and later Interface Operating Layer.
- 5. **One monolithic "everything editor."** Rejected. The Workbench should be a shell plus modules.
- 6. **OS-native widgets as the core tools strategy.** Deprioritized. Rendered UI using Dominium runtime should be first; native wrappers later.
- 7. **Visual Studio/Xcode replacement as immediate goal.** Rejected. Workbench is self-hosting in spirit, not a full IDE replacement.
- 8. **.NET 2.0 as old Windows GUI default.** Rejected/deprioritized in favor of native Win32 for old setup/server surfaces.
- 9. **Raw binaries as primary release unit.** Rejected in favor of deterministic package/profile/bundle/release-manifest model.

## What Future Work Came From It

- The central tradeoff was between short-term visible functionality and long-term architectural leverage. The user repeatedly asked whether the plan could be more modular, future-proof, optimized, robust, reliable, useful, and powerful. The answer consistently favored building shared contracts and proof paths before expanding product surfaces.
- This preservation task specifically required FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels, stable IDs, registers, spec sheets, an aggregator packet, self-audit, and downloadable files if tools are available.
- Future facts involving platforms, software support, toolchains, APIs, laws, schedules, prices, current roles, etc. require verification.
- INFERENCE: The user wants future assistants to preserve reasoning and not collapse tentative ideas into final decisions.
- 1. **Uploaded `Pasted text.txt`.** Contains the preservation/export prompt that generated this package.
- 2. **Repo docs inspected during chat.** Key examples: AppShell constitution, GUI baseline, repo layout target, ownership rules, domain split rules, final convergence audit, post-CONVERGE next steps, versioning/distribution docs, code/data report, modularity proof, product boot proof.
- 4. **Conceptual artifacts produced in chat.** These include proposed architectures, matrices, lane plans, Workbench modules, Interface Operating Layer, boot-to-replay MVP, and structured roadmaps.
- 5. **This preservation package.** Newly generated files and ZIP at the end of this task.
- No prior downloadable handoff ZIP from this chat was visible before this task. The earlier user mentioned a `docs.zip`, but no such file was available in the currently loaded file set.
- 1. Should `engine` remain the physical name while being conceptually treated as kernel, or should a future rename be considered?
- 11. How should future reports from other old chats be reconciled against this one?
- Future assistants might overstate implementation status. Much of this chat defines direction, not completed code. Product boot and portable projection proof were partial/blocked in inspected docs.

## Important Artifacts

- `handoff`: `1`
- `manifest`: `3`
- `markdown`: `2`
- `primary_report`: `1`
- `prompt`: `1`
- `reader_brief`: `2`
- `registers`: `1`
- `source_input`: `1`
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
