"""STRICT test: inline response-curve findings must be tracked in deprecation registry."""

from __future__ import annotations

import json
import os


TEST_ID = "test_inline_response_curve_deprecation_map"
TEST_TAGS = ["strict", "meta", "deprecation"]


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def run(repo_root: str):
    findings_payload = _load_json(repo_root, "docs/audit/auditx/FINDINGS.json")
    deprecations_payload = _load_json(repo_root, "data/registries/deprecation_registry.json")
    if not deprecations_payload:
        return {"status": "fail", "message": "deprecation_registry missing or invalid"}

    deprecated_sites = set()
    rows = list((dict(deprecations_payload.get("record") or {})).get("deprecations") or [])
    for row in rows:
        if not isinstance(row, dict):
            continue
        ext = dict(row.get("extensions") or {})
        if str(ext.get("invariant_id", "")).strip() != "INV-REALISM-DETAIL-MUST-BE-MODEL":
            continue
        source_path = str(ext.get("source_path", "")).replace("\\", "/").strip()
        line_start = int(ext.get("line_start", 0) or 0)
        if source_path and line_start:
            deprecated_sites.add((source_path, line_start))

    findings = []
    for row in list(findings_payload.get("findings") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("analyzer_id", "")).strip() != "E179_INLINE_RESPONSE_CURVE_SMELL":
            continue
        loc = dict(row.get("location") or {})
        source_path = str(loc.get("file_path", "")).replace("\\", "/").strip()
        line_start = int(loc.get("line_start", 0) or 0)
        if source_path and line_start:
            findings.append((source_path, line_start))

    if not findings:
        return {"status": "pass", "message": "no inline response-curve findings present"}

    missing = sorted(site for site in findings if site not in deprecated_sites)
    if missing:
        sample = ",".join("{}:{}".format(path, line) for path, line in missing[:8])
        return {
            "status": "fail",
            "message": "inline response-curve finding(s) missing deprecation mapping: {}".format(sample),
        }
    return {
        "status": "pass",
        "message": "all inline response-curve findings are tracked in deprecation registry (count={})".format(len(findings)),
    }

