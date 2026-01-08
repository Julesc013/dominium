# SPEC_UNIVERSE_BUNDLE - Portable Universe Container

This spec defines the portable universe bundle container. It is a versioned,
skip-unknown format intended for archival and migration.

## 1. Container format
- The universe bundle uses the DTLV container ABI (see
  `docs/SPEC_CONTAINER_TLV.md`).
- Magic: `"DTLV"`, endian marker `0xFFFE`, header version `1`.
- All integers are little-endian.

## 2. Required chunks (v1)
Chunk type IDs are ASCII fourcc values stored as `u32_le`:
- `TIME` (v1): identity + timebase TLV (required)
- `COSM` (v1): cosmos graph container (required; may be empty)
- `SYSM` (v1): system descriptors (required; may be empty)
- `BODS` (v1): body descriptors (required; may be empty)
- `FRAM` (v1): frame tree descriptors (required; may be empty)
- `TOPB` (v1): topology bindings (required; may be empty)
- `ORBT` (v1): orbit state records (required; may be empty)
- `SOVR` (v1): surface overrides (required; may be empty)
- `CNST` (v1): construction instances (required; may be empty)
- `STAT` (v1): station records (required; may be empty)
- `ROUT` (v1): route records (required; may be empty)
- `TRAN` (v1): transfer records (required; may be empty)
- `PROD` (v1): production rules (required; may be empty)
- `MECO` (v1): macro economy aggregates (required; may be empty)
- `MEVT` (v1): macro event schedule (required; may be empty)
- `CELE` (v1): celestial bodies and systems (required; may be empty)
- `VESL` (v1): vessel records (required; may be empty)
- `SURF` (v1): surface records (required; may be empty)
- `LOCL` (v1): local domain records (required; may be empty)
- `RNG ` (v1): RNG state (required)
- `FORN` (v1): preserved foreign chunks (required; may be empty)

Unknown chunk types must be skipped safely and preserved for round-trip.
Logistics chunk formats are defined in `docs/SPEC_SYSTEM_LOGISTICS.md`.

## 2.1 COSM chunk (cosmos graph container)
The `COSM` chunk payload is a DTLV container (see `docs/SPEC_CONTAINER_TLV.md`)
that stores the logical cosmos graph:
- Required subchunks (v1): `SEED`, `ENTY`, `EDGE`, `FORN`.
- Unknown COSM subchunks must be preserved by copying into `COSM/FORN`.

## 3. TIME chunk TLV (identity + timebase)
TLV records use `u32_le tag` + `u32_le len` headers.

Required tags:
- `0x0001` `UNIVERSE_ID` (UTF-8 bytes, no null terminator)
- `0x0002` `INSTANCE_ID` (UTF-8 bytes, no null terminator)
- `0x0003` `CONTENT_GRAPH_HASH` (`u64_le`)
- `0x0004` `SIM_FLAGS_HASH` (`u64_le`)
- `0x0005` `UPS` (`u32_le`)
- `0x0006` `TICK_INDEX` (`u64_le`)
- `0x0007` `FEATURE_EPOCH` (`u32_le`)
- `0x0008` `COSMO_HASH` (`u64_le`)
- `0x0009` `SYSTEMS_HASH` (`u64_le`)
- `0x000A` `BODIES_HASH` (`u64_le`)
- `0x000B` `FRAMES_HASH` (`u64_le`)
- `0x000C` `TOPOLOGY_HASH` (`u64_le`)
- `0x000D` `ORBITS_HASH` (`u64_le`)
- `0x000E` `SURFACE_OVERRIDES_HASH` (`u64_le`)
- `0x000F` `CONSTRUCTIONS_HASH` (`u64_le`)
- `0x0010` `STATIONS_HASH` (`u64_le`)
- `0x0011` `ROUTES_HASH` (`u64_le`)
- `0x0012` `TRANSFERS_HASH` (`u64_le`)
- `0x0013` `PRODUCTION_HASH` (`u64_le`)
- `0x0014` `MACRO_ECONOMY_HASH` (`u64_le`)
- `0x0015` `MACRO_EVENTS_HASH` (`u64_le`)

Notes:
- Missing required tags are a hard refusal.
- Unknown tags are skipped (forward compatible).

## 4. FOREIGN chunk (unknown chunk preservation)
`FORN` contains TLV records that preserve unknown chunks encountered on load.

Record tag:
- `0x0001` `FOREIGN_CHUNK`

Payload layout for `FOREIGN_CHUNK`:
```
u32_le type_id
u16_le version
u16_le flags
u64_le size
u8[size] payload_bytes
```

Writers must copy unknown chunk payloads into `FORN` on re-save so that the
data survives round-trip even when the chunk type is not understood.

## 5. Identity binding and refusal
Universe bundles are bound to:
- `UNIVERSE_ID`, `INSTANCE_ID`
- content/pack graph hash
- sim-affecting flags hash
- cosmos graph hash
- systems hash
- bodies hash
- frames hash
- topology bindings hash
- orbits hash
- surface overrides hash
- constructions hash
- stations hash
- routes hash
- transfers hash
- production rules hash
- macro economy hash
- macro events hash
- timebase (`UPS`, `TICK_INDEX`)
- feature epoch

Mismatch with the launcher handshake or instance context must refuse by
default (`IDENTITY_MISMATCH`).

## 6. Versioning and migrations
- Unknown chunk versions must be refused or explicitly migrated.
- Migration policy is defined in `docs/SPEC_MIGRATIONS.md`.

## Related specs
- `docs/SPEC_CONTAINER_TLV.md`
- `docs/SPEC_UNIVERSE_MODEL.md`
- `docs/SPEC_SYSTEM_LOGISTICS.md`
- `docs/SPEC_SPACETIME.md`
- `docs/SPEC_MIGRATIONS.md`
- `docs/SPEC_FS_CONTRACT.md`
- `docs/SPEC_LAUNCH_HANDSHAKE_GAME.md`
