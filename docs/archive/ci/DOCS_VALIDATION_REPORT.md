Status: HISTORICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: docs/architecture/CANON_INDEX.md

This document is archived.
Reason: Superseded by docs/architecture/CANON_INDEX.md.
Do not use for implementation.

This document is archived.
Reason: Superseded by docs/architecture/CANON_INDEX.md.
Do not use for implementation.

This document is archived.
Reason: Superseded by unknown.
Do not use for implementation.

# ARCHIVED: Docs Validation Report (Normalization + Correctness Pass)





Archived: point-in-time validation report.


Reason: Historical validation snapshot; current status is tracked elsewhere.


Superseded by:


- `docs/policies/DOCUMENTATION_STANDARDS.md`


- `docs/ci/CI_ENFORCEMENT_MATRIX.md`


Still useful: background on prior documentation checks.





# Docs Validation Report (Normalization + Correctness Pass)





This report records the documentation reconciliation work performed to make the


spec set internally consistent, technically correct relative to the current


Domino/Dominium refactor scaffolding, and aligned with repository structure.





Note (CANON0): this report predates the docs/architecture and docs/specs split. Any


paths in this report that start with `docs/` but no longer exist are deprecated


and have moved under `docs/architecture/`, `docs/specs/`, or `docs/guides/`. See


`docs/guides/README.md` for current paths.





## Documents reviewed





Top-level:


- `README.md`


- `DOMINIUM.md`


- `CONTRIBUTING.md`


- `CHANGELOG.md`


- `SECURITY.md`





`docs/` policy + guides:


- `docs/guides/BUILDING.md`


- `docs/architecture/DIRECTORY_CONTEXT.md`


- `docs/LANGUAGE_POLICY.md`


- `docs/STYLE.md`


- `docs/policies/DETERMINISM_REGRESSION_RULES.md`


- `docs/CODE_OF_CONDUCT.md`


- `docs/architecture/OVERVIEW_ARCHITECTURE.md`


- `docs/LAUNCHER_SETUP_OVERVIEW.md`


- `docs/EDITOR_BACKENDS.md`


- `docs/specs/DATA_FORMATS.md`


- `docs/CONTENT_BASE_EXAMPLE.md`


- `docs/MILESTONES.md`


- `docs/SETUP_WINDOWS.md`


- `docs/SETUP_MACOS.md`


- `docs/SETUP_LINUX.md`


- `docs/SETUP_RETRO.md`





`docs/` specifications:


- `docs/specs/SPEC_DETERMINISM.md`


- `docs/specs/SPEC_SIM_SCHEDULER.md`


- `docs/specs/SPEC_ACTIONS.md`


- `docs/specs/SPEC_PACKETS.md`


- `docs/specs/SPEC_FIELDS_EVENTS.md`


- `docs/specs/SPEC_LOD.md`


- `docs/specs/SPEC_VM.md`


- `docs/specs/SPEC_GRAPH_TOOLKIT.md`


- `docs/specs/SPEC_POSE_AND_ANCHORS.md`


- `docs/specs/SPEC_TRANS_STRUCT_DECOR.md`


- `docs/specs/SPEC_TRANS.md`


- `docs/specs/SPEC_STRUCT.md`


- `docs/specs/SPEC_BUILD.md`


- `docs/specs/SPEC_DOMAINS_FRAMES_PROP.md`


- `docs/specs/SPEC_WORLD_COORDS.md`


- `docs/specs/SPEC_INPUT.md`


- `docs/specs/SPEC_SIM.md`


- `docs/specs/SPEC_DOMINO_SIM.md`


- `docs/specs/SPEC_DOMINO_SUBSYSTEMS.md`


- `docs/specs/SPEC_DOMINO_SYS.md`


- `docs/specs/SPEC_DOMINO_GFX.md`


- `docs/specs/SPEC_DOMINO_MOD.md`


- `docs/specs/SPEC_DOMINO_AUDIO_UI_INPUT.md`


- `docs/specs/SPEC_DOMINIUM_LAYER.md`


- `docs/specs/SPEC_DOMINIUM_RULES.md`


- `docs/specs/SPEC_VALIDATION.md`


- `docs/specs/SPEC_AGENT.md`


- `docs/specs/SPEC_JOBS.md`


- `docs/specs/SPEC_JOB_AI.md`


- `docs/specs/SPEC_RES.md`


- `docs/specs/SPEC_ENV.md`


- `docs/specs/SPEC_ZONES.md`


- `docs/specs/SPEC_VEHICLE.md`


- `docs/specs/SPEC_VEHICLES.md`


- `docs/specs/SPEC_NET.md`


- `docs/specs/SPEC_NETCODE.md`


- `docs/specs/SPEC_NETWORKS.md`


- `docs/specs/SPEC_PACKAGES.md`


- `docs/specs/SPEC_PRODUCTS.md`


- `docs/specs/SPEC_GAME_PRODUCT.md`


- `docs/specs/SPEC_GAME_CONTENT_API.md`


- `docs/specs/SPEC_INSTANCE_LAYOUT.md`


- `docs/specs/SPEC_SETUP_CORE.md`


- `docs/specs/SPEC_LAUNCHER.md`


- `docs/specs/SPEC_LAUNCHER_CORE.md`


- `docs/specs/SPEC_LAUNCHER_EXT.md`


- `docs/specs/SPEC_LAUNCHER_CLI.md`


- `docs/specs/SPEC_LAUNCHER_GUI.md`


- `docs/specs/SPEC_LAUNCHER_TUI.md`


- `docs/specs/SPEC_LAUNCHER_NET.md`


- `docs/specs/SPEC_LAUNCHER_PROTOCOL.md`


- `docs/specs/SPEC_VIEW_UI.md`


- `docs/specs/SPEC_DEBUG_UI.md`


- `docs/specs/SPEC_CORE.md`


- `docs/specs/SPEC_CONTENT.md`


- `docs/specs/SPEC_MODELS.md`


- `docs/specs/SPEC_NUMERIC.md`


- `docs/specs/SPEC_IDENTITY.md`


- `docs/specs/SPEC_FIELDS.md`


- `docs/specs/SPEC_KNOWLEDGE.md`


- `docs/specs/SPEC_KNOWLEDGE_VIS_COMMS.md`


- `docs/specs/SPEC_TRANSPORT_NETWORKS.md`


- `docs/specs/SPEC_HYDROLOGY.md`


- `docs/specs/SPEC_CLIMATE_WEATHER.md`


- `docs/specs/SPEC_ORBITS.md`


- `docs/specs/SPEC_SPACE_GRAPH.md`


- `docs/specs/SPEC_BIOMES.md`


- `docs/specs/SPEC_AGGREGATES.md`


- `docs/specs/SPEC_MATTER.md`


- `docs/specs/SPEC_MACHINES.md`


- `docs/specs/SPEC_ENERGY.md`


- `docs/specs/SPEC_ECONOMY.md`


- `docs/specs/SPEC_RECIPES.md`


- `docs/specs/SPEC_RESEARCH.md`


- `docs/specs/SPEC_REPLAY.md`


- `docs/specs/SPEC_BLUEPRINTS.md`


- `docs/specs/SPEC_ACTORS.md`


- `docs/specs/SPEC_EDITOR_GUI.md`


- `docs/specs/SPEC_TOOLS_CORE.md`





`docs/API/`:


- `docs/API/LAUNCHER_CLI.md`


- `docs/API/RUNTIME_CLI.md`


- `docs/API/SETUP_CLI.md`





`docs/FORMATS/`:


- `docs/FORMATS/FORMAT_INSTALL_MANIFEST.md`





`source/domino/**` module READMEs:


- `source/domino/world/README.md`


- `source/domino/world/domain/README.md`


- `source/domino/world/frame/README.md`


- `source/domino/sim/README.md`


- `source/domino/sim/act/README.md`


- `source/domino/sim/bus/README.md`


- `source/domino/sim/know/README.md`


- `source/domino/sim/lod/README.md`


- `source/domino/sim/pkt/README.md`


- `source/domino/sim/prop/README.md`


- `source/domino/sim/sched/README.md`


- `source/domino/sim/sense/README.md`


- `source/domino/sim/vis/README.md`


- `source/domino/trans/README.md`


- `source/domino/trans/compile/README.md`


- `source/domino/struct/README.md`


- `source/domino/struct/model/README.md`


- `source/domino/struct/compile/README.md`


- `source/domino/struct/phys/README.md`


- `source/domino/decor/README.md`


- `source/domino/decor/model/README.md`


- `source/domino/decor/compile/README.md`





## Conflicts found + resolutions applied





Directory/path drift:


- Conflict: references to deprecated `/engine` and `docs/spec` paths and stale


  layout assumptions across entry docs.


- Resolution: normalized all paths to the current repository layout and made


  `docs/architecture/DIRECTORY_CONTEXT.md` the authoritative layout contract.





Terminology ambiguity (authority vs caches):


- Conflict: “compiled artifacts” and other derived outputs were sometimes


  described as authoritative.


- Resolution: standardized terminology in `docs/specs/SPEC_DETERMINISM.md`:


  authoritative state vs derived cache vs compiled artifacts; updated affected


  specs/READMEs to match (compiled artifacts are rebuildable derived caches).





World hash vs build identifier:


- Conflict: mixing “world hash” (authoritative replay/lockstep check) with


  build-identity hashes/diagnostics.


- Resolution: explicitly separated “world hash” from “determinism build hash”


  in `docs/specs/SPEC_DETERMINISM.md`; updated docs that reference hashing to use the


  correct term.





“No grids” vs tile/chunk lattices in code:


- Conflict: some docs implied a ban on any grid usage, conflicting with


  subsystem-specific lattices (terrain tiles, climate grids, hydrology grids,


  tile-anchored transport nodes).


- Resolution: clarified that the prohibition is against treating a global grid


  as universal authoritative placement truth; explicit lattices are permitted


  when owned by a subsystem and documented as such.





TRANS meaning collision:


- Conflict: “TRANS” was used inconsistently (transport vs transform/topology),


  and `source/domino/trans/` contains both refactor `dg_trans_*` corridor


  scaffolding and legacy `d_trans_*` spline/mover plumbing.


- Resolution: canonicalized TRANS as “Transforms/Topology” for the refactor


  corridor pipeline (`docs/specs/SPEC_TRANS.md`); documented legacy transport networks


  separately (`docs/specs/SPEC_TRANSPORT_NETWORKS.md`) and explicitly called out the


  legacy `d_trans_*` coexistence in `source/domino/trans/README.md`.





Scheduler/orchestrator confusion (DSIM vs refactor scheduler):


- Conflict: documentation mixed DSIM’s legacy tick loop and the refactor SIM


  scheduler’s phase/delta-commit model.


- Resolution: `docs/specs/SPEC_SIM.md` scopes DSIM vs refactor scheduler; phase list,


  ordering keys, budgeting, and delta-commit semantics are authoritative in


  `docs/specs/SPEC_SIM_SCHEDULER.md` and referenced elsewhere.





Stub/prompt references and non-authoritative phrasing:


- Conflict: docs contained “Prompt X / future prompts / later prompts” phrasing


  and stub docs without explicit constraints.


- Resolution: removed prompt references and replaced with “later revision”


  phrasing; rewrote stub specs where needed into enforceable contracts (notably


  `docs/specs/SPEC_RES.md`, `docs/specs/SPEC_ENV.md`, `docs/specs/SPEC_JOBS.md`,


  `docs/specs/SPEC_JOB_AI.md`, `docs/specs/SPEC_VALIDATION.md`).





Agent layer boundaries missing:


- Conflict: repository contains both legacy AI (`source/domino/ai/d_agent_*`)


  and refactor agent data model (`source/domino/agent/dg_agent_*`) without a


  boundary spec.


- Resolution: added `docs/specs/SPEC_AGENT.md` defining refactor AGENT boundaries and


  explicitly scoping legacy AI/agent as compatibility-only.





Subsystem registry documentation mismatch:


- Conflict: subsystem registry and save/load framing were described without


  correct implementation pointers and without explicit determinism constraints.


- Resolution: rewrote `docs/specs/SPEC_DOMINO_SUBSYSTEMS.md` to match


  `source/domino/core/d_subsystem.h` and `source/domino/world/d_serialize.c`,


  including ordering rules and tag mapping constraints.





## Invariants now explicitly enforced (cross-document)


- **Determinism**: integer ticks, fixed-point only, canonical ordering keys, and


  explicit tie-break rules (`docs/specs/SPEC_DETERMINISM.md`,


  `docs/specs/SPEC_SIM_SCHEDULER.md`).


- **Authoritative mutation**: refactor SIM mutation occurs via deltas at commit;


  no ad-hoc writes outside the commit point (`docs/specs/SPEC_ACTIONS.md`,


  `docs/specs/SPEC_SIM_SCHEDULER.md`).


- **Serialization/hashing**: no hashing/serializing raw struct bytes; explicit


  encoding rules for deterministic IO (`docs/specs/SPEC_PACKETS.md`,


  `docs/specs/SPEC_DETERMINISM.md`).


- **Placement**: authoritative placement/editing uses anchors + quantized poses;


  UI snapping is non-authoritative (`docs/specs/SPEC_POSE_AND_ANCHORS.md`,


  `docs/specs/SPEC_BUILD.md`).


- **No baked geometry**: baked world-space mesh geometry is never authoritative;


  compiled artifacts are derived and rebuildable (`docs/specs/SPEC_TRANS_STRUCT_DECOR.md`,


  `docs/specs/SPEC_DETERMINISM.md`).


- **Budgeting**: bounded work units and carryover semantics; no skipping and no


  reordering when budgets exhaust (`docs/specs/SPEC_SIM_SCHEDULER.md`).





## Assumptions removed or clarified


- Clarified that “no grids” forbids a universal authoritative placement grid,


  not all subsystem-owned lattices (`docs/specs/SPEC_DETERMINISM.md`,


  `docs/specs/SPEC_WORLD_COORDS.md`).


- Clarified that “compiled artifacts” are derived caches and must be rebuildable


  (multiple specs + module READMEs).


- Clarified that the launcher/setup docs use “later revision” phrasing instead


  of referencing chat prompts (`docs/specs/SPEC_LAUNCHER_CORE.md`,


  `docs/specs/SPEC_LAUNCHER_EXT.md`, `docs/specs/SPEC_SETUP_CORE.md`).


- Clarified ENV “zones” (`denv_zone_state`) vs the legacy `dzone` atmosphere


  registry (`docs/specs/SPEC_ENV.md`, `docs/specs/SPEC_ZONES.md`).
