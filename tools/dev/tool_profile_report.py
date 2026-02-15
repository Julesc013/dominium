"""Deterministic renderer for profile trace markdown summaries."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from typing import Dict, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.validator import validate_instance  # noqa: E402


TOOL_ID = "tool_profile_report"
TOOL_VERSION = "1.0.0"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _resolve_root(repo_root: str, path: str) -> str:
    token = str(path or "").strip()
    if not token:
        return repo_root
    if os.path.isabs(token):
        return os.path.normpath(token)
    return os.path.normpath(os.path.join(repo_root, token))


def _repo_relative(repo_root: str, path: str) -> str:
    try:
        return _norm(os.path.relpath(path, repo_root))
    except ValueError:
        return _norm(path)


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return payload, ""


def _write_text(path: str, text: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text.replace("\r\n", "\n"))


def _render_markdown(trace_payload: dict, trace_path: str) -> str:
    registry_hashes = dict(trace_payload.get("registry_hashes") or {})
    metrics = dict(trace_payload.get("metrics") or {})
    lines = [
        "Status: DERIVED",
        "Version: 1.0.0",
        "Generator: {} {}".format(TOOL_ID, TOOL_VERSION),
        "Source Trace: `{}`".format(_norm(trace_path)),
        "",
        "# Profile Trace Report",
        "",
        "## Identity",
        "",
        "- trace_id: `{}`".format(str(trace_payload.get("trace_id", ""))),
        "- bii: `{}`".format(str(trace_payload.get("bii", ""))),
        "- bundle_id: `{}`".format(str(trace_payload.get("bundle_id", ""))),
        "- session_id: `{}`".format(str(trace_payload.get("session_id", ""))),
        "- scenario_id: `{}`".format(str(trace_payload.get("scenario_id", ""))),
        "- pack_lock_hash: `{}`".format(str(trace_payload.get("pack_lock_hash", ""))),
        "",
        "## Deterministic Metrics",
        "",
        "- resolved_pack_count: `{}`".format(int(metrics.get("resolved_pack_count", 0) or 0)),
        "- registry_count: `{}`".format(int(metrics.get("registry_count", 0) or 0)),
        "- estimated_compute_units: `{}`".format(int(metrics.get("estimated_compute_units", 0) or 0)),
        "- profile_ms: `{}`".format(int(metrics.get("profile_ms", 0) or 0)),
        "",
        "## Registry Hashes",
        "",
    ]
    for key in sorted(registry_hashes.keys()):
        lines.append("- {}: `{}`".format(str(key), str(registry_hashes.get(key, ""))))
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Metrics are informational and non-gating.",
            "- Structure is deterministic and schema-validated (`schemas/profile_trace.schema.json`).",
            "",
        ]
    )
    return "\n".join(lines)


def build_profile_report(repo_root: str, trace_rel: str, out_rel: str) -> Dict[str, object]:
    trace_abs = _resolve_root(repo_root, trace_rel)
    trace_payload, trace_err = _read_json(trace_abs)
    if trace_err:
        return {
            "result": "refused",
            "reason_code": "refusal.profile.trace_missing",
            "message": "profile trace input is missing or invalid",
            "errors": [{"code": "trace_missing", "path": "$.trace", "message": trace_err}],
        }

    validated = validate_instance(
        repo_root=repo_root,
        schema_name="profile_trace",
        payload=trace_payload,
        strict_top_level=True,
    )
    if not bool(validated.get("valid", False)):
        return {
            "result": "refused",
            "reason_code": "refusal.profile.trace_schema_invalid",
            "message": "profile trace failed schema validation",
            "errors": list(validated.get("errors") or []),
        }

    markdown = _render_markdown(trace_payload=trace_payload, trace_path=_repo_relative(repo_root, trace_abs))
    out_abs = _resolve_root(repo_root, out_rel)
    _write_text(out_abs, markdown + "\n")
    return {
        "result": "complete",
        "trace_path": _repo_relative(repo_root, trace_abs),
        "report_path": _repo_relative(repo_root, out_abs),
        "trace_hash": str(validated.get("payload_hash", "")),
        "report_hash": hashlib.sha256(markdown.encode("utf-8")).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render deterministic markdown profile report from profile trace.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--trace", default="docs/audit/perf/profile_trace.sample.json")
    parser.add_argument("--out", default="docs/audit/perf/profile_trace.sample.md")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(args.repo_root)) if str(args.repo_root).strip() else REPO_ROOT_HINT
    result = build_profile_report(
        repo_root=repo_root,
        trace_rel=str(args.trace),
        out_rel=str(args.out),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    token = str(result.get("result", "error"))
    if token == "complete":
        return 0
    if token == "refused":
        return 2
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
