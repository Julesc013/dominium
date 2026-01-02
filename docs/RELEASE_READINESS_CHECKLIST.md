# Release Readiness Checklist

This checklist is the definitive gate for R-1..R-8 readiness. Scripts and CI
should reference this document.

## Layering Invariants (R-1)

- [ ] Kernel targets compile without OS/UI headers visible.
- [ ] `scripts/check_layers.py` passes (no forbidden includes in kernel).
- [ ] Kernel targets link only core libs (no platform backends).
- [ ] Layered targets are split: kernel / services / providers / frontends / platform.

## Required Binaries / Entry Points

- [ ] `dominium-launcher` supports `--front=gui|tui|cli` and `--ui=native|dgfx|null`.
- [ ] `dominium-setup-legacy` exists (legacy setup) and `dominium-setup` (setup CLI) builds.
- [ ] `tool_manifest_inspector` (or equivalent tool) builds and runs via launcher.

## TLV Schemas (Governance + Vectors)

Each schema must have: schema_id, version, validator, migration hook, vectors.

- [ ] instance_manifest (launcher)
- [ ] pack_manifest (launcher)
- [ ] launcher_handshake
- [ ] launcher_audit
- [ ] selection_summary
- [ ] installed_state (setup)
- [ ] core_job_def / core_job_state
- [ ] diagnostics bundle meta/index
- [ ] caps snapshot
- [ ] tools_registry

## Required Commands (CLI)

- [ ] `dominium-launcher` headless: `--front=cli --ui=null --gfx=null`
- [ ] `dominium-launcher --smoke-test` (state contract)
- [ ] `dominium-launcher caps --format=tlv|text`
- [ ] `dominium-launcher diag-bundle <instance_id> --out=<path>`
- [ ] `dominium-setup` plan/apply (installed_state.tlv output)

## Required Tests

- [ ] Layer checks target (`dominium_layer_checks`) passes.
- [ ] Kernel smoke tests: `launcher_kernel_smoke`, `setup_kernel_smoke`.
- [ ] Contract tests: `dominium_contract_tests`.
- [ ] TLV fuzz harness: `dominium_tlv_fuzz_tests`.
- [ ] E2E headless flows (see tests/headless).
- [ ] UI/TUI smoke tests (non-interactive).

## Required Run Artifacts

Per launcher run directory (`instances/<id>/logs/runs/<run_id>/`):

- [ ] `handshake.tlv`
- [ ] `selection_summary.tlv`
- [ ] `launch_config.tlv`
- [ ] `exit_status.tlv`
- [ ] `audit_ref.tlv`

## Scripts (Deterministic Runners)

- [ ] `scripts/build_all.bat` builds all required targets.
- [ ] `scripts/test_all.bat` runs layer checks + tests (unit/contract/fuzz).
- [ ] `scripts/test_headless.bat` runs E2E headless flows.
- [ ] `scripts/verify_release.bat` runs full build + test + E2E and reports PASS/FAIL.

## Documentation Consistency

- [ ] Core docs reflect shared modules (TLV, err_t, log, job, caps/solver, providers).
- [ ] Launcher docs reflect run artifacts and selection summary rules.
- [ ] Setup/setup docs reflect installed_state schema and CLI outputs.
- [ ] This checklist matches scripts and actual binaries.
