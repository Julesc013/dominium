#!/usr/bin/env python3
from __future__ import print_function

import argparse
import gzip
import os
import shutil
import sys
import tarfile
import time
import zipfile


def _norm_rel(path):
    path = path.replace("\\", "/")
    if path.startswith("./"):
        path = path[2:]
    while path.startswith("/"):
        path = path[1:]
    return path


def _iter_tree(root_dir):
    root_dir = os.path.abspath(root_dir)

    dirs = []
    files = []

    for cur_root, cur_dirs, cur_files in os.walk(root_dir):
        cur_dirs.sort()
        cur_files.sort()

        rel_root = os.path.relpath(cur_root, root_dir)
        rel_root = "" if rel_root == "." else _norm_rel(rel_root)

        for d in cur_dirs:
            rel = _norm_rel(os.path.join(rel_root, d))
            dirs.append(rel)

        for f in cur_files:
            if f in (".stage_stamp",):
                continue
            rel = _norm_rel(os.path.join(rel_root, f))
            files.append(rel)

    dirs = sorted(set(dirs))
    files = sorted(set(files))
    return dirs, files


def _source_date_epoch():
    v = os.environ.get("SOURCE_DATE_EPOCH", "").strip()
    if not v:
        return 0
    try:
        return int(v)
    except Exception:
        return 0


def _zip_datetime(epoch):
    # ZIP timestamps are localtime-based and cannot represent dates before 1980.
    # Use a stable canonical timestamp instead.
    if epoch <= 0:
        return (1980, 1, 1, 0, 0, 0)
    t = time.gmtime(epoch)
    year = max(1980, t.tm_year)
    return (year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)


def make_zip(input_dir, output_path, root_name, epoch):
    if os.path.exists(output_path):
        os.remove(output_path)

    dirs, files = _iter_tree(input_dir)
    zdt = _zip_datetime(epoch)

    with zipfile.ZipFile(output_path, "w") as zf:
        # Explicit directory entries to preserve empty dirs.
        for rel_d in dirs:
            arc = _norm_rel(os.path.join(root_name, rel_d)) + "/"
            zi = zipfile.ZipInfo(arc, date_time=zdt)
            zi.compress_type = zipfile.ZIP_STORED
            zi.external_attr = (0o40755 & 0xFFFF) << 16
            zf.writestr(zi, b"")

        for rel_f in files:
            src = os.path.join(input_dir, rel_f)
            arc = _norm_rel(os.path.join(root_name, rel_f))
            st = os.stat(src)
            mode = (st.st_mode & 0o777) if hasattr(st, "st_mode") else 0o644

            zi = zipfile.ZipInfo(arc, date_time=zdt)
            zi.compress_type = zipfile.ZIP_STORED
            zi.external_attr = (mode & 0xFFFF) << 16

            with open(src, "rb") as f:
                data = f.read()
            zf.writestr(zi, data)


def make_tar_gz(input_dir, output_path, root_name, epoch):
    if os.path.exists(output_path):
        os.remove(output_path)

    dirs, files = _iter_tree(input_dir)

    # Stream tar into a gzip with fixed mtime for reproducibility.
    with open(output_path, "wb") as out_f:
        with gzip.GzipFile(filename="", mode="wb", fileobj=out_f, mtime=epoch) as gz:
            with tarfile.open(fileobj=gz, mode="w|") as tf:
                for rel_d in dirs:
                    arc = _norm_rel(os.path.join(root_name, rel_d))
                    ti = tarfile.TarInfo(arc)
                    ti.type = tarfile.DIRTYPE
                    ti.mode = 0o755
                    ti.mtime = epoch
                    ti.uid = 0
                    ti.gid = 0
                    ti.uname = ""
                    ti.gname = ""
                    tf.addfile(ti)

                for rel_f in files:
                    src = os.path.join(input_dir, rel_f)
                    arc = _norm_rel(os.path.join(root_name, rel_f))
                    st = os.stat(src)
                    ti = tarfile.TarInfo(arc)
                    ti.type = tarfile.REGTYPE
                    ti.size = st.st_size
                    ti.mode = (st.st_mode & 0o777) if hasattr(st, "st_mode") else 0o644
                    ti.mtime = epoch
                    ti.uid = 0
                    ti.gid = 0
                    ti.uname = ""
                    ti.gname = ""
                    with open(src, "rb") as f:
                        tf.addfile(ti, fileobj=f)


def main(argv):
    ap = argparse.ArgumentParser(description="Create deterministic archives (ZIP or tar.gz) from an input directory.")
    ap.add_argument("--format", required=True, choices=["zip", "tar.gz"], help="Archive format")
    ap.add_argument("--input", required=True, help="Input directory (staged bundle root)")
    ap.add_argument("--output", required=True, help="Output archive path")
    ap.add_argument("--root-name", required=True, help="Root directory name inside the archive")
    args = ap.parse_args(argv)

    input_dir = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)
    root_name = args.root_name.strip().strip("/").strip("\\")
    if not root_name:
        raise SystemExit("root-name must be non-empty")
    if not os.path.isdir(input_dir):
        raise SystemExit("input directory not found: %s" % input_dir)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    epoch = _source_date_epoch()
    if args.format == "zip":
        make_zip(input_dir, output_path, root_name, epoch)
    else:
        make_tar_gz(input_dir, output_path, root_name, epoch)

    print("wrote", output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
