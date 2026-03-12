# EARTH-10 Material Proxy Baseline

## Scope

EARTH-10 adds three canonical field projections for Earth surface tiles:

- `field.material_proxy`
- `field.surface_flags`
- `field.albedo_proxy`

The layer is additive-only and remains provisional. Truth stores only the proxy fields; all water and illumination usage stays in derived view surfaces.

## Mapping Rules

Deterministic material proxy derivation is authored by `src/worldgen/earth/material/material_proxy_engine.py` and applied through `process.earth_material_proxy_tick`.

- ocean tiles, lake tiles, and river tiles -> `mat.water`
- polar ice or ice-class tiles -> `mat.ice`
- arid inland low-elevation land -> `mat.sand`
- high-relief or high-elevation land -> `mat.rock`
- default land -> `mat.soil`

The sampled replay window at tick `144` currently yields:

- `mat.water`: `76`
- `mat.rock`: `27`
- `mat.ice`: `16`
- `mat.soil`: `9`
- `mat.sand`: `0` in the canonical replay window

## Flag Rules

Surface flags are deterministic masks over the surface flag registry:

- `mat.water` -> `flag.fluid` mask `2`
- `mat.ice` -> `flag.slippery` mask `4`
- every other current proxy -> `flag.buildable` mask `1`

Registry bit assignments:

- `flag.buildable` -> `1`
- `flag.fluid` -> `2`
- `flag.slippery` -> `4`
- `flag.hazardous` -> `8`
- `flag.protected` -> `16`

## Albedo Table

Canonical provisional albedo proxy values are stored as permille integers:

- `mat.rock` -> `420`
- `mat.soil` -> `330`
- `mat.sand` -> `520`
- `mat.water` -> `140`
- `mat.ice` -> `820`
- `mat.synthetic_generic` -> `500`

Optional friction proxy values are also registry-driven and remain opt-in through policy key `earth_material_proxy_friction_enabled`.

## Deterministic Envelope

Scoped EARTH-10 replay hashes:

- `material_proxy_registry_hash`: `ee784b281f531b5570a925fe177803d9f2b4e7f5c3a3dc24eb8151a19947c1d3`
- `surface_flag_registry_hash`: `a2d470564a54e281bb5049937f6a37adff0da0cbe21b4e9f08484209794e6f1e`
- `material_proxy_window_hash`: `0122394c5e7068624f3e299324f0969c650427052731ce9f3c28960095b47629`
- `overlay_hash`: `e3392add4415cbe28b204ebd43e8431d363ef671590191dbf095516dc35b0054`
- `field_projection_hash`: `19af95a81f94e8f31104662ee301c15d320d783c5e80784182528dfe766b7ebf`
- `cross_platform_material_hash`: `828151ef192eabf39f53a4809bd5685d8dd947b1ca61bf90ec53748fbe30251f`

Derived-view fixture hashes updated by the albedo preview hook:

- `EARTH-5 lighting hash`: `0d0f64d22ce4f4c67ba9c24bf13169fe61784f786c8cdd39d4d028cba722ca99`
- `EARTH-8 water hash`: `2d15e58d0dcaac1ee08c9a379810f1ef367bc18e8cb974ba2a7a3949ce6dd56d`

## Replacement Plan Pointers

All proxy rows remain provisional.

- material proxies -> future series `MAT`
- surface flags -> future series `DOM`
- albedo proxy field type -> future `MAT`/illumination-driven surface semantics

Replacement targets are declared in the registries and keep EARTH/collision/view code stable until MAT and DOM own these semantics directly.

## Readiness

EARTH-10 is ready for `SOL-1` illumination geometry unification because:

- the truth-side surface metadata is canonical and deterministic
- collision consumes proxy friction only through an opt-in policy hook
- water and lighting consume albedo through derived-only previews
- chemistry, density, and fluid-volume semantics remain explicitly out of scope
