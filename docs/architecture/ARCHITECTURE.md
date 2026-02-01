Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Architecture (High-Level)





This document summarizes the current component boundaries and directory layout


for Dominium (product layer) and Domino (engine). See


`docs/architecture/DIRECTORY_CONTEXT.md` for the authoritative layout contract and


`docs/guides/DEPENDENCIES.md` for enforceable dependency rules.


Conceptual framing lives in `docs/architectureitecture/MENTAL_MODEL.md`.





## Top-level components


- `engine/` — Domino engine sources (deterministic core + runtime subsystems).


- `game/` — Dominium game sources (authoritative rules + domain logic).


- `client/` — client executable entrypoint.


- `server/` — server executable entrypoint.


- `launcher/` — launcher core and frontends.


- `setup/` — setup core and frontends.


- `tools/` — tool host plus validators/editors.


- `libs/` — shared interface libraries and contracts.


- `schema/` — data schemas and validation docs (data-only; no build targets).


- `legacy/` — archived sources excluded from current builds and checks.





## Layering model


### Domino engine (deterministic core + runtime subsystems)


- Deterministic simulation logic lives under `engine/modules/` and is C90.


- `engine/modules/system/` contains platform backends; it must not influence authoritative simulation state.


- Render backends live under `engine/render/` and are treated as derived output.





### Dominium game (authoritative rules + domain logic)


- Game logic lives under `game/core/`, `game/rules/`, and `game/economy/`.


- Game code uses engine public headers only; it must not include `engine/modules/**`.





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





## Public API boundaries


Public header paths and ABI rules are defined in `docs/specs/CONTRACTS.md`.





## Further reading


- `docs/architecture/ARCHITECTURE_LAYERS.md` (layer summary + target graph)


- `docs/architecture/ARCH_REPO_LAYOUT.md` (ownership map)


- `docs/guides/DEPENDENCIES.md` (allowed/forbidden edges)


- `docs/architecture/CANONICAL_SYSTEM_MAP.md` (canonical dependency map)


- `docs/architecture/INVARIANTS.md` (hard invariants)
