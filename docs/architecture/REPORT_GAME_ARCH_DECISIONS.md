# REPORT_GAME_ARCH_DECISIONS

## Executive summary (10 bullets max)
- Fixed-tick sim is implied; default 60 Hz appears in spec and game CLI defaults, and Domino sim derives dt_s = 1/ups.
- Tick advancement is integer-tick driven via d_sim_step/dom_sim_tick; wall-clock sleep uses tick_rate_hz outside the deterministic core.
- World model is mixed: tile/chunk lattice for grid-like domains plus fixed-point world positions (WPosExact Q16.16); mapping to tiles is derived.
- Visualization grids (world_surface, construction_interior) are explicitly non-authoritative; rendering remains placeholder grids.
- Rendering pipeline uses dgfx IR (CLEAR/VIEWPORT/CAMERA/RECT/TEXT) with soft backend as reference; many backends route through soft.
- Game selects gfx backend via detection and falls back to soft; camera points along -Y with Z up (top-down assumption).
- Save format compatibility is not defined in the game spec (SPEC_SAVE is TODO); surrounding systems use TLV containers with skip-unknown and explicit migration.
- Multiplayer/replay direction is command-stream lockstep: peers exchange commands, and replays store per-tick net packets re-injected before d_sim_step.
- Content pipeline is TLV-based packs/mods plus instance.tlv under DOMINIUM_HOME repo roots; base pack auto-loads first.
- CLI is split across entrypoints with overlapping flags; backend selection flags differ (--renderer vs --gfx).

## Evidence-backed answers
### Q1 Sim tick
Answer:
Fixed-timestep simulation is implied. Defaults target 60 Hz; sim state stores ups and dt_s = 1/ups, and game tick loops advance by integer ticks via d_sim_step/dom_sim_tick while sleeping based on tick_rate_hz.
Evidence:
- docs/SPEC_GAME_PRODUCT.md:10 tick_rate_hz default is 60 Hz when 0 is provided.
- docs/SPEC_DOMINO_SIM.md:58-61 dom_sim_tick uses ups (default 60) and dt_s = 1/ups, looping dom_game_sim_step per tick.
- source/domino/core/sim.c:76 dt_s computed as 1.0 / ups; dom_sim_tick loops ticks and accumulates sim_time_s.
- source/dominium/game/dom_game_cli.cpp:328 default cfg.tick_rate_hz = 60u; --tickrate parses explicit rate.
- source/dominium/game/dom_game_app.cpp:957 sleep_ms = 1000 / tick_rate_hz; 1017 d_sim_step(..., 1u); 1149 tick_dt = 1.0f / tick_rate_hz.
- include/domino/sim.h:81 dm_sim_tick takes dt_usec (legacy stub timing path).
Notes/uncertainty:
- No explicit 16 ms or 33 ms hardcoded sim tick outside the smoke GUI loop; the only fixed 16 ms sleep is in the smoke test path.
- Legacy dm_sim_tick takes dt_usec but is a stub in current code.

### Q2 World model
Answer:
Mixed model. Authoritative positions are fixed-point world coordinates (WPosExact) with sub-tile Q16.16 offsets; tile/chunk lattice is used for grid-like domains (terrain/fields/hydrology/climate) and deterministic chunk mapping. Grid visuals exist but are explicitly non-authoritative.
Evidence:
- docs/SPEC_WORLD_COORDS.md:3-5 tile and chunk ranges; chunk size 16; 25-28 WPosTile/WPosExact and ChunkPos/LocalPos definitions.
- docs/SPEC_WORLD_COORDS.md:8-9 tile/chunk lattice is for grid-like domains and deterministic chunk mapping; 14-15 mapping from pose to tiles/chunks is derived.
- include/domino/dworld.h:28 DOM_CHUNK_SIZE 16; 59-67 WPosTile/WPosExact definitions; 95 ENV_SURFACE_GRID indicates grid layer.
- docs/SPEC_DOMINIUM_RULES.md:26 constructions spawn onto surfaces using world coordinates (WPosExact).
- docs/SPEC_DOMINO_SIM.md:92-95 world_surface and construction_interior grids are visualization-only and not authoritative.
Notes/uncertainty:
- Grid-like domains are defined, but authoritative systems for those domains are still being stubbed; the mix of grid and continuous coordinates is intentional.

### Q3 Rendering target
Answer:
Current rendering is dgfx IR-driven with a soft backend reference. The game uses backend detection and a pipeline abstraction, but world rendering is stubbed to top-down grids and simple UI primitives; camera defaults imply a top-down view (dir_y = -1, up_z = 1).
Evidence:
- docs/SPEC_VIEW_UI.md:4-5 dgfx IR command set and pipeline flow (d_view_render -> dui_render -> d_gfx_submit).
- docs/SPEC_VIEW_UI.md:10 d_view_render emits camera and stubs world rendering; dgfx IR only.
- docs/SPEC_DOMINO_GFX.md:8 backend list (SOFT/DX*/GL*/VK1/etc) and dgfx_init; 20 soft backend is reference; 169-170 world_surface draws a 10x10 top-down grid.
- source/dominium/game/game_app.cpp:505-509 selects backend and falls back to D_GFX_BACKEND_SOFT.
- source/dominium/game/dom_game_camera.cpp:90-98 camera dir_y = -1 and up_z = 1.
- source/dominium/game/core/client/dom_client_main.c:444-483 2D grid draw; 507-529 3D grid draw.
Notes/uncertainty:
- There is no tile renderer beyond grid placeholders; dom_sdl_stub and frontend placeholders indicate UI rendering is still skeletal.

### Q4 Save compatibility promise
Answer:
No explicit save compatibility contract is defined for the game yet; the game save spec is TODO. The surrounding ecosystem uses versioned TLV containers with skip-unknown and explicit migration, and policy is to avoid silently breaking old saves.
Evidence:
- source/dominium/game/SPEC_SAVE.md:6 TODO to define save container header, chunks, and versioning.
- docs/SPEC_DOMINIUM_LAYER.md:25-26 load/save uses TLV container, forward-compatible, unknown tags ignored.
- docs/SPEC_CONTAINER_TLV.md:7 ABI stability with unknown chunks tolerated; 11 migration-first; 146-151 explicit versioning and migrations.
- docs/DATA_FORMATS.md:16 version gates migrations; 75 readers skip unknown TLVs; 153 unversioned formats are not compatibility-safe.
- docs/SPEC_IDENTITY.md:66 policy to never silently break old saves/packs/mods.
- source/dominium/common/dom_instance.cpp:252 unknown tags skipped for forward compatibility.
Notes/uncertainty:
- A concrete save container/versioning policy for game saves is missing; any promise would be inferred from general TLV rules.

### Q5 Multiplayer direction
Answer:
Lockstep, command-stream multiplayer with replay support. Peers exchange commands, apply them at fixed ticks, and replays store per-tick command packets that are re-injected before d_sim_step for deterministic playback.
Evidence:
- docs/SPEC_NETCODE.md:5-6 command-driven multiplayer; 21 d_sim_step applies queued commands at tick start.
- docs/SPEC_REPLAY.md:17-19 replay captures D_NET_MSG_CMD packets and re-injects via d_net_receive_packet before d_sim_step.
- source/dominium/game/dom_game_app.cpp:990-1017 playback path injects packets via d_net_receive_packet before d_sim_step.
- source/dominium/game/dom_game_net.cpp:372-447 d_net_session_init uses D_NET_ROLE_SINGLE/HOST/CLIENT and attaches transport callbacks.
Notes/uncertainty:
- Network transport and snapshot plumbing exist but remain minimal; current flow is command-stream oriented and consistent with replay.

## Extended findings
### Q6 Module boundaries
- Domino is the deterministic C89 engine (sim/world/gfx/ui/content) with stable ABI via POD/TLV. Evidence: docs/OVERVIEW_ARCHITECTURE.md:3.
- Dominium is the product layer (game/launcher/setup/tools) built on Dominium common. Evidence: docs/OVERVIEW_ARCHITECTURE.md:4; DOMINIUM.md:3.
- Dominium/common provides shared paths, instance/pack handling, and compatibility plumbing. Evidence: source/dominium/common/dom_paths.cpp:75-78; source/dominium/common/dom_packset.cpp:117-126.
- Dominium/game hosts runtime, frontends, and content wiring. Evidence: source/dominium/game/README.md:5; source/dominium/game/dom_game_app.cpp:977 (tick_fixed loop in game app).

### Q7 Content pipeline
- Packs/mods are TLV bundles under DOMINIUM_HOME repo roots: packs at repo/packs/<id>/<version>/pack.tlv and mods at repo/mods/<id>/<version>/mod.tlv; base pack autoloads first. Evidence: docs/SPEC_CONTENT.md:6-8; source/dominium/common/dom_packset.cpp:117-126.
- Content roots are resolved from DOMINIUM_HOME: repo/products, repo/packs, repo/mods, instances. Evidence: source/dominium/common/dom_paths.cpp:75-78.
- Instance configuration uses TLV (instance.tlv) and stores pack/mod refs. Evidence: source/dominium/common/dom_instance.cpp:164-166, 277-281.
- Non-core data uses JSON where appropriate (input bindings). Evidence: source/dominium/game/core/client/input/default_bindings.json:1-2.

### Q8 Game CLI contract
- Game CLI (dom_game_cli.cpp) supports: --mode=gui|tui|headless, --server/--listen/--server=off|listen|dedicated, --connect=, --port=, --instance=, --platform=, --gfx=, --tickrate=, --home=, --demo, --devmode, --deterministic-test, --record-replay=, --play-replay=, --smoke-gui. Evidence: source/dominium/game/dom_game_cli.cpp:381-499.
- The thin CLI entrypoint exposes a smaller surface: --instance=, --mode=, --server=, --demo, --platform=, --renderer=, --introspect-json, --help. Evidence: source/dominium/game/cli/dominium_game_cli_main.c:39-93.
- The GUI/runtime entrypoint reserves launcher integration flags: --role, --display, --universe, --launcher-session-id, --launcher-instance-id, --launcher-integration, plus --version and --capabilities. Evidence: source/dominium/game/gui/main.cpp:24-65.
- Profile selection and backend overrides are available globally: --print-caps, --print-selection, --profile=compat|baseline|perf, --lockstep-strict=0|1, --gfx=, --sys.<subsystem>=<backend>. Evidence: source/dominium/common/dom_profile_cli.cpp:166-233.

### Q9 Determinism mechanisms
- Fixed-point math is the deterministic numeric core (Q16.16, Q48.16, etc). Evidence: include/domino/core/fixed.h:10, 37-47.
- Deterministic RNG (LCG) with explicit seeding is provided. Evidence: include/domino/core/rng.h:10, 36-42.
- Deterministic hashing helpers and per-domain/tick hash streams exist. Evidence: source/domino/core/dg_det_hash.h:14-33; source/domino/sim/hash/dg_hash_stream.h:35-38.
- Determinism spec mandates fixed-point only and defines lockstep/world hashing rules. Evidence: docs/specs/SPEC_DETERMINISM.md:4, 159-160, 233.
- Game seeds instance world_seed to a fixed constant (current default). Evidence: source/dominium/game/dom_game_app.cpp:177.

### Q10 Contradictions / blockers
- High: Game save format is undefined (TODO), blocking any concrete forward/backward compatibility promise. Evidence: source/dominium/game/SPEC_SAVE.md:6.
- Medium: Runtime/frontends are explicitly placeholders (GUI/TUI/headless/runtime skeletons), so rendering/UI behavior is largely stubbed. Evidence: source/dominium/game/runtime/dom_game_runtime_placeholder.c:1-2; source/dominium/game/frontends/gui/dom_game_frontend_gui_placeholder.cpp:1-2.
- Medium: CLI backend flag naming differs between entrypoints (--renderer vs --gfx), risking contract confusion. Evidence: source/dominium/game/cli/dominium_game_cli_main.c:41; source/dominium/game/dom_game_cli.cpp:435.
- Low: Backends currently route through the soft pipeline, so renderer selection is mostly soft today. Evidence: docs/SPEC_DOMINO_GFX.md:21.

## Recommendation
- Adopt 60 Hz fixed tick as the default (matches SPEC_GAME_PRODUCT, Domino sim defaults, and game CLI). 
- Treat the MVP world model as mixed: authoritative WPosExact fixed-point positions with derived tile/chunk addressing for grid-like domains.
- For saves, adopt DTLV containers with versioned chunks, skip-unknown, and explicit migration as the default compatibility policy until SPEC_SAVE is defined.
- For multiplayer/replay, continue with command-stream lockstep and replay by re-injecting recorded D_NET_MSG_CMD packets before d_sim_step.
