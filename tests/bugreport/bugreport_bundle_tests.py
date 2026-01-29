import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile


BUGREPORT_CLI = os.path.join("tools", "bugreport", "bugreport_cli.py")
SHARE_CLI = os.path.join("tools", "share", "share_cli.py")


def run_cli(cli, args, env=None):
    cmd = [sys.executable, cli] + args
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
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def sha256_dir(path):
    h = hashlib.sha256()
    for root, dirs, files in os.walk(path):
        dirs.sort()
        rel_root = os.path.relpath(root, path).replace("\\", "/")
        for name in sorted(files):
            rel_path = (rel_root + "/" + name) if rel_root != "." else name
            h.update(rel_path.encode("utf-8"))
            with open(os.path.join(root, name), "rb") as handle:
                for chunk in iter(lambda: handle.read(8192), b""):
                    h.update(chunk)
    return h.hexdigest()


def make_install_manifest(path, install_id, root):
    payload = {
        "install_id": install_id,
        "install_root": root,
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


def make_instance_manifest(path, install_id, instance_id, root):
    payload = {
        "instance_id": instance_id,
        "install_id": install_id,
        "data_root": root,
        "active_profiles": [],
        "active_modpacks": [],
        "capability_lockfile": "lockfiles/capabilities.lock",
        "sandbox_policy_ref": "sandbox.default",
        "update_channel": "stable",
        "created_at": "2000-01-01T00:00:00Z",
        "last_used_at": "2000-01-01T00:00:00Z",
        "extensions": {},
    }
    write_json(path, payload)


def make_runtime_descriptor(path, install_id, instance_id, runtime_id):
    payload = {
        "runtime_id": runtime_id,
        "install_id": install_id,
        "instance_id": instance_id,
        "role": "server",
        "capability_baseline": "BASELINE_MAINLINE_CORE",
        "sandbox_policy": "sandbox.default",
        "log_root": "logs",
        "ipc_endpoints": {
            "control": "ipc://control",
            "telemetry": "ipc://telemetry",
        },
        "launched_at": "2000-01-01T00:00:00Z",
        "extensions": {},
    }
    write_json(path, payload)


def make_compat_report(path, install_id, instance_id, runtime_id):
    payload = {
        "context": "run",
        "install_id": install_id,
        "instance_id": instance_id,
        "runtime_id": runtime_id,
        "capability_baseline": "BASELINE_MAINLINE_CORE",
        "required_capabilities": [],
        "provided_capabilities": [],
        "missing_capabilities": [],
        "compatibility_mode": "full",
        "refusal_codes": [],
        "mitigation_hints": [],
        "timestamp": "2000-01-01T00:00:00Z",
        "extensions": {},
    }
    write_json(path, payload)


def export_share_bundle(tmp_root, bundle_type, suffix):
    artifact = os.path.join(tmp_root, "{}_{}.bin".format(bundle_type, suffix))
    lockfile = os.path.join(tmp_root, "lock.json")
    write_text(artifact, "{}-{}-data".format(bundle_type, suffix))
    write_text(lockfile, "{\"lock\":true}")
    bundle_root = os.path.join(tmp_root, "{}_bundle_{}".format(bundle_type, suffix))
    code, _payload, _ = run_cli(SHARE_CLI, [
        "--deterministic",
        "export",
        "--bundle-type", bundle_type,
        "--artifact", artifact,
        "--lockfile", lockfile,
        "--bundle-id", "bundle.{}.{}.001".format(bundle_type, suffix),
        "--created-at", "2000-01-01T00:00:00Z",
        "--created-by", "test",
        "--tool-version", "test-tool",
        "--out", bundle_root,
    ])
    if code != 0:
        raise AssertionError("failed to export {} bundle".format(bundle_type))
    return bundle_root


def test_create_and_inspect(tmp_root):
    replay_bundle = export_share_bundle(tmp_root, "replay", "base")
    save_bundle = export_share_bundle(tmp_root, "save", "base")

    install_id = "00000000-0000-0000-0000-000000000101"
    instance_id = "00000000-0000-0000-0000-000000000102"
    runtime_id = "00000000-0000-0000-0000-000000000103"

    install_manifest = os.path.join(tmp_root, "install.manifest.json")
    instance_manifest = os.path.join(tmp_root, "instance.manifest.json")
    runtime_descriptor = os.path.join(tmp_root, "runtime.descriptor.json")
    compat_report = os.path.join(tmp_root, "compat_report.json")
    ops_log = os.path.join(tmp_root, "ops.log")
    refusal_summary = os.path.join(tmp_root, "refusal_summary.json")
    reporter_notes = os.path.join(tmp_root, "notes.txt")

    make_install_manifest(install_manifest, install_id, tmp_root)
    make_instance_manifest(instance_manifest, install_id, instance_id, tmp_root)
    make_runtime_descriptor(runtime_descriptor, install_id, instance_id, runtime_id)
    make_compat_report(compat_report, install_id, instance_id, runtime_id)
    write_text(ops_log, "{\"event\":\"ops\"}\n")
    write_json(refusal_summary, {"refusal_count": 0, "refusals": [], "extensions": {}})
    write_text(reporter_notes, "Repro steps here.")

    bug_root = os.path.join(tmp_root, "bugreport_bundle")
    code, payload, _ = run_cli(BUGREPORT_CLI, [
        "--deterministic",
        "create",
        "--replay-bundle", replay_bundle,
        "--save-bundle", save_bundle,
        "--install-manifest", install_manifest,
        "--instance-manifest", instance_manifest,
        "--runtime-descriptor", runtime_descriptor,
        "--compat-report", compat_report,
        "--ops-log", ops_log,
        "--refusal-summary", refusal_summary,
        "--reporter-notes", reporter_notes,
        "--bugreport-id", "bugreport.test.001",
        "--created-at", "2000-01-01T00:00:00Z",
        "--created-by", "test",
        "--tool-version", "test-tool",
        "--out", bug_root,
    ])
    if code != 0 or payload.get("result") != "ok":
        raise AssertionError("bugreport create failed: {}".format(payload))

    code, payload, _ = run_cli(BUGREPORT_CLI, ["inspect", "--bundle", bug_root])
    if code != 0 or payload.get("result") != "ok":
        raise AssertionError("bugreport inspect failed: {}".format(payload))


def test_redaction_preserves_replay(tmp_root):
    replay_bundle = export_share_bundle(tmp_root, "replay", "redact")
    original_hash = sha256_dir(replay_bundle)

    install_id = "00000000-0000-0000-0000-000000000201"
    instance_id = "00000000-0000-0000-0000-000000000202"
    runtime_id = "00000000-0000-0000-0000-000000000203"

    install_manifest = os.path.join(tmp_root, "install.manifest.json")
    instance_manifest = os.path.join(tmp_root, "instance.manifest.json")
    runtime_descriptor = os.path.join(tmp_root, "runtime.descriptor.json")
    compat_report = os.path.join(tmp_root, "compat_report.json")
    ops_log = os.path.join(tmp_root, "ops.log")

    make_install_manifest(install_manifest, install_id, "C:\\\\Users\\\\testuser\\\\install_root")
    make_instance_manifest(instance_manifest, install_id, instance_id, "C:\\\\Users\\\\testuser\\\\instance_root")
    make_runtime_descriptor(runtime_descriptor, install_id, instance_id, runtime_id)
    make_compat_report(compat_report, install_id, instance_id, runtime_id)
    write_text(ops_log, "user=testuser ip=192.168.0.10 path=C:\\\\Users\\\\testuser\\\\logs\n")

    bug_root = os.path.join(tmp_root, "bugreport_redact")
    code, payload, _ = run_cli(BUGREPORT_CLI, [
        "--deterministic",
        "create",
        "--replay-bundle", replay_bundle,
        "--install-manifest", install_manifest,
        "--instance-manifest", instance_manifest,
        "--runtime-descriptor", runtime_descriptor,
        "--compat-report", compat_report,
        "--ops-log", ops_log,
        "--redact-paths",
        "--redact-ips",
        "--redact-user", "testuser",
        "--out", bug_root,
    ])
    if code != 0 or payload.get("result") != "ok":
        raise AssertionError("bugreport create with redaction failed")

    redacted_replay = os.path.join(bug_root, "bundles", "replay")
    if sha256_dir(redacted_replay) != original_hash:
        raise AssertionError("redaction mutated replay bundle")

    redaction_summary = os.path.join(bug_root, "redaction", "redaction_summary.json")
    if not os.path.isfile(redaction_summary):
        raise AssertionError("missing redaction summary")


def test_corruption_refusal(tmp_root):
    replay_bundle = export_share_bundle(tmp_root, "replay", "corrupt")
    install_id = "00000000-0000-0000-0000-000000000301"
    instance_id = "00000000-0000-0000-0000-000000000302"
    runtime_id = "00000000-0000-0000-0000-000000000303"

    install_manifest = os.path.join(tmp_root, "install.manifest.json")
    instance_manifest = os.path.join(tmp_root, "instance.manifest.json")
    runtime_descriptor = os.path.join(tmp_root, "runtime.descriptor.json")
    compat_report = os.path.join(tmp_root, "compat_report.json")
    ops_log = os.path.join(tmp_root, "ops.log")

    make_install_manifest(install_manifest, install_id, tmp_root)
    make_instance_manifest(instance_manifest, install_id, instance_id, tmp_root)
    make_runtime_descriptor(runtime_descriptor, install_id, instance_id, runtime_id)
    make_compat_report(compat_report, install_id, instance_id, runtime_id)
    write_text(ops_log, "{\"event\":\"ops\"}\n")

    bug_root = os.path.join(tmp_root, "bugreport_corrupt")
    code, payload, _ = run_cli(BUGREPORT_CLI, [
        "--deterministic",
        "create",
        "--replay-bundle", replay_bundle,
        "--install-manifest", install_manifest,
        "--instance-manifest", instance_manifest,
        "--runtime-descriptor", runtime_descriptor,
        "--compat-report", compat_report,
        "--ops-log", ops_log,
        "--out", bug_root,
    ])
    if code != 0 or payload.get("result") != "ok":
        raise AssertionError("bugreport create failed")

    ops_dest = os.path.join(bug_root, "ops", "ops.log")
    write_text(ops_dest, "{\"event\":\"tampered\"}\n")

    code, payload, _ = run_cli(BUGREPORT_CLI, ["inspect", "--bundle", bug_root])
    if code == 0:
        raise AssertionError("inspect should refuse corrupted bundle")


def main():
    parser = argparse.ArgumentParser(description="BUG-0 bundle tests")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    os.chdir(os.path.abspath(args.repo_root))

    with tempfile.TemporaryDirectory() as tmp_root:
        test_create_and_inspect(tmp_root)
        test_redaction_preserves_replay(tmp_root)
        test_corruption_refusal(tmp_root)

    print("BUG-0 bugreport bundle tests OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
