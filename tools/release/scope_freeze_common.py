"""Deterministic helpers for the v0.0.0 convergence scope freeze."""

from __future__ import annotations

import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.meta.stability import ALL_REGISTRY_PATHS, registry_entry_rows, validate_all_registries  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


MVP_SCOPE_LOCK_PATH = "docs/release/MVP_SCOPE_LOCK.md"
FROZEN_INVARIANTS_PATH = "docs/release/FROZEN_INVARIANTS_v0_0_0.md"
PROVISIONAL_FEATURE_LIST_PATH = "docs/release/PROVISIONAL_FEATURE_LIST.md"
SEMANTIC_CONTRACT_REGISTRY_PATH = "data/registries/semantic_contract_registry.json"

FROZEN_SEMANTIC_CONTRACT_REGISTRY_HASH = "55bef1f0337c3a311cc5a30c8880715bffbf93d93eb64c24cc2f1d7f86b1df94"
FROZEN_ALLOWED_FUTURE_SERIES = (
    "APPSHELL",
    "APPSHELL-TOOLS",
    "ARCHIVE-POLICY",
    "ASTRO",
    "ASTRO-DOMAIN",
    "CAP-NEG",
    "CAP-NEG/PACK-COMPAT",
    "CAP-NEG/REPLAY",
    "COMPAT/BLUEPRINT",
    "CONCURRENCY",
    "CONTROL/LAW",
    "DIAG",
    "DIST-REFINE/TRUST",
    "DIST-SDK/UPDATE-MODEL",
    "DIST/PLATFORM",
    "DIST/UPDATE-MODEL",
    "DOM",
    "DOMAIN",
    "EARTH",
    "EARTH/MW",
    "EARTH/SOL",
    "GAL+/ASTRO",
    "GEO/MW",
    "GOVERNANCE/COMMERCIAL",
    "GOVERNANCE/RELEASE",
    "INF/TOOLING",
    "LIB",
    "LIB/APPSHELL",
    "LIB/DIST",
    "LIB/PACK-COMPAT",
    "LIB/PROFILE",
    "LIB/SERVER",
    "LIB/UPDATE-MODEL",
    "LOGIC",
    "LOGIC/CAP-NEG",
    "MAT",
    "MAT/DOM",
    "MW",
    "MW/EARTH/SOL",
    "OBSERVABILITY/DIAG",
    "PACK-COMPAT/RELEASE",
    "PLATFORM/DIST",
    "PROC",
    "RELEASE",
    "RELEASE-INDEX/LAB",
    "RELEASE/DIST",
    "RENDER",
    "SAVE/COMPAT",
    "SESSION/COMPAT",
    "SOL",
    "SOL/EARTH",
    "SOL/GAL",
    "SOL/GEO",
    "SOL/LIB",
    "STORE-GC",
    "SYS",
    "TRUST/RELEASE",
    "TRUST/UPDATE-MODEL",
    "UNIVERSAL-ID",
    "UPDATE/TRUST",
    "VALIDATION-GOV",
)
REQUESTED_BUT_UNDECLARED_CONTRACT_IDS = ()
REQUIRED_SCOPE_FREEZE_DOCS = (
    MVP_SCOPE_LOCK_PATH,
    FROZEN_INVARIANTS_PATH,
    PROVISIONAL_FEATURE_LIST_PATH,
)

_LOW_RISK_SERIES = {
    "APPSHELL",
    "DIAG",
    "INF/TOOLING",
    "LIB",
    "LIB/PACK-COMPAT",
    "LIB/SERVER",
}
_HIGH_RISK_SERIES = {
    "ASTRO",
    "ASTRO-DOMAIN",
    "DOM",
    "GAL+/ASTRO",
    "MAT",
    "MAT/DOM",
    "SOL/EARTH",
    "SOL/GAL",
}


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _repo_root(repo_root: str | None = None) -> str:
    return os.path.normpath(os.path.abspath(repo_root or REPO_ROOT_HINT))


def _repo_abs(repo_root: str, rel_path: str) -> str:
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, rel_path.replace("/", os.sep))))


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _read_json(path: str) -> dict:
    import json

    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def semantic_contract_registry_hash(repo_root: str) -> str:
    payload = _read_json(_repo_abs(_repo_root(repo_root), SEMANTIC_CONTRACT_REGISTRY_PATH))
    return canonical_sha256(payload) if payload else ""


def current_semantic_contract_ids(repo_root: str) -> list[str]:
    payload = _read_json(_repo_abs(_repo_root(repo_root), SEMANTIC_CONTRACT_REGISTRY_PATH))
    rows = list(_as_map(payload.get("record")).get("contracts") or [])
    contract_ids = sorted(
        {
            _token(_as_map(row).get("contract_id"))
            for row in rows
            if isinstance(row, Mapping) and _token(_as_map(row).get("contract_id"))
        }
    )
    return contract_ids


def registry_stability_rows(repo_root: str) -> list[dict]:
    root = _repo_root(repo_root)
    rows: list[dict] = []
    for rel_path in ALL_REGISTRY_PATHS:
        entry_report = registry_entry_rows(_repo_abs(root, rel_path))
        for entry in list(entry_report.get("entries") or []):
            entry_row = _as_map(entry)
            row = _as_map(entry_row.get("row"))
            stability = _as_map(row.get("stability"))
            rows.append(
                {
                    "registry_path": rel_path,
                    "family": _token(entry_report.get("family")),
                    "item_id": _token(entry_row.get("item_id")),
                    "entry_path": _token(entry_row.get("path")),
                    "stability_class_id": _token(stability.get("stability_class_id")),
                    "rationale": _token(stability.get("rationale")),
                    "future_series": _token(stability.get("future_series")),
                    "replacement_target": _token(stability.get("replacement_target")),
                    "contract_id": _token(stability.get("contract_id")),
                }
            )
    return sorted(
        rows,
        key=lambda row: (
            _token(row.get("stability_class_id")),
            _token(row.get("future_series")),
            _token(row.get("registry_path")),
            _token(row.get("item_id")),
            _token(row.get("entry_path")),
        ),
    )


def provisional_feature_rows(repo_root: str) -> list[dict]:
    return [row for row in registry_stability_rows(repo_root) if _token(row.get("stability_class_id")) == "provisional"]


def stable_feature_rows(repo_root: str) -> list[dict]:
    return [row for row in registry_stability_rows(repo_root) if _token(row.get("stability_class_id")) == "stable"]


def experimental_feature_rows(repo_root: str) -> list[dict]:
    return [row for row in registry_stability_rows(repo_root) if _token(row.get("stability_class_id")) == "experimental"]


def provisional_future_series(repo_root: str) -> list[str]:
    return sorted({_token(row.get("future_series")) for row in provisional_feature_rows(repo_root) if _token(row.get("future_series"))})


def estimated_refactor_risk(future_series: str) -> str:
    token = _token(future_series)
    if token in _LOW_RISK_SERIES:
        return "low"
    if token in _HIGH_RISK_SERIES:
        return "high"
    return "medium"


def render_provisional_feature_list(repo_root: str) -> str:
    provisional_rows = provisional_feature_rows(repo_root)
    stable_rows = stable_feature_rows(repo_root)
    experimental_rows = experimental_feature_rows(repo_root)
    lines = [
        "Status: CANONICAL",
        "Last Reviewed: 2026-03-13",
        "Supersedes: none",
        "Superseded By: none",
        "Scope: provisional registry entries at the v0.0.0 convergence freeze.",
        "Stability: provisional",
        "Future Series: RELEASE/STABILITY",
        "Replacement Target: stable-contract inventory after authoritative registry promotion completes",
        "",
        "# Provisional Feature List",
        "",
        "This file is generated from current registry stability markers.",
        "It is a release-planning surface only and does not alter runtime behavior.",
        "",
        "## Summary",
        "",
        "- provisional_entry_count: `{}`".format(len(provisional_rows)),
        "- stable_entry_count: `{}`".format(len(stable_rows)),
        "- experimental_entry_count: `{}`".format(len(experimental_rows)),
        "- future_series_count: `{}`".format(len(provisional_future_series(repo_root))),
        "- risk_method: `future_series heuristic`",
        "",
    ]
    current_series = provisional_future_series(repo_root)
    for future_series in current_series:
        series_rows = [row for row in provisional_rows if _token(row.get("future_series")) == future_series]
        lines.extend(
            [
                "## {}".format(future_series),
                "",
                "- entry_count: `{}`".format(len(series_rows)),
                "",
            ]
        )
        for row in series_rows:
            lines.append(
                "- registry_path=`{}` item_id=`{}` stability_class=`provisional` future_series=`{}` risk=`{}` replacement_target=`{}`".format(
                    _token(row.get("registry_path")),
                    _token(row.get("item_id")) or _token(row.get("entry_path")),
                    future_series,
                    estimated_refactor_risk(future_series),
                    _token(row.get("replacement_target")),
                )
            )
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def scope_freeze_violations(repo_root: str) -> list[dict]:
    root = _repo_root(repo_root)
    violations: list[dict] = []
    for rel_path in REQUIRED_SCOPE_FREEZE_DOCS:
        if os.path.isfile(_repo_abs(root, rel_path)):
            continue
        violations.append(
            {
                "code": "missing_scope_freeze_doc",
                "rule_id": "INV-NO-NEW-DOMAIN-SERIES-DURING-CONVERGENCE",
                "file_path": rel_path,
                "message": "required scope-freeze release doc is missing",
            }
        )

    current_hash = semantic_contract_registry_hash(root)
    if current_hash != FROZEN_SEMANTIC_CONTRACT_REGISTRY_HASH:
        violations.append(
            {
                "code": "semantic_contract_registry_hash_drift",
                "rule_id": "INV-NO-SEMANTIC-CONTRACT-CHANGES-POST-FREEZE",
                "file_path": SEMANTIC_CONTRACT_REGISTRY_PATH,
                "message": "semantic contract registry hash differs from the frozen v0.0.0 value",
            }
        )

    extra_series = [series for series in provisional_future_series(root) if series not in set(FROZEN_ALLOWED_FUTURE_SERIES)]
    for series in extra_series:
        violations.append(
            {
                "code": "new_future_series",
                "rule_id": "INV-NO-NEW-DOMAIN-SERIES-DURING-CONVERGENCE",
                "file_path": PROVISIONAL_FEATURE_LIST_PATH,
                "message": "provisional future_series '{}' is outside the frozen convergence allowlist".format(series),
            }
        )

    validation_report = validate_all_registries(root)
    for registry_report in list(validation_report.get("reports") or []):
        report_row = _as_map(registry_report)
        rel_path = _token(report_row.get("file_path"))
        for error in list(report_row.get("errors") or []):
            error_row = _as_map(error)
            code = _token(error_row.get("code"))
            if code in ("provisional_requires_future_series", "provisional_requires_replacement_target"):
                violations.append(
                    {
                        "code": code,
                        "rule_id": "INV-PROVISIONAL-MUST-HAVE-REPLACEMENT-PLAN",
                        "file_path": rel_path,
                        "message": _token(error_row.get("message")) or "provisional entry is missing replacement-plan metadata",
                    }
                )
    return sorted(
        violations,
        key=lambda row: (
            _token(row.get("rule_id")),
            _token(row.get("file_path")),
            _token(row.get("code")),
            _token(row.get("message")),
        ),
    )


__all__ = [
    "FROZEN_ALLOWED_FUTURE_SERIES",
    "FROZEN_INVARIANTS_PATH",
    "FROZEN_SEMANTIC_CONTRACT_REGISTRY_HASH",
    "MVP_SCOPE_LOCK_PATH",
    "PROVISIONAL_FEATURE_LIST_PATH",
    "REQUIRED_SCOPE_FREEZE_DOCS",
    "REQUESTED_BUT_UNDECLARED_CONTRACT_IDS",
    "SEMANTIC_CONTRACT_REGISTRY_PATH",
    "current_semantic_contract_ids",
    "estimated_refactor_risk",
    "experimental_feature_rows",
    "provisional_feature_rows",
    "provisional_future_series",
    "registry_stability_rows",
    "render_provisional_feature_list",
    "scope_freeze_violations",
    "semantic_contract_registry_hash",
    "stable_feature_rows",
]
