Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# SOL2 Retro Audit

Status: AUDIT
Last Reviewed: 2026-03-13
Scope: SOL-2 orbit visualization lens and ephemeris proxy integration.

## Findings

- `generated_planet_orbit_artifact_rows` already exist in GEO/MW refinement outputs and are exposed from `src/geo/worldgen/worldgen_engine.py`.
- Official Sol pin overlays materialize effective celestial object views with `hierarchy`, `orbit`, `physical`, and `surface` properties through `tools/xstack/testx/tests/sol0_testlib.py`.
- TIME-ANCHOR provides the canonical tick source; existing orbit/season proxies already consume integer ticks through `src/worldgen/mw/insolation_proxy.py`.
- No existing runtime stores orbit traces in truth. Current orbit-related runtime state is limited to orbital priors and derived illumination inputs.
- No existing `layer.orbits`, `orbit_view_artifact`, or ephemeris runtime was present in `src/client/ui`, `src/geo/lens`, or `src/astro` before SOL-2.
- `src/client/ui/viewer_shell.py` already carries derived artifact seams for sky, illumination, water, refinement, and inspection surfaces; this is the safest insertion point for a derived orbit surface.
- `src/client/ui/inspect_panels.py` already renders celestial inspection data from snapshots/effective-object rows and can be extended without reading truth directly.
- `src/geo/lens/lens_engine.py` already gates derived layers by diegetic instruments and admin entitlements; the orbit overlay can follow the same pattern.

## Risk Notes

- Official Sol effective object views use orbit axis values as pinned proxy units. SOL-2 must treat them as deterministic visualization inputs, not claim real ephemerides.
- Official Luna rows should prefer `hierarchy.parent_object_id` over `orbit.parent_object_id` when constructing the local moon orbit chart.
- Orbit paths must remain derived artifacts only. No orbit sample arrays may be persisted into canonical truth or canonical object properties.
