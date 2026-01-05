# SPEC_UNIVERSE_MODEL - Universe Graph and Identity

This spec defines the high-level universe model used by Dominium. It is a
deterministic, instance-scoped graph and does not imply any global directory.

## 1. Scope and storage
- A universe exists within an **instance** context.
- Universe data is stored and transferred via the universe bundle container
  (`docs/SPEC_UNIVERSE_BUNDLE.md`).
- There is no mutable global universe directory.

## 2. Core node types (graph)
Minimum node types:
- **Galaxy**: logical grouping of systems.
- **System**: collection of bodies and local domains.
- **Body**: star/planet/moon with orbital parameters and surfaces.
- **Surface**: local domain representation attached to a body.
- **Vessel**: movable entity that may be in local space or orbital space.
- **LocalDomain**: deterministic grid/anchor domain used by surface gameplay.

Edges are explicit and typed (e.g., Galaxy->System, System->Body, Body->Surface,
System->Vessel).

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
- timebase (`tick_index`, `ups`)

Mismatches require explicit refusal by default.

## Related specs
- `docs/SPEC_SPACETIME.md`
- `docs/SPEC_REFERENCE_FRAMES.md`
- `docs/SPEC_UNIVERSE_BUNDLE.md`
