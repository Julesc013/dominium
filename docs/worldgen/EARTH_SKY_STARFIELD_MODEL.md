Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Earth Sky And Starfield Model

## 1) Purpose

EARTH-4 adds a deterministic, data-light sky dome and starfield stub for Earth observation.

It exists to:

- make Earth traversal feel physically grounded in MVP
- expose sun, moon, twilight, and night-sky changes through lawful derived view artifacts
- remain replay-stable and renderer-portable without textures or catalogs

It does not:

- mutate authoritative truth
- require atmospheric PDEs
- require star catalogs
- require wall-clock time

## 2) Activation Surface

- EARTH-4 is a derived-view system.
- It consumes observer position, lawful lens state, canonical tick, and registry-backed priors.
- It produces `sky_view_artifact` rows only.
- UI and renderers consume sky-view artifacts only.
- Mutation of TruthModel is forbidden.

## 3) Inputs

EARTH-4 uses:

- observer `position_ref` plus local observer chart metadata
- canonical tick
- Earth orbit phase from EARTH-2
- Earth rotation and lunar phase from EARTH-3
- Milky Way priors through the active realism profile
- optional turbidity parameter from the active sky model row

When Earth surface context is available, the observer latitude/longitude comes from the routed Earth surface tile artifact.
When Earth surface context is absent, EARTH-4 may degrade deterministically to a neutral observer chart.

## 4) Outputs

The canonical derived payload is `sky_view_artifact`.

It contains:

- sky dome parameters:
  - `zenith_color`
  - `horizon_color`
  - `sun_color`
  - `sun_intensity`
  - `twilight_factor`
- sun direction proxy
- moon direction proxy
- bounded starfield point rows
- bounded Milky Way band rows

All fields are derived and compactable.

## 5) Sun And Moon Direction Proxies

### 5.1 Sun direction

Sun direction is derived from:

- latitude
- longitude
- axial tilt
- canonical orbit phase
- canonical rotation phase

EARTH-4 uses fixed-point only.
No floating trig is required or assumed.

### 5.2 Moon direction

Moon direction is derived from:

- latitude
- longitude
- canonical lunar phase
- canonical rotation phase
- a small deterministic inclination proxy

Moon illumination is a deterministic phase proxy only.
EARTH-4 does not simulate penumbra, shadow cones, or atmospheric scattering.

## 6) Sky Gradient Stub

The canonical sky model is `sky.gradient_stub_default`.

The stub uses sun elevation plus turbidity to select a deterministic piecewise gradient:

- if the sun is well above the horizon:
  - use the day gradient
- if the sun is near the horizon:
  - use twilight blending with warm horizon bias
- if the sun is below the horizon:
  - use the night gradient

The model exposes color and intensity values only.
It does not solve Rayleigh or Mie scattering.

## 7) Starfield And Milky Way Band

### 7.1 Starfield source

The MVP starfield is procedural only.
No catalog dependency is allowed.

Star positions and magnitudes are generated from the named stream:

- `rng.view.sky.starfield`

The stream seed is derived from:

- `universe_seed`
- `generator_version_id`
- `realism_profile_id`
- `observer_cell_key`
- `tick_bucket`

Same inputs must produce the same starfield.

### 7.2 Visibility rule

Stars are visible only when `sun_intensity` is below the configured threshold.

Under daylight:

- star count may lawfully degrade to zero
- the decision must be deterministic

### 7.3 Bound policy

- star count is capped by the active starfield policy
- Milky Way band samples are capped by the active band policy
- unbounded generation is forbidden

## 8) View And Cache Contract

EARTH-4 is cached by:

- tick bucket
- observer cell key
- lens profile id

The sky artifact is a derived view artifact only.
It must not be written into authoritative world state.

## 9) Epistemics And Debug Overlays

- sky dome, sun, moon, twilight, and lawful night stars are physical and may be shown diegetically
- galactic plane markers and similar debug overlays require admin/debug epistemics
- debug overlay activation must be explicit and logged in the derived artifact extensions

## 10) Determinism Contract

- wall-clock time is forbidden
- anonymous RNG is forbidden
- named hash-derived streams only
- star ordering is deterministic
- cache keys are deterministic
- replay over the same tick bucket and observer cell key must reproduce the same artifact fingerprint

## 11) Extensibility

EARTH-4 reserves future extension surfaces for:

- `sky.rayleigh_mie`
- catalog-backed star overlays
- higher-fidelity lunar disks
- cloud, haze, aurora, and shadow packs

These future additions must layer on top of the EARTH-4 artifact contract without forcing identity or cache-key resets.
