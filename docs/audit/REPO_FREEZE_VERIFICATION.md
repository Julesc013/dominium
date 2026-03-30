Status: DERIVED
Last Reviewed: 2026-03-30
Stability: stable
Future Series: XI-8
Replacement Target: superseded by a later explicit repository-freeze verification refresh

# Repo Freeze Verification

- XStack CI STRICT: `complete`
- trust strict suite: `complete`
- dist verify: `complete`
- archive verify: `complete`
- Xi-8 targeted TestX: `pass`

## Commands

- `python -B tools/xstack/ci/xstack_ci_entrypoint.py --repo-root . --profile STRICT --testx-subset test_ci_entrypoint_deterministic_order,test_ci_profiles_exist,test_gate_definitions_valid,test_ci_report_failures_propagate,test_repository_structure_lock_valid,test_no_prohibited_dirs_present`
- `python -B tools/security/tool_run_trust_strict_suite.py --repo-root .`
- `python -B tools/dist/tool_assemble_dist_tree.py --repo-root . --platform-tag win64 --channel mock --output-root dist`
- `python -B tools/dist/tool_verify_distribution.py --repo-root . --platform-tag win64 --dist-root dist`
- `python -B tools/release/tool_archive_release.py --repo-root . --dist-root dist/v0.0.0-mock/win64/dominium --platform-tag win64 --write-offline-bundle`
- `python -B tools/release/tool_verify_archive.py --repo-root . --dist-root dist/v0.0.0-mock/win64/dominium --platform-tag win64 --archive-record-path dist/v0.0.0-mock/win64/archive/archive_record.json`
- `python -B tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_repository_structure_lock_valid,test_no_prohibited_dirs_present,test_xstack_ci_strict_passes`

## Fingerprints

- CI STRICT: `eef85dde0a8c2f42c7ffd300724dd97dde093602685ccef08f2b8816ca263c59`
- trust strict: `de3398e27089e058f1ce1a2796ed4907fc0e91addc4c60b948a6666b1c80e6a3`
- dist refresh: ``
- dist verify: `0693d807a43fba8611bc57fd48bf3ae92476b95e6bbce385f9cab4acd1e44b20`
- archive release: ``
- archive verify: `f449d01ef3a983b9ace76ee5570e9d324ffdd42c40ee0f3197e132e208046a9d`
