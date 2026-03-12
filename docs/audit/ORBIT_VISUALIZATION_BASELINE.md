# SOL-2 Orbit Visualization Baseline

## Scope

SOL-2 adds a deterministic orbit-visualization lens and a minimal ephemeris proxy without storing orbit traces in truth state.

- Provider registry: `data/registries/ephemeris_provider_registry.json`
- Default provider: `ephemeris.kepler_proxy`
- Orbit path policy registry: `data/registries/orbit_path_policy_registry.json`
- Default policy: `orbitpath.mvp_default`
- Derived artifact: `orbit_view_artifact`

Orbit paths remain derived view artifacts. No orbit trace, sampled path buffer, or trajectory history is persisted in canonical truth.

## Sampling Policy

- Provider: `ephemeris.kepler_proxy`
- Samples per orbit: `128`
- Max paths per view: `16`
- Ordering:
  - bodies sorted deterministically by object id
  - sampled points sorted by `sample_index`
  - map markers reduced deterministically by canonical geo-cell hash

## UX Integration

- GEO-5 map and minimap can render `layer.orbits` through the orbit-view artifact layer source.
- Diegetic orbit overlays require telescope or orrery access; admin/omniscient debug remains explicit through the existing lens contract.
- Orbit charts switch to orbit-only layers when active so terrestrial layers do not leak into proxy system charts.
- Inspect panels expose:
  - focus object id
  - center object id
  - chart mode
  - provider id
  - orbital element proxies
  - current ephemeris-proxy position
  - period estimate

## Deterministic Baseline

Validated local baseline on March 13, 2026:

- Replay report fingerprint: `95633fa51cedc2b8b051f2230463f1387b92d122f32a936907f4dbe090d0a476`
- Combined orbit hash: `2eb03efe5872c134f50911c49221afc791663acd0b3c5cafb5ba910049cd594f`
- System artifact hash: `554bc7a84bf78bcd1ad2a4e4280656b0c8756ae569417a39057e9b3dab84c8bf`
- Earth-local artifact hash: `544db4c3c442fdddad181dcd4f55d590ead5b1bdc98f366a9fa5e759638ee379`
- Position hash: `c43509fc8bfd55d640deb8e34d08f625585601320d3cd037dff8c826d280048c`
- Sampling hash: `b494bde2a2342f6f82dd48d8199b692b0f38142255b5543c8bbd7cb439a0ffb8`

Reference positions at tick `123`:

- System chart:
  - `sol.star` -> `[0, 0, 0]`
  - `sol.planet.earth` -> `[1148, 602, 0]`
  - `sol.planet.jupiter` -> `[3653, -5561, -123]`
- Earth-local chart:
  - `sol.planet.earth` -> `[0, 0, 0]`
  - `sol.moon.luna` -> `[-26997, 28413, 2568]`

## Readiness

SOL-2 is ready for:

- SOL-3 higher-fidelity orbital inspection
- GAL-0 / GAL-1 stub expansion
- alternate ephemeris providers supplied through `provides.ephemeris.system.v1`
- later N-body or real-ephemeris providers without changing the orbit-view artifact contract

Deferred by design:

- N-body solvers
- real ephemeris datasets
- eclipse shadowing / occlusion beyond the SOL-1 stub interface
