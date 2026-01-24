# Model Registry

Status: canonical.
Scope: model family declarations and registry rules.
Authority: canonical. All worldgen models MUST follow this contract.

## Model families
A model family is a declarative data record. It MUST define:
- applicable domains or topology traits.
- supported fields and components.
- supported LOD ranges.
- assumptions and validity bounds.
- required capabilities.
- failure modes.

## Registry rules
- Model families MUST be data-registered, not hardcoded.
- Unknown model families MUST be preserved, not rejected.
- Model families MUST NOT define algorithms or procedural solvers.
- Model families MUST NOT encode realism assumptions as defaults.

## Examples (non-exhaustive)
- cosmology
- galaxy morphology
- planetary geology
- climate
- ecology
- magic
- astrology
- alternate physics

## References
- `docs/worldgen/REFINEMENT_CONTRACT.md`
- `schema/worldgen_model.schema`
