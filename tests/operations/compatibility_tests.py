import argparse
import json
import os
import subprocess
import sys


OPS_CLI = os.path.join("tools", "ops", "ops_cli.py")


def run_ops(args, env=None):
    cmd = [sys.executable, OPS_CLI] + args
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    payload = {}
    if result.stdout.strip():
        payload = json.loads(result.stdout)
    return result.returncode, payload, result.stderr


def assert_mode(payload, expected_mode, label):
    report = payload.get("compat_report", {})
    mode = report.get("compatibility_mode")
    if mode != expected_mode:
        raise AssertionError("{} mode mismatch: {}".format(label, mode))


def assert_refused(payload, label):
    report = payload.get("compat_report", {})
    refusal = report.get("refusal", {})
    if refusal.get("code") != "REFUSE_CAPABILITY_MISSING":
        raise AssertionError("{} expected REFUSE_CAPABILITY_MISSING, got {}".format(label, refusal))


def test_client_server_missing_server():
    code, payload, _ = run_ops([
        "compat", "client-server",
        "--client-cap", "cap.shared",
        "--client-cap", "cap.required",
        "--server-cap", "cap.shared",
        "--required-cap", "cap.required",
    ])
    if code == 0:
        raise AssertionError("missing server caps should refuse")
    assert_mode(payload, "refuse", "missing server")
    assert_refused(payload, "missing server")


def test_client_server_missing_client_degraded():
    code, payload, _ = run_ops([
        "compat", "client-server",
        "--client-cap", "cap.shared",
        "--server-cap", "cap.shared",
        "--server-cap", "cap.required",
        "--required-cap", "cap.required",
    ])
    if code != 0:
        raise AssertionError("missing client caps should not refuse")
    assert_mode(payload, "degraded", "missing client")


def test_client_server_overlap_required():
    code, payload, _ = run_ops([
        "compat", "client-server",
        "--client-cap", "cap.client",
        "--server-cap", "cap.server",
    ])
    if code == 0:
        raise AssertionError("empty overlap should refuse")
    assert_mode(payload, "refuse", "overlap required")
    assert_refused(payload, "overlap required")


def test_shard_transfer_missing_target():
    code, payload, _ = run_ops([
        "compat", "shard-transfer",
        "--source-cap", "cap.shared",
        "--source-cap", "cap.required",
        "--target-cap", "cap.shared",
        "--required-cap", "cap.required",
    ])
    if code == 0:
        raise AssertionError("missing target caps should refuse")
    assert_mode(payload, "refuse", "shard transfer")
    assert_refused(payload, "shard transfer")


def test_tools_inspect_only():
    code, payload, _ = run_ops([
        "compat", "tools",
        "--required-cap", "cap.required",
    ])
    if code != 0:
        raise AssertionError("tools should return ok")
    assert_mode(payload, "inspect-only", "tools inspect")


def test_client_server_full():
    code, payload, _ = run_ops([
        "compat", "client-server",
        "--client-cap", "cap.shared",
        "--client-cap", "cap.required",
        "--server-cap", "cap.shared",
        "--server-cap", "cap.required",
        "--required-cap", "cap.required",
    ])
    if code != 0:
        raise AssertionError("full compatibility should be ok")
    assert_mode(payload, "full", "client server full")


def main():
    parser = argparse.ArgumentParser(description="OPS-1 compatibility tests")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    os.chdir(os.path.abspath(args.repo_root))

    test_client_server_missing_server()
    test_client_server_missing_client_degraded()
    test_client_server_overlap_required()
    test_shard_transfer_missing_target()
    test_tools_inspect_only()
    test_client_server_full()

    print("OPS-1 compatibility tests OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
