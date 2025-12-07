# Dominium — Data Formats (Engine v0)

All formats are little-endian, deterministic, and fixed-point-only. Unknown sections are skipped, not rejected. No floats appear in any on-disk file.

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

## 7. Package + product manifests

### Product manifest (`product.toml`)
- Location: alongside binaries in `program/<product_id>/<version>/product.toml`, shipped per installed version.
- Format: simple key/value TOML-like text:
  - `id = "<product id>"` (required)
  - `version = "<semver>"` (required; parsed via `domino_semver_parse`)
  - `[compat]` optional table:
    - `content_api` – integer content ABI of the product itself.
    - `launcher_content_api` – minimum content ABI expected by the launcher.
    - `launcher_ext_api` – extension API version for launcher plug-ins.
- Unspecified compat fields default to `0`; loaders ignore unknown keys for forward compatibility.

### Package manifest (`*.toml` for mods/packs)
- Location: under `data/` (first-party) or `user/` (community) and consumed by `domino_mod` when building registries.
- Top-level keys:
  - `id = "<package id>"`, `version = "<semver>"` (required).
  - `kind = "mod" | "pack"` (required).
  - `target = "game" | "launcher" | "both"` (optional; defaults to `game` today).
- `[compat]` optional table:
  - `launcher_id` and `launcher_range` to describe compatibility with specific launcher ids/versions.
  - `launcher_content_api` and `launcher_ext_api` integers for launcher-facing ABI gates.
- `[launcher]` optional table for launcher-targeted packages:
  - `enabled_by_default = true|false` (defaults to `true`).
  - `[[launcher.view]]` entries may declare view/tab surfaces:
    - `id`, `label`, `kind` (`list/detail/dashboard/settings/custom`), `priority`, `script_entry`.
- Launcher-side parsing of `[launcher]` is intentionally shallow in this pass; unknown keys are ignored and the view definitions are staged for future scripting/runtime registration.
