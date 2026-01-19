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
- Specs under `docs/specs/` are authoritative over README and code comments.
- If conflicts exist, specs win and README/comments MUST be updated.

## Canonical layout reference
See `docs/arch/ARCH_REPO_LAYOUT.md` and `docs/arch/ARCH_SPEC_OWNERSHIP.md` for
ownership rules and boundary enforcement.

## Spec ownership index
| Spec | Primary owner | Secondary consumers | Stability |
| --- | --- | --- | --- |
| `docs/specs/SPEC_ABI_TEMPLATES.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_ACTIONS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_ACTORS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_AGENT.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_AGGREGATES.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_AI_DECISION_TRACES.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_AI_DETERMINISM.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_ARTIFACT_STORE.md` | tools | tools | optional |
| `docs/specs/SPEC_ASSETS_INSTRUMENTS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_ATMOSPHERE.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_BACKEND_CONFORMANCE.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_BIOMES.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_BLUEPRINTS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_BUILD.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_CALENDARS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_CAPABILITIES.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_CAPABILITY_REGISTRY.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_CLIMATE_WEATHER.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_COMMAND_MODEL.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_COMMUNICATION.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_CONSTRUCTIONS_V0.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_CONTAINER_TLV.md` | engine | game, client, server, tools | extension |
| `docs/specs/SPEC_CONTENT.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_CONTRACTS.md` | tools | tools | optional |
| `docs/specs/SPEC_CORE.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_CORE_DATA.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_CORE_DATA_PIPELINE.md` | tools | tools | optional |
| `docs/specs/SPEC_CORE_DATA_VALIDATION.md` | tools | tools | optional |
| `docs/specs/SPEC_COSMO_CORE_DATA.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_COSMO_ECONOMY_EVENTS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_COSMO_LANE.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_DEBUG_UI.md` | tools | tools | optional |
| `docs/specs/SPEC_DETERMINISM.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_DETERMINISM_GRADES.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_DGFX_IR_VERSIONING.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_DOCTRINE_AUTONOMY.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_DOMAINS_FRAMES_PROP.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_DOMINIUM_LAYER.md` | game | client, server, tools | core |
| `docs/specs/SPEC_DOMINIUM_RULES.md` | game | client, server, tools | core |
| `docs/specs/SPEC_DOMINO_AUDIO_UI_INPUT.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_DOMINO_GFX.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_DOMINO_MOD.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_DOMINO_SIM.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_DOMINO_SUBSYSTEMS.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_DOMINO_SYS.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_DUI.md` | tools | tools | optional |
| `docs/specs/SPEC_ECONOMY.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_EDITOR_GUI.md` | tools | tools | optional |
| `docs/specs/SPEC_EFFECT_FIELDS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_ENERGY.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_ENV.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_EPISTEMIC_GATING.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_EPISTEMIC_INTERFACE.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_EVENT_DRIVEN_STEPPING.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_FACADES_BACKENDS.md` | engine | game, client, server, tools | extension |
| `docs/specs/SPEC_FACTIONS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_FEATURE_EPOCH.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_FIDELITY_DEGRADATION.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_FIDELITY_PROJECTION.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_FIELDS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_FIELDS_EVENTS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_FS_CONTRACT.md` | tools | tools | optional |
| `docs/specs/SPEC_GAME_CLI.md` | game | client, server, tools | core |
| `docs/specs/SPEC_GAME_CONTENT_API.md` | game | client, server, tools | core |
| `docs/specs/SPEC_GAME_PRODUCT.md` | game | client, server, tools | core |
| `docs/specs/SPEC_GRAPH_TOOLKIT.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_HYDROLOGY.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_IDENTITY.md` | game | client, server, tools | core |
| `docs/specs/SPEC_INDEX.md` | tools | tools | optional |
| `docs/specs/SPEC_INFORMATION_MODEL.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_INPUT.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_INSTANCE_LAYOUT.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_INTEREST_SETS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_JOBS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_JOB_AI.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_KNOWLEDGE.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_KNOWLEDGE_VIS_COMMS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_LANES_AND_BUBBLES.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_LANGUAGE_BASELINES.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_LEDGER.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_LOD.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_LOGICAL_TRAVEL.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_MACHINES.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_MARKETS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_MATTER.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_MECHANICS_PROFILES.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_MEDIA_FRAMEWORK.md` | engine | game, client, server, tools | extension |
| `docs/specs/SPEC_MIGRATIONS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_MODELS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_MONEY_STANDARDS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_NET.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_NETCODE.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_NETWORKS.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_NET_HANDSHAKE.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_NO_MODAL_LOADING.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_NUMERIC.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_ORBITS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_ORBITS_TIMEWARP.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_PACKAGES.md` | tools | tools | optional |
| `docs/specs/SPEC_PACKETS.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_PERF_BUDGETS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_PLAYER_CONTINUITY.md` | game | client, server, tools | core |
| `docs/specs/SPEC_PLAY_FLOW.md` | game | client, server, tools | core |
| `docs/specs/SPEC_POSE_AND_ANCHORS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_PRODUCTS.md` | tools | tools | optional |
| `docs/specs/SPEC_PROFILING.md` | engine | game, client, server, tools | extension |
| `docs/specs/SPEC_PROPERTY_RIGHTS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_PROVENANCE.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_QOS_ASSISTANCE.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_RECIPES.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_REENTRY_THERMAL.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_REFERENCE_FRAMES.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_REPLAY.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_RES.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_RESEARCH.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_SCHEDULING.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_SENSORS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_SESSIONS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_SETUP_CLI.md` | tools | setup | optional |
| `docs/specs/SPEC_SETUP_CORE.md` | tools | setup | optional |
| `docs/specs/SPEC_SIM.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_SIM_SCHEDULER.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_SMOKE_TESTS.md` | tools | tools | optional |
| `docs/specs/SPEC_SPACETIME.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_SPACE_GRAPH.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_STANDARDS_AND_RENDERERS.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_STANDARD_RESOLUTION.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_STREAMING_BUDGETS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_STRUCT.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_SURFACE_STREAMING.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_SURFACE_TOPOLOGY.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_SYSTEMS_BODIES.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_SYSTEM_LOGISTICS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_TIERS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_TIME_CORE.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_TIME_FRAMES.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_TIME_KNOWLEDGE.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_TIME_STANDARDS.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_TIME_WARP.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_TOOLS_AS_INSTANCES.md` | tools | tools | optional |
| `docs/specs/SPEC_TOOLS_CORE.md` | tools | tools | optional |
| `docs/specs/SPEC_TOOL_IO.md` | tools | tools | optional |
| `docs/specs/SPEC_TRANS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_TRANSPORT_NETWORKS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_TRANS_STRUCT_DECOR.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_UI_CAPABILITIES.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_UI_PROJECTIONS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_UI_WIDGETS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_UNIVERSE_BUNDLE.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_UNIVERSE_MODEL.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_VALIDATION.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_VEHICLE.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_VEHICLES.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_VIEW_UI.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_VM.md` | engine | game, client, server, tools | core |
| `docs/specs/SPEC_WEATHER_CLIMATE_HOOKS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_WORLD_COORDS.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_WORLD_SOURCE_STACK.md` | game | client, server, tools | extension |
| `docs/specs/SPEC_ZONES.md` | game | client, server, tools | extension |
| `schema/life/SPEC_LIFE_CONTINUITY.md` | schema | game, client, server, tools | core |
| `schema/life/SPEC_DEATH_AND_ESTATE.md` | schema | game, client, server, tools | core |
| `schema/life/SPEC_CONTROL_AUTHORITY.md` | schema | game, client, server, tools | core |
| `schema/life/SPEC_CONTINUATION_POLICIES.md` | schema | game, client, server, tools | core |
| `schema/life/SPEC_BIRTH_LINEAGE_OVERVIEW.md` | schema | game, client, server, tools | core |
| `schema/war/SPEC_CONFLICT_CANON.md` | schema | game, client, server, tools | core |
| `schema/war/SPEC_SECURITY_FORCES.md` | schema | game, client, server, tools | core |
| `schema/war/SPEC_ENGAGEMENTS.md` | schema | game, client, server, tools | core |
| `schema/war/SPEC_OCCUPATION_AND_RESISTANCE.md` | schema | game, client, server, tools | core |
| `schema/war/SPEC_INTERPLANETARY_WAR.md` | schema | game, client, server, tools | core |
| `schema/world/SPEC_UNIVERSE_MODEL.md` | schema | game, client, server, tools | core |
| `schema/world/SPEC_GALAXY_MODEL.md` | schema | game, client, server, tools | core |
| `schema/world/SPEC_SYSTEM_MODEL.md` | schema | game, client, server, tools | core |
| `schema/world/SPEC_CELESTIAL_BODY.md` | schema | game, client, server, tools | core |
| `schema/world/SPEC_ORBITAL_RAILS.md` | schema | game, client, server, tools | core |
| `schema/world/SPEC_SURFACE_AND_REGIONS.md` | schema | game, client, server, tools | core |
| `schema/world/SPEC_WORLD_DATA_IMPORT.md` | schema | game, client, server, tools | core |
| `schema/agents/SPEC_AGENT_CANON.md` | schema | game, client, server, tools | core |
| `schema/agents/SPEC_AGENT_CONTEXT.md` | schema | game, client, server, tools | core |
| `schema/agents/SPEC_AGENT_INTENT.md` | schema | game, client, server, tools | core |
| `schema/agents/SPEC_AGENT_GOALS.md` | schema | game, client, server, tools | core |
| `schema/agents/SPEC_AGENT_PLANNING.md` | schema | game, client, server, tools | core |
| `schema/agents/SPEC_AGENT_DOCTRINE.md` | schema | game, client, server, tools | core |
| `schema/agents/SPEC_AGENT_ROLES.md` | schema | game, client, server, tools | core |
| `schema/agents/SPEC_DELEGATION.md` | schema | game, client, server, tools | core |
| `schema/agents/SPEC_AGENT_AGGREGATION.md` | schema | game, client, server, tools | core |
| `schema/agents/SPEC_AGENT_REFINEMENT.md` | schema | game, client, server, tools | core |
| `schema/mods/SPEC_MOD_MANIFEST.md` | schema | game, client, server, tools | core |
| `schema/mods/SPEC_MOD_GRAPH.md` | schema | game, client, server, tools | core |
| `schema/mods/SPEC_MOD_COMPATIBILITY.md` | schema | game, client, server, tools | core |
| `schema/ecs/SPEC_COMPONENT_SCHEMA.md` | schema | engine, game, tools | core |
| `schema/ecs/SPEC_FIELD_IDS.md` | schema | engine, game, tools | core |
| `schema/ecs/SPEC_STORAGE_BACKENDS.md` | schema | engine, game, tools | core |
| `schema/ecs/SPEC_PACKING_AND_DELTAS.md` | schema | engine, game, tools | core |
| `docs/specs/launcher/SPEC_LAUNCHER.md` | tools | launcher | optional |
| `docs/specs/launcher/SPEC_LAUNCHER_CLI.md` | tools | launcher | optional |
| `docs/specs/launcher/SPEC_LAUNCHER_CORE.md` | tools | launcher | optional |
| `docs/specs/launcher/SPEC_LAUNCHER_EXT.md` | tools | launcher | optional |
| `docs/specs/launcher/SPEC_LAUNCHER_GUI.md` | tools | launcher | optional |
| `docs/specs/launcher/SPEC_LAUNCHER_NET.md` | tools | launcher | optional |
| `docs/specs/launcher/SPEC_LAUNCHER_PACKS.md` | tools | launcher | optional |
| `docs/specs/launcher/SPEC_LAUNCHER_PRELAUNCH_CONFIG.md` | tools | launcher | optional |
| `docs/specs/launcher/SPEC_LAUNCHER_PROFILES.md` | tools | launcher | optional |
| `docs/specs/launcher/SPEC_LAUNCHER_PROTOCOL.md` | tools | launcher | optional |
| `docs/specs/launcher/SPEC_LAUNCHER_TUI.md` | tools | launcher | optional |
| `docs/specs/launcher/SPEC_LAUNCH_HANDSHAKE_GAME.md` | tools | launcher | optional |
| `docs/guides/ui_editor/SPEC_ACTIONS_AND_EVENTS.md` | tools | tools | optional |
| `docs/guides/ui_editor/SPEC_CAPABILITIES.md` | tools | tools | optional |
| `docs/guides/ui_editor/SPEC_CODEGEN_ACTIONS.md` | tools | tools | optional |
| `docs/guides/ui_editor/SPEC_UI_DOC_TLV.md` | tools | tools | optional |
