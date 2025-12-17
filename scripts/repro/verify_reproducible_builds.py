#!/usr/bin/env python3
from __future__ import print_function

import argparse
import hashlib
import os
import shutil
import subprocess
import sys


def _repo_root_from_script():
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.normpath(os.path.join(here, os.pardir, os.pardir))


def _run(cmd, cwd=None):
    print("+", " ".join(cmd))
    sys.stdout.flush()
    subprocess.check_call(cmd, cwd=cwd)


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _walk_candidates(root_dir, want_name_lower):
    for cur_root, dirs, files in os.walk(root_dir):
        base = os.path.basename(cur_root)
        if base in ("CMakeFiles", "Testing", ".git", ".idea", ".vscode"):
            dirs[:] = []
            continue
        for fn in files:
            if fn.lower() == want_name_lower:
                yield os.path.join(cur_root, fn)


def _find_unique_file(root_dir, filename):
    want = filename.lower()
    hits = list(_walk_candidates(root_dir, want))
    if len(hits) == 1:
        return hits[0]
    if not hits:
        raise RuntimeError("not found: %s under %s" % (filename, root_dir))
    raise RuntimeError("ambiguous (%d matches) for %s under %s:\n%s"
                       % (len(hits), filename, root_dir, "\n".join(hits)))


def main():
    ap = argparse.ArgumentParser(description="Build twice and compare output file hashes (best-effort reproducible build check).")
    ap.add_argument("--cmake", default="cmake", help="CMake executable (default: cmake)")
    ap.add_argument("--generator", default="", help="CMake generator (optional, e.g. Ninja)")
    ap.add_argument("--build-type", default="Release", help="CMAKE_BUILD_TYPE (default: Release)")
    ap.add_argument("--build-root", default=os.path.join("build", "repro_compare"), help="Root build dir (default: build/repro_compare)")
    ap.add_argument("--target", action="append", default=[], help="CMake target to build (repeatable)")
    ap.add_argument("--define", action="append", default=[], help="Extra -DKEY=VALUE (repeatable)")
    ap.add_argument("--keep", action="store_true", help="Do not delete build dirs on failure")
    args = ap.parse_args()

    repo_root = _repo_root_from_script()
    build_root = os.path.abspath(os.path.join(repo_root, args.build_root))
    build_a = os.path.join(build_root, "a")
    build_b = os.path.join(build_root, "b")

    targets = args.target[:]
    if not targets:
        targets = ["dominium-launcher", "dominium_game", "dominium-setup"]

    def _clean_dir(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        os.makedirs(path)

    try:
        _clean_dir(build_a)
        _clean_dir(build_b)

        def _configure(build_dir):
            cmd = [args.cmake, "-S", repo_root, "-B", build_dir, "-DCMAKE_BUILD_TYPE=%s" % args.build_type,
                   "-DDOMINIUM_ENABLE_REPRODUCIBLE_BUILD=ON", "-DDOM_DISALLOW_DOWNLOADS=ON"]
            if args.generator:
                cmd.extend(["-G", args.generator])
            for d in args.define:
                cmd.append("-D%s" % d)
            _run(cmd)

        _configure(build_a)
        _configure(build_b)

        def _build(build_dir):
            cmd = [args.cmake, "--build", build_dir]
            for t in targets:
                cmd.extend(["--target", t])
            _run(cmd)

        _build(build_a)
        _build(build_b)

        # Compare key binaries by content hash.
        exe_ext = ".exe" if os.name == "nt" else ""
        outputs = [
            ("dominium-launcher%s" % exe_ext, "launcher"),
            ("dominium_game%s" % exe_ext, "game"),
            ("dominium-setup%s" % exe_ext, "setup"),
        ]

        a_hashes = {}
        b_hashes = {}
        for filename, label in outputs:
            pa = _find_unique_file(build_a, filename)
            pb = _find_unique_file(build_b, filename)
            a_hashes[label] = (pa, _sha256_file(pa))
            b_hashes[label] = (pb, _sha256_file(pb))

        failed = False
        for label in sorted(a_hashes.keys()):
            ha = a_hashes[label][1]
            hb = b_hashes[label][1]
            if ha != hb:
                failed = True
                print("MISMATCH:", label)
                print("  a:", a_hashes[label][0])
                print("     sha256:", ha)
                print("  b:", b_hashes[label][0])
                print("     sha256:", hb)

        if failed:
            print("repro check: FAIL")
            return 1
        print("repro check: OK")
        return 0
    except Exception as e:
        print("repro check: ERROR:", str(e))
        if args.keep:
            print("build dirs kept:", build_root)
        else:
            try:
                if os.path.isdir(build_root):
                    shutil.rmtree(build_root)
            except Exception:
                pass
        return 2


if __name__ == "__main__":
    sys.exit(main())

