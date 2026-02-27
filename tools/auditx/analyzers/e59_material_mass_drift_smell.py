"""E59 material mass drift smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E59_MATERIAL_MASS_DRIFT_SMELL"
CONSERVATION_CONTRACT_SET_PATH = "data/registries/conservation_contract_set_registry.json"
LEDGER_ENGINE_PATH = "src/reality/ledger/ledger_engine.py"


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


def _quantity_modes_by_contract_set(contract_sets: object) -> dict:
    out = {}
    if not isinstance(contract_sets, list):
        return out
    for row in sorted((item for item in contract_sets if isinstance(item, dict)), key=lambda item: str(item.get("contract_set_id", ""))):
        contract_set_id = str(row.get("contract_set_id", "")).strip()
        if not contract_set_id:
            continue
        quantity_modes = {}
        for quantity_row in sorted(
            (item for item in list(row.get("quantities") or []) if isinstance(item, dict)),
            key=lambda item: str(item.get("quantity_id", "")),
        ):
            quantity_id = str(quantity_row.get("quantity_id", "")).strip()
            mode = str(quantity_row.get("mode", "")).strip()
            if quantity_id:
                quantity_modes[quantity_id] = mode
        out[contract_set_id] = quantity_modes
    return out


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    conservation_payload = _read_json(repo_root, CONSERVATION_CONTRACT_SET_PATH)
    contract_sets = list(((conservation_payload.get("record") or {}).get("contract_sets") or []))
    quantity_modes_by_set = _quantity_modes_by_contract_set(contract_sets)

    if not quantity_modes_by_set:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.material_mass_drift_smell",
                severity="RISK",
                confidence=0.86,
                file_path=CONSERVATION_CONTRACT_SET_PATH,
                line=1,
                evidence=["conservation contract sets are missing or invalid"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_RULE",
                related_invariants=["INV-COMPOSITION-VALIDATED"],
                related_paths=[CONSERVATION_CONTRACT_SET_PATH],
            )
        )
    else:
        for contract_set_id in sorted(quantity_modes_by_set.keys()):
            mode = str((quantity_modes_by_set.get(contract_set_id) or {}).get("quantity.mass", "")).strip()
            if mode:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.material_mass_drift_smell",
                    severity="VIOLATION",
                    confidence=0.96,
                    file_path=CONSERVATION_CONTRACT_SET_PATH,
                    line=1,
                    evidence=[
                        "contract set does not declare quantity.mass conservation channel",
                        "contract_set_id={}".format(contract_set_id),
                    ],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-COMPOSITION-VALIDATED"],
                    related_paths=[CONSERVATION_CONTRACT_SET_PATH],
                )
            )

    ledger_text = _read_text(repo_root, LEDGER_ENGINE_PATH)
    for token in ("pending_material_mass_deltas", "material_mass_totals", "quantity.mass"):
        if token in ledger_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.material_mass_drift_smell",
                severity="RISK",
                confidence=0.82,
                file_path=LEDGER_ENGINE_PATH,
                line=1,
                evidence=["ledger engine missing material mass tracking token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_RULE",
                related_invariants=["INV-COMPOSITION-VALIDATED"],
                related_paths=[LEDGER_ENGINE_PATH],
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
