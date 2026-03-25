Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none
Stability: stable
Future Series: OMEGA
Replacement Target: Ω-11 execution ledger and final mock signoff

# DIST Final Checklist

## Preconditions

- [ ] Run `python tools/convergence/tool_run_convergence_gate.py --repo-root . --skip-cross-platform --prefer-cached-heavy`
  Expected outputs: convergence report under `docs/audit/convergence_steps/`
  Pass criteria: result `complete`
- [ ] Run `python tools/audit/tool_run_arch_audit.py --repo-root .`
  Expected outputs: `docs/audit/ARCH_AUDIT_REPORT.md`, `data/audit/arch_audit_report.json`
  Pass criteria: result `complete`
- [ ] Run `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
  Expected outputs: `docs/audit/WORLDGEN_LOCK_VERIFY.md`, `data/audit/worldgen_lock_verify.json`
  Pass criteria: result `complete`
- [ ] Run `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
  Expected outputs: `docs/audit/BASELINE_UNIVERSE_VERIFY.md`, `data/audit/baseline_universe_verify.json`
  Pass criteria: result `complete`
- [ ] Run `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
  Expected outputs: `docs/audit/MVP_GAMEPLAY_VERIFY.md`, `data/audit/gameplay_verify.json`
  Pass criteria: result `complete`
- [ ] Run `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
  Expected outputs: `docs/audit/DISASTER_SUITE_RUN.md`, `data/audit/disaster_suite_run.json`
  Pass criteria: result `complete`
- [ ] Run `python tools/mvp/tool_verify_ecosystem.py --repo-root .`
  Expected outputs: `docs/audit/ECOSYSTEM_VERIFY_RUN.md`, `data/audit/ecosystem_verify_run.json`
  Pass criteria: result `complete`
- [ ] Run `python tools/mvp/tool_run_update_sim.py --repo-root .`
  Expected outputs: `docs/audit/UPDATE_SIM_RUN.md`, `data/audit/update_sim_run.json`
  Pass criteria: result `complete`
- [ ] Run `python tools/security/tool_run_trust_strict_suite.py --repo-root .`
  Expected outputs: `docs/audit/TRUST_STRICT_SUITE_RUN.md`, `data/audit/trust_strict_run.json`
  Pass criteria: result `complete`
- [ ] Run `python tools/perf/tool_run_performance_envelope.py --repo-root . --platform-tag win64`
  Expected outputs: `docs/audit/PERFORMANCE_ENVELOPE_BASELINE.md`
  Pass criteria: result `complete`

## Bundle Assembly

- [ ] Assemble the authoritative full bundle with `python tools/dist/tool_assemble_dist_tree.py --repo-root . --platform-tag win64 --channel mock --install-profile-id install.profile.full --output-root dist`
  Expected outputs: `dist/v0.0.0-mock/win64/dominium`
  Pass criteria: `install.manifest.json`, `manifests/release_manifest.json`, and `manifests/release_index.json` present
- [ ] Assemble the server bundle with `python tools/dist/tool_assemble_dist_tree.py --repo-root . --platform-tag win64 --channel mock --install-profile-id install.profile.server --output-root build/dist.final/server`
  Expected outputs: `build/dist.final/server/v0.0.0-mock/win64/dominium`
  Pass criteria: bundle root present and profile-specific manifest generated
- [ ] Assemble the tools bundle with `python tools/dist/tool_assemble_dist_tree.py --repo-root . --platform-tag win64 --channel mock --install-profile-id install.profile.tools --output-root build/dist.final/tools`
  Expected outputs: `build/dist.final/tools/v0.0.0-mock/win64/dominium`
  Pass criteria: bundle root present and profile-specific manifest generated

## Verification

- [ ] Verify the full bundle with `python tools/dist/tool_verify_distribution.py --repo-root . --platform-tag win64 --dist-root dist`
  Expected outputs: `docs/audit/DIST_VERIFY_win64.md`
  Pass criteria: result `complete`
- [ ] Verify the server bundle with `python tools/dist/tool_verify_distribution.py --repo-root . --platform-tag win64 --dist-root build/dist.final/server`
  Expected outputs: distribution verify report for the server staging root
  Pass criteria: result `complete`
- [ ] Verify the tools bundle with `python tools/dist/tool_verify_distribution.py --repo-root . --platform-tag win64 --dist-root build/dist.final/tools`
  Expected outputs: distribution verify report for the tools staging root
  Pass criteria: result `complete`
- [ ] Run store verification with `python tools/setup/setup_cli.py packs verify --root dist/v0.0.0-mock/win64/dominium`
  Expected outputs: offline verification result on stdout or bundle-local logs
  Pass criteria: no refusal, no contract drift
- [ ] Run clean-room verification with `python tools/dist/tool_run_clean_room.py --repo-root . --dist-root dist --platform-tag win64 --mode-policy cli`
  Expected outputs: `data/audit/clean_room_win64.json`, `docs/audit/CLEAN_ROOM_TEST_FINAL.md`
  Pass criteria: result `complete`
- [ ] Run the platform matrix with `python tools/dist/tool_run_platform_matrix.py --repo-root . --dist-spec win64=dist/v0.0.0-mock/win64/dominium --channel mock`
  Expected outputs: `docs/audit/DIST_PLATFORM_MATRIX_REPORT.md`, `docs/audit/DIST4_FINAL.md`
  Pass criteria: result `complete`
- [ ] Run the interop lane with `python tools/dist/tool_run_version_interop.py --repo-root . --dist-root-a dist --dist-root-b dist --platform-tag-a win64 --platform-tag-b win64 --channel mock`
  Expected outputs: `docs/audit/DIST6_FINAL.md`
  Pass criteria: result `complete`

## Archive And Publication

- [ ] Run publication archive generation with `python tools/release/tool_run_archive_policy.py --repo-root . --platform-tag win64`
  Expected outputs: `build/tmp/archive_policy_dist/v0.0.0-mock/win64/archive/archive_record.json`
  Pass criteria: archive record, retained history snapshot, and archive bundle present
- [ ] Build the offline reconstruction archive with `python tools/release/tool_build_offline_archive.py --repo-root . --release-id v0.0.0-mock --dist-root dist/v0.0.0-mock/win64/dominium`
  Expected outputs: `build/offline_archive/dominium-archive-v0.0.0-mock.tar.gz`
  Pass criteria: bundle written and hash recorded
- [ ] Verify the offline reconstruction archive with `python tools/release/tool_verify_offline_archive.py --repo-root . --archive-path build/offline_archive/dominium-archive-v0.0.0-mock.tar.gz`
  Expected outputs: `docs/audit/OFFLINE_ARCHIVE_VERIFY.md`, `data/audit/offline_archive_verify.json`
  Pass criteria: result `complete`

## Signoff

- [ ] Run `python tools/release/tool_dist_final_dryrun.py --repo-root .`
  Expected outputs: `docs/audit/DIST_FINAL_DRYRUN.md`
  Pass criteria: result `complete`
- [ ] Write `data/release/final_dist_signoff.json`
  Expected outputs: final machine-readable release signoff
  Pass criteria: every expected artifact path present and every hash populated
- [ ] Write the human signoff document referenced by the final signoff JSON
  Expected outputs: release signoff note in the selected publication folder
  Pass criteria: references release manifest hash, release index hash, archive hash, offline archive hash, and Ω baseline hashes
