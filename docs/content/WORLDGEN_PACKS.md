# Worldgen Packs

These packs are OPTIONAL. They define procedural baselines and optional
real-world calibration overlays. No pack is required to boot or run the system.

## Procedural baseline packs (WG-2)

### org.dominium.worldgen.base.cosmology
Purpose: Define the universe root and cosmology refinement lattice.
Provides:
- `worldgen.model.cosmology`
- `topology.universe`
- `topology.cosmic_filament`
- `topology.cosmic_void`

### org.dominium.worldgen.base.galaxy
Purpose: Refine cosmology into unnamed galaxies and structures.
Provides:
- `worldgen.model.galaxy_morphology`
- `topology.galaxy`
- `topology.galactic_structure`

### org.dominium.worldgen.base.system
Purpose: Refine galaxies into unnamed star systems.
Provides:
- `worldgen.model.system_formation`
- `topology.star_system`
- `topology.barycenter`

### org.dominium.worldgen.base.body
Purpose: Refine systems into unnamed bodies and belts.
Provides:
- `worldgen.model.body_formation`
- `topology.body`
- `topology.belt`

### org.dominium.worldgen.base.surface_micro
Purpose: Enable infinite micro-scale refinement.
Provides:
- `worldgen.model.surface_micro`
- `field.microstructure`

## Real-world calibration overlays (WG-3)

### org.dominium.worldgen.real.milkyway
Purpose: Refine one galaxy node into the Milky Way.
Provides:
- `topology.galaxy.milkyway`
- `refinement.override.galactic_structure`

### org.dominium.worldgen.real.sol
Purpose: Refine one system node into Sol.
Provides:
- `topology.system.sol`
- `refinement.override.orbits`

### org.dominium.worldgen.real.earth_macro
Purpose: Refine one body node into Earth (macro only).
Provides:
- `topology.body.earth`
- `field.terrain.macro`
- `field.climate.macro`
- `field.atmosphere.macro`

## Contract notes
- All packs use refinement plans and model declarations only.
- All packs declare provenance and confidence metadata.
- Removing any pack MUST leave the remaining universe valid.
