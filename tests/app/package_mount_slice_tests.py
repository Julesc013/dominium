import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


from tools.validators.package.check_package_mount_slice import (  # noqa: E402
    COMMAND_ID,
    VALID_RESULT_REL,
    build_mount_result_from_fixture,
    canonical_result_bytes,
    load_json,
    validate_all,
)


def _assert(condition, message, violations):
    if not condition:
        violations.append(message)


def test_valid_package_mount_fixture_passes(violations):
    result = validate_all(REPO_ROOT, include_fixtures=True, include_inventory=False)
    _assert(result["status"] == "pass", "package mount validator did not pass", violations)
    _assert(result["summary"]["errors"] == 0, "package mount validator reported errors", violations)
    _assert(result["fixtures"]["invalid_fixtures"] == 7, "expected negative fixture count changed", violations)


def test_mount_result_preserves_contract_boundaries(violations):
    result = build_mount_result_from_fixture(REPO_ROOT)
    _assert(result["command_id"] == COMMAND_ID, "mount result command id mismatch", violations)
    _assert(result["status"] == "pass", "mount result status mismatch", violations)
    _assert(result["package_ref"]["id"] == "pack.base.procedural", "package identity mismatch", violations)
    _assert(result["package_ref"]["source_ref_is_authority"] is False, "source_ref became authority", violations)
    _assert(result["pack_mount_lock_ref"]["source_truth"] is False, "lockfile marked source truth", violations)
    _assert(result["pack_mount_lock_ref"]["artifact_class"] == "derived_evidence", "lockfile is not derived evidence", violations)
    for key in ("runtime_mounting_implemented", "package_runtime_implemented", "mod_loader_implemented", "provider_runtime_implemented"):
        _assert(result[key] is False, "{} should remain false".format(key), violations)
    _assert(result["support_claim"] is False, "fixture result claims product support", violations)


def test_negative_fixtures_cover_required_refusals(violations):
    result = validate_all(REPO_ROOT, include_fixtures=True, include_inventory=False)
    observed = {}
    for item in result["fixtures"]["fixtures"]:
        observed[Path(item["path"]).name] = set(item["observed_failures"])
    expected = {
        "invalid_unknown_package_ref.json": "unknown_package_ref",
        "invalid_path_as_identity.json": "path_as_identity",
        "invalid_silent_overlay_overwrite.json": "silent_overlay_overwrite",
        "invalid_missing_required_capability.json": "missing_required_capability",
        "invalid_unsupported_trust_level.json": "unsupported_trust_level",
        "invalid_lockfile_source_truth.json": "lockfile_source_truth",
        "invalid_degraded_fallback_without_trace.json": "degraded_fallback_without_trace",
    }
    for fixture_name, code in expected.items():
        _assert(code in observed.get(fixture_name, set()), "{} did not observe {}".format(fixture_name, code), violations)


def test_mount_result_serializes_deterministically(violations):
    raw = canonical_result_bytes(REPO_ROOT)
    parsed = json.loads(raw.decode("utf-8"))
    fixture = load_json(REPO_ROOT / VALID_RESULT_REL)
    _assert(parsed == fixture, "canonical serialization changed semantic content", violations)
    _assert(raw == canonical_result_bytes(REPO_ROOT), "canonical serialization is not stable", violations)


def main():
    violations = []
    test_valid_package_mount_fixture_passes(violations)
    test_mount_result_preserves_contract_boundaries(violations)
    test_negative_fixtures_cover_required_refusals(violations)
    test_mount_result_serializes_deterministically(violations)
    if violations:
        for violation in violations:
            print(violation)
        return 1
    print("Package mount slice tests OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
