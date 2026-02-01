Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Worldgen Overview

Status: canonical.
Scope: worldgen philosophy and constraints.
Authority: canonical. All worldgen docs MUST defer to this file.

## Core assertions
- World generation MUST be treated as a layered refinement lattice, not a
  generator or content factory.
- Procedural data and authored data MUST be equal citizens. Neither is
  privileged or assumed to be more truthful.
- Reality MUST be refined, not created. Refinement adds detail to existing
  truth; it does not invent default truth.
- Infinite detail MUST be achieved through bounded refinement, not unbounded
  computation or implicit defaults.

## Engine neutrality
- The engine MUST NOT know physics, realism, or setting-specific laws.
- The engine MUST enforce coherence, invariants, and provenance only.
- Realistic, magical, incorrect, and unknown universes MUST all be valid when
  declared by content and models.

## Non-goals
- Worldgen MUST NOT encode real-world assumptions (Earth, Sol, humans).
- Worldgen MUST NOT introduce special cases for physics, magic, or genre.
- Worldgen MUST NOT define or imply procedural algorithms.

## References
- `docs/worldgen/REFINEMENT_LATTICE.md`
- `docs/worldgen/REFINEMENT_CONTRACT.md`
- `docs/worldgen/MODEL_REGISTRY.md`
- `docs/worldgen/OBJECTIVE_VS_SUBJECTIVE_REALITY.md`
- `docs/worldgen/REALISM_IS_CONTENT.md`