import argparse
import json
import os
import subprocess
import sys
import tempfile


def _repo_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


REPO_ROOT = _repo_root()
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.lib.content_store import canonical_sha256, initialize_store_root, store_add_artifact, store_verify


OPS_CLI = os.path.join(REPO_ROOT, "tools", "ops", "ops_cli.py")
SHARE_CLI = os.path.join(REPO_ROOT, "tools", "share", "share_cli.py")
LAUNCHER_CLI = os.path.join(REPO_ROOT, "tools", "launcher", "launcher_cli.py")


def run_json(script: str, args: list, env: dict | None = None):
    cmd = [sys.executable, script] + args
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, check=False)
    payload = {}
    if proc.stdout.strip():
        payload = json.loads(proc.stdout)
    return proc.returncode, payload, proc.stderr


def write_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def make_install_manifest(path: str, install_id: str, root: str) -> None:
    write_json(path, {
        "install_id": install_id,
        "install_root": root,
        "binaries": {
            "engine": {"product_id": "org.dominium.engine", "product_version": "0.1.0", "build_id": "engine.001"},
            "game": {"product_id": "org.dominium.game", "product_version": "0.1.0", "build_id": "game.001"},
        },
        "supported_capabilities": [],
        "protocol_versions": {
            "network": "net@1",
            "save": "save@1",
            "mod": "mod@1",
            "replay": "replay@1",
        },
        "build_identity": 1,
        "trust_tier": "local",
        "created_at": "2000-01-01T00:00:00Z",
        "extensions": {},
    })


def make_pack(root: str, pack_id: str, pack_version: str = "1.0.0") -> str:
    pack_root = os.path.join(root, pack_id)
    os.makedirs(pack_root, exist_ok=True)
    with open(os.path.join(pack_root, "pack.toml"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write('pack_id = "{}"\n'.format(pack_id))
        handle.write('pack_version = "{}"\n'.format(pack_version))
    with open(os.path.join(pack_root, "content.txt"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write("content:{}\n".format(pack_id))
    return pack_root


def test_store_add_deterministic_hash(tmp_root: str) -> None:
    store_a = os.path.join(tmp_root, "store_a")
    store_b = os.path.join(tmp_root, "store_b")
    initialize_store_root(store_a)
    initialize_store_root(store_b)
    artifact = {
        "lock_id": "lock.cas.test",
        "pack_refs": [{"pack_id": "org.dominium.pack.core"}],
        "extensions": {},
    }
    result_a = store_add_artifact(store_a, "locks", artifact)
    result_b = store_add_artifact(store_b, "locks", artifact)
    expected_hash = canonical_sha256(artifact)
    if result_a.get("artifact_hash") != expected_hash or result_b.get("artifact_hash") != expected_hash:
        raise AssertionError("deterministic artifact hash mismatch")
    verify = store_verify(store_a, "locks", expected_hash)
    if verify.get("result") != "ok" or not verify.get("verified"):
        raise AssertionError("store verification failed")


def test_duplicate_artifact_no_duplicate_write(tmp_root: str) -> None:
    store_root = os.path.join(tmp_root, "store_dup")
    initialize_store_root(store_root)
    artifact = {
        "profile_bundle_id": "profile.bundle.test",
        "profile_ids": ["org.dominium.profile.casual"],
        "extensions": {},
    }
    first = store_add_artifact(store_root, "profiles", artifact)
    second = store_add_artifact(store_root, "profiles", artifact)
    if not first.get("created") or second.get("created"):
        raise AssertionError("duplicate artifact write semantics broken")
    artifact_root = os.path.join(store_root, "store", "profiles", first["artifact_hash"])
    if sorted(os.listdir(artifact_root)) != ["artifact.manifest.json", "payload.json"]:
        raise AssertionError("unexpected artifact contents after duplicate write")


def test_instance_clone_linked_no_duplication(tmp_root: str) -> None:
    env = dict(os.environ)
    env["OPS_DETERMINISTIC"] = "1"
    install_root = os.path.join(tmp_root, "install")
    packs_root = os.path.join(install_root, "packs")
    store_root = os.path.join(tmp_root, "shared_store")
    instance_root = os.path.join(tmp_root, "linked_instance")
    clone_root = os.path.join(tmp_root, "linked_clone")
    os.makedirs(install_root, exist_ok=True)
    make_install_manifest(os.path.join(install_root, "install.manifest.json"),
                          "00000000-0000-0000-0000-000000000101",
                          install_root)
    make_pack(packs_root, "org.dominium.pack.core")
    code, payload, stderr = run_json(OPS_CLI, [
        "--deterministic",
        "instances", "create",
        "--install-manifest", os.path.join(install_root, "install.manifest.json"),
        "--data-root", instance_root,
        "--instance-id", "10000000-0000-0000-0000-000000000101",
        "--mode", "linked",
        "--store-root", store_root,
        "--active-profile", "org.dominium.profile.casual",
        "--active-modpack", "org.dominium.pack.core",
        "--pack-root", packs_root,
    ], env=env)
    if code != 0:
        raise AssertionError("linked instance create failed: {} {}".format(payload, stderr))
    manifest_path = payload["instance_manifest"]
    manifest = load_json(manifest_path)
    code, payload, stderr = run_json(OPS_CLI, [
        "--deterministic",
        "instances", "clone",
        "--source-manifest", manifest_path,
        "--data-root", clone_root,
        "--instance-id", "10000000-0000-0000-0000-000000000102",
    ], env=env)
    if code != 0:
        raise AssertionError("linked instance clone failed: {} {}".format(payload, stderr))
    clone_manifest = load_json(payload["instance_manifest"])
    packs_dir = os.path.join(store_root, "store", "packs")
    if len(os.listdir(packs_dir)) != 1:
        raise AssertionError("linked clone duplicated pack artifacts")
    if manifest.get("pack_lock_hash") != clone_manifest.get("pack_lock_hash"):
        raise AssertionError("linked clone changed pack lock hash")
    if clone_manifest.get("mode") != "linked":
        raise AssertionError("linked clone mode lost")


def test_portable_export_import_roundtrip(tmp_root: str) -> None:
    env = dict(os.environ)
    env["OPS_DETERMINISTIC"] = "1"
    install_root = os.path.join(tmp_root, "portable_install")
    packs_root = os.path.join(install_root, "packs")
    instance_root = os.path.join(tmp_root, "portable_instance")
    bundle_root = os.path.join(tmp_root, "portable_instance.bundle")
    import_root = os.path.join(tmp_root, "portable_import")
    os.makedirs(install_root, exist_ok=True)
    make_install_manifest(os.path.join(install_root, "install.manifest.json"),
                          "00000000-0000-0000-0000-000000000201",
                          install_root)
    make_pack(packs_root, "org.dominium.pack.core")
    code, payload, stderr = run_json(OPS_CLI, [
        "--deterministic",
        "instances", "create",
        "--install-manifest", os.path.join(install_root, "install.manifest.json"),
        "--data-root", instance_root,
        "--instance-id", "10000000-0000-0000-0000-000000000201",
        "--mode", "portable",
        "--active-profile", "org.dominium.profile.casual",
        "--active-modpack", "org.dominium.pack.core",
        "--pack-root", packs_root,
    ], env=env)
    if code != 0:
        raise AssertionError("portable instance create failed: {} {}".format(payload, stderr))
    manifest_path = payload["instance_manifest"]
    code, payload, stderr = run_json(SHARE_CLI, [
        "--deterministic",
        "export",
        "--bundle-type", "instance",
        "--artifact", manifest_path,
        "--bundle-id", "bundle.content.store.test",
        "--created-at", "2000-01-01T00:00:00Z",
        "--created-by", "tests",
        "--tool-version", "tests",
        "--out", bundle_root,
    ], env=env)
    if code != 0:
        raise AssertionError("instance export failed: {} {}".format(payload, stderr))
    code, payload, stderr = run_json(SHARE_CLI, [
        "--deterministic",
        "import",
        "--bundle", bundle_root,
        "--confirm",
        "--out", import_root,
        "--instance-id", "10000000-0000-0000-0000-000000000202",
    ], env=env)
    if code != 0:
        raise AssertionError("instance import failed: {} {}".format(payload, stderr))
    imported_manifest_path = os.path.join(import_root, "instance.manifest.json")
    imported_manifest = load_json(imported_manifest_path)
    original_manifest = load_json(manifest_path)
    pack_hash = imported_manifest.get("pack_lock_hash")
    embedded_pack_hash = load_json(os.path.join(import_root, "lockfiles", "capabilities.lock")).get("pack_hashes", {}).get("org.dominium.pack.core")
    if imported_manifest.get("mode") != "portable":
        raise AssertionError("portable roundtrip lost mode")
    if imported_manifest.get("pack_lock_hash") != original_manifest.get("pack_lock_hash"):
        raise AssertionError("portable roundtrip changed pack lock hash")
    if not os.path.isdir(os.path.join(import_root, "embedded_artifacts", "packs", embedded_pack_hash, "payload")):
        raise AssertionError("portable roundtrip missing embedded pack payload")
    code, payload, stderr = run_json(LAUNCHER_CLI, [
        "--deterministic",
        "preflight",
        "--install-manifest", os.path.join(install_root, "install.manifest.json"),
        "--instance-manifest", imported_manifest_path,
    ], env=env)
    if code != 0:
        raise AssertionError("portable roundtrip preflight failed: {} {}".format(payload, stderr))
    if payload.get("compat_report", {}).get("compatibility_mode") != "full":
        raise AssertionError("portable roundtrip preflight should be full")


def test_cross_platform_store_hash_match(tmp_root: str) -> None:
    windows_like = {
        "artifact_path": "embedded_artifacts\\packs\\hash\\payload",
        "manifest_ref": "instance\\instance.manifest.json",
        "extensions": {},
    }
    posix_like = {
        "artifact_path": "embedded_artifacts/packs/hash/payload",
        "manifest_ref": "instance/instance.manifest.json",
        "extensions": {},
    }
    if canonical_sha256(windows_like) != canonical_sha256(posix_like):
        raise AssertionError("cross-platform canonical hash mismatch")


def main() -> int:
    parser = argparse.ArgumentParser(description="LIB-0 content store tests")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    os.chdir(os.path.abspath(args.repo_root))
    with tempfile.TemporaryDirectory() as tmp_root:
        test_store_add_deterministic_hash(tmp_root)
        test_duplicate_artifact_no_duplicate_write(tmp_root)
        test_instance_clone_linked_no_duplication(tmp_root)
        test_portable_export_import_roundtrip(tmp_root)
        test_cross_platform_store_hash_match(tmp_root)
    print("LIB-0 content store tests OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
