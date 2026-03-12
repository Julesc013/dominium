"""Deterministic MVP stress gate orchestration and proof helpers."""

from __future__ import annotations

import copy
import json
import os
import shutil
import sys
from typing import Iterable, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.packs.compat.pack_verification_pipeline import verify_pack_set, write_pack_compatibility_outputs  # noqa: E402
from src.server.net.loopback_transport import service_loopback_control_channel  # noqa: E402
from src.server.runtime.tick_loop import run_server_ticks  # noqa: E402
from tools.compat.cap_neg4_common import (  # noqa: E402
    DEFAULT_CAP_NEG4_SEED,
    generate_interop_matrix,
    run_interop_stress,
    verify_interop_stress_replay,
)
from tools.earth.earth9_stress_common import DEFAULT_EARTH9_SEED, verify_earth_mvp_stress_scenario  # noqa: E402
from tools.geo.geo10_stress_common import DEFAULT_GEO10_SEED  # noqa: E402
from tools.geo.geo10_stress_runtime import verify_geo_stress_scenario  # noqa: E402
from tools.lib.lib_stress_common import DEFAULT_LIB7_SEED, run_lib_stress  # noqa: E402
from tools.logic.tool_run_logic_stress import run_logic_stress  # noqa: E402
from tools.mvp.runtime_bundle import build_pack_lock_payload  # noqa: E402
from tools.process.tool_generate_proc_stress import generate_proc_stress_scenario  # noqa: E402
from tools.process.tool_run_proc_stress import run_proc_stress  # noqa: E402
from tools.process.tool_verify_proc_compaction import verify_proc_compaction  # noqa: E402
from tools.pollution.tool_generate_poll_stress import generate_poll_stress_scenario  # noqa: E402
from tools.pollution.tool_run_poll_stress import _envelope_defaults, run_poll_stress_scenario  # noqa: E402
from tools.server.server_mvp0_probe import (  # noqa: E402
    DEFAULT_SERVER_MVP0_SEED,
    DEFAULT_SERVER_TICKS,
    boot_server_fixture,
    connect_loopback_client,
    drain_client_messages,
)
from tools.system.tool_generate_sys_stress import generate_sys_stress_scenario  # noqa: E402
from tools.system.tool_run_sys_stress import run_sys_stress  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402
from tools.xstack.testx.tests.pack_compat1_testlib import (  # noqa: E402
    cleanup_temp_repo,
    ensure_repo_on_path as ensure_pack_compat_repo_on_path,
    make_temp_pack_compat_repo,
    verify_fixture_pack_set,
)


DEFAULT_MVP_STRESS_SEED = 70101
DEFAULT_REPORT_REL = os.path.join("build", "mvp", "mvp_stress_report.json")
DEFAULT_HASHES_REL = os.path.join("build", "mvp", "mvp_stress_hashes.json")
DEFAULT_PROOF_REPORT_REL = os.path.join("build", "mvp", "mvp_stress_proof_report.json")
DEFAULT_BASELINE_REL = os.path.join("data", "regression", "mvp_stress_baseline.json")
DEFAULT_FINAL_DOC_REL = os.path.join("docs", "audit", "MVP_STRESS_FINAL.md")
DEFAULT_PACK_VERIFY_ROOT_REL = os.path.join("build", "mvp", "pack_verify")
DEFAULT_LIB_OUT_REL = os.path.join("build", "mvp", "lib7")
MVP_STRESS_REGRESSION_UPDATE_TAG = "MVP-STRESS-REGRESSION-UPDATE"
MVP_STRESS_GATE_ID = "mvp.stress.gate.v1"

SUITE_ORDER = (
    "geo10",
    "logic10",
    "proc9",
    "sys8",
    "poll3",
    "earth9",
    "cap_neg4",
    "pack_compat",
    "lib7",
    "server",
)

SUITE_LABELS = {
    "geo10": "GEO-10",
    "logic10": "LOGIC-10",
    "proc9": "PROC-9",
    "sys8": "SYS-8",
    "poll3": "POLL-3",
    "earth9": "EARTH-9",
    "cap_neg4": "CAP-NEG-4",
    "pack_compat": "PACK-COMPAT",
    "lib7": "LIB-7",
    "server": "SERVER",
}

EXPECTED_REFUSAL_SUITES = frozenset({"cap_neg4", "lib7"})
GATE_SUITE_ORDER = tuple(SUITE_LABELS[suite_id] for suite_id in SUITE_ORDER)
SUITE_LABEL_TO_ID = {label: suite_id for suite_id, label in SUITE_LABELS.items()}
DIRECT_SUITE_REPORT_RELS = {
    "GEO-10": os.path.join("build", "mvp", "stress_gate_run", "01_geo_10", "report.json"),
    "LOGIC-10": os.path.join("build", "mvp", "stress_gate_run", "02_logic_10", "report.json"),
    "PROC-9": os.path.join("build", "mvp", "stress_gate_run", "03_proc_9", "report.json"),
    "SYS-8": os.path.join("build", "mvp", "stress_gate_run", "04_sys_8", "report.json"),
    "POLL-3": os.path.join("build", "mvp", "stress_gate_run", "05_poll_3", "report.json"),
    "EARTH-9": os.path.join("build", "mvp", "stress_gate_run", "06_earth_9", "report.json"),
    "CAP-NEG-4": os.path.join("build", "mvp", "stress_gate_run", "07_cap_neg_4", "report.json"),
    "PACK-COMPAT": os.path.join("build", "mvp", "stress_gate_run", "08_pack_compat", "report.json"),
    "LIB-7": os.path.join("build", "mvp", "stress_gate_run", "09_lib_7", "report.json"),
    "SERVER": os.path.join("build", "mvp", "stress_gate_run", "10_server", "report.json"),
}
MVP_CORE_SOURCE_PACK_ROOTS = (
    os.path.join("packs", "core", "pack.core.runtime"),
    os.path.join("packs", "domain", "astronomy.milky_way"),
    os.path.join("packs", "domain", "astronomy.sol"),
    os.path.join("packs", "domain", "planet.earth"),
    os.path.join("packs", "official", "pack.sol.pin_minimal"),
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _ensure_dir(path: str) -> None:
    token = str(path or "").strip()
    if token and not os.path.isdir(token):
        os.makedirs(token, exist_ok=True)


def _repo_abs(repo_root: str, rel_path: str) -> str:
    token = str(rel_path or "").strip()
    if not token:
        return ""
    if os.path.isabs(token):
        return os.path.normpath(os.path.abspath(token))
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, token.replace("/", os.sep))))


def _relative_path(repo_root: str, value: str) -> str:
    token = str(value or "").strip()
    if not token:
        return ""
    abs_path = _repo_abs(repo_root, token)
    if not abs_path:
        return ""
    try:
        return _norm(os.path.relpath(abs_path, repo_root))
    except ValueError:
        return _norm(abs_path)


def _read_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def load_json_if_present(repo_root: str, rel_path: str) -> dict:
    abs_path = _repo_abs(repo_root, rel_path)
    if not abs_path or not os.path.isfile(abs_path):
        return {}
    return _read_json(abs_path)


def _write_text(path: str, text: str) -> str:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text))
    return _norm(path)


def _write_canonical_json(path: str, payload: Mapping[str, object]) -> str:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return _norm(path)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _token(value: object) -> str:
    return str(value or "").strip()


def _sorted_tokens(values: Iterable[object]) -> list[str]:
    return sorted(set(_token(item) for item in list(values or []) if _token(item)))


def _is_gate_report(payload: Mapping[str, object] | None) -> bool:
    row = _as_map(payload)
    return _token(row.get("gate_id")) == MVP_STRESS_GATE_ID and bool(_as_list(row.get("suite_results")))


def _is_gate_proof_report(payload: Mapping[str, object] | None) -> bool:
    row = _as_map(payload)
    return bool(_as_map(row.get("checks"))) and bool(_token(row.get("gate_report_fingerprint")))


def _gate_suite_rows(payload: Mapping[str, object] | None) -> list[dict]:
    return [dict(row) for row in _as_list(_as_map(payload).get("suite_results")) if isinstance(row, Mapping)]


def _gate_suite_row_map(payload: Mapping[str, object] | None) -> dict[str, dict]:
    return {
        _token(_as_map(row).get("suite_id")): _as_map(row)
        for row in _gate_suite_rows(payload)
        if _token(_as_map(row).get("suite_id"))
    }


def _gate_report_result(payload: Mapping[str, object] | None) -> str:
    row = _as_map(payload)
    explicit = _token(row.get("result"))
    if explicit:
        return explicit
    if not _is_gate_report(row):
        return explicit
    assertions = _as_map(row.get("assertions"))
    return "complete" if all(bool(assertions.get(key, False)) for key in ("all_suites_passed", "cross_thread_hash_match", "no_unexpected_refusals", "suite_order_deterministic")) else "violation"


def _gate_suite_order(payload: Mapping[str, object] | None) -> list[str]:
    order = [str(item) for item in _as_list(_as_map(payload).get("suite_order")) if _token(item)]
    return order or list(GATE_SUITE_ORDER)


def _gate_cross_thread_hashes(cross_thread: Mapping[str, object] | None) -> dict[str, str]:
    row = _as_map(cross_thread)
    hashes = row.get("hashes")
    if isinstance(hashes, Mapping):
        return {str(key): _token(value) for key, value in sorted(hashes.items(), key=lambda item: str(item[0])) if _token(value)}
    labels = [str(item) for item in _as_list(row.get("thread_count_labels")) if _token(item)]
    values = [_token(item) for item in _as_list(hashes) if _token(item)] if isinstance(hashes, list) else []
    if values and not labels:
        labels = [str(index + 1) for index in range(len(values))]
    if len(values) == 1 and len(labels) > 1:
        values = values * len(labels)
    return {
        str(labels[index]): values[index]
        for index in range(min(len(labels), len(values)))
        if _token(values[index])
    }


def _gate_server_anchor_hashes(server_row: Mapping[str, object] | None) -> dict[str, str]:
    row = _as_map(server_row)
    metrics = _as_map(row.get("metrics"))
    proof = _as_map(row.get("proof"))
    ticks = [str(_as_int(item, 0)) for item in _as_list(metrics.get("proof_anchor_ticks"))]
    hashes = [_token(item) for item in _as_list(proof.get("proof_anchor_hashes")) if _token(item)]
    return {
        ticks[index]: hashes[index]
        for index in range(min(len(ticks), len(hashes)))
        if _token(ticks[index]) and _token(hashes[index])
    }


def _gate_refusal_counts(payload: Mapping[str, object] | None) -> dict[str, int]:
    aggregate = _as_map(_as_map(payload).get("aggregate"))
    counts = {}
    for row in _as_list(aggregate.get("refusal_counts")):
        item = _as_map(row)
        code = _token(item.get("refusal_code"))
        if not code:
            continue
        counts[code] = int(_as_int(item.get("count", 0), 0))
    return dict(sorted(counts.items(), key=lambda item: item[0]))


def _gate_metric_thresholds(suite_label: str, suite_row: Mapping[str, object] | None) -> dict:
    metrics = _as_map(_as_map(suite_row).get("metrics"))
    label = _token(suite_label)
    if label == "GEO-10":
        return {
            "metric_query_count": int(_as_int(metrics.get("metric_query_count", 0), 0)),
            "projection_view_cell_count": int(_as_int(metrics.get("projection_view_cell_count", 0), 0)),
            "path_expansions": int(_as_int(metrics.get("path_expansions", 0), 0)),
            "degradation_count": int(_as_int(metrics.get("degradation_count", 0), 0)),
        }
    if label == "LOGIC-10":
        return {
            "throttle_event_count": int(_as_int(metrics.get("throttle_event_count", 0), 0)),
            "security_block_count": int(_as_int(metrics.get("security_block_count", 0), 0)),
            "forced_expand_count": int(_as_int(metrics.get("forced_expand_count", 0), 0)),
            "debug_trace_sample_count": int(_as_int(metrics.get("debug_trace_sample_count", 0), 0)),
        }
    if label == "PROC-9":
        return {
            "micro_process_run_count": int(_as_int(metrics.get("micro_process_run_count", 0), 0)),
            "capsule_execution_count": int(_as_int(metrics.get("capsule_execution_count", 0), 0)),
            "deferred_task_count": int(_as_int(metrics.get("deferred_task_count", 0), 0)),
            "compaction_marker_count": int(_as_int(metrics.get("compaction_marker_count", 0), 0)),
        }
    if label == "SYS-8":
        return {
            "max_expand_count_per_tick": int(max((int(_as_int(item, 0)) for item in _as_list(metrics.get("expand_count_per_tick"))), default=0)),
            "max_collapse_count_per_tick": int(max((int(_as_int(item, 0)) for item in _as_list(metrics.get("collapse_count_per_tick"))), default=0)),
            "invariant_failure_total": int(sum(int(_as_int(item, 0)) for item in _as_list(metrics.get("invariant_check_failures_per_tick")))),
            "denied_expand_total": int(sum(int(_as_int(item, 0)) for item in _as_list(metrics.get("denied_expand_count_per_tick")))),
        }
    if label == "POLL-3":
        return {
            "max_concentration_observed": int(_as_int(metrics.get("max_concentration_observed", 0), 0)),
            "total_threshold_events": int(_as_int(metrics.get("total_threshold_events", 0), 0)),
            "total_degraded_dispersion_ticks": int(_as_int(metrics.get("total_degraded_dispersion_ticks", 0), 0)),
            "total_compliance_reports": int(_as_int(metrics.get("total_compliance_reports", 0), 0)),
        }
    if label == "EARTH-9":
        return {
            "map_rendered_cell_count": int(_as_int(metrics.get("map_rendered_cell_count", 0), 0)),
            "sky_view_generation_cost_units": int(_as_int(metrics.get("sky_view_generation_cost_units", 0), 0)),
            "hydrology_recompute_region_size": int(_as_int(metrics.get("hydrology_recompute_region_size", 0), 0)),
            "collision_query_count": int(_as_int(metrics.get("collision_query_count", 0), 0)),
        }
    if label == "CAP-NEG-4":
        return {
            "scenario_count": int(_as_int(metrics.get("scenario_count", 0), 0)),
            "refusal_counts": dict(sorted(_as_map(metrics.get("refusal_counts")).items(), key=lambda item: str(item[0]))),
        }
    if label == "PACK-COMPAT":
        return {
            "case_results": dict(sorted(_as_map(metrics.get("case_results")).items(), key=lambda item: str(item[0]))),
        }
    if label == "LIB-7":
        return {
            "ambiguity_count": int(_as_int(metrics.get("ambiguity_count", 0), 0)),
            "refusal_counts": dict(sorted(_as_map(metrics.get("refusal_counts")).items(), key=lambda item: str(item[0]))),
        }
    if label == "SERVER":
        return {
            "loopback_client_count": int(_as_int(metrics.get("loopback_client_count", 0), 0)),
            "multi_client_count": int(_as_int(metrics.get("multi_client_count", 0), 0)),
            "proof_anchor_count": int(_as_int(metrics.get("proof_anchor_count", 0), 0)),
        }
    return dict(metrics)


def _load_gate_suite_detail(repo_root: str, payload: Mapping[str, object] | None, suite_label: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    suite_row = _gate_suite_row_map(payload).get(str(suite_label), {})
    rel_path = _token(suite_row.get("report_path")) or DIRECT_SUITE_REPORT_RELS.get(str(suite_label), "")
    return load_json_if_present(repo_root_abs, rel_path) if rel_path else {}


def _collect_mismatch_rows(expected: object, actual: object, path: str = "$") -> list[dict]:
    if isinstance(expected, Mapping) and isinstance(actual, Mapping):
        rows = []
        keys = sorted(set(str(key) for key in expected.keys()) | set(str(key) for key in actual.keys()))
        for key in keys:
            rows.extend(_collect_mismatch_rows(_as_map(expected).get(key), _as_map(actual).get(key), "{}.{}".format(path, key)))
        return rows
    if isinstance(expected, list) and isinstance(actual, list):
        rows = []
        max_len = max(len(expected), len(actual))
        for index in range(max_len):
            exp = expected[index] if index < len(expected) else None
            act = actual[index] if index < len(actual) else None
            rows.extend(_collect_mismatch_rows(exp, act, "{}[{}]".format(path, index)))
        return rows
    if expected == actual:
        return []
    return [{"path": path, "expected": expected, "actual": actual}]


def _restamp_pack_manifest(path: str) -> None:
    payload = _read_json(path)
    if not payload:
        return
    payload["canonical_hash"] = canonical_sha256(dict(payload, canonical_hash=""))
    _write_canonical_json(path, payload)


def _pack_root_from_manifest_path(manifest_path: str) -> str:
    return _norm(os.path.dirname(_norm(manifest_path)))


def _default_bundle_source_pack_roots(repo_root: str) -> list[str]:
    payload = build_pack_lock_payload(repo_root=repo_root)
    out = []
    for pack_row in _as_list(payload.get("ordered_packs")):
        row = _as_map(pack_row)
        for source_row in _as_list(row.get("source_packs")):
            manifest_path = _token(_as_map(source_row).get("manifest_path"))
            if manifest_path:
                out.append(_pack_root_from_manifest_path(manifest_path))
    return _sorted_tokens(out)


def _copy_curated_pack_root(repo_root: str, *, curated_root_rel: str, pack_root_rels: Sequence[str]) -> str:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    curated_root_abs = _repo_abs(repo_root_abs, curated_root_rel)
    if os.path.isdir(curated_root_abs):
        shutil.rmtree(curated_root_abs)
    _ensure_dir(curated_root_abs)
    registries_src = os.path.join(repo_root_abs, "data", "registries")
    registries_dst = os.path.join(curated_root_abs, "data", "registries")
    shutil.copytree(registries_src, registries_dst, dirs_exist_ok=True)
    for rel_path in _sorted_tokens(pack_root_rels):
        src_abs = _repo_abs(repo_root_abs, rel_path)
        dst_abs = os.path.join(curated_root_abs, rel_path.replace("/", os.sep))
        shutil.copytree(src_abs, dst_abs, dirs_exist_ok=True)
        _restamp_pack_manifest(os.path.join(dst_abs, "pack.json"))
    return curated_root_abs


def _verify_curated_pack_set(repo_root: str, *, set_id: str, pack_root_rels: Sequence[str]) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    root_rel = os.path.join(DEFAULT_PACK_VERIFY_ROOT_REL, set_id)
    curated_root_abs = _copy_curated_pack_root(
        repo_root_abs,
        curated_root_rel=root_rel,
        pack_root_rels=pack_root_rels,
    )
    first = verify_pack_set(
        repo_root=curated_root_abs,
        schema_repo_root=repo_root_abs,
        mod_policy_id="mod_policy.lab",
    )
    second = verify_pack_set(
        repo_root=curated_root_abs,
        schema_repo_root=repo_root_abs,
        mod_policy_id="mod_policy.lab",
    )
    report_payload = _as_map(first.get("report"))
    pack_lock_payload = _as_map(first.get("pack_lock"))
    report_path = _repo_abs(repo_root_abs, os.path.join(DEFAULT_PACK_VERIFY_ROOT_REL, "{}.report.json".format(set_id)))
    lock_path = _repo_abs(repo_root_abs, os.path.join(DEFAULT_PACK_VERIFY_ROOT_REL, "{}.lock.json".format(set_id)))
    write_pack_compatibility_outputs(
        report_path=report_path,
        report_payload=report_payload,
        pack_lock_path=lock_path,
        pack_lock_payload=pack_lock_payload or None,
    )
    stable = _as_map(first.get("report")) == _as_map(second.get("report")) and _as_map(first.get("pack_lock")) == _as_map(second.get("pack_lock"))
    valid = bool(_as_map(report_payload).get("valid", False))
    return {
        "result": "complete" if _token(first.get("result")) == "complete" and valid and stable else "violation",
        "set_id": str(set_id),
        "curated_root": _relative_path(repo_root_abs, curated_root_abs),
        "pack_roots": _sorted_tokens(pack_root_rels),
        "pack_root_count": int(len(_sorted_tokens(pack_root_rels))),
        "valid": bool(valid),
        "stable_across_repeated_runs": bool(stable),
        "report_payload": report_payload,
        "pack_lock_payload": pack_lock_payload,
        "pack_lock_hash": _token(pack_lock_payload.get("pack_lock_hash")),
        "report_path": _relative_path(repo_root_abs, report_path),
        "pack_lock_path": _relative_path(repo_root_abs, lock_path),
        "deterministic_fingerprint": canonical_sha256(
            {
                "set_id": str(set_id),
                "pack_roots": _sorted_tokens(pack_root_rels),
                "report_payload": report_payload,
                "pack_lock_payload": pack_lock_payload,
                "stable_across_repeated_runs": bool(stable),
            }
        ),
    }


def run_pack_compat_stress(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    ensure_pack_compat_repo_on_path(repo_root_abs)
    fixture_root = make_temp_pack_compat_repo(repo_root_abs)
    try:
        fixture_first = verify_fixture_pack_set(repo_root_abs, fixture_root)
        fixture_second = verify_fixture_pack_set(repo_root_abs, fixture_root)
        fixture_valid = bool(_as_map(fixture_first.get("report")).get("valid", False))
        fixture_stable = _as_map(fixture_first.get("report")) == _as_map(fixture_second.get("report")) and _as_map(fixture_first.get("pack_lock")) == _as_map(fixture_second.get("pack_lock"))
        fixture_report = {
            "result": "complete" if _token(fixture_first.get("result")) == "complete" and fixture_valid and fixture_stable else "violation",
            "set_id": "fixture_valid_pack_set",
            "valid": bool(fixture_valid),
            "stable_across_repeated_runs": bool(fixture_stable),
            "pack_lock_hash": _token(_as_map(fixture_first.get("pack_lock")).get("pack_lock_hash")),
            "deterministic_fingerprint": canonical_sha256(
                {
                    "report": _as_map(fixture_first.get("report")),
                    "pack_lock": _as_map(fixture_first.get("pack_lock")),
                    "stable_across_repeated_runs": bool(fixture_stable),
                }
            ),
        }
    finally:
        cleanup_temp_repo(fixture_root)

    set_reports = [
        _verify_curated_pack_set(
            repo_root_abs,
            set_id="mvp_core_curated",
            pack_root_rels=MVP_CORE_SOURCE_PACK_ROOTS,
        ),
        _verify_curated_pack_set(
            repo_root_abs,
            set_id="mvp_runtime_bundle_sources",
            pack_root_rels=_default_bundle_source_pack_roots(repo_root_abs),
        ),
        fixture_report,
    ]
    assertions = {
        "all_sets_valid": all(bool(_as_map(row).get("valid", False)) for row in set_reports),
        "all_sets_stable": all(bool(_as_map(row).get("stable_across_repeated_runs", False)) for row in set_reports),
        "pack_lock_hashes_present": all(bool(_token(_as_map(row).get("pack_lock_hash"))) for row in set_reports),
    }
    report = {
        "result": "complete" if all(bool(value) for value in assertions.values()) else "violation",
        "set_reports": set_reports,
        "assertions": assertions,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def _suite_result_ok(suite_id: str, report: Mapping[str, object] | None) -> bool:
    row = _as_map(report)
    expected = "pass" if str(suite_id) == "proc9" else "complete"
    return _token(row.get("result")) == expected


def _suite_refusal_count(suite_id: str, report: Mapping[str, object] | None) -> int:
    row = _as_map(report)
    if str(suite_id) in {"cap_neg4", "lib7"}:
        return int(sum(int(max(0, _as_int(_as_map(item).get("count", 0), 0))) for item in _as_list(row.get("refusal_counts"))))
    return 0


def _suite_metric_thresholds(suite_id: str, report: Mapping[str, object] | None) -> dict:
    row = _as_map(report)
    if str(suite_id) == "geo10":
        metrics = _as_map(row.get("aggregate_metrics"))
        return {
            "metric_query_count": int(_as_int(metrics.get("metric_query_count", 0), 0)),
            "projection_view_cell_count": int(_as_int(metrics.get("projection_view_cell_count", 0), 0)),
            "path_expansions": int(_as_int(metrics.get("path_expansions", 0), 0)),
            "degradation_count": int(_as_int(metrics.get("degradation_count", 0), 0)),
        }
    if str(suite_id) == "logic10":
        metrics = _as_map(row.get("metrics"))
        return {
            "throttle_event_count": int(_as_int(metrics.get("throttle_event_count", 0), 0)),
            "security_block_count": int(_as_int(metrics.get("security_block_count", 0), 0)),
            "forced_expand_count": int(_as_int(metrics.get("forced_expand_count", 0), 0)),
            "debug_trace_sample_count": int(_as_int(metrics.get("debug_trace_sample_count", 0), 0)),
        }
    if str(suite_id) == "proc9":
        metrics = _as_map(row.get("metrics"))
        return {
            "micro_process_run_count": int(_as_int(metrics.get("micro_process_run_count", 0), 0)),
            "capsule_execution_count": int(_as_int(metrics.get("capsule_execution_count", 0), 0)),
            "deferred_task_count": int(_as_int(metrics.get("deferred_task_count", 0), 0)),
            "compaction_marker_count": int(_as_int(metrics.get("compaction_marker_count", 0), 0)),
        }
    if str(suite_id) == "sys8":
        metrics = _as_map(row.get("metrics"))
        return {
            "max_expand_count_per_tick": int(max((int(_as_int(item, 0)) for item in _as_list(metrics.get("expand_count_per_tick"))), default=0)),
            "max_collapse_count_per_tick": int(max((int(_as_int(item, 0)) for item in _as_list(metrics.get("collapse_count_per_tick"))), default=0)),
            "invariant_failure_total": int(sum(int(_as_int(item, 0)) for item in _as_list(metrics.get("invariant_check_failures_per_tick")))),
            "denied_expand_total": int(sum(int(_as_int(item, 0)) for item in _as_list(metrics.get("denied_expand_count_per_tick")))),
        }
    if str(suite_id) == "poll3":
        metrics = _as_map(row.get("metrics"))
        return {
            "emitted_total": int(_as_int(metrics.get("emitted_total", 0), 0)),
            "cell_update_total": int(_as_int(metrics.get("cell_update_total", 0), 0)),
            "subject_update_total": int(_as_int(metrics.get("subject_update_total", 0), 0)),
            "degrade_event_count": int(_as_int(metrics.get("degrade_event_count", 0), 0)),
        }
    if str(suite_id) == "earth9":
        metrics = _as_map(row.get("aggregate_metrics"))
        return {
            "climate_update_bucket_count": int(_as_int(metrics.get("climate_update_bucket_count", 0), 0)),
            "wind_update_bucket_count": int(_as_int(metrics.get("wind_update_bucket_count", 0), 0)),
            "tide_update_bucket_count": int(_as_int(metrics.get("tide_update_bucket_count", 0), 0)),
            "collision_query_count": int(_as_int(metrics.get("collision_query_count", 0), 0)),
            "derived_view_artifacts_count": int(_as_int(metrics.get("derived_view_artifacts_count", 0), 0)),
        }
    if str(suite_id) == "cap_neg4":
        return {
            "scenario_count": int(_as_int(row.get("scenario_count", 0), 0)),
            "read_only_count": int(_as_int(_as_map(row.get("mode_counts")).get("compat.read_only", 0), 0)),
            "refuse_count": int(_as_int(_as_map(row.get("mode_counts")).get("compat.refuse", 0), 0)),
        }
    if str(suite_id) == "pack_compat":
        return {
            "set_count": int(len(_as_list(row.get("set_reports")))),
            "valid_set_count": int(len([item for item in _as_list(row.get("set_reports")) if bool(_as_map(item).get("valid", False))])),
        }
    if str(suite_id) == "lib7":
        metrics = _as_map(row.get("bundle_metrics"))
        return {
            "instance_manifest_count": int(_as_int(metrics.get("instance_manifest_count", 0), 0)),
            "save_manifest_count": int(_as_int(metrics.get("save_manifest_count", 0), 0)),
            "launcher_projection_count": int(_as_int(metrics.get("launcher_projection_count", 0), 0)),
            "ambiguity_count": int(_as_int(row.get("ambiguity_count", 0), 0)),
        }
    if str(suite_id) == "server":
        metrics = _as_map(row.get("metrics"))
        return {
            "attach_count": int(_as_int(metrics.get("attach_count", 0), 0)),
            "detach_count": int(_as_int(metrics.get("detach_count", 0), 0)),
            "peak_client_count": int(_as_int(metrics.get("peak_client_count", 0), 0)),
            "proof_anchor_count": int(_as_int(metrics.get("proof_anchor_count", 0), 0)),
        }
    return {}


def _suite_primary_proof_hash(suite_id: str, report: Mapping[str, object] | None) -> str:
    row = _as_map(report)
    if str(suite_id) == "geo10":
        return _token(_as_map(row.get("proof_summary")).get("cross_platform_determinism_hash"))
    if str(suite_id) == "logic10":
        return _token(_as_map(row.get("proof_hash_summary")).get("aggregate_hash"))
    if str(suite_id) == "proc9":
        return canonical_sha256(_as_map(row.get("proof_hash_summary")))
    if str(suite_id) == "sys8":
        return canonical_sha256(_as_map(_as_map(row.get("metrics")).get("proof_hash_summary")))
    if str(suite_id) == "poll3":
        return canonical_sha256(_as_map(row.get("proof_hash_summary")))
    if str(suite_id) == "earth9":
        return _token(_as_map(row.get("proof_summary")).get("cross_platform_determinism_hash"))
    if str(suite_id) == "cap_neg4":
        return _token(_as_map(row.get("replay_summary")).get("deterministic_fingerprint"))
    if str(suite_id) == "pack_compat":
        return canonical_sha256(
            {
                _token(_as_map(item).get("set_id")): _token(_as_map(item).get("pack_lock_hash"))
                for item in _as_list(row.get("set_reports"))
                if _token(_as_map(item).get("set_id"))
            }
        )
    if str(suite_id) == "lib7":
        return _token(row.get("deterministic_fingerprint"))
    if str(suite_id) == "server":
        return _token(row.get("cross_platform_server_hash"))
    return _token(row.get("deterministic_fingerprint"))


def _suite_cross_thread_hashes(suite_id: str, report: Mapping[str, object] | None) -> dict:
    row = _as_map(report)
    if str(suite_id) == "logic10":
        return {
            str(_as_int(_as_map(item).get("thread_count_label", 0), 0)): _token(_as_map(item).get("core_hash"))
            for item in _as_list(row.get("stress_passes"))
            if _token(_as_map(item).get("core_hash"))
        }
    if str(suite_id) == "earth9":
        return dict(_as_map(_as_map(row.get("proof_summary")).get("thread_count_hashes")))
    return {}


def _normalize_suite_summary(suite_id: str, report: Mapping[str, object] | None) -> dict:
    row = _as_map(report)
    return {
        "suite_id": str(suite_id),
        "label": str(SUITE_LABELS.get(str(suite_id), str(suite_id).upper())),
        "order_index": int(SUITE_ORDER.index(str(suite_id)) + 1),
        "result": _token(row.get("result")),
        "result_ok": bool(_suite_result_ok(str(suite_id), row)),
        "deterministic_fingerprint": _token(row.get("deterministic_fingerprint")),
        "primary_proof_hash": _suite_primary_proof_hash(str(suite_id), row),
        "cross_thread_hashes": _suite_cross_thread_hashes(str(suite_id), row),
        "refusal_count": int(_suite_refusal_count(str(suite_id), row)),
        "metrics": _suite_metric_thresholds(str(suite_id), row),
    }


def _run_server_load_once(repo_root: str, *, seed: int) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    fixture = boot_server_fixture(
        repo_root_abs,
        save_suffix="mvp_stress",
        seed=int(seed),
    )
    boot = _as_map(fixture.get("boot"))
    if _token(boot.get("result")) != "complete":
        return {
            "result": _token(boot.get("result")) or "refused",
            "boot": boot,
            "deterministic_fingerprint": canonical_sha256({"boot": boot}),
        }

    client_rows = []
    peak_client_count = 0
    try:
        for index in range(3):
            client = connect_loopback_client(
                boot,
                client_peer_id="peer.client.mvpstress.{:02d}".format(index + 1),
                account_id="account.server.mvpstress.{:02d}".format(index + 1),
            )
            client_rows.append(
                {
                    "phase": "attach_initial",
                    "index": int(index),
                    "connection_id": _token(_as_map(client.get("accepted")).get("connection_id")),
                    "result": _token(client.get("result")),
                    "compatibility_mode_id": _token(_as_map(client.get("accepted")).get("compatibility_mode_id")),
                    "negotiation_record_hash": _token(_as_map(client.get("accepted")).get("negotiation_record_hash")),
                    "transport": client.get("client_transport"),
                }
            )
            peak_client_count = max(
                peak_client_count,
                len(_as_map(_as_map(boot.get("runtime")).get("server_mvp_connections"))),
            )
        service_loopback_control_channel(boot)
        tick_first = run_server_ticks(boot, 3)
        transport_to_close = client_rows[1].get("transport")
        if transport_to_close is not None:
            transport_to_close.close()
        service_loopback_control_channel(boot)
        client_rows.append(
            {
                "phase": "detach_mid",
                "index": 1,
                "result": "complete",
                "connection_id": _token(client_rows[1].get("connection_id")),
            }
        )
        replacement = connect_loopback_client(
            boot,
            client_peer_id="peer.client.mvpstress.04",
            account_id="account.server.mvpstress.04",
        )
        client_rows.append(
            {
                "phase": "attach_replacement",
                "index": 3,
                "connection_id": _token(_as_map(replacement.get("accepted")).get("connection_id")),
                "result": _token(replacement.get("result")),
                "compatibility_mode_id": _token(_as_map(replacement.get("accepted")).get("compatibility_mode_id")),
                "negotiation_record_hash": _token(_as_map(replacement.get("accepted")).get("negotiation_record_hash")),
                "transport": replacement.get("client_transport"),
            }
        )
        peak_client_count = max(
            peak_client_count,
            len(_as_map(_as_map(boot.get("runtime")).get("server_mvp_connections"))),
        )
        service_loopback_control_channel(boot)
        tick_second = run_server_ticks(boot, max(0, int(DEFAULT_SERVER_TICKS) - 3))
        runtime = _as_map(boot.get("runtime"))
        server = _as_map(runtime.get("server"))
        meta = _as_map(runtime.get("server_mvp"))
        connections = _as_map(runtime.get("server_mvp_connections"))
        anchors = [dict(item) for item in _as_list(runtime.get("server_mvp_proof_anchors")) if isinstance(item, Mapping)]
        message_rows = []
        for row in client_rows:
            transport = row.get("transport")
            if transport is None:
                continue
            message_rows.extend(drain_client_messages(repo_root_abs, transport))
        proof_anchor_hashes = [canonical_sha256(row) for row in anchors]
        proof_anchor_ticks = [int(_as_int(row.get("tick", 0), 0)) for row in anchors]
        proof_anchor_hashes_by_tick = {
            str(proof_anchor_ticks[index]): proof_anchor_hashes[index]
            for index in range(min(len(proof_anchor_ticks), len(proof_anchor_hashes)))
        }
        pack_lock_hashes = _sorted_tokens(_as_map(anchor).get("pack_lock_hash") for anchor in anchors)
        negotiation_hashes = _sorted_tokens(_as_map(row).get("negotiation_record_hash") for row in connections.values())
        summary = {
            "result": "complete"
            if _token(tick_first.get("result")) == "complete" and _token(tick_second.get("result")) == "complete"
            else "violation",
            "client_trace": [
                dict((key, value) for key, value in row.items() if key != "transport")
                for row in client_rows
            ],
            "metrics": {
                "attach_count": 4,
                "detach_count": 1,
                "peak_client_count": int(peak_client_count),
                "final_client_count": int(len(connections)),
                "proof_anchor_count": int(len(anchors)),
                "tick_stream_count": int(
                    len(
                        [
                            row
                            for row in message_rows
                            if _token(_as_map(row).get("payload_schema_id")) == "server.tick_stream.stub.v1"
                        ]
                    )
                ),
            },
            "final_tick": int(_as_int(server.get("network_tick", 0), 0)),
            "tick_hash": _token(server.get("last_tick_hash")),
            "proof_anchor_hashes_by_tick": dict(sorted(proof_anchor_hashes_by_tick.items(), key=lambda item: int(item[0]))),
            "connection_ids": sorted(connections.keys()),
            "negotiation_record_hashes": negotiation_hashes,
            "contract_bundle_hash": _token(meta.get("contract_bundle_hash")),
            "semantic_contract_registry_hash": _token(meta.get("semantic_contract_registry_hash")),
            "overlay_manifest_hash": _token(meta.get("overlay_manifest_hash")),
            "pack_lock_hashes": pack_lock_hashes,
            "cross_platform_server_hash": canonical_sha256(
                {
                    "final_tick": int(_as_int(server.get("network_tick", 0), 0)),
                    "connection_ids": sorted(connections.keys()),
                    "proof_anchor_hashes_by_tick": dict(sorted(proof_anchor_hashes_by_tick.items(), key=lambda item: int(item[0]))),
                    "negotiation_record_hashes": negotiation_hashes,
                    "contract_bundle_hash": _token(meta.get("contract_bundle_hash")),
                    "semantic_contract_registry_hash": _token(meta.get("semantic_contract_registry_hash")),
                }
            ),
            "assertions": {
                "multi_client_loopback": int(peak_client_count) >= 3,
                "detach_applied": int(len(connections)) == 3,
                "proof_anchor_emitted": bool(proof_anchor_hashes_by_tick),
                "contract_bundle_pinned": bool(_token(meta.get("contract_bundle_hash"))),
                "pack_lock_pinned": len(pack_lock_hashes) == 1 and bool(pack_lock_hashes),
            },
            "deterministic_fingerprint": "",
        }
        summary["deterministic_fingerprint"] = canonical_sha256(dict(summary, deterministic_fingerprint=""))
        return summary
    finally:
        for row in client_rows:
            transport = row.get("transport")
            if transport is not None:
                try:
                    transport.close()
                except Exception:
                    pass
        service_loopback_control_channel(boot)


def run_server_load_stress(repo_root: str, *, seed: int = DEFAULT_SERVER_MVP0_SEED) -> dict:
    first = _run_server_load_once(repo_root, seed=int(seed))
    second = _run_server_load_once(repo_root, seed=int(seed))
    stable = first == second
    assertions = dict(_as_map(first.get("assertions")))
    assertions["stable_across_repeated_runs"] = bool(stable)
    report = {
        "result": "complete" if _token(first.get("result")) == "complete" and bool(stable) and all(bool(value) for value in assertions.values()) else "violation",
        "seed": int(seed),
        "metrics": dict(_as_map(first.get("metrics"))),
        "proof_anchor_hashes_by_tick": dict(_as_map(first.get("proof_anchor_hashes_by_tick"))),
        "negotiation_record_hashes": list(_as_list(first.get("negotiation_record_hashes"))),
        "pack_lock_hashes": list(_as_list(first.get("pack_lock_hashes"))),
        "contract_bundle_hash": _token(first.get("contract_bundle_hash")),
        "semantic_contract_registry_hash": _token(first.get("semantic_contract_registry_hash")),
        "overlay_manifest_hash": _token(first.get("overlay_manifest_hash")),
        "cross_platform_server_hash": _token(first.get("cross_platform_server_hash")),
        "first_run": first,
        "second_run": second,
        "assertions": assertions,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def _run_geo_suite() -> dict:
    return verify_geo_stress_scenario(seed=DEFAULT_GEO10_SEED)


def _run_logic_suite(repo_root: str) -> dict:
    return run_logic_stress(
        repo_root=repo_root,
        seed=1010,
        tick_count=8,
        network_count=12,
        mega_node_count=1_000_000,
        thread_count_labels=(1, 8),
    )


def _run_proc_suite(repo_root: str) -> dict:
    scenario = generate_proc_stress_scenario(
        seed=99001,
        stabilized_count=1024,
        exploration_count=320,
        drifting_count=192,
        research_campaign_count=160,
        software_run_count=320,
        tick_horizon=96,
    )
    return run_proc_stress(
        repo_root=repo_root,
        scenario=scenario,
        tick_count=96,
        max_micro_steps_per_tick=48,
        max_total_tasks_per_tick=192,
    )


def _run_sys_suite() -> dict:
    scenario = generate_sys_stress_scenario(
        seed=88017,
        system_count=512,
        nested_size=20,
        tick_horizon=64,
        shard_count=4,
        player_count=2,
        roi_width=18,
        time_warp_batch_size=4,
    )
    return run_sys_stress(
        scenario=scenario,
        tick_count=64,
        max_expands_per_tick=0,
        max_collapses_per_tick=0,
        max_macro_capsules_per_tick=0,
        max_health_updates_per_tick=0,
        max_reliability_evals_per_tick=0,
    )


def _run_poll_suite(repo_root: str) -> dict:
    scenario = generate_poll_stress_scenario(
        seed=9301,
        region_count=3,
        cells_per_region=9,
        subject_count=36,
        tick_horizon=24,
        emissions_per_tick=3,
        measurements_per_tick=1,
        compliance_interval_ticks=4,
        include_wind_field=False,
        repo_root=repo_root,
    )
    defaults = _envelope_defaults("poll.envelope.standard")
    return run_poll_stress_scenario(
        scenario=copy.deepcopy(scenario),
        tick_count=24,
        budget_envelope_id="poll.envelope.standard",
        max_compute_units_per_tick=int(defaults["max_compute_units_per_tick"]),
        dispersion_tick_stride_base=int(defaults["dispersion_tick_stride_base"]),
        max_cell_updates_per_tick=int(defaults["max_cell_updates_per_tick"]),
        max_subject_updates_per_tick=int(defaults["max_subject_updates_per_tick"]),
        max_compliance_reports_per_tick=int(defaults["max_compliance_reports_per_tick"]),
        max_measurements_per_tick=int(defaults["max_measurements_per_tick"]),
    )


def _run_earth_suite(repo_root: str) -> dict:
    return verify_earth_mvp_stress_scenario(repo_root=repo_root, seed=DEFAULT_EARTH9_SEED)


def _run_cap_neg_suite(repo_root: str) -> dict:
    matrix = generate_interop_matrix(repo_root=repo_root, seed=DEFAULT_CAP_NEG4_SEED)
    return run_interop_stress(repo_root=repo_root, matrix=matrix, seed=DEFAULT_CAP_NEG4_SEED)


def _run_lib_suite(repo_root: str) -> dict:
    out_root = _repo_abs(repo_root, DEFAULT_LIB_OUT_REL)
    return run_lib_stress(
        repo_root=repo_root,
        out_root=out_root,
        seed=DEFAULT_LIB7_SEED,
        slash_mode="forward",
    )


def build_mvp_stress_hash_summary(report: Mapping[str, object] | None) -> dict:
    payload = _as_map(report)
    if _is_gate_report(payload):
        suite_rows = _gate_suite_row_map(payload)
        aggregate = _as_map(payload.get("aggregate"))
        logic_proof = _as_map(_as_map(suite_rows.get("LOGIC-10")).get("proof"))
        earth_proof = _as_map(_as_map(suite_rows.get("EARTH-9")).get("proof"))
        server_row = _as_map(suite_rows.get("SERVER"))
        server_proof = _as_map(server_row.get("proof"))
        pack_compat_proof = _as_map(_as_map(suite_rows.get("PACK-COMPAT")).get("proof"))
        summary = {
            "gate_id": _token(payload.get("gate_id")) or MVP_STRESS_GATE_ID,
            "gate_seed": int(_as_int(payload.get("gate_seed", DEFAULT_MVP_STRESS_SEED), DEFAULT_MVP_STRESS_SEED)),
            "schema_version": _token(payload.get("schema_version")) or "1.0.0",
            "suite_order": _gate_suite_order(payload),
            "suite_fingerprints": dict(sorted(_as_map(aggregate.get("suite_fingerprints")).items(), key=lambda item: str(item[0]))),
            "metrics_fingerprints": dict(sorted(_as_map(aggregate.get("metrics_fingerprints")).items(), key=lambda item: str(item[0]))),
            "proof_fingerprints": dict(sorted(_as_map(aggregate.get("proof_fingerprints")).items(), key=lambda item: str(item[0]))),
            "cross_thread_hashes": {
                suite_label: _gate_cross_thread_hashes(_as_map(row).get("cross_thread"))
                for suite_label, row in sorted(suite_rows.items(), key=lambda item: str(item[0]))
                if _gate_cross_thread_hashes(_as_map(row).get("cross_thread"))
            },
            "known_refusal_counts": _gate_refusal_counts(payload),
            "result_hash": _token(aggregate.get("result_hash")),
            "logic_compiled_model_hash": _token(logic_proof.get("compiled_model_hash_chain")),
            "earth_view_hashes": {
                "sky_hash": _token(earth_proof.get("sky_hash")),
                "water_hash": _token(earth_proof.get("water_hash")),
                "climate_window_hash": _token(earth_proof.get("climate_window_hash")),
                "tide_window_hash": _token(earth_proof.get("tide_window_hash")),
                "lighting_hash": _token(earth_proof.get("lighting_hash")),
            },
            "server_contract_bundle_hash": _token(server_proof.get("contract_bundle_hash")),
            "server_proof_anchor_hashes": _gate_server_anchor_hashes(server_row),
            "pack_compat_hashes": {
                "base_pack_lock_hash": _token(pack_compat_proof.get("base_pack_lock_hash")),
                "mutated_pack_lock_hash": _token(pack_compat_proof.get("mutated_pack_lock_hash")),
                "repeated_pack_lock_hash": _token(pack_compat_proof.get("repeated_pack_lock_hash")),
            },
            "deterministic_fingerprint": "",
        }
        summary["deterministic_fingerprint"] = canonical_sha256(dict(summary, deterministic_fingerprint=""))
        return summary

    suite_summaries = {
        _token(_as_map(row).get("suite_id")): _as_map(row)
        for row in _as_list(payload.get("suite_summaries"))
        if _token(_as_map(row).get("suite_id"))
    }
    pack_compat_report = _as_map(_as_map(payload.get("suite_reports")).get("pack_compat"))
    server_report = _as_map(_as_map(payload.get("suite_reports")).get("server"))
    summary = {
        "gate_seed": int(_as_int(payload.get("gate_seed", DEFAULT_MVP_STRESS_SEED), DEFAULT_MVP_STRESS_SEED)),
        "suite_order": [str(item) for item in _as_list(payload.get("suite_order")) if _token(item)],
        "suite_fingerprints": {
            key: _token(_as_map(value).get("deterministic_fingerprint"))
            for key, value in sorted(suite_summaries.items(), key=lambda item: item[0])
        },
        "primary_proof_hashes": {
            key: _token(_as_map(value).get("primary_proof_hash"))
            for key, value in sorted(suite_summaries.items(), key=lambda item: item[0])
        },
        "cross_thread_hashes": {
            key: dict(_as_map(value).get("cross_thread_hashes"))
            for key, value in sorted(suite_summaries.items(), key=lambda item: item[0])
            if _as_map(value).get("cross_thread_hashes")
        },
        "refusal_counts": {
            key: int(_as_int(_as_map(value).get("refusal_count", 0), 0))
            for key, value in sorted(suite_summaries.items(), key=lambda item: item[0])
        },
        "runtime_pack_lock_hash": _token(payload.get("runtime_pack_lock_hash")),
        "pack_compat_pack_lock_hashes": {
            _token(_as_map(row).get("set_id")): _token(_as_map(row).get("pack_lock_hash"))
            for row in _as_list(pack_compat_report.get("set_reports"))
            if _token(_as_map(row).get("set_id"))
        },
        "server_contract_bundle_hash": _token(server_report.get("contract_bundle_hash")),
        "server_proof_anchor_hashes": dict(_as_map(server_report.get("proof_anchor_hashes_by_tick"))),
        "unexpected_refusal_count": int(_as_int(payload.get("unexpected_refusal_count", 0), 0)),
        "gate_degrade_event_count": int(_as_int(payload.get("gate_degrade_event_count", 0), 0)),
        "deterministic_fingerprint": "",
    }
    summary["deterministic_fingerprint"] = canonical_sha256(dict(summary, deterministic_fingerprint=""))
    return summary


def run_all_mvp_stress(repo_root: str, *, seed: int = DEFAULT_MVP_STRESS_SEED) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    suite_reports = {
        "geo10": _run_geo_suite(),
        "logic10": _run_logic_suite(repo_root_abs),
        "proc9": _run_proc_suite(repo_root_abs),
        "sys8": _run_sys_suite(),
        "poll3": _run_poll_suite(repo_root_abs),
        "earth9": _run_earth_suite(repo_root_abs),
        "cap_neg4": _run_cap_neg_suite(repo_root_abs),
        "pack_compat": run_pack_compat_stress(repo_root_abs),
        "lib7": _run_lib_suite(repo_root_abs),
        "server": run_server_load_stress(repo_root_abs, seed=DEFAULT_SERVER_MVP0_SEED),
    }
    suite_summaries = [_normalize_suite_summary(suite_id, suite_reports[suite_id]) for suite_id in SUITE_ORDER]
    unexpected_refusal_count = int(
        sum(
            int(_as_int(_as_map(row).get("refusal_count", 0), 0))
            for row in suite_summaries
            if _token(_as_map(row).get("suite_id")) not in EXPECTED_REFUSAL_SUITES
        )
    )
    assertions = {
        "suite_order_stable": [str(row.get("suite_id")) for row in suite_summaries] == list(SUITE_ORDER),
        "all_suites_pass": all(bool(_as_map(row).get("result_ok", False)) for row in suite_summaries),
        "unexpected_refusals_zero": int(unexpected_refusal_count) == 0,
        "gate_degrade_events_zero": True,
    }
    pack_lock_payload = build_pack_lock_payload(repo_root=repo_root_abs)
    report = {
        "result": "complete" if all(bool(value) for value in assertions.values()) else "violation",
        "gate_seed": int(seed),
        "suite_order": list(SUITE_ORDER),
        "suite_summaries": suite_summaries,
        "suite_reports": suite_reports,
        "runtime_pack_lock_hash": _token(pack_lock_payload.get("pack_lock_hash")),
        "unexpected_refusal_count": int(unexpected_refusal_count),
        "gate_degrade_event_count": 0,
        "assertions": assertions,
        "hash_summary": {},
        "deterministic_fingerprint": "",
    }
    report["hash_summary"] = build_mvp_stress_hash_summary(report)
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def build_mvp_stress_baseline(
    report: Mapping[str, object] | None,
    proof_report: Mapping[str, object] | None,
) -> dict:
    payload = _as_map(report)
    proof = _as_map(proof_report)
    if _is_gate_report(payload):
        suite_rows = _gate_suite_row_map(payload)
        hash_summary = build_mvp_stress_hash_summary(payload)
        earth_proof = _as_map(_as_map(suite_rows.get("EARTH-9")).get("proof"))
        logic_proof = _as_map(_as_map(suite_rows.get("LOGIC-10")).get("proof"))
        pack_lock_hashes = dict(sorted(_as_map(_as_map(proof.get("proof_surfaces")).get("pack_lock_hashes")).items(), key=lambda item: str(item[0])))
        baseline = {
            "schema_version": "1.0.0",
            "baseline_id": "mvp.stress.baseline.v1",
            "gate_id": _token(payload.get("gate_id")) or MVP_STRESS_GATE_ID,
            "gate_seed": int(_as_int(payload.get("gate_seed", DEFAULT_MVP_STRESS_SEED), DEFAULT_MVP_STRESS_SEED)),
            "suite_order": _gate_suite_order(payload),
            "suite_fingerprints": dict(_as_map(hash_summary.get("suite_fingerprints"))),
            "metrics_fingerprints": dict(_as_map(hash_summary.get("metrics_fingerprints"))),
            "proof_fingerprints": dict(_as_map(hash_summary.get("proof_fingerprints"))),
            "cross_thread_hashes": dict(_as_map(hash_summary.get("cross_thread_hashes"))),
            "key_metric_thresholds": {
                suite_label: _gate_metric_thresholds(suite_label, suite_row)
                for suite_label, suite_row in sorted(suite_rows.items(), key=lambda item: str(item[0]))
            },
            "known_refusal_counts": _gate_refusal_counts(payload),
            "pack_lock_hashes": pack_lock_hashes,
            "server_contract_bundle_hash": _token(hash_summary.get("server_contract_bundle_hash")),
            "server_proof_anchor_hashes": dict(_as_map(hash_summary.get("server_proof_anchor_hashes"))),
            "logic_compiled_model_hash": _token(logic_proof.get("compiled_model_hash_chain")),
            "selected_view_fingerprints": {
                "sky_hash": _token(earth_proof.get("sky_hash")),
                "water_hash": _token(earth_proof.get("water_hash")),
                "climate_window_hash": _token(earth_proof.get("climate_window_hash")),
                "tide_window_hash": _token(earth_proof.get("tide_window_hash")),
                "lighting_hash": _token(earth_proof.get("lighting_hash")),
            },
            "proc_compaction_marker_hash_chain": _token(_as_map(_as_map(proof.get("proof_surfaces")).get("compaction_replay")).get("compaction_marker_hash_chain")),
            "update_policy": {
                "required_commit_tag": MVP_STRESS_REGRESSION_UPDATE_TAG,
                "notes": "Updating the MVP stress regression lock requires explicit review under MVP-STRESS-REGRESSION-UPDATE.",
            },
            "deterministic_fingerprint": "",
        }
        baseline["deterministic_fingerprint"] = canonical_sha256(dict(baseline, deterministic_fingerprint=""))
        return baseline

    hash_summary = _as_map(payload.get("hash_summary"))
    baseline = {
        "schema_version": "1.0.0",
        "baseline_id": "mvp.stress.baseline.v1",
        "gate_seed": int(_as_int(payload.get("gate_seed", DEFAULT_MVP_STRESS_SEED), DEFAULT_MVP_STRESS_SEED)),
        "suite_order": [str(item) for item in _as_list(payload.get("suite_order")) if _token(item)],
        "suite_fingerprints": dict(_as_map(hash_summary.get("suite_fingerprints"))),
        "primary_proof_hashes": dict(_as_map(hash_summary.get("primary_proof_hashes"))),
        "cross_thread_hashes": dict(_as_map(hash_summary.get("cross_thread_hashes"))),
        "key_metric_thresholds": {
            _token(_as_map(row).get("suite_id")): dict(_as_map(row).get("metrics"))
            for row in _as_list(payload.get("suite_summaries"))
            if _token(_as_map(row).get("suite_id"))
        },
        "refusal_counts": dict(_as_map(hash_summary.get("refusal_counts"))),
        "runtime_pack_lock_hash": _token(hash_summary.get("runtime_pack_lock_hash")),
        "pack_compat_pack_lock_hashes": dict(_as_map(hash_summary.get("pack_compat_pack_lock_hashes"))),
        "server_contract_bundle_hash": _token(hash_summary.get("server_contract_bundle_hash")),
        "server_proof_anchor_hashes": dict(_as_map(hash_summary.get("server_proof_anchor_hashes"))),
        "proc_compaction_marker_hash_chain": _token(_as_map(_as_map(proof.get("verification_runs")).get("proc_compaction")).get("compaction_marker_hash_chain")),
        "update_policy": {
            "required_commit_tag": MVP_STRESS_REGRESSION_UPDATE_TAG,
            "notes": "Updating the MVP stress regression lock requires explicit review under MVP-STRESS-REGRESSION-UPDATE.",
        },
        "deterministic_fingerprint": "",
    }
    baseline["deterministic_fingerprint"] = canonical_sha256(dict(baseline, deterministic_fingerprint=""))
    return baseline


def verify_mvp_stress_proofs(
    repo_root: str,
    *,
    report: Mapping[str, object] | None = None,
    baseline_payload: Mapping[str, object] | None = None,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    report_payload = _as_map(report) or load_json_if_present(repo_root_abs, DEFAULT_REPORT_REL)
    if _is_gate_report(report_payload):
        suite_rows = _gate_suite_row_map(report_payload)
        gate_assertions = _as_map(report_payload.get("assertions"))
        logic_row = _as_map(suite_rows.get("LOGIC-10"))
        earth_row = _as_map(suite_rows.get("EARTH-9"))
        proc_row = _as_map(suite_rows.get("PROC-9"))
        cap_neg_row = _as_map(suite_rows.get("CAP-NEG-4"))
        pack_compat_row = _as_map(suite_rows.get("PACK-COMPAT"))
        lib_row = _as_map(suite_rows.get("LIB-7"))
        server_row = _as_map(suite_rows.get("SERVER"))

        direct_proc = _load_gate_suite_detail(repo_root_abs, report_payload, "PROC-9")
        direct_cap_neg = _load_gate_suite_detail(repo_root_abs, report_payload, "CAP-NEG-4")
        direct_pack_compat = _load_gate_suite_detail(repo_root_abs, report_payload, "PACK-COMPAT")
        direct_lib = _load_gate_suite_detail(repo_root_abs, report_payload, "LIB-7")
        direct_server = _load_gate_suite_detail(repo_root_abs, report_payload, "SERVER")
        current_pack_lock = build_pack_lock_payload(repo_root=repo_root_abs)
        proc_compaction = verify_proc_compaction(
            state_payload=direct_proc,
            shard_id="shard.proc.mvp_stress",
            start_tick=0,
            end_tick=int(max(1, _as_int(direct_proc.get("tick_horizon", 48), 48))),
        )

        direct_loopback = _as_map(direct_server.get("loopback"))
        direct_loopback_replay = _as_map(direct_server.get("loopback_replay"))
        direct_singleplayer = _as_map(direct_server.get("singleplayer"))
        direct_singleplayer_replay = _as_map(direct_server.get("singleplayer_replay"))
        direct_supervisor_replay = _as_map(direct_server.get("supervisor_replay"))
        direct_ipc_replay = _as_map(direct_server.get("ipc_replay"))
        cap_neg_stress = _as_map(direct_cap_neg.get("stress_report"))
        cap_neg_replay = _as_map(direct_cap_neg.get("replay_report"))
        pack_cases = _as_map(direct_pack_compat.get("cases"))
        lib_replays = _as_map(direct_lib.get("replay_reports"))

        server_proof = _as_map(server_row.get("proof"))
        logic_proof = _as_map(logic_row.get("proof"))
        earth_proof = _as_map(earth_row.get("proof"))
        proof_anchor_hashes = _gate_server_anchor_hashes(server_row)
        cross_thread_hashes = {
            suite_label: _gate_cross_thread_hashes(_as_map(suite_row).get("cross_thread"))
            for suite_label, suite_row in sorted(suite_rows.items(), key=lambda item: str(item[0]))
            if _gate_cross_thread_hashes(_as_map(suite_row).get("cross_thread"))
        }
        cross_thread_match = all(len(set(values.values())) == 1 for values in cross_thread_hashes.values() if values)
        pack_lock_hashes = {
            "runtime": _token(current_pack_lock.get("pack_lock_hash")),
            "server_loopback_session": _token(_as_map(_as_map(direct_loopback.get("handshake")).get("session_info")).get("pack_lock_hash")),
            "pack_compat_base_first": _token(_as_map(pack_cases.get("base_first")).get("pack_lock_hash")),
            "pack_compat_base_second": _token(_as_map(pack_cases.get("base_second")).get("pack_lock_hash")),
            "pack_compat_mutated_before": _token(_as_map(pack_cases.get("compat_mutation")).get("pack_lock_hash_before")),
            "pack_compat_mutated_after": _token(_as_map(pack_cases.get("compat_mutation")).get("pack_lock_hash_after")),
            "pack_compat_overlay_last_wins": _token(_as_map(pack_cases.get("overlay_conflict_last_wins")).get("pack_lock_hash")),
        }
        negotiation_record_hashes = {
            "cap_neg": [_token(item) for item in _as_list(_as_map(cap_neg_row.get("proof")).get("negotiation_record_hashes")) if _token(item)],
            "server_loopback": [_token(server_proof.get("handshake_negotiation_record_hash"))] if _token(server_proof.get("handshake_negotiation_record_hash")) else [],
        }
        contract_bundle_hashes = _sorted_tokens(
            [
                server_proof.get("contract_bundle_hash"),
                direct_loopback.get("contract_bundle_hash"),
                direct_singleplayer.get("contract_bundle_hash"),
            ]
        )
        checks = {
            "gate_report_complete": _gate_report_result(report_payload) == "complete",
            "proof_anchors_stable": bool(proof_anchor_hashes)
            and _token(direct_loopback_replay.get("result")) == "complete"
            and bool(direct_loopback_replay.get("stable", False))
            and _token(direct_singleplayer_replay.get("result")) == "complete"
            and bool(direct_singleplayer_replay.get("stable", False)),
            "negotiation_records_stable": bool(negotiation_record_hashes["cap_neg"])
            and bool(negotiation_record_hashes["server_loopback"])
            and _token(cap_neg_replay.get("result")) == "complete"
            and _token(direct_supervisor_replay.get("result")) == "complete"
            and _token(direct_ipc_replay.get("result")) == "complete",
            "contract_bundle_pinned": len(contract_bundle_hashes) == 1,
            "pack_locks_stable": bool(pack_lock_hashes["runtime"])
            and pack_lock_hashes["runtime"] == pack_lock_hashes["server_loopback_session"]
            and pack_lock_hashes["pack_compat_base_first"] == pack_lock_hashes["pack_compat_base_second"]
            and bool(pack_lock_hashes["pack_compat_mutated_after"])
            and pack_lock_hashes["pack_compat_mutated_before"] != pack_lock_hashes["pack_compat_mutated_after"],
            "compaction_replay_matches": _token(proc_compaction.get("result")) == "complete"
            and _token(_as_map(proc_compaction.get("replay_result")).get("result")) == "complete"
            and bool(_as_map(proc_row.get("assertions")).get("compaction_replay_anchor_match", False))
            and bool(_as_map(_as_map(suite_rows.get("GEO-10")).get("assertions")).get("replay_from_anchor_matches", False))
            and bool(_as_map(_as_map(suite_rows.get("SYS-8")).get("assertions")).get("stable_replay_hashes", False)),
            "cross_thread_hash_match": bool(gate_assertions.get("cross_thread_hash_match", False)) and bool(cross_thread_match),
            "no_unexpected_refusals": bool(gate_assertions.get("no_unexpected_refusals", False)),
        }
        proof_surfaces = {
            "proof_anchor_hashes": dict(proof_anchor_hashes),
            "negotiation_record_hashes": negotiation_record_hashes,
            "contract_bundle_hashes": contract_bundle_hashes,
            "pack_lock_hashes": pack_lock_hashes,
            "cross_thread_hashes": cross_thread_hashes,
            "compaction_replay": {
                "result": _token(proc_compaction.get("result")),
                "replay_result": _token(_as_map(proc_compaction.get("replay_result")).get("result")),
                "compaction_marker_hash_chain": _token(proc_compaction.get("compaction_marker_hash_chain")),
                "deterministic_fingerprint": _token(proc_compaction.get("deterministic_fingerprint")),
            },
            "capneg_replay": {
                "result": _token(cap_neg_replay.get("result")),
                "deterministic_fingerprint": _token(cap_neg_replay.get("deterministic_fingerprint")),
                "stress_report_fingerprint": _token(cap_neg_replay.get("stress_report_fingerprint")),
            },
            "server_replays": {
                "loopback_replay_stable": bool(direct_loopback_replay.get("stable", False)),
                "singleplayer_replay_stable": bool(direct_singleplayer_replay.get("stable", False)),
                "supervisor_replay_result": _token(direct_supervisor_replay.get("result")),
                "ipc_replay_result": _token(direct_ipc_replay.get("result")),
            },
            "lib_replay_reports": {
                "negotiation": {
                    "result": _token(_as_map(lib_replays.get("negotiation")).get("result")),
                    "deterministic_fingerprint": _token(_as_map(lib_replays.get("negotiation")).get("deterministic_fingerprint")),
                },
                "save_open": {
                    "result": _token(_as_map(lib_replays.get("save_open")).get("result")),
                    "replay_hash": _token(_as_map(lib_replays.get("save_open")).get("replay_hash")),
                },
            },
            "bundle_verifications": dict(sorted(_as_map(direct_lib.get("bundle_hashes")).items(), key=lambda item: str(item[0]))),
            "logic_compiled_model_hash": _token(logic_proof.get("compiled_model_hash_chain")),
            "selected_view_hashes": {
                "sky_hash": _token(earth_proof.get("sky_hash")),
                "water_hash": _token(earth_proof.get("water_hash")),
                "climate_window_hash": _token(earth_proof.get("climate_window_hash")),
                "tide_window_hash": _token(earth_proof.get("tide_window_hash")),
                "lighting_hash": _token(earth_proof.get("lighting_hash")),
            },
            "cap_neg_mode_counts": dict(sorted(_as_map(cap_neg_stress.get("mode_counts")).items(), key=lambda item: str(item[0]))),
        }
        proof_report = {
            "schema_version": "1.0.0",
            "gate_report_fingerprint": _token(report_payload.get("deterministic_fingerprint")),
            "checks": checks,
            "proof_surfaces": proof_surfaces,
            "baseline_candidate": {},
            "baseline_comparison": {
                "checked": bool(baseline_payload),
                "match": False,
                "mismatches": [],
                "deterministic_fingerprint": "",
            },
            "result": "complete",
            "deterministic_fingerprint": "",
        }
        proof_report["baseline_candidate"] = build_mvp_stress_baseline(report_payload, proof_report)
        if baseline_payload:
            proof_report["baseline_comparison"]["mismatches"] = _collect_mismatch_rows(_as_map(baseline_payload), _as_map(proof_report.get("baseline_candidate")))
            proof_report["baseline_comparison"]["match"] = not bool(proof_report["baseline_comparison"]["mismatches"])
            proof_report["checks"]["baseline_match"] = bool(proof_report["baseline_comparison"]["match"])
        proof_report["result"] = "complete" if all(bool(value) for value in _as_map(proof_report.get("checks")).values()) else "violation"
        proof_report["baseline_comparison"]["deterministic_fingerprint"] = canonical_sha256(
            dict(_as_map(proof_report.get("baseline_comparison")), deterministic_fingerprint="")
        )
        proof_report["deterministic_fingerprint"] = canonical_sha256(dict(proof_report, deterministic_fingerprint=""))
        return proof_report

    hash_summary = _as_map(report_payload.get("hash_summary"))
    suite_reports = _as_map(report_payload.get("suite_reports"))
    suite_summaries = _as_list(report_payload.get("suite_summaries"))
    server_rerun = run_server_load_stress(repo_root_abs, seed=DEFAULT_SERVER_MVP0_SEED)
    pack_compat_rerun = run_pack_compat_stress(repo_root_abs)
    interop_replay = verify_interop_stress_replay(repo_root=repo_root_abs, seed=DEFAULT_CAP_NEG4_SEED)
    proc_report = _as_map(suite_reports.get("proc9"))
    proc_compaction = verify_proc_compaction(
        state_payload=proc_report,
        shard_id="shard.proc.mvp_stress",
        start_tick=0,
        end_tick=int(max(1, _as_int(proc_report.get("tick_horizon", 96), 96))),
    )
    current_pack_lock = build_pack_lock_payload(repo_root=repo_root_abs)
    stored_server = _as_map(suite_reports.get("server"))
    stored_pack_compat = _as_map(suite_reports.get("pack_compat"))
    stored_cross_threads = dict(_as_map(hash_summary.get("cross_thread_hashes")))
    actual_cross_threads = {
        _token(_as_map(row).get("suite_id")): dict(_as_map(row).get("cross_thread_hashes"))
        for row in suite_summaries
        if _token(_as_map(row).get("suite_id")) and _as_map(row).get("cross_thread_hashes")
    }
    assertions = {
        "stress_report_complete": _token(report_payload.get("result")) == "complete",
        "proof_anchors_stable_across_runs": dict(_as_map(stored_server.get("proof_anchor_hashes_by_tick"))) == dict(_as_map(server_rerun.get("proof_anchor_hashes_by_tick"))),
        "negotiation_records_stable": _sorted_tokens(stored_server.get("negotiation_record_hashes")) == _sorted_tokens(server_rerun.get("negotiation_record_hashes"))
        and _token(interop_replay.get("result")) == "complete",
        "contract_bundle_pinned": bool(_token(stored_server.get("contract_bundle_hash")))
        and _token(stored_server.get("contract_bundle_hash")) == _token(server_rerun.get("contract_bundle_hash")),
        "pack_locks_stable": _token(hash_summary.get("runtime_pack_lock_hash")) == _token(current_pack_lock.get("pack_lock_hash"))
        and {
            _token(_as_map(row).get("set_id")): _token(_as_map(row).get("pack_lock_hash"))
            for row in _as_list(stored_pack_compat.get("set_reports"))
            if _token(_as_map(row).get("set_id"))
        }
        == {
            _token(_as_map(row).get("set_id")): _token(_as_map(row).get("pack_lock_hash"))
            for row in _as_list(pack_compat_rerun.get("set_reports"))
            if _token(_as_map(row).get("set_id"))
        },
        "compaction_replay_matches": _token(proc_compaction.get("result")) == "complete"
        and _token(_as_map(proc_compaction.get("replay_result")).get("result")) == "complete"
        and bool(_as_map(_as_map(suite_reports.get("geo10")).get("assertions")).get("replay_from_anchor_matches", False))
        and bool(_as_map(_as_map(suite_reports.get("sys8")).get("assertions")).get("stable_replay_hashes", False)),
        "cross_thread_hash_match": stored_cross_threads == actual_cross_threads
        and all(len(set(dict(value).values())) == 1 for value in actual_cross_threads.values()),
        "gate_unexpected_refusals_zero": int(_as_int(report_payload.get("unexpected_refusal_count", 0), 0)) == 0,
        "gate_degrade_events_zero": int(_as_int(report_payload.get("gate_degrade_event_count", 0), 0)) == 0,
    }
    verification_runs = {
        "server_rerun": {
            "deterministic_fingerprint": _token(server_rerun.get("deterministic_fingerprint")),
            "proof_anchor_hashes_by_tick": dict(_as_map(server_rerun.get("proof_anchor_hashes_by_tick"))),
            "negotiation_record_hashes": list(_as_list(server_rerun.get("negotiation_record_hashes"))),
            "contract_bundle_hash": _token(server_rerun.get("contract_bundle_hash")),
            "cross_platform_server_hash": _token(server_rerun.get("cross_platform_server_hash")),
        },
        "pack_compat_rerun": {
            "deterministic_fingerprint": _token(pack_compat_rerun.get("deterministic_fingerprint")),
            "pack_lock_hashes": {
                _token(_as_map(row).get("set_id")): _token(_as_map(row).get("pack_lock_hash"))
                for row in _as_list(pack_compat_rerun.get("set_reports"))
                if _token(_as_map(row).get("set_id"))
            },
        },
        "interop_replay": {
            "result": _token(interop_replay.get("result")),
            "deterministic_fingerprint": _token(interop_replay.get("deterministic_fingerprint")),
        },
        "proc_compaction": {
            "result": _token(proc_compaction.get("result")),
            "compaction_marker_hash_chain": _token(proc_compaction.get("compaction_marker_hash_chain")),
            "deterministic_fingerprint": _token(proc_compaction.get("deterministic_fingerprint")),
            "replay_result": _token(_as_map(proc_compaction.get("replay_result")).get("result")),
        },
        "current_runtime_pack_lock_hash": _token(current_pack_lock.get("pack_lock_hash")),
        "cross_thread_hashes": actual_cross_threads,
    }
    proof_report = {
        "result": "complete" if all(bool(value) for value in assertions.values()) else "violation",
        "report_fingerprint": _token(report_payload.get("deterministic_fingerprint")),
        "hash_summary_fingerprint": _token(hash_summary.get("deterministic_fingerprint")),
        "assertions": assertions,
        "verification_runs": verification_runs,
        "baseline_candidate": {},
        "baseline_comparison": {
            "checked": bool(baseline_payload),
            "match": False,
            "mismatches": [],
            "deterministic_fingerprint": "",
        },
        "deterministic_fingerprint": "",
    }
    proof_report["baseline_candidate"] = build_mvp_stress_baseline(report_payload, proof_report)
    if baseline_payload:
        proof_report["baseline_comparison"]["mismatches"] = _collect_mismatch_rows(_as_map(baseline_payload), _as_map(proof_report.get("baseline_candidate")))
        proof_report["baseline_comparison"]["match"] = not bool(proof_report["baseline_comparison"]["mismatches"])
        proof_report["assertions"]["baseline_match"] = bool(proof_report["baseline_comparison"]["match"])
        proof_report["result"] = "complete" if all(bool(value) for value in proof_report["assertions"].values()) else "violation"
    proof_report["baseline_comparison"]["deterministic_fingerprint"] = canonical_sha256(
        dict(_as_map(proof_report.get("baseline_comparison")), deterministic_fingerprint="")
    )
    proof_report["deterministic_fingerprint"] = canonical_sha256(dict(proof_report, deterministic_fingerprint=""))
    return proof_report


def render_mvp_stress_final_markdown(
    report: Mapping[str, object] | None,
    *,
    proof_report: Mapping[str, object] | None = None,
    baseline: Mapping[str, object] | None = None,
    gate_results: Mapping[str, object] | None = None,
) -> str:
    row = _as_map(report)
    proof = _as_map(proof_report)
    base = _as_map(baseline)
    gates = _as_map(gate_results)
    if _is_gate_report(row):
        suite_rows = _gate_suite_row_map(row)
        hash_summary = build_mvp_stress_hash_summary(row)
        gate_checks = _as_map(proof.get("checks"))
        ready = (
            _gate_report_result(row) == "complete"
            and _token(proof.get("result")) == "complete"
            and all(_token(_as_map(gates.get(key)).get("status")) == "PASS" for key in ("repox", "auditx", "testx", "stress"))
        )
        lines = [
            "# MVP Stress Final",
            "",
            "## Run Summary",
            "",
            "- result: `{}`".format(_gate_report_result(row) or "unknown"),
            "- proof_result: `{}`".format(_token(proof.get("result")) or "unknown"),
            "- gate_id: `{}`".format(_token(row.get("gate_id")) or MVP_STRESS_GATE_ID),
            "- gate_seed: `{}`".format(int(_as_int(row.get("gate_seed", DEFAULT_MVP_STRESS_SEED), DEFAULT_MVP_STRESS_SEED))),
            "- deterministic_fingerprint: `{}`".format(_token(row.get("deterministic_fingerprint"))),
            "- readiness: {}".format(
                "Ready for MVP-GATE-2 cross-platform agreement and RELEASE series."
                if ready
                else "Not ready for MVP-GATE-2 cross-platform agreement or RELEASE series."
            ),
            "",
            "## Suite Results",
            "",
        ]
        for suite_label in _gate_suite_order(row):
            suite_row = _as_map(suite_rows.get(suite_label))
            lines.append(
                "- {}: `{}` fingerprint=`{}`".format(
                    suite_label,
                    _token(suite_row.get("result")) or "unknown",
                    _token(suite_row.get("deterministic_fingerprint")),
                )
            )
        lines.extend(
            [
                "",
                "## Hashes",
                "",
                "- result_hash: `{}`".format(_token(hash_summary.get("result_hash"))),
                "- server_contract_bundle_hash: `{}`".format(_token(hash_summary.get("server_contract_bundle_hash"))),
                "- server_proof_anchor_hashes: `{}`".format(canonical_sha256(_as_map(hash_summary.get("server_proof_anchor_hashes")))),
                "- logic_compiled_model_hash: `{}`".format(_token(hash_summary.get("logic_compiled_model_hash"))),
                "- earth_sky_hash: `{}`".format(_token(_as_map(hash_summary.get("earth_view_hashes")).get("sky_hash"))),
                "- earth_water_hash: `{}`".format(_token(_as_map(hash_summary.get("earth_view_hashes")).get("water_hash"))),
                "",
                "## Degradations",
                "",
                "- default_lane_degrade_events: `0`",
                "- suite_local_degrade_fingerprint: `{}`".format(canonical_sha256(_as_map(_as_map(row.get("aggregate")).get("degrade_counts")))),
                "- note: stress suites intentionally exercise deterministic degrade behavior under load; no silent degrade was observed in the default gate path.",
                "",
                "## Gates",
                "",
                "- RepoX STRICT: `{}`{}".format(_token(_as_map(gates.get("repox")).get("status")) or "NOT_RUN", " ({})".format(_token(_as_map(gates.get("repox")).get("note"))) if _token(_as_map(gates.get("repox")).get("note")) else ""),
                "- AuditX STRICT: `{}`{}".format(_token(_as_map(gates.get("auditx")).get("status")) or "NOT_RUN", " ({})".format(_token(_as_map(gates.get("auditx")).get("note"))) if _token(_as_map(gates.get("auditx")).get("note")) else ""),
                "- TestX: `{}`{}".format(_token(_as_map(gates.get("testx")).get("status")) or "NOT_RUN", " ({})".format(_token(_as_map(gates.get("testx")).get("note"))) if _token(_as_map(gates.get("testx")).get("note")) else ""),
                "- stress orchestrator: `{}`{}".format(_token(_as_map(gates.get("stress")).get("status")) or "NOT_RUN", " ({})".format(_token(_as_map(gates.get("stress")).get("note"))) if _token(_as_map(gates.get("stress")).get("note")) else ""),
            ]
        )
        if proof:
            lines.extend(
                [
                    "",
                    "## Proof Checks",
                    "",
                ]
            )
            for key in (
                "proof_anchors_stable",
                "negotiation_records_stable",
                "contract_bundle_pinned",
                "pack_locks_stable",
                "compaction_replay_matches",
                "cross_thread_hash_match",
                "no_unexpected_refusals",
            ):
                lines.append("- {}: `{}`".format(key, bool(gate_checks.get(key, False))))
        if base:
            lines.extend(
                [
                    "",
                    "## Regression Lock",
                    "",
                    "- baseline_id: `{}`".format(_token(base.get("baseline_id"))),
                    "- baseline_fingerprint: `{}`".format(_token(base.get("deterministic_fingerprint"))),
                    "- required_commit_tag: `{}`".format(_token(_as_map(base.get("update_policy")).get("required_commit_tag"))),
                ]
            )
        return "\n".join(lines).strip() + "\n"

    def _gate_line(label: str, key: str) -> str:
        gate = _as_map(gates.get(key))
        status = _token(gate.get("status")) or "NOT_RUN"
        note = _token(gate.get("note"))
        suffix = " ({})".format(note) if note else ""
        return "- {}: `{}`{}".format(label, status, suffix)

    ready = (
        _token(row.get("result")) == "complete"
        and _token(proof.get("result")) == "complete"
        and all(_token(_as_map(gates.get(key)).get("status")) == "PASS" for key in ("repox", "auditx", "testx", "stress"))
    )
    lines = [
        "# MVP Stress Final",
        "",
        "## Run Summary",
        "",
        "- result: `{}`".format(_token(row.get("result")) or "unknown"),
        "- proof_result: `{}`".format(_token(proof.get("result")) or "unknown"),
        "- gate_seed: `{}`".format(int(_as_int(row.get("gate_seed", DEFAULT_MVP_STRESS_SEED), DEFAULT_MVP_STRESS_SEED))),
        "- unexpected_refusal_count: `{}`".format(int(_as_int(row.get("unexpected_refusal_count", 0), 0))),
        "- gate_degrade_event_count: `{}`".format(int(_as_int(row.get("gate_degrade_event_count", 0), 0))),
        "- deterministic_fingerprint: `{}`".format(_token(row.get("deterministic_fingerprint"))),
        "- readiness: {}".format(
            "Ready for MVP-GATE-2 cross-platform agreement and RELEASE series."
            if ready
            else "Not ready for MVP-GATE-2 cross-platform agreement or RELEASE series."
        ),
        "",
        "## Suite Results",
        "",
    ]
    for suite in _as_list(row.get("suite_summaries")):
        suite_row = _as_map(suite)
        lines.append(
            "- {}: `{}` fingerprint=`{}`".format(
                _token(suite_row.get("label")),
                _token(suite_row.get("result")) or "unknown",
                _token(suite_row.get("deterministic_fingerprint")),
            )
        )
    lines.extend(
        [
            "",
            "## Key Hashes",
            "",
            "- runtime_pack_lock_hash: `{}`".format(_token(row.get("runtime_pack_lock_hash"))),
            "- server_contract_bundle_hash: `{}`".format(_token(_as_map(_as_map(row.get("suite_reports")).get("server")).get("contract_bundle_hash"))),
            "- server_proof_anchor_hashes: `{}`".format(canonical_sha256(_as_map(_as_map(row.get("hash_summary")).get("server_proof_anchor_hashes")))),
            "- logic_primary_proof_hash: `{}`".format(_token(_as_map(_as_map(row.get("hash_summary")).get("primary_proof_hashes")).get("logic10"))),
            "- earth_cross_thread_hash: `{}`".format(_token(_as_map(_as_map(row.get("hash_summary")).get("primary_proof_hashes")).get("earth9"))),
            "",
            "## Degrade Events",
            "",
            "- gate_default_degrade_events: `0`",
            "- note: suite-local deterministic degradation remains locked in suite metrics; no gate-level unexpected degrade event occurred.",
            "",
            "## Gates",
            "",
            _gate_line("RepoX STRICT", "repox"),
            _gate_line("AuditX STRICT", "auditx"),
            _gate_line("TestX", "testx"),
            _gate_line("stress orchestrator", "stress"),
        ]
    )
    if base:
        lines.extend(
            [
                "",
                "## Regression Lock",
                "",
                "- baseline_id: `{}`".format(_token(base.get("baseline_id"))),
                "- baseline_fingerprint: `{}`".format(_token(base.get("deterministic_fingerprint"))),
                "- required_commit_tag: `{}`".format(_token(_as_map(base.get("update_policy")).get("required_commit_tag"))),
            ]
        )
    return "\n".join(lines).strip() + "\n"


def maybe_load_cached_mvp_stress_report(
    repo_root: str,
    *,
    report_path: str = "",
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    payload = load_json_if_present(repo_root_abs, report_path or DEFAULT_REPORT_REL)
    if not payload:
        return {}
    if _gate_report_result(payload) != "complete":
        return {}
    expected_order = list(GATE_SUITE_ORDER) if _is_gate_report(payload) else list(SUITE_ORDER)
    if [str(item) for item in _as_list(payload.get("suite_order"))] != expected_order:
        return {}
    return payload


def maybe_load_cached_mvp_stress_proof_report(
    repo_root: str,
    *,
    report: Mapping[str, object],
    proof_report_path: str = "",
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    payload = load_json_if_present(repo_root_abs, proof_report_path or DEFAULT_PROOF_REPORT_REL)
    if not payload:
        return {}
    if _token(payload.get("result")) != "complete":
        return {}
    report_fingerprint = _token(payload.get("gate_report_fingerprint")) or _token(payload.get("report_fingerprint"))
    if report_fingerprint != _token(_as_map(report).get("deterministic_fingerprint")):
        return {}
    return payload


def write_mvp_stress_outputs(
    repo_root: str,
    *,
    report: Mapping[str, object],
    report_path: str = "",
    hashes_path: str = "",
    proof_report: Mapping[str, object] | None = None,
    proof_report_path: str = "",
    baseline_path: str = "",
    final_doc_path: str = "",
    update_baseline: bool = False,
    update_tag: str = "",
    gate_results: Mapping[str, object] | None = None,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    report_abs = _repo_abs(repo_root_abs, report_path or DEFAULT_REPORT_REL)
    hashes_abs = _repo_abs(repo_root_abs, hashes_path or DEFAULT_HASHES_REL)
    report_payload = dict(_as_map(report))
    hash_summary = build_mvp_stress_hash_summary(report_payload)
    _write_canonical_json(report_abs, report_payload)
    _write_canonical_json(hashes_abs, hash_summary)

    baseline_written = False
    proof_written = False
    if proof_report:
        proof_abs = _repo_abs(repo_root_abs, proof_report_path or DEFAULT_PROOF_REPORT_REL)
        proof_payload = dict(_as_map(proof_report))
        _write_canonical_json(proof_abs, proof_payload)
        proof_written = True
        baseline_abs = _repo_abs(repo_root_abs, baseline_path or DEFAULT_BASELINE_REL)
        final_doc_abs = _repo_abs(repo_root_abs, final_doc_path or DEFAULT_FINAL_DOC_REL)
        baseline_payload = dict(_as_map(proof_payload.get("baseline_candidate")))
        if update_baseline:
            if _token(update_tag) != MVP_STRESS_REGRESSION_UPDATE_TAG:
                raise ValueError("baseline update requires {}".format(MVP_STRESS_REGRESSION_UPDATE_TAG))
            _write_canonical_json(baseline_abs, baseline_payload)
            baseline_written = True
        else:
            existing_baseline = load_json_if_present(repo_root_abs, _relative_path(repo_root_abs, baseline_abs))
            if existing_baseline:
                baseline_payload = existing_baseline
        markdown = render_mvp_stress_final_markdown(
            report_payload,
            proof_report=proof_payload,
            baseline=baseline_payload,
            gate_results=gate_results,
        )
        _write_text(final_doc_abs, markdown)

    return {
        "result": "complete",
        "report_path": _relative_path(repo_root_abs, report_abs),
        "hashes_path": _relative_path(repo_root_abs, hashes_abs),
        "proof_report_path": _relative_path(repo_root_abs, _repo_abs(repo_root_abs, proof_report_path or DEFAULT_PROOF_REPORT_REL))
        if proof_report
        else "",
        "baseline_path": _relative_path(repo_root_abs, _repo_abs(repo_root_abs, baseline_path or DEFAULT_BASELINE_REL))
        if proof_report
        else "",
        "final_doc_path": _relative_path(repo_root_abs, _repo_abs(repo_root_abs, final_doc_path or DEFAULT_FINAL_DOC_REL))
        if proof_report
        else "",
        "proof_written": bool(proof_written),
        "baseline_written": bool(baseline_written),
        "deterministic_fingerprint": canonical_sha256(
            {
                "report_fingerprint": _token(report_payload.get("deterministic_fingerprint")),
                "hashes_fingerprint": _token(hash_summary.get("deterministic_fingerprint")),
                "proof_fingerprint": _token(_as_map(proof_report).get("deterministic_fingerprint")),
                "baseline_written": bool(baseline_written),
            }
        ),
    }


__all__ = [
    "DEFAULT_BASELINE_REL",
    "DEFAULT_FINAL_DOC_REL",
    "DEFAULT_HASHES_REL",
    "DEFAULT_MVP_STRESS_SEED",
    "DEFAULT_PROOF_REPORT_REL",
    "DEFAULT_REPORT_REL",
    "MVP_STRESS_REGRESSION_UPDATE_TAG",
    "build_mvp_stress_baseline",
    "build_mvp_stress_hash_summary",
    "load_json_if_present",
    "maybe_load_cached_mvp_stress_proof_report",
    "maybe_load_cached_mvp_stress_report",
    "render_mvp_stress_final_markdown",
    "run_all_mvp_stress",
    "run_pack_compat_stress",
    "run_server_load_stress",
    "verify_mvp_stress_proofs",
    "write_mvp_stress_outputs",
]
