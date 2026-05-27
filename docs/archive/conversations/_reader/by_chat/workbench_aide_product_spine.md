Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/Workbench_AIDE_Product_Spine/`
Promotion Status: not_reviewed

# Dominium Architecture, Workbench, AIDE, and Product-Spine Planning - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was primarily about moving Dominium from a large, ambitious but risk-prone game/simulation project into a disciplined, contract-governed, deterministic simulation platform with a reusable engine substrate, a production Workbench, and an AIDE-driven development workflow. The user's underlying concern was that Dominium should not become a one-off indie project with ad hoc code, drifting folders, duplicated UI systems, unverified docs, and fragile feature work. The conversation repeatedly returned to the same long-term aim: make all code, data, systems, and development workflows portable, modular, extensible, deterministic where needed, replaceable, testable, and compatible with future refactors or even total rewrites.

```text Domino    = reusable deterministic substrate Dominium  = game/product family on Domino Workbench = production, validation, editing, inspection, packaging, and evidence environment AIDE      = repo/control-plane harness Codex     = bounded patch executor Contracts = law Diagnostics / tests / replay / evidence = proof ```

A major shift was that the discussion stopped treating "the game," "the UI," "the Workbench," or "the folders" as the center. Instead, the center became contracts, commands, services, providers, packs, modules, artifacts, capabilities, diagnostics, tests, replay, and evidence. The system should be able to replace private implementations and even directories while stable semantic IDs, public contracts, conformance tests, and artifact identities remain intact.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, setup_launcher, simulation, timekeeping, tooling, ui, workbench, worldgen, xstack_aide. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `13` source files. The primary extracted source is `docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__01_human_readable_report.md`.

## What Was Decided

- The user noted that earlier prompts were hard to copy because they were not always contained in one code block, and that prompts should better handle dirty worktrees and concurrent tasks. From then on, generated prompts included detailed dirty worktree handling, allowed/forbidden paths, non-goals, validation, blocker classification, and commit/final-response formats.
- The final recommended sequence was: finish replay proof and barebones client, run product spine review, then begin limited parallel dev. Larger parallel waves should wait until minimum AIDE workflow law exists.
- The user then requested this full preservation package so a new chat could continue without re-explaining everything. This final handoff is itself part of the preservation output.
- The conversation treated epistemics and diegetics as more than flavor. They determine what must be simulated, loaded, rendered, or refined. If a player has not observed something, it can remain summarized so long as future expansion is consistent with seed, law, and causal history.
- DECISION-01 matters because the user's ambitions include worldgen, player invention, civilizations, modding, Workbench, AIDE, and future interfaces. A normal game-feature model would collapse. A deterministic simulation operating environment lets each capability become a contract-backed subsystem.
- DECISION-05 matters because the user wants many agents and machines to work in parallel without being stopped by every blocker. But main cannot become a dumping ground. This is why dev is permissive and main is evidence-blocked.
- DECISION-09 matters because separate CLI, TUI, GUI, and native systems would duplicate behavior and drift. The chosen architecture makes command/result/refusal/view/action the truth and projections the surface.
- DECISION-14 matters because `PACKAGE-MOUNT-SLICE-01` has only proven fixtures and reports. Treating it as package runtime would create false implementation claims.
- The conversation repeatedly balanced ambition against collapse. The user wants an ultimate simulation platform, but the chosen path is incremental proof slices. The system must avoid both extremes: building only doctrine with no usable product, and rushing into broad feature implementation that breaks modularity.
- The most important tradeoff is speed versus evidence. The user wants non-blocking development on `dev`, but main must remain evidence-backed. This led to the doctrine "development is non-blocking, promotion is evidence-blocked."
- A third tradeoff is UI richness versus architectural reuse. Workbench should eventually be powerful, but it must use the same command/view/projection system as client, launcher, setup, server, CLI, and TUI.
- A fourth tradeoff is portability versus modern code quality. The final doctrine accepts C17/C++17 for mainline while preserving C-compatible ABI and explicit serialization.

## What Was Not Decided

- The largest uncertainty is not the conceptual architecture; that has converged. The largest uncertainty is live execution state: whether prompts generated near the end of the chat have already been run locally, committed, or pushed. The next chat should first inspect `.aide/queue/current.toml`, recent commits, and relevant audit files.
- Remaining uncertainty: exact implementation of erosion/ecology/evolution proxies remains future domain work.
- 1. Verify current repo state.
- Explicitly label uncertainty.
- The next chat should verify repo state first.
- Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels.
- Verify live repo state before acting.
- safe_for_aggregation: "Yes, with caveats"
- "UNCERTAIN / UNVERIFIED"
- "Verify current queue and commits before acting."
- "Preserve uncertainty and rejected options."
- uncertain_or_not_established:

## Ideas Rejected, Superseded, Or Deprioritised

- The live repo state changed repeatedly during the conversation. Earlier, Foundation Lock was blocked by dependency-direction violations. Later, Foundation Lock closed as `PASS_WITH_WARNINGS`. The user and assistant repeatedly emphasized that `PASS_WITH_WARNINGS` is not "clean/no warnings"; full CTest remains T4/full-gate debt, and broad feature work remains blocked.
- The old "UI Editor / Tool Editor" plan was superseded by the Dominium Workbench Platform. Workbench should become the visual and agentic production environment for building Dominium: code, data, contracts, packs, modules, UI/HUD layouts, renderer tests, sounds/assets, tests, releases, and AIDE work units.
- Rejected: hardcoding all objects as primary truth or requiring all player intent through non-diegetic declarations.
- broad feature work = blocked
- Promotion is evidence-blocked.
- 3. Ensure future assistants do not restart settled debates.
- DECISION-05 matters because the user wants many agents and machines to work in parallel without being stopped by every blocker. But main cannot become a dumping ground. This is why dev is permissive and main is evidence-blocked.
- The most important tradeoff is speed versus evidence. The user wants non-blocking development on `dev`, but main must remain evidence-backed. This led to the doctrine "development is non-blocking, promotion is evidence-blocked."
- Do not smooth over contradictions.
- Do not ask whether to proceed when user already asked to proceed.

## What Future Work Came From It

- The largest uncertainty is not the conceptual architecture; that has converged. The largest uncertainty is live execution state: whether prompts generated near the end of the chat have already been run locally, committed, or pushed. The next chat should first inspect `.aide/queue/current.toml`, recent commits, and relevant audit files.
- In the later chat, the user requested a series of Codex/AIDE prompts. The assistant generated prompts for:
- The user noted that earlier prompts were hard to copy because they were not always contained in one code block, and that prompts should better handle dirty worktrees and concurrent tasks. From then on, generated prompts included detailed dirty worktree handling, allowed/forbidden paths, non-goals, validation, blocker classification, and commit/final-response formats.
- Near the end, the user wanted to run prompts in parallel on a permanent `origin/dev` and `local/dev`, then checkpoint/merge to `main`. The conversation converged on the AIDE OS model: agents should not mutate shared dev directly; each prompt should run in a task branch/worktree; AIDE integrates to dev; checkpoint branches prove waves; main receives only evidence-backed promotions.
- Remaining uncertainty: exact implementation of erosion/ecology/evolution proxies remains future domain work.
- The conversation treated epistemics and diegetics as more than flavor. They determine what must be simulated, loaded, rendered, or refined. If a player has not observed something, it can remain summarized so long as future expansion is consistent with seed, law, and causal history.
- AIDE should evolve from prompt generator into task operating system:
- The user needed copyable prompts in a single code block. Future prompts should include:
- `PACKAGE-MOUNT-SLICE-01` completed; next product-spine tasks are replay proof and barebones client shell.
- Worldgen, ecology, evolution, fabrication, economy, institutions, cities, conflict, and offworld systems remain future domain constitution work, not immediate implementation.
- 2. Make Dominium modular, extensible, deterministic, portable, and future-proof.
- 6. Generate copyable prompts for each next task.

## Important Artifacts

- `handoff`: `1`
- `json`: `1`
- `manifest`: `2`
- `markdown`: `2`
- `primary_report`: `1`
- `prompt`: `1`
- `reader_brief`: `2`
- `registers`: `1`
- `spec_sheet`: `1`
- `verification`: `1`

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
