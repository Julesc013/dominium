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


def _read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _msi_open(path):
    import msilib
    return msilib.OpenDatabase(path, msilib.MSIDBOPEN_READONLY)


def _msi_table_strings(db, table, column):
    view = db.OpenView("SELECT `%s` FROM `%s`" % (column, table))
    view.Execute(None)
    values = []
    while True:
        rec = view.Fetch()
        if rec is None:
            break
        values.append(rec.GetString(1))
    return values


def _msi_table_kv(db, table, key_col, value_col):
    view = db.OpenView("SELECT `%s`,`%s` FROM `%s`" % (key_col, value_col, table))
    view.Execute(None)
    out = {}
    while True:
        rec = view.Fetch()
        if rec is None:
            break
        out[rec.GetString(1)] = rec.GetString(2)
    return out


def _build_target(build_dir, target, config):
    cmd = ["cmake", "--build", build_dir, "--target", target]
    if config:
        cmd += ["--config", config]
    _run(cmd)


def _find_msi(build_dir, version, arch):
    msi_dir = os.path.join(build_dir, "dist", "installers", "windows", "msi")
    name = "DominiumSetup-%s-%s.msi" % (version, arch)
    path = os.path.join(msi_dir, name)
    return path if os.path.exists(path) else None


def _msi_properties_ok(msi_path, platform):
    db = _msi_open(msi_path)
    props = _msi_table_kv(db, "Property", "Property", "Value")
    required = {
        "DSU_OPERATION",
        "DSU_SCOPE",
        "DSU_PLATFORM",
        "DSU_DETERMINISTIC",
        "DSU_INVOCATION_PATH",
        "DSU_FRONTEND_ID",
    }
    missing = sorted([p for p in required if p not in props])
    if missing:
        raise RuntimeError("missing MSI properties: %s" % ", ".join(missing))
    if props.get("DSU_PLATFORM") != platform:
        raise RuntimeError("DSU_PLATFORM mismatch: %s" % props.get("DSU_PLATFORM"))


def _msi_features_ok(msi_path, manifest_json):
    db = _msi_open(msi_path)
    features = sorted(_msi_table_strings(db, "Feature", "Feature"))
    comp_ids = sorted([c["component_id"] for c in manifest_json.get("components", [])])
    if features != comp_ids:
        raise RuntimeError("Feature table mismatch: %s vs %s" % (features, comp_ids))


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
    data = json.loads(out.decode("utf-8"))
    return data["details"]["invocation_digest64"]


def _run_msi(msi_path, install_root, inv_path):
    cmd = [
        "msiexec",
        "/i",
        msi_path,
        "/qn",
        "DSU_SCOPE=portable",
        "INSTALLDIR=%s" % install_root,
        "ALLUSERS=2",
        "MSIINSTALLPERUSER=1",
        "DSU_INVOCATION_PATH=%s" % inv_path,
    ]
    _run(cmd)


def _uninstall_msi(msi_path, install_root, inv_path):
    cmd = [
        "msiexec",
        "/x",
        msi_path,
        "/qn",
        "INSTALLDIR=%s" % install_root,
        "ALLUSERS=2",
        "MSIINSTALLPERUSER=1",
        "DSU_INVOCATION_PATH=%s" % inv_path,
    ]
    _run(cmd)


def _validate_arch(build_dir, version, arch, platform):
    msi_path = _find_msi(build_dir, version, arch)
    if not msi_path:
        print("skip %s: MSI not found" % arch)
        return

    manifest_json_path = os.path.join(build_dir, "dist", "msi", arch, "manifest.json")
    if not os.path.exists(manifest_json_path):
        raise RuntimeError("missing manifest json: %s" % manifest_json_path)

    manifest_json = _read_json(manifest_json_path)
    _msi_properties_ok(msi_path, platform)
    _msi_features_ok(msi_path, manifest_json)

    artifact_root = os.path.join(build_dir, "dist", "msi", arch, "artifact_root")
    setup_cli = os.path.join(artifact_root, "setup", "dominium-setup.exe")
    manifest_path = os.path.join(artifact_root, "setup", "manifests", "product.dsumanifest")
    if not os.path.exists(setup_cli):
        raise RuntimeError("missing setup cli: %s" % setup_cli)
    if not os.path.exists(manifest_path):
        raise RuntimeError("missing manifest: %s" % manifest_path)

    work = tempfile.mkdtemp(prefix="dominium_msi_test_%s_" % arch)
    try:
        install_root = os.path.join(work, "install")
        os.makedirs(install_root, exist_ok=True)
        msi_inv = os.path.join(work, "msi_invocation.tlv")
        _run_msi(msi_path, install_root, msi_inv)
        if not os.path.exists(msi_inv):
            raise RuntimeError("MSI did not emit invocation payload")

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
            "--ui-mode", "gui",
            "--frontend-id", "msi",
            "--out", cli_inv,
        ], cwd=work)

        digest_cli = _plan_digest(setup_cli, manifest_path, cli_inv, work)
        digest_msi = _plan_digest(setup_cli, manifest_path, msi_inv, work)
        if digest_cli != digest_msi:
            raise RuntimeError("invocation digest mismatch (%s vs %s)" % (digest_cli, digest_msi))

        msi_inv_un = os.path.join(work, "msi_invocation_uninstall.tlv")
        _uninstall_msi(msi_path, install_root, msi_inv_un)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description="MSI validation test (build, tables, invocation parity).")
    ap.add_argument("--build-dir", required=True, help="CMake build directory")
    ap.add_argument("--version", required=True, help="MSI version")
    ap.add_argument("--config", default="", help="CMake build config (for multi-config generators)")
    args = ap.parse_args()

    if not sys.platform.startswith("win"):
        print("skip: not on Windows")
        return 0

    if not shutil.which("msiexec"):
        print("skip: msiexec missing")
        return 0

    for arch, platform in (("x86", "win32-x86"), ("x64", "win64-x64")):
        _build_target(args.build_dir, "msi-%s" % arch, args.config)
        _validate_arch(args.build_dir, args.version, arch, platform)

    print("msi validation: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
