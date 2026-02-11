"""Deterministic ControlX run logging."""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict


def compute_run_id(prompt_hash: str, index: int) -> str:
    token = "{}:{}".format(prompt_hash or "", index)
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return "controlx-run-{}".format(digest[:16])


def write_json(path: str, payload: Dict[str, Any]) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_runlog(run_dir: str, payload: Dict[str, Any]) -> str:
    path = os.path.join(run_dir, "RUNLOG.json")
    write_json(path, payload)
    return path

