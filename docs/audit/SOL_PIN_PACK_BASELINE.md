Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`, `docs/packs/sol/PACK_SOL_PIN_MINIMAL.md`, `packs/official/pack.sol.pin_minimal/pack.json`, `packs/official/pack.sol.pin_minimal/data/overlay/sol_pin_patches.json`, `src/worldgen/mw/sol_anchor.py`, and `src/geo/overlay/overlay_merge_engine.py`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Sol Pin Pack Baseline

## What Is Pinned

`pack.sol.pin_minimal` is the tiny official overlay for the canonical Sol lineage.

Pinned lineage:

- `sol.system`
- `sol.star`
- `sol.planet.mercury`
- `sol.planet.venus`
- `sol.planet.earth`
- `sol.planet.mars`
- `sol.planet.jupiter`
- `sol.planet.saturn`
- `sol.planet.uranus`
- `sol.planet.neptune`
- `sol.moon.luna`

Pinned property classes remain limited to:

- `display_name`
- `tags`
- `hierarchy`
- `physical`
- `spin`
- `orbit`

Observed SOL-0 pack footprint on 2026-03-09:

- `property_patch_count = 62`
- governed artifact bytes `= 67339`
- canonical Sol overlay target hash `= 289e09fd5cd6b9c6c673fe6ccc1e9833865b5c8f8638468fe730b14f1b35e3d5`
- canonical overlay merge result hash chain `= 42ef24107def610758b7d7dfcb7e7327d6e474b42eafa88be86885cd0fe4c0a7`

## What Is Not Pinned

SOL-0 still excludes:

- DEM or terrain height data
- real Earth geography
- climates or climate outputs
- cities, roads, borders, or infrastructure
- authored surface tiles
- any broader star catalog

The pack remains a GEO-9 property overlay only. It does not replace procedural identity and it does not mutate base worldgen algorithms.

## Overlay Behavior

The active realism profile now declares one canonical Sol anchor cell:

- `geo_cell_key.index_tuple = [801, 0, 0]`
- `partition_profile_id = geo.partition.grid_zd`
- `topology_profile_id = geo.topology.r3_infinite`
- `chart_id = chart.global.r3`

At that anchor:

- the procedural base always yields the canonical Sol system at local index `0`
- existing overlap-set objects preserve their GEO-owned `object_id`
- missing outer bodies are lawful overlay-added objects using the same derived IDs

Observed overlap-set status for the canonical MVP universe identity:

- existing procedural overlap slots:
  - `sol.system`
  - `sol.star`
  - `sol.planet.mercury`
  - `sol.planet.venus`
  - `sol.planet.earth`
  - `sol.planet.mars`
  - `sol.planet.jupiter`
- overlay-added slots at SOL-0:
  - `sol.planet.saturn`
  - `sol.planet.uranus`
  - `sol.planet.neptune`
  - `sol.moon.luna`

Removing the official layer returns the overlap set to the procedural base view. Overlay-added bodies disappear cleanly unless another lawful layer or save patch keeps them present.

## Validation Snapshot

- Frozen contract hash guard: PASS on 2026-03-09
- Identity fingerprint check: PASS on 2026-03-09
- Sol overlay verification tool: PASS on 2026-03-09
  - `tools/geo/tool_verify_sol_pin_overlay.py`
  - no violations
- Targeted TestX SOL-0 subset: PASS on 2026-03-09
  - `test_sol_anchor_exists_when_requested`
  - `test_sol_pin_overrides_applied`
  - `test_ids_unchanged_by_overlay`
  - `test_pin_pack_size_under_threshold`
  - `test_cross_platform_sol_hash_match`
- Targeted RepoX SOL-0 invariants: PASS on 2026-03-09
  - `INV-SOL-PACK-MINIMAL-SIZE`
  - `INV-SOL-PACK-NO-TERRAIN-DATA`
  - `INV-NO-IDENTITY-OVERRIDE`
- Targeted AuditX SOL-0 analyzers: PASS on 2026-03-09
  - `E363_LARGE_DATA_IN_PIN_PACK_SMELL`
  - `E364_IDENTITY_OVERRIDE_SMELL`
- AuditX full scan: completed on 2026-03-09
  - output root `build/sol0/auditx/`
  - `findings_count = 2274`
  - `promotion_candidates = 70`
- RepoX STRICT full-repo run: failed on 2026-03-09 due pre-existing repository-wide governance drift
  - output root `build/sol0/repox/`
  - SOL task-local groups remained clean:
    - `repox.runtime.bundle violation_count = 0`
    - `repox.runtime.worldgen violation_count = 0`
  - dominant blocking classes remained `INV-DOC-STATUS-HEADER`, `INV-CANON-INDEX`, `INV-REPOX-STRUCTURE`, `INV-NO-RAW-PATHS`, and `INV-TOOL-VERSION-MISMATCH`
- Strict build lane: blocked on 2026-03-09
  - `cmake --build --preset msvc-verify`
  - environment lacks `Visual Studio 18 2026`

## Topology Map

- `docs/audit/TOPOLOGY_MAP.json` regenerated on 2026-03-09
- deterministic fingerprint `89db459cd176fbae5d47abb426b684f759e691e3b44ff3aa85c6d44f5545888a`
- tool report counts:
  - `node_count = 4371`
  - `edge_count = 9205`

## Readiness

SOL-0 leaves the repository ready for the next overlay layers in the narrow MVP sense required by scope:

- SOL-1 can refine Earth and Moon without changing the Sol identity lineage
- EARTH-0 can attach an Earth-specific surface generator through routing rather than hardcoded worldgen branches
- procedural MW generation remains canonical while official reality data stays small, deterministic, and removable
