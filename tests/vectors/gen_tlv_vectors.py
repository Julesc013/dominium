#!/usr/bin/env python3
"""
Generate deterministic TLV golden vectors for contract tests.

Usage:
  python tests/vectors/gen_tlv_vectors.py --out tests/vectors/tlv
"""
from __future__ import annotations

import argparse
import hashlib
import os
import struct
import zlib


def _le_u16(v: int) -> bytes:
    return struct.pack("<H", int(v) & 0xFFFF)


def _le_u32(v: int) -> bytes:
    return struct.pack("<I", int(v) & 0xFFFFFFFF)


def _le_u64(v: int) -> bytes:
    return struct.pack("<Q", int(v) & 0xFFFFFFFFFFFFFFFF)


def tlv_rec(tag: int, payload: bytes) -> bytes:
    payload = payload or b""
    return _le_u32(tag) + _le_u32(len(payload)) + payload


def tlv_u32(tag: int, v: int) -> bytes:
    return tlv_rec(tag, _le_u32(v))


def tlv_i32(tag: int, v: int) -> bytes:
    return tlv_rec(tag, struct.pack("<i", int(v)))


def tlv_u64(tag: int, v: int) -> bytes:
    return tlv_rec(tag, _le_u64(v))


def tlv_str(tag: int, s: str) -> bytes:
    data = (s or "").encode("utf-8")
    return tlv_rec(tag, data)


def tlv_bytes(tag: int, payload: bytes) -> bytes:
    return tlv_rec(tag, payload or b"")


def tlv_container(tag: int, records: list[bytes]) -> bytes:
    return tlv_rec(tag, b"".join(records))


def sha256_bytes(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_file(path: str, data: bytes) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def write_text(path: str, text: str) -> None:
    write_file(path, text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def write_vector(dir_path: str,
                 name: str,
                 data: bytes,
                 summary_lines: list[str],
                 schema_id: int,
                 version: int,
                 manifest_entries: list[dict[str, str]]) -> None:
    os.makedirs(dir_path, exist_ok=True)
    vec_name = f"{name}.tlv"
    summary_name = f"{name}.expected.txt"
    sha_name = f"{name}.sha256"
    write_file(os.path.join(dir_path, vec_name), data)
    write_text(os.path.join(dir_path, summary_name), "\n".join(summary_lines) + "\n")
    write_text(os.path.join(dir_path, sha_name), sha256_hex(data) + "\n")
    manifest_entries.append({
        "schema_id": str(schema_id),
        "version": str(version),
        "vector": vec_name,
        "summary": summary_name,
        "sha256": sha_name,
    })


def write_manifest(dir_path: str, entries: list[dict[str, str]]) -> None:
    lines: list[str] = []
    for entry in entries:
        lines.append(f"schema_id={entry['schema_id']}")
        lines.append(f"version={entry['version']}")
        lines.append(f"vector={entry['vector']}")
        lines.append(f"summary={entry['summary']}")
        lines.append(f"sha256={entry['sha256']}")
        lines.append("")
    write_text(os.path.join(dir_path, "manifest.txt"), "\n".join(lines).rstrip() + "\n")


def dsk_rec(tag: int, payload: bytes) -> bytes:
    payload = payload or b""
    return _le_u16(tag) + _le_u32(len(payload)) + payload


def dsk_u16(tag: int, v: int) -> bytes:
    return dsk_rec(tag, _le_u16(v))


def dsk_u32(tag: int, v: int) -> bytes:
    return dsk_rec(tag, _le_u32(v))


def dsk_u64(tag: int, v: int) -> bytes:
    return dsk_rec(tag, _le_u64(v))


def dsk_str(tag: int, s: str) -> bytes:
    return dsk_rec(tag, (s or "").encode("utf-8"))


def dsk_container(tag: int, records: list[bytes]) -> bytes:
    return dsk_rec(tag, b"".join(records))


def dsk_wrap(payload: bytes) -> bytes:
    magic = b"DSK1"
    version = _le_u16(1)
    endian = _le_u16(0xFFFE)
    header_size = _le_u32(20)
    payload_size = _le_u32(len(payload))
    header_crc = _le_u32(0)
    header = magic + version + endian + header_size + payload_size + header_crc
    crc = zlib.crc32(header) & 0xFFFFFFFF
    header = magic + version + endian + header_size + payload_size + _le_u32(crc)
    return header + payload


def make_pack_manifest(pack_id: str,
                       pack_type: int,
                       version: str,
                       deps: list[tuple[str, str, str]] = None,
                       conflicts: list[tuple[str, str, str]] = None,
                       phase: int = 2,
                       explicit_order: int = 0,
                       declared_caps: list[str] = None,
                       sim_flags: list[str] = None,
                       unknown: bytes | None = None) -> bytes:
    deps = deps or []
    conflicts = conflicts or []
    declared_caps = declared_caps or []
    sim_flags = sim_flags or []
    records: list[bytes] = []
    records.append(tlv_u32(1, 1))
    records.append(tlv_str(2, pack_id))
    records.append(tlv_u32(3, pack_type))
    records.append(tlv_str(4, version))
    pack_hash = b"\x42" * 32
    records.append(tlv_bytes(5, pack_hash))
    range_engine = [tlv_str(1, "1.0.0"), tlv_str(2, "2.0.0")]
    range_game = [tlv_str(1, "0.1.0"), tlv_str(2, "1.0.0")]
    records.append(tlv_container(6, range_engine))
    records.append(tlv_container(7, range_game))
    for dep_id, min_v, max_v in deps:
        dep_range = [tlv_str(1, min_v), tlv_str(2, max_v)]
        dep_payload = [tlv_str(1, dep_id), tlv_container(2, dep_range)]
        records.append(tlv_container(8, dep_payload))
    for dep_id, min_v, max_v in conflicts:
        dep_range = [tlv_str(1, min_v), tlv_str(2, max_v)]
        dep_payload = [tlv_str(1, dep_id), tlv_container(2, dep_range)]
        records.append(tlv_container(10, dep_payload))
    records.append(tlv_u32(11, phase))
    records.append(tlv_i32(12, explicit_order))
    for cap in declared_caps:
        records.append(tlv_str(13, cap))
    for flag in sim_flags:
        records.append(tlv_str(14, flag))
    task_payload = [tlv_u32(1, 1), tlv_str(2, "data/config.json")]
    records.append(tlv_container(15, task_payload))
    if unknown is not None:
        records.append(tlv_bytes(999, unknown))
    return b"".join(records)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="Output directory for TLV vectors.")
    args = ap.parse_args()

    out_root = os.path.abspath(args.out)

    # Pack manifests (launcher).
    pack_dir = os.path.join(out_root, "pack_manifest")
    pack_entries: list[dict[str, str]] = []
    pack_base = make_pack_manifest(
        "pack.base", 1, "1.0.0",
        declared_caps=["caps.sim"],
        sim_flags=["caps.sim"],
        unknown=b"unknown"
    )
    pack_core = make_pack_manifest(
        "pack.core", 1, "1.1.0",
        deps=[("pack.base", "1.0.0", "2.0.0")],
        declared_caps=["caps.sim"],
        sim_flags=["caps.sim"]
    )
    pack_conflict = make_pack_manifest(
        "pack.conflict", 1, "9.9.0",
        conflicts=[("pack.base", "0.0.0", "9.9.9")],
        declared_caps=["caps.sim"],
        sim_flags=["caps.sim"]
    )
    write_vector(
        pack_dir,
        "pack_base_v1",
        pack_base,
        [
            "schema_version=1",
            "pack_id=pack.base",
            "pack_type=1",
            "version=1.0.0",
            "required_deps=0",
            "conflicts=0",
            "declared_caps=1",
            "sim_flags=1",
            "unknown_root_tags=1",
        ],
        schema_id=2,
        version=1,
        manifest_entries=pack_entries,
    )
    write_vector(
        pack_dir,
        "pack_core_v1",
        pack_core,
        [
            "schema_version=1",
            "pack_id=pack.core",
            "pack_type=1",
            "version=1.1.0",
            "required_deps=1",
            "conflicts=0",
            "declared_caps=1",
            "sim_flags=1",
            "unknown_root_tags=0",
        ],
        schema_id=2,
        version=1,
        manifest_entries=pack_entries,
    )
    write_vector(
        pack_dir,
        "pack_conflict_v1",
        pack_conflict,
        [
            "schema_version=1",
            "pack_id=pack.conflict",
            "pack_type=1",
            "version=9.9.0",
            "required_deps=0",
            "conflicts=1",
            "declared_caps=1",
            "sim_flags=1",
            "unknown_root_tags=0",
        ],
        schema_id=2,
        version=1,
        manifest_entries=pack_entries,
    )
    write_manifest(pack_dir, pack_entries)

    # Instance manifest v2 (launcher).
    inst_dir = os.path.join(out_root, "instance_manifest")
    inst_entries: list[dict[str, str]] = []
    pack_base_hash = sha256_bytes(pack_base)
    pack_core_hash = sha256_bytes(pack_core)
    entry_base = [
        tlv_u32(1, 3),
        tlv_str(2, "pack.base"),
        tlv_str(3, "1.0.0"),
        tlv_bytes(4, pack_base_hash),
        tlv_u32(5, 1),
        tlv_u32(6, 1),
        tlv_i32(7, 0),
        tlv_bytes(99, b"entry_unknown"),
    ]
    entry_core = [
        tlv_u32(1, 3),
        tlv_str(2, "pack.core"),
        tlv_str(3, "1.1.0"),
        tlv_bytes(4, pack_core_hash),
        tlv_u32(5, 1),
        tlv_u32(6, 1),
    ]
    inst_v2_records = [
        tlv_u32(1, 2),
        tlv_str(2, "inst_alpha"),
        tlv_u64(8, 123456),
        tlv_str(3, "engine_1"),
        tlv_str(4, "game_1"),
        tlv_u32(7, 1),
        tlv_u64(9, 123460),
        tlv_u64(10, 0x1111111111111111),
        tlv_container(11, entry_base),
        tlv_container(11, entry_core),
        tlv_bytes(9999, b"root_unknown"),
    ]
    inst_v2 = b"".join(inst_v2_records)
    inst_hash = sha256_bytes(inst_v2)
    write_vector(
        inst_dir,
        "instance_v2_basic",
        inst_v2,
        [
            "schema_version=2",
            "instance_id=inst_alpha",
            "content_entries=2",
            "content[0].id=pack.base",
            "content[1].id=pack.core",
            "known_good=1",
            "unknown_root_tags=1",
            "unknown_entry_tags=1",
        ],
        schema_id=1,
        version=2,
        manifest_entries=inst_entries,
    )

    # Instance manifest v1 legacy (launcher).
    entry_v1 = [
        tlv_u32(1, 3),
        tlv_str(2, "legacy.pack"),
        tlv_str(3, "0.9.0"),
        tlv_bytes(4, b"\x01\x02\x03\x04"),
        tlv_u32(5, 2),
    ]
    inst_v1 = b"".join([
        tlv_u32(1, 1),
        tlv_str(2, "inst_legacy"),
        tlv_str(3, "engine_legacy"),
        tlv_str(4, "game_legacy"),
        tlv_u32(7, 0),
        tlv_container(5, entry_v1),
    ])
    write_vector(
        inst_dir,
        "instance_v1_legacy",
        inst_v1,
        [
            "schema_version=1",
            "instance_id=inst_legacy",
            "content_entries=1",
            "content[0].id=legacy.pack",
            "known_good=0",
            "unknown_root_tags=0",
            "unknown_entry_tags=0",
        ],
        schema_id=1,
        version=1,
        manifest_entries=inst_entries,
    )
    write_manifest(inst_dir, inst_entries)

    # Selection summary (launcher).
    sel_dir = os.path.join(out_root, "selection_summary")
    sel_entries: list[dict[str, str]] = []
    sel_records = [
        tlv_u32(1, 1),
        tlv_u64(2, 0xABCDEF0123456789),
        tlv_str(3, "inst_alpha"),
        tlv_str(4, "baseline"),
        tlv_str(5, "baseline"),
        tlv_u32(6, 0),
        tlv_u32(7, 0),
        tlv_u64(8, 0x1234567890ABCDEF),
        tlv_bytes(9, inst_hash),
        tlv_container(10, [tlv_str(1, "null"), tlv_str(2, "default")]),
        tlv_container(11, [tlv_str(1, "win32"), tlv_str(2, "default")]),
        tlv_container(12, [tlv_str(1, "soft"), tlv_str(2, "default")]),
        tlv_container(15, [tlv_str(1, "net"), tlv_str(2, "null"), tlv_str(3, "default")]),
        tlv_u32(13, 2),
        tlv_str(14, "pack.base,pack.core"),
        tlv_bytes(999, b"sel_unknown"),
    ]
    sel_bytes = b"".join(sel_records)
    write_vector(
        sel_dir,
        "selection_v1_basic",
        sel_bytes,
        [
            "schema_version=1",
            "run_id=0xabcdef0123456789",
            "instance_id=inst_alpha",
            "profile_id=baseline",
            "determinism_profile_id=baseline",
            "resolved_packs_count=2",
            "resolved_packs_summary=pack.base,pack.core",
        ],
        schema_id=5,
        version=1,
        manifest_entries=sel_entries,
    )
    write_manifest(sel_dir, sel_entries)

    # Handshake (launcher).
    hs_dir = os.path.join(out_root, "launcher_handshake")
    hs_entries: list[dict[str, str]] = []
    hs_pack_base = [
        tlv_str(1, "pack.base"),
        tlv_str(2, "1.0.0"),
        tlv_bytes(3, pack_base_hash),
        tlv_u32(4, 1),
        tlv_str(5, "caps.sim"),
        tlv_u32(7, 0),
    ]
    hs_pack_core = [
        tlv_str(1, "pack.core"),
        tlv_str(2, "1.1.0"),
        tlv_bytes(3, pack_core_hash),
        tlv_u32(4, 1),
        tlv_str(5, "caps.sim"),
        tlv_u32(7, 0),
    ]
    hs_records = [
        tlv_u32(1, 1),
        tlv_u64(2, 0x1111222233334444),
        tlv_str(3, "inst_alpha"),
        tlv_bytes(4, inst_hash),
        tlv_str(5, "baseline"),
        tlv_str(6, "baseline"),
        tlv_str(7, "win32"),
        tlv_str(8, "soft"),
        tlv_str(9, "null"),
        tlv_str(10, "engine_1"),
        tlv_str(11, "game_1"),
        tlv_container(12, hs_pack_base),
        tlv_container(12, hs_pack_core),
        tlv_u64(13, 5555),
        tlv_u64(14, 7777),
        tlv_bytes(999, b"hs_unknown"),
    ]
    hs_bytes = b"".join(hs_records)
    write_vector(
        hs_dir,
        "handshake_v1_basic",
        hs_bytes,
        [
            "schema_version=1",
            "run_id=0x1111222233334444",
            "instance_id=inst_alpha",
            "resolved_packs=2",
            "selected_ui=null",
        ],
        schema_id=4,
        version=1,
        manifest_entries=hs_entries,
    )
    write_manifest(hs_dir, hs_entries)

    # Audit log (launcher).
    audit_dir = os.path.join(out_root, "launcher_audit")
    audit_entries: list[dict[str, str]] = []
    audit_backend = [
        tlv_u32(1, 1),
        tlv_str(2, "ui"),
        tlv_str(3, "null"),
        tlv_u32(4, 1),
        tlv_u32(5, 1),
        tlv_u32(6, 10),
        tlv_u32(7, 0),
    ]
    audit_err_detail = [
        tlv_u32(1, 100),
        tlv_u32(2, 1),
        tlv_u32(3, 42),
    ]
    audit_records = [
        tlv_u32(1, 1),
        tlv_u64(2, 0x1111222233334444),
        tlv_u64(3, 9999),
        tlv_str(5, "baseline"),
        tlv_str(9, "1.0.0"),
        tlv_str(10, "build_1"),
        tlv_str(11, "deadbeef"),
        tlv_u64(12, 0x1234567890ABCDEF),
        tlv_i32(13, 0),
        tlv_rec(14, sel_bytes),
        tlv_u32(20, 1),
        tlv_u32(21, 2),
        tlv_u32(22, 4),
        tlv_u32(23, 10),
        tlv_container(24, audit_err_detail),
        tlv_str(4, "--ui=null"),
        tlv_str(4, "--gfx=null"),
        tlv_str(7, "selected:default"),
        tlv_u32(25, 1234),
        tlv_container(6, audit_backend),
    ]
    audit_bytes = b"".join(audit_records)
    write_vector(
        audit_dir,
        "audit_v1_basic",
        audit_bytes,
        [
            "schema_version=1",
            "run_id=0x1111222233334444",
            "inputs=2",
            "selected_profile=baseline",
            "has_selection_summary=1",
            "selected_backends=1",
        ],
        schema_id=3,
        version=1,
        manifest_entries=audit_entries,
    )
    write_manifest(audit_dir, audit_entries)

    # Tools registry (launcher).
    tools_dir = os.path.join(out_root, "tools_registry")
    tools_entries: list[dict[str, str]] = []
    tool_entry = [
        tlv_str(1, "tool.pack_inspector"),
        tlv_str(2, "Pack Inspector"),
        tlv_str(3, "Inspect pack manifests"),
        tlv_bytes(4, b"\xAA" * 32),
        tlv_str(5, "pack.base"),
        tlv_str(6, "pack.core"),
        tlv_str(7, "caps.sim"),
        tlv_container(8, [tlv_str(1, "Inspector"), tlv_str(2, "icon")]),
    ]
    tools_bytes = b"".join([
        tlv_u32(1, 1),
        tlv_container(2, tool_entry),
    ])
    write_vector(
        tools_dir,
        "tools_v1_basic",
        tools_bytes,
        [
            "schema_version=1",
            "tools=1",
            "tool[0].id=tool.pack_inspector",
            "tool[0].required_packs=1",
        ],
        schema_id=9,
        version=1,
        manifest_entries=tools_entries,
    )
    write_manifest(tools_dir, tools_entries)

    # Caps snapshot (launcher).
    caps_dir = os.path.join(out_root, "caps_snapshot")
    caps_entries: list[dict[str, str]] = []
    caps_backend = [
        tlv_u32(1, 1),
        tlv_str(2, "ui"),
        tlv_str(3, "null"),
        tlv_u32(4, 1),
        tlv_u32(5, 1),
        tlv_u32(6, 10),
    ]
    caps_sel = [
        tlv_u32(1, 1),
        tlv_str(2, "ui"),
        tlv_str(3, "null"),
        tlv_u32(4, 1),
        tlv_u32(5, 1),
        tlv_u32(6, 10),
        tlv_u32(7, 0),
    ]
    caps_bytes = b"".join([
        tlv_u32(1, 1),
        tlv_str(4, "1.0.0"),
        tlv_str(2, "build_1"),
        tlv_str(3, "deadbeef"),
        tlv_u32(5, 1),
        tlv_u32(6, 10),
        tlv_u32(7, 2),
        tlv_u32(8, 3),
        tlv_u32(9, 4),
        tlv_u32(12, 0),
        tlv_u32(13, 0),
        tlv_u32(14, 0),
        tlv_u32(15, 0),
        tlv_u32(16, 1),
        tlv_u32(17, 0),
        tlv_u32(18, 1),
        tlv_u32(19, 1),
        tlv_u32(20, 1),
        tlv_u32(21, 260),
        tlv_container(10, caps_backend),
        tlv_container(11, caps_sel),
    ])
    write_vector(
        caps_dir,
        "caps_v1_basic",
        caps_bytes,
        [
            "schema_version=1",
            "os_family=1",
            "cpu_arch=3",
            "ram_class=4",
            "backends=1",
            "selections=1",
        ],
        schema_id=10,
        version=1,
        manifest_entries=caps_entries,
    )
    write_manifest(caps_dir, caps_entries)

    # Diagnostics bundle meta/index (launcher).
    bundle_meta_dir = os.path.join(out_root, "diag_bundle_meta")
    bundle_meta_entries: list[dict[str, str]] = []
    bundle_meta_bytes = b"".join([
        tlv_u32(1, 1),
        tlv_u32(2, 1),
        tlv_str(3, "default"),
        tlv_str(4, "inst_alpha"),
        tlv_str(5, "build_1"),
        tlv_str(6, "deadbeef"),
        tlv_str(7, "1.0.0"),
        tlv_u32(8, 3),
        tlv_u32(9, 2),
        tlv_u64(10, 0x1111222233334444),
    ])
    write_vector(
        bundle_meta_dir,
        "bundle_meta_v1",
        bundle_meta_bytes,
        [
            "schema_version=1",
            "bundle_version=1",
            "mode=default",
            "instance_id=inst_alpha",
            "audit_count=3",
            "run_count=2",
        ],
        schema_id=12,
        version=1,
        manifest_entries=bundle_meta_entries,
    )
    write_manifest(bundle_meta_dir, bundle_meta_entries)

    bundle_index_dir = os.path.join(out_root, "diag_bundle_index")
    bundle_index_entries: list[dict[str, str]] = []
    index_entry = [
        tlv_str(1, "audit/launcher_audit_0000000000000001.tlv"),
        tlv_bytes(2, b"\x11" * 32),
        tlv_u64(3, 1234),
    ]
    bundle_index_bytes = b"".join([
        tlv_u32(1, 1),
        tlv_container(2, index_entry),
    ])
    write_vector(
        bundle_index_dir,
        "bundle_index_v1",
        bundle_index_bytes,
        [
            "schema_version=1",
            "entries=1",
            "entry[0].path=audit/launcher_audit_0000000000000001.tlv",
        ],
        schema_id=11,
        version=1,
        manifest_entries=bundle_index_entries,
    )
    write_manifest(bundle_index_dir, bundle_index_entries)

    # Installed state (setup, DSK TLV).
    state_dir = os.path.join(out_root, "installed_state")
    state_entries: list[dict[str, str]] = []
    components_payload = b"".join([
        dsk_str(0x3010, "core"),
        dsk_str(0x3010, "base"),
    ])
    roots_payload = b"".join([
        dsk_str(0x3011, "root_a"),
        dsk_str(0x3011, "root_b"),
    ])
    artifact_entry = b"".join([
        dsk_u32(0x3021, 1),
        dsk_str(0x3022, "bin/core.exe"),
        dsk_u64(0x3023, 0x1111111111111111),
        dsk_u64(0x3024, 64),
    ])
    artifacts_payload = dsk_container(0x3020, [artifact_entry])
    reg_entry = b"".join([
        dsk_u16(0x3031, 1),
        dsk_str(0x3032, "shortcut://dominium"),
        dsk_u16(0x3033, 2),
    ])
    regs_payload = dsk_container(0x3030, [reg_entry])
    state_payload = b"".join([
        dsk_str(0x3001, "dominium"),
        dsk_str(0x3002, "1.0.0"),
        dsk_str(0x3003, "splat_default"),
        dsk_u16(0x3004, 2),
        dsk_str(0x3005, "C:/Dominium"),
        dsk_u16(0x300A, 1),
        dsk_u64(0x3007, 0xAAAAAAAABBBBBBBB),
        dsk_u64(0x3008, 0xCCCCCCCCDDDDDDDD),
        dsk_container(0x3006, [components_payload]),
        dsk_container(0x3009, [roots_payload]),
        dsk_container(0x300B, [artifacts_payload]),
        dsk_container(0x300C, [regs_payload]),
        dsk_u64(0x300D, 0x1111222233334444),
        dsk_rec(0x3999, b"unknown"),
    ])
    state_bytes = dsk_wrap(state_payload)
    write_vector(
        state_dir,
        "installed_state_v1",
        state_bytes,
        [
            "product_id=dominium",
            "installed_version=1.0.0",
            "selected_splat=splat_default",
            "components=2",
            "install_roots=2",
            "artifacts=1",
            "registrations=1",
        ],
        schema_id=6,
        version=1,
        manifest_entries=state_entries,
    )
    write_manifest(state_dir, state_entries)

    # Core job def/state.
    job_def_dir = os.path.join(out_root, "core_job_def")
    job_def_entries: list[dict[str, str]] = []
    step_a = b"".join([tlv_u32(1, 1), tlv_u32(2, 1), tlv_u32(3, 0)])
    step_b = b"".join([tlv_u32(1, 2), tlv_u32(2, 3), tlv_u32(3, 1), tlv_u32(4, 1)])
    def_payload = b"".join([
        tlv_u32(2, 1),
        tlv_u32(3, 3),
        tlv_u32(4, 2),
        tlv_container(5, [step_a]),
        tlv_container(5, [step_b]),
    ])
    job_def_bytes = tlv_rec(1, def_payload)
    write_vector(
        job_def_dir,
        "job_def_v1",
        job_def_bytes,
        [
            "schema_version=1",
            "job_type=3",
            "step_count=2",
            "steps=2",
        ],
        schema_id=7,
        version=1,
        manifest_entries=job_def_entries,
    )
    write_manifest(job_def_dir, job_def_entries)

    job_state_dir = os.path.join(out_root, "core_job_state")
    job_state_entries: list[dict[str, str]] = []
    retry_entries = []
    for i in range(32):
        retry_entries.append(tlv_container(18, [tlv_u32(1, i), tlv_u32(2, 0)]))
    err_detail = tlv_container(6, [tlv_u32(1, 1), tlv_u32(2, 1), tlv_u32(3, 7)])
    err_payload = b"".join([
        tlv_u32(1, 2),
        tlv_u32(2, 3),
        tlv_u32(3, 4),
        tlv_u32(4, 5),
        tlv_u32(5, 1),
        err_detail,
    ])
    state_payload = b"".join([
        tlv_u32(11, 1),
        tlv_u64(12, 0xABCDEF0123456789),
        tlv_u32(13, 3),
        tlv_u32(14, 2),
        tlv_u32(15, 1),
        tlv_u32(16, 2),
        b"".join(retry_entries),
        tlv_container(19, [err_payload]),
    ])
    job_state_bytes = tlv_rec(10, state_payload)
    write_vector(
        job_state_dir,
        "job_state_v1",
        job_state_bytes,
        [
            "schema_version=1",
            "job_id=0xabcdef0123456789",
            "job_type=3",
            "current_step=2",
            "completed_bitset=1",
            "outcome=2",
        ],
        schema_id=8,
        version=1,
        manifest_entries=job_state_entries,
    )
    write_manifest(job_state_dir, job_state_entries)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
