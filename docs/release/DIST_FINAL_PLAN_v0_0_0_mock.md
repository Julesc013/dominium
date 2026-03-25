Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none
Stability: stable
Future Series: OMEGA
Replacement Target: Ω-11 DIST-7 execution record and mock release signoff

# DIST Final Plan v0.0.0-mock

Authoritative Ω-10 execution plan for producing the `v0.0.0-mock` DIST-7 package set without changing runtime semantics.

This plan is binding for Ω-11.
It documents the exact inputs, commands, outputs, gates, inclusion rules, archive rules, and mock publication steps.

## Frozen Inputs

- Canon:
  - `docs/canon/constitution_v1.md`
  - `docs/canon/glossary_v1.md`
- Distribution / release doctrine:
  - `docs/release/DISTRIBUTION_MODEL.md`
  - `docs/release/DIST_BUNDLE_ASSEMBLY.md`
  - `docs/release/DIST_VERIFICATION_RULES.md`
  - `docs/release/RELEASE_INDEX_RESOLUTION_POLICY.md`
  - `docs/release/ARCHIVE_AND_RETENTION_POLICY.md`
  - `docs/release/OFFLINE_ARCHIVE_MODEL_v0_0_0.md`
- Governing registries:
  - `data/registries/component_graph_registry.json`
  - `data/registries/install_profile_registry.json`
  - `data/registries/release_resolution_policy_registry.json`
  - `data/registries/archive_policy_registry.json`
  - `data/registries/trust_root_registry.json`
  - `data/registries/migration_policy_registry.json`
  - `data/governance/governance_profile.json`
- Ω baselines and reports:
  - worldgen lock
  - baseline universe
  - gameplay loop
  - disaster suite
  - ecosystem verify
  - update simulation
  - trust strict suite
  - offline archive verify
  - toolchain matrix baseline

## A) Preconditions

All of the following must pass before Ω-11 signoff is accepted:

- `CONVERGENCE-GATE-0`
  - `python tools/convergence/tool_run_convergence_gate.py --repo-root . --skip-cross-platform --prefer-cached-heavy`
- `ARCH-AUDIT-2`
  - `python tools/audit/tool_run_arch_audit.py --repo-root .`
- WORLDGEN-LOCK verify
  - `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- BASELINE-UNIVERSE verify
  - `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- MVP-GAMEPLAY verify
  - `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- DISASTER suite pass
  - `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- ECOSYSTEM verify pass
  - `python tools/mvp/tool_verify_ecosystem.py --repo-root .`
- UPDATE simulation pass
  - `python tools/mvp/tool_run_update_sim.py --repo-root .`
- TRUST strict suite pass when strict publication policy is exercised
  - `python tools/security/tool_run_trust_strict_suite.py --repo-root .`
- STORE verify pass on the assembled authoritative release bundle
  - `python tools/setup/setup_cli.py packs verify --root dist/v0.0.0-mock/win64/dominium`
- PERFORMANCE baseline capture retained and current
  - `python tools/perf/tool_run_performance_envelope.py --repo-root . --platform-tag win64`
  - retained supporting baseline: `docs/audit/performance/PERFORMX_BASELINE.json`

## B) Target Selection

Ω-11 packages Tier-1 targets only.

Frozen target set from ARCH-MATRIX-0:

- `target.os_winnt.abi_msvc.arch_x86_64`
- `target.os_linux.abi_glibc.arch_x86_64`

Execution policy for `v0.0.0-mock`:

- `win64` is the authoritative release-anchor target because it is the committed Tier-1 reference lane already exercised by DIST, Ω-8, and Ω-9.
- Additional Tier-1 targets may be packaged only when the required build environment exists at Ω-11 time and the same gates pass there.
- No Tier-2 or Tier-3 targets are eligible for the mock release package set.

Profiles to package:

- `install.profile.full`
- `install.profile.server`
- `install.profile.tools`

## C) Bundle Composition Rules

Every bundle must be derived from:

- component graph
- install profile
- target filters
- trust policy

The plan must not hardcode bundle file lists outside those surfaces.

Profile-to-bundle mapping:

- `install.profile.full`
  - authoritative release-anchor bundle
  - staging root: `dist/v0.0.0-mock/win64/dominium`
- `install.profile.server`
  - derivative server bundle
  - staging root: `build/dist.final/server/v0.0.0-mock/win64/dominium`
- `install.profile.tools`
  - derivative tools bundle
  - staging root: `build/dist.final/tools/v0.0.0-mock/win64/dominium`

Global include rules:

- include:
  - `install.manifest.json`
  - `manifests/release_manifest.json`
  - `manifests/release_index.json`
  - `manifests/filelist.txt`
  - trust registries required by the selected trust policy
  - governance profile and contract-pin surfaces required by the assembled bundle
  - default instance / pack lock / profile bundle surfaces required by the selected install profile

Global exclude rules:

- exclude:
  - tests
  - repo-only dev artifacts
  - scratch outputs
  - temporary logs
  - `.git`
  - non-runtime XStack governance/dev surfaces

Profile-specific selector intent:

- `install.profile.full` includes runtime client/game/server/setup/launcher plus default instance and release notes.
- `install.profile.server` excludes rendered client/game runtime surfaces unless they are required transitively by the component graph for lawful verification.
- `install.profile.tools` excludes client/game/server runtime surfaces unless they are required transitively by the component graph for lawful offline tooling.

## D) Packaging Steps (Ordered)

### 1. Assemble Tree

Run the deterministic assembly tool once per packaged profile:

- full:
  - `python tools/dist/tool_assemble_dist_tree.py --repo-root . --platform-tag win64 --channel mock --install-profile-id install.profile.full --output-root dist`
- server:
  - `python tools/dist/tool_assemble_dist_tree.py --repo-root . --platform-tag win64 --channel mock --install-profile-id install.profile.server --output-root build/dist.final/server`
- tools:
  - `python tools/dist/tool_assemble_dist_tree.py --repo-root . --platform-tag win64 --channel mock --install-profile-id install.profile.tools --output-root build/dist.final/tools`

### 2. Verify Dist

Run DIST-2 verification against each assembled tree:

- full:
  - `python tools/dist/tool_verify_distribution.py --repo-root . --platform-tag win64 --dist-root dist`
- server:
  - `python tools/dist/tool_verify_distribution.py --repo-root . --platform-tag win64 --dist-root build/dist.final/server`
- tools:
  - `python tools/dist/tool_verify_distribution.py --repo-root . --platform-tag win64 --dist-root build/dist.final/tools`

### 3. Clean Room Test

Run the clean-room harness against the authoritative full bundle:

- `python tools/dist/tool_run_clean_room.py --repo-root . --dist-root dist --platform-tag win64 --mode-policy cli`

### 4. Platform Matrix Test

Run the DIST-4 matrix where target environments are available:

- authoritative baseline lane:
  - `python tools/dist/tool_run_platform_matrix.py --repo-root . --dist-spec win64=dist/v0.0.0-mock/win64/dominium --channel mock`
- additional Tier-1 lanes are appended with more `--dist-spec <platform_tag>=<bundle_root>` entries only after those bundles exist and their environments are available.

### 5. Interop Test

Run the DIST-6 interop lane against the authoritative release bundle and any available peer Tier-1 build:

- baseline same-build lane:
  - `python tools/dist/tool_run_version_interop.py --repo-root . --dist-root-a dist --dist-root-b dist --platform-tag-a win64 --platform-tag-b win64 --channel mock`
- additional Tier-1 comparisons repeat the same command with the second bundle root and platform tag adjusted to the available peer bundle.

### 6. Build Deterministic Publication Archive

Build the publication archive tree and release-history snapshot from the authoritative full bundle:

- `python tools/release/tool_run_archive_policy.py --repo-root . --platform-tag win64`

This emits the publication archive root under:

- `build/tmp/archive_policy_dist/v0.0.0-mock/win64/archive`

### 7. Verify Archive Unpack

Verify the offline reconstruction archive retained for extinction prevention:

- build:
  - `python tools/release/tool_build_offline_archive.py --repo-root . --release-id v0.0.0-mock --dist-root dist/v0.0.0-mock/win64/dominium`
- verify:
  - `python tools/release/tool_verify_offline_archive.py --repo-root . --archive-path build/offline_archive/dominium-archive-v0.0.0-mock.tar.gz`

### 8. Create `archive_record`

The publication archive run in step 6 writes:

- `build/tmp/archive_policy_dist/v0.0.0-mock/win64/archive/archive_record.json`

The offline reconstruction archive build in step 7 stages:

- `build/tmp/omega8_offline_archive/staging/v0.0.0-mock/archive_record.json`

The two archive records serve different purposes and must not be conflated:

- publication archive record:
  - release-manifest / release-index / history / mirror retention record
- offline reconstruction record:
  - extinction-prevention bundle content projection and retained governance/baseline record

### 9. Emit Release Index And History Entry

The authoritative release-index emission point is the full bundle:

- current index:
  - `dist/v0.0.0-mock/win64/dominium/manifests/release_index.json`
- retained history snapshot:
  - `build/tmp/archive_policy_dist/v0.0.0-mock/win64/archive/manifests/release_index_history/mock/v0.0.0-mock.json`

History rules:

- append-only
- no overwrite of prior retained snapshots
- `yanked` state recorded explicitly in release-index descriptors
- `policy.latest_compatible` must exclude yanked builds

## Trust Policy And Yanked Build Behavior

- Assembly and baseline verification may use `trust.default_mock`.
- Any strict publication rehearsal must rerun the trust gate under `trust.strict_ranked`.
- `trust.strict_ranked` requires signatures for:
  - `release_index`
  - `release_manifest`
  - official packs
- `trust.default_mock` keeps hashes mandatory and treats missing signatures as warnings, not silent acceptance.
- `policy.exact_suite` is the release-anchor install/update policy for the frozen suite snapshot.
- `policy.latest_compatible` is used only for update-planning verification and must exclude yanked candidates deterministically.
- No silent upgrade, silent downgrade, or silent fallback is permitted.

## E) Artifact Outputs

The Ω-11 signoff must record hashes for all of the following:

- release-anchor full bundle root:
  - `dist/v0.0.0-mock/win64/dominium`
- server bundle root:
  - `build/dist.final/server/v0.0.0-mock/win64/dominium`
- tools bundle root:
  - `build/dist.final/tools/v0.0.0-mock/win64/dominium`
- release manifest hash:
  - `dist/v0.0.0-mock/win64/dominium/manifests/release_manifest.json`
- release index hash:
  - `dist/v0.0.0-mock/win64/dominium/manifests/release_index.json`
- publication archive record hash:
  - `build/tmp/archive_policy_dist/v0.0.0-mock/win64/archive/archive_record.json`
- publication retained history hash:
  - `build/tmp/archive_policy_dist/v0.0.0-mock/win64/archive/manifests/release_index_history/mock/v0.0.0-mock.json`
- publication archive bundle hash:
  - `build/tmp/archive_policy_dist/v0.0.0-mock/win64/archive/dominium-archive-v0.0.0-mock.tar.gz`
- offline reconstruction archive bundle hash:
  - `build/offline_archive/dominium-archive-v0.0.0-mock.tar.gz`
- baseline Ω artifact hashes:
  - worldgen lock snapshot
  - baseline universe snapshot
  - gameplay loop snapshot
  - disaster suite baseline
  - ecosystem verify baseline
  - update simulation baseline
  - trust strict baseline
  - archive baseline
  - toolchain run manifest and hashes

## F) Publishing Steps (Mock)

Mock publication is file emission only.
No network publication is part of Ω-10 or Ω-11.

Publishing sequence:

- write `manifests/release_index.json` in the authoritative full bundle
- retain `release_index_history/mock/v0.0.0-mock.json` in the publication archive root
- produce `archive_record.json`
- retain the offline reconstruction archive bundle
- write `data/release/final_dist_signoff.json`
- write the human signoff document referenced by that JSON signoff

## G) Manual Polish Window

After Ω-11 only the following are allowed:

- UI text edits
- docs improvements
- cosmetic adjustments

The following remain frozen:

- worldgen lock
- contract registry contents
- migration rules
- component graph structure
- trust policy behavior

Required reruns after manual polish:

- `python tools/convergence/tool_run_convergence_gate.py --repo-root . --skip-cross-platform --prefer-cached-heavy`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/release/tool_dist_final_dryrun.py --repo-root .`
- if bundle contents changed:
  - rerun DIST-2 verification
  - rerun clean-room verification
  - rerun archive policy / offline archive verification
