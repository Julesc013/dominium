# Reader Brief — Dominium Canonical Architecture, Repository Foundation, and Provider Model

This package preserves a long chat about fixing Dominium’s repository structure and broader architecture. The top things to know are:

1. The user wanted to end months of structure churn and get back to building real systems.
2. The top-level root model is now settled and should not be casually changed.
3. No first-party `src/` or `source/` wrappers.
4. Domino is the reusable substrate/framework; Dominium is one game/product family.
5. Workbench is a production environment, not the authority.
6. Contracts define law; runtime implements; apps compose; content supplies payload; tools validate; tests prove.
7. Stable IDs and public contracts matter more than stable private folders.
8. C17+C++17 is the mainline baseline, with C-compatible public ABI.
9. Raylib, SDL2, Lua, ImGui, raygui, rlgl, rlsw, and raudio are providers, not architecture.
10. Providers live under `runtime/<service>/providers/<provider>/`.
11. Apps should not encode provider choices in paths.
12. Profiles select provider combinations.
13. Module identity is not path; Workbench modules are one consumer of the module system.
14. CLI/TUI/rendered/native/headless are projections over shared semantic contracts.
15. Full CTest/T4 remains release/full-proof debt.
16. Fast strict is the normal development gate.
17. Stale structure reports were a recurring risk.
18. Do not treat assistant brainstorms as decisions unless the user accepted them.
19. Future work should be targeted, not another root-structure reset.
20. Best next action is to verify current live repo status and proceed with proof hygiene or projection conformance depending on gate status.
