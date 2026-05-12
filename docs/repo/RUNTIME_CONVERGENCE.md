Status: PROVISIONAL
Phase: CONVERGE-07
Supersedes: none
Superseded By: none
Stability: provisional

# Runtime Convergence

CONVERGE-07 consolidates safe runtime-facing source roots under `runtime/` without changing product identity, executable names, pack IDs, virtual-root IDs, renderer selection, AppShell mode resolution, or build semantics beyond path updates required by the move.

## What Moved

- `appshell/` moved to `runtime/appshell/`.
- `app/` moved to `runtime/app/`.
- `ui/` moved to `runtime/ui/`.
- `diag/` moved to `runtime/diagnostics/`.

## What Did Not Move

- `client/`, `server/`, `setup/`, and `launcher/` remain top-level product roots until CONVERGE-08.
- Domain roots remain in place until CONVERGE-09.
- `net/` remains a review root because it mixes transport, anti-cheat, SRZ, and server-authoritative policy code.
- `control/` and `core/` remain review roots because they are mixed and ownership-sensitive.
- `engine/`, `game/`, `contracts/`, content/data roots, archive roots, and generated roots were not moved.

## Runtime Boundaries

`runtime/` is not `apps/`. Product entrypoints and product identity stay out of runtime and move later under `apps/`.

`runtime/` is not engine truth. Runtime can host and adapt engine output, but authoritative deterministic substrate remains under `engine/`.

`runtime/` is not game or domain law. Domain semantics and Process mutation authority remain with game/domain ownership.

`runtime/` is not `contracts/`. Machine-readable schemas, registries, protocols, capabilities, compatibility, replay, ABI, repo, and distribution contracts remain under `contracts/`.

`runtime/` source is not generated runtime output. Logs, IPC sockets, process locks, caches, temp files, and mutable runtime stores belong to install/runtime projections, not source repo roots.

## AppShell, Platform, Render, And UI

AppShell owns bootstrap, command dispatch, mode resolution, virtual path binding, supervisor orchestration, IPC/logging orchestration, TUI shell support, and rendered-mode stubs.

Platform and render source should converge under `runtime/platform/` and `runtime/render/` only when real adapter source is moved or added. CONVERGE-07 did not create new platform or renderer backend behavior.

UI runtime source may present and route UI state. It must not mutate truth directly or own domain law.

## Future Work

- CONVERGE-08: product entrypoints into `apps/`.
- CONVERGE-09: domain split into contracts/game/content/docs/tests.
- CONVERGE-11: product, platform, render, native, toolchain, and packaging matrices.
- CONVERGE-12: stale-doc and cross-reference cleanup.
