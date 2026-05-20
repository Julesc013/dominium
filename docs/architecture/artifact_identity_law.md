Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Binding Sources: `contracts/artifact/artifact_identity.contract.toml`, `contracts/artifact/artifact_manifest.schema.json`, `contracts/artifact/artifact_kind.registry.json`, `contracts/artifact/artifact_hash_policy.contract.toml`, `contracts/artifact/artifact_compatibility.contract.toml`, `contracts/artifact/artifact_trust_policy.contract.toml`

# Artifact Identity Law

An artifact is a persisted, exchanged, generated, or authored unit with identity,
schema, version, provenance, and compatibility behavior. Packs, profiles,
bundles, saves, instances, replays, diagnostic bundles, evidence packets, release
packages, schemas, registries, worldgen baselines, Workbench module descriptors,
app descriptors, generated reports, and archive records are artifact surfaces
when they are durable enough to be referred to across time.

Path is not identity. Filename is not identity. Folder location is not identity.
Implementation code is not artifact identity. A Workbench view is not artifact
identity.

## Manifest Identity

Durable artifacts identify themselves with a manifest. The initial manifest
schema is `contracts/artifact/artifact_manifest.schema.json`.

Every stable or semi-stable artifact should declare:

- `artifact_id`
- `artifact_kind`
- `schema_id`
- `schema_version`
- `artifact_version`
- `owner`
- `stability`
- hash, compatibility, migration, refusal, trust, and provenance fields when
  the artifact is stable, published, release-bearing, or externally consumed

The artifact ID is a semantic ID, not a path. Use Dominium/Domino dotted IDs or
reverse-DNS pack IDs. Examples:

- `dominium.profile.default`
- `domino.replay.log.v1`
- `org.dominium.core.units`
- `dominium.evidence.fast_strict.run`

## Kinds And Lifecycle

Artifact kinds are registered in `contracts/artifact/artifact_kind.registry.json`.
Lifecycle states are registered in
`contracts/artifact/artifact_lifecycle.registry.json`.

Most current artifacts should be treated as provisional, generated, fixture, or
historical until they have compatibility proof. This task does not migrate
existing packs, saves, replays, or release artifacts.

## Hashes

Hash policy is owned by
`contracts/artifact/artifact_hash_policy.contract.toml`.

Stable artifact hashes require canonical serialization. Paths are not hash input
unless the artifact format explicitly declares relative paths as content.
Directory/package hashes use manifest-first identity, sorted relative file lists,
per-file hashes, and an aggregate hash.

Generated reports may have evidence hashes without becoming stable source truth.

## Compatibility, Migration, And Refusal

Compatibility policy is owned by
`contracts/artifact/artifact_compatibility.contract.toml`.

Old artifacts must load, migrate explicitly, or refuse deterministically. Silent
fallback and silent migration are forbidden. Stable artifacts require future
compatibility fixtures or a compatibility corpus. Provisional artifacts may
change, but migration notes must record the meaning of the change.

## Trust And Provenance

Trust policy is owned by `contracts/artifact/artifact_trust_policy.contract.toml`.
Initial trust levels include local, generated, repo-canonical, signed-release,
external, fixture, and historical postures.

Generated artifacts declare generator and source. External artifacts require a
trust posture before they become active dependencies. Deep mod-pack trust remains
owned by `MOD-PACK-TRUST-MODEL-01`.

## Evidence And Diagnostics

Artifact references use `contracts/artifact/artifact_ref.schema.json`. Evidence
packets may include `artifact_refs` so proof can name artifacts without making
paths authoritative.

Artifact diagnostics are registered provisionally under
`contracts/diagnostics/diagnostic_code.registry.json`. They cover missing IDs,
unknown kinds, missing schemas, path-as-ID, hash mismatch, unsupported schema,
required migration, and insufficient trust.

## Generated, Local, Archive, And Fixture Artifacts

Generated/local outputs are not source truth. Archive records are historical by
default. Fixtures live under tests and do not create product compatibility
promises.

## Relationship To Other Law

The public surface registry decides which artifact formats are visible surfaces.
The schema/protocol law will mature schema evolution and compatibility. The
replacement protocol will define stable replacement packets. Workbench modules
and app descriptors must use artifact identity when they become durable.
