Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Blueprints And Research

## Blueprint Contract
- A blueprint is a `KnowledgeArtifact`.
- Blueprint payload includes:
  - structural graph references
  - port/contract expectations
  - process requirements
  - assumptions and confidence metadata
- Blueprints may be incomplete or wrong; refusal semantics handle invalid execution.

## Assumptions, Confidence, Provenance
- Assumptions are explicit artifact fields, not implicit runtime defaults.
- Confidence is metadata and does not grant authority.
- Provenance links blueprint updates to observation/report/training sources.

## Reverse Engineering Workflow
- Reverse engineering proceeds through explicit process stages:
  - observation capture
  - hypothesis creation
  - test execution
  - artifact update
- Process execution remains deterministic and audit-visible.

## Research Workflow
- Research is explicit uncertainty reduction over knowledge artifacts.
- Research outputs update artifact confidence/provenance without mutating simulation law.

## Dependencies
- `docs/architecture/KNOWLEDGE_AND_SKILLS_MODEL.md`
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/REFUSAL_SEMANTICS.md`
