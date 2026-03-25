Status: DERIVED
Last Reviewed: 2026-03-25
Supersedes: none
Superseded By: none
Stability: stable
Future Series: DIST-7/ARCHIVE
Replacement Target: signed historical release archives with retained channel bundles

# Offline Archive Model v0.0.0-mock

## Offline Archive Contents

The Ω-8 offline archive must contain a deterministic reconstruction tree with these required surfaces:

1. `artifacts/`
   - all CAS payloads referenced by the frozen `release_manifest.json`
   - payloads are placed under `artifacts/<content_hash>`
2. `release_index_history/`
   - the full retained history up to `v0.0.0-mock`
3. `release_manifest.json`
4. `component_graph.json`
5. `governance_profile.json`
6. `trust_root_registry.json`
7. `migration_policy_registry.json`
8. `semantic_contract_registry.json`
9. baseline worldgen seed + snapshot
10. baseline universe artifacts + snapshot
11. gameplay loop snapshot
12. disaster suite baseline
13. ecosystem verify baseline
14. update simulation baseline
15. trust strict baseline
16. performance baseline
17. `archive_record.json`

The archive may also contain supporting fixtures required to rerun frozen offline checks, including:

- disaster suite case definitions
- update simulation fixture indices
- trust strict fixtures
- optional source snapshot tarball

## Deterministic Archive Rules

- Archive member ordering is lexicographically sorted.
- Gzip mtime is zero.
- Tar member mtimes are zero.
- Tar owners and groups are zeroed.
- No absolute paths are written into archive member names.
- No host-specific metadata is retained.
- Archive integrity is tracked by:
  - `archive_bundle_hash`
    raw tar.gz sha256, recorded in regression/report surfaces
  - `archive_projection_hash`
    canonical member-hash projection recorded in `archive_record.json`

## Rebuildability Guarantee

Given only the offline archive bundle, an operator can:

- verify release integrity
- reconstruct the frozen install artifact set
- recover the release index history snapshot
- re-anchor governance / trust / migration / contract hashes
- rerun WORLDGEN-LOCK verification
- rerun BASELINE-UNIVERSE verification
- rerun MVP gameplay verification
- rerun the disaster suite

## Scope Notes

- Network access is never required.
- Trust decisions remain offline and policy-driven.
- The archive does not overwrite `release_index_history`; it retains a snapshot.
- Source snapshot inclusion is optional and additive.

## Stability

- `offline_archive_version = 0`
- `stability_class = stable`
