Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Dominium — Data Formats (Engine v0)

All supported runtime targets are little-endian. Deterministic artifacts are integer/fixed-point-only; unknown sections are skipped, not rejected. For ABI-stable containers and explicit parsing rules, see `docs/specs/SPEC_CONTAINER_TLV.md`.

## 1. Fixed-point encoding
- `fix32` (Q16.16) is stored as signed 32-bit.
- `fix16` (Q4.12) is stored as signed 16-bit.
- Angles use unsigned integers (`u16` preferred; compressed `u8` allowed for mods if documented).

## 2. Universe metadata (`universe.meta`)
Binary blob holding:
```
u32 version;          /* current spec uses 1 */
u64 universe_seed;
```
`version` gates migrations; unknown versions must be rejected or migrated explicitly.

## 3. Surface metadata (`surface_XXX.meta`)
One file per surface (XXX = zero-padded id):
```
u32     version;      /* current spec uses 1 */
u32     surface_id;
u64     seed;
u32     recipe_id;
RNGState rng_weather; /* two u64s */
RNGState rng_hydro;
RNGState rng_misc;
```
All deterministic RNG state lives here, never inside chunks.

## 4. Region files (`regions/surface_XXX_region.bin`)
Container for chunk blobs.

### Header
```
u32 magic   = 'REGN';
u16 version = 1;
u16 chunk_count;
```
Followed by `chunk_count` `ChunkEntry` records:
```
ChunkKey3D key; /* i32 gx, gy, gz */
u32       offset; /* from file start to chunk blob */
u32       length; /* bytes of the chunk blob */
```
Offsets point into the same file. Entries are unsorted; readers should iterate in file order for determinism.

### Chunk blob layout
Sequence of TLV sections; each section begins with:
```
u32 type;
u16 version;
u16 reserved;
u32 length;   /* payload bytes that follow immediately */
```
Engine-reserved section types:
- `1` `CHUNK_SEC_TERRAIN_OVERRIDES`
- `2` `CHUNK_SEC_OBJECTS`
- `3` `CHUNK_SEC_EDIT_OPS`
- `4` `CHUNK_SEC_LOCAL_VOLUMES`
- `5` `CHUNK_SEC_LOCAL_ENV_STATE`
- `6` `CHUNK_SEC_LOCAL_NET_STATE`
- `>=1000` reserved for mods/third parties.

Unknown `type` values are skipped using `length`. An empty section is legal and uses `length=0`.

## 5. Positions in saves
- Chunk-local positions use `SaveLocalPos`:
  - `chunk_x/chunk_y/chunk_z` (u16) identify the chunk within a region.
  - `lx/ly/lz` are `fix16` offsets inside the 16×16×16 m chunk.
- Chunk keys (`ChunkKey3D`) store global chunk indices; the combination of `ChunkKey3D` + `SaveLocalPos` can reconstruct a `SimPos` deterministically.

## 6. Determinism rules for IO
- All numeric fields are explicit; no padding/implicit defaults.
- Readers must tolerate extra sections and forward-compatible versions by skipping unknown TLVs.
- Writers must fill version fields and reserve ranges for mods (1000+).
- RNG state is only persisted in `SurfaceMeta`. Chunk caches are regenerable and not authoritative.

This file and `engine/save_*.h` define the authoritative on-disk shapes for v0. Future changes must bump versions and keep skip-friendly framing.

## 7. Packs and mods on disk
- Root is `DOMINIUM_HOME/repo`.
- Packs: `repo/packs/<pack_id>/<version>/pack.tlv` (single TLV per version). Version directories are 8-digit, zero-padded integers (e.g. `00000001`). The built-in base pack lives at `repo/packs/base/00000001/pack.tlv`.
- Mods: `repo/mods/<mod_id>/<version>/mod.tlv` with the same zero-padded version directory rule. Future optional override assets live alongside the TLV.
- Engine does not assume any specific content inside those TLVs beyond schema ids and fields; base is only special by identity and load order.

## 8. TLV schema registry
- Schemas are keyed by `d_tlv_schema_id` + `version`.
- Descriptor: `d_tlv_schema_desc { schema_id, version, validate_fn }`.
- Validation: `d_tlv_schema_validate(id, version, in, out_upgraded)` calls the registered `validate_fn` (optionally producing an upgraded blob).
- Intent: central place to gate pack/mod/blueprint/save TLVs and stage migrations in future passes.

## 9. Subsystem TLV containers
- Per-subsystem payloads are wrapped in TLVs tagged with `TAG_SUBSYS_*` (world/res/env/build/trans/struct/veh/job/net/replay; mods reserve 0x2000+).
- Save/load orchestrator iterates registered subsystems and calls their hooks, appending `(tag,len,payload)` triples into a single container blob.
- Unknown tags are ignored by readers; missing tags mean the subsystem contributed no data for that chunk/instance.
- Current `d_serialize` framing stores `tag` and `len` as native-endian `u32` values via `memcpy` (little-endian on supported hosts); see `source/domino/world/d_serialize.c`.

## 10. Pack and mod TLVs
- Pack TLV schema: `D_TLV_SCHEMA_PACK_V1` (0x0201), version 1.
  - Fields: `id` (u32), `version` (u32), `name` (string), `description` (string), `content` (TLV blob containing prototypes).
- Mod TLV schema: `D_TLV_SCHEMA_MOD_V1` (0x0202), version 1.
  - Fields: `id` (u32), `version` (u32), `name` (string), `description` (string), `deps` (TLV for dependencies), `content` (TLV blob with mod-defined prototypes).
- Unknown fields are ignored so packs/mods can extend their own metadata without breaking the engine.

## 11. Prototype TLV schemas
- All prototype records are stored as TLVs with schema ids:
  - Materials `D_TLV_SCHEMA_MATERIAL_V1` (0x0101), items `0x0102`, containers `0x0103`, processes `0x0104`, deposits `0x0105`, structures `0x0106`, vehicles `0x0107`, spline profiles `0x0108`, job templates `0x0109`, building protos `0x010A`, blueprints `0x010B`.
- Common fields:
  - `id` (u32) and `name` (string) are required for all protos.
  - `tags` (u32 bitmask) is optional but shared across types.
- Type-specific fields:
  - Material: `density`, `hardness`, `melting_point`, `permeability`, `porosity`, `thermal_conductivity`, `erosion_resistance` as Q16.16 (stored as signed 32-bit).
  - Item: `material_id`, `unit_mass`, `unit_volume`.
  - Container: `max_volume`, `max_mass`, `slot_count`, `packing_mode`, `params`.
  - Process: `params` blob for I/O definitions.
  - Deposit: `material_id`, `model_id` (u16), `model_params`.
  - Structure: `layout`, `io`, `processes` blobs.
  - Vehicle: `params` blob.
  - Spline profile: `type`, `flags`, `base_speed`, `max_grade`, `capacity`, `tags`, `params`.
  - Job template: `params` blob.
  - Building: `shell` blob and `params`.
  - Blueprint: opaque `payload` blob.
- Loaders validate TLV framing via the schema registry, then map fields directly into runtime prototype structs without injecting game-specific behavior.

### 11.1 Nested parameter TLVs (selected)
- `structure.layout` and `vehicle.params` may include an environmental volume graph:
  - `D_TLV_ENV_VOLUME` records with local AABB fields `MIN_*`/`MAX_*` (Q16.16, local coordinates).
  - `D_TLV_ENV_EDGE` records connecting local volumes (`A`,`B`), where `B=0` means exterior coupling; includes `GAS_K` and `HEAT_K` conductances (Q16.16).
  - Optional `D_TLV_ENV_HYDRO_FLAGS` (u32 bitmask) for generic hydrology interactions.
- `job_template.params` may include environment constraints:
  - `D_TLV_JOB_ENV_RANGE` records with `FIELD_ID` (u16) and `MIN`/`MAX` (Q16.16), evaluated against `d_env_sample_at` at the job target position.

## 12. Legacy game save blob (dom_game_save)
`source/dominium/game/dom_game_save.cpp` writes a minimal world snapshot format for local saves.

Framing (repeated records until EOF):
```
u32 tag;      /* native-endian (little-endian on supported hosts) */
u32 len;      /* native-endian */
u8  payload[len];
```

Known top-level tags:
- `1` (`TAG_INSTANCE`): payload is the instance-level subsystem TLV blob returned by `d_serialize_save_instance_all`.
- `2` (`TAG_CHUNK`): payload is:
  - `i32 cx`, `i32 cy`
  - `u32 chunk_id`
  - `u32 flags` (serialized from `d_chunk::flags`, currently stored as `u16`)
  - followed by the chunk-level subsystem TLV blob returned by `d_serialize_save_chunk_all`.

Notes:
- This format is currently unversioned; forward/backward compatibility is not guaranteed.
- ABI-stable containers should use `DTLV` (`docs/specs/SPEC_CONTAINER_TLV.md`).
