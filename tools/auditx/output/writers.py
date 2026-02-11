"""AuditX deterministic report writers."""

import json
import os
import platform
from datetime import datetime, timezone


CANONICAL_ARTIFACT_CLASS = "CANONICAL"
DERIVED_VIEW_ARTIFACT_CLASS = "DERIVED_VIEW"
RUN_META_ARTIFACT_CLASS = "RUN_META"

_CANONICAL_FINDINGS_SCHEMA_ID = "dominium.auditx.findings"
_CANONICAL_INVARIANT_MAP_SCHEMA_ID = "dominium.auditx.invariant_map"
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


def _output_root(repo_root):
    return os.path.join(repo_root, "docs", "audit", "auditx")


def _ensure_output_dir(repo_root):
    root = _output_root(repo_root)
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


def _canonical_findings_payload(findings, graph_hash, changed_only, scan_result):
    return {
        "artifact_class": CANONICAL_ARTIFACT_CLASS,
        "schema_id": _CANONICAL_FINDINGS_SCHEMA_ID,
        "schema_version": _CANONICAL_SCHEMA_VERSION,
        "result": scan_result,
        "changed_only": bool(changed_only),
        "graph_hash": graph_hash,
        "finding_count": len(findings),
        "findings": findings,
    }


def _canonical_invariant_map_payload(invariants):
    return {
        "artifact_class": CANONICAL_ARTIFACT_CLASS,
        "schema_id": _CANONICAL_INVARIANT_MAP_SCHEMA_ID,
        "schema_version": _CANONICAL_SCHEMA_VERSION,
        "invariants": invariants,
    }


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
):
    today = _today_utc()
    output_dir = _ensure_output_dir(repo_root)
    _write_readme_if_missing(output_dir, today)

    invariants = _build_invariant_map(findings)
    findings_payload = _canonical_findings_payload(findings, graph_hash, changed_only, scan_result)
    invariant_payload = _canonical_invariant_map_payload(invariants)
    run_meta_payload = _run_meta_payload(
        graph_hash=graph_hash,
        changed_only=changed_only,
        output_format=output_format,
        scan_result=scan_result,
        run_meta=run_meta,
    )

    _write_json(os.path.join(output_dir, "FINDINGS.json"), findings_payload)
    _write_json(os.path.join(output_dir, "INVARIANT_MAP.json"), invariant_payload)
    _write_json(os.path.join(output_dir, "RUN_META.json"), run_meta_payload)

    if output_format in ("md", "both"):
        findings_md = _render_findings_md(findings, today)
        summary_md = _render_summary_md(findings, today)
        _write_text(os.path.join(output_dir, "FINDINGS.md"), findings_md)
        _write_text(os.path.join(output_dir, "SUMMARY.md"), summary_md)

    written = [
        "docs/audit/auditx/FINDINGS.json",
        "docs/audit/auditx/INVARIANT_MAP.json",
        "docs/audit/auditx/RUN_META.json",
    ]
    if output_format in ("md", "both"):
        written.extend(
            (
                "docs/audit/auditx/FINDINGS.md",
                "docs/audit/auditx/SUMMARY.md",
            )
        )

    return {
        "artifact_classes": {
            "FINDINGS.json": CANONICAL_ARTIFACT_CLASS,
            "INVARIANT_MAP.json": CANONICAL_ARTIFACT_CLASS,
            "RUN_META.json": RUN_META_ARTIFACT_CLASS,
            "FINDINGS.md": DERIVED_VIEW_ARTIFACT_CLASS,
            "SUMMARY.md": DERIVED_VIEW_ARTIFACT_CLASS,
        },
        "output_dir": output_dir.replace("\\", "/"),
        "output_format": output_format,
        "written": written,
    }
