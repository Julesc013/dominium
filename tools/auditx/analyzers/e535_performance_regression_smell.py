"""E535 performance regression smell analyzer for PERFORMANCE-ENVELOPE-0."""

from __future__ import annotations

import json
import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.perf.performance_envelope_common import DEFAULT_PLATFORM_TAG, REPORT_JSON_REL


ANALYZER_ID = "E535_PERFORMANCE_REGRESSION_SMELL"
THRESHOLD_RATIO = 1.10
MB = 1024 * 1024
KB = 1024


def _report_path(repo_root: str) -> str:
    return os.path.join(
        os.path.abspath(repo_root),
        REPORT_JSON_REL.format(DEFAULT_PLATFORM_TAG).replace("/", os.sep),
    )


def _load_report(repo_root: str) -> dict:
    path = _report_path(repo_root)
    if not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return dict(payload or {}) if isinstance(payload, dict) else {}


def _metric_rows(report: dict) -> list[dict]:
    startup = dict(report.get("startup") or {})
    memory = dict(report.get("memory") or {})
    storage = dict(report.get("storage") or {})
    graph = dict(report.get("graph") or {})
    targets = dict(report.get("declared_targets") or {})
    return [
        {
            "metric_id": "setup_startup_seconds",
            "actual_value": int(dict(startup.get("setup") or {}).get("elapsed_ms", 0) or 0),
            "allowed_value": int(float(targets.get("setup_startup_seconds", 0.0) or 0.0) * 1000.0),
            "unit": "ms",
        },
        {
            "metric_id": "client_startup_seconds",
            "actual_value": int(dict(startup.get("client") or {}).get("elapsed_ms", 0) or 0),
            "allowed_value": int(float(targets.get("client_startup_seconds", 0.0) or 0.0) * 1000.0),
            "unit": "ms",
        },
        {
            "metric_id": "server_startup_seconds",
            "actual_value": int(dict(startup.get("server") or {}).get("elapsed_ms", 0) or 0),
            "allowed_value": int(float(targets.get("server_startup_seconds", 0.0) or 0.0) * 1000.0),
            "unit": "ms",
        },
        {
            "metric_id": "clean_room_seconds",
            "actual_value": int(dict(startup.get("clean_room") or {}).get("elapsed_ms", 0) or 0),
            "allowed_value": int(float(targets.get("clean_room_seconds", 0.0) or 0.0) * 1000.0),
            "unit": "ms",
        },
        {
            "metric_id": "client_memory_mb",
            "actual_value": int(dict(memory.get("client") or {}).get("peak_working_set_bytes", 0) or 0),
            "allowed_value": int(float(targets.get("client_memory_mb", 0) or 0.0) * MB),
            "unit": "bytes",
        },
        {
            "metric_id": "server_memory_mb",
            "actual_value": int(dict(memory.get("server") or {}).get("peak_working_set_bytes", 0) or 0),
            "allowed_value": int(float(targets.get("server_memory_mb", 0) or 0.0) * MB),
            "unit": "bytes",
        },
        {
            "metric_id": "portable_full_bundle_mb",
            "actual_value": int(storage.get("portable_full_bundle_bytes", 0) or 0),
            "allowed_value": int(float(targets.get("portable_full_bundle_mb", 0) or 0.0) * MB),
            "unit": "bytes",
        },
        {
            "metric_id": "minimal_server_profile_mb",
            "actual_value": int(storage.get("minimal_server_bundle_bytes", 0) or 0),
            "allowed_value": int(float(targets.get("minimal_server_profile_mb", 0) or 0.0) * MB),
            "unit": "bytes",
        },
        {
            "metric_id": "base_pack_bundle_mb",
            "actual_value": int(storage.get("base_pack_bundle_bytes", 0) or 0),
            "allowed_value": int(float(targets.get("base_pack_bundle_mb", 0) or 0.0) * MB),
            "unit": "bytes",
        },
        {
            "metric_id": "full_component_count",
            "actual_value": int(graph.get("install_profile_full_component_count", 0) or 0),
            "allowed_value": int(targets.get("full_component_count", 0) or 0),
            "unit": "count",
        },
        {
            "metric_id": "pack_lock_kb",
            "actual_value": int(storage.get("default_pack_lock_bytes", 0) or 0),
            "allowed_value": int(float(targets.get("pack_lock_kb", 0) or 0.0) * KB),
            "unit": "bytes",
        },
        {
            "metric_id": "store_lookup_latency_ms",
            "actual_value": int(dict(storage.get("store_hash_lookup_latency") or {}).get("elapsed_ms", 0) or 0),
            "allowed_value": int(targets.get("store_lookup_latency_ms", 0) or 0),
            "unit": "ms",
        },
    ]


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    report = _load_report(repo_root)
    if not report or str(report.get("result", "")).strip() != "complete":
        return []
    findings = []
    rel_path = REPORT_JSON_REL.format(DEFAULT_PLATFORM_TAG).replace("\\", "/")
    for row in _metric_rows(report):
        actual_value = int(row.get("actual_value", 0) or 0)
        allowed_value = int(row.get("allowed_value", 0) or 0)
        if allowed_value <= 0:
            continue
        if actual_value <= int(allowed_value * THRESHOLD_RATIO):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="performance.performance_regression_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                evidence=[
                    str(row.get("metric_id", "")).strip(),
                    "actual={}{} allowed={}{}".format(
                        actual_value,
                        "" if str(row.get("unit", "")).strip() == "count" else " " + str(row.get("unit", "")).strip(),
                        allowed_value,
                        "" if str(row.get("unit", "")).strip() == "count" else " " + str(row.get("unit", "")).strip(),
                    ),
                ],
                suggested_classification="TODO-RISK",
                recommended_action="RERUN_PERF_BASELINE_AND_REVIEW_STARTUP_MEMORY_STORAGE_GUARDRAILS_FOR_THE_DECLARED_TARGET",
                related_invariants=["INV-PERFORMANCE-BASELINE-RECORDED", "INV-STARTUP-MEASURED-IN-CI"],
                related_paths=[
                    rel_path,
                    "docs/performance/PERFORMANCE_ENVELOPE_v0_0_0_mock.md",
                    "docs/audit/PERFORMANCE_ENVELOPE_BASELINE.md",
                ],
            )
        )
    return findings
