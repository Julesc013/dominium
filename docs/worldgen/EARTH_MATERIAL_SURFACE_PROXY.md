# EARTH Material / Surface Proxy Model

Date: 2026-03-12
Series: EARTH-10
Status: provisional stub doctrine

## Purpose

EARTH-10 adds minimal, deterministic Earth surface metadata so later MAT, DOM, FLUID, SND, and SOL work can plug into Earth without rewriting Earth terrain, collision, or derived-view code.

This layer is intentionally proxy-only.

- no chemistry
- no molecules
- no density simulation
- no fluid-volume semantics
- no presentation state stored in truth

## Canonical Fields

The canonical fields are:

- `field.material_proxy`
- `field.surface_flags`
- `field.albedo_proxy`

They are additive Earth surface fields and remain loadable even when absent from older saves.

Because the current field engine is integer-only for scalar values, the canonical encodings are:

- `field.material_proxy`
  - scalar integer code
  - code-to-id mapping comes from `data/registries/material_proxy_registry.json`
- `field.surface_flags`
  - scalar integer bitmask
  - bit assignments come from `data/registries/surface_flag_registry.json`
- `field.albedo_proxy`
  - scalar integer permille in the canonical range `0..1000`
  - semantic meaning is normalized albedo `0.0..1.0`

## `field.material_proxy`

Represents the dominant Earth surface material proxy for the tile.

Initial proxy IDs:

- `mat.rock`
- `mat.soil`
- `mat.sand`
- `mat.water`
- `mat.ice`
- `mat.synthetic_generic`

Initial deterministic derivation:

1. ocean tiles, river tiles, and lake tiles map to `mat.water`
2. ice-class or ice-baseline tiles map to `mat.ice`
3. high-elevation land maps to `mat.rock`
4. arid low-relief land may map to `mat.sand`
5. remaining land maps to `mat.soil`

`mat.synthetic_generic` is reserved for future DOM/MAT authored surfaces and is not emitted by the default EARTH-10 terrain stub.

## `field.surface_flags`

Represents a deterministic bitmask of coarse surface affordance flags.

Initial flags:

- `flag.buildable`
- `flag.fluid`
- `flag.slippery`
- `flag.hazardous`
- `flag.protected`

Initial deterministic derivation:

- water tiles
  - set `flag.fluid`
  - clear `flag.buildable`
- ice tiles
  - set `flag.slippery`
  - clear `flag.buildable`
- ordinary land tiles
  - set `flag.buildable`
- `flag.hazardous` and `flag.protected`
  - reserved; default unset in EARTH-10

## `field.albedo_proxy`

Represents a deterministic coarse reflectance proxy.

Initial canonical values are stored as permille:

- water: low-mid
- rock: mid
- soil: low-mid
- sand: mid-high
- ice: high
- synthetic_generic: mid

This value is intended for future illumination/reflection work and may be referenced by derived water/lighting views immediately.

## Determinism

- authoritative derivation is integer-only
- ordering is `geo_cell_key` sorted
- no unnamed RNG
- no wall-clock
- derived-only hooks must call the same proxy engine or consume its output

## Stability

All EARTH-10 proxy rows are `provisional`.

Required replacement plans:

- `field.material_proxy`
  - future series: `MAT`
  - replacement target: authored material surface semantics with pack-defined replacement rules
- `field.surface_flags`
  - future series: `DOM`
  - replacement target: domain-owned affordance and protection semantics
- `field.albedo_proxy`
  - future series: `SOL`
  - replacement target: illumination/material reflectance contract with release-pinned semantics

Any behavior change still requires deterministic regression updates.
