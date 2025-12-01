```markdown
// docs/book/Volume09-Modding.md
# Dominium Design Book v3.0
## Volume 09 — Modding

### Overview
Modding and DLC use a layered, deterministic content stack. Packs provide data, assets, and optional Lua scripts within sandboxed limits. Formats are versioned, endian-stable, and forward/backward compatible. Mods may extend content but cannot alter the deterministic core or violate simulation rules.

### Requirements (MUST)
- Content stack load order: Engine core → base pack `dominium.base` → official DLC (e.g., `dominium.interstellar`, `dominium.extras`, future packs) → user mods/mod packs → optional local overrides (disabled in multiplayer).
- Content packs structured as directories/ZIPs with `pack.toml`, data/ (items/machines/fluids/materials/research/companies/planets/galaxies/systems/biomes/disasters), assets (textures/sprites/models/sounds/music/fonts), scripts, locale, UI, campaign, triggers.
- `pack.toml` includes id, version, requires/conflicts, provides capabilities, priority for override order.
- Allowed data formats: TOML, JSON, fixed-schema `.dmd`, optional Lua wrappers. Mod package format `.dmod` is a ZIP with manifest.json and content folders.
- Deterministic data files: no floats for simulation-critical values; use integers/fixed-point; no platform-dependent layout.
- Lua sandbox: allowed for campaign scripting, UI extensions, conditional content; cannot introduce randomness into simulation, override physics/tick/economic core, modify worker logic internally, or perform OS/file I/O outside mod directory.
- Blueprint format JSON/binary containing nodes/edges/placement/rules/resources; replays and savefiles remain deterministic and include mod lists/versions.

### Recommendations (SHOULD)
- Use `priority` in pack metadata to manage overrides; keep base definitions minimal and extend via DLC/mods.
- Validate mods for missing/orphaned localisation keys, schema correctness, and deterministic math.
- Provide modded fonts under `/mods/<mod>/fonts/` and locale under `/mods/<mod>/locale/<lang>/`.
- Ship planet/biome/galaxy data with Mercator maps and deterministic orbital parameters for consistency.

### Prohibitions (MUST NOT)
- Mods must not bypass tick ordering, determinism kernel, or backpressure rules.
- No modification of core simulation constants, physics, or economic models without explicit compatibility modules.
- No nondeterministic RNG, time-based behaviour, or OS-dependent features in mod logic.
- Mods cannot reposition HUD outside layout rules or hide essential data; UI extensions must stay within deterministic frameworks.

### Detailed Sections
#### 9.1 — Content Stack and Load Order
- Engine core supplies binaries and deterministic kernel.
- Base pack required; DLC adds content with higher priority.
- User mods/mod packs layered above; local overrides for dev/debug only.

#### 9.2 — Pack Structure and Metadata
- Directory/ZIP structure with `pack.toml` (id/version/requires/conflicts/provides/priority).
- Data-driven definitions in data/ folders for items, machines, fluids, research, companies, planets, galaxies, systems, biomes, disasters.
- Assets (textures/sprites/models/sounds/music/fonts) bundled per pack; UI/campaign/trigger scripts optional.

#### 9.3 — Data Formats and Serialization
- `.dmod` package structure; savegames endian-neutral with mod lists/versions; blueprints JSON/binary; replays input-only or snapshot+delta.
- Binary formats packed, little-endian, pointer-free; schema checksums and CRC per block.

#### 9.4 — Lua Sandbox and Extensions
- Lua allowed for campaign scripting, UI additions, conditional logic, world editor tools.
- Sandbox provides deterministic math; no OS access/file I/O beyond mod dir; limited memory; safe coroutines.
- Mods may add HUD panels, markers, themes, and localisation, but cannot alter simulation logic directly.

#### 9.5 — Validation and Compatibility
- Load-time validation of dependencies/conflicts, schema correctness, deterministic value ranges.
- Multiplayer disables local overrides and enforces identical mod sets/versions for lockstep determinism.
- Future compatibility handled via migration tables and explicit compatibility modules.

### Cross-References
- Volume 01 — Vision (mod-first philosophy)
- Volume 02 — Simulation (determinism kernel mods must respect)
- Volume 03 — World (planet/biome/resource data supplied by packs)
- Volume 04 — Networks (device/link definitions in data files)
- Volume 05 — Economy (goods/companies/markets definitions)
- Volume 06 — Climate (planet/climate/biome definitions)
- Volume 07 — UIUX (UI extensions, fonts, localisation)
- Volume 08 — Engine (serialization, format rules, Lua sandbox integration)
```
