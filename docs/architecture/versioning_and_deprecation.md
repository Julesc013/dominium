Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Versioning And Deprecation

VERSION-DEPRECATION-LAW-01 defines how Dominium surfaces and durable artifacts evolve without silent breakage. A thing does not become stable by existing, and it does not become safe to delete because the implementation moved.

This law applies to public surfaces, ABI/API boundaries, schemas, protocols, registries, commands, diagnostics, refusal codes, artifacts, providers, modules, Workbench workspaces, app descriptors, packs, release artifacts, generated outputs, fixtures, and historical records.

## Versioned Surface

A versioned surface declares:

- `id`
- `kind`
- `version`
- `owner`
- `lifecycle_state`
- `stability`
- `compatibility_range`
- `introduced_in`
- optional `deprecated_in`, `retired_in`, and `removed_in`
- optional `replacement`
- `migration_policy`
- `refusal_policy`
- `proof`
- `notes`

Identity is the declared ID. It is not a path, filename, folder name, executable name, provider directory, or implementation detail.

## Lifecycle States

The lifecycle registry is `contracts/versioning/lifecycle_state.registry.json`.

`experimental` may change or disappear and must not be a stable dependency.

`provisional` is visible and intended, but does not carry a compatibility promise.

`stable` carries a compatibility promise and requires proof plus compatibility range.

`deprecated` remains supported, but new use is discouraged and a replacement, migration, or reason for no replacement is declared.

`retired` is not active for new use. Old references must have compatibility, migration, bridge, or refusal behavior.

`removed` is no longer available. Old references must refuse deterministically or be bridged by a declared compatibility path.

`generated` is derived from a source of truth and must declare source and generator before promotion.

`fixture` is test-only.

`historical` is archive-only.

## Transitions

Allowed transitions are intentionally narrow:

- experimental to provisional
- provisional to stable
- stable to deprecated
- deprecated to retired
- retired to removed
- generated to provisional or stable only with source/generator and promotion proof

Stable to removed directly is forbidden. Fixture or historical surfaces do not become active stable surfaces without explicit promotion or replacement/recovery process.

## Compatibility Ranges

Compatibility range mode can be:

- `exact`
- `minimum`
- `maximum`
- `range`
- `any_provisional`
- `incompatible_refuse`

Stable surfaces cannot omit compatibility range. Semver-like numbering helps readers, but compatibility is not inferred from a version string alone.

## Versioning Guidance

Breaking stable API or ABI changes require a major version, replacement, migration, or deterministic refusal.

Non-breaking compatible additions may be minor changes when the owning contract permits them.

Documentation-only and proof-only corrections may be patch changes when behavior and compatibility are unchanged.

Schema and protocol versions may be semver or integer versions, but they must declare compatibility, unknown-field/default policy, migration, and refusal behavior under schema/protocol law.

## Deprecation

A deprecation notice uses `contracts/versioning/deprecation_notice.schema.json`.

It must name the deprecated surface, deprecated version/date, replacement or no-replacement reason, migration path, refusal behavior after retirement, removal policy, owner, proof, and evidence.

Deprecation is not removal. The surface remains supported until retirement policy says otherwise.

## Retirement And Removal

Retirement means no new use. It requires a policy for existing references.

Removal is a governed lifecycle state after obligations are resolved, migrated, bridged, or intentionally refused. Deleting a file is not a removal policy.

Public stable removal requires evidence that downstream obligations are gone, migrated, bridged, or deterministically refused.

## Migration And Refusal

Migration is explicit. Silent or best-effort migration is forbidden.

Unsupported or incompatible versions must produce structured refusal and diagnostics where the relevant registry exists. Initial diagnostics include `DOM-VERSION-UNSUPPORTED`, `DOM-VERSION-INCOMPATIBLE`, and `DOM-BREAKING-CHANGE-MISSING-MIGRATION`.

Initial refusals include `dominium.refusal.version.unsupported`, `dominium.refusal.version.incompatible`, `dominium.refusal.surface.retired`, and `dominium.refusal.surface.removed`.

## Relationships

Public surface law records visible surfaces and their stability.

Artifact identity law records durable artifact identity, kind, schema, hash, compatibility, trust, migration, and refusal.

Schema/protocol law governs schema and protocol evolution details.

Replacement protocol governs planned rewrites and replacements.

Capability/refusal law governs typed refusals and recovery actions.

Provider and module law govern descriptor lifecycle and conformance before promotion.

Release promotion remains later work; this task does not create release gates.

## Examples

Compatible stable schema update: bump minor version, keep compatibility range, add fixtures, and declare unknown/default behavior under schema law.

Breaking command input change: create a new command or major version, preserve old command behavior until deprecation/retirement, and refuse unsupported old input after retirement with a code.

Provider removal: deprecate provider descriptor, declare replacement provider/capability behavior, retire with refusal or degraded path, then remove only after evidence.

Pack format retirement: preserve old pack artifact IDs, declare migration or refusal, and do not infer compatibility from filename or folder location.
