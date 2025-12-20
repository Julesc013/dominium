#!/usr/bin/env python3
"""
Create a deterministic "support bundle" (crash bundle) from a launcher home.

Bundle contents are intentionally minimal and offline:
- Recent launcher audit TLV(s)
- Instance manifest/config/history/known-good pointers
- Optional staged transaction markers (if present)
- A small derived build_info.txt summary (parsed from newest audit TLV)

The produced archive is deterministic:
- Stable file ordering (via make_deterministic_archive.py)
- Stable timestamps (SOURCE_DATE_EPOCH; defaults to 0)
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from typing import Iterable, Optional, Tuple


AUDIT_GLOB_PREFIX = "launcher_audit_"
AUDIT_GLOB_SUFFIX = ".tlv"


def _norm_rel(path: str) -> str:
    path = path.replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    while path.startswith("/"):
        path = path[1:]
    return path


def _read_file(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def _write_text_deterministic(path: str, text: str) -> None:
    data = text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def _copy_file_best_effort(src: str, dst: str) -> bool:
    if not os.path.isfile(src):
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    return True


def _iter_tlv_records(data: bytes) -> Iterable[Tuple[int, bytes]]:
    off = 0
    n = len(data)
    while off + 8 <= n:
        tag = int.from_bytes(data[off : off + 4], "little", signed=False)
        ln = int.from_bytes(data[off + 4 : off + 8], "little", signed=False)
        off += 8
        if off + ln > n:
            raise ValueError("truncated_tlv")
        payload = data[off : off + ln]
        off += ln
        yield tag, payload
    if off != n:
        raise ValueError("trailing_bytes")


def _tlv_read_u32(payload: bytes) -> Optional[int]:
    if len(payload) != 4:
        return None
    return int.from_bytes(payload, "little", signed=False)


def _tlv_read_u64(payload: bytes) -> Optional[int]:
    if len(payload) != 8:
        return None
    return int.from_bytes(payload, "little", signed=False)


def _tlv_read_i32(payload: bytes) -> Optional[int]:
    if len(payload) != 4:
        return None
    return int.from_bytes(payload, "little", signed=True)


def _tlv_read_string(payload: bytes) -> str:
    try:
        return payload.decode("utf-8", errors="replace")
    except Exception:
        return ""


@dataclass
class AuditSummary:
    schema_version: Optional[int] = None
    run_id: Optional[int] = None
    timestamp_us: Optional[int] = None
    version_string: str = ""
    build_id: str = ""
    git_hash: str = ""
    exit_result: Optional[int] = None
    toolchain_id: str = ""


def _parse_audit_summary(audit_path: str) -> AuditSummary:
    data = _read_file(audit_path)
    s = AuditSummary()
    toolchain_re = re.compile(r"(^|\s)toolchain_id=([^\s]+)")
    for tag, payload in _iter_tlv_records(data):
        # Root schema version tag is always 1u for launcher TLV roots.
        if tag == 1:
            v = _tlv_read_u32(payload)
            if v is not None:
                s.schema_version = v
        elif tag == 2:
            v = _tlv_read_u64(payload)
            if v is not None:
                s.run_id = v
        elif tag == 3:
            v = _tlv_read_u64(payload)
            if v is not None:
                s.timestamp_us = v
        elif tag == 9:
            s.version_string = _tlv_read_string(payload)
        elif tag == 10:
            s.build_id = _tlv_read_string(payload)
        elif tag == 11:
            s.git_hash = _tlv_read_string(payload)
        elif tag == 13:
            v = _tlv_read_i32(payload)
            if v is not None:
                s.exit_result = v
        elif tag == 7:
            reason = _tlv_read_string(payload)
            m = toolchain_re.search(reason)
            if m and not s.toolchain_id:
                s.toolchain_id = m.group(2)
    return s


def _audit_runid_from_name(filename: str) -> Optional[int]:
    base = os.path.basename(filename)
    if not (base.startswith(AUDIT_GLOB_PREFIX) and base.endswith(AUDIT_GLOB_SUFFIX)):
        return None
    mid = base[len(AUDIT_GLOB_PREFIX) : -len(AUDIT_GLOB_SUFFIX)]
    if len(mid) != 16:
        return None
    try:
        return int(mid, 16)
    except Exception:
        return None


def _find_audit_candidates(home: str) -> list[str]:
    home = os.path.abspath(home)
    candidates: list[str] = []
    for d in (home, os.path.join(home, "audit")):
        if not os.path.isdir(d):
            continue
        try:
            for name in os.listdir(d):
                if name.startswith(AUDIT_GLOB_PREFIX) and name.endswith(AUDIT_GLOB_SUFFIX):
                    candidates.append(os.path.join(d, name))
        except OSError:
            continue
    # Deduplicate and sort deterministically by run_id when possible, else by normalized path.
    uniq = sorted(set(candidates), key=lambda p: p.replace("\\", "/"))
    with_ids: list[Tuple[int, str]] = []
    no_ids: list[str] = []
    for p in uniq:
        rid = _audit_runid_from_name(os.path.basename(p))
        if rid is None:
            no_ids.append(p)
        else:
            with_ids.append((rid, p))
    with_ids.sort(key=lambda t: (t[0], t[1].replace("\\", "/")))
    no_ids.sort(key=lambda p: p.replace("\\", "/"))
    return [p for (_, p) in with_ids] + no_ids


def _select_recent(paths: list[str], count: int) -> list[str]:
    if count <= 0:
        return []
    if not paths:
        return []
    # Prefer the end of the list (highest run id, then lexicographic).
    if len(paths) <= count:
        return paths[:]
    return paths[-count:]


def _run_deterministic_archive(input_dir: str, output_path: str, fmt: str, root_name: str) -> None:
    script = os.path.join("scripts", "packaging", "make_deterministic_archive.py")
    argv = [
        sys.executable,
        script,
        "--format",
        fmt,
        "--input",
        os.path.abspath(input_dir),
        "--output",
        os.path.abspath(output_path),
        "--root-name",
        root_name,
    ]
    subprocess.check_call(argv)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Generate a deterministic support bundle (crash bundle) archive.")
    ap.add_argument("--home", default=".", help="Launcher home/state root (defaults to current directory)")
    ap.add_argument("--instance", required=True, help="Instance id to bundle")
    ap.add_argument("--output", required=True, help="Output archive path (zip or tar.gz)")
    ap.add_argument("--format", choices=["zip", "tar.gz"], default="zip", help="Archive format (default: zip)")
    ap.add_argument("--audit-count", type=int, default=3, help="Number of most recent audit TLVs to include")
    args = ap.parse_args(argv)

    home = os.path.abspath(args.home)
    instance_id = args.instance.strip()
    if not instance_id:
        raise SystemExit("instance id must be non-empty")

    instance_root = os.path.join(home, "instances", instance_id)
    if not os.path.isdir(instance_root):
        raise SystemExit("instance not found: %s" % instance_root)

    # Resolve candidate audit logs and derive build summary from newest audit (if any).
    audits_all = _find_audit_candidates(home)
    audits = _select_recent(audits_all, args.audit_count)
    newest_audit = audits[-1] if audits else ""
    summary = _parse_audit_summary(newest_audit) if newest_audit else AuditSummary()

    bundle_root_name = "dominium_support_bundle_%s" % instance_id

    with tempfile.TemporaryDirectory(prefix="dom_support_bundle_") as tmp:
        stage = os.path.join(tmp, "stage")
        os.makedirs(stage, exist_ok=True)

        # Build-info summary (derived; deterministic content).
        build_info = []
        build_info.append("version_string=%s\n" % (summary.version_string or "unknown"))
        build_info.append("build_id=%s\n" % (summary.build_id or "unknown"))
        build_info.append("git_hash=%s\n" % (summary.git_hash or "unknown"))
        build_info.append("toolchain_id=%s\n" % (summary.toolchain_id or "unknown"))
        if summary.run_id is not None:
            build_info.append("run_id=0x%016x\n" % summary.run_id)
        if summary.timestamp_us is not None:
            build_info.append("timestamp_us=%d\n" % int(summary.timestamp_us))
        if summary.exit_result is not None:
            build_info.append("exit_result=%d\n" % int(summary.exit_result))
        _write_text_deterministic(os.path.join(stage, "build_info.txt"), "".join(build_info))

        # Audit logs (newest last; stable naming).
        for p in audits:
            name = os.path.basename(p)
            _copy_file_best_effort(p, os.path.join(stage, "audit", name))

        # Core instance state.
        _copy_file_best_effort(os.path.join(instance_root, "manifest.tlv"), os.path.join(stage, "instance", "manifest.tlv"))
        _copy_file_best_effort(
            os.path.join(instance_root, "config", "config.tlv"), os.path.join(stage, "instance", "config.tlv")
        )
        _copy_file_best_effort(
            os.path.join(instance_root, "logs", "launch_history.tlv"), os.path.join(stage, "instance", "launch_history.tlv")
        )
        _copy_file_best_effort(os.path.join(instance_root, "known_good.tlv"), os.path.join(stage, "instance", "known_good.tlv"))

        # Optional staged crash markers (useful when a crash happened mid-transaction).
        _copy_file_best_effort(
            os.path.join(instance_root, "staging", "transaction.tlv"), os.path.join(stage, "instance", "staging", "transaction.tlv")
        )
        _copy_file_best_effort(
            os.path.join(instance_root, "staging", "manifest.tlv"), os.path.join(stage, "instance", "staging", "manifest.tlv")
        )
        _copy_file_best_effort(
            os.path.join(instance_root, "staging", "payload_refs.tlv"),
            os.path.join(stage, "instance", "staging", "payload_refs.tlv"),
        )

        # Write archive deterministically.
        _run_deterministic_archive(stage, args.output, args.format, bundle_root_name)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
