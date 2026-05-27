# Reader Brief — Domino Framework and Open-Source Provider Architecture

## What this chat was about

This chat developed a framework/provider strategy for Dominium. The user wanted to accelerate development with open-source code while preserving portability, modularity, extensibility, determinism, and future replaceability. The final architecture is Domino Framework + Domino engine implementation + Dominium game implementation. Third-party libraries become providers.

## Top 20 things to know

1. Use the framework approach, not a monolithic fork.
2. Domino Framework defines contracts and provider ABI.
3. A Domino engine implementation provides services.
4. Dominium is one game implementation using those services.
5. raylib is a first visible provider suite, not the engine.
6. `rlsw` is a raylib software provider, not Dominium reference renderer.
7. `rlgl` is an OpenGL-family provider, not final `opengl33`.
8. `raygui` is Workbench/debug UI provider, not UI document law.
9. `raudio` is audio provider.
10. `raymath` is render/editor math only.
11. SDL2 remains platform/input/audio provider.
12. Lua should be pinned behind `dominium.script.v1`.
13. Use `runtime/<service>/providers/<provider>`.
14. Apps remain generic; profiles select providers.
15. Third-party types are forbidden in contracts/game/content/saves/replays.
16. External games/engines are mostly references.
17. Sparse deterministic delegated simulation is core future architecture.
18. Clients can compute but host verifies results.
19. CAD creations compile into bounded runtime graphs.
20. Next step is `DOMINO-FRAMEWORK-WEDGE-01`.

## Decisions

See Decision Register. Most important: framework/provider architecture, raylib as first provider suite, service-first layout, profiles for provider selection, Lua/SDL2 as first-wave providers, and sparse deterministic delegated simulation as design doctrine.

## Pending tasks

Top tasks: verify repo baseline, draft framework ABI, add provider manifests, add forbidden include validator, implement null providers, implement raylib providers, create profiles, and define work-lease/CAD schemas.

## Open questions

Main open questions: dependency versions, C17/C++17 repo state, Lua version, framework ABI, profile order, deterministic class, license policy, CAD graph scope, and distributed compute verification.

## Artifacts

Primary artifact: uploaded preservation prompt. This package creates the full handoff files and ZIP.

## Verification items

Verify repository state, raylib/SDL2/Lua versions and platform support, licenses for reference projects, and any second-wave dependency licenses.

## Best next step

Draft `DOMINO-FRAMEWORK-WEDGE-01` into an implementation-ready PR plan.
