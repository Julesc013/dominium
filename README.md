# DOMINIUM & DOMINO  
## A Deterministic, Multi-Scale, Multi-Platform Simulation Game and Engine

Dominium on Domino is a **fully deterministic**, **integer-math**, **platform-agnostic**, **modular** engine and game designed to run identically across:

- Modern systems (Windows NT family, Linux, macOS X)
- Legacy systems (Win9x, Win3.x, Win16, DOS, macOS 7–9, OS/2 strata via shims)
- Future systems (WASM/Web, consoles, embedded)
- Headless/server nodes (single or clustered)

Dominium is a game running on the Domino engine.  
The official game is one compatible implementation atop it.  
Determinism permeates physics, AI, networks, world updates, rendering order, mod execution, and replay.

This repository includes:

- **Domino Engine** — deterministic C89/C++98 core  
- **Dominium Game** — content-agnostic gameplay layer  
- **Data Packs** — first-party assets and base definitions  
- **Tools & Editors** — world tools, asset pipelines, modding interfaces  
- **Ports** — DOS, Win3.x, Win9x, macOS Classic, WASM, etc.  
- **Specifications** — binding behaviour contracts  
- **Modding API** — deterministic, forward-compatible, sandboxed  

All behaviour derives from written specifications. No code exists without a contract.

---

# 1. PROJECT VISION

Dominium aims to:

1. Produce **universally reproducible simulation**: any two machines, of any era or ISA, must yield identical results per tick.  
2. Handle **extreme spatial scales**, from 16th-meter structural grids to multi-gigameter surfaces and orbital networks.  
3. Execute on **decades of hardware**, from 286-class machines upward, with optional fidelity reduction but identical simulation.  
4. Be **maximally modifiable** without weakening determinism.  
5. Support **interchangeable 2D/3D vector and raster renderers** at runtime.  
6. Model **surface + orbital domains** with deterministic rails-based spaceflight, docking graphs, transfer windows, and orbital infrastructure.  
7. Provide a **unified construction system** with block components, structural slabs, vector splines (rails, roads, tunnels), cut/fill operations, and multi-layer buildings.  
8. Maintain strict separation between **physical surfaces** and **logical orbital/space graphs**.  
9. Allow deterministic **clustered multiplayer**, synchronizing planets and orbital bodies.  
10. Provide engineering clarity such that the project remains viable for decades.

Dominium is engineered to outlive its original hardware.

---

# 2. CORE PHILOSOPHY

## 2.1 Determinism
No floating point exists in any simulation codepath.  
Integer/fixed-point formats only (runtime Q16.16; save Q4.12; segment addressing for world scale).  
Deterministic ordering of:  
- Input  
- Pre-state  
- Simulation lanes  
- Network phase  
- Merge  
- Postprocess  
- Finalization  

Replay files must verify identical state hashes across platforms.

## 2.2 Tick Phasing and Ordering

Immutable phases:  
1. Input  
2. Pre-state  
3. Simulation lanes  
4. Networks  
5. Merge  
6. Post-process  
7. Finalize  

Systems cannot break phase ordering.

## 2.3 Spatial Hierarchy

World represented as sparse microgrids across scales:

```yaml
Subnano = 1/65536 m
Submicro = 1/4096 m
Submini = 1/256 m
Subtile = 1/16 m
Tile = 1 m
Subchunk = 16 m
Chunk = 256 m
Subregion = 4096 m
Region = 65536 m
Subcontinent = 1,048,576 m
Continent = 16,777,216 m
Supercontinent = 268,435,456 m
Surface = 4,294,967,296 m
```

Surfaces are **collections of sparse grids**, not monolithic arrays.  
Supports underground structures, multi-level constructs, and intersecting vector systems.

## 2.4 Universal Modularity

All subsystems are hot-swappable:

- Rendering: software, vector, GL1/2, DX9/11/12, Vulkan, VGA/EGA/CGA/MDA, VESA, QuickDraw/Carbon, Metal  
- Audio: modular abstraction  
- Platform backends: SDL1/SDL2, Win32, Win16, macOS Classic, POSIX, X11, Wayland  
- Tools and data packs  
- Mods with deterministic scripting (Lua subset or Dominium Script)

## 2.5 Platform Breadth

Engine compiles under:

- Strict C89  
- Strict C++98 with no STL beyond allowed subset  
- No libc extensions in core  
- All platform-specific behaviour contained in `/engine/platform`

Ports adapt to core contracts, never the reverse.

---

# 3. REPOSITORY OVERVIEW

Top-level structure:

```yaml
/docs – specifications, formats, policies, style, building
/engine – deterministic engine core (C89/C++98)
/game – high-level gameplay logic
/data – base assets, DLC, data packs
/mods – third-party deterministic mods
/tools – editors, converters, pipelines
/tests – unit, replay, integration, perf tests
/external – vendored dependencies (Lua, platform libs, etc.)
/build – build trees, generated headers, CI outputs
/package – installer scripts, retro media images
/scripts – automation, maintenance, CI utilities
/ports – DOS, Win3.x, Win9x, macOS Classic, WASM, consoles
```

Formal definitions live in:  
`/docs/spec/DIRECTORY_CONTRACT.md`.

---

# 4. BUILDING

## 4.1 Modern Platforms

CMake workflow:

```shell
mkdir build
cd build
cmake ..
cmake --build .
```

Build step increments global build number in `.dominium_build_number`.  
Generated header: `build/generated/dom_build_version.h`.

## 4.2 Retro Platforms

Per-port instructions under `/ports/<target>/config/`.

Examples:  
- **DOS**: OpenWatcom + wmake  
- **Win3.x**: MASM + MSVC 1.52  
- **Win9x**: MSVC6 + DX7 SDK or SDL1 backend  
- **macOS Classic (7–9)**: CodeWarrior + MPW  
- **WASM**: Emscripten  

Simulation behaviour remains identical across all targets.

---

# 5. RUNNING

## 5.1 Headless Server

```shell
./dominium_server --world myworld
```

## 5.2 Client

```yaml
./dominium_client
```

Clients and servers operate in deterministic lockstep; divergences are rejected with replay/resync.

Launcher is optional and never required to run the game.

---

# 6. MODDING

A mod contains:

- `mod.json`  
- Prefabs  
- Data packs  
- Scripts (deterministic subset of Lua)  
- Assets  

Loading order:  
1. Base  
2. DLC  
3. Mods by UUID (stable ordering)

Mods may *add* systems but never alter engine rules.  
Mods cannot introduce nondeterminism, patch binaries, or violate directory contracts.

---

# 7. DATA FORMATS

All engine data uses:

- Integer math only  
- Packed structs, no padding  
- Little-endian canonical representation  
- Explicit versioning  
- No pointers in serialized data  
- CRC and replay hash metadata

Save files contain:

- Components  
- Entities  
- Networks  
- Jobs  
- Prefab references  
- Messages  
- Chunk/subchunk microgrids  
- Full world snapshot  
- Optional replay delta log

---

# 8. SURFACE + SPACE ARCHITECTURE

Two primary domains exist.

## 8.1 Physical Domains

- Planet surfaces  
- Underground volumes  
- Oceans  
- Sparse terrain grids  
- Structural microgrids  
- Buildings  
- Vector networks (rails, roads, conveyors, pipes, tunnels)  
- Cut/fill terrain layers  

## 8.2 Logical Domains (Orbital/Space)

- Discrete orbital tracks  
- Transfer windows  
- Docking graphs  
- Asteroid belts  
- Stations and ships  
- Lagrange nodes  
- Deterministic transitions (rails-based orbital mechanics)  

Space simulation is integer-based and deterministic. No floating dynamics.

---

# 9. PLATFORM + RENDERER MATRIX

Dominium supports simultaneous platform and renderer abstraction.

**Platforms**:  
SDL1, SDL2, Win32, Win16, Win32s, Win9x, NT3–11, macOS 7–9 (Classic/Carbon), macOS X, POSIX, X11, Wayland, DOS, CP/M-80/86, Linux/BSD, Android.

**Renderers**:  
Software, Vector, GL1, GL2, DX9, DX11, DX12, Vulkan1, VGA/EGA/CGA/MDA/Hercules, VESA, QuickDraw, Carbon, Metal, WinG.

Any platform can run any renderer or headless mode.

---

# 10. INSTALLER + LAUNCHER

Three installation modes:

1. Portable  
2. Per-user  
3. All-users  

Setup provides **install**, **repair**, and **uninstall**.  
Installer respects directory contract; repair audits only manifest files.  
Launcher can control multiple instances, manage mods, accounts, tools, wiki/forum access, messaging, tracking, and network browsing.

Scripts:

```yaml
setup → installer/repair/uninstaller
dominium → launcher
```

Game runs with or without launcher.

---

# 11. CONTRIBUTING

Requirements:

- Determinism preserved  
- C89/C++98 compliance  
- Specification updates for any change  
- Tests for all new features (unit + replay + integration)  
- Documentation updates  
- No floats in simulation  
- No platform API in `/engine`  
- No game logic in `/engine`

---

# 12. LICENSE

Tiered system:

- Engine: permissive open source (TBD)  
- Game assets: proprietary or CC-BY-NC depending on pack  
- Tools: open  
- Mods: author-owned

`/docs/legal/LICENCE.md` defines terms.

---

# 13. STATUS

Completed:
- Deterministic kernel specification  
- ECS foundation  
- Messaging and job systems  
- Serialization v3  
- Chunk/subchunk world format  
- Prefabs  
- Mod loader  
- Platform and renderer abstraction frameworks  

In Development:
- Full renderer integration  
- Cut/fill terrain  
- Orbital logistics  
- Worker/robot AI  
- Server clusters  
- Editor suite  
- Retro platform parity  
- Unified launcher ecosystem  

---

# 14. COMMUNITY

Documentation: `/docs/design/`  
Roadmap: `/docs/spec/MILESTONES.md`  
Issues: GitHub  

Discord and dev-blog pending.

---

# 15. ACKNOWLEDGEMENTS

Dominium draws influence from deterministic simulation traditions, retro engineering practices, and long-term archival design philosophies.

---

# 16. FINAL NOTE

Dominium is an attempt at a **universal deterministic simulation engine**:

- Cross-era hardware  
- Perfect reproducibility  
- Planetary + orbital scale  
- Unlimited mod extensibility  
- Long-term archival survivability  

This README evolves as specifications advance.  
Definitive rules reside in `/docs/spec`.