# Dominium — Directory Context (Engine v0)

This repo is now organised around a deterministic C89 core with thin C++98 frontends. Anything that conflicts with this layout must be refactored to match.

## Top-level
- `/engine` — deterministic core, C89, fixed-point only. Builds `dom_engine` static library.
- `/runtime` — game-facing binaries (C++98). May use floats internally for rendering/UI but never feed them back into engine state. `dom_cli` is the headless runner; `dom_sdl` is a stub placeholder.
- `/launcher` — C++98 stub that prepares runtime invocations; reads metadata only and does not touch sim state.
- `/tools` — offline utilities. `dom_inspect` and `dom_validate_content` reuse engine IO; no format reimplementation.
- `/content` (future) — data packs/mod packs. Data-first; loaded via registries.
- `/docs` — specs and context (this file, SPEC_CORE, DATA_FORMATS, MILESTONES).
- `/tests` — deterministic smoke tests that link against the engine.
- Legacy directories remain but are no longer authoritative; new work should follow this layout.

## Language/float rules
- `/engine`: C89, no floats/doubles, no platform/renderer/audio headers.
- `/runtime`, `/launcher`, `/tools`: C++98 allowed, floats allowed internally, but all calls into the engine use fixed-point and integer APIs only.

## Build targets
- `dom_engine` (static lib) from `/engine`.
- `dom_cli` and `dom_sdl_stub` from `/runtime`.
- `dom_launcher` from `/launcher`.
- `dom_inspect`, `dom_validate_content` from `/tools`.
- `dom_tests` from `/tests`.

## Data and IO
- Authoritative formats live in `docs/DATA_FORMATS.md` and the headers under `/engine/save_*.h`.
- Offline tools must consume engine IO modules rather than rolling their own parsers.

Keep these constraints in mind when adding modules or wiring new frontends. Determinism and layering trump convenience.
