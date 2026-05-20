Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Versioning Deprecation Guidelines

Use `contracts/versioning/versioning.contract.toml` when adding or changing a durable public or compatibility-bearing surface.

## Add A Versioned Surface

1. Choose a stable dotted ID that does not encode a path.
2. Declare owner, kind, version, lifecycle state, and stability.
3. Declare compatibility range when stable or when public dependents rely on the surface.
4. Declare migration and refusal policy.
5. Add proof and fixtures appropriate to the surface.
6. Register the public surface when it is externally visible or governance-relevant.

## Version An Artifact

Artifact versioning does not replace artifact identity. A durable artifact must still identify itself through artifact law: manifest, artifact ID, kind, schema ID/version, hash policy, compatibility policy, trust policy, and migration/refusal behavior.

Use the versioning law to state which artifact versions are compatible, deprecated, retired, or removed.

## Deprecate A Surface

Create a deprecation notice that names:

- surface ID
- deprecated version/date
- replacement ID or reason no replacement exists
- migration path
- refusal behavior after retirement
- removal policy
- owner
- proof/evidence

Do not remove implementation or registry entries as part of deprecation unless the task explicitly authorizes it.

## Retire A Surface

Retirement means no new use. Before retirement, make sure old references have one of:

- compatible bridge
- migration path
- explicit refusal code and diagnostic
- documented no-recovery policy

Retirement should update the owning registry and status evidence.

## Remove A Surface

Removal requires prior retirement for stable public surfaces. If old artifacts, saves, packs, replays, providers, modules, commands, or downstream products can reference the surface, removal must still produce migration, compatibility bridge, or refusal.

Never treat file deletion as proof that obligations disappeared.

## Breaking Changes

A breaking stable change needs at least one of:

- major version bump with old version preserved
- replacement protocol packet
- explicit migration
- explicit refusal
- compatibility bridge with proof

Breaking changes without a major version, migration, or refusal fail the validator fixture model.

## Generated, Fixture, And Historical Surfaces

Generated surfaces declare source and generator. Promotion to stable requires source, generator, promotion record, and proof.

Fixture surfaces are test-only and do not become public active contracts directly.

Historical surfaces are archive-only and need replacement/recovery process before active use.

## Validation

Run:

```text
python -m py_compile tools/validators/contracts/check_version_deprecation.py
python tools/validators/contracts/check_version_deprecation.py --repo-root . --strict
python tools/validators/contracts/check_version_deprecation.py --repo-root . --fixtures
python tools/validators/contracts/check_version_deprecation.py --repo-root . --inventory
```

Use `--inventory` for descriptive coverage. It reports current version-like surfaces but does not migrate them.
