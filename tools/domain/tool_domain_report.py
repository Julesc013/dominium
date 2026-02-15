#!/usr/bin/env python3
"""Deterministic reporting for domain foundation registries."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.domain.tool_domain_validate import validate_domain_foundation  # noqa: E402


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return payload, ""


def _write_json(path: str, payload: Dict[str, object]) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _rows(payload: dict, key: str) -> List[dict]:
    raw = payload.get(key)
    if not isinstance(raw, list):
        return []
    return [dict(item) for item in raw if isinstance(item, dict)]


def _domain_rows(payload: dict) -> List[dict]:
    out = []
    for row in _rows(payload, "records"):
        out.append(
            {
                "domain_id": str(row.get("domain_id", "")),
                "status": str(row.get("status", "")),
                "deprecated": bool(row.get("deprecated", False)),
                "scope_tags": sorted(set(str(item).strip() for item in (row.get("scope_tags") or []) if str(item).strip())),
                "solver_kinds_allowed": sorted(
                    set(str(item).strip() for item in (row.get("solver_kinds_allowed") or []) if str(item).strip())
                ),
                "contract_ids": sorted(
                    set(str(item).strip() for item in (row.get("contract_ids") or []) if str(item).strip())
                ),
            }
        )
    return sorted(out, key=lambda item: str(item.get("domain_id", "")))


def _contract_rows(payload: dict) -> List[dict]:
    out = []
    for row in _rows(payload, "records"):
        out.append(
            {
                "contract_id": str(row.get("contract_id", "")),
                "conservation_tags": sorted(
                    set(str(item).strip() for item in (row.get("conservation_tags") or []) if str(item).strip())
                ),
                "violation_refusal_codes": sorted(
                    set(str(item).strip() for item in (row.get("violation_refusal_codes") or []) if str(item).strip())
                ),
            }
        )
    return sorted(out, key=lambda item: str(item.get("contract_id", "")))


def _solver_rows(payload: dict) -> List[dict]:
    out = []
    for row in _rows(payload, "records"):
        out.append(
            {
                "solver_id": str(row.get("solver_id", "")),
                "domain_ids": sorted(set(str(item).strip() for item in (row.get("domain_ids") or []) if str(item).strip())),
                "contract_ids": sorted(set(str(item).strip() for item in (row.get("contract_ids") or []) if str(item).strip())),
                "transition_support": sorted(
                    set(str(item).strip() for item in (row.get("transition_support") or []) if str(item).strip())
                ),
                "resolution_tags": sorted(
                    set(str(item).strip() for item in (row.get("resolution_tags") or []) if str(item).strip())
                ),
            }
        )
    return sorted(out, key=lambda item: str(item.get("solver_id", "")))


def _markdown_report(result: dict, domains: List[dict], contracts: List[dict], solvers: List[dict]) -> str:
    lines: List[str] = []
    lines.append("Status: DERIVED")
    lines.append("Version: 1.0.0")
    lines.append("")
    lines.append("# Domain Foundation Report")
    lines.append("")
    lines.append("## Validation Result")
    lines.append("- result: `{}`".format(str(result.get("result", ""))))
    summary = dict(result.get("summary") or {})
    lines.append("- domains: `{}`".format(int(summary.get("domain_count", 0) or 0)))
    lines.append("- contracts: `{}`".format(int(summary.get("contract_count", 0) or 0)))
    lines.append("- solvers: `{}`".format(int(summary.get("solver_count", 0) or 0)))
    lines.append("")
    lines.append("## Domains")
    for row in domains:
        lines.append(
            "- `{}` status=`{}` deprecated=`{}` scopes=`{}` solver_kinds=`{}` contracts=`{}`".format(
                str(row.get("domain_id", "")),
                str(row.get("status", "")),
                "true" if bool(row.get("deprecated", False)) else "false",
                ",".join(list(row.get("scope_tags") or [])),
                ",".join(list(row.get("solver_kinds_allowed") or [])),
                ",".join(list(row.get("contract_ids") or [])),
            )
        )
    lines.append("")
    lines.append("## Contracts")
    for row in contracts:
        lines.append(
            "- `{}` tags=`{}` refusals=`{}`".format(
                str(row.get("contract_id", "")),
                ",".join(list(row.get("conservation_tags") or [])),
                ",".join(list(row.get("violation_refusal_codes") or [])),
            )
        )
    lines.append("")
    lines.append("## Solver Bindings")
    for row in solvers:
        lines.append(
            "- `{}` domains=`{}` contracts=`{}` transitions=`{}` resolution_tags=`{}`".format(
                str(row.get("solver_id", "")),
                ",".join(list(row.get("domain_ids") or [])),
                ",".join(list(row.get("contract_ids") or [])),
                ",".join(list(row.get("transition_support") or [])),
                ",".join(list(row.get("resolution_tags") or [])),
            )
        )
    errors = list(result.get("errors") or [])
    lines.append("")
    lines.append("## Errors")
    if not errors:
        lines.append("- none")
    else:
        for row in errors:
            lines.append(
                "- `{}` path=`{}` message=`{}`".format(
                    str(row.get("code", "")),
                    str(row.get("path", "")),
                    str(row.get("message", "")),
                )
            )
    lines.append("")
    lines.append("## Cross-References")
    lines.append("- `docs/scale/DOMAIN_MODEL.md`")
    lines.append("- `docs/scale/CONTRACTS_AND_CONSERVATION.md`")
    lines.append("- `docs/scale/SOLVER_DOMAIN_BINDINGS.md`")
    return "\n".join(lines) + "\n"


def build_domain_report(
    repo_root: str,
    out_json_rel: str = "docs/audit/DOMAIN_REGISTRY_REPORT.json",
    out_md_rel: str = "docs/audit/DOMAIN_REGISTRY_REPORT.md",
) -> Dict[str, object]:
    result = validate_domain_foundation(repo_root=repo_root)
    domain_payload, _ = _read_json(os.path.join(repo_root, "data", "registries", "domain_registry.json"))
    contract_payload, _ = _read_json(os.path.join(repo_root, "data", "registries", "domain_contract_registry.json"))
    solver_payload, _ = _read_json(os.path.join(repo_root, "data", "registries", "solver_registry.json"))

    domain_rows = _domain_rows(domain_payload)
    contract_rows = _contract_rows(contract_payload)
    solver_rows = _solver_rows(solver_payload)

    report_payload = {
        "schema_version": "1.0.0",
        "result": str(result.get("result", "")),
        "summary": dict(result.get("summary") or {}),
        "domains": domain_rows,
        "contracts": contract_rows,
        "solver_bindings": solver_rows,
        "errors": list(result.get("errors") or []),
    }

    out_json_abs = os.path.join(repo_root, out_json_rel.replace("/", os.sep))
    out_md_abs = os.path.join(repo_root, out_md_rel.replace("/", os.sep))
    _write_json(out_json_abs, report_payload)
    md = _markdown_report(result=result, domains=domain_rows, contracts=contract_rows, solvers=solver_rows)
    parent = os.path.dirname(out_md_abs)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(out_md_abs, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(md)

    return {
        "result": str(result.get("result", "")),
        "json_report_path": _norm(out_json_rel),
        "markdown_report_path": _norm(out_md_rel),
        "summary": dict(result.get("summary") or {}),
        "errors": list(result.get("errors") or []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic domain foundation audit reports.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--out-json", default="docs/audit/DOMAIN_REGISTRY_REPORT.json")
    parser.add_argument("--out-md", default="docs/audit/DOMAIN_REGISTRY_REPORT.md")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(args.repo_root)) if str(args.repo_root).strip() else REPO_ROOT_HINT
    report = build_domain_report(
        repo_root=repo_root,
        out_json_rel=str(args.out_json),
        out_md_rel=str(args.out_md),
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")) == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
