Status: CANONICAL
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` v1.0.0, `docs/canon/glossary_v1.md` v1.0.0, and `AGENTS.md`.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Galaxy Scale Readiness

## Scope
Readiness checklist for deterministic traversal from Milky Way macro scale to Earth surface micro scale in the Lab Galaxy build.

## Required Capabilities
1. Deterministic pack selection and lockfile enforcement.
2. Deterministic registry compile and cache reuse.
3. Truth/Perceived/Render separation with law-gated observation.
4. Process-only camera and time control mutations.
5. Deterministic ROI expansion/collapse with budget/fidelity policy control.
6. Deterministic SRZ phase scheduling and hash anchor tracking.

## Real Data Integration Readiness
1. Source packs are declared separately from derived packs.
2. SPICE ephemeris source ingestion generates deterministic derived ephemeris tables.
3. SRTM DEM source ingestion generates deterministic derived terrain tile pyramids.
4. Derived artifacts include provenance headers and canonical hashes.
5. Universe index consumes derived artifacts only.
6. Dist packaging includes derived packs selected by bundle and excludes source packs by default.

## Determinism Checks
1. Identical source + tool versions produce identical derived artifact hashes.
2. Repeated registry compile over same inputs yields identical registry hashes.
3. Repeated scripted traversal yields identical composite hash anchors.
4. Cache hit/miss state does not alter pass/fail outcomes.

## Known Limits (v1.0.0)
1. Initial SRTM coverage may be partial for test slices.
2. SPICE kernel subset is intentionally minimal for Sol baseline.
3. Expanded scientific fidelity remains future work; governance contracts are in place now.

## Cross-References
- `docs/worldgen/REAL_DATA_IMPORT_PIPELINE.md`
- `docs/architecture/registry_compile.md`
- `docs/architecture/camera_and_navigation.md`
- `docs/architecture/interest_regions.md`
- `docs/architecture/macro_capsules.md`
- `docs/architecture/deterministic_packaging.md`
