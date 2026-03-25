Status: DERIVED
Last Reviewed: 2026-03-25
Supersedes: none
Superseded By: none
Stability: stable
Future Series: DIST-7/ARCHIVE
Replacement Target: signed retained release archives with historical channel bundles

# ARCHIVE-OFFLINE-0 Retro Audit

## Existing Archive Inputs

- `ARCHIVE-POLICY-0` already freezes deterministic archive records, append-only `release_index_history`, and an offline tarball builder via [archive_policy_common.py](/d:/Projects/Dominium/dominium/tools/release/archive_policy_common.py).
- The current archive-policy path emits `archive_record.json` beside the distribution bundle, not a single reconstruction-first archive tree.
- `build_deterministic_archive_bundle()` already guarantees sorted members, zero gzip mtime, zero tar mtimes, normalized owners, and stable file ordering.

## Release Artifact State

- The current mock distribution exists at `dist/v0.0.0-mock/win64/dominium`.
- `release_manifest.json` is present and enumerates 25 artifacts: binaries, descriptors, pack lock, profile bundle, install manifests, and three pack payloads.
- Pack artifacts are currently directory trees under `store/packs/...`, so any offline CAS export must support both file and directory artifacts.

## Release Index History

- The repo does not retain a committed `release_index_history/` tree yet.
- `ARCHIVE-POLICY-0` synthesizes the append-only history snapshot during archive generation at `manifests/release_index_history/<channel>/<release>.json`.
- For `v0.0.0-mock`, the historical set is therefore one retained release-index snapshot.

## Artifact CAS Layout

- There is no committed single-bundle offline CAS tree today.
- Release artifacts are addressable by `content_hash` through `release_manifest.json`, but they remain stored in live distribution paths rather than under a dedicated `artifacts/<hash>` archive namespace.
- The offline archive layer therefore needs a reconstruction-first CAS projection that copies each manifest artifact into a stable `artifacts/<hash>` location.

## Trust / Governance / Migration Storage

- Governance profile storage is already stable at `data/governance/governance_profile.json` and inside the dist tree at `data/governance/governance_profile.json`.
- Trust roots are already stable at `data/registries/trust_root_registry.json` and inside the dist tree.
- Migration lifecycle policy coverage is already stable at `data/registries/migration_policy_registry.json`.
- Semantic contract pinning is already stable at `data/registries/semantic_contract_registry.json`.

## Baseline / Recovery Surfaces Already Available

- WORLDGEN lock inputs exist: `baseline_seed.txt`, `baseline_worldgen_snapshot.json`, and the verifier tool.
- BASELINE-UNIVERSE freeze inputs exist: baseline instance/profile/pack-lock/save/snapshot plus the verifier tool.
- MVP gameplay snapshot exists plus the verifier tool.
- Disaster suite cases and regression baseline exist plus the harness.
- Ecosystem, update-sim, trust-strict, and performance baselines already exist and are committed.

## Source Archive Availability

- There is still no automatically emitted per-release source snapshot tarball.
- The archive doctrine already allows an optional source snapshot for open or partially open releases.
- Ω-8 should preserve that policy: source snapshot support is structural and offline, but optional.

## Gaps To Close In Ω-8

- Build one deterministic archive tree that includes:
  - `artifacts/<hash>` CAS payloads
  - retained `release_index_history`
  - release/governance/trust/migration/contract snapshots
  - Ω baseline artifacts needed for reconstruction and regression
- Verify that the archive can re-anchor release integrity and rerun the frozen Ω subchecks offline.
- Freeze archive hash / record hash outputs into a committed regression baseline.
