Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: COMPAT/RELEASE
Replacement Target: release-pinned artifact lifecycle governance and migration execution bundles

# Migration Lifecycle Model

## Artifact Classes

- `artifact.save`
- `artifact.install_manifest`
- `artifact.instance_manifest`
- `artifact.pack_lock`
- `artifact.profile_bundle`
- `artifact.blueprint`
- `artifact.release_manifest`
- `artifact.release_index`
- `artifact.component_graph`
- `artifact.install_plan`
- `artifact.negotiation_record`
- `artifact.session_template`

## Compatibility Ranges

Each artifact kind is governed by a declared migration policy:

- `backward_read_range`
  - versions that may be loaded directly without migration
- `forward_read_range`
  - versions that may be opened read-only when the artifact class allows read-only access
- `migration_supported_range`
  - versions that may be migrated through a deterministic chain

Range evaluation is deterministic and version-order based only. No wall-clock, host state, or network state may participate in the decision.

## Migration Policy

For every governed artifact load:

1. resolve the artifact kind
2. load the lifecycle policy from `migration_policy_registry`
3. determine the observed version
4. compare the observed version with the declared current version
5. choose exactly one action:
   - `load`
   - `migrate`
   - `read_only`
   - `refuse`
6. emit a canonical `migration_decision_record`

No loader may silently migrate or silently reinterpret a newer artifact version.

## Deterministic Migration Chains

Migration chains are deterministic only:

- each step declares:
  - `migration_id`
  - `from_version`
  - `to_version`
  - `artifact_kind_id`
- steps are applied in stable version order
- each applied step must emit a canonical migration event with deterministic hashes

If no chain exists, the loader must refuse with explicit remediation.

## Read-Only Policy

Read-only is allowed only when all of the following hold:

- the artifact kind declares `read_only_allowed=true`
- the artifact version is within `forward_read_range`
- the caller explicitly allows read-only behavior
- semantic contract compatibility is safe for the artifact class

Read-only mode must:

- be explicit in the decision record
- be explicit in user-facing output
- preserve the existing law-profile override or equivalent non-authoritative open policy where applicable

## Refusal and Remediation

Canonical lifecycle refusal codes:

- `refusal.migration.no_path`
- `refusal.migration.not_allowed`
- `refusal.migration.contract_incompatible`

Required remediation guidance:

- install an older compatible build
- run a specific migration tool
- open the artifact in read-only mode if allowed

## Artifact-Specific Notes

- saves
  - may migrate deterministically when the current engine supports a save migration chain
  - may open read-only only when save metadata and instance/tool policy allow it
- installs / instances
  - current mock release treats missing explicit `format_version` as current policy version for compatibility
  - policy consultation is still mandatory; missing policy is refusal
- release manifests / release indices / component graphs / install plans
  - current mock release freezes their lifecycle ranges and decision records without changing their canonical meaning
- negotiation records
  - migration is expected to be rare; future versions may be inspected read-only only when policy allows it
