#!/usr/bin/env python3
from __future__ import print_function

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile


def _run(cmd, cwd=None):
    sys.stdout.flush()
    subprocess.check_call(cmd, cwd=cwd)


def _run_allow(cmd, cwd=None, allowed=(0, 1)):
    sys.stdout.flush()
    rc = subprocess.call(cmd, cwd=cwd)
    if rc not in allowed:
        raise RuntimeError("command failed (%s): %s" % (rc, " ".join(cmd)))
    return rc


def _read_json_bytes(data):
    return json.loads(data.decode("utf-8"))


def _build_target(build_dir, target, config):
    cmd = ["cmake", "--build", build_dir, "--target", target]
    if config:
        cmd += ["--config", config]
    _run(cmd)


def _plan_digest(setup_cli, manifest_path, invocation_path, work_dir):
    plan_path = os.path.join(work_dir, "plan.dsuplan")
    cmd = [
        setup_cli,
        "--deterministic", "1",
        "plan",
        "--manifest", manifest_path,
        "--invocation", invocation_path,
        "--out", plan_path,
        "--format", "json",
    ]
    out = subprocess.check_output(cmd, cwd=work_dir)
    data = _read_json_bytes(out)
    return data["details"]["invocation_digest64"]


def _exe_path(build_dir, name):
    return os.path.join(build_dir, "dist", "windows", name)


def _validate_arch(build_dir, exe_name, platform, frontend_id, config):
    exe_path = _exe_path(build_dir, exe_name)
    if not os.path.exists(exe_path):
        print("skip: missing %s" % exe_path)
        return

    artifact_root = os.path.join(build_dir, "dist", "artifact_root")
    setup_cli = os.path.join(artifact_root, "setup", "dominium-setup-legacy.exe")
    manifest_path = os.path.join(artifact_root, "setup", "manifests", "product.dsumanifest")
    if not os.path.exists(setup_cli):
        fallback = os.path.join(artifact_root, "setup", "tool_setup.exe")
        if os.path.exists(fallback):
            setup_cli = fallback
        else:
            print("skip: missing legacy setup cli: %s" % setup_cli)
            return
    if not os.path.exists(manifest_path):
        raise RuntimeError("missing manifest: %s" % manifest_path)

    work = tempfile.mkdtemp(prefix="dominium_exe_test_")
    try:
        install_root = os.path.join(work, "install")
        os.makedirs(install_root, exist_ok=True)

        exe_inv = os.path.join(work, "exe_invocation.tlv")
        _run([
            exe_path,
            "--cli", "export-invocation",
            "--manifest", manifest_path,
            "--op", "install",
            "--scope", "portable",
            "--platform", platform,
            "--install-root", install_root,
            "--ui-mode", "cli",
            "--frontend-id", frontend_id,
            "--out", exe_inv,
            "--deterministic", "1",
        ], cwd=work)

        cli_inv = os.path.join(work, "cli_invocation.tlv")
        _run([
            setup_cli,
            "--deterministic", "1",
            "export-invocation",
            "--manifest", manifest_path,
            "--op", "install",
            "--scope", "portable",
            "--platform", platform,
            "--install-root", install_root,
            "--ui-mode", "cli",
            "--frontend-id", frontend_id,
            "--out", cli_inv,
        ], cwd=work)

        digest_cli = _plan_digest(setup_cli, manifest_path, cli_inv, work)
        digest_exe = _plan_digest(setup_cli, manifest_path, exe_inv, work)
        if digest_cli != digest_exe:
            raise RuntimeError("invocation digest mismatch (%s vs %s)" % (digest_cli, digest_exe))

        _run_allow([exe_path, "--cli", "detect", "--manifest", manifest_path, "--install-root", install_root], cwd=work)

        plan_out = os.path.join(work, "plan.dsuplan")
        _run([
            exe_path,
            "--cli", "plan",
            "--manifest", manifest_path,
            "--op", "install",
            "--scope", "portable",
            "--platform", platform,
            "--install-root", install_root,
            "--out", plan_out,
            "--deterministic", "1",
            "--dry-run",
        ], cwd=work)

        _run([
            exe_path,
            "--cli", "apply",
            "--manifest", manifest_path,
            "--op", "install",
            "--scope", "portable",
            "--platform", platform,
            "--install-root", install_root,
            "--deterministic", "1",
            "--dry-run",
        ], cwd=work)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description="EXE validation test (parity + smoke).")
    ap.add_argument("--build-dir", required=True, help="CMake build directory")
    ap.add_argument("--version", required=True, help="Version string")
    ap.add_argument("--config", default="", help="CMake build config (multi-config generators)")
    args = ap.parse_args()

    if not sys.platform.startswith("win"):
        print("skip: not on Windows")
        return 0

    _build_target(args.build_dir, "setup_exe_win32_nt", args.config)
    _build_target(args.build_dir, "setup_exe_win64", args.config)

    _validate_arch(args.build_dir, "DominiumSetup-win32.exe", "win32-x86", "exe-win32", args.config)
    _validate_arch(args.build_dir, "DominiumSetup-win64.exe", "win64-x64", "exe-win64", args.config)

    print("exe validation: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
