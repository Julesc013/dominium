"""Deterministic archive bundle builder isolated from release-layer audit scans."""

from __future__ import annotations

import gzip
import hashlib
import os
import tarfile
from typing import Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256


DEFAULT_ARCHIVE_BUNDLE_PREFIX = "dominium-archive"


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: object) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: object) -> str:
    return _token(path).replace("\\", "/")


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(_norm(path), "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _gather_bundle_rows(
    source_root: str,
    *,
    excluded_rel_paths: Sequence[str] | None = None,
) -> list[tuple[str, str]]:
    root = _norm(source_root)
    excluded = {_norm_rel(path) for path in list(excluded_rel_paths or []) if _norm_rel(path)}
    rows: list[tuple[str, str]] = []
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(dirnames)
        for name in sorted(filenames):
            abs_path = os.path.join(current_root, name)
            rel_path = _norm_rel(os.path.relpath(abs_path, root))
            if rel_path in excluded:
                continue
            rows.append((rel_path, abs_path))
    return sorted(rows, key=lambda row: row[0])


def build_deterministic_archive_bundle(
    source_root: str,
    output_path: str,
    *,
    root_arcname: str = "",
    extra_files: Mapping[str, object] | None = None,
) -> dict:
    root = _norm(source_root)
    target = _norm(output_path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    excluded: list[str] = []
    try:
        if os.path.commonpath([root, target]) == root:
            excluded.append(_norm_rel(os.path.relpath(target, root)))
    except ValueError:
        pass
    if os.path.isfile(target):
        os.remove(target)

    source_rows = _gather_bundle_rows(root, excluded_rel_paths=excluded)
    extra_rows = sorted(
        (
            (_norm_rel(key), _norm(value))
            for key, value in _as_map(extra_files).items()
            if _norm_rel(key) and os.path.isfile(_norm(value))
        ),
        key=lambda row: row[0],
    )
    arc_root = _token(root_arcname) or os.path.splitext(os.path.splitext(os.path.basename(target))[0])[0] or DEFAULT_ARCHIVE_BUNDLE_PREFIX

    with open(target, "wb") as raw_handle:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw_handle, mtime=0) as gzip_handle:
            with tarfile.open(fileobj=gzip_handle, mode="w") as tar_handle:
                for rel_path, abs_path in source_rows:
                    arcname = _norm_rel(os.path.join(arc_root, rel_path))
                    tar_info = tar_handle.gettarinfo(abs_path, arcname=arcname)
                    tar_info.uid = 0
                    tar_info.gid = 0
                    tar_info.uname = ""
                    tar_info.gname = ""
                    tar_info.mtime = 0
                    tar_info.mode = 0o644
                    with open(abs_path, "rb") as input_handle:
                        tar_handle.addfile(tar_info, fileobj=input_handle)
                for rel_path, abs_path in extra_rows:
                    arcname = _norm_rel(os.path.join(arc_root, rel_path))
                    tar_info = tarfile.TarInfo(name=arcname)
                    tar_info.uid = 0
                    tar_info.gid = 0
                    tar_info.uname = ""
                    tar_info.gname = ""
                    tar_info.mtime = 0
                    tar_info.mode = 0o644
                    tar_info.size = os.path.getsize(abs_path)
                    with open(abs_path, "rb") as input_handle:
                        tar_handle.addfile(tar_info, fileobj=input_handle)

    file_rows = [
        {"path": rel_path, "sha256": _sha256_file(abs_path)}
        for rel_path, abs_path in source_rows
    ] + [
        {"path": rel_path, "sha256": _sha256_file(abs_path)}
        for rel_path, abs_path in extra_rows
    ]
    return {
        "bundle_path": target,
        "bundle_hash": _sha256_file(target),
        "root_arcname": arc_root,
        "file_count": int(len(source_rows) + len(extra_rows)),
        "file_rows": file_rows,
        "deterministic_fingerprint": canonical_sha256(
            {
                "root_arcname": arc_root,
                "files": file_rows,
            }
        ),
    }


__all__ = ["DEFAULT_ARCHIVE_BUNDLE_PREFIX", "build_deterministic_archive_bundle"]
