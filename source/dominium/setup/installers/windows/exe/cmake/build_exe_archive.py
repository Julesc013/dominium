#!/usr/bin/env python3
from __future__ import print_function

import argparse
import os
import struct
import sys


MAGIC = b"DSUARCH1"
TAIL_MAGIC = b"DSUTAIL1"
VERSION = 1


def crc32_update(crc, data):
    c = crc ^ 0xFFFFFFFF
    for b in data:
        x = (c ^ b) & 0xFF
        for _ in range(8):
            if x & 1:
                x = (x >> 1) ^ 0xEDB88320
            else:
                x >>= 1
        c = (c >> 8) ^ x
    return c ^ 0xFFFFFFFF


def crc32(data):
    return crc32_update(0, data)


def norm_rel(path):
    path = path.replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    while path.startswith("/"):
        path = path[1:]
    return path


def walk_files(root_dir):
    root_dir = os.path.abspath(root_dir)
    rels = []
    for cur_root, dirs, files in os.walk(root_dir):
        dirs.sort()
        files.sort()
        rel_root = os.path.relpath(cur_root, root_dir)
        rel_root = "" if rel_root == "." else norm_rel(rel_root)
        for fn in files:
            rel = norm_rel(os.path.join(rel_root, fn))
            if not rel:
                continue
            rels.append(rel)
    return sorted(set(rels))


def build_table(root_dir, rels):
    entries = []
    data_size = 0
    for rel in rels:
        abs_p = os.path.join(root_dir, rel.replace("/", os.sep))
        if not os.path.isfile(abs_p):
            raise RuntimeError("missing file: %s" % rel)
        size = os.path.getsize(abs_p)
        with open(abs_p, "rb") as f:
            data = f.read()
        crc = crc32(data)
        entries.append({
            "path": rel,
            "offset": data_size,
            "size": size,
            "crc": crc,
        })
        data_size += size

    table = bytearray()
    for ent in entries:
        path_bytes = ent["path"].encode("utf-8")
        if len(path_bytes) > 0xFFFF:
            raise RuntimeError("path too long: %s" % ent["path"])
        table += struct.pack("<HHQQI", len(path_bytes), 0, ent["offset"], ent["size"], ent["crc"])
        table += path_bytes

    return entries, bytes(table), data_size


def main(argv):
    ap = argparse.ArgumentParser(description="Append a DSU EXE archive to a stub executable.")
    ap.add_argument("--stub", required=True, help="Path to stub exe (frontend binary)")
    ap.add_argument("--input", required=True, help="Input directory to embed")
    ap.add_argument("--output", required=True, help="Output exe path")
    args = ap.parse_args(argv)

    stub_path = os.path.abspath(args.stub)
    input_dir = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)

    if not os.path.isfile(stub_path):
        raise SystemExit("stub not found: %s" % stub_path)
    if not os.path.isdir(input_dir):
        raise SystemExit("input dir not found: %s" % input_dir)

    rels = walk_files(input_dir)
    entries, table_bytes, data_size = build_table(input_dir, rels)
    table_crc = crc32(table_bytes)

    with open(stub_path, "rb") as f:
        stub_data = f.read()

    header = struct.pack(
        "<8sIIQQI",
        MAGIC,
        VERSION,
        len(entries),
        len(table_bytes),
        data_size,
        table_crc,
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as out:
        out.write(stub_data)
        header_offset = out.tell()
        out.write(header)
        out.write(table_bytes)
        for ent in entries:
            abs_p = os.path.join(input_dir, ent["path"].replace("/", os.sep))
            with open(abs_p, "rb") as f:
                out.write(f.read())
        out.write(struct.pack("<8sQ", TAIL_MAGIC, header_offset))

    print("wrote", output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
