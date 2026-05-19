#!/usr/bin/env bash
set -u

root="$(cd "$(dirname "$0")/../.." && pwd)"
fail=0

required=(
  "docs/apps/setup/README.md"
  "docs/apps/setup/INVARIANTS.md"
  "docs/apps/setup/BUILD_RULES.md"
  "docs/apps/setup/ERROR_TAXONOMY.md"
  "docs/apps/setup/AUDIT_MODEL.md"
  "docs/apps/setup/SERVICES_FACADES.md"
  "docs/apps/setup/SERVICES_ERRORS.md"
  "docs/apps/setup/SPLAT_REGISTRY.md"
  "docs/apps/setup/SPLAT_SELECTION_RULES.md"
  "docs/apps/setup/TLV_INSTALL_MANIFEST.md"
  "docs/apps/setup/TLV_INSTALL_REQUEST.md"
  "docs/apps/setup/TLV_INSTALL_PLAN.md"
  "docs/apps/setup/TLV_INSTALLED_STATE.md"
  "docs/apps/setup/TLV_SETUP_AUDIT.md"
  "docs/apps/setup/TLV_JOB_JOURNAL.md"
  "docs/apps/setup/TLV_TXN_JOURNAL.md"
  "docs/apps/setup/PLANNING_RULES.md"
  "docs/apps/setup/JOB_ENGINE.md"
  "docs/apps/setup/TRANSACTIONS.md"
  "docs/apps/setup/RECOVERY_PLAYBOOK.md"
  "docs/apps/setup/FAILPOINTS.md"
  "docs/apps/setup/FRONTEND_CONTRACT.md"
  "docs/apps/setup/CLI_REFERENCE.md"
  "docs/apps/setup/CLI_JSON_SCHEMAS.md"
  "docs/apps/setup/TUI_REFERENCE.md"
  "docs/apps/setup/ADAPTERS.md"
  "docs/apps/setup/ADAPTER_MATRIX.md"
  "docs/apps/setup/PARITY_LOCK_MATRIX.md"
  "docs/apps/setup/OWNERSHIP_MODEL.md"
  "docs/apps/setup/CONFORMANCE.md"
  "docs/apps/setup/TROUBLESHOOTING.md"
  "docs/apps/setup/REPRODUCIBLE_BUILDS.md"
  "docs/apps/setup/SCHEMA_FREEZE_V1.md"
  "docs/apps/setup/ARCHIVAL_AND_HANDOFF.md"
  "docs/apps/setup/SECURITY_MODEL.md"
  "docs/apps/setup/DEFAULTS_AND_FLAGS.md"
  "docs/apps/setup/LEGACY_STATE_IMPORT.md"
  "docs/apps/setup/PACKAGING_DEFAULTS.md"
  "docs/apps/setup/DEPRECATION_PLAN.md"
  "docs/apps/setup/EXTENSION_POLICY.md"
  "docs/apps/setup/PARITY_WITH_LAUNCHER.md"
  "docs/apps/setup/ADDING_FEATURES.md"
  "docs/apps/setup/SPLAT_LIFECYCLE.md"
  "docs/apps/setup/STATE_EVOLUTION.md"
  "docs/apps/setup/OPERATOR_TOOLS.md"
  "docs/apps/setup/REPRODUCIBILITY_GUARANTEES.md"
  "docs/apps/setup/STATUS_SR5.md"
  "docs/apps/setup/STATUS_SR6.md"
  "docs/apps/setup/STATUS_SR8.md"
  "docs/apps/setup/STATUS_SR9.md"
  "docs/apps/setup/STATUS_SR10.md"
  "docs/apps/setup/STATUS_SR11.md"
)

for rel in "${required[@]}"; do
  path="$root/$rel"
  if [ ! -f "$path" ]; then
    echo "MISSING: $rel"
    fail=1
    continue
  fi
  first="$(head -n 1 "$path")"
  case "$first" in
    "# "*) ;;
    *)
      echo "BAD HEADING: $rel"
      fail=1
      ;;
  esac
done

if [ "$fail" -ne 0 ]; then
  exit 1
fi
exit 0
