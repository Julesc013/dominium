import argparse
import json
import os
import shutil
import sys
import tempfile

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from lib.save import (
    deterministic_fingerprint,
    migrate_save_manifest,
    normalize_save_manifest,
    validate_save_manifest,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def _build_contract_bundle_payload(bundle_id: str) -> dict:
    return {
        "schema_id": "dominium.schema.universe_contract_bundle",
        "schema_version": "1.0.0",
        "bundle_id": bundle_id,
        "contracts": [
            {
                "contract_category_id": "contract.logic.eval",
                "version": 1,
            }
        ],
        "extensions": {},
    }


def make_save_root(tmp_root: str, *, save_id: str = "save.test.alpha", save_format_version: str = "1.0.0") -> tuple[str, str]:
    save_root = os.path.join(tmp_root, "saves", save_id)
    os.makedirs(os.path.join(save_root, "state.snapshots"), exist_ok=True)
    os.makedirs(os.path.join(save_root, "patches"), exist_ok=True)
    contract_bundle_payload = _build_contract_bundle_payload("bundle.contract.save.tests")
    write_json(os.path.join(save_root, "universe_contract_bundle.json"), contract_bundle_payload)
    write_json(os.path.join(save_root, "state.snapshots", "snapshot.000.json"), {"tick": 0})
    write_json(os.path.join(save_root, "patches", "overlay.000.json"), {"patch": 0})
    payload = {
        "save_id": save_id,
        "save_format_version": save_format_version,
        "universe_identity_hash": canonical_sha256({"save_id": save_id, "universe": "alpha"}),
        "universe_contract_bundle_hash": canonical_sha256(contract_bundle_payload),
        "semantic_contract_registry_hash": "r" * 64,
        "generator_version_id": "generator.test",
        "realism_profile_id": "realism.profile.default",
        "pack_lock_hash": "p" * 64,
        "overlay_manifest_hash": canonical_sha256({"save_id": save_id, "overlay": "default"}),
        "mod_policy_id": "mod.policy.default",
        "created_by_build_id": "game.build.test",
        "migration_chain": [],
        "allow_read_only_open": False,
        "contract_bundle_ref": "universe_contract_bundle.json",
        "state_snapshots_ref": "state.snapshots",
        "patches_ref": "patches",
        "proofs_ref": "proofs",
        "extensions": {},
        "deterministic_fingerprint": "",
    }
    payload = normalize_save_manifest(payload)
    payload["deterministic_fingerprint"] = deterministic_fingerprint(payload)
    manifest_path = os.path.join(save_root, "save.manifest.json")
    write_json(manifest_path, payload)
    return save_root, manifest_path


def test_save_manifest_valid(tmp_root: str) -> None:
    _save_root, manifest_path = make_save_root(tmp_root)
    report = validate_save_manifest(repo_root=REPO_ROOT_HINT, save_manifest_path=manifest_path)
    if report.get("result") != "complete":
        raise RuntimeError("save manifest validation failed: %s" % report)


def test_migration_chain_logged(tmp_root: str) -> None:
    _save_root, manifest_path = make_save_root(tmp_root, save_id="save.test.migrate", save_format_version="0.9.0")
    result = migrate_save_manifest(
        repo_root=REPO_ROOT_HINT,
        save_manifest_path=manifest_path,
        to_version="1.0.0",
        migration_id="migration.save.tests.0_9_to_1_0",
        tick_applied=42,
    )
    if result.get("result") != "complete":
        raise RuntimeError("save migration failed: %s" % result)
    manifest = json.load(open(manifest_path, "r", encoding="utf-8"))
    chain = manifest.get("migration_chain") or []
    if len(chain) != 1:
        raise RuntimeError("expected single migration event")
    event = dict(chain[0] or {})
    if event.get("migration_id") != "migration.save.tests.0_9_to_1_0":
        raise RuntimeError("migration event missing migration_id")
    if int(event.get("tick_applied", 0) or 0) != 42:
        raise RuntimeError("migration event missing tick_applied")
    if manifest.get("save_format_version") != "1.0.0":
        raise RuntimeError("save_format_version not upgraded")


def test_cross_platform_save_manifest_hash_match(tmp_root: str) -> None:
    _save_root, manifest_path = make_save_root(tmp_root, save_id="save.test.hash")
    manifest = json.load(open(manifest_path, "r", encoding="utf-8"))
    mutated = json.loads(json.dumps(manifest))
    for field in ("contract_bundle_ref", "state_snapshots_ref", "patches_ref", "proofs_ref"):
        if mutated.get(field):
            mutated[field] = str(mutated[field]).replace("/", "\\")
    if deterministic_fingerprint(mutated) != manifest.get("deterministic_fingerprint"):
        raise RuntimeError("save fingerprint changed across path separators")


def main():
    parser = argparse.ArgumentParser(description="Save manifest validation tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    os.chdir(repo_root)

    with tempfile.TemporaryDirectory() as tmp_root:
        test_save_manifest_valid(tmp_root)
        test_migration_chain_logged(tmp_root)
        test_cross_platform_save_manifest_hash_match(tmp_root)

    print("save manifest tests: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
