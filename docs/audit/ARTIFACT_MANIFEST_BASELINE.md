Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# ARTIFACT_MANIFEST_BASELINE

## Purpose

LIB-4 defines a universal manifest envelope for shareable non-pack artifacts. The envelope pins:

- `artifact_id`
- `artifact_kind_id`
- `format_version`
- `content_hash`
- `required_contract_ranges`
- `degrade_mode_id`
- `migration_refs`
- `deterministic_fingerprint`

Optional compatibility selectors:

- `required_capabilities`
- `compatible_topology_profiles`
- `compatible_physics_profiles`

## Kinds And Degrade Modes

Canonical kinds:

- `artifact.profile_bundle`
- `artifact.blueprint`
- `artifact.system_template`
- `artifact.process_definition`
- `artifact.logic_program`
- `artifact.view_preset`
- `artifact.resource_pack_stub`

Canonical degrade modes:

- `artifact.degrade.strict_refuse`
- `artifact.degrade.best_effort`
- `artifact.degrade.read_only_only`

## Load / Validate Decision Tree

When loading a LIB-4 artifact:

1. validate the artifact manifest shape
2. verify `content_hash`
3. compare required contract ranges against the selected install contract surface
4. compare required capabilities against the selected endpoint/install capabilities
5. compare optional topology/physics profile declarations
6. if any check mismatches:
   - `strict_refuse` -> refuse
   - `best_effort` -> degrade deterministically
   - `read_only_only` -> inspect/read-only only when explicitly allowed
7. if migration is required:
   - explicit migration only
   - otherwise refuse or remain inspect-only

No silent migration is permitted.

## Readiness For LIB-5

LIB-4 is ready for forking/namespacing/provides work because:

- shareable artifact identity is now hash-pinned
- compatibility requirements are explicit and portable
- content-addressed store categories can expand to third-party kinds without path semantics
- migration hooks are declared without forcing silent rewrites

## Enforced Invariants

- `INV-SHAREABLE-ARTIFACTS-MUST-HAVE-MANIFEST`
- `INV-ARTIFACTS-CONTENT-ADDRESSED`
- `INV-ARTIFACT-LOAD-VALIDATED`
