# Context Transfer Packet — Dominium Foundation Lock, Workbench Spine, and Parallel Codex Handoff

## Ultra-Condensed Bootstrap Brief

This chat continued the Dominium project at `Julesc013/dominium`. It focused on the transition from repository cleanup into contract-governed product work. The final architecture is: Domino is the reusable deterministic/runtime substrate; Dominium is the game/product family; Workbench is the production, validation, editing, inspection, packaging, evidence, and agent-control environment; AIDE is the repo/control-plane harness; Codex is a bounded patch executor; contracts are law; tests/replay/diagnostics/evidence are proof.

The main principles are: path is not identity; implementation is not contract; UI is not authority; generated output is not source truth. Workbench must not become authority. It must call registered commands/services and display typed results/refusals/diagnostics/evidence. Broad gameplay, renderer, native GUI, provider runtime, package runtime, runtime module loading, broad Workbench shell, and public release remain blocked until narrower product/runtime slices prove the architecture.

The repo previously had major root cleanup frustration. The canonical root model is now treated as settled: `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, and `archive/`. Old roots like `core/`, `data/`, `lib/`, `validation/`, `meta/`, `net/`, etc. should not return.

Foundation Lock was once blocked by dependency-direction strict validation. Later state says `FOUNDATION-CLOSEOUT-02` closed Foundation Lock with warnings: dependency-direction strict passed with 0 violations and 68 warnings; fast strict passed; RepoX STRICT passed with stale AuditX warning; CMake configure/build and smoke CTest passed through fast strict; full CTest remains T4/full-gate debt. Narrow slices are allowed; broad feature work remains blocked.

The project baseline is C17 + C++17, C-compatible public ABI, 64-bit source-native for full products, little-endian mainline, fixed-width persisted data, no pointer-sized truth. 32-bit/vintage targets are constrained-native, contract-projection, or archive-runner lanes.

The user shifted to parallel Codex worktrees. Parallel workers must not push to main or edit global AIDE latest files. They must use task-local evidence, allowed paths, targeted validators, and local commits. Wave 1 prompts generated in this chat were: SERVICE-CONFORMANCE-LAW-01, DOCUMENT-PATCH-TRANSACTION-RUNTIME-01, PROJECT-GRAPH-SERVICE-01, COMPOSITION-RESOLVER-LAW-01, and DOMINIUM-DOCTRINE-RECOVERY-MATRIX-01. Latest pasted state says Wave 1 and WORKBENCH-VALIDATION-SLICE-01 are effectively complete. The next task is COMMAND-RESULT-VIEW-SLICE-01.

Recommended first action: verify live repo state, then generate COMMAND-RESULT-VIEW-SLICE-01 unless already run.

## Source Hierarchy

1. Direct user statements in this chat.
2. Explicit decisions accepted by the user.
3. Current task register.
4. Constraint register.
5. Artifact ledger.
6. Inferences.
7. Assistant suggestions not accepted by the user.
8. General model knowledge.

## Operating Rules for Future Assistants

- Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels.
- Verify stale live repo facts before relying on them.
- Do not re-ask already answered questions.
- Ask clarifying questions only if materially necessary.
- Do not invent missing details.
- Do not treat tentative plans as final.
- Do not repeat rejected options.
- Preserve artifacts and generated prompts.
- Use structured outputs for continuation.
- If generating Codex prompts, produce one large continuous code/text block.
- Do not run full CTest by default.
- Do not start broad feature work while current plan says blocked.

## Active Workstreams

Active: Foundation/product slice, command-result-view, parallel Codex execution, Workbench spine, runtime/product spine, portability architecture, doctrine recovery.

## Current Priorities

1. Verify live repo.
2. Generate/run COMMAND-RESULT-VIEW-SLICE-01.
3. Run PHASE-REVIEW-02.
4. Proceed to PACKAGE-MOUNT-SLICE-01, REPLAY-PROOF-SLICE-01, BAREBONES-CLIENT-SHELL-01.

## Current Open Questions

- Is Wave 1 merged/live?
- Has PORTABILITY-ARCH-POLICY-02 completed?
- Has COMMAND-RESULT-VIEW-SLICE-01 already run?
- What exact `dominium.validation.run` schemas exist?
- What warnings remain?

## Recommended First Action

Check live `origin/main`, current queue/status docs, and relevant audits. If the pasted state is still current, generate `COMMAND-RESULT-VIEW-SLICE-01`.
