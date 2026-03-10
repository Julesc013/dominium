"""APPSHELL-2 TestX helpers."""

from __future__ import annotations

import hashlib
import json
import os
import sys


def ensure_repo_on_path(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)


def canonical_hash(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def load_jsonl(path: str) -> list[dict]:
    rows = []
    if not os.path.isfile(path):
        return rows
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            text = str(line).strip()
            if not text:
                continue
            payload = json.loads(text)
            if isinstance(payload, dict):
                rows.append(payload)
    return rows

