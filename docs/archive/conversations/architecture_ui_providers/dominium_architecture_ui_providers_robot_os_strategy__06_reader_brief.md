# Reader Brief — Dominium Architecture, UI, Providers, and Robot OS Strategy

This chat is a major Dominium convergence chat. The top 20 things to know:

1. Dominium should be a long-lived platform, not a one-off game.
2. The core architecture is service-first, provider-backed, profile-selected, contract-governed, third-party-fenced.
3. C17/C++17 is the current mainline language baseline.
4. Public/stable boundaries should remain C-compatible, POD/versioned, and explicit.
5. First-wave floors are Windows 7 SP1+, Mac OS X 10.9.5+, and Linux, subject to verification.
6. Old renderers such as OpenGL 1.1/2.1 and Direct3D 9 are back-port/research, not first wave.
7. OpenGL 3.3 is first direct hardware renderer; Direct3D 11 follows; Metal/Vulkan later.
8. Software renderer remains important for fallback, CI, reference, and evidence.
9. `vector2d` is not a renderer backend; drawing/canvas is a feature layer.
10. raylib, rlgl, rlsw, raygui, raudio, SDL2, and Lua are providers, not architecture.
11. Third-party types must not leak into engine/game/contracts/content/saves/replays/packs/public SDK.
12. Apps stay generic; provider choices are profiles.
13. Workbench authors Dominium UI documents, not raygui or raylib objects.
14. CLI/TUI/rendered/native/immersive are projections of one command/action/view/document system.
15. Dominium should be a robotic seed-civilisation game.
16. Players are robots or machine consciousnesses, not human labour managers.
17. The mothership provides knowledge and precision but not infinite scale.
18. Nanotech is a construction actuator, not magic.
19. UI should feel like a customizable robot operating system.
20. Fog-of-war and UI epistemics are sensor/network/permission constrained.

Best next step: implement PROVIDER-WEDGE-01 and ROBOT-OS-WEDGE-01 specs.
