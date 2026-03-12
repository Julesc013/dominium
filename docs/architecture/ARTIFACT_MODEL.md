Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Artifact Model (LIB-4)

Status: binding.
Scope: shareable non-pack, non-binary artifacts such as profile bundles, blueprints, system templates, process definitions, and view presets.

## Purpose

LIB-4 defines a universal artifact manifest pattern so shareable artifacts can:

- live in the content-addressable store by hash
- travel in portable bundles
- declare contract/capability requirements explicitly
- degrade or refuse deterministically
- require explicit migration instead of silent reinterpretation

## Canonical Kinds

- `artifact.profile_bundle`
- `artifact.blueprint`
- `artifact.system_template`
- `artifact.process_definition`
- `artifact.logic_program`
- `artifact.view_preset`
- `artifact.resource_pack_stub`

## Required Manifest Envelope

Every canonical LIB-4 artifact manifest declares:

- `artifact_id`
- `artifact_kind_id`
- `format_version`
- `content_hash`
- `required_contract_ranges`
- optional `required_capabilities`
- optional `compatible_topology_profiles`
- optional `compatible_physics_profiles`
- `degrade_mode_id`
- `migration_refs`
- `deterministic_fingerprint`

Payload-level schemas remain authoritative for their domain meaning. LIB-4 is the compatibility and sharing envelope around those payloads.

## Content Hash Rule

- If the artifact manifest is embedded in the payload itself, `content_hash` is computed from the canonical serialized payload with `content_hash` and `deterministic_fingerprint` blanked.
- If the artifact manifest is emitted as a sidecar, `content_hash` is computed from the canonical serialized referenced payload.
- Filesystem path spelling does not change `content_hash` or `deterministic_fingerprint`.

## Artifact Load Pipeline

Artifact load pipeline steps are mandatory for every LIB-4 shareable artifact load.

1. parse the artifact manifest
2. verify `content_hash`
3. compare `required_contract_ranges` against the selected install contract ranges
4. compare `required_capabilities` against the selected endpoint/install capabilities
5. compare optional topology/physics compatibility declarations when present
6. apply `degrade_mode_id`
7. if migration is needed, require explicit invoke-only migration

No silent migration is permitted.

## Degrade Modes

- `artifact.degrade.strict_refuse`: mismatch is a refusal outcome
- `artifact.degrade.best_effort`: mismatch degrades deterministically and logs the disabled surface
- `artifact.degrade.read_only_only`: mismatch permits inspect/read-only flows only when the caller explicitly allows read-only

## Invariants

- `INV-SHAREABLE-ARTIFACTS-MUST-HAVE-MANIFEST`
- `INV-ARTIFACTS-CONTENT-ADDRESSED`
- `INV-ARTIFACT-LOAD-VALIDATED`

## Related Contracts

- `schema/lib/artifact_manifest.schema`
- `schema/lib/artifact_reference.schema`
- `docs/architecture/CONTENT_AND_STORAGE_MODEL.md`
- `docs/architecture/BUNDLE_MODEL.md`
