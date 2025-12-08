# Dominium Rules Surface

The Dominium rules layer exposes a small C89-friendly API that sits **behind** `dom_core`, `dom_sim`, and `dom_canvas`. It is not a cross-process ABI; it is a local facade used by the game runtime and, later, by the SDK. Each public struct begins with `{struct_size, struct_version}` and all handles are opaque integers.

## Header Map
- `game_api.h` — runtime entry points for creating/destroying the game runtime and handling command/query calls routed from `dom_core`.
- `world.h` — surface lifecycle and frame acquisition; seeds/tiers and surface handles live here.
- `content_materials.h` — material registry bridging game-specific ids to Domino material entries.
- `content_parts.h` — block/beam/machine part registry with part kinds and default materials.
- `content_prefabs.h` — prefab/blueprint descriptors referencing part ids.
- `constructions.h` — construction instances (vehicles/buildings) spawned from prefabs onto surfaces.
- `net_power.h` — power network context with node/link registration.
- `net_fluid.h` — fluid/gas network context with node/link registration.
- `net_data.h` — logical/data network context with node/link registration.
- `actors.h` — player/NPC/robot lifecycle and life-support state.
- `environment.h` — sampling weather/atmosphere/radiation fields and ticking environment solvers.
- `economy.h` — market/company/trade scaffolding and price queries.

## Placement in the Stack
- Domino ABIs live in `include/domino/` and are the only cross-module ABI used by `dom_core`, `dom_canvas`, and `dom_sim`.
- Dominium rules APIs are **game-facing** and assume in-process calls; they never include platform or renderer headers directly.
- Future SDK bindings will sit on top of these headers while still flowing through Domino core dispatch (`dom_core_dispatch/query`).

## System Sketches
- **Surfaces + Space** — `world.h` seeds and tiers define surfaces; callers acquire/release frames via surface ids. Space/orbital domains will be layered as additional surface kinds when the solvers exist.
- **Constructions** — `constructions.h` spawns construction instances from prefab ids onto surfaces using world coordinates (`WPosExact`). Constructions are treated as graphs of parts that feed into the network systems.
- **Networks** — `net_power.h`, `net_fluid.h`, and `net_data.h` register nodes/links associated with constructions and surfaces; each exposes a single `step` entry point for deterministic solves per tick.
- **Environment & Economy** — `environment.h` samples local atmospheric/hydrology/radiation state and ticks environment solvers; `economy.h` seeds markets, exposes deterministic price quotes, and records trade submissions.

Stub implementations currently return `DOM_STATUS_UNSUPPORTED`; behaviour contracts will be filled in alongside the simulation code in later milestones.
