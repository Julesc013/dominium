Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Built-in Templates (WD-0)





Status: binding.


Scope: mandatory built-in WorldDefinition templates.





## Global requirements


- Built-in templates require no packs and no assets.


- Built-in templates are deterministic.


- Labels are identifiers only; they are not truth claims.


- All output uses the canonical WorldDefinition schema.


- Generator source is `built_in`.





## Template: Empty Universe


template_id: `builtin.empty_universe`


version: `1.0.0`


Description: Topology root only; valid but inert.





Parameter schema:


- `seed.primary` (u64, optional; default 0)





Output guarantees:


- One topology node (root) with stable id.


- No bodies, no surfaces, no patches.


- Spawn spec resolves to the root node.





Refusal conditions:


- Seed outside [0, 2^64-1].





## Template: Minimal System


template_id: `builtin.minimal_system`


version: `1.0.0`


Description: One system and one body (sphere); spawn possible.





Parameter schema:


- `seed.primary` (u64, optional; default 0)





Output guarantees:


- Universe → system → body DAG.


- One body tagged as a sphere.


- Spawn spec resolves to the body node.





Refusal conditions:


- Seed outside [0, 2^64-1].





## Template: Realistic Test Universe


template_id: `builtin.realistic_test_universe`


version: `1.0.0`


Description: One labeled galaxy, one labeled system, a labeled star, rocky and


gas giant spheres, and an Earth-labeled sphere with spawn.





Parameter schema:


- `seed.primary` (u64, optional; default 0)





Output guarantees:


- Universe → galaxy → system DAG.


- Labeled bodies: Sun, Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus,


  Neptune (all spheres).


- Spawn spec resolves to the Earth-labeled body.


- Labels are identifiers only and do not assert real-world truth.





Refusal conditions:


- Seed outside [0, 2^64-1].





## References


- `docs/architecture/WORLDDEFINITION.md`


- `docs/worldgen/TEMPLATE_REGISTRY.md`


- `schema/world_definition.schema`
