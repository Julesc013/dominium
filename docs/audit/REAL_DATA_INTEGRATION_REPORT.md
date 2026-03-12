Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# REAL_DATA_INTEGRATION_REPORT

Version: 1.0.0  
Date: 2026-02-15  
Scope: Prompt 18/20 deterministic real-data integration (SPICE + SRTM)  
Binding refs: `AGENTS.md`, `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/worldgen/REAL_DATA_IMPORT_PIPELINE.md`

## 1. Summary

Prompt 18 real-data integration is implemented and validated under `STRICT` without changing simulation semantics.  
SPICE source data feeds deterministic Sol ephemeris derived artifacts; SRTM source data feeds deterministic Earth tile-pyramid derived artifacts.  
Registry compile, lockfile enforcement, ROI tile selection, packaging, and cache behavior remain deterministic.

## 2. Source Pack Integration

| Source pack | Source descriptor | Import tool | Deterministic source hashes (SHA256) |
|---|---|---|---|
| `org.dominium.sol.spice` | `packs/source/org.dominium.sol.spice/data/ephemeris_source.json` | `tools/data/tool_spice_import` | `ephemeris_source.json=d93c7acc7bb60b125e31122f509235f570f4765c84070ce0ad886dabc3e59925`, `de440s.bsp=b3198844cad382d714aec3bdc72c1086915c3b8ac7bafd7fffc042307d128f28` |
| `org.dominium.earth.srtm` | `packs/source/org.dominium.earth.srtm/data/dem_source.json` | `tools/data/tool_srtm_import` | `dem_source.json=e7e3e65e21a5fca4866e89d0f77ef591c118af7de99087a66a04655eca90da20`, `N00E000.asc=67f69a7876e15e6cbc7a220a7800dfe70bc0831283dc6be8c641f7d0439a022a` |

## 3. Derived Artifacts and Registry Hashes

### 3.1 Derived pack payload hashes

- `packs/derived/org.dominium.sol.ephemeris/data/sol_ephemeris_table.json`: `a1a28b83412570963627dded4ba31aa95b2d58abeaf148eff7ce748967e6f656`
- `packs/derived/org.dominium.earth.tiles/data/earth_tile_pyramid.json`: `9c33102743a90dc9170d8978d1c2752aee7cf5c0ad9b41f7557dd9de50f0f93f`

### 3.2 STRICT run canonical hashes (`tools/xstack/out/strict/latest/report.json`)

- `pack_lock_hash`: `83e022ebf2ffc2686d0c2b8854b24b3febd5c80edbe06b3f4a0931575d8eb1b8`
- `ephemeris_registry_hash`: `694eddbd245046e5e0a16bc45555ed00f6bc9f3d13104136c60b5d259ad176e8`
- `terrain_tile_registry_hash`: `fe003e69d5339172ebf15bc16c18bdc5fcb7b19b21ebb6e4472cf738306ed529`
- `composite_hash_anchor`: `16d6f5b6333bb1cbb5a5e8670c95095ce795967afb1318829afa4c5060fc12b7`
- Packaging content hash (`packaging.verify`): `fa5957dea9014c8cba6f258b33e9af54f5780b50d13a7760e96b548e6d6aeb02`
- Packaging manifest hash (`packaging.verify`): `9a3952053d742764b2c5097f0d2db85b7dc1c1dd2d42c9b7b0dae8937b13b7ad`

## 4. Determinism Verification

`STRICT` execution (`tools/xstack/run strict`) passed with exit code `0` and `lab_build_status=pass`.

Determinism and integration coverage executed in TestX includes:

- `test_spice_import_determinism.py`
- `test_srtm_import_determinism.py`
- `test_tile_pyramid_consistency.py`
- `test_height_value_rounding_stability.py`
- `test_sol_ephemeris_consistency.py`
- `test_earth_tile_roi_selection_determinism.py`
- `test_observer_real_data_path_hash.py`
- `test_no_truth_leak_outside_observer_profile.py`
- `test_packaging_real_data_reproducibility.py`
- `test_cache_hit_real_data.py`
- `test_derived_hash_changes_on_source_change.py`
- `test_derived_refusal_source_missing.py`

Observed enforcement:

- Registry compile cache key remained deterministic (`cache_hit=true` during STRICT compile step).
- ROI terrain tile selection is deterministic and stable for repeated script replay.
- Packaging determinism remained stable with matching canonical manifest/content hashes.
- Derived artifact provenance checks and refusal paths remain enforced (`refusal.data_source_missing`, `refusal.data_schema_invalid`, `refusal.data_import_failed`, `refusal.provenance_missing`).

## 5. Performance Baseline (Informational)

From `tools/xstack/out/strict/latest/report.json`:

- `auditx.scan`: `215965 ms`
- `testx.run`: `311454 ms`
- `packaging.verify`: `3094 ms`
- `performx` deterministic proxy: `proxy_compute_units=36`, `proxy_entities=20`

These numbers are run-meta only and are excluded from canonical hash inputs.

## 6. Known Limitations

- Current SPICE and SRTM datasets are intentionally minimal subsets for deterministic pipeline validation, not full production coverage.
- Earth DEM coverage is limited to the provided source tile subset; broader coverage requires additional source packs and regenerated derived packs.
- Import outputs are currently canonical JSON artifacts; compact binary encodings are deferred.
- Source packs are not included in `dist` by default; derived packs are included via bundle selection.
- Real-data ingestion remains structural and deterministic; no new simulation primitive or semantic behavior was introduced.

## 7. Conclusion

Prompt 18 acceptance criteria are met for deterministic real-data ingestion and derived artifact integration:

- deterministic SPICE/SRTM import tooling,
- provenance-enforced derived artifacts,
- deterministic registry/lockfile/packaging integration,
- deterministic observer traversal path hashes,
- and passing FAST/STRICT verification gates.
