#!/usr/bin/env python3
"""
Determinism test for scripts/diagnostics/make_support_bundle.py.

This creates a tiny synthetic launcher home with:
- a deterministic audit TLV (fixed run_id/timestamp, fixed toolchain_id reason)
- a minimal instance directory with placeholder TLV files and a run directory

It then generates the support bundle twice with the same SOURCE_DATE_EPOCH and
asserts the output archives are byte-identical.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tarfile
import zipfile


def _tlv_rec(tag: int, payload: bytes) -> bytes:
    return (
        int(tag).to_bytes(4, "little", signed=False)
        + int(len(payload)).to_bytes(4, "little", signed=False)
        + payload
    )


def _tlv_u32(tag: int, v: int) -> bytes:
    return _tlv_rec(tag, int(v).to_bytes(4, "little", signed=False))


def _tlv_u64(tag: int, v: int) -> bytes:
    return _tlv_rec(tag, int(v).to_bytes(8, "little", signed=False))


def _tlv_i32(tag: int, v: int) -> bytes:
    return _tlv_rec(tag, int(v).to_bytes(4, "little", signed=True))


def _tlv_str(tag: int, s: str) -> bytes:
    return _tlv_rec(tag, s.encode("utf-8"))


def _write(path: str, data: bytes) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def _hash_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _build_fixture(home: str, instance_id: str) -> str:
    # Instance tree.
    inst_root = os.path.join(home, "instances", instance_id)
    os.makedirs(os.path.join(inst_root, "config"), exist_ok=True)
    os.makedirs(os.path.join(inst_root, "logs"), exist_ok=True)
    os.makedirs(os.path.join(inst_root, "logs", "runs", "0000000000000001"), exist_ok=True)
    os.makedirs(os.path.join(inst_root, "staging"), exist_ok=True)
    os.makedirs(os.path.join(home, "logs"), exist_ok=True)

    # Placeholder TLVs (not parsed by bundler; only copied).
    _write(os.path.join(inst_root, "manifest.tlv"), b"manifest\x0a")
    _write(os.path.join(inst_root, "config", "config.tlv"), b"config\x0a")
    _write(os.path.join(inst_root, "logs", "launch_history.tlv"), b"history\x0a")
    _write(os.path.join(inst_root, "known_good.tlv"), b"known_good\x0a")
    _write(os.path.join(inst_root, "payload_refs.tlv"), b"payload_refs\x0a")
    _write(os.path.join(inst_root, "staging", "transaction.tlv"), b"transaction\x0a")
    _write(os.path.join(home, "logs", "caps_latest.tlv"), b"caps_latest\x0a")

    # Run artifacts/logs.
    run_root = os.path.join(inst_root, "logs", "runs", "0000000000000001")
    _write(os.path.join(run_root, "events.tlv"), b"events\x0a")
    _write(os.path.join(run_root, "handshake.tlv"), b"handshake\x0a")
    _write(os.path.join(run_root, "launch_config.tlv"), b"launch_config\x0a")
    _write(os.path.join(run_root, "audit_ref.tlv"), b"audit_ref\x0a")
    _write(os.path.join(run_root, "selection_summary.tlv"), b"selection_summary\x0a")
    _write(os.path.join(run_root, "exit_status.tlv"), b"exit_status\x0a")
    _write(os.path.join(run_root, "last_run_summary.tlv"), b"last_run_summary\x0a")
    _write(os.path.join(run_root, "caps.tlv"), b"caps\x0a")

    # Deterministic audit TLV.
    # Tags mirror launcher/core/include/launcher_audit.h:
    #   root schema_version tag=1
    #   run_id tag=2
    #   timestamp_us tag=3
    #   reason tag=7 (repeated)
    #   version_string tag=9
    #   build_id tag=10
    #   git_hash tag=11
    #   exit_result tag=13
    audit = b"".join(
        [
            _tlv_u32(1, 1),
            _tlv_u64(2, 1),
            _tlv_u64(3, 0),
            _tlv_str(7, "toolchain_id=test_toolchain"),
            _tlv_str(9, "launcher-test"),
            _tlv_str(10, "test_build_id"),
            _tlv_str(11, "deadbeef"),
            _tlv_i32(13, 0),
        ]
    )
    audit_name = "launcher_audit_%016x.tlv" % 1
    audit_path = os.path.join(home, audit_name)
    _write(audit_path, audit)
    return audit_path


def _generate_bundle(home: str, instance_id: str, out_path: str, fmt: str, audit_count: int) -> None:
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = env.get("SOURCE_DATE_EPOCH", "0")
    cmd = [
        sys.executable,
        os.path.join("scripts", "diagnostics", "make_support_bundle.py"),
        "--home",
        home,
        "--instance",
        instance_id,
        "--output",
        out_path,
        "--format",
        fmt,
        "--audit-count",
        str(audit_count),
        "--run-count",
        "1",
        "--mode",
        "default",
    ]
    subprocess.check_call(cmd, env=env)


def _assert_archive_contains(out_path: str, fmt: str, root_name: str, required_rel: list[str]) -> None:
    required = set([root_name + "/" + r for r in required_rel])
    if fmt == "zip":
        with zipfile.ZipFile(out_path, "r") as zf:
            names = set(zf.namelist())
    else:
        with tarfile.open(out_path, "r:gz") as tf:
            names = set(tf.getnames())
    missing = sorted(required - names)
    if missing:
        raise SystemExit("bundle missing expected entries: %s" % ", ".join(missing))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Verify deterministic support bundle generation.")
    ap.add_argument("--out-dir", required=True, help="Directory to place fixtures and resulting bundles")
    ap.add_argument("--format", choices=["zip", "tar.gz", "both"], default="both", help="Archive format to test")
    args = ap.parse_args(argv)

    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    instance_id = "inst_ci"
    fixture = os.path.join(out_dir, "fixture_home")
    if os.path.isdir(fixture):
        shutil.rmtree(fixture)
    os.makedirs(fixture, exist_ok=True)

    _build_fixture(fixture, instance_id)
    root_name = "dominium_support_bundle_%s" % instance_id
    required_rel = [
        "build_info.txt",
        "bundle_meta.tlv",
        "bundle_index.tlv",
        "audit/launcher_audit_0000000000000001.tlv",
        "instance/manifest.tlv",
        "instance/config.tlv",
        "instance/launch_history.tlv",
        "instance/known_good.tlv",
        "instance/payload_refs.tlv",
        "instance/staging/transaction.tlv",
        "logs/caps_latest.tlv",
        "runs/0000000000000001/events.tlv",
        "runs/0000000000000001/handshake.tlv",
        "runs/0000000000000001/launch_config.tlv",
        "runs/0000000000000001/audit_ref.tlv",
        "runs/0000000000000001/selection_summary.tlv",
        "runs/0000000000000001/exit_status.tlv",
        "runs/0000000000000001/last_run_summary.tlv",
        "runs/0000000000000001/caps.tlv",
    ]

    fmts = ["zip", "tar.gz"] if args.format == "both" else [args.format]
    for fmt in fmts:
        out1 = os.path.join(out_dir, "support_bundle_1.%s" % ("zip" if fmt == "zip" else "tar.gz"))
        out2 = os.path.join(out_dir, "support_bundle_2.%s" % ("zip" if fmt == "zip" else "tar.gz"))
        if os.path.exists(out1):
            os.remove(out1)
        if os.path.exists(out2):
            os.remove(out2)

        _generate_bundle(fixture, instance_id, out1, fmt, audit_count=1)
        _generate_bundle(fixture, instance_id, out2, fmt, audit_count=1)

        h1 = _hash_file(out1)
        h2 = _hash_file(out2)
        if h1 != h2:
            raise SystemExit("support bundle is nondeterministic for %s (hashes differ)" % fmt)

        _assert_archive_contains(out1, fmt, root_name, required_rel)

    print("support_bundle_determinism: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

