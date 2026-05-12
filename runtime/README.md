# Runtime Root

Status: PROVISIONAL
Phase: CONVERGE-07

`runtime/` is the canonical source root for host-facing runtime infrastructure. It owns AppShell, platform adapters, render adapters, UI adapters, input/audio/network/storage adapters, diagnostics, IPC, logging, supervisor support, CLI/TUI shell support, and mode-selection implementation.

Runtime may host, adapt, present, route, persist, observe, and diagnose. Runtime does not own simulation truth, game/domain law, product identity, pack authority, schemas, registries, protocol contracts, generated runtime output, log output, cache output, or install/runtime store projections.

## Subroots

- `runtime/app/`: shared C app-runtime helpers, read-only adapters, UI event helpers, and app-facing runtime support.
- `runtime/appshell/`: product bootstrap, command dispatch, mode resolution, virtual path binding, supervisor, IPC, logging, TUI, and rendered-mode shell support.
- `runtime/diagnostics/`: deterministic repro and diagnostic bundle source.
- `runtime/ui/`: shared UI model and UI runtime adapter surfaces.
- `runtime/process_spawn.py`: process-hosting helper retained at the runtime root until later subroot refinement.

Future runtime subroots such as `runtime/platform/`, `runtime/render/`, `runtime/input/`, `runtime/audio/`, `runtime/network/`, `runtime/storage/`, `runtime/ipc/`, `runtime/logs/`, `runtime/supervisor/`, `runtime/tui/`, `runtime/cli/`, and `runtime/modes/` may be created only when real source material is moved or added there.

## Boundaries

- Engine truth remains under `engine/`.
- Game/domain logic remains under `game/` or current domain roots until CONVERGE-09.
- Product entrypoints remain under `client/`, `server/`, `setup/`, and `launcher/` until CONVERGE-08.
- Machine-readable schemas, registries, and contracts remain under `contracts/`.
- Authored packs, profiles, fixtures, datasets, and assets belong under `content/` after content convergence.
- Generated runtime logs, IPC sockets, locks, caches, and temp files belong to install/runtime projections, not source `runtime/`.

Root-level `app/`, `appshell/`, `ui/`, and `diag/` are retired after CONVERGE-07. Root-level `net/`, `control/`, and `core/` remain review roots because they are mixed and cannot be moved wholesale without deeper ownership inspection.
