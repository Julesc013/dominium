Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Epistemics Overview

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: canonical.
Scope: knowledge artifacts, epistemic boundaries, and subjective projection.
Authority: canonical. All epistemic systems MUST defer to this.

## Binding rules
- Knowledge artifacts MUST be modeled as data and MUST NOT mutate objective truth.
- Objective truth MUST remain the single authoritative simulation state.
- Subjective snapshots MUST be derived from objective truth plus epistemic artifacts.
- Unknown, inferred, and known states MUST be explicit and preserved.
- Access control MUST gate subjective visibility, not objective state.

## Knowledge artifacts
- Observations, measurements, surveys, theories, myths, and misinformation are all knowledge artifacts.
- Artifacts MUST carry provenance and confidence/uncertainty descriptors.
- Conflicting artifacts MUST coexist; none may overwrite objective truth.

## Epistemic refinement gating
- Subjective refinement MUST require sufficient epistemic artifacts.
- Insufficient knowledge MUST degrade resolution or emit explicit unknowns.
- Refinement MUST NOT be granted by camera zoom or viewer privilege.

## References
- `docs/worldgen/OBJECTIVE_VS_SUBJECTIVE_REALITY.md`
- `docs/worldgen/REFINEMENT_CONTRACT.md`
- `schema/knowledge.schema`
- `schema/measurement_artifact.schema`
