"""ControlX bridge into gate remediation artifacts."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List


def _rel(repo_root: str, path: str) -> str:
    return os.path.relpath(path, repo_root).replace("\\", "/")


def _collect_remediation_dirs(repo_root: str, ws_id: str) -> List[str]:
    root = os.path.join(repo_root, "docs", "audit", "remediation", ws_id)
    if not os.path.isdir(root):
        return []
    out = []
    for entry in sorted(os.listdir(root)):
        full = os.path.join(root, entry)
        if os.path.isdir(full):
            out.append(_rel(repo_root, full))
    return out[-20:]


def write_remediation_links(repo_root: str, run_dir: str, ws_id: str, route_result: Dict[str, Any]) -> Dict[str, Any]:
    links = _collect_remediation_dirs(repo_root, ws_id)
    payload = {
        "artifact_class": "DERIVED_VIEW",
        "workspace_id": ws_id,
        "returncode": int(route_result.get("returncode", 1)),
        "mechanical_failure": bool(route_result.get("mechanical_failure", False)),
        "semantic_failure": bool(route_result.get("semantic_failure", False)),
        "gate_steps": [
            {
                "command": " ".join(step.get("command", [])),
                "returncode": int(step.get("returncode", 1)),
            }
            for step in route_result.get("steps", [])
        ],
        "remediation_artifacts": links,
    }
    path = os.path.join(run_dir, "remediation_links.json")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return payload

