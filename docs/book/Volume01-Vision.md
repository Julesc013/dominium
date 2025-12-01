```markdown
// docs/book/Volume01-Vision.md
# Dominium Design Book v3.0
## Volume 01 — Vision

### Overview
Dominium is a deterministic, industrial simulation spanning property-to-planet scale. It prioritises an engine-first, simulation-first approach using integer and fixed-point math, multi-network infrastructure, and cross-platform support from Windows 2000+, macOS 10.6+, and Linux, with retro paths for older systems. Realistic technology (no fantasy tech unless DLC) and mod-first extensibility underpin every system.

### Requirements (MUST)
- Maintain bit-for-bit determinism across platforms using integer/fixed-point math and fixed tick ordering.
- Support the linear technical order emphasising engine, time system, core simulation, networks, world structure, logistics, economy, workers, multiplayer, rendering, platform abstraction, modding, tools, and packaging.
- Target platforms: Windows 2000+/macOS 10.6+/Linux (stage 1), later Win98 SE+/classic macOS/DOS with degradations; build with CMake/Make/MSVC.
- Deliver artifacts: `dom_client`, `dom_server`, `dom_hclient`, `dom_tools_*`.
- Adhere to C89 for deterministic core; C++98 (no exceptions/RTTI/templates beyond basics) for non-core modules.
- Ensure deterministic data formats that are endian/alignment neutral and forward/backward compatible.
- Follow roadmap milestones M0–M8 to stage features (design book, core loop, networks, logistics, economy/research, climate, UI, modding, release engineering).

### Recommendations (SHOULD)
- Favour realistic industrial progression, science grounded in engineering, and TEU-based logistics.
- Spread heavy systems via multi-rate scheduling to balance load while preserving determinism.
- Use dense, ID-ordered data structures and chunk-based world paging for scalability.
- Present multi-view UI (ortho, iso, 3D) that is renderer-agnostic and accessible.
- Keep modding and DLC layered: base pack → official DLC → user mods → local overrides.

### Prohibitions (MUST NOT)
- No fantasy technology unless explicitly introduced by DLC.
- No floating-point simulation, nondeterministic scheduling, or asynchronous side effects.
- No platform-specific code in core modules; no implicit RNG/time dependence.
- No hidden singletons or global mutable state outside the defined spec.

### Detailed Sections
#### 1.1 — Core Vision
Dominium is a pure deterministic machine: identical inputs and versions produce identical state each tick. All gameplay—networks, logistics, economy, workers, climate—runs on fixed pipelines, backpressure over loss, and reproducible math. Simulation integrity trumps real-time speed; UPS may scale down deterministically under load.

#### 1.2 — Scope and Universe
The universe contains galaxies, solar systems, and planets (e.g., Sol, Earth/Mars/Moon) with deterministic time and content profiles. Worlds use chunked spatial hierarchies (subchunk→chunk→superchunk→hyperchunk) and support property-to-planet play, later extending to interstellar settings via DLC/mods.

#### 1.3 — Platform and Language Constraints
Core uses C89 with allowed headers only; no C99 features, VLAs, or non-portable extensions. Non-core optional modules compile as C++98 without exceptions/RTTI and avoid STL across APIs. Build systems: CMake primary; Make and legacy MSVC supported. Graphics backends: SDL1/SDL2/OpenGL 1.1/2.0/DX9 (later DX11/software).

#### 1.4 — Roadmap and Milestones
M0 finalises Design Book v3.0 and SPEC-core; M1 delivers engine foundations (I/O, logging, RNG, tick loop, chunk paging); M2 adds networks (power/data/fluids); M3 logistics; M4 economy/research; M5 climate/weather/hydrology; M6 UI/UX across render modes; M7 tools/modding (editor, pipeline, Lua); M8 release engineering (packaging/launcher/outputs).

#### 1.5 — Design Principles
- Determinism: tick-driven phases, fixed UPS set {1,2,5,10,20,30,45,60,90,120,180,240}, stable iteration order, no random packet loss.
- Realism: engineering-based research, physical goods/services, authentic power/data/fluids, industrial simulation fantasy.
- Mod-first: layered packs, deterministic schemas, sandboxed Lua, and deterministic data files.
- Accessibility and reach: scalable UI, renderer-independent presentation, retro fallbacks.

### Cross-References
- Volume 02 — Simulation (determinism kernel, tick pipeline)
- Volume 03 — World (spatial hierarchy, terrain/construction)
- Volume 04 — Networks (power/data/fluids/transport)
- Volume 05 — Economy (markets, finance, logistics costs)
- Volume 06 — Climate (weather, hydrology, environment)
- Volume 07 — UIUX (views, accessibility, HUD, input)
- Volume 08 — Engine (language/build rules, ECS, messaging)
- Volume 09 — Modding (content stack, packs, Lua limits)
```
