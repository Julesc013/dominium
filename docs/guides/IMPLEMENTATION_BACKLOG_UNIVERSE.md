Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Universe / Spacetime Expansion Backlog (M1 Audit)

This list captures stub/TODO locations relevant to the universe/spacetime/
orbits/calendars/portability/migration expansion. It is an audit baseline for
scaffolding work and future implementation.

| Path | Stub/TODO description | Planned owner/module |
| --- | --- | --- |
| `source/dominium/game/runtime/dom_game_runtime_placeholder.c` | Placeholder translation unit for runtime skeleton. | Runtime kernel and universe modules (`dom_universe_bundle`, `dom_frames`, `dom_orbit_lane`, `dom_calendar`). |
| `source/dominium/game/rules/rules_stub.c` | `dominium_rules_init` stub with no rule system wiring. | Game rules layer once universe model and deterministic scheduling are defined. |
| `source/dominium/common/dom_paths.cpp` | TODO: replace `file_exists`/`dir_exists` helpers with dedicated `dsys` interfaces. | Filesystem contract helpers used by instance/universe tooling. |
| `source/dominium/common/dom_packset.cpp` | TODO: dependency resolution and conflict detection. | Packset/identity resolution and migration gating. |
| `docs/specs/SPEC_WORLD_COORDS.md` | Environment transition helpers are stubbed for high-atmo/orbit. | Reference frames + orbit lane integration. |
| `docs/specs/SPEC_VEHICLES.md` | Integrators and orbit transitions are stubbed. | Orbit lane scaffolding and frame transforms. |
| `docs/specs/SPEC_ORBITS.md` | Radiation/belt environment queries are deterministic stubs. | Orbit/space environment scaffolding. |
| `docs/REPORT_GAME_ARCH_DECISIONS.md` | Notes legacy `dm_sim_tick(dt_usec)` stub path and runtime/frontends placeholders. | Spacetime canonical types + runtime kernel hardening. |
| `docs/specs/SPEC_DOMINIUM_RULES.md` | Stubbed network/economy/environment hooks. | Rules integration after universe model is defined. |