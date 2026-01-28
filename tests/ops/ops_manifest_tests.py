import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile


OPS_CLI = os.path.join("tools", "ops", "ops_cli.py")


def run_ops(args, env=None):
    cmd = [sys.executable, OPS_CLI] + args
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    payload = {}
    if result.stdout.strip():
        payload = json.loads(result.stdout)
    return result.returncode, payload, result.stderr


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


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


def make_sandbox_policy(path, allowed, denied):
    payload = {
        "allowed_paths": allowed,
        "denied_paths": denied,
        "network_policy": "offline",
        "pack_source_whitelist": [],
        "cpu_budget": 1,
        "memory_budget": 1,
        "io_budget": 1,
        "extensions": {},
    }
    write_json(path, payload)


def assert_ok(result, payload, label):
    if result != 0 or payload.get("result") != "ok":
        raise AssertionError("{} failed: {}".format(label, payload))


def assert_refused(result, payload, code_id, label):
    if result == 0:
        raise AssertionError("{} expected refusal".format(label))
    refusal = payload.get("compat_report", {}).get("refusal", {})
    if refusal.get("code_id") != code_id:
        raise AssertionError("{} refusal mismatch: {}".format(label, refusal))


def test_multiple_installs(tmp_root):
    install_a = os.path.join(tmp_root, "install_a")
    install_b = os.path.join(tmp_root, "install_b")
    os.makedirs(install_a, exist_ok=True)
    os.makedirs(install_b, exist_ok=True)
    make_install_manifest(os.path.join(install_a, "install.manifest.json"),
                          "00000000-0000-0000-0000-000000000001",
                          install_a)
    make_install_manifest(os.path.join(install_b, "install.manifest.json"),
                          "00000000-0000-0000-0000-000000000002",
                          install_b)

    code, payload, _ = run_ops(["installs", "list", "--search", tmp_root])
    assert_ok(code, payload, "installs list")
    installs = payload.get("installs", [])
    if len(installs) != 2:
        raise AssertionError("expected 2 installs, got {}".format(len(installs)))


def test_instances_share_install(tmp_root):
    install_root = os.path.join(tmp_root, "install_root")
    os.makedirs(install_root, exist_ok=True)
    make_install_manifest(os.path.join(install_root, "install.manifest.json"),
                          "00000000-0000-0000-0000-000000000003",
                          install_root)

    instance_a = os.path.join(tmp_root, "instance_a")
    instance_b = os.path.join(tmp_root, "instance_b")
    env = dict(os.environ)
    env["OPS_DETERMINISTIC"] = "1"

    code, payload, _ = run_ops([
        "instances", "create",
        "--install-manifest", os.path.join(install_root, "install.manifest.json"),
        "--data-root", instance_a,
        "--instance-id", "10000000-0000-0000-0000-000000000001",
        "--update-channel", "stable",
    ], env=env)
    assert_ok(code, payload, "instance create A")

    code, payload, _ = run_ops([
        "instances", "create",
        "--install-manifest", os.path.join(install_root, "install.manifest.json"),
        "--data-root", instance_b,
        "--instance-id", "10000000-0000-0000-0000-000000000002",
        "--update-channel", "stable",
    ], env=env)
    assert_ok(code, payload, "instance create B")

    code, payload, _ = run_ops([
        "instances", "create",
        "--install-manifest", os.path.join(install_root, "install.manifest.json"),
        "--data-root", instance_a,
        "--instance-id", "10000000-0000-0000-0000-000000000003",
        "--update-channel", "stable",
    ], env=env)
    assert_refused(code, payload, 5, "instance create duplicate root")


def test_instance_portability(tmp_root):
    install_root = os.path.join(tmp_root, "install_portable")
    os.makedirs(install_root, exist_ok=True)
    make_install_manifest(os.path.join(install_root, "install.manifest.json"),
                          "00000000-0000-0000-0000-000000000004",
                          install_root)

    instance_root = os.path.join(tmp_root, "portable_instance")
    env = dict(os.environ)
    env["OPS_DETERMINISTIC"] = "1"
    code, payload, _ = run_ops([
        "instances", "create",
        "--install-manifest", os.path.join(install_root, "install.manifest.json"),
        "--data-root", instance_root,
        "--instance-id", "10000000-0000-0000-0000-000000000010",
        "--update-channel", "stable",
    ], env=env)
    assert_ok(code, payload, "instance create portable")

    copied_root = os.path.join(tmp_root, "portable_copy")
    shutil.copytree(instance_root, copied_root)
    code, payload, _ = run_ops([
        "instances", "list",
        "--search", copied_root,
    ])
    assert_ok(code, payload, "instance list portable")
    if not payload.get("instances"):
        raise AssertionError("portable instance not discovered")


def test_transaction_rollback(tmp_root):
    install_root = os.path.join(tmp_root, "install_rollback")
    os.makedirs(install_root, exist_ok=True)
    make_install_manifest(os.path.join(install_root, "install.manifest.json"),
                          "00000000-0000-0000-0000-000000000005",
                          install_root)
    instance_root = os.path.join(tmp_root, "rollback_instance")
    env = dict(os.environ)
    env["OPS_DETERMINISTIC"] = "1"
    code, payload, _ = run_ops([
        "--transaction-id", "tx-rollback",
        "instances", "create",
        "--install-manifest", os.path.join(install_root, "install.manifest.json"),
        "--data-root", instance_root,
        "--instance-id", "10000000-0000-0000-0000-000000000020",
        "--update-channel", "stable",
        "--simulate-failure", "stage",
    ], env=env)
    assert_refused(code, payload, 1, "rollback simulate")
    manifest_path = os.path.join(instance_root, "instance.manifest.json")
    if os.path.exists(manifest_path):
        raise AssertionError("rollback left manifest behind")
    log_path = os.path.join(instance_root, "ops", "ops.log")
    if not os.path.isfile(log_path):
        raise AssertionError("rollback missing ops log")


def test_sandbox_refusal(tmp_root):
    install_root = os.path.join(tmp_root, "install_sandbox")
    os.makedirs(install_root, exist_ok=True)
    make_install_manifest(os.path.join(install_root, "install.manifest.json"),
                          "00000000-0000-0000-0000-000000000006",
                          install_root)
    sandbox_path = os.path.join(tmp_root, "sandbox.policy.json")
    make_sandbox_policy(sandbox_path, allowed=[], denied=[tmp_root])
    instance_root = os.path.join(tmp_root, "sandbox_instance")
    code, payload, _ = run_ops([
        "instances", "create",
        "--install-manifest", os.path.join(install_root, "install.manifest.json"),
        "--data-root", instance_root,
        "--instance-id", "10000000-0000-0000-0000-000000000030",
        "--update-channel", "stable",
        "--sandbox-policy", sandbox_path,
    ])
    assert_refused(code, payload, 2, "sandbox refusal")


def main():
    parser = argparse.ArgumentParser(description="OPS-0 manifest tests")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    os.chdir(repo_root)

    with tempfile.TemporaryDirectory() as tmp_root:
        test_multiple_installs(tmp_root)
        test_instances_share_install(tmp_root)
        test_instance_portability(tmp_root)
        test_transaction_rollback(tmp_root)
        test_sandbox_refusal(tmp_root)

    print("OPS-0 manifest tests OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
