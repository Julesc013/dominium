#!/usr/bin/env python3
"""Generate META-GENRE-0 demand coverage gap report from canonical matrix data."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from typing import Dict, Iterable, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


MATRIX_REL = "data/meta/player_demand_matrix.json"
OUTPUT_REL = "docs/audit/PLAYER_DEMAND_GAPS.md"


def _load_json(repo_root: str, rel_path: str) -> Tuple[dict, str]:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {}, str(exc)
    if not isinstance(payload, dict):
        return {}, "json root must be object"
    return payload, ""


def _ids(rows: Iterable[dict], key: str) -> set[str]:
    out = set()
    for row in rows:
        token = str(dict(row).get(key, "")).strip()
        if token:
            out.add(token)
    return out


def _known_refs(repo_root: str) -> Dict[str, set[str]]:
    action_family_payload, _ = _load_json(repo_root, "data/registries/action_family_registry.json")
    action_template_payload, _ = _load_json(repo_root, "data/registries/action_template_registry.json")
    explain_payload, _ = _load_json(repo_root, "data/registries/explain_contract_registry.json")
    law_payload, _ = _load_json(repo_root, "data/registries/law_profiles.json")
    phys_payload, _ = _load_json(repo_root, "data/registries/physics_profile_registry.json")
    rwam_payload, _ = _load_json(repo_root, "data/meta/real_world_affordance_matrix.json")

    return {
        "action_families": _ids(list((dict(action_family_payload.get("record") or {})).get("families") or []), "action_family_id"),
        "action_templates": _ids(list((dict(action_template_payload.get("record") or {})).get("templates") or []), "action_template_id"),
        "explain_contracts": _ids(list((dict(explain_payload.get("record") or {})).get("explain_contracts") or []), "contract_id"),
        "law_profiles": _ids(list((dict(law_payload.get("record") or {})).get("profiles") or []), "law_profile_id"),
        "physics_profiles": _ids(list((dict(phys_payload.get("record") or {})).get("physics_profiles") or []), "physics_profile_id"),
        "rwam_affordances": _ids(list((rwam_payload if isinstance(rwam_payload, dict) else {}).get("affordances") or []), "id"),
    }


def _valid_or_tbd(token: str, known: set[str], next_series: str) -> bool:
    value = str(token or "").strip()
    if not value:
        return False
    if value in known:
        return True
    if value.startswith("TBD:") and str(next_series or "").strip():
        return True
    return False


def generate_gap_report(repo_root: str) -> dict:
    payload, err = _load_json(repo_root, MATRIX_REL)
    if err:
        return {
            "result": "refusal",
            "reason_code": "refusal.meta_genre.matrix_missing",
            "message": err,
        }
    demands = list(payload.get("demands") or [])
    if not demands:
        return {
            "result": "refusal",
            "reason_code": "refusal.meta_genre.matrix_empty",
            "message": "matrix demands list is empty",
        }

    known = _known_refs(repo_root)
    coverage = Counter()
    cluster_counts = Counter()
    next_series_counts = Counter()
    unresolved_by_demand = defaultdict(list)

    for row in demands:
        if not isinstance(row, dict):
            continue
        demand_id = str(row.get("demand_id", "")).strip() or "<unknown>"
        coverage_status = str(row.get("coverage_status", "")).strip() or "unknown"
        coverage[coverage_status] += 1
        next_series = str(row.get("next_series", "")).strip()
        if coverage_status in {"partial", "planned", "unknown"} and next_series:
            next_series_counts[next_series] += 1
        for cluster_id in list(row.get("clusters") or []):
            cluster_token = str(cluster_id).strip()
            if cluster_token:
                cluster_counts[cluster_token] += 1

        for token in list(row.get("action_families") or []):
            if not _valid_or_tbd(token, known["action_families"], next_series):
                unresolved_by_demand[demand_id].append("action_family:{}".format(token))
        for token in list(row.get("action_templates") or []):
            if not _valid_or_tbd(token, known["action_templates"], next_series):
                unresolved_by_demand[demand_id].append("action_template:{}".format(token))
        for token in list(row.get("explain") or []):
            if not _valid_or_tbd(token, known["explain_contracts"], next_series):
                unresolved_by_demand[demand_id].append("explain:{}".format(token))
        for token in list(row.get("rwam_affordances") or []):
            if not _valid_or_tbd(token, known["rwam_affordances"], next_series):
                unresolved_by_demand[demand_id].append("rwam:{}".format(token))
        for token in list((dict(row.get("break_rules") or {})).get("profiles") or []):
            if (
                not _valid_or_tbd(token, known["law_profiles"], next_series)
                and not _valid_or_tbd(token, known["physics_profiles"], next_series)
            ):
                unresolved_by_demand[demand_id].append("profile:{}".format(token))

    partial_like = sorted(
        str(row.get("demand_id", "")).strip()
        for row in demands
        if isinstance(row, dict)
        and str(row.get("coverage_status", "")).strip() in {"partial", "planned", "unknown"}
    )

    unresolved = {
        demand_id: sorted(set(tokens))
        for demand_id, tokens in sorted(unresolved_by_demand.items())
    }
    report = {
        "result": "complete",
        "matrix_version": str(payload.get("version", "")),
        "demand_count": len([row for row in demands if isinstance(row, dict)]),
        "coverage_histogram": dict(sorted(coverage.items())),
        "cluster_counts": dict(sorted(cluster_counts.items())),
        "partial_planned_unknown_demands": partial_like,
        "next_series_histogram": dict(sorted(next_series_counts.items())),
        "unresolved_references": unresolved,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(
        dict(report, deterministic_fingerprint="")
    )
    return report


def write_gap_markdown(repo_root: str, report: dict, out_rel: str = OUTPUT_REL) -> str:
    out_abs = os.path.join(repo_root, out_rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(out_abs), exist_ok=True)

    lines = []
    lines.append("# Player Demand Gaps")
    lines.append("")
    lines.append("Status: GENERATED")
    lines.append("")
    lines.append("- matrix_version: `{}`".format(str(report.get("matrix_version", ""))))
    lines.append("- demand_count: `{}`".format(int(report.get("demand_count", 0) or 0)))
    lines.append("- deterministic_fingerprint: `{}`".format(str(report.get("deterministic_fingerprint", ""))))
    lines.append("")

    lines.append("## Coverage Histogram")
    lines.append("")
    for key, value in sorted(dict(report.get("coverage_histogram") or {}).items()):
        lines.append("- {}: {}".format(key, int(value)))
    lines.append("")

    lines.append("## Cluster Counts")
    lines.append("")
    for key, value in sorted(dict(report.get("cluster_counts") or {}).items()):
        lines.append("- {}: {}".format(key, int(value)))
    lines.append("")

    lines.append("## Partial / Planned / Unknown Demands")
    lines.append("")
    partial_rows = list(report.get("partial_planned_unknown_demands") or [])
    if not partial_rows:
        lines.append("- none")
    else:
        for demand_id in partial_rows:
            lines.append("- {}".format(str(demand_id)))
    lines.append("")

    lines.append("## Missing Registry/Contract Links")
    lines.append("")
    unresolved = dict(report.get("unresolved_references") or {})
    if not unresolved:
        lines.append("- none")
    else:
        for demand_id in sorted(unresolved):
            lines.append("- {}: {}".format(demand_id, ", ".join(unresolved[demand_id])))
    lines.append("")

    lines.append("## Recommended Next Series")
    lines.append("")
    next_series = dict(report.get("next_series_histogram") or {})
    if not next_series:
        lines.append("- none")
    else:
        for series_id, value in sorted(next_series.items(), key=lambda item: (-int(item[1]), item[0])):
            lines.append("- {} ({})".format(series_id, int(value)))
    lines.append("")

    open(out_abs, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return out_abs


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate META-GENRE demand gap report.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--out", default=OUTPUT_REL, help="output markdown path relative to repo root")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root)))
    report = generate_gap_report(repo_root=repo_root)
    if str(report.get("result", "")).strip() != "complete":
        print(json.dumps(report, indent=2, sort_keys=True))
        return 2
    out_abs = write_gap_markdown(repo_root=repo_root, report=report, out_rel=str(args.out))
    print(
        json.dumps(
            {
                "result": "complete",
                "out_path": os.path.relpath(out_abs, repo_root).replace("\\", "/"),
                "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
