import argparse
import json
import os
import subprocess
import sys
import tempfile

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.lib.instance import deterministic_fingerprint, validate_instance_manifest


OPS_CLI = os.path.join("tools", "ops", "ops_cli.py")


def run_ops(args, env=None):
    cmd = [sys.executable, OPS_CLI] + list(args or [])
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    payload = {}
    out = proc.stdout.decode("utf-8", errors="ignore").strip()
    if out:
        payload = json.loads(out)
    return proc.returncode, payload, proc.stderr.decode("utf-8", errors="ignore")


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


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


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def test_instance_manifest_valid(tmp_root):
    install_root = os.path.join(tmp_root, "install")
    instance_root = os.path.join(tmp_root, "instance")
    os.makedirs(install_root, exist_ok=True)
    install_manifest = os.path.join(install_root, "install.manifest.json")
    make_install_manifest(install_manifest, "install.test.valid")

    code, payload, _stderr = run_ops([
        "--deterministic",
        "instances", "create",
        "--install-manifest", install_manifest,
        "--data-root", instance_root,
        "--instance-id", "instance.test.valid",
        "--save-ref", "save.alpha",
        "--last-opened-save-id", "save.alpha",
    ])
    if code != 0 or payload.get("result") != "ok":
        raise RuntimeError("instance create failed")

    manifest_path = os.path.join(instance_root, "instance.manifest.json")
    manifest = load_json(manifest_path)
    for field in (
        "instance_id",
        "instance_kind",
        "mode",
        "install_ref",
        "pack_lock_hash",
        "profile_bundle_hash",
        "mod_policy_id",
        "overlay_conflict_policy_id",
        "default_session_template_id",
        "seed_policy",
        "instance_settings",
        "save_refs",
        "deterministic_fingerprint",
        "extensions",
    ):
        if field not in manifest:
            raise RuntimeError("missing instance field %s" % field)
    report = validate_instance_manifest(repo_root=REPO_ROOT_HINT, instance_manifest_path=manifest_path)
    if report.get("result") != "complete":
        raise RuntimeError("instance manifest validation failed: %s" % report)


def test_clone_deterministic(tmp_root):
    install_root = os.path.join(tmp_root, "install")
    source_root = os.path.join(tmp_root, "source")
    clone_a_root = os.path.join(tmp_root, "clone_a")
    clone_b_root = os.path.join(tmp_root, "clone_b")
    os.makedirs(install_root, exist_ok=True)
    install_manifest = os.path.join(install_root, "install.manifest.json")
    make_install_manifest(install_manifest, "install.test.clone")

    code, payload, _stderr = run_ops([
        "--deterministic",
        "instances", "create",
        "--install-manifest", install_manifest,
        "--data-root", source_root,
        "--instance-id", "instance.test.clone.source",
    ])
    if code != 0 or payload.get("result") != "ok":
        raise RuntimeError("source instance create failed")

    source_manifest = os.path.join(source_root, "instance.manifest.json")
    code, payload, _stderr = run_ops([
        "--deterministic",
        "instances", "clone",
        "--source-manifest", source_manifest,
        "--data-root", clone_a_root,
    ])
    if code != 0 or payload.get("result") != "ok":
        raise RuntimeError("deterministic clone A failed")
    clone_a_manifest = load_json(os.path.join(clone_a_root, "instance.manifest.json"))

    code, payload, _stderr = run_ops([
        "--deterministic",
        "instances", "clone",
        "--source-manifest", source_manifest,
        "--data-root", clone_b_root,
    ])
    if code != 0 or payload.get("result") != "ok":
        raise RuntimeError("deterministic clone B failed")
    clone_b_manifest = load_json(os.path.join(clone_b_root, "instance.manifest.json"))

    if clone_a_manifest.get("instance_id") != clone_b_manifest.get("instance_id"):
        raise RuntimeError("deterministic clone instance_id mismatch")


def test_cross_platform_instance_hash_match(tmp_root):
    install_root = os.path.join(tmp_root, "install_hash")
    instance_root = os.path.join(tmp_root, "instance_hash")
    os.makedirs(install_root, exist_ok=True)
    install_manifest = os.path.join(install_root, "install.manifest.json")
    make_install_manifest(install_manifest, "install.test.hash")

    code, payload, _stderr = run_ops([
        "--deterministic",
        "instances", "create",
        "--install-manifest", install_manifest,
        "--data-root", instance_root,
        "--instance-id", "instance.test.hash",
    ])
    if code != 0 or payload.get("result") != "ok":
        raise RuntimeError("instance create failed for hash test")

    manifest_path = os.path.join(instance_root, "instance.manifest.json")
    manifest = load_json(manifest_path)
    mutated = json.loads(json.dumps(manifest))
    install_ref = mutated.get("install_ref") or {}
    if isinstance(install_ref, dict):
        for key in ("manifest_ref", "root_path"):
            if install_ref.get(key):
                install_ref[key] = str(install_ref[key]).replace("/", "\\")
    for row in mutated.get("embedded_artifacts") or []:
        if isinstance(row, dict) and row.get("artifact_path"):
            row["artifact_path"] = str(row["artifact_path"]).replace("/", "\\")
    settings = mutated.get("instance_settings") or {}
    if isinstance(settings, dict) and settings.get("data_root"):
        settings["data_root"] = str(settings["data_root"]).replace("/", "\\")
    if mutated.get("capability_lockfile"):
        mutated["capability_lockfile"] = str(mutated["capability_lockfile"]).replace("/", "\\")
    if deterministic_fingerprint(mutated) != manifest.get("deterministic_fingerprint"):
        raise RuntimeError("instance fingerprint changed across path separators")


def main():
    parser = argparse.ArgumentParser(description="Instance manifest validation tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    os.chdir(repo_root)

    with tempfile.TemporaryDirectory() as tmp_root:
        test_instance_manifest_valid(tmp_root)
        test_clone_deterministic(tmp_root)
        test_cross_platform_instance_hash_match(tmp_root)

    print("instance manifest tests: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
