--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. This document is documentation only.

GAME:
- None. This document is documentation only.

TOOLS:
- Maintains the canonical spec catalog and ownership metadata.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No runtime logic or system redesign in this index.
- Do not treat this document as a public API surface.

DEPENDENCIES:
- Documentation only; no runtime dependencies.
--------------------------------

# SPEC_INDEX — Canonical Specification Index

Status: draft
Version: 3

## Authority
- Specs under `docs/` are authoritative over README and code comments.
- If conflicts exist, specs win and README/comments MUST be updated.

## Canonical layout reference
See `docs/ARCH_REPO_LAYOUT.md` and `docs/ARCH_SPEC_OWNERSHIP.md` for
ownership rules and boundary enforcement.

## Spec ownership index
| Spec | Primary owner | Secondary consumers | Stability |
| --- | --- | --- | --- |
| `docs/SPEC_ABI_TEMPLATES.md` | game | client, server, tools | extension |
| `docs/SPEC_ACTIONS.md` | game | client, server, tools | extension |
| `docs/SPEC_ACTORS.md` | game | client, server, tools | extension |
| `docs/SPEC_AGENT.md` | game | client, server, tools | extension |
| `docs/SPEC_AGGREGATES.md` | game | client, server, tools | extension |
| `docs/SPEC_AI_DECISION_TRACES.md` | game | client, server, tools | extension |
| `docs/SPEC_AI_DETERMINISM.md` | game | client, server, tools | extension |
| `docs/SPEC_ARTIFACT_STORE.md` | tools | tools | optional |
| `docs/SPEC_ASSETS_INSTRUMENTS.md` | game | client, server, tools | extension |
| `docs/SPEC_ATMOSPHERE.md` | game | client, server, tools | extension |
| `docs/SPEC_BACKEND_CONFORMANCE.md` | engine | game, client, server, tools | core |
| `docs/SPEC_BIOMES.md` | game | client, server, tools | extension |
| `docs/SPEC_BLUEPRINTS.md` | game | client, server, tools | extension |
| `docs/SPEC_BUILD.md` | game | client, server, tools | extension |
| `docs/SPEC_CALENDARS.md` | game | client, server, tools | extension |
| `docs/SPEC_CAPABILITIES.md` | engine | game, client, server, tools | core |
| `docs/SPEC_CAPABILITY_REGISTRY.md` | engine | game, client, server, tools | core |
| `docs/SPEC_CLIMATE_WEATHER.md` | game | client, server, tools | extension |
| `docs/SPEC_COMMAND_MODEL.md` | game | client, server, tools | extension |
| `docs/SPEC_COMMUNICATION.md` | game | client, server, tools | extension |
| `docs/SPEC_CONSTRUCTIONS_V0.md` | game | client, server, tools | extension |
| `docs/SPEC_CONTAINER_TLV.md` | engine | game, client, server, tools | extension |
| `docs/SPEC_CONTENT.md` | game | client, server, tools | extension |
| `docs/SPEC_CONTRACTS.md` | tools | tools | optional |
| `docs/SPEC_CORE.md` | engine | game, client, server, tools | core |
| `docs/SPEC_CORE_DATA.md` | game | client, server, tools | extension |
| `docs/SPEC_CORE_DATA_PIPELINE.md` | tools | tools | optional |
| `docs/SPEC_CORE_DATA_VALIDATION.md` | tools | tools | optional |
| `docs/SPEC_COSMO_CORE_DATA.md` | game | client, server, tools | extension |
| `docs/SPEC_COSMO_ECONOMY_EVENTS.md` | game | client, server, tools | extension |
| `docs/SPEC_COSMO_LANE.md` | game | client, server, tools | extension |
| `docs/SPEC_DEBUG_UI.md` | tools | tools | optional |
| `docs/SPEC_DETERMINISM.md` | engine | game, client, server, tools | core |
| `docs/SPEC_DETERMINISM_GRADES.md` | engine | game, client, server, tools | core |
| `docs/SPEC_DGFX_IR_VERSIONING.md` | engine | game, client, server, tools | core |
| `docs/SPEC_DOCTRINE_AUTONOMY.md` | game | client, server, tools | extension |
| `docs/SPEC_DOMAINS_FRAMES_PROP.md` | game | client, server, tools | extension |
| `docs/SPEC_DOMINIUM_LAYER.md` | game | client, server, tools | core |
| `docs/SPEC_DOMINIUM_RULES.md` | game | client, server, tools | core |
| `docs/SPEC_DOMINO_AUDIO_UI_INPUT.md` | engine | game, client, server, tools | core |
| `docs/SPEC_DOMINO_GFX.md` | engine | game, client, server, tools | core |
| `docs/SPEC_DOMINO_MOD.md` | game | client, server, tools | extension |
| `docs/SPEC_DOMINO_SIM.md` | engine | game, client, server, tools | core |
| `docs/SPEC_DOMINO_SUBSYSTEMS.md` | engine | game, client, server, tools | core |
| `docs/SPEC_DOMINO_SYS.md` | engine | game, client, server, tools | core |
| `docs/SPEC_DUI.md` | tools | tools | optional |
| `docs/SPEC_ECONOMY.md` | game | client, server, tools | extension |
| `docs/SPEC_EDITOR_GUI.md` | tools | tools | optional |
| `docs/SPEC_EFFECT_FIELDS.md` | game | client, server, tools | extension |
| `docs/SPEC_ENERGY.md` | game | client, server, tools | extension |
| `docs/SPEC_ENV.md` | game | client, server, tools | extension |
| `docs/SPEC_EPISTEMIC_GATING.md` | game | client, server, tools | extension |
| `docs/SPEC_EPISTEMIC_INTERFACE.md` | game | client, server, tools | extension |
| `docs/SPEC_EVENT_DRIVEN_STEPPING.md` | engine | game, client, server, tools | core |
| `docs/SPEC_FACADES_BACKENDS.md` | engine | game, client, server, tools | extension |
| `docs/SPEC_FACTIONS.md` | game | client, server, tools | extension |
| `docs/SPEC_FEATURE_EPOCH.md` | game | client, server, tools | extension |
| `docs/SPEC_FIDELITY_DEGRADATION.md` | game | client, server, tools | extension |
| `docs/SPEC_FIDELITY_PROJECTION.md` | game | client, server, tools | extension |
| `docs/SPEC_FIELDS.md` | game | client, server, tools | extension |
| `docs/SPEC_FIELDS_EVENTS.md` | game | client, server, tools | extension |
| `docs/SPEC_FS_CONTRACT.md` | tools | tools | optional |
| `docs/SPEC_GAME_CLI.md` | game | client, server, tools | core |
| `docs/SPEC_GAME_CONTENT_API.md` | game | client, server, tools | core |
| `docs/SPEC_GAME_PRODUCT.md` | game | client, server, tools | core |
| `docs/SPEC_GRAPH_TOOLKIT.md` | engine | game, client, server, tools | core |
| `docs/SPEC_HYDROLOGY.md` | game | client, server, tools | extension |
| `docs/SPEC_IDENTITY.md` | game | client, server, tools | core |
| `docs/SPEC_INDEX.md` | tools | tools | optional |
| `docs/SPEC_INFORMATION_MODEL.md` | game | client, server, tools | extension |
| `docs/SPEC_INPUT.md` | game | client, server, tools | extension |
| `docs/SPEC_INSTANCE_LAYOUT.md` | game | client, server, tools | extension |
| `docs/SPEC_INTEREST_SETS.md` | game | client, server, tools | extension |
| `docs/SPEC_JOBS.md` | game | client, server, tools | extension |
| `docs/SPEC_JOB_AI.md` | game | client, server, tools | extension |
| `docs/SPEC_KNOWLEDGE.md` | game | client, server, tools | extension |
| `docs/SPEC_KNOWLEDGE_VIS_COMMS.md` | game | client, server, tools | extension |
| `docs/SPEC_LANES_AND_BUBBLES.md` | game | client, server, tools | extension |
| `docs/SPEC_LANGUAGE_BASELINES.md` | game | client, server, tools | extension |
| `docs/SPEC_LEDGER.md` | game | client, server, tools | extension |
| `docs/SPEC_LOD.md` | game | client, server, tools | extension |
| `docs/SPEC_LOGICAL_TRAVEL.md` | game | client, server, tools | extension |
| `docs/SPEC_MACHINES.md` | game | client, server, tools | extension |
| `docs/SPEC_MARKETS.md` | game | client, server, tools | extension |
| `docs/SPEC_MATTER.md` | game | client, server, tools | extension |
| `docs/SPEC_MECHANICS_PROFILES.md` | game | client, server, tools | extension |
| `docs/SPEC_MEDIA_FRAMEWORK.md` | engine | game, client, server, tools | extension |
| `docs/SPEC_MIGRATIONS.md` | game | client, server, tools | extension |
| `docs/SPEC_MODELS.md` | game | client, server, tools | extension |
| `docs/SPEC_MONEY_STANDARDS.md` | game | client, server, tools | extension |
| `docs/SPEC_NET.md` | engine | game, client, server, tools | core |
| `docs/SPEC_NETCODE.md` | engine | game, client, server, tools | core |
| `docs/SPEC_NETWORKS.md` | engine | game, client, server, tools | core |
| `docs/SPEC_NET_HANDSHAKE.md` | game | client, server, tools | extension |
| `docs/SPEC_NO_MODAL_LOADING.md` | game | client, server, tools | extension |
| `docs/SPEC_NUMERIC.md` | engine | game, client, server, tools | core |
| `docs/SPEC_ORBITS.md` | game | client, server, tools | extension |
| `docs/SPEC_ORBITS_TIMEWARP.md` | game | client, server, tools | extension |
| `docs/SPEC_PACKAGES.md` | tools | tools | optional |
| `docs/SPEC_PACKETS.md` | engine | game, client, server, tools | core |
| `docs/SPEC_PERF_BUDGETS.md` | game | client, server, tools | extension |
| `docs/SPEC_PLAYER_CONTINUITY.md` | game | client, server, tools | core |
| `docs/SPEC_PLAY_FLOW.md` | game | client, server, tools | core |
| `docs/SPEC_POSE_AND_ANCHORS.md` | game | client, server, tools | extension |
| `docs/SPEC_PRODUCTS.md` | tools | tools | optional |
| `docs/SPEC_PROFILING.md` | engine | game, client, server, tools | extension |
| `docs/SPEC_PROPERTY_RIGHTS.md` | game | client, server, tools | extension |
| `docs/SPEC_PROVENANCE.md` | game | client, server, tools | extension |
| `docs/SPEC_QOS_ASSISTANCE.md` | game | client, server, tools | extension |
| `docs/SPEC_RECIPES.md` | game | client, server, tools | extension |
| `docs/SPEC_REENTRY_THERMAL.md` | game | client, server, tools | extension |
| `docs/SPEC_REFERENCE_FRAMES.md` | game | client, server, tools | extension |
| `docs/SPEC_REPLAY.md` | game | client, server, tools | extension |
| `docs/SPEC_RES.md` | game | client, server, tools | extension |
| `docs/SPEC_RESEARCH.md` | game | client, server, tools | extension |
| `docs/SPEC_SCHEDULING.md` | engine | game, client, server, tools | core |
| `docs/SPEC_SENSORS.md` | game | client, server, tools | extension |
| `docs/SPEC_SESSIONS.md` | game | client, server, tools | extension |
| `docs/SPEC_SETUP_CLI.md` | tools | setup | optional |
| `docs/SPEC_SETUP_CORE.md` | tools | setup | optional |
| `docs/SPEC_SIM.md` | game | client, server, tools | extension |
| `docs/SPEC_SIM_SCHEDULER.md` | engine | game, client, server, tools | core |
| `docs/SPEC_SMOKE_TESTS.md` | tools | tools | optional |
| `docs/SPEC_SPACETIME.md` | engine | game, client, server, tools | core |
| `docs/SPEC_SPACE_GRAPH.md` | game | client, server, tools | extension |
| `docs/SPEC_STANDARDS_AND_RENDERERS.md` | engine | game, client, server, tools | core |
| `docs/SPEC_STANDARD_RESOLUTION.md` | engine | game, client, server, tools | core |
| `docs/SPEC_STREAMING_BUDGETS.md` | game | client, server, tools | extension |
| `docs/SPEC_STRUCT.md` | game | client, server, tools | extension |
| `docs/SPEC_SURFACE_STREAMING.md` | game | client, server, tools | extension |
| `docs/SPEC_SURFACE_TOPOLOGY.md` | game | client, server, tools | extension |
| `docs/SPEC_SYSTEMS_BODIES.md` | game | client, server, tools | extension |
| `docs/SPEC_SYSTEM_LOGISTICS.md` | game | client, server, tools | extension |
| `docs/SPEC_TIERS.md` | game | client, server, tools | extension |
| `docs/SPEC_TIME_CORE.md` | engine | game, client, server, tools | core |
| `docs/SPEC_TIME_FRAMES.md` | engine | game, client, server, tools | core |
| `docs/SPEC_TIME_KNOWLEDGE.md` | engine | game, client, server, tools | core |
| `docs/SPEC_TIME_STANDARDS.md` | engine | game, client, server, tools | core |
| `docs/SPEC_TIME_WARP.md` | engine | game, client, server, tools | core |
| `docs/SPEC_TOOLS_AS_INSTANCES.md` | tools | tools | optional |
| `docs/SPEC_TOOLS_CORE.md` | tools | tools | optional |
| `docs/SPEC_TOOL_IO.md` | tools | tools | optional |
| `docs/SPEC_TRANS.md` | game | client, server, tools | extension |
| `docs/SPEC_TRANSPORT_NETWORKS.md` | game | client, server, tools | extension |
| `docs/SPEC_TRANS_STRUCT_DECOR.md` | game | client, server, tools | extension |
| `docs/SPEC_UI_CAPABILITIES.md` | game | client, server, tools | extension |
| `docs/SPEC_UI_PROJECTIONS.md` | game | client, server, tools | extension |
| `docs/SPEC_UI_WIDGETS.md` | game | client, server, tools | extension |
| `docs/SPEC_UNIVERSE_BUNDLE.md` | game | client, server, tools | extension |
| `docs/SPEC_UNIVERSE_MODEL.md` | game | client, server, tools | extension |
| `docs/SPEC_VALIDATION.md` | game | client, server, tools | extension |
| `docs/SPEC_VEHICLE.md` | game | client, server, tools | extension |
| `docs/SPEC_VEHICLES.md` | game | client, server, tools | extension |
| `docs/SPEC_VIEW_UI.md` | game | client, server, tools | extension |
| `docs/SPEC_VM.md` | engine | game, client, server, tools | core |
| `docs/SPEC_WEATHER_CLIMATE_HOOKS.md` | game | client, server, tools | extension |
| `docs/SPEC_WORLD_COORDS.md` | game | client, server, tools | extension |
| `docs/SPEC_WORLD_SOURCE_STACK.md` | game | client, server, tools | extension |
| `docs/SPEC_ZONES.md` | game | client, server, tools | extension |
| `schema/life/SPEC_LIFE_CONTINUITY.md` | schema | game, client, server, tools | core |
| `schema/life/SPEC_DEATH_AND_ESTATE.md` | schema | game, client, server, tools | core |
| `schema/life/SPEC_CONTROL_AUTHORITY.md` | schema | game, client, server, tools | core |
| `schema/life/SPEC_CONTINUATION_POLICIES.md` | schema | game, client, server, tools | core |
| `schema/life/SPEC_BIRTH_LINEAGE_OVERVIEW.md` | schema | game, client, server, tools | core |
| `docs/launcher/SPEC_LAUNCHER.md` | tools | launcher | optional |
| `docs/launcher/SPEC_LAUNCHER_CLI.md` | tools | launcher | optional |
| `docs/launcher/SPEC_LAUNCHER_CORE.md` | tools | launcher | optional |
| `docs/launcher/SPEC_LAUNCHER_EXT.md` | tools | launcher | optional |
| `docs/launcher/SPEC_LAUNCHER_GUI.md` | tools | launcher | optional |
| `docs/launcher/SPEC_LAUNCHER_NET.md` | tools | launcher | optional |
| `docs/launcher/SPEC_LAUNCHER_PACKS.md` | tools | launcher | optional |
| `docs/launcher/SPEC_LAUNCHER_PRELAUNCH_CONFIG.md` | tools | launcher | optional |
| `docs/launcher/SPEC_LAUNCHER_PROFILES.md` | tools | launcher | optional |
| `docs/launcher/SPEC_LAUNCHER_PROTOCOL.md` | tools | launcher | optional |
| `docs/launcher/SPEC_LAUNCHER_TUI.md` | tools | launcher | optional |
| `docs/launcher/SPEC_LAUNCH_HANDSHAKE_GAME.md` | tools | launcher | optional |
| `docs/ui_editor/SPEC_ACTIONS_AND_EVENTS.md` | tools | tools | optional |
| `docs/ui_editor/SPEC_CAPABILITIES.md` | tools | tools | optional |
| `docs/ui_editor/SPEC_CODEGEN_ACTIONS.md` | tools | tools | optional |
| `docs/ui_editor/SPEC_UI_DOC_TLV.md` | tools | tools | optional |
