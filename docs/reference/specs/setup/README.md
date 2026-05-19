Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

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
- `docs/reference/specs/setup/INVARIANTS.md`: layering, prohibitions, required properties.
- `docs/apps/setup/BUILD_RULES.md`: kernel purity rules and enforcement.
- `docs/apps/setup/SECURITY_MODEL.md`: trust boundaries and sandbox rules.
- `docs/apps/setup/DEFAULTS_AND_FLAGS.md`: default selection and build flags.

## Contracts and Schemas (TLV)
- `docs/apps/setup/TLV_INSTALL_MANIFEST.md`
- `docs/apps/setup/TLV_INSTALL_REQUEST.md`
- `docs/apps/setup/TLV_INSTALL_PLAN.md`
- `docs/apps/setup/TLV_INSTALLED_STATE.md`
- `docs/apps/setup/TLV_SETUP_AUDIT.md`
- `docs/apps/setup/TLV_JOB_JOURNAL.md`
- `docs/apps/setup/TLV_TXN_JOURNAL.md`
- `docs/apps/setup/SCHEMA_FREEZE_V1.md`

## Planning and Execution
- `docs/apps/setup/PLANNING_RULES.md`
- `docs/reference/specs/setup/JOB_ENGINE.md`
- `docs/apps/setup/TRANSACTIONS.md`
- `docs/apps/setup/RECOVERY_PLAYBOOK.md`
- `docs/apps/setup/FAILPOINTS.md`

## Services, SPLAT, and Errors
- `docs/apps/setup/SERVICES_FACADES.md`
- `docs/apps/setup/SERVICES_ERRORS.md`
- `docs/apps/setup/ERROR_TAXONOMY.md`
- `docs/apps/setup/SPLAT_REGISTRY.md`
- `docs/reference/specs/setup/SPLAT_SELECTION_RULES.md`

## Frontends and CLI
- `docs/apps/setup/FRONTEND_CONTRACT.md`
- `docs/apps/setup/CLI_REFERENCE.md`
- `docs/apps/setup/CLI_JSON_SCHEMAS.md`
- `docs/apps/setup/TUI_REFERENCE.md`
- `docs/apps/setup/OPERATOR_TOOLS.md`

## Adapters and Ownership
- `docs/apps/setup/ADAPTERS.md`
- `docs/apps/setup/ADAPTER_MATRIX.md`
- `docs/apps/setup/OWNERSHIP_MODEL.md`
- `docs/apps/setup/WINDOWS_MSI_WRAPPER.md`
- `docs/apps/setup/MACOS_PKG_WRAPPER.md`
- `docs/apps/setup/LINUX_DEB_WRAPPER.md`
- `docs/apps/setup/LINUX_RPM_WRAPPER.md`
- `docs/apps/setup/STEAM_PROVIDER.md`

## Validation and Operations
- `docs/apps/setup/CONFORMANCE.md`
- `docs/apps/setup/TROUBLESHOOTING.md`
- `docs/apps/setup/REPRODUCIBLE_BUILDS.md`
- `docs/apps/setup/REPRODUCIBILITY_GUARANTEES.md`
- `docs/reference/specs/setup/PARITY_LOCK_MATRIX.md`
- `docs/apps/setup/ARCHIVAL_AND_HANDOFF.md`

## Roadmap
- `docs/apps/setup/DEPRECATION_PLAN.md`
- `docs/apps/setup/LEGACY_STATE_IMPORT.md`
- `docs/apps/setup/PACKAGING_DEFAULTS.md`
- `docs/apps/setup/STATUS_SR1.md` .. `docs/apps/setup/STATUS_SR11.md`

## Maintenance and Extensions
- `docs/apps/setup/EXTENSION_POLICY.md`
- `docs/apps/setup/ADDING_FEATURES.md`
- `docs/apps/setup/STATE_EVOLUTION.md`
- `docs/apps/setup/SPLAT_LIFECYCLE.md`
- `docs/apps/setup/PARITY_WITH_LAUNCHER.md`
- `docs/reference/specs/setup/PARITY_LOCK_MATRIX.md`

## Deferred Work (Non-Binding)
- `docs/apps/setup/FUTURE_BACKLOG.md`
- Setup is complete without these items.

## Read-Only Status
- `docs/apps/setup/READ_ONLY_LOCK.md`
- `docs/apps/setup/SCHEMA_FREEZE_V1.md`
- `docs/reference/specs/setup/PARITY_LOCK_MATRIX.md`

## Handoff Snapshot
- `docs/apps/setup/HANDOFF_SNAPSHOT.md`
- `docs/apps/setup/OPERATIONS_QUICKSTART.md`

## How to Start v2 (If Ever)
- Setup v1 is frozen; changes require a new ladder starting at SR-0.
- See `docs/apps/setup/READ_ONLY_LOCK.md` for criteria and approvals.
