Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Binding Sources: `contracts/artifact/artifact_identity.contract.toml`, `contracts/artifact/artifact_manifest.schema.json`

# Artifact Identity Guidelines

Create an artifact manifest when a file or directory must be referred to across
time, exchanged, validated, migrated, trusted, released, or preserved as evidence.

Do not use a path, filename, or implementation directory as artifact identity.

## Choosing An Artifact ID

Use a semantic ID:

- `domino.<area>.<name>.vN` for reusable Domino substrate artifacts.
- `dominium.<area>.<name>.vN` for Dominium product artifacts.
- reverse-DNS IDs for packs where appropriate, such as
  `org.dominium.core.units`.

Invalid IDs include:

- `content/packs/core/pack_manifest.json`
- `pack_manifest.json`
- `C:\Temp\artifact.json`

Paths may appear only as non-authoritative location hints.

## Choosing A Kind

Use `contracts/artifact/artifact_kind.registry.json`. Add a kind only when an
existing one does not describe the artifact. New kinds require owner, expected
proof, and compatibility expectations.

## Required Manifest Fields

A durable artifact manifest needs:

- `artifact_id`
- `artifact_kind`
- `schema_id`
- `schema_version`
- `artifact_version`
- `owner`
- `stability`

Stable, locked, published, release, or externally consumed artifacts also need
hash, compatibility, migration/refusal, trust, and provenance policy.

## Generated Artifacts

Generated artifacts must declare their generator and source. Generated evidence
is not source truth unless a stronger contract promotes a fixture, corpus, or
registry entry.

## Fixtures

Fixture artifacts live under `tests/` and use `stability = fixture`. Fixtures
prove validator behavior. They do not define product compatibility promises.

## Archive And Quarantine

Archive records are historical by default. Quarantined artifacts are retained
for review or repair, not active source truth. Do not use archive paths as active
artifact identity.

## Updating An Artifact Format

For provisional artifacts, update the manifest and record migration notes. For
stable artifacts, add compatibility proof, migration or refusal behavior, and a
replacement/deprecation record before changing meaning.

## Validation

Run:

```text
python tools/validators/contracts/check_artifact_identity.py --repo-root . --strict
python tools/validators/contracts/check_artifact_identity.py --repo-root . --fixtures
python tools/validators/contracts/check_artifact_identity.py --repo-root . --inventory
```

The inventory is descriptive in ARTIFACT-IDENTITY-LAW-01. It does not require all
existing artifacts to be migrated immediately.
