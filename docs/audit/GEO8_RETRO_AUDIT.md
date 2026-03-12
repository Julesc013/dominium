Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# GEO8 Retro Audit

Status: Drafted for GEO-8 implementation.
Scope: existing worldgen stubs, RNG usage, spatial identity posture, and migration points for the GEO worldgen contract.

## Relevant Invariants

- `docs/canon/constitution_v1.md` `A1` Determinism is primary
- `docs/canon/constitution_v1.md` `A2` Process-only mutation
- `docs/canon/constitution_v1.md` `A4` No runtime mode flags
- `docs/canon/constitution_v1.md` `A6` Provenance is mandatory
- `docs/canon/constitution_v1.md` `A9` Pack-driven integration
- `docs/canon/constitution_v1.md` `E4` Named RNG streams
- `docs/canon/constitution_v1.md` `C3` CompatX obligations

## Current Worldgen Surfaces

### 1. Planning and constraint tooling exists, but not GEO cell generation

Observed code:

- `worldgen/core/constraint_solver.py`
- `worldgen/core/pipeline.py`
- `worldgen/core/module_resolver.py`
- `worldgen/core/constraint_commands.py`
- `tools/xstack/sessionx/creator.py`

Findings:

- Existing worldgen code is focused on deterministic planning, constraint solving, and pack/module ordering.
- `tools/xstack/sessionx/creator.py` invokes the planning pipeline during session bootstrap and persists `worldgen_search_plan.json`.
- There is no authoritative GEO runtime that generates canonical base-layer content by `geo_cell_key`.
- There is no `process.worldgen_request` handler yet.
- There is no canonical `worldgen_result` model in runtime state.

Implication:

- Existing worldgen is compatible with GEO-8 as an upstream planning/input surface, but it does not satisfy the required on-demand cell generation contract.

### 2. Real-data and pack content already exist as overlays/stubs

Observed data roots:

- `data/packs/org.dominium.worldgen.base.*`
- `data/packs/org.dominium.worldgen.real.*`
- `data/worldgen/real/*`

Findings:

- The repository already contains worldgen models, refinement plans, topology nodes, and measurement/provenance payloads for base and real-data packs.
- These assets are not yet bound to an authoritative GEO cell-key generation path.
- This matches the GEO-8 requirement to keep procedural base generation separate from later overlay layers.

Implication:

- GEO-8 should define the canonical procedural base layer and leave authored/real-data overlays for GEO-9.

## RNG Audit

### 3. Existing worldgen planning randomness is deterministic and named

Observed code:

- `worldgen/core/constraint_solver.py:62`

Finding:

- The existing search planner derives candidate seeds from a deterministic hash over the string `rng.worldgen.constraints.search|...`.
- No direct `random`, `secrets`, `uuid4`, or wall-clock use was found under `worldgen/`.

Implication:

- The repository already has precedent for hash-derived named RNG streams in worldgen-adjacent code.
- GEO-8 should formalize the authoritative runtime streams:
  - `rng.worldgen.galaxy`
  - `rng.worldgen.system`
  - `rng.worldgen.planet`
  - `rng.worldgen.surface`

### 4. No authoritative GEO worldgen RNG enforcement exists yet

Finding:

- There is no current RepoX/AuditX rule forbidding unnamed RNG specifically in GEO worldgen runtime code because that runtime code does not exist yet.

Migration note:

- GEO-8 must add enforcement for named RNG only within `src/geo/worldgen/` and related process/runtime hooks.

## Identity Audit

### 5. GEO stable object identity exists, but worldgen does not consume it yet

Observed code:

- `src/geo/index/object_id_engine.py`
- `src/geo/index/geo_index_engine.py`

Findings:

- GEO-1 already provides stable `geo_cell_key` derivation and stable `geo_object_id(...)`.
- There is no current worldgen runtime path that derives object identities from:
  - `UniverseIdentity`
  - GEO profiles
  - `geo_cell_key`
  - `object_kind_id`
  - deterministic local subkeys

Implication:

- GEO-8 can and should adopt GEO-1 identity derivation directly.

### 6. Existing runtime object IDs are domain-specific, not worldgen-cell-derived

Observed examples:

- mobility deterministic IDs
- signal deterministic IDs
- geometry/material batch IDs

Finding:

- Current deterministic IDs are lawful for their domains, but they do not establish a worldgen base-layer identity contract.

Migration note:

- Future procedurally generated galaxies, systems, planets, and surface tiles must be emitted through `geo_object_id(...)`.

## Universe Identity Audit

### 7. `UniverseIdentity` does not yet lock worldgen version/profile

Observed code and schema:

- `schemas/universe_identity.schema.json`
- `schema/universe/universe_identity.schema`
- `tools/xstack/sessionx/creator.py`

Findings:

- `UniverseIdentity` already locks:
  - `global_seed`
  - `physics_profile_id`
  - GEO profile ids
- It does not yet explicitly lock:
  - `generator_version_id`
  - `realism_profile_id`

Implication:

- GEO-8 must extend UniverseIdentity handling so worldgen version and realism are part of the immutable universe contract.
- This should be done compatibly because older identities/saves may exist without these fields.

## Process and Runtime Audit

### 8. Process runtime already has the right pattern for GEO-owned authoritative mutation

Observed code:

- `tools/xstack/sessionx/process_runtime.py`
- `src/geo/edit/geometry_state_engine.py`
- `src/geo/path/path_engine.py`

Findings:

- GEO-6 and GEO-7 already establish the expected implementation pattern:
  - deterministic engine module in `src/geo/...`
  - process handler in `process_runtime.py`
  - canonical result/event rows in runtime state
  - hash-chain refresh
  - proof propagation into server/shard proof surfaces

Implication:

- GEO-8 should follow this pattern rather than adding a parallel worldgen runtime outside the process layer.

## Viewer / ROI / Query Integration Audit

### 9. Viewer and ROI surfaces exist, but they do not trigger worldgen yet

Observed code:

- `src/geo/projection/projection_engine.py`
- `src/geo/lens/lens_engine.py`
- `src/system/roi/system_roi_scheduler.py`
- `tools/xstack/sessionx/process_runtime.py` for teleport and ROI processes

Findings:

- Projection/lens code enumerates cell keys deterministically for views.
- ROI scheduling already expresses deterministic interest decisions.
- Teleport/query-like flows exist in runtime, but none currently materialize missing GEO world cells through a worldgen request process.

Migration note:

- GEO-8 should provide deterministic request builders and minimal integration hooks so:
  - view extent can request cells
  - ROI interest can request nearby cells
  - teleport/query targets can request specific cells

## Migration Points

No migrations are performed in this audit phase. Required follow-up points:

1. Add a GEO worldgen runtime under `src/geo/worldgen/`.
2. Add `process.worldgen_request` to `tools/xstack/sessionx/process_runtime.py`.
3. Add canonical runtime state for:
   - `worldgen_requests`
   - `worldgen_results`
   - `worldgen_result` hash chains
4. Extend proof surfaces to carry:
   - generator version registry hash
   - realism profile registry hash
   - worldgen request/result hash chains
5. Extend `UniverseIdentity` creation and validation so generator version and realism profile are locked.
6. Route generated object IDs through `src/geo/index/object_id_engine.py`.
7. Seed field and geometry initial conditions through canonical GEO/field/geometry helpers rather than ad hoc writes.
8. Add RepoX and AuditX checks for:
   - cell-key-only worldgen
   - named RNG only
   - generator version lock

## Audit Conclusion

The repository already has deterministic planning-oriented worldgen surfaces and canonical GEO identity machinery, but it lacks the authoritative on-demand worldgen contract required by GEO-8. The implementation path is clear and does not require breaking the existing canon:

- keep planning/tooling code as upstream support
- add GEO-owned cell generation runtime
- lock generator version and realism through UniverseIdentity
- enforce named RNG and cell-key-only generation
