"""FAST Xi-6 TestX helpers."""

from __future__ import annotations

import json
import os

from tools.review.xi6_common import (
    ARCHITECTURE_GRAPH_V1_REL,
    MODULE_BOUNDARY_RULES_V1_REL,
    SINGLE_ENGINE_REGISTRY_REL,
    build_single_engine_findings,
    evaluate_architecture_drift,
    load_architecture_graph_v1,
    load_module_boundary_rules,
    load_single_engine_registry,
    recompute_content_hash,
    recompute_fingerprint,
)


def _load_json(repo_root: str, rel_path: str) -> dict:
    path = os.path.join(os.path.abspath(repo_root), rel_path.replace("/", os.sep))
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError(f"{rel_path} is not a JSON object")
    return payload


def committed_architecture_graph_v1(repo_root: str) -> dict:
    return _load_json(repo_root, ARCHITECTURE_GRAPH_V1_REL)


def committed_module_boundary_rules(repo_root: str) -> dict:
    return _load_json(repo_root, MODULE_BOUNDARY_RULES_V1_REL)


def committed_single_engine_registry(repo_root: str) -> dict:
    return _load_json(repo_root, SINGLE_ENGINE_REGISTRY_REL)


def synthetic_drift_report(repo_root: str) -> dict:
    frozen = load_architecture_graph_v1(repo_root)
    live = dict(frozen)
    for key in ("identity", "contract_id", "stability_class", "content_hash", "deterministic_fingerprint"):
        live.pop(key, None)
    modules = [dict(item or {}) for item in list(live.get("modules") or [])]
    modules.append(
        {
            "confidence": 1.0,
            "dependencies": [],
            "domain": "runtime",
            "file_count": 1,
            "languages": [{"file_count": 1, "language_id": "python"}],
            "module_id": "runtime.synthetic_drift_probe",
            "module_root": "runtime/synthetic_drift_probe",
            "owned_files": ["runtime/synthetic_drift_probe.py"],
            "stability_class": "provisional",
        }
    )
    live["modules"] = modules
    return evaluate_architecture_drift(
        repo_root,
        live_graph=live,
        frozen_graph=frozen,
        update_tag_payload={"required_tags": []},
    )


__all__ = [
    "build_single_engine_findings",
    "committed_architecture_graph_v1",
    "committed_module_boundary_rules",
    "committed_single_engine_registry",
    "evaluate_architecture_drift",
    "load_architecture_graph_v1",
    "load_module_boundary_rules",
    "load_single_engine_registry",
    "recompute_content_hash",
    "recompute_fingerprint",
    "synthetic_drift_report",
]
