# Setup Conformance Suite

The conformance suite is required for release gating.

## Runner
Executable: `setup_conformance_runner`

Required flags:
- `--sandbox-root <dir>`
- `--fixtures-root <dir>`
- `--deterministic 1`
- `--out-json <file>`

Example:
```
setup_conformance_runner --sandbox-root build/msvc-debug/source/tests/setup_conformance --fixtures-root tests/setup/fixtures --deterministic 1 --out-json build/msvc-debug/source/tests/setup_conformance/conformance_summary.json
```

Wrapper scripts:
- `scripts/setup/run_conformance.bat`
- `scripts/setup/run_conformance.sh`

## Repeatability check
- `ctest -R setup_conformance_repeat` runs the suite twice and compares outputs.

## Required Cases
- `fresh_install_portable`
- `crash_during_staging_resume`
- `crash_during_commit_rollback`
- `crash_during_commit_resume`
- `repair_fixes_corruption`
- `uninstall_leaves_only_documented_residue`
- `upgrade_preserves_user_data_and_can_rollback`
- `offline_install_works`
- `determinism_repeatability`

## Artifacts
Each case writes artifacts under the sandbox root:
- `out/plan.tlv`
- `out/state.tlv`
- `out/audit.tlv`
- `out/journal.tlv`
- `out/journal.tlv.txn.tlv`
