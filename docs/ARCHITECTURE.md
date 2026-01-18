# Architecture (High-Level)

This document summarizes the current component boundaries and directory layout
for Dominium (product layer) and Domino (engine). See `docs/DIRECTORY_CONTEXT.md`
for the authoritative layout contract and `docs/DEPENDENCIES.md` for enforceable
dependency rules.

## Top-level components
- `engine/` — Domino engine library (`domino_engine`), public headers in `engine/include/`.
- `game/` — Dominium game library (`dominium_game`), public headers in `game/include/`.
- `client/` — client executable (`dominium_client`) linking engine + game.
- `server/` — server executable (`dominium_server`) linking engine + game.
- `launcher/` — launcher core library + CLI/GUI/TUI frontends.
- `setup/` — setup core library + CLI/GUI/TUI frontends.
- `tools/` — tools host + validators/editors (some tools link engine; most link libs/contracts).
- `libs/` — interface libraries (`base`, `crypto`, `fsmodel`, `netproto`, `contracts`).
- `schema/` — data schemas and validation docs (data-only; no build targets).
- `legacy/` — archived sources excluded from current builds and checks.

## Layering model
### Domino engine (deterministic core + runtime subsystems)
- Deterministic simulation logic lives under `engine/modules/` and is C90.
- Public engine APIs live under `engine/include/domino/`.
- `engine/modules/system/` contains platform backends; it must not influence authoritative simulation state.
- Render backends live under `engine/render/` and are treated as derived output.

### Dominium game (authoritative rules + domain logic)
- Game logic lives under `game/core/`, `game/rules/`, and `game/economy/`.
- Game code uses engine public headers only; it must not include `engine/modules/**`.
- Public game APIs live under `game/include/dominium/`.

### Product executables
- `client/` and `server/` are entrypoints that link `domino_engine` + `dominium_game`.
- `launcher/` provides product orchestration and links `engine::domino` + `libs::contracts`.
- `setup/` provides installation flow and links `libs::contracts`.
- `tools/` hosts offline tooling; some tools link `engine::domino` (e.g., `data_validate`).

## Dependency directions (summary)
- `engine/` → (no top-level product directories)
- `game/` → `engine/`
- `client/`, `server/` → `engine/` + `game/`
- `launcher/` → `engine/` (public) + `libs/` (`contracts`)
- `setup/` → `libs/` (`contracts`)
- `tools/` → `libs/` (`contracts`) and select engine public APIs
- `libs/` → leaf (no engine/game/launcher/setup/tools dependencies)
- `schema/` → data-only (no code dependencies)

## Public header boundaries
- `engine/include/**` is the only public engine API surface.
- `game/include/**` is the only public game API surface.
- `launcher/include/**` and `setup/include/**` expose their product APIs.
- `engine/modules/**` and `engine/render/**` are internal.

## Further reading
- `docs/ARCHITECTURE_LAYERS.md` (layer summary + target graph)
- `docs/ARCH_REPO_LAYOUT.md` (ownership map)
- `docs/DEPENDENCIES.md` (allowed/forbidden edges)
