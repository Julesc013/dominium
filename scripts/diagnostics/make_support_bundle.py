#!/usr/bin/env python3
"""
Create a deterministic "support bundle" (crash bundle) from a launcher home.

Bundle contents are intentionally minimal and offline:
- Recent launcher audit TLV(s)
- Instance manifest/config/history/known-good pointers
- Recent run artifacts (handshake/selection/exit status/caps/run summary)
- Structured event logs (run-scoped; rolling in extended mode)
- Bundle metadata + index (deterministic TLV)
- Optional staged transaction markers (if present)
- A small derived build_info.txt summary (parsed from newest audit TLV)

The produced archive is deterministic:
- Stable file ordering (via make_deterministic_archive.py)
- Stable timestamps (SOURCE_DATE_EPOCH; defaults to 0)
"""

from __future__ import annotations

import argparse
import hashlib
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


def _tlv_bytes(tag: int, payload: bytes) -> bytes:
    return _tlv_rec(tag, payload or b"")


def _tlv_str(tag: int, s: str) -> bytes:
    return _tlv_rec(tag, (s or "").encode("utf-8"))


def _write_tlv(path: str, records: Iterable[bytes]) -> None:
    data = b"".join(records)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def _hash_file(path: str) -> bytes:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.digest()


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


@dataclass
class BundleFile:
    src: str
    rel: str


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


def _run_id_from_dir(name: str) -> Optional[int]:
    if len(name) != 16:
        return None
    try:
        return int(name, 16)
    except Exception:
        return None


def _list_run_dirs(instance_root: str) -> list[str]:
    runs_root = os.path.join(instance_root, "logs", "runs")
    if not os.path.isdir(runs_root):
        return []
    names: list[str] = []
    try:
        for name in os.listdir(runs_root):
            full = os.path.join(runs_root, name)
            if not os.path.isdir(full):
                continue
            names.append(name)
    except OSError:
        return []
    with_ids: list[Tuple[int, str]] = []
    no_ids: list[str] = []
    for name in names:
        rid = _run_id_from_dir(name)
        if rid is None:
            no_ids.append(name)
        else:
            with_ids.append((rid, name))
    with_ids.sort(key=lambda t: (t[0], t[1]))
    no_ids.sort()
    return [name for (_, name) in with_ids] + no_ids


def _parse_manifest_content_entries(data: bytes) -> list[Tuple[int, str, str]]:
    # Tags mirror launcher_instance.h manifest schema.
    TAG_CONTENT_ENTRY = 11
    TAG_ENTRY_TYPE = 1
    TAG_ENTRY_ID = 2
    TAG_ENTRY_VERSION = 3
    out: list[Tuple[int, str, str]] = []
    for tag, payload in _iter_tlv_records(data):
        if tag != TAG_CONTENT_ENTRY:
            continue
        entry_type: Optional[int] = None
        entry_id = ""
        entry_ver = ""
        for etag, epl in _iter_tlv_records(payload):
            if etag == TAG_ENTRY_TYPE:
                entry_type = _tlv_read_u32(epl)
            elif etag == TAG_ENTRY_ID:
                entry_id = _tlv_read_string(epl)
            elif etag == TAG_ENTRY_VERSION:
                entry_ver = _tlv_read_string(epl)
        if entry_type is not None and entry_id and entry_ver:
            out.append((int(entry_type), entry_id, entry_ver))
    return out


def _collect_pack_manifests(home: str, manifest_path: str) -> list[Tuple[str, str]]:
    # Returns list of (src_path, rel_path) for pack/mod manifests referenced by the instance manifest.
    if not os.path.isfile(manifest_path):
        return []
    try:
        data = _read_file(manifest_path)
    except Exception:
        return []
    # LauncherContentType values: 3=pack, 4=mod, 5=runtime.
    entries = _parse_manifest_content_entries(data)
    out: list[Tuple[str, str]] = []
    for (etype, eid, ever) in entries:
        if etype == 3:
            rel = os.path.join("packs", eid, ever, "pack.tlv")
        elif etype == 4:
            rel = os.path.join("mods", eid, ever, "mod.tlv")
        else:
            continue
        src = os.path.join(home, rel)
        if os.path.isfile(src):
            out.append((src, rel))
    return out


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


def _iter_stage_files(root_dir: str) -> list[str]:
    root_dir = os.path.abspath(root_dir)
    files: list[str] = []
    for cur_root, cur_dirs, cur_files in os.walk(root_dir):
        cur_dirs.sort()
        cur_files.sort()
        rel_root = os.path.relpath(cur_root, root_dir)
        rel_root = "" if rel_root == "." else _norm_rel(rel_root)
        for f in cur_files:
            if f in (".stage_stamp",):
                continue
            rel = _norm_rel(os.path.join(rel_root, f))
            files.append(rel)
    return sorted(set(files))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Generate a deterministic support bundle (crash bundle) archive.")
    ap.add_argument("--home", default=".", help="Launcher home/state root (defaults to current directory)")
    ap.add_argument("--instance", required=True, help="Instance id to bundle")
    ap.add_argument("--output", required=True, help="Output archive path (zip or tar.gz)")
    ap.add_argument("--format", choices=["zip", "tar.gz"], default="zip", help="Archive format (default: zip)")
    ap.add_argument("--audit-count", type=int, default=3, help="Number of most recent audit TLVs to include")
    ap.add_argument("--run-count", type=int, default=3, help="Number of most recent runs to include")
    ap.add_argument("--mode", choices=["default", "extended"], default="default", help="Redaction mode")
    args = ap.parse_args(argv)

    home = os.path.abspath(args.home)
    instance_id = args.instance.strip()
    if not instance_id:
        raise SystemExit("instance id must be non-empty")

    instance_root = os.path.join(home, "instances", instance_id)
    if not os.path.isdir(instance_root):
        raise SystemExit("instance not found: %s" % instance_root)

    audit_count = max(0, int(args.audit_count))
    run_count = max(0, int(args.run_count))
    mode = args.mode
    if mode == "extended":
        audit_count = max(audit_count, 8)
        run_count = max(run_count, 8)

    # Resolve candidate audit logs and derive build summary from newest audit (if any).
    audits_all = _find_audit_candidates(home)
    audits = _select_recent(audits_all, audit_count)
    newest_audit = audits[-1] if audits else ""
    summary = _parse_audit_summary(newest_audit) if newest_audit else AuditSummary()

    bundle_root_name = "dominium_support_bundle_%s" % instance_id

    with tempfile.TemporaryDirectory(prefix="dom_support_bundle_") as tmp:
        stage = os.path.join(tmp, "stage")
        os.makedirs(stage, exist_ok=True)

        bundle_files: list[BundleFile] = []

        def add_file(src: str, rel: str) -> None:
            if not src or not rel:
                return
            bundle_files.append(BundleFile(src=src, rel=_norm_rel(rel)))

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
            add_file(p, os.path.join("audit", name))

        # Core instance state.
        manifest_path = os.path.join(instance_root, "manifest.tlv")
        add_file(manifest_path, os.path.join("instance", "manifest.tlv"))
        add_file(os.path.join(instance_root, "config", "config.tlv"), os.path.join("instance", "config.tlv"))
        add_file(os.path.join(instance_root, "logs", "launch_history.tlv"), os.path.join("instance", "launch_history.tlv"))
        add_file(os.path.join(instance_root, "known_good.tlv"), os.path.join("instance", "known_good.tlv"))
        add_file(os.path.join(instance_root, "payload_refs.tlv"), os.path.join("instance", "payload_refs.tlv"))

        # Optional staged crash markers (useful when a crash happened mid-transaction).
        add_file(os.path.join(instance_root, "staging", "transaction.tlv"), os.path.join("instance", "staging", "transaction.tlv"))
        add_file(os.path.join(instance_root, "staging", "manifest.tlv"), os.path.join("instance", "staging", "manifest.tlv"))
        add_file(os.path.join(instance_root, "staging", "payload_refs.tlv"), os.path.join("instance", "staging", "payload_refs.tlv"))

        # Pack/mod manifests referenced by the instance (when present).
        for src, rel in _collect_pack_manifests(home, manifest_path):
            add_file(src, rel)

        # Run artifacts/logs (bounded).
        run_dirs = _list_run_dirs(instance_root)
        run_ids = _select_recent(run_dirs, run_count)
        for run_id in run_ids:
            run_root = os.path.join(instance_root, "logs", "runs", run_id)
            add_file(os.path.join(run_root, "events.tlv"), os.path.join("runs", run_id, "events.tlv"))
            add_file(os.path.join(run_root, "handshake.tlv"), os.path.join("runs", run_id, "handshake.tlv"))
            add_file(os.path.join(run_root, "launch_config.tlv"), os.path.join("runs", run_id, "launch_config.tlv"))
            add_file(os.path.join(run_root, "audit_ref.tlv"), os.path.join("runs", run_id, "audit_ref.tlv"))
            add_file(os.path.join(run_root, "launcher_audit.tlv"), os.path.join("runs", run_id, "launcher_audit.tlv"))
            add_file(os.path.join(run_root, "selection_summary.tlv"), os.path.join("runs", run_id, "selection_summary.tlv"))
            add_file(os.path.join(run_root, "exit_status.tlv"), os.path.join("runs", run_id, "exit_status.tlv"))
            add_file(os.path.join(run_root, "last_run_summary.tlv"), os.path.join("runs", run_id, "last_run_summary.tlv"))
            add_file(os.path.join(run_root, "caps.tlv"), os.path.join("runs", run_id, "caps.tlv"))

        # Rolling logs (extended mode only).
        if mode == "extended":
            add_file(os.path.join(instance_root, "logs", "rolling", "events_rolling.tlv"),
                     os.path.join("instance", "logs", "rolling", "events_rolling.tlv"))
            add_file(os.path.join(home, "logs", "rolling", "events_rolling.tlv"),
                     os.path.join("logs", "rolling", "events_rolling.tlv"))

        # Latest caps snapshot (global).
        add_file(os.path.join(home, "logs", "caps_latest.tlv"), os.path.join("logs", "caps_latest.tlv"))

        # Copy bundle files in deterministic order (dedupe by destination).
        uniq: dict[str, str] = {}
        for bf in bundle_files:
            if bf.rel not in uniq:
                uniq[bf.rel] = bf.src
        for rel in sorted(uniq.keys()):
            _copy_file_best_effort(uniq[rel], os.path.join(stage, rel))

        # Bundle metadata TLV (deterministic, redaction-aware).
        meta_records: list[bytes] = []
        meta_records.append(_tlv_u32(1, 1))  # schema_version
        meta_records.append(_tlv_u32(2, 1))  # bundle_version
        meta_records.append(_tlv_str(3, mode))
        meta_records.append(_tlv_str(4, instance_id))
        meta_records.append(_tlv_str(5, summary.build_id or "unknown"))
        meta_records.append(_tlv_str(6, summary.git_hash or "unknown"))
        meta_records.append(_tlv_str(7, summary.version_string or "unknown"))
        meta_records.append(_tlv_u32(8, audit_count))
        meta_records.append(_tlv_u32(9, run_count))
        for run_id in run_ids:
            rid = _run_id_from_dir(run_id)
            if rid is not None:
                meta_records.append(_tlv_u64(10, rid))
        _write_tlv(os.path.join(stage, "bundle_meta.tlv"), meta_records)

        # Bundle index TLV (path + sha256 + size).
        index_records: list[bytes] = []
        index_records.append(_tlv_u32(1, 1))  # schema_version
        for rel in _iter_stage_files(stage):
            if rel == "bundle_index.tlv":
                continue
            full = os.path.join(stage, rel)
            try:
                size = os.path.getsize(full)
            except OSError:
                continue
            payload = b"".join(
                [
                    _tlv_str(1, rel),
                    _tlv_bytes(2, _hash_file(full)),
                    _tlv_u64(3, size),
                ]
            )
            index_records.append(_tlv_rec(2, payload))
        _write_tlv(os.path.join(stage, "bundle_index.tlv"), index_records)

        # Write archive deterministically.
        _run_deterministic_archive(stage, args.output, args.format, bundle_root_name)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
