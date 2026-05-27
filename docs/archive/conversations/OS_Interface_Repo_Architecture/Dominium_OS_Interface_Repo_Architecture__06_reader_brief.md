# Reader Brief — Dominium OS-like Architecture, Repository Convergence, and Interface Operating Layer

This chat preserved a major architectural synthesis for Dominium. The most important idea is that Dominium should be treated as a deterministic simulation operating environment with a reusable Interface Operating Layer.

## Top 20 Things to Know

1. CLI is mandatory, TUI expected, GUI modular.
2. GUI shells are thin projections over command/service contracts.
3. Current repo authority is post-CONVERGE roots.
4. Domain work splits across contracts/game/content/docs/tests.
5. Current code is partly modular but not fully data-driven.
6. Product boot proof was partial/blocked in inspected docs.
7. The OS-like reframing is the strongest conceptual direction.
8. Engine is conceptually kernel-like, but physical rename is unresolved.
9. Workbench replaces old UI Editor / Tool Editor final product.
10. Workbench is modular shell plus modules, not monolithic editor.
11. Interface Operating Layer is broader than Workbench.
12. No-assets GUI is guaranteed floor.
13. Rendered mode currently conflicts with AppShell client-only rule.
14. Rendered mode should become product-declared by capability.
15. Shipped modules should not depend on repo-only `tools/`.
16. Command dispatch must be unified.
17. First modules should be Validation Dashboard and Pack Browser.
18. Boot-to-replay is the best MVP definition.
19. Packaging should be deterministic and manifest-driven.
20. Future assistants must not overstate implementation status.

## Best Next Step

Draft `INTERFACE-LAW-00` and `DOMINIUM_OPERATING_ENVIRONMENT.md`, then turn them into PR-sized tasks after verifying current repo state.
