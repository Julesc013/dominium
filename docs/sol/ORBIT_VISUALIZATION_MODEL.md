# Orbit Visualization Model

Status: AUTHORITATIVE
Last Reviewed: 2026-03-13
Applies To: SOL-2, GEO-5 lenses, UX inspect surfaces, future ephemeris overlays.

## 1. Purpose

SOL-2 defines a deterministic, data-light orbit visualization lens for MVP.
It provides inspectable orbit positions and sampled orbit paths without storing traces in truth and without introducing N-body simulation.

## 2. Ephemeris Proxy

### 2.1 Provider model

- `ephemeris.kepler_proxy` is the MVP provider.
- Future replacement points are declared through `ephemeris_provider_registry.json`.
- Provider selection is pack-driven through `provides.ephemeris.system.v1`.

### 2.2 Position-at-tick

- `position_at_tick(body, tick)` is derived only.
- Inputs come from orbital element proxies already available in MW/SOL artifacts:
  - semi-major axis proxy
  - eccentricity proxy
  - inclination proxy
  - deterministic phase offset proxy
- The tick source is canonical `tick_t` from TIME-ANCHOR.
- No wall-clock time, native clock, or platform timer may participate.

### 2.3 Approximation discipline

- MVP uses a fixed-point Kepler proxy, not a real ephemeris dataset.
- Fixed-point trig helpers from SOL-1 are reused.
- Error is accepted only as bounded proxy error for visualization and inspectability.
- Official Sol overlay axis values are treated as deterministic proxy units for visualization and period estimation.

## 3. Orbit Path View

- Orbit paths are derived sampled paths over one proxy orbit period.
- `samples_per_orbit` is policy-driven and bounded.
- Sample order is stable and ascending by sample index.
- Output artifacts are compactable derived view artifacts only.

## 4. Replaceability

- `ephemeris_provider_registry.json` defines provider ids and kinds.
- MVP ships:
  - `ephemeris.kepler_proxy`
- Reserved future ids:
  - `ephemeris.nbody_future`
  - `ephemeris.real_pack_future`
- Selection must resolve through profile + pack provides and degrade explicitly if an unavailable provider is requested.

## 5. Map And Inspect Integration

- `layer.orbits` is a derived GEO-5 layer only.
- Diegetic visibility requires `instrument.telescope`, `instrument.orrery`, `ch.diegetic.telescope`, or `ch.diegetic.orrery`.
- Admin/nondiegetic inspection may always view derived orbit overlays.
- Inspect panels may expose:
  - orbital elements
  - current derived position
  - period estimate
  - provider id
  - chart mode

## 6. Truth Discipline

- Orbit traces, sampled path arrays, and current orbit positions must not be written into canonical truth state.
- Canonical truth may continue to store orbital priors and pinned overlay object properties only.
- SOL-2 artifacts are derived, evictable, and replayable.
