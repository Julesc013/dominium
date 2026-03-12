Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`, `docs/worldgen/MILKY_WAY_CONSTITUTION.md`, `docs/worldgen/STAR_SYSTEM_SEED_MODEL.md`, `schema/worldgen/star_system_seed.schema`, `schema/worldgen/star_system_artifact.schema`, and `src/geo/worldgen/worldgen_engine.py`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Star System Seed Baseline

## Seed Model

- Canonical seed source: MW-0 Milky Way cell generation
- Canonical refinement threshold: `worldgen_request.refinement_level >= 1`
- Deterministic seed inputs:
  - `universe_seed`
  - `realism_profile_id`
  - `generator_version_id`
  - `geo_cell_key`
- Canonical `StarSystemSeed` fields:
  - `cell_key`
  - `local_index`
  - `system_seed_value`
  - deterministic fingerprint

Each cell-local seed row is a derived view, ordered canonically by `local_index`, and carries the stable object lineage for `kind.star_system`.

Canonical refinement-1 solar-band fixture (`geo_cell_key = [800, 0, 0]`) yields:

- `star_system_artifact_count = 7`
- `star_system_artifact_hash_chain = d52412cd0bd3289ab46e53cdfc46c4fd4356751c8e670ba55eb67bae80a31656`
- `worldgen_result_hash_chain = 9af181ed006731063702c1f23eee2a783c6238d44d947061f8837db71b98472a`

## Instantiation Flow

MW-1 upgrades MW-0 seed rows into first-class star-system artifacts without eager galaxy expansion.

Canonical flow:

1. `process.worldgen_request` targets one galaxy cell.
2. MW worldgen emits deterministic `star_system_seed_rows`.
3. At refinement `L1`, the same request materializes `generated_star_system_artifact_rows`.
4. `process.worldgen_request` persists the resulting `kind.star_system` artifact state idempotently.

Each instantiated artifact carries:

- stable `object_id`
- `system_seed_value`
- `metallicity_proxy`
- galaxy-frame `position_ref`
- bounded MW-1 metadata in `extensions`

Repeated refinement requests for the same cell do not duplicate artifacts; canonical ordering remains stable by `local_index`.

## Query And Teleport Integration

Discovery stays read-only and on-demand.

MW-1 provides:

- `list_systems_in_cell(cell_key)`
- `query_nearest_system(position_ref, radius)`
- `filter_habitable_candidates(criteria_stub)`

Query behavior remains deterministic because:

- galaxy-cell enumeration order is stable
- result ordering is stable
- nearest-distance evaluation uses GEO metric queries

Teleport integration remains lawful:

- teleport resolves by stable `target_object_id`
- if the system artifact is absent, runtime first issues deterministic `L1` worldgen for the containing cell
- camera teleport then resolves against the persisted procedural object entry

No catalog, wall-clock input, or eager galaxy index is required.

## Replay And Proof

MW-1 proof surfaces now include:

- star-system seed rows
- star-system artifact rows
- instantiated artifact IDs
- deterministic seed values

`tools/worldgen/tool_replay_system_instantiation.py` verifies that the same inputs reproduce the same artifact rows and hash chain.

## Validation Snapshot

- Frozen contract hash guard: PASS on 2026-03-09
- Identity fingerprint check: PASS on 2026-03-09
- Replay proof tool: PASS on 2026-03-09
  - `tools/worldgen/tool_replay_system_instantiation.py`
  - repeated runs remained byte-stable
- Targeted TestX MW subset: PASS on 2026-03-09
  - `test_mw_cell_generation_deterministic`
  - `test_system_count_bounded`
  - `test_system_ids_stable`
  - `test_cross_platform_mw_hash_match`
  - `test_star_system_seed_deterministic`
  - `test_instantiation_idempotent`
  - `test_query_nearest_deterministic`
  - `test_cross_platform_system_hash_match`
- Targeted RepoX MW-1 invariants: PASS on 2026-03-09
  - `INV-SYSTEM-INSTANTIATION-VIA-WORLDGEN`
  - `INV-NO-EAGER-SYSTEM-GENERATION`
- Targeted AuditX MW-1 analyzers: PASS on 2026-03-09
  - `E357_DIRECT_SYSTEM_SPAWN_SMELL`
  - `E358_NONDETERMINISTIC_QUERY_SMELL`
- AuditX full scan: completed on 2026-03-09
  - output root `build/mw1/auditx/`
  - `findings_count = 2266`
  - `promotion_candidates = 69`
  - blocked classifications `= 0`
- RepoX STRICT full-repo run: failed on 2026-03-09 due pre-existing repository-wide governance drift
  - output root `build/mw1/repox/`
  - MW task-local groups remained clean:
    - `repox.runtime.worldgen violation_count = 0`
    - `repox.runtime.bundle violation_count = 0`
  - dominant blocking classes remained `INV-DOC-STATUS-HEADER`, `INV-CANON-INDEX`, `INV-REPOX-STRUCTURE`, `INV-NO-RAW-PATHS`, and `INV-TOOL-VERSION-MISMATCH`
- Strict build lane: blocked on 2026-03-09
  - `cmake --build --preset msvc-verify`
  - environment lacks `Visual Studio 18 2026`

## Topology Map

- `docs/audit/TOPOLOGY_MAP.json` regenerated on 2026-03-09
- deterministic fingerprint `ba1168037c4c64160273b271ff02f1ac6a0a456c234468a783000c3abc70a68b`
- node count `4334`
- edge count `9140`

## MW-2 Readiness

MW-1 leaves the repository ready for MW-2 star and orbital priors in the narrow sense required by MVP:

- star-system identity is stable and overlay-safe
- discovery and teleport can target procedural systems without catalogs
- authoritative instantiation still occurs only through worldgen process execution
- replay and cross-platform hashing now cover the system-artifact layer
