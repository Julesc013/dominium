# Travel and Transport Baseline (TRAVEL0)

Status: binding for T8 baseline.  
Scope: deterministic movement cost and feasibility across terrain, weather, and structures.

## What travel is in T8
- Travel is movement through space with **explicit, additive costs**.
- Movement feasibility and cost are derived from **fields**, not from meshes.
- Pathfinding is **local, interest-bounded, deterministic**, and cached/disposable.

## Travel field stack (authoritative)
Required fields:
- `travel.cost` (terrain + structure adjustments)
- `travel.obstacle` (0..1)
- `travel.weather_modifier`
- `travel.mode_modifier`

All numeric values are unit-tagged per `docs/architecture/UNIT_SYSTEM_POLICY.md`.

## Structures, roads, and bridges
- Roads/paths/bridges are **assemblies** that modify travel cost.
- Structures can mark obstacles without special casing “building vs terrain.”
- Destruction and placement are process-driven (see T7).

## Vehicles (simple, assembly-backed)
- Vehicles are assemblies tied to travel modes.
- Modes carry mass/inertia and cost modifiers.
- No cargo, fuel, or logistics chains are included.

## Weather interaction (symbolic)
- Rain/snow and surface wetness add deterministic cost modifiers.
- Temperature extremes add symbolic penalties within data-defined bounds.
- No fluid dynamics or erosion is performed here.

## Pathfinding rules (T8 baseline)
- Local, hierarchical (coarse → fine), and **bounded by budgets**.
- Deterministic tie-breaking and fixed sampling order.
- Cached paths are disposable and never authoritative.

## What is NOT included yet
- No teleportation or fast-travel abstractions.
- No global scans or per-tick recomputation.
- No trade/logistics/economy or fuel chains.

## Collapse/expand compatibility
Travel collapse stores:
- total road length per domain (coarse)
- average travel cost and distribution histograms

Expanded domains reconstruct travel deterministically from these summaries.

## Maturity labels
- Travel fields: **BOUNDED** (deterministic field queries).
- Pathfinding: **BOUNDED** (local, bounded search).
- Vehicles: **BOUNDED** (assembly-linked, no logistics).

## See also
- `docs/architecture/TRAVEL_AND_MOVEMENT.md`
- `docs/architecture/NO_MAGIC_TELEPORTS.md`
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`
