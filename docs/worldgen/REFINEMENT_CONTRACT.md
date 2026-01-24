# Refinement Contract

Status: canonical.
Scope: unified contract for refinement and collapse.
Authority: canonical. All materialization MUST use this contract.

## Refinement request (data shape)
A refinement request MUST be expressed as data with the following fields:

- target: a topology node reference and domain volume reference.
- resolution band: LOD_min..LOD_max tags.
- field/component set: explicit identifiers for requested fields or components.
- mode: objective or subjective.
- budget: explicit compute, memory, and time limits.
- authority token: explicit token scoped to the request.
- seed namespace: explicit namespace binding for determinism.
- required capabilities: explicit capability identifiers.
- dependencies: pack and model references required to satisfy the request.
- failure semantics: explicit outcome policy (degrade, freeze, or deny).

## Refinement response (data shape)
A refinement response MUST be expressed as data with the following fields:

- materialized snapshot: immutable snapshot handle and metadata.
- provenance record: identifiers for inputs, models, and decisions.
- validation targets: declared targets and bounds for verification.
- confidence and uncertainty metadata: explicit epistemic descriptors.

## Binding rules
- This contract applies at ALL scales.
- This contract applies to collapse as well as refinement.
- This contract is the ONLY gateway to materialization or collapse.
- No implicit defaults are permitted; every request MUST declare its scope and
  bounds.
- Requests that exceed budgets or violate capabilities MUST resolve through the
  explicit failure semantics.

## References
- `schema/topology.schema`
- `schema/domain.schema`
- `schema/field.schema`
- `schema/capability.schema`
- `schema/authority.schema`
- `schema/snapshot.schema`
- `schema/knowledge.schema`
- `schema/worldgen_model.schema`
- `schema/refinement_plan.schema`
- `schema/measurement_artifact.schema`
