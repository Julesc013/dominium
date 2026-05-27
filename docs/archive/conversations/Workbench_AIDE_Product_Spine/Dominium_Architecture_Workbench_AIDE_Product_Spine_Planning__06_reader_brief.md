# Reader Brief — Dominium Architecture, Workbench, AIDE, and Product-Spine Planning

## What this chat was about

This chat preserved and refined the architecture, repo-control strategy, Workbench plan, AIDE development model, and immediate product-spine task sequence for Dominium. It established Dominium as a deterministic, contract-governed simulation platform, not merely a game. Domino is the reusable substrate; Dominium is the product/game family; Workbench is the production and validation environment; AIDE is the repo control plane; Codex is the bounded patch executor.

## Top 20 things to know

1. Foundation Lock is PASS_WITH_WARNINGS, not clean.
2. Fast strict passes; full CTest remains T4 debt.
3. Dependency-direction has 0 violations but known warnings.
4. Broad feature work remains blocked.
5. Package mount slice is complete only as fixture-level proof.
6. Replay proof is the next product-spine task if not already run.
7. Barebones client follows replay proof.
8. Product Spine Review follows replay + barebones.
9. Workbench is not authority.
10. AIDE should manage task branches, blockers, repairs, and checkpoints.
11. Dev should be non-blocking; main should be evidence-blocked.
12. Agents should use task branches/worktrees, not shared dev directly.
13. Paths are not identity.
14. Implementation is not contract.
15. UI modes are projections, not separate systems.
16. Public ABI remains C-compatible.
17. C17/C++17 is intended target baseline; verify live build files.
18. Full gameplay/worldgen work is deferred.
19. Presentation contracts are a near-future task.
20. Verify live queue before generating any new prompt.

## Best next step

Check live repo state and determine whether QUEUE-RECONCILE-01, REPLAY-PROOF-SLICE-01, and BAREBONES-CLIENT-SHELL-01 have run. Then generate the next missing prompt.
