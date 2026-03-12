Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/worldgen/EARTH_SKY_STARFIELD_MODEL.md`, and EARTH-5 runtime/proof tooling.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Earth Illumination And Shadow Model

This document freezes the EARTH-5 illumination and shadow stub contract for Dominium v0.0.0.

## Relevant Invariants

- `docs/canon/constitution_v1.md` `A1` Determinism is primary
- `docs/canon/constitution_v1.md` `A2` Process-only mutation
- `docs/canon/constitution_v1.md` `A7` Observation is not truth
- `docs/canon/constitution_v1.md` `A9` Extensibility without restart
- `docs/canon/constitution_v1.md` `A10` Explicit degradation and refusal
- `docs/canon/constitution_v1.md` `E2` Deterministic ordering
- `docs/canon/constitution_v1.md` `E4` Bounded work
- `docs/canon/constitution_v1.md` `E6` Replay equivalence

## 1. Scope

EARTH-5 adds deterministic observer-side illumination and coarse terrain shadowing for Earth traversal.

It provides:

- derived per-view illumination parameters
- sun key light and moon fill light proxies
- sky-light and ambient contribution derived from EARTH-4 sky artifacts
- a bounded horizon-shadow approximation
- renderer-portable view artifacts for null, software, and future hardware backends

It does not provide:

- authoritative lighting truth
- PBR materials
- shadow maps
- volumetric lighting
- atmospheric scattering

## 2. Activation Surface

- EARTH-5 is a derived-view system.
- It consumes:
  - observer reference
  - EARTH-4 `sky_view_artifact`
  - derived Earth surface-tile context when available
- It produces:
  - `illumination_view_artifact`
- UI and renderers consume the derived artifact only.
- Mutation of TruthModel is forbidden.

## 3. Inputs

EARTH-5 uses:

- `sun_direction` and `sun_intensity_permille` from EARTH-4
- `moon_direction` and lunar illumination proxy from EARTH-4 and EARTH-3
- sky colors from EARTH-4
- observer surface tile elevation proxy when available
- observer latitude/longitude and tile-cell context when available

When Earth surface context is absent, EARTH-5 may degrade deterministically to:

- no local terrain occlusion
- sky-derived ambient plus directional values only

## 4. Lighting Model

The canonical illumination model is `illum.basic_diffuse_default`.

It derives:

- `ambient_color`
- `ambient_intensity`
- `sky_light_color`
- `key_light_direction`
- `key_light_color`
- `key_light_intensity`
- `fill_light_direction`
- `fill_light_color`
- `fill_light_intensity`

Rules:

- sun is the canonical key light
- moon is an optional night fill light
- ambient intensity rises in day and falls at night
- moon fill intensity is scaled by lunar illumination and suppressed by daylight
- all authoritative calculations are integer or fixed-point only

## 5. Shadow Model

The canonical shadow model is `shadow.horizon_stub_default`.

The MVP shadow is a local horizon approximation only.

For a given observer tile and sun azimuth:

1. if the sun is below the horizon:
   - `shadow_factor = 0`
2. else sample `K` bounded horizon points in the sun direction path
3. compute an approximate maximum horizon angle from sampled elevation proxies
4. if `horizon_angle > sun_elevation`:
   - sunlight is occluded

Rules:

- `K` is fixed by the shadow model row
- K is fixed by the shadow model row
- step distance is fixed by the shadow model row
- no unbounded search is allowed
- no shadow map allocation is allowed
- no recursion is allowed

## 6. Horizon Sampling Contract

EARTH-5 samples only a bounded local terrain profile.

Required rules:

- sample ordering is deterministic by sample index
- sample azimuth is derived from the sun-direction proxy only
- sample elevations are derived from macro terrain inputs only
- local terrain occlusion must not require global planet traversal
- replay with the same observer/tick/model inputs must reproduce the same sample set and shadow result

## 7. Output Artifact

The canonical derived payload is `illumination_view_artifact`.

It contains, at minimum:

- `view_id`
- `tick`
- `observer_ref`
- `illum_model_id`
- `shadow_model_id`
- `sun_dir`
- `sun_intensity`
- `moon_dir`
- `moon_intensity`
- `ambient_intensity`
- `shadow_factor`

Additional renderer-facing lighting colors, summary fields, sample traces, and cache metadata may appear in `extensions`.

The artifact is:

- derived-only
- compactable
- cacheable by deterministic observer/tick keys

## 8. Lens And Renderer Contract

EARTH-5 integrates through lens/view artifacts only.

Required layer surfaces:

- `layer.illumination`
- `layer.shadow_factor`

Renderer rules:

- renderers consume `illumination_view_artifact` only
- renderers may ignore the artifact lawfully if they are null/no-op backends
- renderers must not read terrain truth, process runtime, or hidden world state directly

## 9. Determinism Contract

- wall-clock time is forbidden
- anonymous RNG is forbidden
- horizon sampling count is fixed and bounded
- cache keys are deterministic
- all sample ordering is deterministic
- same observer/tick/model inputs must reproduce the same illumination fingerprint

## 10. Extensibility

EARTH-5 reserves future model slots:

- illumination models:
  - `illum.basic_diffuse`
  - `illum.pbr_future`
- shadow models:
  - `shadow.none`
  - `shadow.horizon_stub`
  - `shadow.maps_cascaded`

Future systems must layer on top of the EARTH-5 artifact contract without introducing truth reads in renderers or forcing identity changes.

## 11. Non-Goals

- no full PBR
- no cascaded shadow maps
- no terrain self-shadow mesh solve
- no atmospheric light transport
- no authoritative lighting mutation
