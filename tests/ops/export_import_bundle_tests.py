import argparse
import importlib
import json
import os
import shutil
import sys
import tempfile

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from lib.export import export_instance_bundle, export_save_bundle
from lib.instance import (
    deterministic_fingerprint as instance_deterministic_fingerprint,
    normalize_instance_manifest,
)
from lib.save import (
    deterministic_fingerprint as save_deterministic_fingerprint,
    normalize_save_manifest,
)
from tools.lib.content_store import (
    build_pack_lock_payload,
    build_profile_bundle_payload,
    embed_json_artifact,
    initialize_store_root,
    store_add_artifact,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


IMPORT_MOD = importlib.import_module("lib.import")
import_instance_bundle = IMPORT_MOD.import_instance_bundle
import_save_bundle = IMPORT_MOD.import_save_bundle


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def make_save_root(tmp_root, *, save_id="save.test.alpha", slash_mode="forward"):
    store_root = os.path.join(tmp_root, "store_root")
    initialize_store_root(store_root)
    pack_lock_payload, pack_lock_hash = build_pack_lock_payload(
        instance_id="instance.test",
        pack_ids=[],
        mod_policy_id="mod.policy.default",
        overlay_conflict_policy_id="overlay.conflict.default",
        source_payload={"semantic_contract_registry_hash": "r" * 64},
    )
    store_add_artifact(store_root, "locks", pack_lock_payload, expected_hash=pack_lock_hash)

    save_root = os.path.join(store_root, "saves", save_id)
    os.makedirs(os.path.join(save_root, "state.snapshots"), exist_ok=True)
    os.makedirs(os.path.join(save_root, "patches"), exist_ok=True)
    contract_bundle_payload = {
        "schema_id": "dominium.schema.universe_contract_bundle",
        "schema_version": "1.0.0",
        "bundle_id": "bundle.contract.tests",
        "contracts": [],
        "extensions": {},
    }
    write_json(os.path.join(save_root, "universe_contract_bundle.json"), contract_bundle_payload)
    write_json(os.path.join(save_root, "state.snapshots", "snapshot.000.json"), {"tick": 0})
    write_json(os.path.join(save_root, "patches", "overlay.000.json"), {"patch": 0})

    def slash(value):
        return value if slash_mode == "forward" else value.replace("/", "\\")

    payload = normalize_save_manifest(
        {
            "save_id": save_id,
            "save_format_version": "1.0.0",
            "universe_identity_hash": canonical_sha256({"save_id": save_id, "universe": "alpha"}),
            "universe_contract_bundle_hash": canonical_sha256(contract_bundle_payload),
            "semantic_contract_registry_hash": "r" * 64,
            "generator_version_id": "generator.test",
            "realism_profile_id": "realism.default",
            "pack_lock_hash": pack_lock_hash,
            "overlay_manifest_hash": canonical_sha256({"save_id": save_id, "overlay": "default"}),
            "mod_policy_id": "mod.policy.default",
            "created_by_build_id": "game.build.test",
            "migration_chain": [],
            "allow_read_only_open": False,
            "contract_bundle_ref": slash("universe_contract_bundle.json"),
            "state_snapshots_ref": slash("state.snapshots"),
            "patches_ref": slash("patches"),
            "proofs_ref": slash("proofs"),
            "extensions": {},
            "deterministic_fingerprint": "",
        }
    )
    payload["deterministic_fingerprint"] = save_deterministic_fingerprint(payload)
    manifest_path = os.path.join(save_root, "save.manifest.json")
    write_json(manifest_path, payload)
    return store_root, save_root, manifest_path


def make_instance_root(tmp_root, *, instance_id="instance.test.alpha", slash_mode="forward"):
    instance_root = os.path.join(tmp_root, "instances", instance_id)
    os.makedirs(instance_root, exist_ok=True)
    pack_lock_payload, pack_lock_hash = build_pack_lock_payload(
        instance_id=instance_id,
        pack_ids=[],
        mod_policy_id="mod.policy.default",
        overlay_conflict_policy_id="overlay.conflict.default",
        source_payload={"semantic_contract_registry_hash": "r" * 64},
    )
    profile_bundle_payload, profile_bundle_hash = build_profile_bundle_payload(
        instance_id=instance_id,
        profile_ids=["profile.default"],
        mod_policy_id="mod.policy.default",
        overlay_conflict_policy_id="overlay.conflict.default",
    )
    embed_json_artifact(instance_root, "locks", pack_lock_payload, expected_hash=pack_lock_hash)
    embed_json_artifact(instance_root, "profiles", profile_bundle_payload, expected_hash=profile_bundle_hash)

    def slash(value):
        return value if slash_mode == "forward" else value.replace("/", "\\")

    payload = normalize_instance_manifest(
        {
            "instance_id": instance_id,
            "instance_kind": "instance.client",
            "mode": "portable",
            "install_ref": {
                "install_id": "install.test",
                "manifest_ref": "",
                "root_path": "",
            },
            "embedded_builds": {},
            "pack_lock_hash": pack_lock_hash,
            "profile_bundle_hash": profile_bundle_hash,
            "mod_policy_id": "mod.policy.default",
            "overlay_conflict_policy_id": "overlay.conflict.default",
            "default_session_template_id": "session.template.default",
            "seed_policy": "prompt",
            "instance_settings": {
                "renderer_mode": None,
                "ui_mode_default": "cli",
                "allow_read_only_fallback": True,
            },
            "save_refs": [],
            "embedded_artifacts": [
                {
                    "category": "locks",
                    "artifact_hash": pack_lock_hash,
                    "artifact_id": str(pack_lock_payload.get("pack_lock_id", "")),
                    "artifact_type": "json",
                    "artifact_path": slash("embedded_artifacts/locks/{}".format(pack_lock_hash)),
                },
                {
                    "category": "profiles",
                    "artifact_hash": profile_bundle_hash,
                    "artifact_id": str(profile_bundle_payload.get("profile_bundle_id", "")),
                    "artifact_type": "json",
                    "artifact_path": slash("embedded_artifacts/profiles/{}".format(profile_bundle_hash)),
                },
            ],
            "extensions": {},
            "deterministic_fingerprint": "",
        }
    )
    payload["deterministic_fingerprint"] = instance_deterministic_fingerprint(payload)
    manifest_path = os.path.join(instance_root, "instance.manifest.json")
    write_json(manifest_path, payload)
    return instance_root, manifest_path


def test_export_bundle_hash_stable(tmp_root):
    store_root, _save_root, manifest_path = make_save_root(tmp_root, save_id="save.test.stable")
    bundle_a = os.path.join(tmp_root, "bundle_a")
    bundle_b = os.path.join(tmp_root, "bundle_b")
    result_a = export_save_bundle(
        repo_root=REPO_ROOT_HINT,
        save_manifest_path=manifest_path,
        out_path=bundle_a,
        vendor_packs=False,
        store_root=store_root,
    )
    result_b = export_save_bundle(
        repo_root=REPO_ROOT_HINT,
        save_manifest_path=manifest_path,
        out_path=bundle_b,
        vendor_packs=False,
        store_root=store_root,
    )
    if result_a.get("result") != "complete" or result_b.get("result") != "complete":
        raise RuntimeError("save bundle export failed")
    if str(result_a.get("bundle_hash", "")) != str(result_b.get("bundle_hash", "")):
        raise RuntimeError("bundle_hash changed across repeated exports")


def test_import_refuses_hash_mismatch(tmp_root):
    store_root, _save_root, manifest_path = make_save_root(tmp_root, save_id="save.test.mismatch")
    bundle_root = os.path.join(tmp_root, "bundle_bad")
    result = export_save_bundle(
        repo_root=REPO_ROOT_HINT,
        save_manifest_path=manifest_path,
        out_path=bundle_root,
        vendor_packs=False,
        store_root=store_root,
    )
    if result.get("result") != "complete":
        raise RuntimeError("save bundle export failed")
    tampered_path = os.path.join(bundle_root, "content", "save", "state.snapshots", "snapshot.000.json")
    write_json(tampered_path, {"tick": 999})
    imported = import_save_bundle(
        repo_root=REPO_ROOT_HINT,
        bundle_path=bundle_root,
        out_path=os.path.join(tmp_root, "imported_save_bad"),
        store_root=store_root,
    )
    if imported.get("result") == "complete":
        raise RuntimeError("tampered bundle import should refuse")


def test_instance_export_import_roundtrip(tmp_root):
    _instance_root, manifest_path = make_instance_root(tmp_root, instance_id="instance.test.roundtrip")
    bundle_root = os.path.join(tmp_root, "instance.bundle")
    exported = export_instance_bundle(
        repo_root=REPO_ROOT_HINT,
        instance_manifest_path=manifest_path,
        out_path=bundle_root,
        export_mode="portable",
    )
    if exported.get("result") != "complete":
        raise RuntimeError("instance bundle export failed: %s" % exported)
    imported_root = os.path.join(tmp_root, "imported_instance")
    imported = import_instance_bundle(
        repo_root=REPO_ROOT_HINT,
        bundle_path=bundle_root,
        out_path=imported_root,
        import_mode="portable",
    )
    if imported.get("result") != "complete":
        raise RuntimeError("instance bundle import failed: %s" % imported)
    imported_manifest = load_json(os.path.join(imported_root, "instance.manifest.json"))
    if str(imported_manifest.get("instance_id", "")).strip() != "instance.test.roundtrip":
        raise RuntimeError("instance_id changed during roundtrip")


def test_save_export_import_roundtrip(tmp_root):
    store_root, _save_root, manifest_path = make_save_root(tmp_root, save_id="save.test.roundtrip")
    bundle_root = os.path.join(tmp_root, "save.bundle")
    exported = export_save_bundle(
        repo_root=REPO_ROOT_HINT,
        save_manifest_path=manifest_path,
        out_path=bundle_root,
        vendor_packs=False,
        store_root=store_root,
    )
    if exported.get("result") != "complete":
        raise RuntimeError("save bundle export failed: %s" % exported)
    imported_root = os.path.join(tmp_root, "imported_save")
    imported = import_save_bundle(
        repo_root=REPO_ROOT_HINT,
        bundle_path=bundle_root,
        out_path=imported_root,
        store_root=store_root,
    )
    if imported.get("result") != "complete":
        raise RuntimeError("save bundle import failed: %s" % imported)
    imported_manifest = load_json(os.path.join(imported_root, "save.manifest.json"))
    if str(imported_manifest.get("save_id", "")).strip() != "save.test.roundtrip":
        raise RuntimeError("save_id changed during roundtrip")


def test_cross_platform_bundle_hash_match(tmp_root):
    store_root_a, _save_root_a, manifest_a = make_save_root(os.path.join(tmp_root, "forward"), save_id="save.test.paths", slash_mode="forward")
    store_root_b, _save_root_b, manifest_b = make_save_root(os.path.join(tmp_root, "backslash"), save_id="save.test.paths", slash_mode="backslash")
    bundle_a = os.path.join(tmp_root, "bundle_forward")
    bundle_b = os.path.join(tmp_root, "bundle_backslash")
    result_a = export_save_bundle(
        repo_root=REPO_ROOT_HINT,
        save_manifest_path=manifest_a,
        out_path=bundle_a,
        vendor_packs=False,
        store_root=store_root_a,
    )
    result_b = export_save_bundle(
        repo_root=REPO_ROOT_HINT,
        save_manifest_path=manifest_b,
        out_path=bundle_b,
        vendor_packs=False,
        store_root=store_root_b,
    )
    if result_a.get("result") != "complete" or result_b.get("result") != "complete":
        raise RuntimeError("cross-platform bundle export failed")
    if str(result_a.get("bundle_hash", "")) != str(result_b.get("bundle_hash", "")):
        raise RuntimeError("bundle_hash changed across path separators")


def main():
    parser = argparse.ArgumentParser(description="LIB-6 export/import bundle tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    os.chdir(repo_root)

    with tempfile.TemporaryDirectory() as tmp_root:
        test_export_bundle_hash_stable(tmp_root)
        test_import_refuses_hash_mismatch(tmp_root)
        test_instance_export_import_roundtrip(tmp_root)
        test_save_export_import_roundtrip(tmp_root)
        test_cross_platform_bundle_hash_match(tmp_root)

    print("export/import bundle tests: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
