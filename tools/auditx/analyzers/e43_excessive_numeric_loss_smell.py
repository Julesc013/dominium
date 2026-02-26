"""E43 excessive numeric loss smell analyzer (warn-only)."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E43_EXCESSIVE_NUMERIC_LOSS_SMELL"
CONTRACT_REGISTRY_PATH = "data/registries/conservation_contract_set_registry.json"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    payload = _read_json(repo_root, CONTRACT_REGISTRY_PATH)
    contract_sets = list(((payload.get("record") or {}).get("contract_sets") or []))
    if not contract_sets:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="reality.excessive_numeric_loss_smell",
                severity="WARN",
                confidence=0.76,
                file_path=CONTRACT_REGISTRY_PATH,
                line=1,
                evidence=["conservation contract set registry is missing or empty"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-CONSERVATION-CONTRACT-SET-REQUIRED"],
                related_paths=[CONTRACT_REGISTRY_PATH],
            )
        )
    for contract_row in sorted((row for row in contract_sets if isinstance(row, dict)), key=lambda row: str(row.get("contract_set_id", ""))):
        contract_set_id = str(contract_row.get("contract_set_id", "")).strip()
        for quantity_row in sorted((row for row in list(contract_row.get("quantities") or []) if isinstance(row, dict)), key=lambda row: str(row.get("quantity_id", ""))):
            mode = str(quantity_row.get("mode", "")).strip()
            quantity_id = str(quantity_row.get("quantity_id", "")).strip()
            tolerance = int(quantity_row.get("tolerance", 0) or 0)
            if mode == "enforce_strict" and tolerance > 0:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="reality.excessive_numeric_loss_smell",
                        severity="WARN",
                        confidence=0.83,
                        file_path=CONTRACT_REGISTRY_PATH,
                        line=1,
                        evidence=[
                            "strict conservation tolerance > 0 may hide cumulative drift",
                            "contract_set_id={},quantity_id={},tolerance={}".format(contract_set_id, quantity_id, tolerance),
                        ],
                        suggested_classification="NEEDS_REVIEW",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-NO-SILENT-VIOLATIONS"],
                        related_paths=[CONTRACT_REGISTRY_PATH],
                    )
                )

    runtime_text = _read_text(repo_root, PROCESS_RUNTIME_PATH)
    if "_ledger_emit_exception(" not in runtime_text or "exception.numeric_error_budget" not in runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="reality.excessive_numeric_loss_smell",
                severity="WARN",
                confidence=0.8,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=[
                    "numeric loss path missing explicit numeric_error_budget accounting hook",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-SILENT-VIOLATIONS"],
                related_paths=[PROCESS_RUNTIME_PATH],
            )
        )

    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )
