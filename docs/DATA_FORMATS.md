# Dominium — DATA FORMATS (V5)

All Dominium runtime formats are **deterministic**, **little-endian**, **strictly versioned**, and **integer/fixed-point only**. Unknown blocks must be safely skipped, not rejected. No platform padding is permitted; all structs are manually packed.

This document aligns the spec layer with the dev addenda for data, mods, networking, and serialization.

---

## 0. GLOBAL RULES
- Endianness: little-endian everywhere.
- Numeric domain: `int64` for coordinates/IDs; `q16.16` / `q32.32` for fixed-point; **no floats** in any on-disk or on-wire format.
- Block framing (for any top-level block):
```
uint32 block_magic;
uint16 block_version;
uint16 block_flags;
uint32 block_size_bytes; /* payload only */
```
- Unknown blocks and trailing fields must be skipped; forward/backward compatibility is mandatory.
- IDs are stable: entity (uint64), network nodes (uint32–uint64), chunks/surfaces (uint64 signed).

---

## 1. SAVEGAME FORMAT (`*.dom`)
A save is a container header followed by ordered blocks. Required blocks must appear once. Optional blocks may appear zero or more times.

### 1.1 File header (fixed-size)
```
char    magic[8] = "DOMSAVE";
uint32  format_version;     /* e.g., 0x00050000 for V5 */
uint32  engine_version;     /* semantic + build encoded */
uint128 world_uuid;         /* universe identifier */
uint128 surface_uuid;       /* specific surface identifier */
uint64  tick_id;            /* current deterministic tick */
uint32  endian_tag = 0x01020304;
uint32  reserved[8] = {0};
```

### 1.2 Required blocks
- **WORLD_METADATA**  
  - Universe/galaxy/system/planet/surface IDs and parameters.  
  - Seeds for deterministic worldgen.  
  - Spatial hierarchy settings (chunk sizes, z-layer counts).

- **PACK_SET**  
  - Active data packs (base + DLC + asset packs).  
  - Fields per entry: `pack_id`, `version`, `priority`, `content_hash`.

- **MOD_SET**  
  - Active mods with deterministic ordering.  
  - Fields per entry: `mod_id`, `version`, `order`, `determinism_flags`, `content_hash`.  
  - Save must refuse to load if the mod set does not match (or mark non-deterministic mode explicitly).

- **CHUNK_TABLE**  
  ```
  uint32 count;
  repeat count:
      int64  chunk_x;
      int64  chunk_y;
      int64  chunk_z;
      uint64 chunk_id;
      uint32 flags;
  ```
  Sorted by (x, y, z).

- **CHUNK_DATA**  
  - Per chunk: compressed (deterministic) tile data, terrain heightfield, cut/fill overlays, entities-in-chunk index, chunk-local network nodes, blueprint fragments.  
  - Compression: deterministic LZ4 or equivalent; same input → same bytes.

- **ENTITY_LIST**  
  ```
  uint32 entity_count;
  repeat entity_count:
      uint64 entity_id;
      uint32 prefab_id;
      uint8  active;
      uint8  lane_id;
      int64  pos_x, pos_y, pos_z;
      uint32 component_mask;
      /* component payloads follow in deterministic component-id order */
  ```

- **NETWORK_POWER**  
  - Node table, edge table, per-node voltage/current/frequency, transformer/breaker states. Component-level ordering must be deterministic.

- **NETWORK_DATA**  
  - Routers/switches, routing tables, deterministic tick queues, packet buffers (fixed depths), signal channels.

- **NETWORK_FLUIDS**  
  - Tanks, pipes, valves/pumps; per-node pressure, temperature, fluid type, volume.

- **NETWORK_THERMAL**  
  - Thermal nodes/cells and their temperature fields; multi-rate scheduling metadata if applicable.

- **ECONOMY**  
  - Accounts, inventories, price indices (local/global), outstanding trades/logistics queues.

- **RESEARCH**  
  - Research nodes, required science, progress counters, unlock flags, infinite/levelled tech states.

- **CLIMATE**  
  - Climate cell parameters; temperature/precipitation/wind indices; CO₂eq and forcing fields; multi-rate tick offsets.

- **WORKERS**  
  - Worker agents, skills, job queues, current assignments; deterministic ordering.

- **RNG_STATE**  
  - Global and per-lane deterministic RNG states (per §3 in SPEC_CORE).

- **BLUEPRINTS**  
  - Blueprint instances: id, prefab references, placement, orientation, stage, pending jobs/resources.

### 1.3 Optional blocks
- **SNAPSHOT_METADATA** — hashes, profiling info, build metadata.
- **DEBUG_VARS** — non-authoritative debug overlays.
- **CUSTOM_MOD_DATA** — namespaced mod payloads; must not affect core without explicit mod determinism flags.

---

## 2. REPLAY FORMATS
Two deterministic replay modes are supported.

### 2.1 Input replay (`*.dreplay`)
- **Header:** `"DOMREP\0"`, `format_version`, `world_uuid`, `surface_uuid`, optional `mod_set_hash`, `pack_set_hash`.
- **Event stream per tick:**
  ```
  uint64 tick_id;
  uint16 event_count;
  repeat event_count:
      uint16 event_type;
      uint16 size;
      uint8  payload[size];
  ```
- No delta compression; strict ordering; identical input streams must yield identical sim state across platforms.

### 2.2 Snapshot + delta replay (`*.drepd`)
- **SNAPSHOT** blocks every N ticks: subset of save blocks needed for resync (WORLD_METADATA, PACK_SET, MOD_SET, CHUNK_TABLE/DATA, ENTITY_LIST, NETWORK_* subsets, RNG_STATE).
- **DELTA** blocks between snapshots: changes to entities, networks, climate, research, economy.
- Compression allowed only in deterministic mode; delta application must be order-stable.

---

## 3. MOD PACKAGE FORMAT (`*.dmod`)
- Container: ZIP.
- Required: `mod.json` manifest (see `docs/dev/dominium_new_mods.txt` for fields: id, version, engine version bounds, dependencies, conflicts, determinism flags).
- Directory layout inside ZIP:
  ```
  mod.json
  data/      # entities, recipes, tech, networks, etc.
  scripts/   # deterministic sandboxed scripts (optional)
  gfx/       # tiles, sprites, ui, vector sets (optional)
  audio/     # sfx/music (optional)
  locale/    # translations (optional)
  docs/      # optional
  tests/     # optional
  ```
- Prohibitions: no native binaries auto-loaded by engine; no OS/network/wallclock access from scripts; no schema changes inside mods.
- Mod IDs must be namespaced and unique; overrides require explicit `override:true` semantics as defined by the modding spec.

---

## 4. BLUEPRINT FORMATS
Blueprints describe prefab placement and construction.

### 4.1 JSON form
```json
{
  "blueprint_id": "mod.namespace.bp_example",
  "name_key": "bp.example.name",
  "size_tiles": [32, 8],
  "anchor": [0, 0],
  "dlc_required": [],
  "entities": [
    {"prefab": "mod.namespace.machine_basic", "x": 4, "y": 2, "z": 0, "o": 0}
  ],
  "networks": {
    "power": [{ "type": "pole_small", "x": 2, "y": 1, "z": 0 }],
    "belts": [{ "type": "belt_basic", "path": [[0,4,0],[31,4,0]] }]
  },
  "resources": { "iron_plate": 50 },
  "metadata": { "intended_throughput": { "item_id": "iron_plate", "items_per_second": 30 } }
}
```
- Entities ordered by (prefab, coord) for determinism. Paths use integer coordinates only.

### 4.2 Binary form
```
uint32 magic = 0x424C5054; /* "BLPT" */
uint16 version;
uint16 flags;
uint32 node_count;
/* nodes... (sorted) */
uint32 edge_count;
/* edges... (sorted) */
/* resource table ... */
```

---

## 5. DRAW-COMMAND FORMAT
Renderer backends never read simulation directly; they consume deterministic draw-command buffers produced by game/engine.

### 5.1 Command types (screen-space integers)
```
uint16 cmd_type;  /* rect, line, poly, sprite, text */
uint16 flags;
int32  x0, y0, x1, y1;    /* semantics depend on cmd */
int32  x2, y2, x3, y3;    /* optional */
uint32 color_rgba;        /* 0xAARRGGBB */
uint32 stroke_width_q16;  /* fixed-point stroke */
uint32 extra_index;       /* sprite/font/vector set index */
```
- Commands are stored in order; max count is fixed by the renderer buffer (`DOM_RENDER_CMD_MAX`). Overflow is a deterministic error.
- Backends convert to floats internally if needed but must not mutate simulation state.

### 5.2 Command stream block
```
DCMD
uint16 block_version;
uint16 camera_id;
uint32 count;
[commands...]
```

---

## 6. UNIVERSE / GALAXY / SYSTEM / SURFACE METADATA
Stored in `WORLD_METADATA`:
- IDs for universe/galaxy/system/planet/surface.
- Orbital parameters (integer/fixed) for on-rails orbits.
- Planet properties: radius, gravity, rotation, atmosphere composition/pressure.
- Seeds used for orbital layout and worldgen.
- No N-body data; orbital paths are deterministic rails.

---

## 7. CHUNK STORAGE FORMAT
- **CHUNK_HEADER**
  ```
  uint64 chunk_id;
  int64  origin_x, origin_y, origin_z;
  uint32 flags;
  uint32 tile_count;
  ```
- **TILE_DATA** — compact terrain/material IDs, height offsets, cut/fill overrides, water level indices; compressed deterministically.
- **NETWORK_SUBSECTIONS** — chunk-local node tables for power/data/fluids/thermal.
- **ENTITY_INDEX** — list of entity IDs inside the chunk (sorted).

---

## 8. NETWORK FORMATS (SAVE/REPLAY)
### 8.1 Power
```
uint32 node_count; [nodes...]
uint32 edge_count; [edges...]

node:
  uint32 node_id;
  int64  x, y, z;
  uint32 voltage_mv;
  uint32 frequency_millihz;
  uint16 type_flags;
edge:
  uint32 a, b;
  uint32 capacity_va;
  uint32 flags;
```

### 8.2 Data
```
uint32 node_count;
uint32 edge_count;
uint32 queue_size;

packet:
  uint32 src;
  uint32 dst;
  uint32 payload_size;
  uint8  payload[];
```
Packets are logged in deterministic order per tick; overflow drops oldest with a flag.

### 8.3 Fluids
```
node:
  uint32 fluid_id;
  int32  pressure_q16;
  int32  temperature_q16;
  int32  volume_q16;
edge:
  uint32 a, b;
  int32  conductance_q16;
  int32  capacity_q16;
  uint32 flags;
```

### 8.4 Thermal
- Grid/graph cells with integer/fixed temperatures; stored in deterministic scan order.

---

## 9. SERIALIZATION CONSTRAINTS
- No pointers serialized; only stable IDs and value types.
- Arrays/lists are **sorted** (by ID or coordinate) before serialization.
- Hash maps are not serialized directly; convert to sorted lists.
- No floats anywhere in authoritative formats.
- All block sizes/versions must be correct; tools must not guess defaults silently.
- Savefiles must record the exact mod and pack sets; loading with a mismatched set is a hard error unless explicitly marked as non-deterministic.
- Breaking changes require new block versions and migration tooling.
- Only `/engine/core`, `/engine/sim`, `/engine/io`, and `/engine/net` may serialize core state.

End of DATA_FORMATS.md (V5).
