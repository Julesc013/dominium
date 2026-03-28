import argparse
import json
import os
import sys
import tempfile

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from lib.artifact import (
    ARTIFACT_DEGRADE_BEST_EFFORT,
    ARTIFACT_DEGRADE_STRICT_REFUSE,
    ARTIFACT_KIND_BLUEPRINT,
    ARTIFACT_KIND_PROFILE_BUNDLE,
    canonicalize_artifact_manifest,
    compute_artifact_content_hash,
    deterministic_fingerprint,
    evaluate_artifact_load,
    validate_artifact_manifest,
)


def _clone(payload: dict) -> dict:
    return json.loads(json.dumps(payload))


def _profile_bundle_manifest() -> dict:
    return canonicalize_artifact_manifest(
        {
            "schema_id": "dominium.schema.profile.bundle",
            "schema_version": "1.0.0",
            "format_version": "1.0.0",
            "artifact_id": "profile_bundle.test.alpha",
            "artifact_kind_id": ARTIFACT_KIND_PROFILE_BUNDLE,
            "profile_bundle_id": "profile_bundle.test.alpha",
            "profile_ids": ["profile.casual", "profile.creator"],
            "required_contract_ranges": {},
            "required_capabilities": [],
            "compatible_topology_profiles": [],
            "compatible_physics_profiles": [],
            "degrade_mode_id": ARTIFACT_DEGRADE_STRICT_REFUSE,
            "migration_refs": [],
            "extensions": {},
        },
        expected_kind_id=ARTIFACT_KIND_PROFILE_BUNDLE,
    )


def _blueprint_manifest(*, degrade_mode_id: str, required_capabilities: list[str], required_contract_ranges: dict) -> dict:
    return canonicalize_artifact_manifest(
        {
            "schema_id": "dominium.schema.materials.blueprint",
            "schema_version": "1.0.0",
            "format_version": "1.0.0",
            "artifact_id": "blueprint.house.test",
            "artifact_kind_id": ARTIFACT_KIND_BLUEPRINT,
            "blueprint_id": "blueprint.house.test",
            "description": "Test blueprint",
            "bom_ref": "bom.house.test",
            "ag_ref": "ag.house.test",
            "tags": ["test"],
            "required_contract_ranges": required_contract_ranges,
            "required_capabilities": list(required_capabilities),
            "compatible_topology_profiles": [],
            "compatible_physics_profiles": [],
            "degrade_mode_id": degrade_mode_id,
            "migration_refs": [],
            "extensions": {},
        },
        expected_kind_id=ARTIFACT_KIND_BLUEPRINT,
    )


def test_artifact_manifest_schema_valid() -> None:
    payload = _profile_bundle_manifest()
    report = validate_artifact_manifest(
        repo_root=REPO_ROOT_HINT,
        manifest_payload=payload,
        expected_kind_id=ARTIFACT_KIND_PROFILE_BUNDLE,
    )
    if report.get("result") != "complete":
        raise RuntimeError("artifact manifest validation failed: %s" % report)


def test_content_hash_verification() -> None:
    payload = _profile_bundle_manifest()
    tampered = _clone(payload)
    tampered["profile_ids"].append("profile.extra")
    report = validate_artifact_manifest(
        repo_root=REPO_ROOT_HINT,
        manifest_payload=tampered,
        expected_kind_id=ARTIFACT_KIND_PROFILE_BUNDLE,
    )
    if report.get("result") == "complete":
        raise RuntimeError("artifact content hash verification should refuse tampered payload")


def test_contract_range_validation() -> None:
    payload = _blueprint_manifest(
        degrade_mode_id=ARTIFACT_DEGRADE_STRICT_REFUSE,
        required_capabilities=[],
        required_contract_ranges={
            "contract.logic.eval": {
                "contract_category_id": "contract.logic.eval",
                "min_version": 2,
                "max_version": 2,
                "extensions": {},
            }
        },
    )
    install_manifest = {
        "supported_contract_ranges": {
            "contract.logic.eval": {
                "contract_category_id": "contract.logic.eval",
                "min_version": 1,
                "max_version": 1,
                "extensions": {},
            }
        }
    }
    result = evaluate_artifact_load(
        repo_root=REPO_ROOT_HINT,
        manifest_payload=payload,
        expected_kind_id=ARTIFACT_KIND_BLUEPRINT,
        install_manifest=install_manifest,
        provided_capabilities=[],
    )
    if result.get("result") != "refused":
        raise RuntimeError("artifact contract range mismatch should refuse")


def test_best_effort_degrade_deterministic() -> None:
    payload = _blueprint_manifest(
        degrade_mode_id=ARTIFACT_DEGRADE_BEST_EFFORT,
        required_capabilities=["cap.blueprint.preview"],
        required_contract_ranges={},
    )
    left = evaluate_artifact_load(
        repo_root=REPO_ROOT_HINT,
        manifest_payload=payload,
        expected_kind_id=ARTIFACT_KIND_BLUEPRINT,
        provided_capabilities=[],
    )
    right = evaluate_artifact_load(
        repo_root=REPO_ROOT_HINT,
        manifest_payload=payload,
        expected_kind_id=ARTIFACT_KIND_BLUEPRINT,
        provided_capabilities=[],
    )
    if left != right:
        raise RuntimeError("best-effort degrade must be deterministic")
    if left.get("compatibility_mode") != "degraded":
        raise RuntimeError("best-effort degrade should produce degraded compatibility_mode")


def test_cross_platform_artifact_hash_match() -> None:
    windows_like = canonicalize_artifact_manifest(
        {
            "schema_id": "dominium.schema.profile.bundle",
            "schema_version": "1.0.0",
            "format_version": "1.0.0",
            "artifact_id": "profile_bundle.test.path",
            "artifact_kind_id": ARTIFACT_KIND_PROFILE_BUNDLE,
            "profile_bundle_id": "profile_bundle.test.path",
            "profile_ids": ["profile.casual"],
            "required_contract_ranges": {},
            "required_capabilities": [],
            "compatible_topology_profiles": [],
            "compatible_physics_profiles": [],
            "degrade_mode_id": ARTIFACT_DEGRADE_STRICT_REFUSE,
            "migration_refs": [],
            "extensions": {
                "official.payload_ref": "artifacts\\profile\\payload.json",
            },
        },
        expected_kind_id=ARTIFACT_KIND_PROFILE_BUNDLE,
    )
    posix_like = _clone(windows_like)
    posix_like["extensions"]["official.payload_ref"] = "artifacts/profile/payload.json"
    if compute_artifact_content_hash(windows_like) != compute_artifact_content_hash(posix_like):
        raise RuntimeError("artifact content hash changed across path separators")
    if deterministic_fingerprint(windows_like) != deterministic_fingerprint(posix_like):
        raise RuntimeError("artifact fingerprint changed across path separators")


def main() -> int:
    parser = argparse.ArgumentParser(description="Artifact manifest validation tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    os.chdir(os.path.abspath(args.repo_root))

    with tempfile.TemporaryDirectory():
        test_artifact_manifest_schema_valid()
        test_content_hash_verification()
        test_contract_range_validation()
        test_best_effort_degrade_deterministic()
        test_cross_platform_artifact_hash_match()

    print("artifact manifest tests: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
