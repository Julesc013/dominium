# Canonical Base Packs

These packs are OPTIONAL and are provided only to demonstrate the architecture.
No pack is required to boot or run the engine or game.

Pack definitions live under `data/packs/`.

## org.dominium.base.topology

Purpose:
- Minimal topology root for inspection and testing.

Provides:
- `topology.universe`
- `topology.node.basic`
- `domain.volume.basic`

## org.dominium.base.rules

Purpose:
- Template-only process, capability, and institution descriptors.

Provides:
- `process.template.basic`
- `capability.template.basic`
- `institution.template.basic`

## org.dominium.base.universe.milkyway

Purpose:
- Macro-scale galaxy example with procedural/hybrid representation only.

Provides:
- `topology.galaxy.milkyway`
- `topology.cluster.local_group`
- `topology.structure.spiral_arms`
- `navigation.importance.index`

## org.dominium.base.system.sol

Purpose:
- Macro-scale star system example with planets, belts, and major moons.

Provides:
- `topology.system.sol`
- `topology.star.g_type`
- `topology.body.planetary`
- `topology.belt.asteroid`

## org.dominium.base.body.earth_macro

Purpose:
- Macro planetary body example with explicit facts and procedural refinement.

Provides:
- `topology.body.earth`
- `field.terrain.macro`
- `field.climate.macro`
- `field.atmosphere.macro`

## org.dominium.base.scenarios.minimal

Purpose:
- Explainable, non-assumptive scenario definitions.

Provides:
- `scenario.start.minimal`
- `scenario.autorun.ai`
- `scenario.inspection`
