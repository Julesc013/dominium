"""Deterministic refusal payload helpers for Pack System tooling."""

from __future__ import annotations

from typing import Any, Dict, List


def build_error(code: str, message: str, path: str = "") -> Dict[str, str]:
    return {
        "code": str(code),
        "message": str(message),
        "path": str(path),
    }


def sort_errors(errors: List[Dict[str, str]]) -> List[Dict[str, str]]:
    out = []
    for row in errors or []:
        out.append(
            {
                "code": str(row.get("code", "")),
                "message": str(row.get("message", "")),
                "path": str(row.get("path", "")),
            }
        )
    return sorted(out, key=lambda row: (row["code"], row["path"], row["message"]))


def result_complete(payload: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(payload)
    out["result"] = "complete"
    out["errors"] = []
    return out


def result_refused(payload: Dict[str, Any], errors: List[Dict[str, str]]) -> Dict[str, Any]:
    out = dict(payload)
    stable = sort_errors(errors)
    out["result"] = "refused"
    out["error_count"] = len(stable)
    out["errors"] = stable
    return out

