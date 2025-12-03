# Dominium — DATA FORMATS (V4)

All Dominium data formats are:

- **Deterministic**
- **Endian-defined (little-endian only)**
- **Portable across platforms**
- **Strictly versioned**
- **No floating point** (integer and fixed-point only)
- **No platform-defined padding**
- **Forward- and backward-compatible** via block headers and version tags

This file defines:

1. Savegame / State format  
2. Replay formats  
3. Mod package formats  
4. Blueprint formats  
5. Draw-command formats (for renderers)  
6. Universe / Galaxy / System / Surface metadata formats  
7. Chunked world storage formats  
8. Network formats (power, data, fluids)  
9. Serialization constraints

All serialization code lives in `/engine/sim`, `/engine/net`, and `/engine/core`, with public read/write helpers exposed as C89 functions.

---

# 0. GLOBAL RULES (BINDING)

### 0.1 Endianness
All binary formats are **little-endian** regardless of platform.

### 0.2 Integer / Fixed-Point Only
- Coordinates use `int64`
- Fixed-point uses q16.16 or q32.32
- No floats appear in any file or packet

### 0.3 Versioning
Every top-level block begins with:

uint32 block_magic
uint16 block_version
uint16 block_flags
uint32 block_size_bytes // payload only

pgsql
Copy code

Blocks may appear in any order unless otherwise specified.

### 0.4 Forward-Compatibility
- Unknown block types must be **skipped**, not rejected.
- Unknown fields at end of known blocks must be skipped.

### 0.5 IDs Must Be Stable
- Entity IDs are 64-bit.
- Network node IDs are 32–64 bit depending on subsystem.
- Chunk and surface IDs are 64-bit signed integers.

---

# 1. SAVEGAME FORMAT (V4)

A Dominium save (`*.dom`) is a binary file consisting of a **container header** followed by a series of **blocks**.

## 1.1 File Header (fixed-size)

char magic[8] = "DOMSAVE"
uint32 format_version // e.g. 0x00040000 for V4
uint32 engine_version // encoded engine build
uint128 world_uuid // unique per universe
uint128 surface_uuid // identifies specific planet/surface
uint64 tick_id // deterministic tick number
uint32 endian_tag // always 0x01020304
uint32 reserved[8] // future use, must be zero

shell
Copy code

## 1.2 Required Blocks

### 1.2.1 WORLD_METADATA
Contains:
- universe/galaxy/system identifiers
- surface parameters (radius, gravity, rotation)
- seed values for deterministic worldgen
- spatial hierarchy settings (chunk sizes, etc.)

### 1.2.2 CHUNK_TABLE
List of all allocated chunks:

uint32 count
for each:
int64 chunk_x
int64 chunk_y
int64 chunk_z
uint64 chunk_id
uint32 flags

sql
Copy code

Chunks appear in sorted order (x, then y, then z).

### 1.2.3 CHUNK_DATA
For each chunk:

- Tile data (compressed)
- Terrain heightfield
- Cut/fill overrides
- Entities-in-chunk index
- Local network nodes (power/data/fluids)
- Local blueprint fragments

Compression allowed: LZ4, deterministic mode only.

### 1.2.4 ENTITY_LIST
Contains full ECS entity table:

uint64 entity_id
uint32 prefab_id
uint8 active
uint8 lane_id
int64 pos_x, pos_y, pos_z
uint32 component_mask
... component payloads, deterministic order ...

diff
Copy code

### 1.2.5 NETWORK_POWER
Includes:
- Node table
- Edge table
- Per-node voltage/current/frequency
- Transformer/breaker states

### 1.2.6 NETWORK_DATA
Includes:
- Routers/switches
- Routing tables
- Deterministic tick queues
- Packet buffers (max depth fixed)

### 1.2.7 NETWORK_FLUIDS
Includes:
- Tanks
- Pipes
- Valves/pumps
- Per-node pressure, temperature, fluid type

### 1.2.8 ECONOMY
Contains:
- Accounts (integer)
- Resource inventories (per property/company)
- Price indices (local/global)

### 1.2.9 RESEARCH
Contains:
- Research nodes
- Required science amounts
- Progress counters
- Unlock flags

### 1.2.10 CLIMATE
Contains:
- Regional climate cell parameters
- Temperature/precip/wind indices
- CO₂eq and radiative forcing fields

### 1.2.11 WORKERS
Contains:
- Worker agents
- Skills
- Job queues
- Assigned job state

### 1.2.12 RNG_STATE
Contains:
- Global deterministic RNG state (xoshiro or chosen algorithm)
- Per-lane RNG states (if used)

### 1.2.13 BLUEPRINTS
Contains:
- Blueprint instances
- Construction stage
- Required resources
- Pending worker tasks

## 1.3 Optional Blocks

- SNAPSHOT_METADATA
- DEBUG_VARS
- CUSTOM_MOD_DATA (namespaced)

---

# 2. REPLAY FORMATS (V4)

Dominium supports **two** deterministic replay modes.

## 2.1 Input Replay (`*.dreplay`)

### 2.1.1 File Header
"DOMREP\0"
format_version
world_uuid
surface_uuid

perl
Copy code

### 2.1.2 Event Stream
For each tick:

uint64 tick_id
uint16 event_count
[event entries...]

vbnet
Copy code

Each event entry:

uint16 event_type
uint16 size
uint8 payload[size]

shell
Copy code

No delta compression; fully deterministic.

## 2.2 Snapshot + Delta Replay (`*.drepd`)

Used for long replays.

### 2.2.1 Snapshots
Every N ticks:

SNAPSHOT
serialized save blocks subset

shell
Copy code

### 2.2.2 Deltas
Between snapshots:

DELTA
changes to entity component tables
changes to networks
changes to climate and research

yaml
Copy code

Compression allowed but deterministic only.

---

# 3. MOD PACKAGE FORMAT (V4)

Mod files have extension: `*.dmod`.

A mod is a **ZIP container** with:

manifest.json
data/
data/entities/
data/networks/
data/recipes/
data/terrain/
lua/
textures/
sounds/
music/
blueprints/
tech_tree.json

bash
Copy code

## 3.1 manifest.json (required)

Example minimal:

```json
{
  "mod_id": "example.mod",
  "name": "Example Mod",
  "version": "1.0.0",
  "engine_version_min": "3.0.0",
  "engine_version_max": "3.999",
  "load_after": ["base"],
  "scripts": ["lua/init.lua"]
}
Rules:

All strings Unicode UTF-8.

No executable binaries permitted.

No engine-side .dll/.so allowed for mods.

All mod identifiers canonical ASCII.

4. BLUEPRINT FORMAT (V4)
Blueprints describe prefab placement and construction.

Blueprints can exist as JSON or compact binary.

4.1 JSON form
json
Copy code
{
  "blueprint_id": "bp_example",
  "nodes": [
    {"prefab": 1001, "x": 123, "y": 45, "z": 0, "o": 1}
  ],
  "edges": [
    {"a": 0, "b": 1, "type": "connection"}
  ],
  "resources": {
    "iron_plate": 50,
    "copper_wire": 20
  }
}
4.2 Binary form
go
Copy code
uint32 magic = 0x424C5054 ("BLPT")
uint16 version
uint16 flags
uint32 node_count
nodes...
uint32 edge_count
edges...
resource table...
Nodes stored in sorted order (prefab, then coordinate).

5. DRAW-COMMAND FORMAT (V4)
Renderer backends do not access simulation directly.
Simulation outputs DomDrawCmd[] arrays every frame.

5.1 DomDrawCmd
go
Copy code
uint16 cmd_type    // rect, line, poly, sprite, text, model, etc.
uint16 flags
int64  x0, y0, z0
int64  x1, y1, z1
int64  x2, y2, z2
int64  x3, y3, z3
uint32 color_rgba
uint32 stroke_width_q16
uint32 extra_index     // index into renderer-side tables for UVs, sprites, meshes
5.2 Draw Command Stream
Stream block:

csharp
Copy code
DCMD
block_version
camera_id
count
[commands...]
No floating point; renderers convert to floats internally if needed.

6. UNIVERSE / GALAXY / SYSTEM / SURFACE METADATA (V4)
Stored in WORLD_METADATA block.

Contains:

Versioned descriptors for:

Universe ID

Galaxy ID

System ID

Planet ID

Surface ID

Orbital parameters (integer only)

Seeds used for orbital layout

Planet physical properties (radius, rotation period, gravity)

Atmospheric properties (pressure, composition IDs)

No N-body data—system is “on rails”, deterministic.

7. CHUNK STORAGE FORMAT (V4)
Each chunk stores:

7.1 CHUNK_HEADER
go
Copy code
uint64 chunk_id
int64  origin_x, origin_y, origin_z
uint32 flags
uint32 tile_count
7.2 TILE_DATA
1–few bytes per tile for:

terrain type

height offset

cut/fill override

water level index

7.3 NETWORK_SUBSECTIONS
Per-network chunk-local node tables:

power nodes

data nodes

fluids nodes

7.4 ENTITY_INDEX
List of entity IDs inside the chunk.

8. NETWORK FORMATS (V4)
Networks appear in both savegames and snapshots.

8.1 Power
csharp
Copy code
uint32 node_count
[nodes...]
uint32 edge_count
[edges...]
Each node:

go
Copy code
uint32 node_id
int64  x, y, z
uint32 voltage_mv
uint32 frequency_millihz
uint16 type_flags
Edge:

go
Copy code
uint32 a, b
uint32 capacity_va
uint32 flags
8.2 Data
go
Copy code
uint32 node_count
uint32 edge_count
uint32 queue_size
Packets:

go
Copy code
uint32 src
uint32 dst
uint32 payload_size
uint8  payload[]
8.3 Fluids
makefile
Copy code
node:
    fluid_id
    pressure_q16
    temperature_q16
    volume_q16
Edges carry capacities and conductances.

9. SERIALIZATION CONSTRAINTS
No pointer values written to disk.

All structs packed manually; no compiler padding.

All arrays sorted to guarantee deterministic iteration.

No hash tables serialized directly—only sorted lists.

No floats anywhere in on-disk formats.

All seeds, IDs, and timestamps must be explicitly saved.

All block sizes must be correct—Codex must not guess.

Unknown blocks/fields must be skipped safely.

Breaking changes require:

new block version

optional migration tool

Only /engine/core, /engine/sim, and /engine/net may serialize core state.

End of DATA_FORMATS.md (V4).