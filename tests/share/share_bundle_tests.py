import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile


SHARE_CLI = os.path.join("tools", "share", "share_cli.py")
OPS_CLI = os.path.join("tools", "ops", "ops_cli.py")


def run_share(args, env=None):
    cmd = [sys.executable, SHARE_CLI] + args
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    payload = {}
    if result.stdout.strip():
        payload = json.loads(result.stdout)
    return result.returncode, payload, result.stderr


def run_ops(args, env=None):
    cmd = [sys.executable, OPS_CLI] + args
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    payload = {}
    if result.stdout.strip():
        payload = json.loads(result.stdout)
    return result.returncode, payload, result.stderr


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def sha256_text(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        h.update(handle.read())
    return h.hexdigest()


def load_container(bundle_root):
    with open(os.path.join(bundle_root, "bundle.container.json"), "r", encoding="utf-8") as handle:
        return json.load(handle)


def find_entry(container, kind):
    for entry in container.get("contents_index", []):
        if entry.get("content_kind") == kind:
            return entry
    return None


def make_install_manifest(path, install_id):
    payload = {
        "install_id": install_id,
        "install_root": ".",
        "binaries": {
            "engine": {"product_id": "org.dominium.engine", "product_version": "0.0.0"},
            "game": {"product_id": "org.dominium.game", "product_version": "0.0.0"},
        },
        "supported_capabilities": [],
        "protocol_versions": {
            "network": "net@0",
            "save": "save@0",
            "mod": "mod@0",
            "replay": "replay@0",
        },
        "build_identity": 0,
        "trust_tier": "local",
        "created_at": "2000-01-01T00:00:00Z",
        "extensions": {},
    }
    write_json(path, payload)


def test_export_deterministic(tmp_root):
    save_path = os.path.join(tmp_root, "save.bin")
    lock_path = os.path.join(tmp_root, "lock.json")
    write_text(save_path, "save-data")
    write_text(lock_path, "{\"lock\":true}")

    bundle_a = os.path.join(tmp_root, "bundle_a")
    bundle_b = os.path.join(tmp_root, "bundle_b")

    args = [
        "--deterministic",
        "export",
        "--bundle-type", "save",
        "--artifact", save_path,
        "--lockfile", lock_path,
        "--bundle-id", "bundle.test.001",
        "--created-at", "2000-01-01T00:00:00Z",
        "--created-by", "test",
        "--tool-version", "test-tool",
        "--pack-ref", "org.example.pack@1.0.0",
        "--out",
    ]
    code, payload, _ = run_share(args + [bundle_a])
    if code != 0:
        raise AssertionError("export bundle_a failed")
    code, payload, _ = run_share(args + [bundle_b])
    if code != 0:
        raise AssertionError("export bundle_b failed")

    container_a = load_container(bundle_a)
    container_b = load_container(bundle_b)
    if container_a != container_b:
        raise AssertionError("deterministic export mismatch")

    entry = find_entry(container_a, "save")
    if not entry:
        raise AssertionError("save entry missing")
    saved_path = os.path.join(bundle_a, entry["content_path"])
    if sha256_text(saved_path) != entry["sha256"]:
        raise AssertionError("save hash mismatch")


def test_portable_inspect(tmp_root):
    save_path = os.path.join(tmp_root, "save.bin")
    lock_path = os.path.join(tmp_root, "lock.json")
    write_text(save_path, "save-data")
    write_text(lock_path, "{\"lock\":true}")
    bundle_root = os.path.join(tmp_root, "bundle_portable")
    code, payload, _ = run_share([
        "--deterministic",
        "export",
        "--bundle-type", "save",
        "--artifact", save_path,
        "--lockfile", lock_path,
        "--bundle-id", "bundle.test.002",
        "--created-at", "2000-01-01T00:00:00Z",
        "--created-by", "test",
        "--tool-version", "test-tool",
        "--out", bundle_root,
    ])
    if code != 0:
        raise AssertionError("portable export failed")

    copy_root = os.path.join(tmp_root, "bundle_copy")
    shutil.copytree(bundle_root, copy_root)
    code, payload, _ = run_share(["inspect", "--bundle", copy_root])
    if code != 0:
        raise AssertionError("inspect failed")


def test_missing_packs_detection(tmp_root):
    replay_path = os.path.join(tmp_root, "replay.bin")
    lock_path = os.path.join(tmp_root, "lock.json")
    write_text(replay_path, "replay-data")
    write_text(lock_path, "{\"lock\":true}")
    bundle_root = os.path.join(tmp_root, "bundle_replay")
    code, payload, _ = run_share([
        "--deterministic",
        "export",
        "--bundle-type", "replay",
        "--artifact", replay_path,
        "--lockfile", lock_path,
        "--bundle-id", "bundle.test.003",
        "--created-at", "2000-01-01T00:00:00Z",
        "--created-by", "test",
        "--tool-version", "test-tool",
        "--pack-ref", "org.example.pack@1.0.0",
        "--out", bundle_root,
    ])
    if code != 0:
        raise AssertionError("replay export failed")

    code, payload, _ = run_share([
        "import",
        "--bundle", bundle_root,
        "--require-full",
    ])
    if code == 0:
        raise AssertionError("require-full should refuse on missing packs")
    report = payload.get("compat_report", {})
    if report.get("compatibility_mode") != "refuse":
        raise AssertionError("expected refuse on missing packs")

    code, payload, _ = run_share([
        "import",
        "--bundle", bundle_root,
    ])
    if code != 0:
        raise AssertionError("import should be ok without require-full")
    if payload.get("import_state") != "confirm_required":
        raise AssertionError("expected confirm_required state")
    report = payload.get("compat_report", {})
    if report.get("compatibility_mode") != "degraded":
        raise AssertionError("expected degraded mode on missing packs")


def test_incompatible_bundle_refusal(tmp_root):
    save_path = os.path.join(tmp_root, "save.bin")
    lock_path = os.path.join(tmp_root, "lock.json")
    write_text(save_path, "save-data")
    write_text(lock_path, "{\"lock\":true}")
    bundle_root = os.path.join(tmp_root, "bundle_bad")
    code, payload, _ = run_share([
        "--deterministic",
        "export",
        "--bundle-type", "save",
        "--artifact", save_path,
        "--lockfile", lock_path,
        "--bundle-id", "bundle.test.004",
        "--created-at", "2000-01-01T00:00:00Z",
        "--created-by", "test",
        "--tool-version", "test-tool",
        "--out", bundle_root,
    ])
    if code != 0:
        raise AssertionError("bundle export failed")
    container = load_container(bundle_root)
    entry = find_entry(container, "save")
    bad_path = os.path.join(bundle_root, entry["content_path"])
    os.remove(bad_path)
    code, payload, _ = run_share(["inspect", "--bundle", bundle_root])
    if code == 0:
        raise AssertionError("inspect should refuse missing artifact")


def test_replay_hash(tmp_root):
    replay_path = os.path.join(tmp_root, "replay.bin")
    lock_path = os.path.join(tmp_root, "lock.json")
    write_text(replay_path, "replay-data")
    write_text(lock_path, "{\"lock\":true}")
    bundle_root = os.path.join(tmp_root, "bundle_replay_hash")
    code, payload, _ = run_share([
        "--deterministic",
        "export",
        "--bundle-type", "replay",
        "--artifact", replay_path,
        "--lockfile", lock_path,
        "--bundle-id", "bundle.test.005",
        "--created-at", "2000-01-01T00:00:00Z",
        "--created-by", "test",
        "--tool-version", "test-tool",
        "--out", bundle_root,
    ])
    if code != 0:
        raise AssertionError("replay export failed")
    container = load_container(bundle_root)
    entry = find_entry(container, "replay")
    if not entry:
        raise AssertionError("replay entry missing")
    original_hash = sha256_text(replay_path)
    if entry["sha256"] != original_hash:
        raise AssertionError("replay hash mismatch")


def test_portable_export_import_roundtrip_instance(tmp_root):
    install_root = os.path.join(tmp_root, "install")
    instance_root = os.path.join(tmp_root, "instance")
    packs_root = os.path.join(tmp_root, "packs")
    pack_root = os.path.join(packs_root, "org.example.pack.core")
    bundle_root = os.path.join(tmp_root, "instance_bundle")
    imported_portable = os.path.join(tmp_root, "imported_portable")
    imported_linked = os.path.join(tmp_root, "imported_linked")
    store_root = os.path.join(tmp_root, "store_root")
    os.makedirs(install_root, exist_ok=True)
    os.makedirs(pack_root, exist_ok=True)
    write_text(os.path.join(pack_root, "pack.toml"), "pack_id = \"org.example.pack.core\"\npack_version = \"1.0.0\"\n")
    write_text(os.path.join(pack_root, "content.txt"), "demo\n")
    install_manifest = os.path.join(install_root, "install.manifest.json")
    make_install_manifest(install_manifest, "install.test.instance.bundle")

    code, payload, _ = run_ops([
        "--deterministic",
        "instances", "create",
        "--install-manifest", install_manifest,
        "--data-root", instance_root,
        "--instance-id", "instance.test.bundle",
        "--active-profile", "org.dominium.profile.casual",
        "--active-modpack", "org.example.pack.core",
        "--pack-root", packs_root,
        "--save-ref", "save.alpha",
        "--last-opened-save-id", "save.alpha",
    ])
    if code != 0 or payload.get("result") != "ok":
        raise AssertionError("ops instance create failed for share roundtrip")

    manifest_path = os.path.join(instance_root, "instance.manifest.json")
    code, payload, _ = run_share([
        "--deterministic",
        "export",
        "--bundle-type", "instance",
        "--artifact", manifest_path,
        "--out", bundle_root,
    ])
    if code != 0 or payload.get("result") != "ok":
        raise AssertionError("instance bundle export failed")

    code, payload, _ = run_share([
        "--deterministic",
        "import",
        "--bundle", bundle_root,
        "--confirm",
        "--out", imported_portable,
    ])
    if code != 0 or payload.get("result") != "ok":
        raise AssertionError("portable instance bundle import failed")
    portable_manifest = json.load(open(os.path.join(imported_portable, "instance.manifest.json"), "r", encoding="utf-8"))
    if portable_manifest.get("mode") != "portable":
        raise AssertionError("portable import lost portable mode")
    if portable_manifest.get("save_refs") != ["save.alpha"]:
        raise AssertionError("portable import lost save refs")
    if os.path.isdir(os.path.join(imported_portable, "saves")):
        raise AssertionError("portable import should not embed saves")

    code, payload, _ = run_share([
        "--deterministic",
        "import",
        "--bundle", bundle_root,
        "--confirm",
        "--out", imported_linked,
        "--import-mode", "linked",
        "--store-root", store_root,
    ])
    if code != 0 or payload.get("result") != "ok":
        raise AssertionError("linked instance bundle import failed")
    linked_manifest = json.load(open(os.path.join(imported_linked, "instance.manifest.json"), "r", encoding="utf-8"))
    if linked_manifest.get("mode") != "linked":
        raise AssertionError("linked import did not switch mode")
    if linked_manifest.get("embedded_artifacts") != []:
        raise AssertionError("linked import should not retain embedded artifacts")
    if linked_manifest.get("save_refs") != ["save.alpha"]:
        raise AssertionError("linked import lost save refs")


def main():
    parser = argparse.ArgumentParser(description="Share bundle tests")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    os.chdir(os.path.abspath(args.repo_root))

    with tempfile.TemporaryDirectory() as tmp_root:
        test_export_deterministic(tmp_root)
        test_portable_inspect(tmp_root)
        test_missing_packs_detection(tmp_root)
        test_incompatible_bundle_refusal(tmp_root)
        test_replay_hash(tmp_root)
        test_portable_export_import_roundtrip_instance(tmp_root)

    print("SHARE-0 bundle tests OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
