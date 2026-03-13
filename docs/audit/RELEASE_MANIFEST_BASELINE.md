Status: DERIVED
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: RELEASE
Replacement Target: release-pinned signed manifest surfaces and reproducible-build audit outputs after RELEASE-2 and RELEASE-3

# Release Manifest Baseline

## Manifest Schema Summary

- `schema/release/release_manifest.schema`
  Defines one deterministic manifest per distribution directory with:
  `release_id`, `platform_tag`, `manifest_version`, `semantic_contract_registry_hash`, optional `stability_report_hash`, ordered `artifacts`, `manifest_hash`, and `deterministic_fingerprint`.
- `schema/release/release_artifact_entry.schema`
  Defines ordered artifact rows with:
  `artifact_kind`, `artifact_name`, `content_hash`, optional `build_id`, optional `endpoint_descriptor_hash`, optional `pack_compat_hash`, and `deterministic_fingerprint`.

## Generation Steps

1. Enumerate governed product binaries in `dist/bin` and capture:
   binary content hash, deterministic `build_id`, and live `--descriptor` hash.
2. Enumerate auxiliary shipped wrappers in `dist/bin` as binary artifacts without inventing descriptor semantics.
3. Enumerate packs in `dist/packs` and compute:
   canonical directory tree hash plus effective `pack.compat` hash.
4. Enumerate profiles, locks, bundles, and shipped manifest files in stable sorted order.
5. Resolve `semantic_contract_registry_hash` from the shipped distribution surface, falling back to descriptor agreement when required.
6. Optionally include stability and regression hashes when the local repository surface provides them.
7. Canonically serialize the manifest, derive `manifest_hash`, and derive `deterministic_fingerprint`.

## Verification Steps

1. Load the release manifest from disk without network access.
2. Recompute `manifest_hash` and `deterministic_fingerprint` from canonical serialization.
3. Re-hash each artifact and refuse on any missing artifact or content mismatch.
4. Re-run `--descriptor` for governed product binaries and verify:
   descriptor hash and `build_id`.
5. Recompute effective pack compatibility hashes for shipped packs.
6. Re-check `semantic_contract_registry_hash` through descriptor agreement or local registry fallback.
7. Refuse deterministically on the first observed mismatch set; do not use wall-clock data or host-specific metadata.

## Guarantees

- Manifest ordering is deterministic and content-addressed.
- Offline verification is supported through `tools/release/tool_verify_release_manifest.py`.
- `setup verify --release-manifest <path>` routes through the canonical AppShell verification path.
- `launcher compat-status` surfaces release identity and manifest hash when a release manifest is present under the active install root.

## Non-Guarantees

- The committed baseline does not pin a live manifest hash from the repo-backed `dist/` tree.
- Bitwise-identical binaries across toolchains remain a later `RELEASE-3` concern; RELEASE-1 governs semantic manifest reproducibility and offline verification.

## Readiness

- Ready for `RELEASE-2` signing hooks.
- Ready for `RELEASE-3` reproducible build checks.
