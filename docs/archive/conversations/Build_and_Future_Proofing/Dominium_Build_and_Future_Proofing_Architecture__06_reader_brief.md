# Reader Brief — Dominium Build and Future-Proofing Architecture

## What this chat was about

This chat asked how Dominium should be engineered so it remains portable, modular, extensible, reusable, compatible with old and new toolchains, and safe to refactor over time. It focused first on build/toolchain governance and then on broader source-structure/API/schema/rewrite discipline.

## Top 20 things to know

1. User's canon: C89 engine, C++98 game, determinism, per-floor artifacts, no CRT mixing, no silent API creep.
2. Build complexity comes from many machines and historical toolchains.
3. More hand-written presets are not the optimal solution.
4. Build truth should live in tuple contracts.
5. Local machine probes should generate local `CMakeUserPresets.json`.
6. CMake remains build authority.
7. AIDE should probe/explain/generate/verify/record evidence.
8. XStack orchestrates; RepoX/TestX enforce/prove.
9. Dist/package manifests should preserve artifact identity.
10. Dominium should be treated as an engine platform, not a one-off game.
11. Freeze contracts, not implementations.
12. The current top-level repo spine is close to right.
13. Deeper boundaries and naming still need cleanup.
14. Public surface registry is a key missing mechanism.
15. Replacement protocol is a key missing mechanism.
16. Dependency-edge enforcement is needed.
17. ABI/header conformance tests are needed.
18. Schema/protocol compatibility fixtures are needed.
19. Many recommendations are not yet accepted decisions.
20. Verify live repo state before implementation.

## Best next step

Ask: "Which recommendation should become canon first: public surface registry or tuple-driven build contracts?" Then verify current repo state and write a narrow implementation prompt.
