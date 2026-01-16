--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# SPEC_UNIVERSE_MODEL - Universe Graph and Identity

This spec defines the high-level universe model used by Dominium. It is a
deterministic, instance-scoped graph and does not imply any global directory.

## 1. Scope and storage
- A universe exists within an **instance** context.
- Universe data is stored and transferred via the universe bundle container
  (`docs/SPEC_UNIVERSE_BUNDLE.md`).
- Systems, bodies, frames, and topology bindings are stored in bundle chunks
  `SYSM`, `BODS`, `FRAM`, and `TOPB`.
- Baseline cosmos/system anchors are authored in core data packs; see
  `docs/SPEC_CORE_DATA.md` and `docs/SPEC_COSMO_CORE_DATA.md`.
- There is no mutable global universe directory.

## 2. Core node types (graph)
Minimum node types:
- **Filament**: logical grouping of clusters (cosmos lane).
- **Cluster**: logical grouping of galaxies (cosmos lane).
- **Galaxy**: logical grouping of systems.
- **System**: collection of bodies and local domains.
- **Body**: star/planet/moon with orbital parameters and topology bindings.
- **Surface**: local domain representation attached to a body.
- **Vessel**: movable entity that may be in local space or orbital space.
- **LocalDomain**: deterministic grid/anchor domain used by surface gameplay.

Edges are explicit and typed (e.g., Galaxy->System, System->Body, Body->Surface,
System->Vessel).

Cosmos-lane nodes (Filament/Cluster/Galaxy/System) are logical-only and do not
require physical coordinates. See `docs/SPEC_COSMO_LANE.md`.
Mechanics profiles define sim-affecting modifiers; astronomical labels and
positions are non-sim (`docs/SPEC_MECHANICS_PROFILES.md`).

## 3. Stable IDs and ordering
- Each node has a stable string ID (UTF-8, case-sensitive).
- Numeric `u64` IDs are derived via FNV-1a 64-bit.
- Deterministic ordering is by `(node_type, id_u64)` ascending.
- Graph traversal and serialization must follow the canonical order.

## 4. Identity binding (authoritative)
Universe identity binds to:
- `universe_id` (string + hash)
- instance identity
- content/pack graph digests
- sim-affecting flags digest
- cosmos graph hash
- timebase (`tick_index`, `ups`)

Mismatches require explicit refusal by default.

## Related specs
- `docs/SPEC_SPACETIME.md`
- `docs/SPEC_REFERENCE_FRAMES.md`
- `docs/SPEC_SYSTEMS_BODIES.md`
- `docs/SPEC_SURFACE_TOPOLOGY.md`
- `docs/SPEC_UNIVERSE_BUNDLE.md`
- `docs/SPEC_COSMO_LANE.md`
- `docs/SPEC_LOGICAL_TRAVEL.md`
- `docs/SPEC_CORE_DATA.md`
- `docs/SPEC_COSMO_CORE_DATA.md`
- `docs/SPEC_MECHANICS_PROFILES.md`
