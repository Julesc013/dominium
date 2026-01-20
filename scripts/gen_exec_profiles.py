#!/usr/bin/env python3
import os
import struct


def tag(a, b, c, d):
    return ord(a) | (ord(b) << 8) | (ord(c) << 16) | (ord(d) << 24)


def u32_le(v):
    return struct.pack("<I", v)


def tlv(tag_id, payload):
    return u32_le(tag_id) + u32_le(len(payload)) + payload


def arr_u32(values):
    return b"".join(u32_le(v) for v in values)


CHUNK_TYPE = tag("E", "P", "R", "F")
CHUNK_VERSION = 1

T_PROFILE_ID = tag("P", "I", "D", "0")
T_SCHED_ORDER = tag("S", "C", "H", "D")
T_KERNEL_ORDER = tag("K", "O", "R", "D")
T_ALLOW_MASK = tag("A", "L", "O", "W")
T_MIN_CORES = tag("M", "I", "N", "C")
T_BUDGET_ID = tag("B", "I", "D", "0")
T_BUDGET_CPU_AUTH = tag("B", "C", "A", "U")
T_BUDGET_CPU_DER = tag("B", "C", "D", "R")
T_BUDGET_IO_DER = tag("B", "I", "O", "D")
T_BUDGET_NET = tag("B", "N", "E", "T")
T_MEM_CLASS = tag("M", "E", "M", "C")
T_DEGRADATION_ID = tag("D", "E", "G", "R")
T_CPU_SCALE_MIN = tag("C", "S", "M", "N")
T_CPU_SCALE_MAX = tag("C", "S", "M", "X")
T_IO_SCALE_MAX = tag("I", "O", "S", "X")
T_NET_SCALE_MAX = tag("N", "S", "M", "X")
T_RENDER_ALLOW = tag("R", "N", "D", "L")


PROFILES = {
    "retro_1990s": {
        "scheduler_order": [0],
        "kernel_order": [0],
        "allow_mask": 0,
        "min_cores": 0,
        "budget_id": "retro_1990s",
        "cpu_auth": 50,
        "cpu_der": 25,
        "io_der": 8,
        "net": 4,
        "mem_class": 1,
        "degradation_id": "retro_aggressive",
        "cpu_scale_min": 1,
        "cpu_scale_max": 1,
        "io_scale_max": 1,
        "net_scale_max": 1,
        "render_allow": [],
    },
    "baseline_2010": {
        "scheduler_order": [1, 0],
        "kernel_order": [0, 1, 2],
        "allow_mask": 3,
        "min_cores": 4,
        "budget_id": "baseline_2010",
        "cpu_auth": 200,
        "cpu_der": 120,
        "io_der": 40,
        "net": 20,
        "mem_class": 2,
        "degradation_id": "baseline_conservative",
        "cpu_scale_min": 1,
        "cpu_scale_max": 2,
        "io_scale_max": 2,
        "net_scale_max": 2,
        "render_allow": [],
    },
    "modern_2020": {
        "scheduler_order": [1, 0],
        "kernel_order": [1, 0, 2],
        "allow_mask": 7,
        "min_cores": 4,
        "budget_id": "modern_2020",
        "cpu_auth": 400,
        "cpu_der": 300,
        "io_der": 120,
        "net": 40,
        "mem_class": 3,
        "degradation_id": "modern_balanced",
        "cpu_scale_min": 1,
        "cpu_scale_max": 4,
        "io_scale_max": 3,
        "net_scale_max": 2,
        "render_allow": [],
    },
    "server_mmo": {
        "scheduler_order": [1, 0],
        "kernel_order": [1, 0, 2],
        "allow_mask": 3,
        "min_cores": 4,
        "budget_id": "server_mmo",
        "cpu_auth": 500,
        "cpu_der": 400,
        "io_der": 150,
        "net": 25,
        "mem_class": 4,
        "degradation_id": "server_authoritative",
        "cpu_scale_min": 1,
        "cpu_scale_max": 4,
        "io_scale_max": 3,
        "net_scale_max": 1,
        "render_allow": [],
    },
}


def build_profile(profile_id, data):
    records = []
    records.append(tlv(T_PROFILE_ID, profile_id.encode("ascii")))
    records.append(tlv(T_SCHED_ORDER, arr_u32(data["scheduler_order"])))
    records.append(tlv(T_KERNEL_ORDER, arr_u32(data["kernel_order"])))
    records.append(tlv(T_ALLOW_MASK, u32_le(data["allow_mask"])))
    records.append(tlv(T_MIN_CORES, u32_le(data["min_cores"])))
    records.append(tlv(T_BUDGET_ID, data["budget_id"].encode("ascii")))
    records.append(tlv(T_BUDGET_CPU_AUTH, u32_le(data["cpu_auth"])))
    records.append(tlv(T_BUDGET_CPU_DER, u32_le(data["cpu_der"])))
    records.append(tlv(T_BUDGET_IO_DER, u32_le(data["io_der"])))
    records.append(tlv(T_BUDGET_NET, u32_le(data["net"])))
    records.append(tlv(T_MEM_CLASS, u32_le(data["mem_class"])))
    records.append(tlv(T_DEGRADATION_ID, data["degradation_id"].encode("ascii")))
    records.append(tlv(T_CPU_SCALE_MIN, u32_le(data["cpu_scale_min"])))
    records.append(tlv(T_CPU_SCALE_MAX, u32_le(data["cpu_scale_max"])))
    records.append(tlv(T_IO_SCALE_MAX, u32_le(data["io_scale_max"])))
    records.append(tlv(T_NET_SCALE_MAX, u32_le(data["net_scale_max"])))
    for name in data["render_allow"]:
        records.append(tlv(T_RENDER_ALLOW, name.encode("ascii")))

    chunk_payload = b"".join(records)
    header_size = 32
    dir_entry_size = 32
    chunk_offset = header_size
    dir_offset = header_size + len(chunk_payload)

    header = struct.pack(
        "<4sHHIQIII",
        b"DTLV",
        0xFFFE,
        1,
        header_size,
        dir_offset,
        1,
        dir_entry_size,
        0,
    )
    entry = struct.pack(
        "<IHHQQII",
        CHUNK_TYPE,
        CHUNK_VERSION,
        0,
        chunk_offset,
        len(chunk_payload),
        0,
        0,
    )
    return header + chunk_payload + entry


def main():
    out_dir = os.path.join("data", "defaults", "profiles")
    os.makedirs(out_dir, exist_ok=True)
    for profile_id, data in PROFILES.items():
        blob = build_profile(profile_id, data)
        out_path = os.path.join(out_dir, profile_id + ".tlv")
        with open(out_path, "wb") as f:
            f.write(blob)


if __name__ == "__main__":
    main()
