Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# ARTIFACT-IDENTITY-LAW-01 Audit

## Status

PASS_WITH_WARNINGS.

## Why

Dominium needs stable artifact identity that does not depend on paths,
filenames, implementation directories, generated output locations, or Workbench
views. Packs, profiles, bundles, saves, replays, diagnostics, evidence packets,
release artifacts, schemas, registries, worldgen baselines, module descriptors,
and app descriptors need manifest-backed identity, version, hash, compatibility,
trust, migration, and refusal behavior.

## Added

- `contracts/artifact/artifact_identity.contract.toml`
- `contracts/artifact/artifact_manifest.schema.json`
- `contracts/artifact/artifact_kind.registry.json`
- `contracts/artifact/artifact_lifecycle.registry.json`
- `contracts/artifact/artifact_ref.schema.json`
- `contracts/artifact/artifact_hash_policy.contract.toml`
- `contracts/artifact/artifact_compatibility.contract.toml`
- `contracts/artifact/artifact_trust_policy.contract.toml`
- `tools/validators/contracts/check_artifact_identity.py`
- `tests/contract/artifact_identity/**`
- `docs/architecture/artifact_identity_law.md`
- `docs/development/artifact_identity_guidelines.md`

## Initial Registry

- artifact kinds registered: 23.
- lifecycle states registered: 11.
- artifact diagnostic codes added: 8.
- public surface registry updated with artifact identity surfaces.

No artifact format is marked stable. No artifact runtime loader, save/replay
system, package runtime, Workbench UI, product behavior, or release publication
was implemented.

## Initial Inventory

The inventory scanned 17,782 tracked files and found 1,890 artifact-like files.
It classified 244 manifest-backed candidates, 1,437 schema/registry files,
103 historical/archive files, 1 generated-evidence file, and 105 deferred
artifact-like files. Existing artifacts were not migrated.

## Proof

- Artifact validator strict: PASS, 23 kinds, 11 lifecycle states, 0 findings.
- Artifact validator fixtures: PASS.
- Artifact inventory: PASS_WITH_WARNINGS, descriptive only.
- Diagnostics validator: PASS, 22 diagnostic codes.
- Public surface validator: PASS, 57 surfaces.
- Command surface validator: PASS.
- ABI validator: PASS with 2,851 existing warnings.
- Dependency direction validator: FAIL on known existing debt from
  DEPENDENCY-DIRECTION-01; latest scan checked 16,175 files with
  358 violations and 38 warnings.
- Fast strict: PASS, 32/32 commands, 321.578 seconds after correcting the
  CANON_INDEX placement for the new derived architecture document.
- Remaining validation is recorded in
  `.aide/reports/ARTIFACT-IDENTITY-LAW-01-validation.md`.

## Known Warnings

- Artifact identity law is provisional.
- Existing artifacts are inventoried but not migrated.
- Compatibility corpus is not yet populated.
- Runtime artifact loading and save/replay/package systems remain future work.
- Dependency-direction strict debt remains visible and unresolved.
- Full CTest was not run and remains T4 full/release proof.

## Next Task

`SCHEMA-PROTOCOL-LAW-01`.
