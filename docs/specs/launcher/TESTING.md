# Launcher Testing and Troubleshooting

Doc Version: 1

This document describes how to run the launcher test suite (including headless end-to-end flows) and how to interpret failures using run artifacts.

## 1) Running Tests

### 1.1 Recommended Headless Configuration

The launcher must run under:
- `--ui=null`
- `--gfx=null`

In CI this corresponds to building with the null backend enabled (see `.github/workflows/ci.yml`).

### 1.2 Core + E2E Tests (CTest)

From a configured build directory:

- Run all launcher tests:
  - `ctest --test-dir build/<config> --output-on-failure -R dominium_launcher_`
- Run headless control-plane E2E tests only:
  - `ctest --test-dir build/<config> --output-on-failure -R dominium_launcher_control_plane_tests`
- Run installed-state smoke test only:
  - `ctest --test-dir build/<config> --output-on-failure -R dominium_launcher_state_smoke_tests`

Key test groups:
- `dominium_launcher_control_plane_tests`: headless control-plane E2E flows (instance lifecycle, tool launch, pack determinism, offline refusal, safe mode).
- `dominium_launcher_tlv_migrations_tests`: TLV migration/round-trip behavior.
- `dominium_launcher_handshake_tests`: handshake encode/decode + validation invariants.
- `dominium_launcher_tools_registry_tests`: tools registry schema and determinism.
- `dominium_launcher_state_smoke_tests`: builds a minimal DSU install and validates `--smoke-test` against installed-state.

Manual smoke (installed-state only):
- `dominium-launcher --smoke-test --state <install_root>/.dsu/installed_state.dsustate`

## 2) Where to Find Run Artifacts

Every launch attempt (including refusals) creates:

`<state_root>/instances/<instance_id>/logs/runs/<run_dir_id>/`

Files (stable names):
- `handshake.tlv`
- `launch_config.tlv`
- `selection_summary.tlv`
- `exit_status.tlv`
- `audit_ref.tlv`

For the schema details of these files, see `docs/launcher/ECOSYSTEM_INTEGRATION.md`.

### 2.1 Quick CLI to Inspect the Last Run

- Print the last run audit and selection summary:
  - `dominium-launcher --ui=null --gfx=null --home=<state_root> audit-last <instance_id>`

The output includes `run_dir_id`, `audit_path`, and `selection_summary_path`.

## 3) Interpreting Refusals

Launch refusals are explicit, stable, and audited:
- `refused=1` in `launch` output
- `refusal_code=<u32>`
- `refusal_detail=<text>`

Refusal codes are enumerated in `docs/launcher/ECOSYSTEM_INTEGRATION.md`.

For `refusal_code=5` (prelaunch validation failed), the `refusal_detail` begins with:
- `prelaunch_validation_failed`

And may include:
- `code=<failure_code>`
- `detail=<failure_detail>`

### 3.1 Common Next Steps

When diagnosing a refusal, inspect:
- `audit_ref.tlv` (reasons include refusal code/detail, handshake path, selection summary path)
- `selection_summary.tlv` (offline mode / safe mode flags + resolved packs summary)
- `handshake.tlv` (resolved packs list and pins)
- `launch_config.tlv` (effective resolved launch configuration)
- `exit_status.tlv` (termination type, timestamps, exit code)

## 4) Troubleshooting Checklist

- **Selection visibility**: `audit-last` prints `selection_summary.line` and a stable `selection_summary.*` dump; the UI status bar uses the same source (`selection_summary.tlv`).
- **Determinism**: rerun the same inputs and compare `selection_summary.manifest_sha256_short` and `selection_summary.packs.resolved.order`.
- **Offline enforcement**: when offline mode is active, operations requiring network must refuse explicitly and emit audit reasons.
- **Safe mode**: safe mode must appear in both `handshake.tlv` (pack safe-mode flags) and `selection_summary.tlv` (`safe_mode=1`).

## Related Docs

- `docs/launcher/CLI.md`
- `docs/launcher/ARCHITECTURE.md`
- `docs/launcher/ECOSYSTEM_INTEGRATION.md`
