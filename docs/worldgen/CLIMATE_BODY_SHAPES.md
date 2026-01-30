# Climate Body Shapes (CLIMATE0)

Status: binding for T3 baseline.  
Scope: mapping climate envelopes across body shapes without special casing.

## Purpose
- Define how climate envelopes read coordinates for spheres, oblates, and slabs.
- Preserve determinism and scale behavior across body sizes.

## Shape handling rules
- **Sphere / oblate**
  - Use the authoritative terrain shape to derive latitude/longitude and altitude.
  - Latitude/longitude are expressed as turns (fixed-point), not degrees.
  - Altitude is measured relative to the configured radii; negative altitude is clamped for envelopes.
- **Slab (superflat)**
  - Latitude/longitude are synthesized from X/Y within the slab extent.
  - Longitude uses the full span; latitude uses a half-span to preserve consistent gradients.
  - Altitude derives from the absolute Z offset inside the slab thickness.
- **No planet-only logic**
  - The same mapping rules apply to asteroids, planets, megastructures, and slabs.
  - “North/South” is defined only by the chosen coordinate frame.

## Determinism and precision
- Authoritative transforms are fixed-point only.
- Shape-derived mapping is deterministic and stable under replay.
- Any conversion to floating point is presentation-only and non-authoritative.

## See also
- `docs/architecture/TERRAIN_COORDINATES.md`
- `docs/architecture/FLOAT_POLICY.md`
- `docs/architecture/SCALING_MODEL.md`
