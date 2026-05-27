# Reader Brief — Dominium Canon, Repository Alignment, and Portability Doctrine

## What this chat was about

This chat restored old Dominium v1 canon, audited current GitHub repository alignment, and developed a future-proofing doctrine for building Dominium/Domino as a reusable platform rather than a one-off game.

## Top 20 things to know

1. The old v1 Constitution and Glossary were pasted and used as baseline.
2. The live repo has materialized versions under `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.
3. Repo canon index says raw prompts are not authoritative unless materialized.
4. The repo has strong docs/schema/registry/governance alignment.
5. The repo has real deterministic code scaffolding, including RNG/world/session pipeline pieces.
6. Full gameplay/runtime implementation is not yet proven.
7. Survival exists strongly in registries, but concrete runtime Process implementation needs audit.
8. Advanced systems such as MMO distributed authority are not proven complete.
9. The user wants portability, modularity, extensibility, reuse, and replaceability.
10. The correct doctrine is stable contracts and replaceable implementations.
11. Ownership-root layout is preferred over generic `src`/`source`.
12. Current target roots include `apps`, `engine`, `game`, `runtime`, `contracts`, `content`, `docs`, `tests`, `tools`, `scripts`, `cmake`, `external`, `release`, `archive`.
13. Paths are storage; IDs/contracts define semantic identity.
14. Public Domino boundaries should be C-compatible and stable.
15. Schemas/protocols/saves/replays/packs need versioning and migration/refusal rules.
16. Apps should stay thin.
17. Runtime must not own simulation truth.
18. Tools must not become runtime dependencies.
19. Future cleanup must be gated and preserve IDs.
20. This package should feed the master spec book with labels preserved.

## Best next step

Verify current repo physical layout, exception ledger, public API inventory, and runtime implementation status before broad refactors or new feature work.

## Key files in this package

Read file 01 for the human explanation, file 04 for registers, file 05 for aggregator merge, and file 08 for future-chat bootstrap.
