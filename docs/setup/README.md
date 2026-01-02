# Setup Documentation Index

This directory is the authoritative reference for the Setup kernel/services/frontends refactor.
Setup is the default installer system; legacy setup remains buildable behind explicit flags.
Legacy documentation lives in `docs/setup_legacy/`.
Setup is a long-lived, governed system with deterministic behavior and audited evolution.

## Quick Commands
- Conformance: `scripts/setup/run_conformance.bat` or `scripts/setup/run_conformance.sh`
- Release gate: `scripts/release/run_setup_release_gate.bat` or `scripts/release/run_setup_release_gate.sh`
- Doc lint: `scripts/setup/doc_lint.bat` or `scripts/setup/doc_lint.sh`

## Architecture and Rules
- `docs/setup/INVARIANTS.md`: layering, prohibitions, required properties.
- `docs/setup/BUILD_RULES.md`: kernel purity rules and enforcement.
- `docs/setup/SECURITY_MODEL.md`: trust boundaries and sandbox rules.
- `docs/setup/DEFAULTS_AND_FLAGS.md`: default selection and build flags.

## Contracts and Schemas (TLV)
- `docs/setup/TLV_INSTALL_MANIFEST.md`
- `docs/setup/TLV_INSTALL_REQUEST.md`
- `docs/setup/TLV_INSTALL_PLAN.md`
- `docs/setup/TLV_INSTALLED_STATE.md`
- `docs/setup/TLV_SETUP_AUDIT.md`
- `docs/setup/TLV_JOB_JOURNAL.md`
- `docs/setup/TLV_TXN_JOURNAL.md`
- `docs/setup/SCHEMA_FREEZE_V1.md`

## Planning and Execution
- `docs/setup/PLANNING_RULES.md`
- `docs/setup/JOB_ENGINE.md`
- `docs/setup/TRANSACTIONS.md`
- `docs/setup/RECOVERY_PLAYBOOK.md`
- `docs/setup/FAILPOINTS.md`

## Services, SPLAT, and Errors
- `docs/setup/SERVICES_FACADES.md`
- `docs/setup/SERVICES_ERRORS.md`
- `docs/setup/ERROR_TAXONOMY.md`
- `docs/setup/SPLAT_REGISTRY.md`
- `docs/setup/SPLAT_SELECTION_RULES.md`

## Frontends and CLI
- `docs/setup/FRONTEND_CONTRACT.md`
- `docs/setup/CLI_REFERENCE.md`
- `docs/setup/CLI_JSON_SCHEMAS.md`
- `docs/setup/TUI_REFERENCE.md`
- `docs/setup/OPERATOR_TOOLS.md`

## Adapters and Ownership
- `docs/setup/ADAPTERS.md`
- `docs/setup/ADAPTER_MATRIX.md`
- `docs/setup/OWNERSHIP_MODEL.md`
- `docs/setup/WINDOWS_MSI_WRAPPER.md`
- `docs/setup/MACOS_PKG_WRAPPER.md`
- `docs/setup/LINUX_DEB_WRAPPER.md`
- `docs/setup/LINUX_RPM_WRAPPER.md`
- `docs/setup/STEAM_PROVIDER.md`

## Validation and Operations
- `docs/setup/CONFORMANCE.md`
- `docs/setup/TROUBLESHOOTING.md`
- `docs/setup/REPRODUCIBLE_BUILDS.md`
- `docs/setup/REPRODUCIBILITY_GUARANTEES.md`
- `docs/setup/PARITY_LOCK_MATRIX.md`
- `docs/setup/ARCHIVAL_AND_HANDOFF.md`

## Roadmap
- `docs/setup/DEPRECATION_PLAN.md`
- `docs/setup/LEGACY_STATE_IMPORT.md`
- `docs/setup/PACKAGING_DEFAULTS.md`
- `docs/setup/STATUS_SR1.md` .. `docs/setup/STATUS_SR11.md`

## Maintenance and Extensions
- `docs/setup/EXTENSION_POLICY.md`
- `docs/setup/ADDING_FEATURES.md`
- `docs/setup/STATE_EVOLUTION.md`
- `docs/setup/SPLAT_LIFECYCLE.md`
- `docs/setup/PARITY_WITH_LAUNCHER.md`
- `docs/setup/PARITY_LOCK_MATRIX.md`

## Deferred Work (Non-Binding)
- `docs/setup/FUTURE_BACKLOG.md`
- Setup is complete without these items.

## Read-Only Status
- `docs/setup/READ_ONLY_LOCK.md`
- `docs/setup/SCHEMA_FREEZE_V1.md`
- `docs/setup/PARITY_LOCK_MATRIX.md`

## Handoff Snapshot
- `docs/setup/HANDOFF_SNAPSHOT.md`
- `docs/setup/OPERATIONS_QUICKSTART.md`

## How to Start v2 (If Ever)
- Setup v1 is frozen; changes require a new ladder starting at SR-0.
- See `docs/setup/READ_ONLY_LOCK.md` for criteria and approvals.
