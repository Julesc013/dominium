Status: BASELINE
Last Reviewed: 2026-03-06
Supersedes: docs/system/SYSTEM_TIER_AND_ROI_POLICY.md
Superseded By: none
Version: 1.0.0
Compatibility: SYS-4 system template library doctrine.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# System Templates

## Purpose
`SystemTemplate` provides reusable, pack-driven blueprints for composing complex systems without introducing bespoke runtime object classes.

Templates:
- accelerate player/institution build workflows,
- remain expandable/inspectable,
- preserve SYS collapse/expand invariants and deterministic execution.

## A) Template Purpose
- Templates are optional accelerators, not mandatory content.
- Runtime must boot with no template packs present.
- Templates cannot bypass process/control/commitment discipline.

## B) Template Composition
A template may reference nested templates (hierarchical composition) and must declare:
- interface signature template reference,
- boundary invariant template references,
- macro model set reference,
- tier contract reference,
- safety pattern instance templates,
- spec bindings.

Template composition is declarative and deterministic; no hidden imperative build scripts are allowed.

## C) Template Instantiation Modes
- `instantiate.micro`
  - compile full assembly graph specification and instantiate micro system rows/assemblies.
- `instantiate.macro`
  - create macro capsule directly (policy-gated).
  - forbidden when macro direct instantiate policy denies.
- `instantiate.hybrid`
  - produce hybrid decomposition plan (capsule + selected expanded submodules).
  - deterministic output only; no runtime randomness.

All authoritative mutations occur through `process.template_instantiate`.

## D) Compatibility and Versioning
- Templates are versioned records (`template_id` + `version`) bound to schema semver.
- Breaking schema transitions require explicit CompatX migration or deterministic refusal.
- Open-map `extensions` fields remain preserved for forward compatibility.

## E) Process/Control/MAT Discipline
Template instantiation is controlled by:
- CTRL planning and resolution (`PlanArtifact` creation),
- MAT commitments (canonical commitment rows),
- canonical instance recording (`template_instance_record`).

No direct world spawn is allowed unless explicitly authorized by profile/law and still routed through process.

## F) Determinism Rules
- Nested template resolution uses deterministic topological ordering by `template_id`.
- Duplicate/ambiguous references are normalized deterministically.
- Compilation outputs include deterministic fingerprints.
- Replay/proof must reproduce identical compile fingerprints for identical inputs.

## G) Null-Boot and Optional Packs
- Core registry can be empty and still valid.
- Starter templates are delivered as optional pack content (`packs/system_templates/base/`).
- Missing packs must yield deterministic refusals (`refusal.template.missing_domain`/`not_found`) without state corruption.

## H) Non-Goals
- No bespoke engine/vehicle/factory object classes.
- No wall-clock behavior.
- No nondeterministic compile/instantiate behavior.
- No bypass of SYS collapse/expand or control-plane contracts.

## I) UX Integration (RND + CTRL)
- Developer-facing browser: `tools/system/tool_template_browser`.
- Browser surfaces:
  - interface signature template summary,
  - invariant template set,
  - safety pattern instances,
  - expected macro outputs from compiled model bindings.
- Execution path remains policy-gated:
  - browser execute requires explicit gate (`--allow-execute`),
  - macro mode additionally requires policy (`allow_macro`).
- Build actions run through `process.template_instantiate`; no direct spawn path.

## J) Proof and Replay
- Instantiation process writes:
  - canonical `system_template_instance_record_rows`,
  - `template_instance_record_hash_chain`,
  - `compiled_template_fingerprint_hash_chain`.
- Deterministic reproducibility verifier:
  - `tools/system/tool_verify_template_reproducible`
- Any fingerprint drift under identical inputs is treated as a contract violation.
