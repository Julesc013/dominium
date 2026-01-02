# Setup2 Documentation Index

This directory is the authoritative reference for the Setup2 kernel/services/frontends refactor.
Setup2 is the default installer system; legacy setup remains buildable behind explicit flags.
Setup2 is a long-lived, governed system with deterministic behavior and audited evolution.

## Quick Commands
- Conformance: `scripts/setup2/run_conformance.bat` or `scripts/setup2/run_conformance.sh`
- Release gate: `scripts/release/run_setup2_release_gate.bat` or `scripts/release/run_setup2_release_gate.sh`
- Doc lint: `scripts/setup2/doc_lint.bat` or `scripts/setup2/doc_lint.sh`

## Architecture and Rules
- `docs/setup2/INVARIANTS.md`: layering, prohibitions, required properties.
- `docs/setup2/BUILD_RULES.md`: kernel purity rules and enforcement.
- `docs/setup2/SECURITY_MODEL.md`: trust boundaries and sandbox rules.
- `docs/setup2/DEFAULTS_AND_FLAGS.md`: default selection and build flags.

## Contracts and Schemas (TLV)
- `docs/setup2/TLV_INSTALL_MANIFEST.md`
- `docs/setup2/TLV_INSTALL_REQUEST.md`
- `docs/setup2/TLV_INSTALL_PLAN.md`
- `docs/setup2/TLV_INSTALLED_STATE.md`
- `docs/setup2/TLV_SETUP_AUDIT.md`
- `docs/setup2/TLV_JOB_JOURNAL.md`
- `docs/setup2/TLV_TXN_JOURNAL.md`
- `docs/setup2/SCHEMA_FREEZE_V1.md`

## Planning and Execution
- `docs/setup2/PLANNING_RULES.md`
- `docs/setup2/JOB_ENGINE.md`
- `docs/setup2/TRANSACTIONS.md`
- `docs/setup2/RECOVERY_PLAYBOOK.md`
- `docs/setup2/FAILPOINTS.md`

## Services, SPLAT, and Errors
- `docs/setup2/SERVICES_FACADES.md`
- `docs/setup2/SERVICES_ERRORS.md`
- `docs/setup2/ERROR_TAXONOMY.md`
- `docs/setup2/SPLAT_REGISTRY.md`
- `docs/setup2/SPLAT_SELECTION_RULES.md`

## Frontends and CLI
- `docs/setup2/FRONTEND_CONTRACT.md`
- `docs/setup2/CLI_REFERENCE.md`
- `docs/setup2/CLI_JSON_SCHEMAS.md`
- `docs/setup2/TUI_REFERENCE.md`
- `docs/setup2/OPERATOR_TOOLS.md`

## Adapters and Ownership
- `docs/setup2/ADAPTERS.md`
- `docs/setup2/ADAPTER_MATRIX.md`
- `docs/setup2/OWNERSHIP_MODEL.md`
- `docs/setup2/WINDOWS_MSI_WRAPPER.md`
- `docs/setup2/MACOS_PKG_WRAPPER.md`
- `docs/setup2/LINUX_DEB_WRAPPER.md`
- `docs/setup2/LINUX_RPM_WRAPPER.md`
- `docs/setup2/STEAM_PROVIDER.md`

## Validation and Operations
- `docs/setup2/CONFORMANCE.md`
- `docs/setup2/TROUBLESHOOTING.md`
- `docs/setup2/REPRODUCIBLE_BUILDS.md`
- `docs/setup2/REPRODUCIBILITY_GUARANTEES.md`
- `docs/setup2/PARITY_LOCK_MATRIX.md`
- `docs/setup2/ARCHIVAL_AND_HANDOFF.md`

## Roadmap
- `docs/setup2/DEPRECATION_PLAN.md`
- `docs/setup2/LEGACY_STATE_IMPORT.md`
- `docs/setup2/PACKAGING_DEFAULTS.md`
- `docs/setup2/STATUS_SR1.md` .. `docs/setup2/STATUS_SR11.md`

## Maintenance and Extensions
- `docs/setup2/EXTENSION_POLICY.md`
- `docs/setup2/ADDING_FEATURES.md`
- `docs/setup2/STATE_EVOLUTION.md`
- `docs/setup2/SPLAT_LIFECYCLE.md`
- `docs/setup2/PARITY_WITH_LAUNCHER.md`
- `docs/setup2/PARITY_LOCK_MATRIX.md`

## Deferred Work (Non-Binding)
- `docs/setup2/FUTURE_BACKLOG.md`
- Setup2 is complete without these items.
