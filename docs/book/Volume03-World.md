```markdown
// docs/book/Volume03-World.md
# Dominium Design Book v3.0
## Volume 03 — World

### Overview
The world is a deterministic, chunked spatial hierarchy supporting property-to-planet play. It uses integer coordinates, fixed grids, and layered construction over terrain generated from planet→continent→area→property pipelines. Spatial indexing, prefabs, and construction layers enable dense industrial builds without physics-driven instability.

### Requirements (MUST)
- Use coordinate hierarchy: subchunk 16×16 m, chunk 256×256 m, superchunk 4096×4096 m, hyperchunk 65536×65536 m; world uses arbitrary chunk paging deterministically.
- Represent coordinates as int64 (meters) with fixed axes; no floating positions in simulation.
- Terrain generation stages: planet parameters → continental features → area (256 km × 256 km) → property tiles; deterministic noise only.
- Construction grid resolution 1 m³; layered cells (terrain, foundation, floor/ceiling, wall, interior utilities, machine/fixture, air/occupancy).
- Spatial indexing uses grid + chunk + acceleration (BVH/cell/wide grid) with deterministic lookup.
- Prefabs/blueprints instantiate deterministically; no runtime randomness in placement.
- Environment grid per 16×16 m subchunk storing temp/humidity/rain/wind/solar/cloud/pressure; climate zones per area.
- Store only IDs/indices in persistence; no pointers.

### Recommendations (SHOULD)
- Cache chunk and subchunk data for active areas; keep inactive tiles implicit as empty.
- Align machines, utilities, and multi-storey structures to the 1 m grid for validation and pathing consistency.
- Use deterministic excavation records only where modifications occur to reduce storage.
- Leverage multi-layer climate data to drive building loads and agriculture.

### Prohibitions (MUST NOT)
- No floating-point terrain or construction math in simulation.
- No nondeterministic terrain noise or per-client differences; no procedural randomness outside seeded generators.
- No free-floating item entities; inventories and resource slots must back all goods.
- No physics bodies for construction stability; structural constraints enforced via data checks, not physics.

### Detailed Sections
#### 3.1 — Spatial Model
- Coordinate system (x,y,z,r) with integer meters; z=0 at sea level.
- Chunk paging deterministic; chunk/subchunk tables used for lookup; tiles stored only when modified.
- Utility masks per tile for power/data/fluid/thermal nodes; entities referenced by IDs.

#### 3.2 — Terrain and Geology Generation
- Planet layer defines radius, axial tilt, orbit, atmosphere, base biome/height/ocean depth.
- Continent layer adds shelves, highlands, river basins, deserts via deterministic noise.
- Area layer (256 km square) holds heightmap, biome map, hydrology; property inherits with microclimate variation.
- Soil/rock/resource densities and water table stored per subchunk; excavation tracked at 1 m resolution when altered.

#### 3.3 — Construction System
- 1 m grid placement; supports foundations, walls, floors, roofs, tunnels, bridges, basements, multi-level buildings.
- Interior utility layer routes power/data/fluids inside walls; machines and fixtures occupy machine layer; air/occupancy layer for walkability.
- Structural validation is deterministic; no partial physics. Integrated with logistics, workers, and networks.

#### 3.4 — Spatial Indexing and Prefabs
- Grid layer mandatory; chunk/subchunk layer plus acceleration (BVH) for queries.
- Prefabs and blueprints resolve to deterministic IDs; loading/injection follows fixed resource ID assignment.
- Collision layers defined per collider class; terrain sampling rules deterministic.

#### 3.5 — Universe and Planet Structure
- Universe contains galaxies → solar systems → bodies (planets/moons/stations) with deterministic Keplerian orbits; time tracked via global tick.
- Base content includes Sol system; additional galaxies/systems added via DLC/mods using Mercator planet maps.

#### 3.6 — Environment Grid
- EnvCell per 16×16 m subchunk stores temp, humidity, rainfall, wind speed/dir, solar flux, cloud cover, pressure (fixed-point).
- Climate zones (tropical/arid/temperate/continental/polar/highland/oceanic/tundra/desert) set envelopes; transitions blend deterministically.
- Environmental data feeds building loads, hydrology, agriculture, worker health, and network interactions.

### Cross-References
- Volume 02 — Simulation (chunk paging, tick-driven updates)
- Volume 04 — Networks (utilities embedded in cells and routes)
- Volume 05 — Economy (resource extraction, property assets)
- Volume 06 — Climate (environment grid and climate layers)
- Volume 07 — UIUX (map/minimap/overlays on world data)
- Volume 08 — Engine (spatial indexing, persistence)
- Volume 09 — Modding (planet/biome/resource definitions in packs)
```
