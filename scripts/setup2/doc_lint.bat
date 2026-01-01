@echo off
setlocal enabledelayedexpansion

set ROOT=%~dp0\..\..
for %%I in ("%ROOT%") do set ROOT=%%~fI

set FAIL=0

for %%F in (
    docs\setup2\README.md
    docs\setup2\INVARIANTS.md
    docs\setup2\BUILD_RULES.md
    docs\setup2\ERROR_TAXONOMY.md
    docs\setup2\AUDIT_MODEL.md
    docs\setup2\SERVICES_FACADES.md
    docs\setup2\SERVICES_ERRORS.md
    docs\setup2\SPLAT_REGISTRY.md
    docs\setup2\SPLAT_SELECTION_RULES.md
    docs\setup2\TLV_INSTALL_MANIFEST.md
    docs\setup2\TLV_INSTALL_REQUEST.md
    docs\setup2\TLV_INSTALL_PLAN.md
    docs\setup2\TLV_INSTALLED_STATE.md
    docs\setup2\TLV_SETUP_AUDIT.md
    docs\setup2\TLV_JOB_JOURNAL.md
    docs\setup2\TLV_TXN_JOURNAL.md
    docs\setup2\PLANNING_RULES.md
    docs\setup2\JOB_ENGINE.md
    docs\setup2\TRANSACTIONS.md
    docs\setup2\RECOVERY_PLAYBOOK.md
    docs\setup2\FAILPOINTS.md
    docs\setup2\FRONTEND_CONTRACT.md
    docs\setup2\CLI_REFERENCE.md
    docs\setup2\CLI_JSON_SCHEMAS.md
    docs\setup2\TUI_REFERENCE.md
    docs\setup2\ADAPTERS.md
    docs\setup2\ADAPTER_MATRIX.md
    docs\setup2\PARITY_LOCK_MATRIX.md
    docs\setup2\OWNERSHIP_MODEL.md
    docs\setup2\CONFORMANCE.md
    docs\setup2\TROUBLESHOOTING.md
    docs\setup2\REPRODUCIBLE_BUILDS.md
    docs\setup2\SCHEMA_FREEZE_V1.md
    docs\setup2\ARCHIVAL_AND_HANDOFF.md
    docs\setup2\SECURITY_MODEL.md
    docs\setup2\DEFAULTS_AND_FLAGS.md
    docs\setup2\LEGACY_STATE_IMPORT.md
    docs\setup2\PACKAGING_DEFAULTS.md
    docs\setup2\DEPRECATION_PLAN.md
    docs\setup2\EXTENSION_POLICY.md
    docs\setup2\PARITY_WITH_LAUNCHER.md
    docs\setup2\ADDING_FEATURES.md
    docs\setup2\SPLAT_LIFECYCLE.md
    docs\setup2\STATE_EVOLUTION.md
    docs\setup2\OPERATOR_TOOLS.md
    docs\setup2\REPRODUCIBILITY_GUARANTEES.md
    docs\setup2\STATUS_SR5.md
    docs\setup2\STATUS_SR6.md
    docs\setup2\STATUS_SR8.md
    docs\setup2\STATUS_SR9.md
    docs\setup2\STATUS_SR10.md
    docs\setup2\STATUS_SR11.md
) do (
    set FILE=%ROOT%\%%F
    if not exist "!FILE!" (
        echo MISSING: %%F
        set FAIL=1
    ) else (
        set LINE=
        set /p LINE=<"!FILE!"
        if not "!LINE:~0,2!"=="# " (
            echo BAD HEADING: %%F
            set FAIL=1
        )
    )
)

if not "%FAIL%"=="0" exit /b 1
exit /b 0
