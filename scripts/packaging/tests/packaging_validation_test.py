#!/usr/bin/env python3
from __future__ import print_function

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile


def _repo_root_from_script():
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.normpath(os.path.join(here, os.pardir, os.pardir, os.pardir))


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _run(cmd, env=None, cwd=None):
    sys.stdout.flush()
    subprocess.check_call(cmd, env=env, cwd=cwd)


def _must_exist(path):
    if not os.path.exists(path):
        raise RuntimeError("missing: %s" % path)


def _assert_layout(artifact_root):
    exe = ".exe" if os.name == "nt" else ""
    for rel in (
        os.path.join("setup", "manifests", "product.dsumanifest"),
        os.path.join("setup", "artifact_manifest.json"),
        os.path.join("setup", "SHA256SUMS"),
        os.path.join("docs", "LICENSE"),
        os.path.join("docs", "README"),
        os.path.join("docs", "VERSION"),
        os.path.join("payloads", "launcher", "bin", "dominium-launcher" + exe),
        os.path.join("payloads", "runtime", "bin", "dominium_game" + exe),
        os.path.join("payloads", "tools", "tools", "README.txt"),
    ):
        _must_exist(os.path.join(artifact_root, rel))
    _must_exist(os.path.join(artifact_root, "payloads", "packs", "base", "repo", "mods", "base_demo"))


def _read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _dry_run_install(artifact_root):
    setup_dir = os.path.join(artifact_root, "setup")
    exe = "dominium-setup.exe" if os.name == "nt" else "dominium-setup"
    cli = os.path.join(setup_dir, exe)
    _must_exist(cli)

    manifest = os.path.join(setup_dir, "manifests", "product.dsumanifest")
    plan = os.path.join(artifact_root, "_test_install.dsuplan")

    _run([cli, "plan", "--manifest", manifest, "--op", "install", "--scope", "user", "--out", plan], cwd=artifact_root)
    _run([cli, "apply", "--plan", plan, "--dry-run"], cwd=artifact_root)


def _extract_zip(zip_path, out_dir):
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(out_dir)


def _extract_tgz(tgz_path, out_dir):
    with tarfile.open(tgz_path, "r:gz") as tf:
        tf.extractall(out_dir)


def main():
    ap = argparse.ArgumentParser(description="Packaging pipeline validation (Plan S-8).")
    ap.add_argument("--build-dir", required=True, help="CMake build directory to package from")
    ap.add_argument("--version", required=True, help="Artifact/product version")
    ap.add_argument("--manifest-template", required=True, help="Manifest template JSON path")
    ap.add_argument("--source-date-epoch", default="946684800", help="SOURCE_DATE_EPOCH for reproducible packaging (default: 946684800)")
    args = ap.parse_args()

    repo_root = _repo_root_from_script()
    pipeline = os.path.join(repo_root, "scripts", "packaging", "pipeline.py")

    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = str(int(args.source_date_epoch))

    work = tempfile.mkdtemp(prefix="dominium_packaging_test_")
    try:
        a_root = os.path.join(work, "a", "artifact_root")
        b_root = os.path.join(work, "b", "artifact_root")

        _run([sys.executable, pipeline, "assemble",
              "--build-dir", os.path.abspath(args.build_dir),
              "--out", a_root,
              "--version", args.version,
              "--manifest-template", os.path.abspath(args.manifest_template),
              "--reproducible"], env=env)

        _run([sys.executable, pipeline, "assemble",
              "--build-dir", os.path.abspath(args.build_dir),
              "--out", b_root,
              "--version", args.version,
              "--manifest-template", os.path.abspath(args.manifest_template),
              "--reproducible"], env=env)

        _assert_layout(a_root)
        _assert_layout(b_root)

        a_port = os.path.join(work, "a", "portable")
        b_port = os.path.join(work, "b", "portable")
        os.makedirs(a_port, exist_ok=True)
        os.makedirs(b_port, exist_ok=True)

        _run([sys.executable, pipeline, "portable", "--artifact", a_root, "--out", a_port, "--version", args.version, "--reproducible"], env=env)
        _run([sys.executable, pipeline, "portable", "--artifact", b_root, "--out", b_port, "--version", args.version, "--reproducible"], env=env)

        a_zip = os.path.join(a_port, "dominium-%s.zip" % args.version)
        b_zip = os.path.join(b_port, "dominium-%s.zip" % args.version)
        a_tgz = os.path.join(a_port, "dominium-%s.tar.gz" % args.version)
        b_tgz = os.path.join(b_port, "dominium-%s.tar.gz" % args.version)

        if _sha256_file(a_zip) != _sha256_file(b_zip):
            raise RuntimeError("portable zip not reproducible")
        if _sha256_file(a_tgz) != _sha256_file(b_tgz):
            raise RuntimeError("portable tar.gz not reproducible")

        # Dry-run install from extracted portable artifacts.
        ex_zip = os.path.join(work, "extract_zip")
        ex_tgz = os.path.join(work, "extract_tgz")
        os.makedirs(ex_zip, exist_ok=True)
        os.makedirs(ex_tgz, exist_ok=True)

        _extract_zip(a_zip, ex_zip)
        _extract_tgz(a_tgz, ex_tgz)

        _dry_run_install(os.path.join(ex_zip, "artifact_root"))
        _dry_run_install(os.path.join(ex_tgz, "artifact_root"))

        # Steam depot staging + dry-run install from depot root.
        steam_out = os.path.join(work, "steam")
        _run([sys.executable, pipeline, "steam", "--artifact", a_root, "--out", steam_out, "--version", args.version, "--appid", "0", "--depotid", "0", "--reproducible"], env=env)
        _dry_run_install(os.path.join(steam_out, "depots", "0"))

        # Verify artifact manifest has stable layout digest key.
        am = _read_json(os.path.join(a_root, "setup", "artifact_manifest.json"))
        if "layout_sha256" not in am:
            raise RuntimeError("artifact_manifest.json missing layout_sha256")

        print("packaging validation: OK")
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
