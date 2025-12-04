# DOMINIUM  
## A Deterministic, Multi-Scale, Multi-Platform Simulation Engine and Game

Dominium is a **fully deterministic**, **integer-math**, **platform-agnostic**, **modular** engine and game built to run identically across:

- Modern systems (Windows, Linux, macOS)
- Legacy systems (Win9x, Win3.x, DOS, macOS Classic)
- Future systems (WASM/Web, consoles, embedded)
- Headless servers (dedicated simulation clusters)

Dominium is not “a game with an engine.”  
Dominium *is an engine*, with one official game built on top of it.  
Everything is deterministic, from physics to pathfinding to networks, across all supported targets.

This repository contains the full source tree for:
- The **Dominium Engine** (core deterministic C89/C++98 code)
- The **Dominium Game** (content-agnostic gameplay logic layer)
- The **Data Packs** (first-party assets)
- The **Tools & Editors**
- The **Ports** (retro and alternative platforms)
- The **Specification documents** (binding behaviour contract)
- The **Modding API** (deterministic, forward-compatible)

---

# 1. PROJECT VISION

Dominium aims to:

1. Provide a **universally reproducible simulation** where any two machines, of any architecture or era, produce identical results tick-for-tick.
2. Support **extreme temporal and spatial scales**, from 16th-meter microgrids up to multi-gigameter planetary surfaces and multi-system galaxies.
3. Run across decades of hardware, including ultra-constrained retro platforms.
4. Be **maximally modifiable**, without compromising determinism.
5. Support **2D and 3D vector and raster rendering**, interchangeable on the fly.
6. Support **surface and orbital simulation**, including:
   - Orbital ships and stations  
   - Docking/undocking  
   - Re-entry and ascent profiles (rails-based or approximate dynamics)  
   - Cargo tugs, drop pods, and construction of orbital infrastructure  
7. Provide a **unified construction system** using:
   - Block-based structural components  
   - Edge/face walls, floors, slabs, ramps  
   - Arbitrary vector splines (tunnels, rails, roads, bridges)  
   - Cut/fill terrain interaction  
   - Arbitrary grade or cliff formation  
8. Maintain a **clean separation** between:
   - Physical domains (surfaces)
   - Logical domains (space, orbital tracks)
9. Support a fully deterministic **multiplayer / multi-server universe** capable of coordinating many planets.

Dominium is built to last for decades and outlive the hardware it first shipped on.

---

# 2. CORE PHILOSOPHY

The entire engine is designed around the following non-negotiable principles:

### 2.1 Determinism
Every simulation result is bit-identical for:
- Same inputs  
- Same tick schedule  
- Same modset  
- Same engine version  

No floating point appears in simulation code.  
All math uses integers or fixed-point formats.

### 2.2 Strict Phasing and Ordering
The engine is structured into immutable tick phases:
1. Input  
2. Pre-state  
3. Simulation (multi-lane)  
4. Networks  
5. Merge  
6. Post-process  
7. Finalize  

No system may run outside its assigned slot.

### 2.3 Spatial Hierarchy
Worlds are structured into multi-scale grids:

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
Supercont. = 268,435,456 m
Surface = 4,294,967,296 m

One surface per planet.

Surfaces are **not continuous arrays**, but **collections of sparse microgrids**, enabling:
- Underground structures  
- Cut/fill  
- Multi-level buildings  
- Vector networks intersecting grids  

### 2.4 Universal Modularity
Everything is plug-and-play:
- Renderers (OpenGL, DX9, DX11, SDL vector)
- Audio backends  
- Platform backends  
- Data packs  
- Mods  
- Tools  

No engine modification required to add new content or systems.

### 2.5 Platform Breadth
The engine compiles and runs on:
- C89 compilers  
- No libc extensions  
- No platform-specific hacks in sim code  

Ports adapt to the engine, never the other way around.

---

# 3. REPOSITORY OVERVIEW

The repository is organised into top-level directories:

/docs – design and specification documents
/engine – deterministic engine core (C/C++98)
/game – game layer using engine
/data – base assets, DLCs, packs
/mods – third-party mod ecosystem
/tools – editors, devkits, pipelines
/tests – unit, integration, replay, perf tests
/external – vendored dependencies
/build – build scripts and outputs
/package – installers and retro media layouts
/scripts – automation and maintenance
/ports – DOS, Win3.x, Win9x, macOS Classic, WASM, consoles

Each directory is formally defined in the **Directory Contract** (`/docs/spec/DIRECTORY_CONTRACT.md`).

---

# 4. BUILDING

### 4.1 Modern platforms
Use CMake:

mkdir build
cd build
cmake ..
cmake --build .

Every build invocation increments the global repository build number (stored in `.dominium_build_number`) and writes `build/generated/dom_build_version.h`; multi-target builds share the same number.

### 4.2 Retro platforms
Each `/ports/<target>/config/` contains its own build instructions.

Examples:
- DOS: OpenWatcom + wmake  
- Win3.x: MASM + VC++ 1.52  
- Win9x: MSVC6 + DX7 SDK  
- macOS Classic: CodeWarrior + MPW  
- WASM: Emscripten  

These builds produce reduced-fidelity executables but identical simulation behaviour.

---

# 5. RUNNING

### 5.1 Headless server
./dominium_server --world myworld

### 5.2 Client
./dominium_client

Clients and servers communicate via deterministic lockstep protocols.

---

# 6. MODDING

Modding is deterministic and fully sandboxed.

Each mod directory contains:
- `mod.json` (manifest)
- Prefabs  
- Data packs  
- Scripts (optional, deterministic subset of Lua)  

Mod loading order:
1. Base  
2. DLC  
3. Mods sorted by UUID  

Mods may add:
- Entities  
- Blocks  
- Jobs  
- Networks  
- Graphical assets  
- UI  

Mods may not:
- Modify engine behaviour  
- Introduce nondeterministic code  
- Patch binaries  

---

# 7. DATA FORMAT BASICS

All simulation data uses:
- Integer math  
- Fixed-size structs  
- Little-endian  
- No padding  
- No floats  
- No pointers  

Save files contain:
- Entities  
- Components  
- Networks  
- Jobs  
- Messages  
- Prefab references  
- Chunk microgrids  
- World snapshot  
- Optional replay log  

Everything is CRC-verified and version-tracked.

---

# 8. SURFACE AND SPACE ARCHITECTURE

Dominium supports **two complementary domains**:

### 8.1 Physical domains  
- Planetary surfaces  
- Underground layers  
- Oceans  
- Terrain grids  
- Structural microgrids  
- Buildings  
- Vector networks (rails, roads, conveyors, pipes, tunnels)

### 8.2 Logical domains  
- Orbits  
- Transfer windows  
- Docking graphs  
- Lagrange points  
- Asteroid belts  
- Gas clouds  
- Electromagnetic hazard areas  
- Orbital stations and ships  

Space simulation is **on rails**, deterministic, integer-based:
- Discrete orbital tracks  
- Deterministic transitions  
- Docking ports as graph nodes  
- Cargo routing between orbital/logical nodes  

---

# 9. CONTRIBUTING

Contributions must follow:

- Determinism rules  
- Specification compliance  
- C89/C++98 core style  
- Strict linting (`clang-format`, `cpplint`)  
- No floating-point in simulation  
- No platform APIs outside `/engine/platform`  
- No game logic in `/engine`  

All new features require:
- Spec update  
- Tests (unit + replay)  
- Documentation  

---

# 10. LICENSE

The project is released under a tiered licensing system:

- Engine core: permissive open source licence (to be finalised)  
- Game assets: proprietary or CC-BY-NC depending on pack  
- Tools: open source  
- Mods: copyright remains with authors  

See `/docs/legal/LICENCE.md`.

---

# 11. STATUS

Dominium is under active development.

Completed:

- Deterministic kernel spec  
- ECS core foundation  
- Messaging architecture  
- Job system  
- Serialization v3  
- World chunk/subchunk format  
- Prefab system  
- Mod loader  
- Platform abstraction design  
- Rendering abstraction design  

In development:

- 2D/3D renderer integration  
- Full cut/fill terrain system  
- Orbital logistics  
- Worker/robot AI  
- Multiplayer server clusters  
- Editor suite  

---

# 12. CONTACT & COMMUNITY

- Discord: *TBD*  
- Developer Blog: *TBD*  
- Documentation Portal: `/docs/design/`  
- Issue Tracker: GitHub Issues  
- Roadmap: `/docs/spec/MILESTONES.md`  

---

# 13. ACKNOWLEDGEMENTS

Dominium stands on:
- The philosophy of deterministic simulation (Factorio, Dwarf Fortress inspirations)
- The engineering traditions of old-school C and embedded systems
- The desire to create a game that will run long after modern hardware becomes obsolete.

---

# 14. FINAL NOTE

Dominium is not a toy project.  
It is an attempt at a **universal simulation engine** that:

- Spans eras of hardware  
- Maintains perfect determinism  
- Supports planetary and orbital scales  
- Is fully extensible and moddable  
- Can run archived forever  

This README is a living document.  
All architectural detail lives in `/docs/spec`.
