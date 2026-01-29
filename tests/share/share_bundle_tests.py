import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile


SHARE_CLI = os.path.join("tools", "share", "share_cli.py")


def run_share(args, env=None):
    cmd = [sys.executable, SHARE_CLI] + args
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    payload = {}
    if result.stdout.strip():
        payload = json.loads(result.stdout)
    return result.returncode, payload, result.stderr


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


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

    print("SHARE-0 bundle tests OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
