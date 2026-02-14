"""AuditX deterministic report writers."""

import hashlib
import json
import os
import platform
from datetime import datetime, timezone

from canonicalize import canonical_json_string, canonicalize_json_payload


CANONICAL_ARTIFACT_CLASS = "CANONICAL"
DERIVED_VIEW_ARTIFACT_CLASS = "DERIVED_VIEW"
RUN_META_ARTIFACT_CLASS = "RUN_META"

_CANONICAL_FINDINGS_SCHEMA_ID = "dominium.auditx.findings"
_CANONICAL_INVARIANT_MAP_SCHEMA_ID = "dominium.auditx.invariant_map"
_CANONICAL_PROMOTION_SCHEMA_ID = "dominium.auditx.promotion_candidates"
_CANONICAL_TRENDS_SCHEMA_ID = "dominium.auditx.trends"
_CANONICAL_SCHEMA_VERSION = "1.0.0"


def _today_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _doc_header(today):
    return (
        "Status: DERIVED\n"
        "Last Reviewed: {}\n"
        "Supersedes: none\n"
        "Superseded By: none\n\n"
    ).format(today)


def _output_root(repo_root, override=""):
    value = str(override or "").strip()
    if value:
        if os.path.isabs(value):
            return os.path.normpath(value)
        return os.path.normpath(os.path.join(repo_root, value))
    return os.path.join(repo_root, "docs", "audit", "auditx")


def _ensure_output_dir(repo_root, override=""):
    root = _output_root(repo_root, override=override)
    os.makedirs(root, exist_ok=True)
    return root


def _write_json(path, payload):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
        handle.write("\n")


def _write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _severity_counts(findings):
    counts = {}
    for finding in findings:
        severity = finding.get("severity", "UNKNOWN")
        counts[severity] = counts.get(severity, 0) + 1
    return dict(sorted(counts.items()))


def _category_counts(findings):
    counts = {}
    for finding in findings:
        category = finding.get("category", "general")
        counts[category] = counts.get(category, 0) + 1
    return dict(sorted(counts.items()))


def _build_invariant_map(findings):
    table = {}
    for finding in findings:
        invariants = finding.get("related_invariants") or []
        if not invariants:
            continue
        for invariant in invariants:
            record = table.setdefault(
                invariant,
                {
                    "finding_count": 0,
                    "severities": {},
                    "recommended_actions": {},
                    "sample_findings": [],
                },
            )
            record["finding_count"] += 1
            severity = finding.get("severity", "INFO")
            action = finding.get("recommended_action", "DOC_FIX")
            record["severities"][severity] = record["severities"].get(severity, 0) + 1
            record["recommended_actions"][action] = record["recommended_actions"].get(action, 0) + 1
            if len(record["sample_findings"]) < 5:
                record["sample_findings"].append(
                    {
                        "finding_id": finding.get("finding_id", ""),
                        "category": finding.get("category", ""),
                        "location": finding.get("location", {}).get("file", ""),
                    }
                )

    ordered = {}
    for invariant_id in sorted(table.keys()):
        item = table[invariant_id]
        ordered[invariant_id] = {
            "finding_count": item["finding_count"],
            "severities": dict(sorted(item["severities"].items())),
            "recommended_actions": dict(sorted(item["recommended_actions"].items())),
            "sample_findings": item["sample_findings"],
        }
    return ordered


def _build_promotion_candidates(findings):
    candidates = {}
    severity_weight = {"INFO": 0.25, "WARN": 0.5, "RISK": 0.75, "VIOLATION": 1.0}
    for finding in findings:
        severity = str(finding.get("severity", "INFO"))
        confidence = float(finding.get("confidence", 0.0) or 0.0)
        if severity not in ("RISK", "VIOLATION"):
            continue
        if confidence < 0.70:
            continue

        invariants = finding.get("related_invariants") or []
        category = str(finding.get("category", "general"))
        anchor = invariants[0] if invariants else category
        suggested_ruleset = "core.json"
        if category.startswith("workspace"):
            suggested_ruleset = "workspace.json"
        elif category.startswith("prompt") or category.startswith("docs"):
            suggested_ruleset = "prompt_policy.json"
        elif category.startswith("derived"):
            suggested_ruleset = "derived.json"
        elif category.startswith("tool"):
            suggested_ruleset = "tooling.json"
        elif category.startswith("identity"):
            suggested_ruleset = "identity.json"

        rule_type = "INVARIANT_HARDEN"
        if str(finding.get("recommended_action", "")) == "ADD_TEST":
            rule_type = "TEST_REGRESSION"

        key = "{}::{}::{}".format(rule_type, suggested_ruleset, anchor)
        record = candidates.setdefault(
            key,
            {
                "rule_type": rule_type,
                "rationale": "Promote repeated high-confidence semantic risk into static governance.",
                "evidence_paths": set(),
                "suggested_ruleset": suggested_ruleset,
                "risk_score": 0.0,
            },
        )
        paths = set(finding.get("related_paths") or [])
        location_file = str(finding.get("location", {}).get("file", "")).strip()
        if location_file:
            paths.add(location_file)
        record["evidence_paths"].update(path for path in paths if path)
        score = round(confidence * severity_weight.get(severity, 0.25), 4)
        if score > record["risk_score"]:
            record["risk_score"] = score

    rows = []
    for key in sorted(candidates.keys()):
        record = candidates[key]
        rows.append(
            {
                "rule_type": record["rule_type"],
                "rationale": record["rationale"],
                "evidence_paths": sorted(record["evidence_paths"]),
                "suggested_ruleset": record["suggested_ruleset"],
                "risk_score": float(record["risk_score"]),
            }
        )
    rows.sort(key=lambda item: (-item["risk_score"], item["rule_type"], item["suggested_ruleset"], item["evidence_paths"]))
    return rows


def _count_by_key(findings, key_name):
    counts = {}
    for finding in findings:
        key = str(finding.get(key_name, "UNKNOWN"))
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _delta_counts(current, previous):
    out = {}
    all_keys = sorted(set(current.keys()) | set(previous.keys()))
    for key in all_keys:
        out[key] = int(current.get(key, 0)) - int(previous.get(key, 0))
    return out


def _build_trends(findings, cache):
    findings_blob = canonical_json_string({"findings": findings})
    findings_hash = hashlib.sha256(findings_blob.encode("utf-8")).hexdigest()
    category_counts = _count_by_key(findings, "category")
    severity_counts = _count_by_key(findings, "severity")

    previous = {}
    previous_hash = ""
    history = {"history": []}
    if cache is not None:
        history = cache.load_trend_history()
    history_rows = history.get("history", []) if isinstance(history, dict) else []
    for row in reversed(history_rows):
        if not isinstance(row, dict):
            continue
        if str(row.get("findings_hash", "")) == findings_hash:
            continue
        previous_hash = str(row.get("findings_hash", ""))
        previous = row
        break

    previous_category = previous.get("category_frequency", {}) if isinstance(previous, dict) else {}
    previous_severity = previous.get("severity_distribution", {}) if isinstance(previous, dict) else {}
    if not isinstance(previous_category, dict):
        previous_category = {}
    if not isinstance(previous_severity, dict):
        previous_severity = {}

    payload = {
        "artifact_class": CANONICAL_ARTIFACT_CLASS,
        "schema_id": _CANONICAL_TRENDS_SCHEMA_ID,
        "schema_version": _CANONICAL_SCHEMA_VERSION,
        "findings_hash": findings_hash,
        "total_findings": len(findings),
        "category_frequency": category_counts,
        "severity_distribution": severity_counts,
        "delta_over_time": {
            "category_frequency": _delta_counts(category_counts, previous_category),
            "severity_distribution": _delta_counts(severity_counts, previous_severity),
        },
        "history_reference": {
            "previous_distinct_hash": previous_hash,
        },
    }

    if cache is not None:
        next_row = {
            "findings_hash": findings_hash,
            "category_frequency": category_counts,
            "severity_distribution": severity_counts,
        }
        next_history = list(history_rows)
        if not next_history or next_history[-1].get("findings_hash") != findings_hash:
            next_history.append(next_row)
        if len(next_history) > 256:
            next_history = next_history[-256:]
        cache.save_trend_history({"history": next_history})

    return payload


def _canonical_findings_payload(findings, graph_hash, changed_only, scan_result):
    return canonicalize_json_payload(
        {
        "artifact_class": CANONICAL_ARTIFACT_CLASS,
        "schema_id": _CANONICAL_FINDINGS_SCHEMA_ID,
        "schema_version": _CANONICAL_SCHEMA_VERSION,
        "result": scan_result,
        "changed_only": bool(changed_only),
        "graph_hash": graph_hash,
        "finding_count": len(findings),
        "findings": findings,
        }
    )


def _canonical_invariant_map_payload(invariants):
    return canonicalize_json_payload(
        {
        "artifact_class": CANONICAL_ARTIFACT_CLASS,
        "schema_id": _CANONICAL_INVARIANT_MAP_SCHEMA_ID,
        "schema_version": _CANONICAL_SCHEMA_VERSION,
        "invariants": invariants,
        }
    )


def _canonical_promotion_payload(candidates):
    return canonicalize_json_payload(
        {
            "artifact_class": CANONICAL_ARTIFACT_CLASS,
            "schema_id": _CANONICAL_PROMOTION_SCHEMA_ID,
            "schema_version": _CANONICAL_SCHEMA_VERSION,
            "candidate_count": len(candidates),
            "candidates": candidates,
        }
    )


def _run_meta_payload(graph_hash, changed_only, output_format, scan_result, run_meta=None):
    payload = {
        "artifact_class": RUN_META_ARTIFACT_CLASS,
        "status": "DERIVED",
        "last_reviewed": _today_utc(),
        "generated_utc": _now_utc(),
        "result": scan_result,
        "changed_only": bool(changed_only),
        "output_format": output_format,
        "graph_hash": graph_hash,
        "python_version": platform.python_version(),
        "platform": platform.system().lower(),
    }
    if isinstance(run_meta, dict):
        for key in sorted(run_meta.keys()):
            payload[key] = run_meta[key]
    return payload


def _render_findings_md(findings, today):
    lines = [_doc_header(today), "# AuditX Findings", "", "## Summary", ""]
    lines.append("- Total findings: {}".format(len(findings)))
    severity_counts = _severity_counts(findings)
    category_counts = _category_counts(findings)
    lines.append("- Severities: {}".format(", ".join("{}={}".format(k, v) for k, v in severity_counts.items()) or "none"))
    lines.append("- Categories: {}".format(", ".join("{}={}".format(k, v) for k, v in category_counts.items()) or "none"))
    lines.append("")
    lines.append("## Top Findings")
    lines.append("")
    top = findings[: min(len(findings), 100)]
    for finding in top:
        lines.append("- `{}` {} `{}` ({})".format(
            finding.get("finding_id", ""),
            finding.get("severity", ""),
            finding.get("category", ""),
            finding.get("location", {}).get("file", ""),
        ))
        for evidence in finding.get("evidence", [])[:2]:
            lines.append("  - {}".format(evidence))
    lines.append("")
    return "\n".join(lines)


def _render_summary_md(findings, today):
    severity_counts = _severity_counts(findings)
    category_counts = _category_counts(findings)

    lines = [_doc_header(today), "# AuditX Summary", "", "## Counts By Severity", ""]
    if severity_counts:
        for severity, count in severity_counts.items():
            lines.append("- {}: {}".format(severity, count))
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Counts By Category")
    lines.append("")
    if category_counts:
        for category, count in category_counts.items():
            lines.append("- {}: {}".format(category, count))
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def _write_readme_if_missing(output_dir, today):
    readme = os.path.join(output_dir, "README.md")
    if os.path.exists(readme):
        return
    content = _doc_header(today) + (
        "# AuditX Artifacts\n\n"
        "- `FINDINGS.json`: canonical machine-readable findings payload.\n"
        "- `INVARIANT_MAP.json`: canonical invariant mapping payload.\n"
        "- `PROMOTION_CANDIDATES.json`: canonical RepoX-promotion candidate suggestions.\n"
        "- `TRENDS.json`: canonical trend summary derived from canonical findings.\n"
        "- `RUN_META.json`: non-canonical run metadata (timestamps and host info).\n"
        "- `FINDINGS.md`: derived view summary for humans.\n"
        "- `SUMMARY.md`: derived count rollups for humans.\n"
    )
    _write_text(readme, content)


def write_reports(
    repo_root,
    findings,
    graph_hash,
    changed_only,
    output_format,
    scan_result="scan_complete",
    run_meta=None,
    cache=None,
    output_root="",
):
    today = _today_utc()
    output_dir = _ensure_output_dir(repo_root, override=output_root)
    _write_readme_if_missing(output_dir, today)

    invariants = _build_invariant_map(findings)
    promotion_candidates = _build_promotion_candidates(findings)
    trends_payload = _build_trends(findings, cache=cache)
    findings_payload = _canonical_findings_payload(findings, graph_hash, changed_only, scan_result)
    invariant_payload = _canonical_invariant_map_payload(invariants)
    promotion_payload = _canonical_promotion_payload(promotion_candidates)
    run_meta_payload = _run_meta_payload(
        graph_hash=graph_hash,
        changed_only=changed_only,
        output_format=output_format,
        scan_result=scan_result,
        run_meta=run_meta,
    )

    _write_json(os.path.join(output_dir, "FINDINGS.json"), findings_payload)
    _write_json(os.path.join(output_dir, "INVARIANT_MAP.json"), invariant_payload)
    _write_json(os.path.join(output_dir, "PROMOTION_CANDIDATES.json"), promotion_payload)
    _write_json(os.path.join(output_dir, "TRENDS.json"), trends_payload)
    _write_json(os.path.join(output_dir, "RUN_META.json"), run_meta_payload)

    if output_format in ("md", "both"):
        findings_md = _render_findings_md(findings, today)
        summary_md = _render_summary_md(findings, today)
        _write_text(os.path.join(output_dir, "FINDINGS.md"), findings_md)
        _write_text(os.path.join(output_dir, "SUMMARY.md"), summary_md)

    def _rel(path):
        return os.path.relpath(path, repo_root).replace("\\", "/")

    written = [
        _rel(os.path.join(output_dir, "FINDINGS.json")),
        _rel(os.path.join(output_dir, "INVARIANT_MAP.json")),
        _rel(os.path.join(output_dir, "PROMOTION_CANDIDATES.json")),
        _rel(os.path.join(output_dir, "TRENDS.json")),
        _rel(os.path.join(output_dir, "RUN_META.json")),
    ]
    if output_format in ("md", "both"):
        written.extend(
            (
                _rel(os.path.join(output_dir, "FINDINGS.md")),
                _rel(os.path.join(output_dir, "SUMMARY.md")),
            )
        )

    return {
        "artifact_classes": {
            "FINDINGS.json": CANONICAL_ARTIFACT_CLASS,
            "INVARIANT_MAP.json": CANONICAL_ARTIFACT_CLASS,
            "PROMOTION_CANDIDATES.json": CANONICAL_ARTIFACT_CLASS,
            "TRENDS.json": CANONICAL_ARTIFACT_CLASS,
            "RUN_META.json": RUN_META_ARTIFACT_CLASS,
            "FINDINGS.md": DERIVED_VIEW_ARTIFACT_CLASS,
            "SUMMARY.md": DERIVED_VIEW_ARTIFACT_CLASS,
        },
        "output_dir": output_dir.replace("\\", "/"),
        "output_format": output_format,
        "written": written,
    }
