# Aggregator Packet — Dominium Foundation Lock, Workbench Spine, and Parallel Codex Handoff

## Packet Metadata

* Chat label: Dominium Foundation Lock, Workbench Spine, and Parallel Codex Handoff
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only unless labelled PROJECT-CONTEXT
* Coverage: Partial but high-context
* Confidence: 4 / 5
* Staleness risk: Medium
* Merge priority: High
* Main limitations: skipped turns, expired previous uploads, final live repo state not rechecked after latest paste

## Ultra-Condensed Carry-Forward Capsule

This chat is a major continuity bridge for the Dominium project. It preserves the transition from repository cleanup and Foundation Lock into narrow governed product slices and parallel Codex execution. The settled architecture is: Domino is reusable deterministic/runtime substrate; Dominium is the game/product family; Workbench is the production, validation, editing, inspection, packaging, evidence, and agent-control environment; AIDE is the repo-control harness; Codex is a bounded patch executor; contracts are law; tests/replay/diagnostics/evidence are proof. The core invariants are: path is not identity, implementation is not contract, UI is not authority, generated output is not source truth.

The repo root cleanup era is treated as mostly behind us. The canonical root model is closed: apps, engine, game, runtime, contracts, content, docs, tests, tools, scripts, cmake, external, release, archive. Old root junk drawers should not return. The project’s language/architecture direction is C17 + C++17, C-compatible public ABI, 64-bit source-native full products, little-endian mainline, fixed-width persisted formats, and no pointer-sized truth.

Foundation Lock was first blocked by dependency-direction strict validation and later reportedly closed with warnings after repair. Current working state says fast strict passes, RepoX STRICT passes with stale AuditX warning, CMake configure/build and smoke CTest pass through fast strict, full CTest remains T4/full-gate debt, broad feature work remains blocked, and `WORKBENCH-VALIDATION-SLICE-01` is authorized and reportedly complete.

The user introduced a parallel Codex workflow: multiple isolated git worktrees/branches; no direct pushes to main by workers; no edits to global AIDE latest files; task-local evidence only; strict path allowlists; targeted validators; coordinator serial merges and fast strict checks. Wave 1 prompts generated here were service conformance law, document/patch/transaction law, project graph law, composition resolver law, and doctrine recovery matrix. Later pasted state says Wave 1 is complete and the next task is `COMMAND-RESULT-VIEW-SLICE-01`.

The immediate next action, after live verification, is to generate/run `COMMAND-RESULT-VIEW-SLICE-01`. It should use `dominium.validation.run` if possible to prove same command, result schema, refusal codes, diagnostics, evidence packet, and semantic view across CLI/headless/text/TUI/Workbench projections. It must not implement full Workbench shell, rendered GUI, native GUI, package runtime, provider runtime, module loader, gameplay, renderer implementation, or release publication.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
|---|---|---|---|---|---|---|
| 1 | Generate COMMAND-RESULT-VIEW-SLICE-01 | Task | TASK-02 | Immediate next bridge from governance to product spine | FACT/UNCERTAIN | Medium |
| 2 | Verify live repo state | Task | TASK-01 | Avoid acting on stale pasted state | FACT | High |
| 3 | Preserve Workbench-not-authority law | Constraint | CONSTRAINT-06 | Prevents private-tool bypass | FACT | High |
| 4 | Preserve parallel worker rules | Constraint | CONSTRAINT-03/04 | Prevents merge chaos | FACT | High |
| 5 | Treat full CTest as T4 debt | Constraint | CONSTRAINT-02 | Keeps progress fast | FACT | High |

## Workstream Summaries

### WORKSTREAM-01 — Dominium / Domino / Workbench / AIDE master architecture
* Objective: Preserve the final system model: Domino substrate, Dominium product family, Workbench environment, AIDE harness, contracts law, proof by tests/replay/evidence.
* Current state: Foundation/governance spine mostly established; broad feature work blocked; narrow slices authorized after Foundation Lock.
* Desired end state: A deterministic, contract-governed simulation platform with replaceable implementations and evidence-backed product slices.
* Priority: P0
* Status: active

### WORKSTREAM-02 — Canonical repository skeleton and root cleanup
* Objective: Keep the repo in the closed ownership-root model and avoid junk-root recurrence.
* Current state: Root cleanup reportedly no longer the main issue; earlier router/move work replaced bad roots or quarantined unknowns.
* Desired end state: No active old root junk drawers; canonical roots remain stable; generated/local roots stay out of source authority.
* Priority: P0
* Status: mostly-complete

### WORKSTREAM-03 — Foundation Lock and governance spine
* Objective: Ensure public surfaces, ABI, dependency direction, commands, diagnostics, artifacts, schema/protocol, capability/refusal, providers, modules/apps, replacement, versioning, trust, and portability are validated.
* Current state: Foundation Lock reportedly PASS_WITH_WARNINGS after dependency repair; fast strict passes; full CTest remains T4 debt.
* Desired end state: Foundation Lock remains the baseline gate for narrow product work; full gate reserved for release/trust.
* Priority: P0
* Status: active

### WORKSTREAM-04 — Fast strict proof loop
* Objective: Use a fast, meaningful normal gate instead of full CTest for every task.
* Current state: Fast strict reportedly passes 32 commands in ~272–315 seconds depending audit; full CTest remains T4 debt.
* Desired end state: Normal changes use targeted validators + fast strict; release/trust changes use full gate.
* Priority: P0
* Status: active

### WORKSTREAM-05 — Language and native architecture baseline
* Objective: Use C17/C++17, 64-bit source-native, little-endian, C-compatible ABI, fixed-width persisted formats.
* Current state: C17/C++17 reportedly live; 64-bit architecture policy prompted/in-flight or pending verification.
* Desired end state: Mainline full native products are x86_64/arm64; 32-bit/vintage targets are constrained/projection/archive-runner.
* Priority: P0
* Status: active

### WORKSTREAM-06 — Parallel Codex/AIDE workflow
* Objective: Run isolated Codex workers in parallel with strict path allowlists and coordinator merges.
* Current state: Wave 1 prompts generated; later pasted state says Wave 1 effectively complete.
* Desired end state: Multiple safe branches produce task-local evidence; coordinator serially merges and runs fast strict.
* Priority: P0
* Status: active

### WORKSTREAM-07 — Workbench validation and command/view spine
* Objective: Build a narrow Workbench/product spine through registered commands, typed results, semantic views, projections, diagnostics, and evidence.
* Current state: WORKBENCH-VALIDATION-SLICE-01 reportedly complete; next task is COMMAND-RESULT-VIEW-SLICE-01.
* Desired end state: One command/result/view/projection path works across CLI/headless/text/Workbench without private bypass.
* Priority: P0
* Status: active

### WORKSTREAM-08 — Service conformance, document/patch, project graph, composition law
* Objective: Define supporting laws needed before bigger Workbench/product work.
* Current state: Prompts generated; pasted state says complete or pass-with-warnings.
* Desired end state: Conformance, document/patch/transaction, graph, and composition models inform later runtime/product slices.
* Priority: P1
* Status: active

### WORKSTREAM-09 — Runtime/product spine slices
* Objective: Build package mount, replay proof, and barebones client shell after command/result/view proof.
* Current state: Planned; not yet executed in visible chat.
* Desired end state: Package/profile/content mount proof; deterministic replay proof; minimal client status/refusal shell.
* Priority: P1
* Status: planned

### WORKSTREAM-10 — Presentation/accessibility/localization spine
* Objective: Define semantic presentation, projection conformance, accessibility, and text/localization before rich UI.
* Current state: Planned after runtime/product checkpoint.
* Desired end state: CLI/TUI/headless/rendered/native projections share semantics; accessibility and localization not late afterthoughts.
* Priority: P2
* Status: planned

### WORKSTREAM-11 — Doctrine recovery and domain constitution
* Objective: Preserve long-running design doctrine and instantiate it into domain constitutions.
* Current state: Prompt generated; uploaded transcript says most doctrine preserved but deep primitives/failure/domain constitutions remain partial.
* Desired end state: Doctrine recovery matrix guides deep primitives, failure ontology, representation proof, domain constitutions, playable baseline.
* Priority: P2
* Status: active/planned

### WORKSTREAM-12 — Future game/product/domain expansion
* Objective: Eventually build playable baseline and domain/game slices: survival, fabrication, maintenance, settlements, logistics/economy, institutions, knowledge, civilization, conflict, offworld.
* Current state: Broad feature work currently blocked; future order planned.
* Desired end state: Gameplay/features enter as domain constitutions, bridges, capabilities, representations, failure models, proofs, not ad hoc features.
* Priority: P3
* Status: future


## Compact Registers for Merge

Use the separate registers file for full tables. Key task register begins with:
1. Verify live repo.
2. Generate COMMAND-RESULT-VIEW-SLICE-01.
3. Run PHASE-REVIEW-02.
4. PACKAGE-MOUNT-SLICE-01.
5. REPLAY-PROOF-SLICE-01.
6. BAREBONES-CLIENT-SHELL-01.

## Possible Cross-Chat Duplicates

Root cleanup, AIDE install, Foundation Lock, old doctrine specs, Workbench module brainstorming, C17/C++17 language baseline, 64-bit policy, and fast strict/full CTest split may overlap with other old chats.

## Possible Cross-Chat Conflicts

Watch for:
- C89/C++98 vs C17/C++17.
- Foundation blocked vs Foundation closed.
- Whether Wave 1 is actually merged.
- Whether Workbench validation slice is complete.
- Whether root cleanup is considered finished.

## Spec Book Integration Guidance

This chat should feed into architecture, repo governance, Workbench, command/view/projection, test/proof, portability, and doctrine chapters. Do not prematurely merge brainstormed game features as requirements unless backed by doctrine matrix/domain constitution tasks.

## Aggregator Warnings

Do not treat this as proof that runtime provider/module/package systems exist. Many are contract-level only. Verify live repo before acting.
