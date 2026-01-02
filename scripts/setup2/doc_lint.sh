#!/usr/bin/env bash
set -u

root="$(cd "$(dirname "$0")/../.." && pwd)"
fail=0

required=(
  "docs/setup2/README.md"
  "docs/setup2/INVARIANTS.md"
  "docs/setup2/BUILD_RULES.md"
  "docs/setup2/ERROR_TAXONOMY.md"
  "docs/setup2/AUDIT_MODEL.md"
  "docs/setup2/SERVICES_FACADES.md"
  "docs/setup2/SERVICES_ERRORS.md"
  "docs/setup2/SPLAT_REGISTRY.md"
  "docs/setup2/SPLAT_SELECTION_RULES.md"
  "docs/setup2/TLV_INSTALL_MANIFEST.md"
  "docs/setup2/TLV_INSTALL_REQUEST.md"
  "docs/setup2/TLV_INSTALL_PLAN.md"
  "docs/setup2/TLV_INSTALLED_STATE.md"
  "docs/setup2/TLV_SETUP_AUDIT.md"
  "docs/setup2/TLV_JOB_JOURNAL.md"
  "docs/setup2/TLV_TXN_JOURNAL.md"
  "docs/setup2/PLANNING_RULES.md"
  "docs/setup2/JOB_ENGINE.md"
  "docs/setup2/TRANSACTIONS.md"
  "docs/setup2/RECOVERY_PLAYBOOK.md"
  "docs/setup2/FAILPOINTS.md"
  "docs/setup2/FRONTEND_CONTRACT.md"
  "docs/setup2/CLI_REFERENCE.md"
  "docs/setup2/CLI_JSON_SCHEMAS.md"
  "docs/setup2/TUI_REFERENCE.md"
  "docs/setup2/ADAPTERS.md"
  "docs/setup2/ADAPTER_MATRIX.md"
  "docs/setup2/PARITY_LOCK_MATRIX.md"
  "docs/setup2/OWNERSHIP_MODEL.md"
  "docs/setup2/CONFORMANCE.md"
  "docs/setup2/TROUBLESHOOTING.md"
  "docs/setup2/REPRODUCIBLE_BUILDS.md"
  "docs/setup2/SCHEMA_FREEZE_V1.md"
  "docs/setup2/ARCHIVAL_AND_HANDOFF.md"
  "docs/setup2/SECURITY_MODEL.md"
  "docs/setup2/DEFAULTS_AND_FLAGS.md"
  "docs/setup2/LEGACY_STATE_IMPORT.md"
  "docs/setup2/PACKAGING_DEFAULTS.md"
  "docs/setup2/DEPRECATION_PLAN.md"
  "docs/setup2/EXTENSION_POLICY.md"
  "docs/setup2/PARITY_WITH_LAUNCHER.md"
  "docs/setup2/ADDING_FEATURES.md"
  "docs/setup2/SPLAT_LIFECYCLE.md"
  "docs/setup2/STATE_EVOLUTION.md"
  "docs/setup2/OPERATOR_TOOLS.md"
  "docs/setup2/REPRODUCIBILITY_GUARANTEES.md"
  "docs/setup2/STATUS_SR5.md"
  "docs/setup2/STATUS_SR6.md"
  "docs/setup2/STATUS_SR8.md"
  "docs/setup2/STATUS_SR9.md"
  "docs/setup2/STATUS_SR10.md"
  "docs/setup2/STATUS_SR11.md"
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
