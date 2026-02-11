"""Reproducible build hash comparison helpers."""

from __future__ import annotations

import hashlib
import os
from typing import Dict, Iterable, List, Tuple


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1 << 16)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def canonical_hash_map(paths: Iterable[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for path in sorted(set(os.path.normpath(item) for item in paths if item)):
        if not os.path.isfile(path):
            continue
        out[path.replace("\\", "/")] = _sha256_file(path)
    return out


def compare_hash_maps(left: Dict[str, str], right: Dict[str, str]) -> Tuple[bool, List[str]]:
    issues: List[str] = []
    left_keys = sorted(left.keys())
    right_keys = sorted(right.keys())
    if left_keys != right_keys:
        issues.append("refuse.repro_build.path_set_mismatch")
        return False, issues
    for key in left_keys:
        if left[key] != right.get(key, ""):
            issues.append("refuse.repro_build.hash_mismatch.{}".format(key))
    return len(issues) == 0, sorted(set(issues))

