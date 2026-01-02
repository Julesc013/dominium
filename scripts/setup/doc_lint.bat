@echo off
setlocal enabledelayedexpansion

set ROOT=%~dp0\..\..
for %%I in ("%ROOT%") do set ROOT=%%~fI

set FAIL=0

for %%F in (
    docs\setup\README.md
    docs\setup\INVARIANTS.md
    docs\setup\BUILD_RULES.md
    docs\setup\ERROR_TAXONOMY.md
    docs\setup\AUDIT_MODEL.md
    docs\setup\SERVICES_FACADES.md
    docs\setup\SERVICES_ERRORS.md
    docs\setup\SPLAT_REGISTRY.md
    docs\setup\SPLAT_SELECTION_RULES.md
    docs\setup\TLV_INSTALL_MANIFEST.md
    docs\setup\TLV_INSTALL_REQUEST.md
    docs\setup\TLV_INSTALL_PLAN.md
    docs\setup\TLV_INSTALLED_STATE.md
    docs\setup\TLV_SETUP_AUDIT.md
    docs\setup\TLV_JOB_JOURNAL.md
    docs\setup\TLV_TXN_JOURNAL.md
    docs\setup\PLANNING_RULES.md
    docs\setup\JOB_ENGINE.md
    docs\setup\TRANSACTIONS.md
    docs\setup\RECOVERY_PLAYBOOK.md
    docs\setup\FAILPOINTS.md
    docs\setup\FRONTEND_CONTRACT.md
    docs\setup\CLI_REFERENCE.md
    docs\setup\CLI_JSON_SCHEMAS.md
    docs\setup\TUI_REFERENCE.md
    docs\setup\ADAPTERS.md
    docs\setup\ADAPTER_MATRIX.md
    docs\setup\PARITY_LOCK_MATRIX.md
    docs\setup\OWNERSHIP_MODEL.md
    docs\setup\CONFORMANCE.md
    docs\setup\TROUBLESHOOTING.md
    docs\setup\REPRODUCIBLE_BUILDS.md
    docs\setup\SCHEMA_FREEZE_V1.md
    docs\setup\ARCHIVAL_AND_HANDOFF.md
    docs\setup\SECURITY_MODEL.md
    docs\setup\DEFAULTS_AND_FLAGS.md
    docs\setup\LEGACY_STATE_IMPORT.md
    docs\setup\PACKAGING_DEFAULTS.md
    docs\setup\DEPRECATION_PLAN.md
    docs\setup\EXTENSION_POLICY.md
    docs\setup\PARITY_WITH_LAUNCHER.md
    docs\setup\ADDING_FEATURES.md
    docs\setup\SPLAT_LIFECYCLE.md
    docs\setup\STATE_EVOLUTION.md
    docs\setup\OPERATOR_TOOLS.md
    docs\setup\REPRODUCIBILITY_GUARANTEES.md
    docs\setup\STATUS_SR5.md
    docs\setup\STATUS_SR6.md
    docs\setup\STATUS_SR8.md
    docs\setup\STATUS_SR9.md
    docs\setup\STATUS_SR10.md
    docs\setup\STATUS_SR11.md
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
