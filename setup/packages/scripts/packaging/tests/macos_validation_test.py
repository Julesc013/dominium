#!/usr/bin/env python3
from __future__ import print_function

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile


def _run(cmd, env=None, cwd=None):
    sys.stdout.flush()
    subprocess.check_call(cmd, cwd=cwd, env=env)


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _build_target(build_dir, target, config, env):
    cmd = ["cmake", "--build", build_dir, "--target", target]
    if config:
        cmd += ["--config", config]
    _run(cmd, env=env)


def _copy_outputs(src_dir, dst_dir, version):
    pkg = os.path.join(src_dir, "DominiumSetup-%s.pkg" % version)
    dmg = os.path.join(src_dir, "DominiumSetup-%s.dmg" % version)
    if not os.path.exists(pkg) or not os.path.exists(dmg):
        raise RuntimeError("missing pkg/dmg outputs under %s" % src_dir)
    os.makedirs(dst_dir, exist_ok=True)
    pkg_out = os.path.join(dst_dir, os.path.basename(pkg))
    dmg_out = os.path.join(dst_dir, os.path.basename(dmg))
    shutil.copy2(pkg, pkg_out)
    shutil.copy2(dmg, dmg_out)
    return pkg_out, dmg_out


def main():
    ap = argparse.ArgumentParser(description="macOS PKG/DMG reproducibility test.")
    ap.add_argument("--build-dir", required=True, help="CMake build directory")
    ap.add_argument("--version", required=True, help="Version string")
    ap.add_argument("--config", default="", help="CMake build config (multi-config generators)")
    args = ap.parse_args()

    if sys.platform != "darwin":
        print("skip: not on macOS")
        return 0

    build_dir = os.path.abspath(args.build_dir)
    dist_dir = os.path.join(build_dir, "dist", "macos")

    epoch = os.environ.get("SOURCE_DATE_EPOCH", "946684800")
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = epoch

    tmp = tempfile.mkdtemp(prefix="dominium_macos_pkg_test_")
    try:
        shutil.rmtree(dist_dir, ignore_errors=True)
        _build_target(build_dir, "package-macos", args.config, env)
        pkg_a, dmg_a = _copy_outputs(dist_dir, os.path.join(tmp, "a"), args.version)

        shutil.rmtree(dist_dir, ignore_errors=True)
        _build_target(build_dir, "package-macos", args.config, env)
        pkg_b, dmg_b = _copy_outputs(dist_dir, os.path.join(tmp, "b"), args.version)

        if _sha256(pkg_a) != _sha256(pkg_b):
            raise RuntimeError("pkg not reproducible")
        if _sha256(dmg_a) != _sha256(dmg_b):
            raise RuntimeError("dmg not reproducible")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("macos validation: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
