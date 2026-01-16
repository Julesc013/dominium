# SPEC_INDEX — Canonical Specification Index

Status: draft
Version: 2

## Authority
- Specs under `docs/` are authoritative over README and code comments.
- If conflicts exist, specs win and README/comments MUST be updated.

## Ownership legend
- Engine (E): engine primitives/invariants under `engine/`
- Game (G): game rules/policy under `game/`
- Tool (T): authoring/inspection under `tools/`
- Notes: Launcher/Setup/Schema/Client/Server as applicable

## Canonical layout reference
See `docs/ARCH_REPO_LAYOUT.md` for directory mapping and boundary rules.

## Full spec ownership index
| Spec | E | G | T | Notes |
| --- | --- | --- | --- | --- |
| `docs/launcher/SPEC_LAUNCH_HANDSHAKE_GAME.md` | - | Y | - | Launcher + client/server contract |
| `docs/launcher/SPEC_LAUNCHER.md` | - | - | - | Launcher |
| `docs/launcher/SPEC_LAUNCHER_CLI.md` | - | - | - | Launcher |
| `docs/launcher/SPEC_LAUNCHER_CORE.md` | - | - | - | Launcher |
| `docs/launcher/SPEC_LAUNCHER_EXT.md` | - | - | - | Launcher |
| `docs/launcher/SPEC_LAUNCHER_GUI.md` | - | - | - | Launcher |
| `docs/launcher/SPEC_LAUNCHER_NET.md` | - | - | - | Launcher |
| `docs/launcher/SPEC_LAUNCHER_PACKS.md` | - | - | - | Launcher, Schema |
| `docs/launcher/SPEC_LAUNCHER_PRELAUNCH_CONFIG.md` | - | - | - | Launcher |
| `docs/launcher/SPEC_LAUNCHER_PROFILES.md` | - | - | - | Launcher |
| `docs/launcher/SPEC_LAUNCHER_PROTOCOL.md` | - | - | - | Launcher |
| `docs/launcher/SPEC_LAUNCHER_TUI.md` | - | - | - | Launcher |
| `docs/SPEC_ABI_TEMPLATES.md` | Y | Y | - | Public ABI templates |
| `docs/SPEC_ACTIONS.md` | Y | Y | - | Action primitives + semantics |
| `docs/SPEC_ACTORS.md` | Y | Y | - | Actor primitives + semantics |
| `docs/SPEC_AGENT.md` | Y | Y | - | Agent primitives + semantics |
| `docs/SPEC_AGGREGATES.md` | Y | Y | - | Aggregation primitives + policy |
| `docs/SPEC_AI_DECISION_TRACES.md` | - | Y | - | Game AI |
| `docs/SPEC_AI_DETERMINISM.md` | - | Y | - | Game AI |
| `docs/SPEC_ARTIFACT_STORE.md` | - | - | Y | Launcher/Setup |
| `docs/SPEC_ASSETS_INSTRUMENTS.md` | - | Y | - | Economy |
| `docs/SPEC_ATMOSPHERE.md` | - | Y | - | World rules |
| `docs/SPEC_BACKEND_CONFORMANCE.md` | Y | - | - | Render/system backends |
| `docs/SPEC_BIOMES.md` | - | Y | - | World content |
| `docs/SPEC_BLUEPRINTS.md` | - | Y | Y | Content authoring |
| `docs/SPEC_BUILD.md` | Y | Y | - | Build primitives + rules |
| `docs/SPEC_CALENDARS.md` | Y | Y | - | Time standards |
| `docs/SPEC_CAPABILITIES.md` | Y | - | Y | Hardware/system caps |
| `docs/SPEC_CAPABILITY_REGISTRY.md` | Y | - | Y | Caps registry |
| `docs/SPEC_CLIMATE_WEATHER.md` | - | Y | - | World rules |
| `docs/SPEC_COMMAND_MODEL.md` | Y | Y | - | Command primitives + semantics |
| `docs/SPEC_COMMUNICATION.md` | Y | Y | - | Comms primitives + semantics |
| `docs/SPEC_CONSTRUCTIONS_V0.md` | - | Y | - | Construction rules |
| `docs/SPEC_CONTAINER_TLV.md` | Y | - | Y | Schema/TLV |
| `docs/SPEC_CONTENT.md` | - | Y | Y | Content pipeline |
| `docs/SPEC_CONTRACTS.md` | - | - | - | libs/contracts, schema |
| `docs/SPEC_CORE.md` | Y | - | - | Engine core |
| `docs/SPEC_CORE_DATA.md` | - | Y | Y | Schema |
| `docs/SPEC_CORE_DATA_PIPELINE.md` | - | - | Y | Schema |
| `docs/SPEC_CORE_DATA_VALIDATION.md` | - | - | Y | Schema |
| `docs/SPEC_COSMO_CORE_DATA.md` | - | Y | Y | Schema |
| `docs/SPEC_COSMO_ECONOMY_EVENTS.md` | - | Y | - | Economy |
| `docs/SPEC_COSMO_LANE.md` | - | Y | - | World rules |
| `docs/SPEC_DEBUG_UI.md` | - | - | Y | Tools/Client debug |
| `docs/SPEC_DETERMINISM.md` | Y | Y | - | Determinism contract |
| `docs/SPEC_DETERMINISM_GRADES.md` | Y | Y | - | Determinism contract |
| `docs/SPEC_DGFX_IR_VERSIONING.md` | Y | - | - | Render |
| `docs/SPEC_DOCTRINE_AUTONOMY.md` | - | Y | - | Rules |
| `docs/SPEC_DOMAINS_FRAMES_PROP.md` | Y | Y | - | World frames |
| `docs/SPEC_DOMINIUM_LAYER.md` | - | Y | - | Game layering |
| `docs/SPEC_DOMINIUM_RULES.md` | - | Y | - | Game rules |
| `docs/SPEC_DOMINO_AUDIO_UI_INPUT.md` | Y | - | - | Engine audio/input |
| `docs/SPEC_DOMINO_GFX.md` | Y | - | - | Engine render |
| `docs/SPEC_DOMINO_MOD.md` | Y | Y | Y | Mod host + validation |
| `docs/SPEC_DOMINO_SIM.md` | Y | - | - | Engine sim |
| `docs/SPEC_DOMINO_SUBSYSTEMS.md` | Y | - | - | Engine subsystems |
| `docs/SPEC_DOMINO_SYS.md` | Y | - | - | Engine system layer |
| `docs/SPEC_DUI.md` | - | - | Y | Tool/UI shared |
| `docs/SPEC_ECONOMY.md` | - | Y | - | Economy rules |
| `docs/SPEC_EDITOR_GUI.md` | - | - | Y | Editor tools |
| `docs/SPEC_EFFECT_FIELDS.md` | Y | Y | - | Field primitives + rules |
| `docs/SPEC_ENERGY.md` | - | Y | - | World rules |
| `docs/SPEC_ENV.md` | - | Y | - | World rules |
| `docs/SPEC_EPISTEMIC_GATING.md` | - | Y | Y | UI semantics |
| `docs/SPEC_EPISTEMIC_INTERFACE.md` | - | Y | Y | UI semantics |
| `docs/SPEC_EVENT_DRIVEN_STEPPING.md` | Y | Y | - | Sim stepping |
| `docs/SPEC_FACADES_BACKENDS.md` | Y | - | - | Platform facades |
| `docs/SPEC_FACTIONS.md` | - | Y | - | World rules |
| `docs/SPEC_FEATURE_EPOCH.md` | - | Y | - | Content/rules |
| `docs/SPEC_FIDELITY_DEGRADATION.md` | Y | Y | - | Fidelity policy |
| `docs/SPEC_FIDELITY_PROJECTION.md` | Y | Y | - | Fidelity projection |
| `docs/SPEC_FIELDS.md` | Y | Y | - | Field primitives + rules |
| `docs/SPEC_FIELDS_EVENTS.md` | Y | Y | - | Field events |
| `docs/SPEC_FS_CONTRACT.md` | - | - | Y | Launcher/Setup |
| `docs/SPEC_GAME_CLI.md` | - | Y | - | Client/Server |
| `docs/SPEC_GAME_CONTENT_API.md` | - | Y | Y | Content API |
| `docs/SPEC_GAME_PRODUCT.md` | - | Y | - | Client/Server |
| `docs/SPEC_GRAPH_TOOLKIT.md` | Y | - | - | Engine toolkit |
| `docs/SPEC_HYDROLOGY.md` | - | Y | - | World rules |
| `docs/SPEC_IDENTITY.md` | - | Y | - | Identity rules |
| `docs/SPEC_INDEX.md` | - | - | - | Index |
| `docs/SPEC_INFORMATION_MODEL.md` | Y | Y | - | Info model |
| `docs/SPEC_INPUT.md` | Y | Y | - | Client input |
| `docs/SPEC_INSTANCE_LAYOUT.md` | - | Y | - | Game data |
| `docs/SPEC_INTEREST_SETS.md` | Y | Y | - | LOD/interest |
| `docs/SPEC_JOB_AI.md` | - | Y | - | Game AI |
| `docs/SPEC_JOBS.md` | Y | Y | - | Scheduling + rules |
| `docs/SPEC_KNOWLEDGE.md` | - | Y | - | Knowledge rules |
| `docs/SPEC_KNOWLEDGE_VIS_COMMS.md` | - | Y | - | Knowledge rules |
| `docs/SPEC_LANES_AND_BUBBLES.md` | - | Y | - | Travel rules |
| `docs/SPEC_LANGUAGE_BASELINES.md` | - | Y | - | UI/text |
| `docs/SPEC_LEDGER.md` | - | Y | - | Economy ledger |
| `docs/SPEC_LOD.md` | Y | Y | - | LOD primitives + policy |
| `docs/SPEC_LOGICAL_TRAVEL.md` | - | Y | - | Travel rules |
| `docs/SPEC_MACHINES.md` | - | Y | - | World rules |
| `docs/SPEC_MARKETS.md` | - | Y | - | Economy |
| `docs/SPEC_MATTER.md` | - | Y | - | World rules |
| `docs/SPEC_MECHANICS_PROFILES.md` | - | Y | Y | Profiles |
| `docs/SPEC_MEDIA_FRAMEWORK.md` | Y | - | Y | Client/tools |
| `docs/SPEC_MIGRATIONS.md` | - | Y | Y | Schema |
| `docs/SPEC_MODELS.md` | Y | Y | - | Model primitives + semantics |
| `docs/SPEC_MONEY_STANDARDS.md` | - | Y | - | Economy |
| `docs/SPEC_NET.md` | Y | - | - | Engine net |
| `docs/SPEC_NET_HANDSHAKE.md` | Y | Y | - | Client/Server |
| `docs/SPEC_NETCODE.md` | Y | - | - | Engine netcode |
| `docs/SPEC_NETWORKS.md` | Y | - | - | Engine net |
| `docs/SPEC_NO_MODAL_LOADING.md` | - | Y | - | Client UI |
| `docs/SPEC_NUMERIC.md` | Y | - | - | Engine numeric |
| `docs/SPEC_ORBITS.md` | - | Y | - | World rules |
| `docs/SPEC_ORBITS_TIMEWARP.md` | - | Y | - | World rules |
| `docs/SPEC_PACKAGES.md` | - | - | Y | Launcher/Setup, Schema |
| `docs/SPEC_PACKETS.md` | Y | - | - | Engine packets |
| `docs/SPEC_PERF_BUDGETS.md` | Y | Y | - | Perf policy |
| `docs/SPEC_PLAY_FLOW.md` | - | Y | - | Game flow |
| `docs/SPEC_PLAYER_CONTINUITY.md` | - | Y | - | Game rules |
| `docs/SPEC_POSE_AND_ANCHORS.md` | Y | Y | - | World primitives |
| `docs/SPEC_PRODUCTS.md` | - | - | - | Repo overview |
| `docs/SPEC_PROFILING.md` | Y | - | Y | Profiling |
| `docs/SPEC_PROPERTY_RIGHTS.md` | - | Y | - | Economy |
| `docs/SPEC_PROVENANCE.md` | Y | Y | - | Provenance law |
| `docs/SPEC_QOS_ASSISTANCE.md` | - | Y | - | Gameplay QoS |
| `docs/SPEC_RECIPES.md` | - | Y | - | Content |
| `docs/SPEC_REENTRY_THERMAL.md` | - | Y | - | World rules |
| `docs/SPEC_REFERENCE_FRAMES.md` | Y | Y | - | World frames |
| `docs/SPEC_REPLAY.md` | Y | Y | - | Replay |
| `docs/SPEC_RES.md` | Y | Y | - | Resource systems |
| `docs/SPEC_RESEARCH.md` | - | Y | - | Rules |
| `docs/SPEC_SCHEDULING.md` | Y | Y | - | Time/scheduling |
| `docs/SPEC_SENSORS.md` | Y | Y | - | Sensors |
| `docs/SPEC_SESSIONS.md` | - | Y | - | Client/Launcher |
| `docs/SPEC_SETUP_CLI.md` | - | - | - | Setup |
| `docs/SPEC_SETUP_CORE.md` | - | - | - | Setup |
| `docs/SPEC_SIM.md` | Y | Y | - | Simulation |
| `docs/SPEC_SIM_SCHEDULER.md` | Y | - | - | Engine scheduler |
| `docs/SPEC_SMOKE_TESTS.md` | - | - | Y | CI |
| `docs/SPEC_SPACE_GRAPH.md` | Y | Y | - | World graph |
| `docs/SPEC_SPACETIME.md` | Y | Y | - | Spacetime |
| `docs/SPEC_STANDARD_RESOLUTION.md` | Y | - | - | Standards |
| `docs/SPEC_STANDARDS_AND_RENDERERS.md` | Y | - | - | Standards/renderers |
| `docs/SPEC_STREAMING_BUDGETS.md` | Y | Y | - | Streaming |
| `docs/SPEC_STRUCT.md` | Y | Y | - | Structure primitives + rules |
| `docs/SPEC_SURFACE_STREAMING.md` | Y | Y | - | Surface streaming |
| `docs/SPEC_SURFACE_TOPOLOGY.md` | - | Y | - | World rules |
| `docs/SPEC_SYSTEM_LOGISTICS.md` | - | Y | - | World rules |
| `docs/SPEC_SYSTEMS_BODIES.md` | - | Y | - | World rules |
| `docs/SPEC_TIERS.md` | - | Y | - | Progression |
| `docs/SPEC_TIME_CORE.md` | Y | Y | - | Time core |
| `docs/SPEC_TIME_FRAMES.md` | Y | Y | - | Time frames |
| `docs/SPEC_TIME_KNOWLEDGE.md` | Y | Y | - | Time knowledge |
| `docs/SPEC_TIME_STANDARDS.md` | Y | Y | - | Time standards |
| `docs/SPEC_TIME_WARP.md` | Y | Y | - | Time warp |
| `docs/SPEC_TOOL_IO.md` | - | - | Y | Tools |
| `docs/SPEC_TOOLS_AS_INSTANCES.md` | - | - | Y | Tools |
| `docs/SPEC_TOOLS_CORE.md` | - | - | Y | Tools |
| `docs/SPEC_TRANS.md` | Y | Y | - | Transport primitives + rules |
| `docs/SPEC_TRANS_STRUCT_DECOR.md` | - | Y | - | World rules |
| `docs/SPEC_TRANSPORT_NETWORKS.md` | - | Y | - | World rules |
| `docs/SPEC_UI_CAPABILITIES.md` | - | Y | Y | UI semantics |
| `docs/SPEC_UI_PROJECTIONS.md` | - | Y | Y | UI semantics |
| `docs/SPEC_UI_WIDGETS.md` | - | Y | Y | UI semantics |
| `docs/SPEC_UNIVERSE_BUNDLE.md` | - | Y | - | Content bundle |
| `docs/SPEC_UNIVERSE_MODEL.md` | - | Y | - | World model |
| `docs/SPEC_VALIDATION.md` | - | Y | Y | Validation |
| `docs/SPEC_VEHICLE.md` | - | Y | - | World rules |
| `docs/SPEC_VEHICLES.md` | - | Y | - | World rules |
| `docs/SPEC_VIEW_UI.md` | - | Y | Y | UI semantics |
| `docs/SPEC_VM.md` | Y | - | - | Engine VM |
| `docs/SPEC_WEATHER_CLIMATE_HOOKS.md` | - | Y | - | World rules |
| `docs/SPEC_WORLD_COORDS.md` | Y | Y | - | World coords |
| `docs/SPEC_WORLD_SOURCE_STACK.md` | Y | Y | Y | WSS |
| `docs/SPEC_ZONES.md` | - | Y | - | World rules |
| `docs/ui_editor/SPEC_ACTIONS_AND_EVENTS.md` | - | - | Y | UI editor |
| `docs/ui_editor/SPEC_CAPABILITIES.md` | - | - | Y | UI editor |
| `docs/ui_editor/SPEC_CODEGEN_ACTIONS.md` | - | - | Y | UI editor |
| `docs/ui_editor/SPEC_UI_DOC_TLV.md` | - | - | Y | UI editor, Schema |
