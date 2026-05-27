# Reader Brief — Dominium Canonical Structure and Domino Framework Architecture

This chat was about turning Dominium from a messy, repeatedly refactored game repository into a stable, reusable Domino/Dominium architecture. The central result is that the repo should have a closed root model, and the architecture should be contract-centered rather than folder-, UI-, app-, or vendor-centered.

## Top 20 things to know

1. Domino is the reusable deterministic/runtime substrate.
2. Dominium is the game/product family built on Domino.
3. Workbench is a production/evidence/editor surface, not authority.
4. AIDE is the repo/control-plane harness.
5. The canonical root model is mostly settled.
6. Do not add top-level `framework/`, `modules/`, `profiles/`, `labs`, or `src`.
7. Domino Framework lives in contracts, public surfaces, ABI law, service/provider law, and public headers.
8. Public headers live in `engine/include/domino`, `runtime/include/domino`, and `game/include/dominium` where needed.
9. Public ABI is C-compatible even though implementation is C17/C++17.
10. Raylib/SDL/Lua are providers, not architecture.
11. Provider implementations belong under `runtime/<service>/providers/<provider>`.
12. Provider choices belong in profiles, not app paths.
13. Third-party types must not leak into stable contracts/saves/replays/game law.
14. Workbench modules are UI modules only; general module law is under contracts/manifests/packs.
15. CLI/TUI/rendered/native/headless should be projections of the same semantic spine.
16. The spine is command → result/refusal → document/snapshot/patch → diagnostics/evidence → view/action → projection.
17. Multiple structure cleanup passes were reported and many active old paths were removed.
18. Structure is credible but still PASS_WITH_WARNINGS, not perfect.
19. Full CTest/T4 remains debt.
20. Next work should be proof hygiene, projection conformance, and provider wedges—not broad root cleanup.

## Best next step

Verify latest live repo gate state. If fast-strict/RepoX still fails on stale evidence or launcher marker debt, fix that first. If normal gates are clean, continue with `PROJECTION-CONFORMANCE-01`.
