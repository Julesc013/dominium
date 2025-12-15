# SPEC_RES — World Resources (RES)

This spec defines the deterministic world resource subsystem (`D_SUBSYS_RES`):
per-chunk resource channels, sampling, and delta application.

## Scope
Applies to:
- per-chunk resource channel state (`dres_channel_cell`)
- resource sampling (`dres_sample_at`) and mutation (`dres_apply_delta`)
- resource model dispatch (`dres_model_vtable`, `D_MODEL_FAMILY_RES`)
- deterministic resource worldgen population (current stub)
- save/load payload framing under `TAG_SUBSYS_DRES`

Does not define economy pricing, UI presentation, rendering, or platform IO.

## Owns / Produces / Consumes

### Owns (authoritative state)
RES owns resource channel state attached to chunks. For each loaded chunk, the
subsystem maintains zero-or-more `dres_channel_cell` entries:

- Descriptor: `dres_channel_desc { channel_id, model_family, model_id, flags }`
- Content references: `proto_id` (deposit proto), `material_id`, `tags`
- Params: `model_params` TLV blob (opaque to RES core; interpreted by the model)
- Values: fixed-point `values[DRES_VALUE_MAX]` and `deltas[DRES_VALUE_MAX]` (Q16.16)

Authoritative invariants:
- All values are fixed-point (no floats).
- Cell counts are bounded per chunk (`DRES_MAX_CELLS_PER_CHUNK` in the current
  implementation); RES MUST NOT grow unbounded data per tick.
- Authoritative state MUST NOT embed baked world-space mesh/triangle data.

### Produces (derived outputs)
- `dres_sample` results returned from `dres_sample_at` (read-only views).
- Optional indices/accelerators to speed sampling; any such structures are
  derived caches and MUST be rebuildable from authoritative cell state.

### Consumes
- Chunk partitioning (`d_chunk`) and deterministic world coordinates (`q32_32`).
- Deposit/material protos and tags from `content/d_content.h`.
- Model registry plumbing via `core/d_model.h` (family `D_MODEL_FAMILY_RES`).

## Determinism + ordering
- Model registration and dispatch MUST be deterministic:
  - model ids (`model_id`) are stable integers
  - dispatch MUST NOT depend on pointer identity or hash-table iteration
- Iteration over cells and serialization MUST use a stable, explicit order.
  Recommended canonical key: `(proto_id, channel_id, material_id)`.
- Sampling and delta application MUST NOT call OS APIs, read wall-clock time, or
  branch on non-deterministic inputs.

## Delta application (authoritative mutation)
`dres_apply_delta` is the authoritative mutation entry point for RES state.

Rules:
- Delta values MUST be quantized fixed-point values.
- Any stochastic behavior (if added later) MUST be derived only from explicit
  deterministic seed contexts (`seed_context`), never OS RNG.
- Applying a delta MUST be deterministic and side-effect free outside RES.
- Higher-level game logic MUST express RES mutations as deltas in SIM
  (`docs/SPEC_ACTIONS.md`).

## Save/load framing
- Subsystem id: `D_SUBSYS_RES` (`source/domino/core/d_subsystem.h`).
- Container tag: `TAG_SUBSYS_DRES` (`source/domino/core/d_serialize_tags.h`).
- Chunk payloads store RES per-chunk cells; instance/global payload is empty in
  the current implementation.

## Forbidden behaviors
- Treating derived caches (samples, indices) as authoritative truth.
- Hashing/serializing raw struct bytes that include padding/pointers.
- Unbounded per-tick allocation or OS interaction in deterministic paths.

## Source of truth vs derived cache
**Source of truth:**
- per-chunk `dres_channel_cell` arrays and their quantized values/deltas
- content identifiers referenced by those cells (`proto_id`, `material_id`, tags)

**Derived cache:**
- `dres_sample` outputs
- any accelerators/indices derived from cell state

## Implementation pointers
- Internal API: `source/domino/res/d_res.h`, `source/domino/res/d_res.c`
- Model params tags: `source/domino/content/d_content_extra.h`

## Related specs
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_PACKETS.md`
- `docs/SPEC_ACTIONS.md`
- `docs/SPEC_SIM.md`
- `docs/SPEC_DOMINO_SUBSYSTEMS.md`
