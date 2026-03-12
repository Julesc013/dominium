"""Deterministic MVP smoke scenario and harness helpers."""

from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
from typing import Iterable, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.appshell.logging import create_log_engine, get_current_log_engine, set_current_log_engine  # noqa: E402
from src.appshell.tui import build_tui_surface, run_tui_mode  # noqa: E402
from src.compat import build_default_endpoint_descriptor, build_degrade_runtime_state, negotiate_endpoint_descriptors  # noqa: E402
from src.diag.repro_bundle_builder import verify_repro_bundle, write_repro_bundle  # noqa: E402
from src.embodiment import build_logic_probe_task, build_logic_trace_task  # noqa: E402
from src.packs.compat.pack_verification_pipeline import verify_pack_set, write_pack_compatibility_outputs  # noqa: E402
from tools.earth.earth9_stress_common import (  # noqa: E402
    generate_earth_mvp_stress_scenario,
    verify_earth_mvp_stress_scenario,
    build_earth_mvp_regression_baseline,
)
from tools.embodiment.emb1_probe import build_tool_session_report  # noqa: E402
from tools.logic.tool_replay_compiled_logic_window import replay_compiled_logic_window_from_payload  # noqa: E402
from tools.logic.tool_replay_trace_window import replay_trace_window_from_payload  # noqa: E402
from tools.logic.tool_run_logic_debug_stress import build_logic_debug_stress_scenario  # noqa: E402
from tools.mvp.runtime_bundle import (  # noqa: E402
    build_pack_lock_payload,
    build_profile_bundle_payload,
    build_session_template_payload,
)
from tools.server import server_mvp0_probe as server_probe  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402
from tools.xstack.sessionx.common import write_canonical_json  # noqa: E402
from tools.xstack.testx.tests._logic_eval_test_utils import (  # noqa: E402
    load_eval_inputs,
    make_chain_network,
    seed_signal_requests,
)


DEFAULT_MVP_SMOKE_SEED = 456
DEFAULT_SCENARIO_REL = os.path.join("build", "mvp", "mvp_smoke_scenario.json")
DEFAULT_HASHES_REL = os.path.join("build", "mvp", "mvp_smoke_hashes.json")
DEFAULT_REPORT_REL = os.path.join("build", "mvp", "mvp_smoke_report.json")
DEFAULT_BASELINE_REL = os.path.join("data", "regression", "mvp_smoke_baseline.json")
DEFAULT_FINAL_DOC_REL = os.path.join("docs", "audit", "MVP_SMOKE_FINAL.md")
MVP_SMOKE_REGRESSION_UPDATE_TAG = "MVP-SMOKE-REGRESSION-UPDATE"
DEFAULT_CAPTURE_WINDOW = 16
DEFAULT_SERVER_TICKS = int(server_probe.DEFAULT_SERVER_TICKS)
DEFAULT_SERVER_SAVE_SUFFIX = "mvp_smoke"

CURATED_VERIFY_ROOT_REL = os.path.join("build", "mvp", "verify_root")
CURATED_REPORT_REL = os.path.join("build", "mvp", "curated_pack_compatibility_report.json")
CURATED_LOCK_REL = os.path.join("build", "mvp", "curated_pack_lock.json")
SMOKE_PROFILE_REL = os.path.join("build", "mvp", "bundle.mvp_smoke.json")
SMOKE_SESSION_REL = os.path.join("build", "mvp", "session.mvp_smoke.json")
SMOKE_LOCK_REL = os.path.join("build", "mvp", "pack_lock.mvp_smoke.json")
SETUP_VERIFY_REPORT_REL = os.path.join("build", "mvp", "setup_verify_report.json")
SETUP_VERIFY_LOCK_REL = os.path.join("build", "mvp", "setup_verify_lock.json")
LAUNCHER_BUILD_LOCK_REPORT_REL = os.path.join("build", "mvp", "launcher_build_lock_report.json")
LAUNCHER_BUILD_LOCK_LOCK_REL = os.path.join("build", "mvp", "launcher_build_lock.json")
DIAG_BUNDLE_DIR_REL = os.path.join("build", "mvp", "diag_bundle")

MVP_SOURCE_PACK_MANIFESTS = (
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


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def _read_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


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


def _payload_fingerprint(payload: Mapping[str, object] | None) -> str:
    return canonical_sha256(dict(_as_map(payload), deterministic_fingerprint=""))


def _derived_seed(seed: int, stream: str) -> int:
    digest = canonical_sha256({"seed": int(seed), "stream": str(stream).strip()})
    return int(digest[:12], 16) % 1000000


def _command_summary(report: Mapping[str, object] | None) -> dict:
    row = _as_map(report)
    payload = _as_map(row.get("payload"))
    return {
        "command": str(row.get("command", "")).strip(),
        "returncode": int(row.get("returncode", 0) or 0),
        "result": _token(payload.get("result")),
        "refusal_code": _token(payload.get("refusal_code")) or _token(_as_map(payload.get("refusal")).get("reason_code")),
        "stdout_hash": canonical_sha256(str(row.get("stdout", ""))),
        "stderr_hash": canonical_sha256(str(row.get("stderr", ""))),
        "payload_fingerprint": canonical_sha256(payload),
    }


def _failure_result(result: str, reason: str, **details: object) -> dict:
    payload = {
        "result": str(result or "refused").strip() or "refused",
        "reason": str(reason or "").strip(),
        "details": {str(key): value for key, value in sorted(details.items(), key=lambda item: str(item[0]))},
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _restamp_pack_manifest(path: str) -> None:
    payload = _read_json(path)
    if not payload:
        return
    payload["canonical_hash"] = canonical_sha256(dict(payload, canonical_hash=""))
    write_canonical_json(path, payload)


def build_curated_pack_runtime(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    curated_root_abs = _repo_abs(repo_root_abs, CURATED_VERIFY_ROOT_REL)
    if os.path.isdir(curated_root_abs):
        shutil.rmtree(curated_root_abs)
    _ensure_dir(curated_root_abs)

    registries_src = os.path.join(repo_root_abs, "data", "registries")
    registries_dst = os.path.join(curated_root_abs, "data", "registries")
    shutil.copytree(registries_src, registries_dst, dirs_exist_ok=True)
    copied_pack_roots = []
    for rel_path in MVP_SOURCE_PACK_MANIFESTS:
        src_abs = _repo_abs(repo_root_abs, rel_path)
        dst_abs = os.path.join(curated_root_abs, rel_path.replace("/", os.sep))
        shutil.copytree(src_abs, dst_abs, dirs_exist_ok=True)
        manifest_abs = os.path.join(dst_abs, "pack.json")
        _restamp_pack_manifest(manifest_abs)
        copied_pack_roots.append(_relative_path(curated_root_abs, dst_abs))

    verify_result = verify_pack_set(
        repo_root=curated_root_abs,
        schema_repo_root=repo_root_abs,
        mod_policy_id="mod_policy.lab",
    )
    report_payload = _as_map(verify_result.get("report"))
    pack_lock_payload = _as_map(verify_result.get("pack_lock"))
    report_path = _repo_abs(repo_root_abs, CURATED_REPORT_REL)
    lock_path = _repo_abs(repo_root_abs, CURATED_LOCK_REL)
    write_pack_compatibility_outputs(
        report_path=report_path,
        report_payload=report_payload,
        pack_lock_path=lock_path,
        pack_lock_payload=pack_lock_payload or None,
    )
    return {
        "result": _token(verify_result.get("result")) or "refused",
        "curated_root": _relative_path(repo_root_abs, curated_root_abs),
        "curated_root_abs": curated_root_abs,
        "copied_pack_roots": copied_pack_roots,
        "verify_result": verify_result,
        "report_path": _relative_path(repo_root_abs, report_path),
        "pack_lock_path": _relative_path(repo_root_abs, lock_path),
        "report_payload": report_payload,
        "pack_lock_payload": pack_lock_payload,
        "pack_lock_hash": _token(pack_lock_payload.get("pack_lock_hash")),
        "deterministic_fingerprint": canonical_sha256(
            {
                "curated_root": _relative_path(repo_root_abs, curated_root_abs),
                "copied_pack_roots": copied_pack_roots,
                "verify_result": verify_result,
            }
        ),
    }


def build_smoke_runtime_artifacts(repo_root: str, *, curated_runtime: Mapping[str, object] | None = None) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    curated = _as_map(curated_runtime) or build_curated_pack_runtime(repo_root_abs)
    verification_pack_lock_payload = _as_map(curated.get("pack_lock_payload"))
    profile_bundle_payload = build_profile_bundle_payload(repo_root=repo_root_abs)
    pack_lock_payload = build_pack_lock_payload(
        repo_root=repo_root_abs,
        profile_bundle_payload=profile_bundle_payload,
    )
    session_template_payload = build_session_template_payload(
        repo_root=repo_root_abs,
        pack_lock_payload=pack_lock_payload,
    )

    profile_path = _repo_abs(repo_root_abs, SMOKE_PROFILE_REL)
    session_path = _repo_abs(repo_root_abs, SMOKE_SESSION_REL)
    pack_lock_path = _repo_abs(repo_root_abs, SMOKE_LOCK_REL)
    _write_canonical_json(profile_path, profile_bundle_payload)
    _write_canonical_json(session_path, session_template_payload)
    _write_canonical_json(pack_lock_path, pack_lock_payload)
    return {
        "result": "complete",
        "profile_bundle_payload": profile_bundle_payload,
        "session_template_payload": session_template_payload,
        "pack_lock_payload": pack_lock_payload,
        "verification_pack_lock_payload": verification_pack_lock_payload,
        "profile_bundle_path": _relative_path(repo_root_abs, profile_path),
        "session_template_path": _relative_path(repo_root_abs, session_path),
        "pack_lock_path": _relative_path(repo_root_abs, pack_lock_path),
        "pack_lock_hash": _token(pack_lock_payload.get("pack_lock_hash")),
        "verification_pack_lock_hash": _token(verification_pack_lock_payload.get("pack_lock_hash")),
        "deterministic_fingerprint": canonical_sha256(
            {
                "profile_bundle_hash": _token(profile_bundle_payload.get("profile_bundle_hash")),
                "session_template_fingerprint": _token(session_template_payload.get("deterministic_fingerprint")),
                "pack_lock_hash": _token(pack_lock_payload.get("pack_lock_hash")),
                "verification_pack_lock_hash": _token(verification_pack_lock_payload.get("pack_lock_hash")),
            }
        ),
    }


def _run_wrapper(repo_root: str, bin_name: str, args: Sequence[str]) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    wrapper_path = os.path.join(repo_root_abs, "dist", "bin", str(bin_name))
    proc = subprocess.run(
        [sys.executable, wrapper_path] + [str(item) for item in list(args or [])],
        cwd=repo_root_abs,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    stdout = str(proc.stdout or "")
    stderr = str(proc.stderr or "")
    payload = {}
    try:
        parsed = json.loads(stdout.strip() or "{}")
    except ValueError:
        parsed = {}
    if isinstance(parsed, Mapping):
        payload = dict(parsed)
    return {
        "command": " ".join([str(bin_name)] + [str(item) for item in list(args or [])]),
        "bin_name": str(bin_name),
        "args": [str(item) for item in list(args or [])],
        "returncode": int(proc.returncode or 0),
        "stdout": stdout,
        "stderr": stderr,
        "payload": payload,
        "deterministic_fingerprint": canonical_sha256(
            {
                "command": " ".join([str(bin_name)] + [str(item) for item in list(args or [])]),
                "returncode": int(proc.returncode or 0),
                "stdout": stdout,
                "stderr": stderr,
            }
        ),
    }


def _extract_process_endpoint_ids(status_payload: Mapping[str, object] | None) -> dict:
    endpoints = {}
    for row in _as_list(_as_map(status_payload).get("processes")):
        row_map = _as_map(row)
        product_id = _token(row_map.get("product_id"))
        endpoint_id = _token(row_map.get("endpoint_id"))
        if product_id and endpoint_id:
            endpoints[product_id] = endpoint_id
    return dict(sorted(endpoints.items(), key=lambda item: item[0]))


def _mvp_authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "law_profile_id": "law.lab_freecam",
        "privilege_level": "operator",
        "entitlements": [
            "session.boot",
            "entitlement.inspect",
            "entitlement.control.admin",
            "entitlement.teleport",
            "entitlement.tool.equip",
            "entitlement.tool.use",
            "entitlement.observer.truth",
            "ent.tool.logic_probe",
            "ent.tool.logic_trace",
            "ent.tool.teleport",
        ],
    }


def _teleport_chain_from_earth_scenario(scenario: Mapping[str, object] | None) -> list[dict]:
    scripts = [_as_map(row) for row in _as_list(_as_map(scenario).get("teleport_scripts"))]
    commands = ("/tp sol", "/tp earth", "/tp random_star")
    rows = []
    for command in commands:
        for row in scripts:
            if _token(row.get("command")) == command:
                rows.append(
                    {
                        "command": command,
                        "script_id": _token(row.get("script_id")),
                        "teleport_plan_fingerprint": _token(_as_map(row.get("teleport_plan")).get("deterministic_fingerprint")),
                        "target_kind": _token(_as_map(row.get("teleport_plan")).get("target_kind")),
                    }
                )
                break
    rows.append(copy.deepcopy(rows[1]) if len(rows) >= 2 else {"command": "/tp earth", "script_id": "tp.earth"})
    if len(rows) >= 4:
        rows[3]["command"] = "/tp earth"
        rows[3]["script_id"] = "tp.earth"
    return rows


def _build_tui_unavailable_record(repo_root: str) -> dict:
    previous = get_current_log_engine()
    logger = create_log_engine(
        product_id="mvp_smoke",
        build_id="mvp_smoke",
        session_id="tui_unavailable",
        console_enabled=False,
    )
    set_current_log_engine(logger)
    try:
        dispatch = run_tui_mode(repo_root, product_id="server", requested_layout_id="layout.server")
        payload = _as_map(dispatch.get("payload"))
        events = list(logger.ring_events())
    finally:
        set_current_log_engine(previous)
    event_keys = _sorted_tokens(_as_map(event).get("message_key") for event in events)
    record = {
        "result": "complete",
        "dispatch_kind": _token(dispatch.get("dispatch_kind")),
        "exit_code": int(dispatch.get("exit_code", 0) or 0),
        "compatibility_mode_id": _token(payload.get("compatibility_mode_id")),
        "effective_ui_mode": _token(payload.get("effective_mode_id")),
        "backend_id": _token(payload.get("backend_id")),
        "disabled_capability_ids": _sorted_tokens(_as_map(row).get("capability_id") for row in _as_list(payload.get("disabled_capabilities"))),
        "substituted_capability_ids": _sorted_tokens(_as_map(row).get("substitute_capability_id") for row in _as_list(payload.get("substituted_capabilities"))),
        "event_message_keys": event_keys,
        "degrade_logged": "appshell.tui.backend_degraded" in event_keys,
        "deterministic_fingerprint": "",
    }
    record["deterministic_fingerprint"] = canonical_sha256(dict(record, deterministic_fingerprint=""))
    return record


def _build_rendered_disabled_record(repo_root: str) -> dict:
    client_descriptor = build_default_endpoint_descriptor(
        repo_root,
        product_id="client",
        product_version="0.0.0+mvp.smoke.client",
    )
    server_descriptor = build_default_endpoint_descriptor(
        repo_root,
        product_id="server",
        product_version="0.0.0+mvp.smoke.server",
    )
    negotiation = negotiate_endpoint_descriptors(
        repo_root,
        client_descriptor,
        server_descriptor,
        chosen_contract_bundle_hash="hash.contract.bundle.mvp_smoke",
    )
    record = _as_map(negotiation.get("negotiation_record"))
    runtime_state = build_degrade_runtime_state(record)
    payload = {
        "result": _token(negotiation.get("result")) or "refused",
        "compatibility_mode_id": _token(record.get("compatibility_mode_id")),
        "negotiation_record_hash": _token(negotiation.get("negotiation_record_hash")),
        "effective_ui_mode": _token(runtime_state.get("effective_ui_mode")),
        "disabled_capability_ids": _sorted_tokens(_as_map(row).get("capability_id") for row in _as_list(record.get("disabled_capabilities"))),
        "substituted_capability_ids": _sorted_tokens(_as_map(row).get("substitute_capability_id") for row in _as_list(record.get("substituted_capabilities"))),
        "degrade_plan_rule_ids": _sorted_tokens(_as_map(row).get("rule_id") for row in _as_list(record.get("degrade_plan"))),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def run_logic_smoke_suite(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    inputs = load_eval_inputs(repo_root_abs)
    network_id = "net.logic.mvp.smoke"
    _, logic_network_state = make_chain_network(network_id=network_id, binding_extensions={"logic_policy_id": "logic.default"})

    def _compiled_case(toggle_value: int) -> dict:
        signal_store_state = seed_signal_requests(
            signal_store_state=None,
            signal_requests=[
                {
                    "tick": 0,
                    "network_id": network_id,
                    "element_id": "inst.logic.and.1",
                    "port_id": "in.a",
                    "signal_type_id": "signal.boolean",
                    "carrier_type_id": "carrier.electrical",
                    "value_payload": {"value": int(toggle_value)},
                },
                {
                    "tick": 0,
                    "network_id": network_id,
                    "element_id": "inst.logic.and.1",
                    "port_id": "in.b",
                    "signal_type_id": "signal.boolean",
                    "carrier_type_id": "carrier.electrical",
                    "value_payload": {"value": int(toggle_value)},
                },
            ],
            inputs=inputs,
        )
        scenario = {
            "logic_network_state": copy.deepcopy(logic_network_state),
            "signal_store_state": signal_store_state,
            "logic_eval_state": {},
            "state_vector_snapshot_rows": [],
            "evaluation_requests": [
                {"tick": 1, "network_id": network_id},
                {"tick": 2, "network_id": network_id},
            ],
        }
        return replay_compiled_logic_window_from_payload(repo_root=repo_root_abs, payload=scenario)

    off_report = _compiled_case(0)
    on_report = _compiled_case(1)

    authority_context = _mvp_authority_context()
    probe_task = build_logic_probe_task(
        authority_context=authority_context,
        subject_id=network_id,
        measurement_point_id="measure.logic.signal",
        network_id=network_id,
        element_id="inst.logic.and.1",
        port_id="out.q",
    )
    trace_task = build_logic_trace_task(
        authority_context=authority_context,
        subject_id=network_id,
        measurement_point_ids=["measure.logic.signal"],
        targets=[
            {
                "subject_id": network_id,
                "network_id": network_id,
                "element_id": "inst.logic.and.1",
                "port_id": "out.q",
                "measurement_point_id": "measure.logic.signal",
            }
        ],
        current_tick=1,
        duration_ticks=4,
    )
    debug_signal_store = seed_signal_requests(
        signal_store_state=None,
        signal_requests=[
            {
                "tick": 0,
                "network_id": network_id,
                "element_id": "inst.logic.and.1",
                "port_id": "out.q",
                "signal_type_id": "signal.boolean",
                "carrier_type_id": "carrier.electrical",
                "value_payload": {"value": 1},
            }
        ],
        inputs=inputs,
    )
    trace_payload = {
        "logic_network_state": {},
        "signal_store_state": debug_signal_store,
        "logic_eval_state": {},
        "compiled_model_rows": [],
        "state_vector_snapshot_rows": [],
        "probe_requests": [
            {
                "tick": 1,
                "probe_request": _as_map(probe_task.get("probe_request")),
                "authority_context": authority_context,
                "has_physical_access": True,
                "available_instrument_type_ids": ["instrument.logic_probe"],
                "compute_profile_id": "compute.default",
            }
        ],
        "trace_requests": [
            {
                "tick": 1,
                "trace_request": _as_map(trace_task.get("trace_request")),
                "authority_context": authority_context,
                "has_physical_access": True,
                "available_instrument_type_ids": ["instrument.logic_probe"],
                "compute_profile_id": "compute.default",
            }
        ],
    }
    trace_report = replay_trace_window_from_payload(repo_root=repo_root_abs, payload=trace_payload)
    stress_scenario = build_logic_debug_stress_scenario(repo_root=repo_root_abs, session_count=4, tick_count=4)
    stress_trace = replay_trace_window_from_payload(repo_root=repo_root_abs, payload=stress_scenario)

    payload = {
        "result": (
            "complete"
            if _token(off_report.get("result")) == "complete"
            and _token(on_report.get("result")) == "complete"
            and _token(trace_report.get("result")) == "complete"
            and _token(stress_trace.get("result")) == "complete"
            else "violation"
        ),
        "network_id": network_id,
        "toggle_off_final_signal_hash": _token(off_report.get("compiled_final_signal_hash")),
        "toggle_on_final_signal_hash": _token(on_report.get("compiled_final_signal_hash")),
        "compiled_model_hash": _token(on_report.get("compiled_model_hash_chain")) or _token(off_report.get("compiled_model_hash_chain")),
        "probe_artifact_count": int(trace_report.get("probe_artifact_count", 0) or 0),
        "trace_artifact_count": int(trace_report.get("trace_artifact_count", 0) or 0),
        "logic_debug_request_hash_chain": _token(stress_trace.get("logic_debug_request_hash_chain")) or _token(trace_report.get("logic_debug_request_hash_chain")),
        "logic_debug_trace_hash_chain": _token(stress_trace.get("logic_debug_trace_hash_chain")) or _token(trace_report.get("logic_debug_trace_hash_chain")),
        "logic_protocol_summary_hash_chain": _token(stress_trace.get("logic_protocol_summary_hash_chain")),
        "forced_expand_event_hash_chain": _token(stress_trace.get("forced_expand_event_hash_chain")) or _token(trace_report.get("forced_expand_event_hash_chain")),
        "compiled_toggle_reports": {
            "off": off_report,
            "on": on_report,
        },
        "probe_trace_report": trace_report,
        "stress_trace_report": stress_trace,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def run_server_window_with_pack_lock(
    repo_root: str,
    *,
    seed: int,
    ticks: int,
    save_suffix: str,
    pack_lock_path: str,
    with_client: bool = True,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    fixture = server_probe.boot_server_fixture(
        repo_root_abs,
        save_suffix=save_suffix,
        seed=int(seed),
        pack_lock_path=pack_lock_path,
    )
    boot = _as_map(fixture.get("boot"))
    if _token(boot.get("result")) != "complete":
        return {
            "result": _token(boot.get("result")) or "refused",
            "boot": boot,
            "session_spec_path": _relative_path(repo_root_abs, _token(fixture.get("session_spec_abs"))),
            "save_dir": _relative_path(repo_root_abs, _token(fixture.get("save_dir"))),
            "deterministic_fingerprint": canonical_sha256({"boot": boot, "ticks": int(ticks), "with_client": bool(with_client)}),
        }

    handshake = {"result": "empty"}
    client_transport = None
    if with_client:
        handshake = server_probe.connect_loopback_client(boot)
        if _token(handshake.get("result")) != "complete":
            return {
                "result": "refused",
                "boot": boot,
                "handshake": handshake,
                "session_spec_path": _relative_path(repo_root_abs, _token(fixture.get("session_spec_abs"))),
                "save_dir": _relative_path(repo_root_abs, _token(fixture.get("save_dir"))),
                "deterministic_fingerprint": canonical_sha256({"boot": boot, "handshake": handshake}),
            }
        client_transport = handshake.get("client_transport")

    tick_report = server_probe.run_server_ticks(boot, int(max(0, int(ticks or 0))))
    runtime = _as_map(boot.get("runtime"))
    server_runtime = _as_map(runtime.get("server"))
    meta = _as_map(runtime.get("server_mvp"))
    connections = _as_map(runtime.get("server_mvp_connections"))
    proof_anchor_rows = [dict(row) for row in _as_list(runtime.get("server_mvp_proof_anchors")) if isinstance(row, Mapping)]
    client_messages = server_probe.drain_client_messages(repo_root_abs, client_transport)
    tick_stream_messages = [
        row
        for row in client_messages
        if _token(_as_map(row).get("msg_type")) == "payload"
        and _token(_as_map(row).get("payload_schema_id")) == "server.tick_stream.stub.v1"
    ]
    summary = {
        "result": "complete" if _token(tick_report.get("result")) == "complete" else _token(tick_report.get("result")) or "refused",
        "save_id": _token(fixture.get("save_id")),
        "tick_count_requested": int(ticks),
        "final_tick": int(server_runtime.get("network_tick", 0) or 0),
        "listener_endpoint": _token(meta.get("listener_endpoint")),
        "client_count": len(connections),
        "connection_ids": sorted(_token(item) for item in connections.keys() if _token(item)),
        "handshake": {
            "connection_id": _token(_as_map(handshake.get("accepted")).get("connection_id")),
            "account_id": _token(_as_map(handshake.get("accepted")).get("account_id")),
            "compatibility_mode_id": _token(_as_map(handshake.get("accepted")).get("compatibility_mode_id")),
            "negotiation_record_hash": _token(_as_map(handshake.get("accepted")).get("negotiation_record_hash")),
            "session_info": _as_map(_as_map(_as_map(handshake.get("ack_proto")).get("payload_ref")).get("inline_json")).get("session_info", {}),
        },
        "proof_anchor_rows": proof_anchor_rows,
        "proof_anchor_ticks": [int(_as_map(row).get("tick", 0) or 0) for row in proof_anchor_rows],
        "proof_anchor_hashes": [canonical_sha256(row) for row in proof_anchor_rows],
        "proof_anchor_hashes_by_tick": {
            str(int(_as_map(row).get("tick", 0) or 0)): canonical_sha256(row)
            for row in proof_anchor_rows
        },
        "tick_stream_messages": tick_stream_messages,
        "tick_stream_ticks": [
            int(_as_map(_as_map(row).get("payload_ref")).get("inline_json", {}).get("tick", 0) or 0)
            for row in tick_stream_messages
        ],
        "tick_hash": _token(server_runtime.get("last_tick_hash")),
        "overlay_manifest_hash": _token(meta.get("overlay_manifest_hash")),
        "contract_bundle_hash": _token(meta.get("contract_bundle_hash")),
        "semantic_contract_registry_hash": _token(meta.get("semantic_contract_registry_hash")),
        "mod_policy_id": _token(meta.get("mod_policy_id")),
        "session_spec_path": _relative_path(repo_root_abs, _token(fixture.get("session_spec_abs"))),
        "save_dir": _relative_path(repo_root_abs, _token(fixture.get("save_dir"))),
        "pack_lock_path": _relative_path(repo_root_abs, pack_lock_path),
        "deterministic_fingerprint": "",
    }
    summary["cross_platform_server_hash"] = canonical_sha256(
        {
            "final_tick": int(summary.get("final_tick", 0)),
            "connection_ids": list(summary.get("connection_ids") or []),
            "proof_anchor_hashes": list(summary.get("proof_anchor_hashes") or []),
            "tick_hash": _token(summary.get("tick_hash")),
            "mod_policy_id": _token(summary.get("mod_policy_id")),
            "contract_bundle_hash": _token(summary.get("contract_bundle_hash")),
            "semantic_contract_registry_hash": _token(summary.get("semantic_contract_registry_hash")),
            "negotiation_record_hash": _token(_as_map(summary.get("handshake")).get("negotiation_record_hash")),
        }
    )
    summary["deterministic_fingerprint"] = canonical_sha256(dict(summary, deterministic_fingerprint=""))
    return summary


def generate_mvp_smoke_scenario(repo_root: str, seed: int = DEFAULT_MVP_SMOKE_SEED) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    earth_seed = _derived_seed(int(seed), "earth")
    server_seed = _derived_seed(int(seed), "server")
    earth_scenario = generate_earth_mvp_stress_scenario(repo_root=repo_root_abs, seed=int(earth_seed))
    teleport_chain = _teleport_chain_from_earth_scenario(earth_scenario)
    scenario = {
        "schema_version": "1.0.0",
        "scenario_id": "scenario.mvp.smoke.{}".format(canonical_sha256({"seed": int(seed)})[:12]),
        "scenario_seed": int(seed),
        "derived_seeds": {
            "earth_seed": int(earth_seed),
            "server_seed": int(server_seed),
        },
        "required_products": [
            "setup",
            "launcher",
            "appshell_supervisor",
            "client",
            "server",
            "earth",
            "logic",
            "diag",
        ],
        "phases": [
            {
                "phase_id": "A",
                "label": "Launch & Verify",
                "steps": [
                    {"kind": "wrapper", "bin_name": "setup", "command_tokens": ["verify"]},
                    {"kind": "wrapper", "bin_name": "launcher", "command_tokens": ["compat-status"]},
                    {"kind": "wrapper", "bin_name": "launcher", "command_tokens": ["packs", "build-lock"]},
                ],
            },
            {
                "phase_id": "B",
                "label": "Start Session",
                "steps": [
                    {
                        "kind": "wrapper",
                        "bin_name": "launcher",
                        "command_tokens": ["launcher", "start", "--seed", str(int(seed))],
                    }
                ],
            },
            {
                "phase_id": "C",
                "label": "Teleport Chain",
                "steps": [dict(row) for row in teleport_chain],
            },
            {
                "phase_id": "D",
                "label": "Earth Interactions",
                "steps": [
                    {"kind": "tool_session", "step_id": "scan", "task_id": "scan"},
                    {"kind": "tool_session", "step_id": "mine", "task_id": "mine"},
                    {"kind": "tool_session", "step_id": "fill", "task_id": "fill"},
                    {"kind": "earth", "step_id": "hydrology", "task_id": "verify_local_hydrology"},
                    {"kind": "earth", "step_id": "collision", "task_id": "verify_collision_after_edit"},
                ],
            },
            {
                "phase_id": "E",
                "label": "Logic Interaction",
                "steps": [
                    {"kind": "logic", "step_id": "toggle_output"},
                    {"kind": "logic", "step_id": "compile"},
                    {"kind": "logic", "step_id": "probe"},
                    {"kind": "logic", "step_id": "trace"},
                ],
            },
            {
                "phase_id": "F",
                "label": "Time Warp",
                "steps": [
                    {"kind": "earth", "step_id": "advance_1_day", "ticks": "1 day"},
                    {"kind": "earth", "step_id": "advance_30_days", "ticks": "30 days"},
                    {"kind": "earth", "step_id": "advance_365_days", "ticks": "365 days"},
                ],
            },
            {
                "phase_id": "G",
                "label": "Replay Verification",
                "steps": [
                    {"kind": "diag", "step_id": "capture_repro_bundle"},
                    {"kind": "diag", "step_id": "verify_replay_bundle"},
                ],
            },
        ],
        "teleport_chain": teleport_chain,
        "earth_scenario": earth_scenario,
        "expected_hashes_path": _norm(DEFAULT_HASHES_REL),
        "deterministic_fingerprint": "",
    }
    scenario["deterministic_fingerprint"] = canonical_sha256(dict(scenario, deterministic_fingerprint=""))
    return scenario


def _build_hash_summary(
    *,
    scenario: Mapping[str, object],
    setup_verify_payload: Mapping[str, object],
    compat_status_payload: Mapping[str, object],
    build_lock_payload: Mapping[str, object],
    earth_report: Mapping[str, object],
    earth_baseline: Mapping[str, object],
    tool_session_report: Mapping[str, object],
    logic_report: Mapping[str, object],
    degradations: Mapping[str, object],
    server_report: Mapping[str, object],
) -> dict:
    setup_report = _as_map(setup_verify_payload.get("report"))
    setup_lock = _as_map(setup_verify_payload.get("pack_lock"))
    compat_record = _as_map(compat_status_payload.get("negotiation_record"))
    build_lock_report = _as_map(build_lock_payload.get("report"))
    build_lock_lock = _as_map(build_lock_payload.get("pack_lock"))
    earth_proof = _as_map(earth_report.get("proof_summary"))
    earth_baseline_views = _as_map(earth_baseline.get("view_fingerprints"))
    tool_scan = _as_map(tool_session_report.get("scan"))
    tool_mine = _as_map(tool_session_report.get("mine"))
    tool_fill = _as_map(tool_session_report.get("fill"))
    tool_teleport = _as_map(tool_session_report.get("teleport"))
    return {
        "scenario_id": _token(scenario.get("scenario_id")),
        "scenario_fingerprint": _token(scenario.get("deterministic_fingerprint")),
        "setup_verify": {
            "valid": bool(setup_report.get("valid", False)),
            "report_fingerprint": _token(setup_report.get("deterministic_fingerprint")),
            "pack_lock_hash": _token(setup_lock.get("pack_lock_hash")),
            "warning_codes": _sorted_tokens(_as_map(row).get("code") for row in _as_list(setup_verify_payload.get("warnings"))),
            "error_codes": _sorted_tokens(_as_map(row).get("code") for row in _as_list(setup_verify_payload.get("errors"))),
        },
        "compat_status": {
            "compatibility_mode_id": _token(compat_status_payload.get("compatibility_mode_id")),
            "effective_ui_mode": _token(compat_status_payload.get("effective_ui_mode")),
            "negotiation_record_hash": _token(compat_status_payload.get("negotiation_record_hash")),
            "deterministic_fingerprint": _token(compat_status_payload.get("deterministic_fingerprint")),
            "disabled_capability_ids": _sorted_tokens(_as_map(row).get("capability_id") for row in _as_list(compat_record.get("disabled_capabilities"))),
            "substituted_capability_ids": _sorted_tokens(_as_map(row).get("substitute_capability_id") for row in _as_list(compat_record.get("substituted_capabilities"))),
        },
        "build_lock": {
            "valid": bool(build_lock_report.get("valid", False)),
            "report_fingerprint": _token(build_lock_report.get("deterministic_fingerprint")),
            "pack_lock_hash": _token(build_lock_lock.get("pack_lock_hash")),
            "warning_codes": _sorted_tokens(_as_map(row).get("code") for row in _as_list(build_lock_payload.get("warnings"))),
            "error_codes": _sorted_tokens(_as_map(row).get("code") for row in _as_list(build_lock_payload.get("errors"))),
        },
        "teleport_chain": [dict(row) for row in _as_list(scenario.get("teleport_chain"))],
        "earth": {
            "report_fingerprint": _token(earth_report.get("deterministic_fingerprint")),
            "cross_platform_determinism_hash": _token(earth_proof.get("cross_platform_determinism_hash")),
            "hydrology_flow_hash": _token(earth_proof.get("hydrology_flow_hash")),
            "collision_final_state_hash": _token(earth_proof.get("collision_final_state_hash")),
            "climate_overlay_hash_a": _token(_as_map(earth_baseline.get("climate_snapshots")).get("season_a", {}).get("overlay_hash")),
            "climate_overlay_hash_b": _token(_as_map(earth_baseline.get("climate_snapshots")).get("season_b", {}).get("overlay_hash")),
            "tide_window_hash": _token(_as_map(earth_baseline.get("tide_snapshot")).get("window_hash")),
            "water_hash": _token(_as_map(earth_baseline.get("water_snapshot")).get("water_hash")),
            "selected_view_fingerprints": dict(sorted(earth_baseline_views.items(), key=lambda item: item[0])),
        },
        "tool_session": {
            "report_fingerprint": _token(tool_session_report.get("deterministic_fingerprint")),
            "scan_fingerprint": _token(tool_scan.get("deterministic_fingerprint")),
            "mine_fingerprint": _token(tool_mine.get("deterministic_fingerprint")),
            "fill_fingerprint": _token(tool_fill.get("deterministic_fingerprint")),
            "teleport_fingerprint": _token(tool_teleport.get("deterministic_fingerprint")),
        },
        "logic": {
            "report_fingerprint": _token(logic_report.get("deterministic_fingerprint")),
            "compiled_model_hash": _token(logic_report.get("compiled_model_hash")),
            "toggle_off_final_signal_hash": _token(logic_report.get("toggle_off_final_signal_hash")),
            "toggle_on_final_signal_hash": _token(logic_report.get("toggle_on_final_signal_hash")),
            "logic_debug_request_hash_chain": _token(logic_report.get("logic_debug_request_hash_chain")),
            "logic_debug_trace_hash_chain": _token(logic_report.get("logic_debug_trace_hash_chain")),
            "logic_protocol_summary_hash_chain": _token(logic_report.get("logic_protocol_summary_hash_chain")),
            "forced_expand_event_hash_chain": _token(logic_report.get("forced_expand_event_hash_chain")),
        },
        "degradations": {
            "tui_unavailable": dict(_as_map(degradations.get("tui_unavailable"))),
            "rendered_disabled": dict(_as_map(degradations.get("rendered_disabled"))),
        },
        "server_probe": {
            "report_fingerprint": _token(server_report.get("deterministic_fingerprint")),
            "cross_platform_server_hash": _token(server_report.get("cross_platform_server_hash")),
            "negotiation_record_hash": _token(_as_map(server_report.get("handshake")).get("negotiation_record_hash")),
            "proof_anchor_hashes_by_tick": dict(sorted(_as_map(server_report.get("proof_anchor_hashes_by_tick")).items(), key=lambda item: item[0])),
        },
        "deterministic_fingerprint": "",
    }


def build_expected_hash_fingerprints(
    repo_root: str,
    seed: int = DEFAULT_MVP_SMOKE_SEED,
    scenario: Mapping[str, object] | None = None,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    scenario_payload = _as_map(scenario) or generate_mvp_smoke_scenario(repo_root_abs, seed=int(seed))
    curated_runtime = build_curated_pack_runtime(repo_root_abs)
    runtime_artifacts = build_smoke_runtime_artifacts(repo_root_abs, curated_runtime=curated_runtime)

    setup_verify = _run_wrapper(
        repo_root_abs,
        "setup",
        [
            "verify",
            "--root",
            _token(curated_runtime.get("curated_root")),
            "--out-report",
            _norm(SETUP_VERIFY_REPORT_REL),
            "--out-lock",
            _norm(SETUP_VERIFY_LOCK_REL),
            "--write-outputs",
        ],
    )
    compat_status = _run_wrapper(repo_root_abs, "launcher", ["compat-status"])
    build_lock = _run_wrapper(
        repo_root_abs,
        "launcher",
        [
            "packs",
            "build-lock",
            "--root",
            _token(curated_runtime.get("curated_root")),
            "--out-report",
            _norm(LAUNCHER_BUILD_LOCK_REPORT_REL),
            "--out-lock",
            _norm(LAUNCHER_BUILD_LOCK_LOCK_REL),
        ],
    )
    earth_seed = int(_as_map(scenario_payload.get("derived_seeds")).get("earth_seed", 0) or 0)
    earth_report = verify_earth_mvp_stress_scenario(
        repo_root=repo_root_abs,
        scenario=_as_map(scenario_payload.get("earth_scenario")),
        seed=int(earth_seed),
    )
    earth_baseline = build_earth_mvp_regression_baseline(
        repo_root=repo_root_abs,
        scenario=_as_map(scenario_payload.get("earth_scenario")),
        seed=int(earth_seed),
    )
    tool_session_report = build_tool_session_report(repo_root_abs)
    logic_report = run_logic_smoke_suite(repo_root_abs)
    degradations = {
        "tui_unavailable": _build_tui_unavailable_record(repo_root_abs),
        "rendered_disabled": _build_rendered_disabled_record(repo_root_abs),
    }
    server_report = run_server_window_with_pack_lock(
        repo_root_abs,
        seed=int(_as_map(scenario_payload.get("derived_seeds")).get("server_seed", 0) or 0),
        ticks=int(DEFAULT_SERVER_TICKS),
        save_suffix=DEFAULT_SERVER_SAVE_SUFFIX,
        pack_lock_path=_token(runtime_artifacts.get("pack_lock_path")),
    )
    summary = _build_hash_summary(
        scenario=scenario_payload,
        setup_verify_payload=_as_map(setup_verify.get("payload")),
        compat_status_payload=_as_map(compat_status.get("payload")),
        build_lock_payload=_as_map(build_lock.get("payload")),
        earth_report=earth_report,
        earth_baseline=earth_baseline,
        tool_session_report=tool_session_report,
        logic_report=logic_report,
        degradations=degradations,
        server_report=server_report,
    )
    expected = {
        "schema_version": "1.0.0",
        "scenario_id": _token(scenario_payload.get("scenario_id")),
        "scenario_seed": int(seed),
        "pack_lock_hash": _token(_as_map(build_lock.get("payload")).get("pack_lock", {}).get("pack_lock_hash"))
        or _token(curated_runtime.get("pack_lock_hash")),
        "runtime_artifacts": {
            "curated_root": _token(curated_runtime.get("curated_root")),
            "profile_bundle_path": _token(runtime_artifacts.get("profile_bundle_path")),
            "session_template_path": _token(runtime_artifacts.get("session_template_path")),
            "pack_lock_path": _token(runtime_artifacts.get("pack_lock_path")),
        },
        "hash_summary": summary,
        "deterministic_fingerprint": "",
    }
    expected["deterministic_fingerprint"] = canonical_sha256(dict(expected, deterministic_fingerprint=""))
    return expected


def _collect_mismatch_rows(expected: object, actual: object, path: str = "$") -> list[dict]:
    if isinstance(expected, Mapping) and isinstance(actual, Mapping):
        keys = sorted(set(str(key) for key in expected.keys()) | set(str(key) for key in actual.keys()))
        rows = []
        for key in keys:
            rows.extend(
                _collect_mismatch_rows(
                    _as_map(expected).get(key),
                    _as_map(actual).get(key),
                    path="{}.{}".format(path, key),
                )
            )
        return rows
    if isinstance(expected, list) and isinstance(actual, list):
        rows = []
        max_len = max(len(expected), len(actual))
        for index in range(max_len):
            exp = expected[index] if index < len(expected) else None
            act = actual[index] if index < len(actual) else None
            rows.extend(_collect_mismatch_rows(exp, act, path="{}[{}]".format(path, index)))
        return rows
    if expected == actual:
        return []
    return [{"path": path, "expected": expected, "actual": actual}]


def _assert_degrade_is_explicit(record: Mapping[str, object] | None, *, require_logged: bool = False) -> dict:
    row = _as_map(record)
    disabled_ids = _sorted_tokens(row.get("disabled_capability_ids"))
    substituted_ids = _sorted_tokens(row.get("substituted_capability_ids"))
    explicit = bool(_token(row.get("compatibility_mode_id"))) and (bool(disabled_ids) or bool(substituted_ids))
    logged = (not require_logged) or bool(row.get("degrade_logged", False))
    return {
        "explicit": bool(explicit),
        "logged": bool(logged),
        "disabled_capability_ids": disabled_ids,
        "substituted_capability_ids": substituted_ids,
        "deterministic_fingerprint": canonical_sha256(
            {
                "explicit": bool(explicit),
                "logged": bool(logged),
                "disabled_capability_ids": disabled_ids,
                "substituted_capability_ids": substituted_ids,
            }
        ),
    }


def write_generated_mvp_smoke_inputs(
    repo_root: str,
    *,
    seed: int = DEFAULT_MVP_SMOKE_SEED,
    scenario_path: str = "",
    hashes_path: str = "",
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    scenario_payload = generate_mvp_smoke_scenario(repo_root_abs, seed=int(seed))
    expected_hashes = build_expected_hash_fingerprints(repo_root_abs, seed=int(seed), scenario=scenario_payload)
    scenario_abs = _repo_abs(repo_root_abs, scenario_path or DEFAULT_SCENARIO_REL)
    hashes_abs = _repo_abs(repo_root_abs, hashes_path or DEFAULT_HASHES_REL)
    _write_canonical_json(scenario_abs, scenario_payload)
    _write_canonical_json(hashes_abs, expected_hashes)
    return {
        "result": "complete",
        "scenario_path": _relative_path(repo_root_abs, scenario_abs),
        "hashes_path": _relative_path(repo_root_abs, hashes_abs),
        "scenario": scenario_payload,
        "expected_hashes": expected_hashes,
        "deterministic_fingerprint": canonical_sha256(
            {
                "scenario_path": _relative_path(repo_root_abs, scenario_abs),
                "hashes_path": _relative_path(repo_root_abs, hashes_abs),
                "scenario_fingerprint": _token(scenario_payload.get("deterministic_fingerprint")),
                "hashes_fingerprint": _token(expected_hashes.get("deterministic_fingerprint")),
            }
        ),
    }


def _count_refused_results(*rows: Mapping[str, object] | None) -> int:
    count = 0
    for row in rows:
        if _token(_as_map(row).get("result")) == "refused":
            count += 1
    return count


def run_mvp_smoke(
    repo_root: str,
    *,
    seed: int = DEFAULT_MVP_SMOKE_SEED,
    scenario: Mapping[str, object] | None = None,
    expected_hashes: Mapping[str, object] | None = None,
    baseline_payload: Mapping[str, object] | None = None,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    scenario_payload = _as_map(scenario) or generate_mvp_smoke_scenario(repo_root_abs, seed=int(seed))
    expected_payload = _as_map(expected_hashes) or build_expected_hash_fingerprints(
        repo_root_abs,
        seed=int(seed),
        scenario=scenario_payload,
    )
    curated_runtime = build_curated_pack_runtime(repo_root_abs)
    runtime_artifacts = build_smoke_runtime_artifacts(repo_root_abs, curated_runtime=curated_runtime)

    command_results: dict[str, dict] = {}
    stop_result = {}
    started = False
    endpoint_ids = {}
    try:
        command_results["setup_verify"] = _run_wrapper(
            repo_root_abs,
            "setup",
            [
                "verify",
                "--root",
                _token(curated_runtime.get("curated_root")),
                "--out-report",
                _norm(SETUP_VERIFY_REPORT_REL),
                "--out-lock",
                _norm(SETUP_VERIFY_LOCK_REL),
                "--write-outputs",
            ],
        )
        command_results["compat_status"] = _run_wrapper(repo_root_abs, "launcher", ["compat-status"])
        command_results["build_lock"] = _run_wrapper(
            repo_root_abs,
            "launcher",
            [
                "packs",
                "build-lock",
                "--root",
                _token(curated_runtime.get("curated_root")),
                "--out-report",
                _norm(LAUNCHER_BUILD_LOCK_REPORT_REL),
                "--out-lock",
                _norm(LAUNCHER_BUILD_LOCK_LOCK_REL),
            ],
        )
        command_results["launcher_start"] = _run_wrapper(
            repo_root_abs,
            "launcher",
            [
                "launcher",
                "start",
                "--seed",
                str(int(seed)),
                "--session-template-path",
                _token(runtime_artifacts.get("session_template_path")),
                "--profile-bundle-path",
                _token(runtime_artifacts.get("profile_bundle_path")),
                "--pack-lock-path",
                _token(runtime_artifacts.get("pack_lock_path")),
            ],
        )
        started = _token(_as_map(command_results["launcher_start"].get("payload")).get("result")) == "complete"
        command_results["launcher_status"] = _run_wrapper(repo_root_abs, "launcher", ["launcher", "status"])
        endpoint_ids = _extract_process_endpoint_ids(_as_map(command_results["launcher_status"].get("payload")))
        if _token(endpoint_ids.get("client")):
            command_results["launcher_attach_client"] = _run_wrapper(
                repo_root_abs,
                "launcher",
                ["console", "attach", "--endpoint-id", _token(endpoint_ids.get("client"))],
            )
        else:
            command_results["launcher_attach_client"] = {
                "command": "launcher console attach --endpoint-id <missing client>",
                "returncode": 1,
                "stdout": "",
                "stderr": "",
                "payload": _failure_result("refused", "missing client endpoint id"),
            }
        if _token(endpoint_ids.get("server")):
            command_results["launcher_attach_server"] = _run_wrapper(
                repo_root_abs,
                "launcher",
                ["console", "attach", "--endpoint-id", _token(endpoint_ids.get("server"))],
            )
        else:
            command_results["launcher_attach_server"] = {
                "command": "launcher console attach --endpoint-id <missing server>",
                "returncode": 1,
                "stdout": "",
                "stderr": "",
                "payload": _failure_result("refused", "missing server endpoint id"),
            }
    finally:
        if started:
            stop_result = _run_wrapper(repo_root_abs, "launcher", ["launcher", "stop"])
        else:
            stop_result = {"command": "launcher launcher stop", "returncode": 0, "stdout": "", "stderr": "", "payload": {"result": "skipped"}}
        command_results["launcher_stop"] = stop_result

    earth_seed = int(_as_map(scenario_payload.get("derived_seeds")).get("earth_seed", 0) or 0)
    earth_report = verify_earth_mvp_stress_scenario(
        repo_root=repo_root_abs,
        scenario=_as_map(scenario_payload.get("earth_scenario")),
        seed=int(earth_seed),
    )
    earth_baseline = build_earth_mvp_regression_baseline(
        repo_root=repo_root_abs,
        scenario=_as_map(scenario_payload.get("earth_scenario")),
        seed=int(earth_seed),
    )
    tool_session_report = build_tool_session_report(repo_root_abs)
    logic_report = run_logic_smoke_suite(repo_root_abs)
    degradations = {
        "tui_unavailable": _build_tui_unavailable_record(repo_root_abs),
        "rendered_disabled": _build_rendered_disabled_record(repo_root_abs),
    }
    server_report = run_server_window_with_pack_lock(
        repo_root_abs,
        seed=int(_as_map(scenario_payload.get("derived_seeds")).get("server_seed", 0) or 0),
        ticks=int(DEFAULT_SERVER_TICKS),
        save_suffix=DEFAULT_SERVER_SAVE_SUFFIX,
        pack_lock_path=_token(runtime_artifacts.get("pack_lock_path")),
    )

    client_attach_payload = _as_map(_as_map(command_results.get("launcher_attach_client")).get("payload"))
    server_attach_payload = _as_map(_as_map(command_results.get("launcher_attach_server")).get("payload"))
    client_attach = _as_map(client_attach_payload.get("attach"))
    server_attach = _as_map(server_attach_payload.get("attach"))
    compat_status_payload = _as_map(_as_map(command_results.get("compat_status")).get("payload"))
    launcher_status_payload = _as_map(_as_map(command_results.get("launcher_status")).get("payload"))
    launcher_stop_payload = _as_map(_as_map(command_results.get("launcher_stop")).get("payload"))

    canonical_event_rows = [
        dict(row)
        for row in _as_list(server_report.get("tick_stream_messages"))
        if isinstance(row, Mapping)
    ] or [
        {"tick": _as_int(_as_map(row).get("tick"), 0), "proof_anchor_hash": canonical_sha256(row)}
        for row in _as_list(server_report.get("proof_anchor_rows"))
        if isinstance(row, Mapping)
    ]
    log_events = [dict(row) for row in _as_list(launcher_status_payload.get("latest_logs")) if isinstance(row, Mapping)]
    log_events.extend(dict(row) for row in _as_list(launcher_stop_payload.get("latest_logs")) if isinstance(row, Mapping))
    log_events.extend(dict(row) for row in _as_list(client_attach_payload.get("log_events")) if isinstance(row, Mapping))
    log_events.extend(dict(row) for row in _as_list(server_attach_payload.get("log_events")) if isinstance(row, Mapping))
    ipc_attach_rows = [dict(client_attach), dict(server_attach)]
    negotiation_records = [
        _as_map(compat_status_payload.get("negotiation_record")),
        _as_map(client_attach.get("negotiation_record")),
        _as_map(server_attach.get("negotiation_record")),
    ]
    negotiation_records = [row for row in negotiation_records if row]
    view_fingerprints = [
        {"view_id": str(key), "fingerprint": str(value)}
        for key, value in sorted(_as_map(earth_baseline.get("view_fingerprints")).items(), key=lambda item: item[0])
    ]
    for season_key, row in sorted(_as_map(earth_baseline.get("climate_snapshots")).items(), key=lambda item: item[0]):
        row_map = _as_map(row)
        view_fingerprints.append(
            {
                "view_id": "climate.{}".format(season_key),
                "fingerprint": _token(row_map.get("overlay_hash")),
            }
        )
    view_fingerprints.append(
        {
            "view_id": "tide.window",
            "fingerprint": _token(_as_map(earth_baseline.get("tide_snapshot")).get("window_hash")),
        }
    )
    diag_bundle = write_repro_bundle(
        repo_root=repo_root_abs,
        created_by_product_id="mvp_smoke",
        out_dir=_repo_abs(repo_root_abs, DIAG_BUNDLE_DIR_REL),
        window=DEFAULT_CAPTURE_WINDOW,
        include_views=True,
        run_manifest_path=_token(_as_map(_as_map(command_results.get("launcher_start")).get("payload")).get("run_manifest_path")),
        session_spec_path=_token(server_report.get("session_spec_path")),
        pack_lock_path=_token(runtime_artifacts.get("pack_lock_path")),
        semantic_contract_registry_hash=_token(server_report.get("semantic_contract_registry_hash")),
        contract_bundle_hash=_token(server_report.get("contract_bundle_hash")),
        overlay_manifest_hash=_token(server_report.get("overlay_manifest_hash")),
        seed=str(int(seed)),
        session_id=_token(server_report.get("save_id")),
        session_template_id=_token(_as_map(runtime_artifacts.get("session_template_payload")).get("template_id")),
        proof_anchor_rows=_as_list(server_report.get("proof_anchor_rows")),
        canonical_event_rows=canonical_event_rows,
        log_events=log_events,
        ipc_attach_rows=ipc_attach_rows,
        negotiation_records=negotiation_records,
        view_fingerprints=view_fingerprints,
    )
    diag_verify = verify_repro_bundle(
        repo_root=repo_root_abs,
        bundle_path=_token(diag_bundle.get("bundle_dir")),
        tick_window=DEFAULT_CAPTURE_WINDOW,
    )

    actual_hash_summary = _build_hash_summary(
        scenario=scenario_payload,
        setup_verify_payload=_as_map(command_results["setup_verify"].get("payload")),
        compat_status_payload=compat_status_payload,
        build_lock_payload=_as_map(command_results["build_lock"].get("payload")),
        earth_report=earth_report,
        earth_baseline=earth_baseline,
        tool_session_report=tool_session_report,
        logic_report=logic_report,
        degradations=degradations,
        server_report=server_report,
    )
    expected_hash_comparison = {
        "match": False,
        "mismatches": [],
        "deterministic_fingerprint": "",
    }
    expected_summary = _as_map(expected_payload.get("hash_summary"))
    expected_hash_comparison["mismatches"] = _collect_mismatch_rows(expected_summary, actual_hash_summary)
    expected_hash_comparison["match"] = not bool(expected_hash_comparison["mismatches"])
    expected_hash_comparison["deterministic_fingerprint"] = canonical_sha256(
        dict(expected_hash_comparison, deterministic_fingerprint="")
    )

    command_summaries = {
        key: _command_summary(value)
        for key, value in sorted(command_results.items(), key=lambda item: item[0])
    }
    degrade_checks = {
        "tui_unavailable": _assert_degrade_is_explicit(_as_map(degradations.get("tui_unavailable")), require_logged=True),
        "rendered_disabled": _assert_degrade_is_explicit(_as_map(degradations.get("rendered_disabled")), require_logged=False),
    }
    refusal_count = _count_refused_results(
        compat_status_payload,
        _as_map(command_results["setup_verify"].get("payload")),
        _as_map(command_results["build_lock"].get("payload")),
        _as_map(command_results["launcher_start"].get("payload")),
        launcher_status_payload,
        client_attach_payload,
        server_attach_payload,
        launcher_stop_payload,
        earth_report,
        logic_report,
        server_report,
        diag_verify,
    )
    diag_replay = _as_map(diag_verify.get("replay_result"))
    teleport_chain = [dict(row) for row in _as_list(scenario_payload.get("teleport_chain"))]
    actual_teleport_commands = [str(_as_map(row).get("command", "")).strip() for row in teleport_chain]
    assertions = {
        "setup_verify_complete": int(command_results["setup_verify"].get("returncode", 0)) == 0
        and _token(_as_map(command_results["setup_verify"].get("payload")).get("result")) == "complete"
        and bool(_as_map(_as_map(command_results["setup_verify"].get("payload")).get("report")).get("valid", False)),
        "compat_status_complete": int(command_results["compat_status"].get("returncode", 0)) == 0
        and _token(compat_status_payload.get("result")) == "complete",
        "build_lock_complete": int(command_results["build_lock"].get("returncode", 0)) == 0
        and _token(_as_map(command_results["build_lock"].get("payload")).get("result")) == "complete"
        and bool(_as_map(_as_map(command_results["build_lock"].get("payload")).get("report")).get("valid", False)),
        "launcher_lifecycle_complete": int(command_results["launcher_start"].get("returncode", 0)) == 0
        and _token(_as_map(command_results["launcher_start"].get("payload")).get("result")) == "complete"
        and int(command_results["launcher_status"].get("returncode", 0)) == 0
        and _token(launcher_status_payload.get("result")) == "complete"
        and int(command_results["launcher_stop"].get("returncode", 0)) == 0
        and _token(launcher_stop_payload.get("result")) in ("complete", "skipped"),
        "launcher_pack_lock_pinned": _token(_as_map(_as_map(command_results["launcher_start"].get("payload")).get("run_spec")).get("pack_lock_hash"))
        == _token(runtime_artifacts.get("pack_lock_hash")),
        "launcher_client_attach_explicit": int(command_results["launcher_attach_client"].get("returncode", 0)) == 0
        and _token(client_attach.get("compatibility_mode_id")) == "compat.degraded"
        and bool(degrade_checks["rendered_disabled"].get("explicit", False)),
        "launcher_server_attach_full": int(command_results["launcher_attach_server"].get("returncode", 0)) == 0
        and _token(server_attach.get("compatibility_mode_id")) == "compat.full",
        "teleport_chain_deterministic": actual_teleport_commands == ["/tp sol", "/tp earth", "/tp random_star", "/tp earth"],
        "earth_complete": _token(earth_report.get("result")) == "complete" and bool(earth_report.get("stable_across_repeated_runs", False)),
        "tool_session_complete": bool(_token(tool_session_report.get("deterministic_fingerprint"))),
        "logic_complete": _token(logic_report.get("result")) == "complete"
        and _token(logic_report.get("toggle_off_final_signal_hash")) != _token(logic_report.get("toggle_on_final_signal_hash")),
        "tui_unavailable_explicit": bool(degrade_checks["tui_unavailable"].get("explicit", False))
        and bool(degrade_checks["tui_unavailable"].get("logged", False)),
        "rendered_disabled_explicit": bool(degrade_checks["rendered_disabled"].get("explicit", False))
        and _token(_as_map(degradations.get("rendered_disabled")).get("effective_ui_mode")) in ("tui", "cli"),
        "server_probe_complete": _token(server_report.get("result")) == "complete"
        and bool(_as_map(server_report.get("proof_anchor_hashes_by_tick"))),
        "diag_replay_valid": _token(diag_verify.get("result")) == "complete"
        and bool(diag_replay.get("hash_match", False))
        and bool(diag_replay.get("proof_hash_match", False)),
        "expected_hashes_match": bool(expected_hash_comparison.get("match", False)),
        "no_refusals": int(refusal_count) == 0,
    }

    report = {
        "result": "complete" if all(bool(value) for value in assertions.values()) else "violation",
        "scenario_id": _token(scenario_payload.get("scenario_id")),
        "scenario_seed": int(seed),
        "scenario_fingerprint": _token(scenario_payload.get("deterministic_fingerprint")),
        "expected_hashes_fingerprint": _token(expected_payload.get("deterministic_fingerprint")),
        "scenario": scenario_payload,
        "expected_hashes": expected_payload,
        "curated_runtime": curated_runtime,
        "smoke_runtime": runtime_artifacts,
        "command_results": command_results,
        "command_summaries": command_summaries,
        "endpoint_ids": endpoint_ids,
        "launcher_attach_hashes": {
            "compat_status": _token(compat_status_payload.get("negotiation_record_hash")),
            "client": _token(client_attach.get("negotiation_record_hash")),
            "server": _token(server_attach.get("negotiation_record_hash")),
            "server_probe": _token(_as_map(server_report.get("handshake")).get("negotiation_record_hash")),
        },
        "teleport_chain": teleport_chain,
        "earth": earth_report,
        "earth_baseline": earth_baseline,
        "tool_session": tool_session_report,
        "logic": logic_report,
        "degradations": degradations,
        "degradation_summary": {
            "tui_unavailable": {
                "compatibility_mode_id": _token(_as_map(degradations.get("tui_unavailable")).get("compatibility_mode_id")),
                "effective_ui_mode": _token(_as_map(degradations.get("tui_unavailable")).get("effective_ui_mode")),
                "degrade_logged": bool(_as_map(degradations.get("tui_unavailable")).get("degrade_logged", False)),
            },
            "rendered_disabled": {
                "compatibility_mode_id": _token(_as_map(degradations.get("rendered_disabled")).get("compatibility_mode_id")),
                "effective_ui_mode": _token(_as_map(degradations.get("rendered_disabled")).get("effective_ui_mode")),
            },
        },
        "server_probe": server_report,
        "diag_bundle": diag_bundle,
        "diag_verify": diag_verify,
        "actual_hash_summary": actual_hash_summary,
        "expected_hash_comparison": expected_hash_comparison,
        "refusal_count": int(refusal_count),
        "assertions": assertions,
        "deterministic_fingerprint": "",
    }
    baseline_candidate = build_mvp_smoke_baseline(report)
    report["baseline_candidate"] = baseline_candidate
    baseline_comparison = {
        "checked": bool(baseline_payload),
        "match": False,
        "mismatches": [],
        "deterministic_fingerprint": "",
    }
    if baseline_payload:
        baseline_comparison["mismatches"] = _collect_mismatch_rows(_as_map(baseline_payload), baseline_candidate)
        baseline_comparison["match"] = not bool(baseline_comparison["mismatches"])
    baseline_comparison["deterministic_fingerprint"] = canonical_sha256(
        dict(baseline_comparison, deterministic_fingerprint="")
    )
    report["baseline_comparison"] = baseline_comparison
    if bool(baseline_payload):
        report["assertions"]["baseline_match"] = bool(baseline_comparison.get("match", False))
        report["result"] = "complete" if all(bool(value) for value in report["assertions"].values()) else "violation"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def build_mvp_smoke_baseline(report: Mapping[str, object] | None) -> dict:
    payload = _as_map(report)
    actual_hash_summary = _as_map(payload.get("actual_hash_summary"))
    earth_baseline = _as_map(payload.get("earth_baseline"))
    diag_bundle = _as_map(payload.get("diag_bundle"))
    diag_manifest = _as_map(diag_bundle.get("manifest"))
    launcher_attach_hashes = _as_map(payload.get("launcher_attach_hashes"))
    smoke_runtime = _as_map(payload.get("smoke_runtime"))
    expected_hashes = _as_map(payload.get("expected_hashes"))
    verification_pack_lock_hash = (
        _token(_as_map(actual_hash_summary.get("build_lock")).get("pack_lock_hash"))
        or _token(smoke_runtime.get("verification_pack_lock_hash"))
        or _token(_as_map(expected_hashes.get("hash_summary")).get("build_lock", {}).get("pack_lock_hash"))
    )
    baseline = {
        "schema_version": "1.0.0",
        "baseline_id": "mvp.smoke.baseline.v1",
        "description": "Deterministic regression lock for the v0.0.0 MVP smoke lane.",
        "scenario_seed": int(payload.get("scenario_seed", DEFAULT_MVP_SMOKE_SEED) or DEFAULT_MVP_SMOKE_SEED),
        "scenario_id": _token(payload.get("scenario_id")),
        "scenario_fingerprint": _token(payload.get("scenario_fingerprint")),
        "pack_lock_hash": verification_pack_lock_hash,
        "runtime_pack_lock_hash": _token(smoke_runtime.get("pack_lock_hash")),
        "negotiation_record_hashes": {
            "compat_status": _token(launcher_attach_hashes.get("compat_status")),
            "launcher_client_attach": _token(launcher_attach_hashes.get("client")),
            "launcher_server_attach": _token(launcher_attach_hashes.get("server")),
            "server_probe": _token(launcher_attach_hashes.get("server_probe")),
        },
        "proof_anchor_hashes": dict(sorted(_as_map(_as_map(payload.get("server_probe")).get("proof_anchor_hashes_by_tick")).items(), key=lambda item: item[0])),
        "logic_compiled_model_hash": _token(_as_map(payload.get("logic")).get("compiled_model_hash")),
        "selected_view_fingerprints": {
            **dict(sorted(_as_map(earth_baseline.get("view_fingerprints")).items(), key=lambda item: item[0])),
            "climate_season_a": _token(_as_map(_as_map(earth_baseline.get("climate_snapshots")).get("season_a")).get("overlay_hash")),
            "climate_season_b": _token(_as_map(_as_map(earth_baseline.get("climate_snapshots")).get("season_b")).get("overlay_hash")),
            "tide_window": _token(_as_map(earth_baseline.get("tide_snapshot")).get("window_hash")),
        },
        "replay_bundle_hashes": {
            "bundle_hash": _token(diag_bundle.get("bundle_hash")),
            "manifest_fingerprint": _token(diag_manifest.get("deterministic_fingerprint")),
            "proof_window_hash": _token(diag_manifest.get("proof_window_hash")),
        },
        "degradation_summary": dict(_as_map(payload.get("degradation_summary"))),
        "update_policy": {
            "required_commit_tag": MVP_SMOKE_REGRESSION_UPDATE_TAG,
            "notes": "Updating the MVP smoke regression lock requires explicit review under MVP-SMOKE-REGRESSION-UPDATE.",
        },
        "deterministic_fingerprint": "",
    }
    baseline["deterministic_fingerprint"] = canonical_sha256(dict(baseline, deterministic_fingerprint=""))
    return baseline


def render_mvp_smoke_final_markdown(
    report: Mapping[str, object] | None,
    *,
    baseline: Mapping[str, object] | None = None,
    gate_results: Mapping[str, object] | None = None,
) -> str:
    row = _as_map(report)
    base = _as_map(baseline)
    gates = _as_map(gate_results)
    hashes = _as_map(row.get("actual_hash_summary"))
    degradation_summary = _as_map(row.get("degradation_summary"))
    readiness = (
        "Ready for MVP-GATE-1 stress and RELEASE series."
        if _token(row.get("result")) == "complete"
        and all(_token(_as_map(gates.get(key)).get("status")) == "PASS" for key in ("repox", "auditx", "testx", "smoke"))
        else "Not ready for MVP-GATE-1 stress or RELEASE series."
    )

    def _gate_line(label: str, key: str) -> str:
        gate = _as_map(gates.get(key))
        status = _token(gate.get("status")) or "NOT_RUN"
        note = _token(gate.get("note"))
        suffix = " ({})".format(note) if note else ""
        return "- {}: `{}`{}".format(label, status, suffix)

    lines = [
        "# MVP Smoke Final",
        "",
        "## Run Summary",
        "",
        "- result: `{}`".format(_token(row.get("result")) or "unknown"),
        "- scenario_id: `{}`".format(_token(row.get("scenario_id"))),
        "- scenario_seed: `{}`".format(int(row.get("scenario_seed", DEFAULT_MVP_SMOKE_SEED) or DEFAULT_MVP_SMOKE_SEED)),
        "- refusal_count: `{}`".format(int(row.get("refusal_count", 0) or 0)),
        "- deterministic_fingerprint: `{}`".format(_token(row.get("deterministic_fingerprint"))),
        "- readiness: {}".format(readiness),
        "",
        "## Hashes",
        "",
        "- pack_lock_hash: `{}`".format(_token(_as_map(hashes.get("build_lock")).get("pack_lock_hash"))),
        "- smoke_runtime pack_lock_hash: `{}`".format(
            _token(_as_map(row.get("smoke_runtime")).get("pack_lock_hash"))
        ),
        "- compat_status negotiation hash: `{}`".format(_token(_as_map(hashes.get("compat_status")).get("negotiation_record_hash"))),
        "- server proof anchors: `{}`".format(_token(_as_map(hashes.get("server_probe")).get("report_fingerprint"))),
        "- logic compiled model hash: `{}`".format(_token(_as_map(hashes.get("logic")).get("compiled_model_hash"))),
        "- replay bundle hash: `{}`".format(_token(_as_map(row.get("diag_bundle")).get("bundle_hash"))),
        "",
        "## Degradations",
        "",
        "- rendered_disabled: `{}` -> `{}`".format(
            _token(_as_map(degradation_summary.get("rendered_disabled")).get("compatibility_mode_id")),
            _token(_as_map(degradation_summary.get("rendered_disabled")).get("effective_ui_mode")),
        ),
        "- tui_unavailable: `{}` -> `{}` logged=`{}`".format(
            _token(_as_map(degradation_summary.get("tui_unavailable")).get("compatibility_mode_id")),
            _token(_as_map(degradation_summary.get("tui_unavailable")).get("effective_ui_mode")),
            bool(_as_map(degradation_summary.get("tui_unavailable")).get("degrade_logged", False)),
        ),
        "",
        "## Gates",
        "",
        _gate_line("RepoX STRICT", "repox"),
        _gate_line("AuditX STRICT", "auditx"),
        _gate_line("TestX", "testx"),
        _gate_line("smoke harness", "smoke"),
    ]
    if base:
        lines.extend(
            [
                "",
                "## Regression Lock",
                "",
                "- baseline_id: `{}`".format(_token(base.get("baseline_id"))),
                "- baseline_fingerprint: `{}`".format(_token(base.get("deterministic_fingerprint"))),
                "- baseline runtime_pack_lock_hash: `{}`".format(_token(base.get("runtime_pack_lock_hash"))),
                "- required_commit_tag: `{}`".format(_token(_as_map(base.get("update_policy")).get("required_commit_tag"))),
            ]
        )
    return "\n".join(lines).strip() + "\n"


def maybe_load_cached_mvp_smoke_report(
    repo_root: str,
    *,
    scenario: Mapping[str, object],
    expected_hashes: Mapping[str, object],
    report_path: str = "",
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    report_payload = load_json_if_present(repo_root_abs, report_path or DEFAULT_REPORT_REL)
    if not report_payload:
        return {}
    if _token(report_payload.get("result")) != "complete":
        return {}
    if _token(report_payload.get("scenario_id")) != _token(_as_map(scenario).get("scenario_id")):
        return {}
    if _token(report_payload.get("scenario_fingerprint")) != _token(_as_map(scenario).get("deterministic_fingerprint")):
        return {}
    if _token(report_payload.get("expected_hashes_fingerprint")) != _token(_as_map(expected_hashes).get("deterministic_fingerprint")):
        return {}
    return report_payload


def write_mvp_smoke_outputs(
    repo_root: str,
    *,
    report: Mapping[str, object],
    report_path: str = "",
    final_doc_path: str = "",
    baseline_path: str = "",
    update_baseline: bool = False,
    update_tag: str = "",
    gate_results: Mapping[str, object] | None = None,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    report_abs = _repo_abs(repo_root_abs, report_path or DEFAULT_REPORT_REL)
    baseline_abs = _repo_abs(repo_root_abs, baseline_path or DEFAULT_BASELINE_REL)
    final_doc_abs = _repo_abs(repo_root_abs, final_doc_path or DEFAULT_FINAL_DOC_REL)
    report_payload = dict(_as_map(report))
    baseline_payload = dict(_as_map(report_payload.get("baseline_candidate")))
    _write_canonical_json(report_abs, report_payload)
    if update_baseline:
        if _token(update_tag) != MVP_SMOKE_REGRESSION_UPDATE_TAG:
            raise ValueError("baseline update requires {}".format(MVP_SMOKE_REGRESSION_UPDATE_TAG))
        _write_canonical_json(baseline_abs, baseline_payload)
    else:
        existing_baseline = load_json_if_present(repo_root_abs, _relative_path(repo_root_abs, baseline_abs))
        if existing_baseline:
            baseline_payload = existing_baseline
    markdown = render_mvp_smoke_final_markdown(report_payload, baseline=baseline_payload, gate_results=gate_results)
    _write_text(final_doc_abs, markdown)
    return {
        "result": "complete",
        "report_path": _relative_path(repo_root_abs, report_abs),
        "baseline_path": _relative_path(repo_root_abs, baseline_abs),
        "final_doc_path": _relative_path(repo_root_abs, final_doc_abs),
        "baseline_written": bool(update_baseline),
        "deterministic_fingerprint": canonical_sha256(
            {
                "report_path": _relative_path(repo_root_abs, report_abs),
                "baseline_path": _relative_path(repo_root_abs, baseline_abs),
                "final_doc_path": _relative_path(repo_root_abs, final_doc_abs),
                "baseline_written": bool(update_baseline),
                "report_fingerprint": _token(report_payload.get("deterministic_fingerprint")),
            }
        ),
    }


__all__ = [
    "DEFAULT_BASELINE_REL",
    "DEFAULT_FINAL_DOC_REL",
    "DEFAULT_HASHES_REL",
    "DEFAULT_MVP_SMOKE_SEED",
    "DEFAULT_REPORT_REL",
    "DEFAULT_SCENARIO_REL",
    "MVP_SMOKE_REGRESSION_UPDATE_TAG",
    "build_curated_pack_runtime",
    "build_expected_hash_fingerprints",
    "build_mvp_smoke_baseline",
    "build_smoke_runtime_artifacts",
    "generate_mvp_smoke_scenario",
    "load_json_if_present",
    "maybe_load_cached_mvp_smoke_report",
    "render_mvp_smoke_final_markdown",
    "run_logic_smoke_suite",
    "run_mvp_smoke",
    "run_server_window_with_pack_lock",
    "write_generated_mvp_smoke_inputs",
    "write_mvp_smoke_outputs",
]
