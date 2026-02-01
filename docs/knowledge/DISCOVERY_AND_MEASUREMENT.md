Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Discovery and Measurement

Status: canonical.
Scope: epistemic processes and measurement artifacts.
Authority: canonical. All discovery workflows MUST follow this.

## Process requirements
- Discovery MUST be expressed as epistemic processes.
- Epistemic processes MUST declare inputs, outputs, and required capabilities.
- Outputs MUST be knowledge or measurement artifacts.
- Epistemic processes MUST NOT mutate objective truth.

## Measurement artifacts
- Measurements MUST include target references, era tags, and access control descriptors.
- Measurements MUST include confidence and uncertainty descriptors.
- Measurements MUST be immutable records; corrections require new artifacts.

## Publication and suppression
- publish, suppress, and distort MUST only affect visibility or subjective projection.
- These processes MUST NOT delete or rewrite objective truth.

## References
- `schema/process.schema`
- `schema/knowledge.schema`
- `schema/measurement_artifact.schema`
- `docs/worldgen/REFINEMENT_CONTRACT.md`