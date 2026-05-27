# Structured Registers — Dominium Architecture II

## 1. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Unified documentation/source-of-truth | Consolidate architecture and Codex-facing instructions into a coherent source of truth. | V4 replacements for BUILDING.md, SPEC_CORE.md, DATA_FORMATS.md, and DIRECTORY_CONTEXT.md were generated in this chat; actual on-disk application is unverified. | The four docs plus docs/dev/dominium_new_addendum.txt consistently guide Codex without contradictions. | active | P0 | high | FACT |
| WORKSTREAM-02 | Deterministic core/kernel | Implement the deterministic C89 simulation kernel. | Detailed V3 determinism material and SPEC_CORE V4 exist as visible design outputs. | A ticking deterministic core with fixed phases, lanes, merge, fixed-point math, and no sim floats. | active | P0 | high | FACT |
| WORKSTREAM-03 | ECS architecture | Define and implement deterministic entity/component/system architecture. | V3 1B material and engine/ecs dev spec were generated. | Stable entity IDs/generations, POD components, dense arrays, sorted active lists, deterministic iteration. | active | P0 | high | FACT |
| WORKSTREAM-04 | Messaging, events, jobs | Provide deterministic event buses, command buffers, jobs, deferred ops and interrupts. | V3 1B-2a/b visible and sim dev spec generated. | Fixed-size queues, deterministic ordering, one-tick cross-lane/global latency, job assignment with stable tie-breaks. | active | P0 | high | FACT |
| WORKSTREAM-05 | Spatial hierarchy and cosmic identity | Define coordinates, scale ladder, sparse chunking, and universe/galaxy/system/planet/surface IDs. | User fixed the scale ladder and defaults; SPEC_CORE/DATA_FORMATS were updated around it. | Single Earth surface MVP with full hierarchy capability and sparse chunks/microgrids. | active | P0 | high | FACT |
| WORKSTREAM-06 | Terrain, cut/fill, and microgrids | Support terrain edits, underground/overground structures, and logical separation from base terrain. | Three-layer model established: immutable base terrain, earthworks deltas/cavities, structural microgrids. | Flat MVP surface with future-ready cut/fill/cavity hooks. | active | P1 | high | FACT |
| WORKSTREAM-07 | Building system: cells, faces, edges, fixtures | Use a unified building system for surface, underground and orbital structures. | Blocks/modules/cells/faces/edges model and explicit fixture/anchor system defined. | MVP can place functional blocks/devices and simple walls/floors; future supports collapse/destruction. | active | P0 | high | FACT |
| WORKSTREAM-08 | Vector corridor/spline infrastructure | Support arbitrary vector splines for roads, rails, tunnels, bridges, platforms and utilities. | Alignment-to-chainpoint-to-linear-microgrid pipeline defined; full implementation deferred beyond minimal MVP. | Data-driven corridor archetypes, fixtures/anchors, bridge/tunnel/cut/fill generation, node topology. | active/future | P1 | high | FACT |
| WORKSTREAM-09 | Utility networks: power, data, fluids, thermal | Graph/field utility systems for machines and infrastructure. | Power/data/fluid/thermal network specs generated; MVP requires minimal interactive prototypes. | Power gen/load works first; fluid/data minimal snapshots; thermal may be stubbed. | active | P0/P1 | high | FACT |
| WORKSTREAM-10 | Transport systems | Represent rail, road, water, air and space movement as graphs/corridors/fields. | Generalized design exists; MVP only needs one minimal transport segment/vehicle. | Unified transport graph with modes, vehicles, stations, signals, bridges/tunnels. | active/future | P1 | medium-high | FACT |
| WORKSTREAM-11 | Pathfinding and deterministic movement | Deterministic path and vehicle/worker movement primitives. | Engine/path and engine/physics dev specs generated; no code confirmed. | Integer A*/routing and simple kinematics suitable for workers/vehicles/corridors. | active | P1 | medium-high | FACT |
| WORKSTREAM-12 | Surface vs space and orbital systems | Separate high-resolution surface sim from logical on-rails space sim. | Design defined, post-MVP. | Orbit rails, SOI, Lagrange points, belts/clouds/EM fields, local bubbles, docking transitions. | future | P2 | high | FACT |
| WORKSTREAM-13 | Orbital construction/logistics | Support construction and servicing of orbital ships/stations. | Conceptual design defined, not MVP. | Orbital yards/stations/ships serviced by rockets/drop pods/cargo tugs. | future | P2 | high | FACT |
| WORKSTREAM-14 | Renderer/platform mix-and-match | Cleanly separate OS/platform and renderer backends and allow cross-product selection. | Addendum and BUILDING V4 specify platform API, renderer API, backend registry, DX9 MVP. | Win32+DX9 MVP; later SDL2/DX11/GL/VK/DX12/Linux/macOS/retro.  | active | P0 | high | FACT |
| WORKSTREAM-15 | Lua data and script binding | Enable Lua-driven data prototypes and sandboxed script interaction. | Codex clarification answered: /engine/script, Lua 5.4.4, API namespaces and sandbox. | Lua loads data/prefabs/jobs/net snapshots through safe deterministic engine APIs. | active | P0 | high | FACT |
| WORKSTREAM-16 | Serialization, save/replay, state hash | Persist and hash authoritative state deterministically. | DATA_FORMATS V4 generated; FNV-1a hash rule clarified. | Canonical serialization buffer for save/load/replay/hash, FNV-1a tick hash tests. | active | P0 | high | FACT |
| WORKSTREAM-17 | Build system and CMake | Create deterministic modular CMake build and stubs. | BUILDING V4 and root CMake draft/prompt exist; actual applied state unknown. | Root and per-dir CMake with explicit file lists, DR mode, MVP backend flags. | active | P0 | high | FACT |
| WORKSTREAM-18 | MVP client loop and UI/HUD | Produce a playable vector-only minimal loop. | Prompt generated for minimal client loop; no code confirmed. | 2D/3D camera, tick loop, vector rendering, selection/placement UI, minimal HUD. | active | P0/P1 | high | FACT |
| WORKSTREAM-19 | Testing and CI | Validate determinism and prevent regressions. | Tests dev spec generated; FNV tick+hash test planned. | Unit, integration, replay, perf tests; CI boundary checks. | active | P0/P1 | high | FACT |
| WORKSTREAM-20 | Legal/governance docs | Provide restrictive project governance, licence, contribution and security docs. | Drafts generated for README, LICENCE, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, CHANGELOG, .gitignore, etc. | Consistent, legally reviewed governance docs. | active draft | P1 | medium | FACT |
| WORKSTREAM-21 | Future multiplayer and server universe | Add deterministic multiplayer, server/shard interaction and cross-server trade/communication. | Planned after MVP; net protocol/dev specs exist conceptually. | Lockstep or server-authoritative multiplayer with async cross-surface interactions. | future | P2 | medium-high | FACT |
| WORKSTREAM-22 | Future platforms/renderers/assets | Add non-MVP renderers/platforms/textures/audio/music. | Roadmap defined; implementation deferred. | DX11/GL1/GL2/VK1/DX12, Windows 98, Linux/macOS, retro, textures/audio/music packs. | future | P2/P3 | medium-high | FACT |

## 2. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Use meter-based world coordinates with fixed substeps/Q16.16. | final | User selected world unit option B. | Fits base-16 hierarchy and avoids millimeter-wide coordinates. | Spatial representation and serialization use meter tiles plus substeps. | WORKSTREAM-05 | high | FACT |
| DECISION-02 | Use strict sim/render separation. | final | User selected rendering contract A. | Simplifies determinism proof. | Renderer is pure observer; sim has no GPU/OS dependencies. | WORKSTREAM-14 | high | FACT |
| DECISION-03 | Adopt base-16 spatial ladder from subnano to surface. | final | User explicitly provided ladder. | Matches fixed-point subdivisions and chunk hierarchy. | Constants and chunking derive from ladder. | WORKSTREAM-05 | high | FACT |
| DECISION-04 | Store surfaces as sparse microgrids/chunks, not continuous dense arrays. | final | User explicitly stated no continuous grid. | Full-size surfaces are too large dense. | Only active chunks/microgrids allocate data. | WORKSTREAM-05 | high | FACT |
| DECISION-05 | Default local world is Earth/Sol/Milky Way. | final | User stated default planet/system/galaxy. | Canonical single-player world. | MVP starts on Earth surface. | WORKSTREAM-05 | high | FACT |
| DECISION-06 | Support canonical surface plus multiple surface instances for shards/mirrors. | final-ish | User asked; assistant reconciled one surface vs sharding; no rejection. | Needed for servers and mirrors without cross-sim coupling. | SurfaceID identifies instance; one canonical default. | WORKSTREAM-09 | medium-high | FACT |
| DECISION-07 | Cross-surface interactions are asynchronous external events only. | final-ish | Assistant recommendation after sharding discussion; continuation accepted. | Avoids cross-shard desync. | No shared physics/networks across surfaces. | WORKSTREAM-09 | medium-high | FACT |
| DECISION-08 | Use on-rails orbital mechanics, not full n-body. | final-ish | Space mechanics answer. | Full n-body harms determinism/debuggability. | Orbit graph/rails and local bubbles. | WORKSTREAM-12 | high | FACT |
| DECISION-09 | Docking, landing and takeoff are state-machine/domain transitions. | final-ish | Space and orbital logistics answers. | One domain owns entity at a time. | Rockets/pods/craft transition via command events. | WORKSTREAM-12 | high | FACT |
| DECISION-10 | Use blocks/modules/cells/faces/edges as building simulation truth. | final | User and assistant building discussion. | Discrete sim supports pathing/collision/pressure/retro. | Buildings, stations, ships share representation. | WORKSTREAM-07 | high | FACT |
| DECISION-11 | Use vector shapes/splines as authoring, generation and visual layers only. | final | Building/spline discussions. | Avoid continuous geometry in sim. | Vectors bake into chainpoints/cells/meshes. | WORKSTREAM-08 | high | FACT |
| DECISION-12 | Place walls/floors/roofs on grid faces/edges including diagonals. | final | User explicitly requested. | Allows arbitrary orthogonal/diagonal layouts. | FaceWall/EdgeWall lattice needed. | WORKSTREAM-07 | high | FACT |
| DECISION-13 | Buildings rigid for now but schema supports destruction/collapse later. | final | User explicitly stated. | Avoids MVP complexity but future-proofs data. | Strength/connectivity fields may be present. | WORKSTREAM-07 | high | FACT |
| DECISION-14 | Doors/devices are explicit fixtures placed manually or by explicit blueprint/pattern. | final | User did not want auto doors; assistant socket model. | Avoids coding doors into each tunnel type. | Anchors/sockets + fixture entities. | WORKSTREAM-07 | high | FACT |
| DECISION-15 | Immutable base terrain plus earthworks deltas and cavities. | final | Cut/fill discussion. | Preserves natural terrain and tracks modifications. | H_eff=H_base+ΔH; cavities overlay terrain. | WORKSTREAM-06 | high | FACT |
| DECISION-16 | Vector alignments bake into deterministic ChainPoints and linear microgrids. | final | Spline answer. | Runtime efficiency/determinism. | Corridor generator pipeline. | WORKSTREAM-08 | high | FACT |
| DECISION-17 | Connections occur at nodes; mid-segment connections create/split nodes. | final | Earlier way-spline answer. | Simplifies topology and signalling. | Graph topologies remain explicit. | WORKSTREAM-08 | medium-high | FACT |
| DECISION-18 | Generalize architecture to five primitives. | final-ish | Generalization answer. | Avoids 100 subsystems. | Frames/lattices, archetypes/components, graphs/fields, blueprints/diffs, ticks/jobs. | WORKSTREAM-01 | high | FACT |
| DECISION-19 | MVP is one full-size Earth surface with all systems interactable via minimal prototypes. | final | User explicit MVP. | Test core breadth without full content. | Implementation scope. | WORKSTREAM-18 | high | FACT |
| DECISION-20 | MVP uses Lua for all data. | final | User explicit MVP. | Data-driven prototypes. | Lua binding must exist. | WORKSTREAM-15 | high | FACT |
| DECISION-21 | MVP uses 2D vector top-down and 3D vector first-person rendering. | final | User explicit MVP. | Avoid texture/sound asset bottleneck. | Vector render shell needed. | WORKSTREAM-18 | high | FACT |
| DECISION-22 | Initial platform/render target is Windows 2000+ to Windows 11+ with DX9.0c and Win32/SDL2. | final-ish | User explicit rollout. | Focus implementation. | Win32+DX9 first; SDL2 optional/later. | WORKSTREAM-14 | medium-high | FACT |
| DECISION-23 | Textures, sounds and music are post-MVP. | final | User stated they will make textures/sounds/music later. | Avoid assets during core work. | Null audio/vector only for now. | WORKSTREAM-22 | high | FACT |
| DECISION-24 | Multiplayer is post-MVP. | final | User next steps list. | Core first. | Net stubs/serialization now; live multiplayer later. | WORKSTREAM-21 | high | FACT |
| DECISION-25 | Space/Sol system is post-MVP. | final | User next steps list. | Core/surface first. | Orbital stubs/context only. | WORKSTREAM-12 | high | FACT |
| DECISION-26 | Add /engine/script for Lua binding and amend directory contract. | final | Codex clarification answer. | Needed for Lua without misplacing code. | New engine subdir. | WORKSTREAM-15 | high | FACT |
| DECISION-27 | Vendor Lua 5.4.4 under /third_party. | final-ish | Clarification answer. | Chosen Lua runtime. | Third-party pinned source/includes. | WORKSTREAM-15 | medium-high | FACT |
| DECISION-28 | Lua API is sandboxed and limited to data/light orchestration. | final | Clarification answer. | Protect determinism/security. | No OS/native module access; commands only. | WORKSTREAM-15 | high | FACT |
| DECISION-29 | Use FNV-1a 64-bit over canonical serialized sim state for tests. | final | Clarification answer. | Early deterministic validation. | Implement dom_core_hash and serializer. | WORKSTREAM-16 | high | FACT |
| DECISION-30 | Codex must use only listed files. | final | User explicit. | Avoid hidden-project assumptions. | Prompts scope tightly. | WORKSTREAM-22 | high | FACT |
| DECISION-31 | Regenerate BUILDING.md, SPEC_CORE.md, DATA_FORMATS.md, DIRECTORY_CONTEXT.md as next docs. | done | User explicit; assistant generated V4 replacements. | Aligns core spec layer. | Docs should be applied/verified. | WORKSTREAM-01 | high | FACT |
| DECISION-32 | Licence should be restrictive except personal use/source viewing. | draft/final intent | User explicitly requested. | Protect IP. | LICENCE.md draft generated; legal review needed. | WORKSTREAM-20 | medium | FACT |

## 3. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Apply/verify BUILDING.md V4 | P0 | U0 | User/Codex | Generated BUILDING V4 | Existing docs/BUILDING.md | Updated BUILDING.md | Patch or compare file | WORKSTREAM-01 | FACT |
| TASK-02 | Apply/verify SPEC_CORE.md V4 | P0 | U0 | User/Codex | Generated SPEC_CORE V4 | Existing docs/SPEC_CORE.md | Updated SPEC_CORE.md | Patch or compare file | WORKSTREAM-01 | FACT |
| TASK-03 | Apply/verify DATA_FORMATS.md V4 | P0 | U0 | User/Codex | Generated DATA_FORMATS V4 | Existing docs/DATA_FORMATS.md | Updated DATA_FORMATS.md | Patch or compare file | WORKSTREAM-01 | FACT |
| TASK-04 | Apply/verify DIRECTORY_CONTEXT.md V4 | P0 | U0 | User/Codex | Generated DIRECTORY_CONTEXT V4, User tree | Existing docs/DIRECTORY_CONTEXT.md | Updated directory contract | Patch or compare file | WORKSTREAM-01 | FACT |
| TASK-05 | Verify dominium_new_addendum.txt contains renderer/platform addendum | P0 | U0 | User/Codex | Addendum generated in chat | docs/dev/dominium_new_addendum.txt | Correct addendum file | Inspect/paste/update | WORKSTREAM-01 | FACT |
| TASK-06 | Generate CMake/build skeleton | P0 | U1 | Codex | Docs consistency | CMake prompt, BUILDING V4 | Root/per-dir CMake and minimal stubs | Run generated prompt | WORKSTREAM-17 | FACT |
| TASK-07 | Implement core/sim/ECS shell | P0 | U1 | Codex | CMake skeleton, Core docs | Core and sim prompts | dom_core and dom_sim skeleton files | Run core then sim prompts | WORKSTREAM-02 | FACT |
| TASK-08 | Implement Win32 + DX9 vector shell | P0 | U1 | Codex | Platform/render API | Render/platform prompt | Window, input, DX9 vector backend | Run prompt after build skeleton | WORKSTREAM-14 | FACT |
| TASK-09 | Wire minimal client loop | P0 | U1 | Codex | Core/sim/render/platform shells | Client loop prompt | Empty Earth surface loop with cameras | Run prompt after shells | WORKSTREAM-18 | FACT |
| TASK-10 | Implement 2D/3D vector camera/input controls | P0 | U1 | Codex | Client loop, Render API | Input/camera spec needs finalization | Pan/zoom/toggle first-person camera | Finalize API then implement | WORKSTREAM-18 | FACT |
| TASK-11 | Add /engine/script to DIRECTORY_CONTEXT/build | P0 | U1 | Codex | Lua decision | Clarification answer | Directory contract and build include script dir | Patch docs and CMake | WORKSTREAM-15 | FACT |
| TASK-12 | Vendor Lua 5.4.4 | P0 | U1 | Codex/User | Third-party policy | Lua source, Licence | Pinned Lua source/includes | Verify and add | WORKSTREAM-15 | FACT |
| TASK-13 | Implement script VM and sandbox | P0 | U1 | Codex | Lua vendored | Lua API/sandbox spec | dom_script_vm and sandbox files | Create /engine/script skeleton | WORKSTREAM-15 | FACT |
| TASK-14 | Implement Lua bindings | P0 | U1 | Codex | Script VM, ECS/prefabs/net/jobs APIs | Binding scope | dom.entity/query/prefab/data/net/jobs/random | Implement minimal safe bindings | WORKSTREAM-15 | FACT |
| TASK-15 | Create minimal Lua data prototypes | P0 | U1 | Codex/User | Lua bindings | Data schema decision | Generator/consumer/cable/worker/vehicle prototypes | Define data tables | WORKSTREAM-15 | FACT |
| TASK-16 | Reconcile Lua-for-data with DATA_FORMATS JSON sections | P0 | U1 | User/Codex | MVP data decision | DATA_FORMATS V4 | Clear data policy | Update docs if needed | WORKSTREAM-15 | INFERENCE |
| TASK-17 | Implement FNV-1a hash | P0 | U1 | Codex | Core skeleton | Hash spec | dom_core_hash.[ch] | Implement early | WORKSTREAM-16 | FACT |
| TASK-18 | Implement canonical state serializer and headless hash test | P0 | U1 | Codex | ECS/sim state, Hash | DATA_FORMATS, test spec | Serialized state hash and test | Implement after sim shell | WORKSTREAM-16 | FACT |
| TASK-19 | Implement single Earth surface spatial roots | P0 | U1 | Codex | Spatial constants | Scale ladder, SPEC_CORE | Flat/sparse Earth surface root | Implement minimal spatial module | WORKSTREAM-05 | FACT |
| TASK-20 | Implement minimal power prototype | P0 | U1 | Codex | ECS/network components, Lua data | SPEC_CORE | Generator-consumer-cable working | Implement first network | WORKSTREAM-09 | FACT |
| TASK-21 | Implement minimal fluid/data prototypes | P1 | U1 | Codex | Network shell | SPEC_CORE | Simple flow and data snapshots | Implement after power | WORKSTREAM-09 | FACT |
| TASK-22 | Implement worker/job prototype | P0 | U1 | Codex | Jobs, path, Lua data | Job specs | Worker walks/performs fixed job | Implement with simple path | WORKSTREAM-04 | FACT |
| TASK-23 | Implement minimal building/device placement | P0 | U1 | Codex | Lua prefabs, ECS, client UI | Building spec | Place generator/consumer/cable/building | Implement after data loading | WORKSTREAM-07 | FACT |
| TASK-24 | Implement minimal HUD/hotbar/selection | P1 | U1 | Codex | Client loop, render/UI | MVP UI needs | Tick/hash/status/hotbar/inspector | Implement thin UI | WORKSTREAM-18 | FACT |
| TASK-25 | Implement one transport segment and vehicle | P1 | U1 | Codex | Path/physics/render | Pick rail/road | Deterministic vehicle movement | Choose simplest mode | WORKSTREAM-10 | FACT |
| TASK-26 | Implement minimal save/load roundtrip | P1 | U2 | Codex | Serializer, world state | DATA_FORMATS | Save/load same hash | Implement after serializer | WORKSTREAM-16 | FACT |
| TASK-27 | Stub terrain cut/fill fields | P1 | U2 | Codex | Spatial/chunk | Terrain design | Base terrain + ΔH/cavity placeholders | Implement flat terrain first | WORKSTREAM-06 | FACT |
| TASK-28 | Keep multiplayer as stub/future | P2 | U2 | Codex/User | Core/net | Roadmap | No premature multiplayer complexity | Do not implement live MP yet | WORKSTREAM-21 | FACT |
| TASK-29 | Keep space/Sol/orbital as stub/future | P2 | U2 | Codex/User | Core/spatial | Roadmap | No premature space implementation | Preserve design only | WORKSTREAM-12 | FACT |
| TASK-30 | Defer textures/audio/music/extra renderers | P2 | U2 | Codex/User | MVP scope | Roadmap | No asset dependency in MVP | Use vector/null audio | WORKSTREAM-22 | FACT |
| TASK-31 | Legal-review restrictive LICENCE.md | P1 | U2 | User/legal | Licence draft | Legal expertise | Valid restrictive licence | Seek review before public release | WORKSTREAM-20 | UNCERTAIN / UNVERIFIED |
| TASK-32 | Verify DirectX9/Win2000/SDK compatibility | P1 | U1 | User/Codex | External docs | DX9/Win2000 info | Confirmed viable platform target | Research/test | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| TASK-33 | Verify Lua 5.4.4 old compiler portability | P1 | U1 | User/Codex | Lua source, toolchains | Compiler tests | Confirmed or patched Lua | Test build | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| TASK-34 | Finalize DomDrawCmd/camera API | P0 | U1 | User/Codex | Addendum, DATA_FORMATS | Render API choices | Consistent render header | Resolve before DX9 implementation | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |

## 4. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Simulation must be deterministic for identical inputs/version. | technical | hard | V3/SPEC_CORE | All state order fixed; no nondeterminism. | Desync, invalid replays. | FACT | high |
| CONSTRAINT-02 | No floating point in authoritative simulation. | technical | hard | Repeated specs | Use integer/fixed-point only. | Cross-platform divergence. | FACT | high |
| CONSTRAINT-03 | /engine/core and /engine/sim must be C89. | technical | hard | BUILDING/CONTRIBUTING | Preserve retro/old compiler compatibility. | Build incompatibility. | FACT | high |
| CONSTRAINT-04 | Non-core engine/game may use C++98 max, no newer features. | technical | hard | BUILDING/CONTRIBUTING | Avoid modern language dependence. | Toolchain mismatch. | FACT | high |
| CONSTRAINT-05 | No OS headers outside /engine/platform or /ports. | technical/architecture | hard | DIRECTORY_CONTEXT/Addendum | Keep platform isolation. | Layer contamination. | FACT | high |
| CONSTRAINT-06 | No graphics headers/calls outside /engine/render. | technical/architecture | hard | Addendum | Keep renderer isolation. | GPU API leakage. | FACT | high |
| CONSTRAINT-07 | Codex must use only listed files/context. | process | hard | User statement | Avoid hallucinated context. | Wrong docs/code. | FACT | high |
| CONSTRAINT-08 | World mutations go through command buffers/deferred phases. | technical | hard | V3/Jobs/ECS | Safe deterministic mutation. | Mid-tick inconsistency. | FACT | high |
| CONSTRAINT-09 | No direct global writes from virtual lanes. | technical | hard | V3 determinism | Lane-local then merge. | Race/order bugs. | FACT | high |
| CONSTRAINT-10 | Binary formats little-endian; no pointers; no floats. | data | hard | DATA_FORMATS | Portable save/network. | Unreadable/incompatible saves. | FACT | high |
| CONSTRAINT-11 | No new top-level dirs unless DIRECTORY_CONTEXT updated. | process/directory | hard | Directory contract | Controlled structure. | Repo sprawl. | FACT | high |
| CONSTRAINT-12 | Use actual file names from user tree. | process/directory | hard | User tree | Avoid broken references. | Broken docs/Codex. | FACT | high |
| CONSTRAINT-13 | Lua script sandbox disables OS/time/native access. | security/technical | hard | Lua clarification | Protect determinism/security. | Sandbox escape/desync. | FACT | high |
| CONSTRAINT-14 | Lua may mutate sim only through deterministic engine APIs/commands. | technical | hard | Lua clarification | Preserve tick/order. | Undocumented state changes. | FACT | high |
| CONSTRAINT-15 | No dense full surface allocation. | resource/technical | hard | Spatial discussion | Use sparse chunks/microgrids. | Memory explosion. | FACT | high |
| CONSTRAINT-16 | Base game MVP uses one Earth surface. | scope | hard | User MVP | Keep scope bounded. | Multiworld scope creep. | FACT | high |
| CONSTRAINT-17 | Base terrain immutable. | technical | hard | Cut/fill discussion | Earthworks overlay base. | Loss of original terrain. | FACT | high |
| CONSTRAINT-18 | Structural microgrids separate from terrain. | technical | hard | Cut/fill discussion | Over/under structures remain distinct. | Terrain/structure conflation. | FACT | high |
| CONSTRAINT-19 | Blocks/modules are sim truth for structures. | technical | hard | Building decision | Deterministic structure/path/pressure. | Continuous geometry complexity. | FACT | high |
| CONSTRAINT-20 | Doors/devices must be explicitly placed fixtures. | user preference/technical | hard | User statement | No automatic doors. | Unwanted doors/type bloat. | FACT | high |
| CONSTRAINT-21 | Buildings rigid for MVP, but data future-proofs collapse. | scope/technical | hard | User statement | Avoid collapse implementation now. | MVP creep or incompatible data. | FACT | high |
| CONSTRAINT-22 | Splines are baked to discrete chainpoints for runtime. | technical | hard | Spline discussion | Runtime deterministic cells/graphs. | Runtime curve complexity. | FACT | high |
| CONSTRAINT-23 | Connections occur at explicit graph nodes. | technical | hard | Way connectivity discussion | Topology stable. | Mid-edge graph ambiguity. | FACT | medium-high |
| CONSTRAINT-24 | Networks deterministic, fixed capacity/latency/ordering. | technical | hard | Network specs | No random loss/ordering. | Desync. | FACT | high |
| CONSTRAINT-25 | Renderer/platform mix-and-match via APIs/vtables. | architecture | hard | User rollout/addendum | Extensible backend matrix. | Hardcoded backend coupling. | FACT | high |
| CONSTRAINT-26 | Cross-surface interactions async only. | architecture | hard | Sharding discussion | Surface isolation. | Cross-shard desync. | FACT | medium-high |
| CONSTRAINT-27 | MVP vector-only, textures/audio later. | scope | hard | User MVP | No asset blockers. | Scope creep. | FACT | high |
| CONSTRAINT-28 | All systems interactable in MVP via minimal prototypes. | scope | hard | User MVP | Thin systems, not full simulation. | Either too narrow or too broad. | FACT | high |
| CONSTRAINT-29 | Unknown binary blocks skippable. | data compatibility | hard | DATA_FORMATS | Forward compatibility. | Future format breakage. | FACT | high |
| CONSTRAINT-30 | No hash tables serialized directly; sorted lists only. | data/determinism | hard | DATA_FORMATS | Deterministic serialization. | Ordering mismatch. | FACT | high |
| CONSTRAINT-31 | FNV hash over authoritative state only. | testing | hard | Hash clarification | Stable determinism testing. | False positives/negatives. | FACT | high |
| CONSTRAINT-32 | CMake explicit file lists; no globbing. | build | hard | BUILDING | Deterministic sources. | Accidental files included. | FACT | high |
| CONSTRAINT-33 | Retro builds isolated under /ports. | build/platform | hard | BUILDING/ports | Modern CMake not contaminated. | Toolchain sprawl. | FACT | high |
| CONSTRAINT-34 | Licence restrictive except personal use/source viewing. | legal/user preference | hard intent | User request | Distribution restrictions. | Licence intent violated. | FACT | medium |
| CONSTRAINT-35 | No textures/sounds/music required in MVP. | scope/resource | hard | User statement | Vector/null audio initially. | Asset bottleneck. | FACT | high |
| CONSTRAINT-36 | Tests must avoid OS randomness/wallclock dependencies. | testing | hard | Tests dev spec | Cross-platform validation. | Flaky tests. | FACT | high |

## 5. User Preference Register

| ID | Preference | Area | Explicit or inferred | Strength | Implication for future assistant | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREFERENCE-01 | Maximum-fidelity, structured handoff rather than normal summary. | handoff | explicit | strong | Produce exhaustive self-contained reports with labels and IDs. | FACT | high |
| PREFERENCE-02 | No invented facts or silent inference. | reasoning | explicit | strong | Label uncertainties and avoid unsupported claims. | FACT | high |
| PREFERENCE-03 | Preserve rejected/superseded/deprioritised options. | handoff | explicit | strong | Do not erase design history. | FACT | high |
| PREFERENCE-04 | Prioritise direct user statements over assistant suggestions. | reasoning | explicit | strong | Treat suggestions as tentative unless accepted. | FACT | high |
| PREFERENCE-05 | Use Codex with strict scoped prompts. | coding/process | explicit | strong | Prompts must list source files and constraints. | FACT | high |
| PREFERENCE-06 | Detailed architecture/spec outputs, often as long as possible. | length/detail | inferred | strong | Provide comprehensive specs when asked. | INFERENCE | high |
| PREFERENCE-07 | Vector graphics first; textures/sounds/music later. | MVP scope | explicit | strong | Avoid asset work in early implementation. | FACT | high |
| PREFERENCE-08 | Lua for all MVP data. | data/modding | explicit | strong | Implement script/data bridge early. | FACT | high |
| PREFERENCE-09 | Determinism and integer math as non-negotiable. | engineering | explicit | strong | Challenge any float/nondeterministic design. | FACT | high |
| PREFERENCE-10 | Retro and future extensibility kept in architecture even if deferred. | architecture | explicit/inferred | strong | Do not hardcode MVP-only assumptions. | INFERENCE | high |
| PREFERENCE-11 | Restrictive licensing. | legal | explicit | strong | Docs/licence should enforce source-view/personal-use only. | FACT | medium |
| PREFERENCE-12 | Do not make doors auto-appear; arbitrary explicit placement. | building UX | explicit | strong | Use fixture/anchor system. | FACT | high |
| PREFERENCE-13 | Use real file tree and avoid phantom files. | repo/process | explicit | strong | References must match listed paths. | FACT | high |

## 6. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Have V4 docs been applied to the actual repository? | Codex state depends on disk contents. | Generated V4 docs exist in chat. | On-disk state unknown. | Inspect repo files. | P0 | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | Does the actual repo contain /engine, /game, /data etc. yet? | Determines whether Codex creates dirs or edits existing. | User tree showed only root/docs. | Actual filesystem unknown. | Codex/file inspection. | P0 | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | Should docs root remain flat or use /docs/spec? | Old and new docs differ. | User tree has docs root files. | Final organization unclear if future moves planned. | Follow current tree or user confirm. | P0 | WORKSTREAM-01 | FACT / UNCERTAIN |
| QUESTION-04 | How to reconcile Lua-for-all-data with JSON-oriented DATA_FORMATS sections? | Affects data loader and Codex implementation. | User wants Lua MVP; DATA_FORMATS includes JSON/mod schema. | Final long-term policy. | Update DATA_FORMATS/BUILDING or ask user. | P0 | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | What is the final DomDrawCmd/camera API? | DX9 renderer implementation needs exact API. | Addendum and DATA_FORMATS have differing sketches. | Final coordinate/types. | Finalize dom_render_api.h. | P0 | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Native Win32 or SDL2 first? | Initial platform implementation scope. | User allowed both; assistant recommended Win32 first. | Whether SDL2 is MVP requirement. | Clarify or implement Win32 first with SDL2 optional. | P1 | WORKSTREAM-14 | FACT / INFERENCE |
| QUESTION-07 | Can DX9.0c reliably target Windows 2000 SP4 through Windows 11? | Platform feasibility. | User wants it. | SDK/runtime details. | External verification/test. | P1 | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | Can SDL2 support Windows 2000 target? | If SDL2 is used early. | SDL2 named by user. | Version support. | External verification. | P2 | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | Can Lua 5.4.4 build with old/retro compilers? | Vendor/runtime feasibility. | Assistant recommended 5.4.4. | Portability/patched needs. | Test/verify. | P1 | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | What exact ECS component set is MVP? | Data/scripts/networks need fields. | Transform/occupancy/network/worker/building implied. | Exact fields. | Define minimal component schema. | P0 | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | Which transport mode first for MVP? | Implementation priority. | Need at least one segment/vehicle. | Rail vs road choice. | User or Codex decide simplest. | P1 | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | What does “fully complete core” mean at MVP depth? | Scope control. | All systems interactable minimal. | How thin each system can be. | MVP acceptance checklist. | P0 | WORKSTREAM-18 | UNCERTAIN / UNVERIFIED |
| QUESTION-13 | Do generated root docs like VERSION exist or matter? | Avoid referencing missing files. | VERSION generated earlier; user tree lacks it. | User intent. | Inspect repo/ask if needed. | P2 | WORKSTREAM-20 | UNCERTAIN / UNVERIFIED |
| QUESTION-14 | Is the restrictive licence legally valid? | Release risk. | Draft exists. | Legal enforceability. | Legal review. | P1 | WORKSTREAM-20 | UNCERTAIN / UNVERIFIED |
| QUESTION-15 | Are docs/dev files identical to generated dev specs? | Codex source fidelity. | Names listed. | Contents uninspected. | Inspect files. | P0 | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |

## 7. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Referenced ZIP with 17 files | file reference | Existing files from earlier chat | Mentioned, not inspected | User mention | maybe | Visible transcript does not include zip contents. | FACT / UNCERTAIN |
| ARTIFACT-02 | V3 Volume 1A-1 Determinism Kernel Foundations | generated document | Determinism foundations | Visible | Transcribed in chat | yes | Important historical spec. | FACT |
| ARTIFACT-03 | V3 Volume 1A-2 Determinism Pipeline & Parallelism | generated document | Tick/lane/merge/network propagation | Visible | Transcribed | yes | Important historical spec. | FACT |
| ARTIFACT-04 | V3 Volume 1B-1 Core Simulation Architecture | generated document | ECS/entity/component/system model | Visible | Transcribed | yes | Important historical spec. | FACT |
| ARTIFACT-05 | V3 Volume 1B-2a Messaging Architecture | generated document | Events/commands/deferred ops | Visible | Transcribed | yes | Important. | FACT |
| ARTIFACT-06 | V3 Volume 1B-2b Jobs/Interrupts/Routing | generated document | Jobs and task routing | Visible | Transcribed | yes | Important. | FACT |
| ARTIFACT-07 | V3 Volume 1B-3a Serialization/Persistence | generated document | Save/replay/chunks | Visible | Transcribed | yes | Important. | FACT |
| ARTIFACT-08 | V3 Volume 1B-3b Spatial/Physics/Prefabs/Mods | generated document | Spatial/prefab/mod architecture | Visible | Transcribed | yes | Important. | FACT |
| ARTIFACT-09 | Unified Engine Specification outline | framework/plan | 12-section UES plan | Visible | Assistant output | yes | Not full formal spec but useful. | FACT |
| ARTIFACT-10 | Massive unified summary | generated summary | Whole-engine macro summary | Visible | Assistant output | yes | Architecture bridge. | FACT |
| ARTIFACT-11 | Updated world rundown | generated summary | Cosmic/spatial/server/worldgen model | Visible | Assistant output | yes | Use for world model. | FACT |
| ARTIFACT-12 | Surface vs space design answer | generated design | Physical/logical domains and orbits | Visible | Assistant output | yes | Use for future space. | FACT |
| ARTIFACT-13 | Orbital construction answer | generated design | Stations/ships/rockets/pods/tugs | Visible | Assistant output | yes | Future space logistics. | FACT |
| ARTIFACT-14 | Building/cut-fill/spline design answers | generated design | Blocks, fixtures, terrain, corridors | Visible | Assistant output | yes | Core architecture. | FACT |
| ARTIFACT-15 | Five primitives generalization | framework | Unifying systems | Visible | Assistant output | yes | High-value architecture. | FACT |
| ARTIFACT-16 | Full ASCII git directory tree | directory plan | Ideal repo structure | Visible | Assistant output | historical | Superseded by user actual tree. | FACT |
| ARTIFACT-17 | Per-directory dev spec messages | generated specs | Detailed file/API guidance | Visible | Assistant outputs | yes | Likely reflected in docs/dev files. | FACT |
| ARTIFACT-18 | Root docs drafts | generated documents | README, LICENCE, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, .gitignore, CMake, CHANGELOG, BUILDING, VERSION | Visible | Assistant outputs | some | Some may not exist in actual tree. | FACT / UNCERTAIN |
| ARTIFACT-19 | User-provided current directory tree | file tree | Actual current file set for Codex | Visible | User | yes | Highest-priority structure source. | FACT |
| ARTIFACT-20 | BUILDING.md V4 | generated document | Updated build/platform spec | Visible | Assistant after old doc pasted | yes | Apply/verify. | FACT |
| ARTIFACT-21 | SPEC_CORE.md V4 | generated document | Updated core spec | Visible | Assistant after old doc pasted | yes | Apply/verify. | FACT |
| ARTIFACT-22 | DATA_FORMATS.md V4 | generated document | Updated data formats spec | Visible | Assistant after old doc pasted | yes | Apply/verify. | FACT |
| ARTIFACT-23 | DIRECTORY_CONTEXT.md V4 | generated document | Updated directory contract | Visible | Assistant after old doc pasted | yes | Apply/verify. | FACT |
| ARTIFACT-24 | Codex consistency pass prompt | prompt | Ask Codex to reconcile four docs | Visible | Assistant | yes | Immediate use. | FACT |
| ARTIFACT-25 | Codex CMake/build skeleton prompt | prompt | Build system implementation step | Visible | Assistant | yes | Next implementation. | FACT |
| ARTIFACT-26 | Codex core API skeleton prompt | prompt | engine/core skeleton step | Visible | Assistant | yes | Implementation. | FACT |
| ARTIFACT-27 | Codex sim/ECS shell prompt | prompt | Tick/ECS/events/jobs skeleton | Visible | Assistant | yes | Implementation. | FACT |
| ARTIFACT-28 | Codex platform/render shell prompt | prompt | Win32/DX9 vector shell | Visible | Assistant | yes | Implementation. | FACT |
| ARTIFACT-29 | Codex minimal client loop prompt | prompt | MVP loop step | Visible | Assistant | yes | Implementation. | FACT |
| ARTIFACT-30 | Lua clarification answer | implementation decision | /engine/script, Lua 5.4.4, API, FNV hash | Visible | Assistant to Codex question | yes | Essential. | FACT |
| ARTIFACT-31 | OC-1 Discovery Inventory | handoff artifact | Discovery pass inventory | Visible | Assistant | yes | Basis for packet. | FACT |
| ARTIFACT-32 | Partial OC-2 registers | handoff artifact | Structured registers started but superseded | Partial | Assistant | historical | This packet supersedes. | FACT |
| ARTIFACT-33 | Current Context Transfer Packet | handoff report | Maximum-fidelity chat state transfer | Current output | Assistant | yes | Use for next chat. | FACT |

## 8. Rejected / Superseded Options Register

| ID | Option | Status | Reason rejected/superseded/deprioritised | Is rejection final? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Pure vector shapes as simulation truth. | rejected | Too complex for deterministic collision/serialization/retro. | final | Use vectors as skins/editor/generators. | WORKSTREAM-07 | FACT |
| REJECTED-02 | Pure blocks without vector authoring. | rejected as sole system | Insufficient for arbitrary curves/splines. | final-ish | Blocks remain sim truth; vectors authoring. | WORKSTREAM-08 | FACT |
| REJECTED-03 | Full n-body orbital mechanics. | rejected | Complex and hostile to determinism/debuggability. | final-ish | Optional future high-fidelity non-core only. | WORKSTREAM-12 | FACT |
| REJECTED-04 | Synchronous cross-surface simulation. | rejected | Would break surface/shard isolation. | final-ish | Async messaging/trade only. | WORKSTREAM-09 | FACT |
| REJECTED-05 | Hard one-surface-per-planet limit. | superseded | Sharding/mirroring requires multiple surface instances. | final-ish | One canonical surface remains. | WORKSTREAM-09 | FACT |
| REJECTED-06 | Arbitrary mid-edge topology without nodes. | rejected | Graph/path/signal ambiguity. | final-ish | Auto-split/create node. | WORKSTREAM-08 | FACT |
| REJECTED-07 | Coding doors into every tunnel type. | rejected | User explicitly did not want it. | final | Use fixtures/anchors. | WORKSTREAM-07 | FACT |
| REJECTED-08 | Auto-spawned doors/utilities. | rejected | User wants only explicit placement. | final | Pattern/blueprint only if invoked. | WORKSTREAM-07 | FACT |
| REJECTED-09 | Runtime arbitrary spline math in sim. | rejected | Runtime determinism/performance. | final | Bake to chainpoints. | WORKSTREAM-08 | FACT |
| REJECTED-10 | Continuous mesh collisions. | rejected | Too heavy, float-prone, retro-unfriendly. | final-ish | AABB/cell/edge collision. | WORKSTREAM-11 | FACT |
| REJECTED-11 | Collapse/destruction in MVP. | deprioritised | User said rigid for now, future support. | tentative for MVP | Later structural graph. | WORKSTREAM-07 | FACT |
| REJECTED-12 | Textures/sounds/music in MVP. | deprioritised | User wants vector now, assets later. | final for MVP | Post-MVP. | WORKSTREAM-22 | FACT |
| REJECTED-13 | Multiplayer in MVP. | deprioritised | User lists next steps after MVP. | final for MVP | Post-MVP. | WORKSTREAM-21 | FACT |
| REJECTED-14 | Sol system/space in MVP. | deprioritised | User lists next steps. | final for MVP | Post-MVP. | WORKSTREAM-12 | FACT |
| REJECTED-15 | DX11/GL/VK/DX12 in MVP. | deprioritised | DX9 first. | final for MVP | Later renderer phases. | WORKSTREAM-22 | FACT |
| REJECTED-16 | Mac Classic/MS-DOS/Android in MVP. | deprioritised | User says later. | final for MVP | Later ports. | WORKSTREAM-22 | FACT |
| REJECTED-17 | CMake as primary retro build system. | rejected | Retro uses isolated build systems. | final-ish | CMake stubs only. | WORKSTREAM-22 | FACT |
| REJECTED-18 | Top-level /render and /platform dirs. | superseded | Directory contract puts them under /engine. | final-ish | Only if contract changes. | WORKSTREAM-14 | FACT |
| REJECTED-19 | Separate CODEGEN_ADDENDUM.md file. | rejected | User wants only listed files. | final | Use docs/dev/dominium_new_addendum.txt. | WORKSTREAM-01 | FACT |
| REJECTED-20 | Unbounded queues/dynamic sim allocation. | rejected | Determinism/resource control. | final | Preallocated bounded buffers. | WORKSTREAM-02 | FACT |

## 9. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Spec drift across docs/dev files. | Codex implements contradictory architecture. | high | high | Run consistency pass; keep V4 docs canonical. | WORKSTREAM-01 | FACT |
| RISK-02 | Codex invents directories or files outside contract. | Repo sprawl and bad implementation. | medium | high | Prompt scope and DIRECTORY_CONTEXT. | WORKSTREAM-01, WORKSTREAM-22 | FACT |
| RISK-03 | Treating brainstorming as final decisions. | Wrong architecture enters spec. | medium | high | Use labels and user-statement priority. | WORKSTREAM-01 | FACT |
| RISK-04 | Platform/render boundaries blur. | OS/GPU APIs leak into sim/game. | medium | critical | Addendum, BUILDING V4, lint checks. | WORKSTREAM-14 | FACT |
| RISK-05 | Floats enter authoritative simulation through Lua/render/helpers. | Cross-platform desync. | medium | critical | API conversion, no sim floats, tests. | WORKSTREAM-02, WORKSTREAM-15 | FACT |
| RISK-06 | Lua sandbox escape or nondeterministic script behavior. | Security/desync. | medium | critical | Disable OS/native/debug and deterministic RNG. | WORKSTREAM-15 | FACT |
| RISK-07 | Surface/space/cross-surface sync overreach. | Sharding/orbit complexity, desync. | medium | high | Defer space/multiplayer; async only. | WORKSTREAM-12, WORKSTREAM-21 | FACT |
| RISK-08 | DX9/Win2000 target not feasible as assumed. | MVP platform failure. | medium | high | Verify SDK/runtime early. | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| RISK-09 | SDL2 or Lua version incompatible with old targets. | Build/tooling failures. | medium | medium-high | Verify and patch/version-pin. | WORKSTREAM-14, WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| RISK-10 | Canonical hash/serializer includes unstable data or misses authoritative state. | False determinism results. | medium | high | Define serialization order and exclusions. | WORKSTREAM-16 | FACT |
| RISK-11 | MVP scope too broad. | Implementation stalls. | high | high | Minimal prototypes only; defer assets/multiplayer/space. | WORKSTREAM-18 | FACT |
| RISK-12 | Corridor/microgrid overlap ambiguity. | Invalid construction/pathing. | medium | medium-high | Ownership/portal rules. | WORKSTREAM-08 | FACT |
| RISK-13 | Network solver complexity creep. | MVP delay. | medium | medium | Simple power first, fluid/data thin. | WORKSTREAM-09 | INFERENCE |
| RISK-14 | Binary formats too underdefined for Codex. | Serializer guesses layouts. | medium | high | Finalize exact structs for MVP components. | WORKSTREAM-16 | FACT |
| RISK-15 | Sparse/full-size surface overdesign. | Memory/perf or slow implementation. | medium | medium | MVP flat sparse test area with full surface metadata. | WORKSTREAM-05 | INFERENCE |
| RISK-16 | .gitignore/build rules hide needed files. | Missing tracked build configs. | medium | medium | Audit git ignore. | WORKSTREAM-17 | INFERENCE |
| RISK-17 | Actual repo tree differs from generated specs. | Patches fail or create wrong files. | medium | medium | Inspect before applying. | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| RISK-18 | Restrictive licence legally weak. | Legal exposure. | unclear | high | Legal review. | WORKSTREAM-20 | UNCERTAIN / UNVERIFIED |
| RISK-19 | Future cross-server trade/security underspecified. | Cheating/rollback/desync. | medium | high | Future security/net spec. | WORKSTREAM-21 | INFERENCE |

## 10. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Actual repo file contents and whether V4 docs applied. | Generated docs may not be on disk. | Repo inspection/diff. | P0 | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Actual directory existence under /engine, /game, /data, etc. | User tree only showed root/docs. | Filesystem inspection. | P0 | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | DX9.0c support on Windows 2000 SP4 through Windows 11+. | External API/runtime/toolchain fact. | Microsoft/SDK/runtime docs and test build. | P1 | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | SDL2 support for Windows 2000 target. | Version-dependent. | SDL2 docs/build test. | P2 | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Lua 5.4.4 portability to required compilers. | May require shims. | Build/test with target compilers. | P1 | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | Restrictive LICENCE.md legal enforceability. | Legal validity depends on jurisdiction. | Legal review. | P1 | WORKSTREAM-20 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | CMake minimum/toolchains and flags. | External toolchain compatibility. | CMake/compiler docs and build tests. | P2 | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | JSON-vs-Lua data policy. | Docs and MVP may conflict. | User confirmation and doc update. | P0 | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Final DomDrawCmd/camera API. | Conflicting sketches. | Header design/user confirmation. | P0 | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | Current docs use LICENCE.md and SPEC_CORE.md names consistently. | Name mismatches likely. | Search repo. | P0 | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | .gitignore behaviour. | Could ignore /build/cmake. | git check-ignore tests. | P1 | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Third-party licence compliance for Lua/LZ4/etc. | Legal/build risk. | Licence audit. | P1 | WORKSTREAM-15, WORKSTREAM-20 | UNCERTAIN / UNVERIFIED |
| VERIFY-13 | OpenGL/Vulkan/future platform support matrices. | External-world/API facts stale. | Official API/platform docs. | P3 | WORKSTREAM-22 | UNCERTAIN / UNVERIFIED |
| VERIFY-14 | Win98 SE DX9/GL1 feasibility. | Historical platform support nuanced. | SDK/runtime tests. | P3 | WORKSTREAM-22 | UNCERTAIN / UNVERIFIED |
| VERIFY-15 | Exact contents of docs/dev/dominium_new_*.txt. | Listed but not inspected. | Read files. | P0 | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |

## 11. Timeline Register

| ID | Event / topic | What changed or was decided | Current relevance | Confidence |
| --- | --- | --- | --- | --- |
| TIMELINE-01 | Rail gauge/rail system discussion. | Gauge classes, weights, traction and multigauge groundwork. | Historical; feeds transport specs. | medium |
| TIMELINE-02 | Road, water, air, space transport broadening. | Project expanded beyond rail. | Historical/active architecture. | medium |
| TIMELINE-03 | Building/vector/voxel deterministic discussion. | Led toward grid/vector hybrid. | Active architecture. | high |
| TIMELINE-04 | V3 volumes transcribed. | Detailed determinism/ECS/persistence specs available. | Historical source. | high |
| TIMELINE-05 | Assistant reviewed existing docs/files. | Identified need for source-of-truth docs. | Active rationale. | high |
| TIMELINE-06 | UES outline and massive summary. | Created unified architecture frame. | Active context. | high |
| TIMELINE-07 | User fixed world unit and render contract. | Meter+fixed substeps and strict separation. | Current decision. | high |
| TIMELINE-08 | User fixed spatial ladder and defaults. | Subnano→surface, Earth/Sol/Milky Way. | Current decision. | high |
| TIMELINE-09 | Sharding/surface discussion. | Multiple surface instances, async cross-surface. | Current/future. | high |
| TIMELINE-10 | Surface/space and orbital mechanics discussion. | On-rails space and local bubbles. | Future architecture. | high |
| TIMELINE-11 | Orbital construction/logistics. | Ships/stations/rockets/drop pods/tugs. | Future architecture. | high |
| TIMELINE-12 | Building/cut-fill/splines generalized. | Blocks/faces/edges; terrain layers; corridor archetypes. | Current architecture. | high |
| TIMELINE-13 | Five primitives and full game summary. | Frames, archetypes, graphs, blueprints, ticks/jobs. | Current architecture. | high |
| TIMELINE-14 | Directory tree and dev specs generated. | Repo/implementation guide created. | Artifacts. | high |
| TIMELINE-15 | Root docs generated. | README, licence, contributing, security, etc. | Artifacts. | medium-high |
| TIMELINE-16 | User supplied actual current tree and Codex constraint. | Only listed files to be used. | Current. | high |
| TIMELINE-17 | BUILDING/SPEC_CORE/DATA_FORMATS/DIRECTORY_CONTEXT V4 generated. | Key docs updated. | Current, verify on disk. | high |
| TIMELINE-18 | Codex prompts generated. | Consistency pass and staged implementation prompts. | Next actions. | high |
| TIMELINE-19 | Lua/Codex clarification answered. | /engine/script, Lua 5.4.4, API, FNV hash. | Current implementation decisions. | high |
| TIMELINE-20 | OC-1 discovery and final context transfer. | Handoff preparation. | Current packet. | high |

## 12. Spec Book Contribution Register

### Likely sections

- Architecture Overview and Determinism Kernel
- Repository and Directory Contract
- Build and Platform Strategy
- Spatial Hierarchy and World Model
- Terrain, Earthworks and Microgrids
- Buildings, Fixtures and Construction
- Transport Corridors and Vector Alignments
- Utilities and Networks
- Renderer/Platform Abstraction
- Lua Data and Modding
- Serialization, Replay and Determinism Hashing
- MVP Roadmap and Implementation Plan

### Unique contributions

- Finalized meter+Q16.16 world unit decision.
- Finalized strict render/platform/sim separation for MVP.
- Detailed terrain/earthworks/microgrid model.
- Detailed block/face/edge/fixture building model.
- Vector corridor baking model for infrastructure.
- Explicit MVP definition and Codex implementation sequence.
- Lua binding decisions including /engine/script and Lua 5.4.4.
- FNV-1a full-state hash decision.

### Formal requirements candidates

- No floats in authoritative sim.
- Renderer pure observer.
- Codex uses listed files only.
- MVP vector-only and DX9-first.
- Lua sandbox restrictions.
- Canonical state hash requirements.

### Background candidates

- Earlier rail gauge exploration.
- Full future orbital/logistics ideas.
- Retro platform aspirations.

### Needs confirmation

- Lua vs JSON long-term data policy.
- Final DomDrawCmd/camera API.
- Native Win32 vs SDL2 first implementation path.
- Legal licence validity.
