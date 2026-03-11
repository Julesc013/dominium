Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none

# CONTENT_STORE_BASELINE

## Scope

LIB-0 establishes the content-addressable storage constitution for reusable artifacts, linked instances, portable instances, and deterministic instance bundles.

## Directory Layout

Reference layout:

```text
<root>/
  bin/<product>/<build_id>/
  store/packs/<hash>/
  store/profiles/<hash>/
  store/blueprints/<hash>/
  store/locks/<hash>/
  store/migrations/<hash>/
  store/repro/<hash>/
  instances/<instance_id>/instance.manifest.json
  saves/<save_id>/save.manifest.json
  saves/<save_id>/state.snapshots/
  saves/<save_id>/patches/
  saves/<save_id>/proofs/
  exports/<bundle_id>.bundle
```

## Schema Definitions

Added LIB-0 schemas:

- `schema/lib/store_root.schema`
- `schema/lib/install_manifest.schema`
- `schema/lib/instance_manifest.schema`
- `schema/lib/save_manifest.schema`

Compatibility stance:

- Existing top-level install/instance/save schemas remain supported.
- LIB-0 fields are additive and hash-authoritative.

## Linked vs Portable

- Linked instances store `pack_lock_hash`, `profile_bundle_hash`, and `store_root`; reusable artifacts resolve from the shared CAS.
- Portable instances store the same hashes plus `embedded_artifacts`; required artifacts are vendored inside the instance.
- `mode` is storage topology only and does not create a runtime behavior fork.

## Readiness for LIB-1

LIB-0 now provides:

- deterministic CAS add/get/verify primitives
- hash-backed launcher preflight resolution
- linked clone without store duplication
- portable instance export/import roundtrip via instance bundles
- compatibility adapters for legacy path lockfiles

LIB-1 can now integrate InstallManifest/store bootstrap flows on top of the hash-pinned instance contract without redefining artifact identity.

## Validation Snapshot

Relevant invariants/docs upheld:

- `docs/canon/constitution_v1.md` A1, A4, A9
- `INV-ARTIFACTS-CONTENT-ADDRESSED`
- `INV-NO-PATH-BASED-SEMANTICS`
- `INV-PORTABLE-MODE-SELF-CONTAINED`

Contract/schema impact:

- changed: `schema/lib/store_root.schema`
- changed: `schema/lib/install_manifest.schema`
- changed: `schema/lib/instance_manifest.schema`
- changed: `schema/lib/save_manifest.schema`
- unchanged: existing top-level install/instance/save schema ids and versions

Validation runs:

- RepoX STRICT: refusal due repository-wide pre-existing findings outside LIB-0 scope (`data/meta/real_world_affordance_matrix.json`, derived pack provenance gaps, embodiment/process runtime findings)
- AuditX STRICT: `python tools/auditx/auditx.py verify --repo-root .` -> `scan_complete`
- TestX: `python tests/ops/content_store_tests.py --repo-root .`
- Compatibility smoke: `python tests/ops/ops_manifest_tests.py --repo-root .`
- Compatibility smoke: `python tests/share/share_bundle_tests.py --repo-root .`
- Compatibility smoke: `python tests/launcher/launcher_cli_tests.py --repo-root .`
- Topology refresh: `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`
- strict build: `cmake --build --preset verify --config Debug --target ALL_BUILD` -> refusal due pre-existing `mod_pack_builder` / `mod_pack_validator` runtime-library mismatches
