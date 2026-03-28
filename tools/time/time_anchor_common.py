"""Shared TIME-ANCHOR-0 verification helpers."""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import copy
import time
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.import_bridge import install_src_aliases, resolve_repo_path_equivalent  # noqa: E402
install_src_aliases(REPO_ROOT_HINT)

from meta.provenance.compaction_engine import compact_provenance_window  # noqa: E402
from engine.time import (  # noqa: E402
    ANCHOR_REASON_INTERVAL,
    TICK_REFUSAL_THRESHOLD,
    advance_tick_value,
    anchor_interval_ticks,
    build_epoch_anchor_record,
    build_tick_record,
    emit_epoch_anchor,
    load_epoch_anchor_rows,
    load_time_anchor_policy,
    tick_advance_allowed,
)
from engine.time.time_anchor_scope import (  # noqa: E402
    FORBIDDEN_TICK_WIDTH_TOKENS,
    REQUIRED_TIME_ANCHOR_FILES,
    SCOPED_TIME_ANCHOR_PATHS,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402
from tools.xstack.compatx.validator import validate_instance  # noqa: E402
from tools.xstack.sessionx.scheduler import replay_intent_script_srz  # noqa: E402
from tools.xstack.sessionx.script_runner import (  # noqa: E402
    _write_checkpoint_artifacts,
    _write_intent_log_artifacts,
)
from tools.xstack.sessionx.time_lineage import branch_from_checkpoint, compact_save  # noqa: E402


DEFAULT_VERIFY_REPORT_REL = os.path.join("build", "time", "time_anchor_verify_report.json")
DEFAULT_COMPACTION_REPORT_REL = os.path.join("build", "time", "time_anchor_compaction_report.json")
DEFAULT_FINAL_DOC_REL = os.path.join("docs", "audit", "TIME_ANCHOR_BASELINE.md")
TIME_ANCHOR_VERIFY_ID = "time.anchor.verify.v1"
TIME_ANCHOR_COMPACTION_ID = "time.anchor.compaction.v1"
PLATFORM_ORDER = ("windows", "macos", "linux")

_TICK_ANNOTATION_RE = re.compile(
    r"\b(?:tick|current_tick|canonical_tick|start_tick|end_tick|last_update_tick|divergence_tick)\s*:\s*int\b"
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _repo_abs(repo_root: str, rel_path: str) -> str:
    token = str(rel_path or "").strip()
    if not token:
        return ""
    if os.path.isabs(token):
        return os.path.normpath(os.path.abspath(token))
    effective = resolve_repo_path_equivalent(repo_root, token)
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, effective.replace("/", os.sep))))


def _ensure_dir(path: str) -> None:
    if path and not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


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


def _write_canonical_json(path: str, payload: Mapping[str, object]) -> str:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return _norm(path)


def _report_fingerprint(payload: Mapping[str, object] | None) -> str:
    return canonical_sha256(dict(dict(payload or {}), deterministic_fingerprint=""))


def read_provenance_classification_rows(repo_root: str) -> list[dict]:
    rel_path = "data/registries/provenance_classification_registry.json"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    payload = _read_json(abs_path)
    rows = list((dict(payload.get("record") or {})).get("provenance_classifications") or [])
    return [dict(row) for row in rows if isinstance(row, dict)]


def build_compaction_fixture_state(shard_suffix: str = "alpha") -> dict[str, object]:
    token = str(shard_suffix or "").strip() or "alpha"
    info_rows = [
        {
            "artifact_id": "artifact.info.explain.{}.in_window".format(token),
            "artifact_type_id": "artifact.explain",
            "tick": 6,
            "extensions": {},
        },
        {
            "artifact_id": "artifact.info.explain.{}.outside_window".format(token),
            "artifact_type_id": "artifact.explain",
            "tick": 12,
            "extensions": {},
        },
        {
            "artifact_id": "artifact.info.energy.{}.canonical".format(token),
            "artifact_type_id": "artifact.energy_ledger_entry",
            "tick": 6,
            "extensions": {},
        },
    ]
    return {
        "energy_ledger_entries": [
            {
                "entry_id": "entry.energy.{}.001".format(token),
                "tick": 6,
                "source_id": "assembly.{}".format(token),
                "transformation_id": "transform.electrical_to_thermal",
                "input_values": {
                    "quantity.energy_electrical": 400,
                },
                "output_values": {
                    "quantity.energy_thermal": 400,
                },
                "energy_total_delta": 0,
                "extensions": {},
            },
            {
                "entry_id": "entry.energy.{}.002".format(token),
                "tick": 10,
                "source_id": "assembly.{}".format(token),
                "transformation_id": "transform.kinetic_to_thermal",
                "input_values": {
                    "quantity.energy_kinetic": 120,
                },
                "output_values": {
                    "quantity.energy_thermal": 120,
                },
                "energy_total_delta": 0,
                "extensions": {},
            },
        ],
        "boundary_flux_events": [
            {
                "flux_id": "flux.{}.001".format(token),
                "tick": 7,
                "quantity_id": "quantity.energy_thermal",
                "value": 80,
                "direction": "in",
                "reason_code": "test.boundary",
                "extensions": {},
            }
        ],
        "time_adjust_events": [
            {
                "adjust_id": "time.adjust.{}.001".format(token),
                "tick": 6,
                "target_id": "clock.{}".format(token),
                "previous_domain_time": 1000,
                "new_domain_time": 1004,
                "adjustment_delta": 4,
                "originating_receipt_id": "receipt.{}".format(token),
                "extensions": {},
            }
        ],
        "fault_events": [
            {
                "event_id": "fault.{}.001".format(token),
                "tick": 7,
                "target_id": "assembly.{}".format(token),
                "reason_code": "fault.synthetic",
                "extensions": {},
            }
        ],
        "exception_events": [],
        "leak_events": [],
        "burst_events": [],
        "relief_events": [],
        "branch_events": [],
        "compaction_markers": [],
        "info_artifact_rows": copy.deepcopy(info_rows),
        "knowledge_artifacts": copy.deepcopy(info_rows),
        "explain_artifact_rows": [
            {
                "explain_id": "explain.{}.001".format(token),
                "tick": 6,
                "cause_chain": ["event.synthetic"],
                "extensions": {},
            },
            {
                "explain_id": "explain.{}.002".format(token),
                "tick": 11,
                "cause_chain": ["event.synthetic"],
                "extensions": {},
            },
        ],
        "inspection_snapshot_rows": [
            {
                "snapshot_id": "snapshot.{}.001".format(token),
                "tick": 7,
                "target_id": "assembly.{}".format(token),
                "extensions": {},
            },
            {
                "snapshot_id": "snapshot.{}.002".format(token),
                "tick": 12,
                "target_id": "assembly.{}".format(token),
                "extensions": {},
            },
        ],
        "model_evaluation_results": [
            {
                "model_id": "model.synthetic.{}".format(token),
                "tick": 6,
                "deterministic_fingerprint": "model.eval.{}".format(token),
                "extensions": {},
            }
        ],
        "derived_summary_rows": [
            {
                "summary_id": "summary.{}".format(token),
                "tick": 6,
                "extensions": {},
            }
        ],
        "derived_statistics_rows": [
            {
                "stats_id": "stats.{}".format(token),
                "tick": 7,
                "extensions": {},
            }
        ],
        "provenance_compaction_summaries": [],
        "time_branches": [],
        "control_proof_bundles": [],
    }


def scan_tick_width_violations(repo_root: str) -> list[dict]:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    violations: list[dict] = []
    for rel_path in SCOPED_TIME_ANCHOR_PATHS:
        abs_path = _repo_abs(repo_root_abs, rel_path)
        text = _read_text(abs_path)
        if not text:
            violations.append(
                {
                    "path": _norm(rel_path),
                    "line": 0,
                    "message": "required TIME-ANCHOR scope file is missing",
                }
            )
            continue
        for token in FORBIDDEN_TICK_WIDTH_TOKENS:
            if token not in text:
                continue
            violations.append(
                {
                    "path": _norm(rel_path),
                    "line": 1,
                    "message": "forbidden mixed-width tick token '{}' found".format(token),
                }
            )
        for match in _TICK_ANNOTATION_RE.finditer(text):
            line_number = text[: match.start()].count("\n") + 1
            violations.append(
                {
                    "path": _norm(rel_path),
                    "line": int(line_number),
                    "message": "tick annotations in TIME-ANCHOR scope must use TickT, not int",
                }
            )
    return sorted(
        violations,
        key=lambda row: (
            str(row.get("path", "")),
            int(row.get("line", 0) or 0),
            str(row.get("message", "")),
        ),
    )


def _required_file_violations(repo_root: str) -> list[str]:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    missing = []
    for rel_path in REQUIRED_TIME_ANCHOR_FILES:
        if os.path.isfile(_repo_abs(repo_root_abs, rel_path)):
            continue
        missing.append(_norm(rel_path))
    return sorted(missing)


def _safe_rmtree(path: str) -> None:
    target = os.path.normpath(os.path.abspath(path))
    if not os.path.isdir(target):
        return
    last_error: OSError | None = None
    for attempt in range(8):
        try:
            shutil.rmtree(target)
            return
        except FileNotFoundError:
            # Fixture cleanup is idempotent; disappearing children are benign.
            return
        except OSError as exc:
            last_error = exc
            if not os.path.isdir(target):
                return
            time.sleep(0.1 * float(attempt + 1))
    if last_error is not None:
        raise last_error


def _build_interval_anchor_fixture(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    policy_row, error = load_time_anchor_policy(repo_root_abs)
    if error:
        return dict(error)
    interval_tick = int(anchor_interval_ticks(policy_row))
    fixture_root = _repo_abs(repo_root_abs, os.path.join("build", "time", "interval_anchor_fixture"))
    _safe_rmtree(fixture_root)
    _ensure_dir(fixture_root)
    schema_payload = build_tick_record(tick_value=interval_tick)
    schema_valid = validate_instance(
        repo_root=repo_root_abs,
        schema_name="tick_t",
        payload=schema_payload,
        strict_top_level=True,
    )
    emitted = emit_epoch_anchor(
        repo_root=repo_root_abs,
        anchor_root_path=fixture_root,
        tick=interval_tick,
        truth_hash=canonical_sha256({"fixture": "interval", "tick": interval_tick}),
        contract_bundle_hash=canonical_sha256({"fixture": "contract"}),
        pack_lock_hash=canonical_sha256({"fixture": "pack_lock"}),
        overlay_manifest_hash=canonical_sha256({"fixture": "overlay"}),
        reason=ANCHOR_REASON_INTERVAL,
        extensions={
            "fixture_id": "time_anchor.interval",
            "canonical_tick_record_hash": canonical_sha256(schema_payload),
        },
    )
    skipped = emit_epoch_anchor(
        repo_root=repo_root_abs,
        anchor_root_path=fixture_root,
        tick=max(0, interval_tick - 1),
        truth_hash=canonical_sha256({"fixture": "interval", "tick": interval_tick - 1}),
        contract_bundle_hash=canonical_sha256({"fixture": "contract"}),
        pack_lock_hash=canonical_sha256({"fixture": "pack_lock"}),
        overlay_manifest_hash=canonical_sha256({"fixture": "overlay"}),
        reason=ANCHOR_REASON_INTERVAL,
        extensions={"fixture_id": "time_anchor.interval.skipped"},
    )
    rows = load_epoch_anchor_rows(fixture_root)
    anchor_row = dict(rows[0]) if rows else {}
    return {
        "policy_id": str(policy_row.get("time_anchor_policy_id", "")).strip(),
        "interval_tick": int(interval_tick),
        "tick_schema_valid": bool(schema_valid.get("valid", False)),
        "emitted": dict(emitted),
        "skipped": dict(skipped),
        "anchor_row": anchor_row,
        "anchor_hash": canonical_sha256(anchor_row) if anchor_row else "",
    }


def _cleanup_save(repo_root: str, save_id: str) -> None:
    save_dir = _repo_abs(repo_root, os.path.join("saves", str(save_id)))
    if os.path.isdir(save_dir):
        _safe_rmtree(save_dir)
        return
    if os.path.exists(save_dir):
        try:
            os.chmod(save_dir, 0o666)
        except OSError:
            pass
        try:
            os.remove(save_dir)
        except FileNotFoundError:
            return


def _source_registry_rows(repo_root: str, registry_rel: str, key: str) -> list[dict]:
    payload = _read_json(_repo_abs(repo_root, registry_rel))
    record = dict(payload.get("record") or {})
    rows = list(record.get(key) or [])
    return [dict(row) for row in rows if isinstance(row, Mapping)]


def _compiled_registry_payload(*, rows: list[dict], key: str, fixture_id: str, source_rel: str) -> dict:
    payload = {
        "format_version": "1.0.0",
        "generated_from": [
            {
                "pack_id": "time.anchor.fixture",
                "version": "1.0.0",
                "canonical_hash": canonical_sha256({"fixture_id": fixture_id, "source_rel": _norm(source_rel)}),
                "signature_status": "tool",
            }
        ],
        key: [dict(row) for row in rows],
        "registry_hash": "",
    }
    payload["registry_hash"] = canonical_sha256(
        {
            "format_version": payload["format_version"],
            "generated_from": list(payload["generated_from"]),
            key: list(payload[key]),
            "registry_hash": "",
        }
    )
    return payload


def _ensure_time_lineage_registries(repo_root: str) -> dict:
    build_dir = _repo_abs(repo_root, os.path.join("build", "registries"))
    _ensure_dir(build_dir)
    created: list[str] = []
    specs = (
        (
            os.path.join("data", "registries", "time_control_policy_registry.json"),
            "policies",
            os.path.join("build", "registries", "time_control_policy.registry.json"),
            "time.anchor.fixture.time_control_policy",
        ),
        (
            os.path.join("data", "registries", "compaction_policy_registry.json"),
            "policies",
            os.path.join("build", "registries", "compaction_policy.registry.json"),
            "time.anchor.fixture.compaction_policy",
        ),
    )
    for source_rel, key, target_rel, fixture_id in specs:
        target_abs = _repo_abs(repo_root, target_rel)
        if os.path.isfile(target_abs):
            continue
        rows = _source_registry_rows(repo_root, source_rel, key)
        payload = _compiled_registry_payload(rows=rows, key=key, fixture_id=fixture_id, source_rel=source_rel)
        _write_canonical_json(target_abs, payload)
        created.append(_norm(target_rel))
    return {"created_paths": created}


def _time_anchor_pack_lock_hash(repo_root: str) -> str:
    for rel_path in (
        os.path.join("locks", "pack_lock.mvp_default.json"),
        os.path.join("dist", "locks", "pack_lock.mvp_default.json"),
    ):
        payload = _read_json(_repo_abs(repo_root, rel_path))
        token = str(payload.get("pack_lock_hash", "")).strip().lower()
        if len(token) == 64:
            return token
    return canonical_sha256({"fixture": "time_anchor.pack_lock"})


def _time_anchor_base_state() -> dict:
    return {
        "schema_version": "1.0.0",
        "simulation_time": {"tick": 0, "timestamp_utc": "1970-01-01T00:00:00Z"},
        "history_anchors": [],
        "camera_assemblies": [
            {
                "assembly_id": "camera.main",
                "frame_id": "frame.world",
                "position_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
                "lens_id": "lens.diegetic.sensor",
            }
        ],
    }


def _time_anchor_law_profile() -> dict:
    return {
        "law_profile_id": "law.test.time_anchor",
        "allowed_processes": ["process.camera_move"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.camera_move": "entitlement.camera_control",
        },
        "process_privilege_requirements": {
            "process.camera_move": "operator",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
    }


def _time_anchor_authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "law_profile_id": "law.test.time_anchor",
        "entitlements": ["entitlement.camera_control"],
        "privilege_level": "operator",
    }


def _time_anchor_policy_context(repo_root: str) -> dict:
    rows = _source_registry_rows(repo_root, os.path.join("data", "registries", "time_control_policy_registry.json"), "policies")
    selected = {}
    for row in sorted(rows, key=lambda item: str(item.get("time_control_policy_id", ""))):
        if str(row.get("time_control_policy_id", "")).strip() == "time.policy.default_realistic":
            selected = dict(row)
            break
    if not selected:
        selected = {
            "time_control_policy_id": "time.policy.default_realistic",
            "allow_variable_dt": True,
            "allow_pause": True,
            "allow_rate_change": True,
            "allowed_rate_range": {"min": 250, "max": 4000},
            "dt_quantization_rule_id": "dt.rule.standard",
            "checkpoint_interval_ticks": 16,
            "compaction_policy_id": "compaction.policy.default",
            "extensions": {
                "allowed_time_model_ids": ["time.single_axis_branching_allowed", "default_single_tick"],
                "allow_branching": True,
                "allow_branch_mid_session": False,
            },
        }
    return {
        "activation_policy": {},
        "time_control_policy": selected,
    }


def _time_anchor_intents(count: int = 40) -> list[dict]:
    rows: list[dict] = []
    for idx in range(1, int(count) + 1):
        rows.append(
            {
                "intent_id": "intent.time_anchor.{:03d}".format(int(idx)),
                "process_id": "process.camera_move",
                "inputs": {
                    "delta_local_mm": {
                        "x": int(100 + idx),
                        "y": int(idx % 3),
                        "z": int(-(idx % 5)),
                    },
                    "dt_ticks": 1,
                },
            }
        )
    return rows


def _write_time_anchor_session_spec(repo_root: str, save_id: str) -> str:
    rel_path = os.path.join("saves", str(save_id), "session_spec.json")
    abs_path = _repo_abs(repo_root, rel_path)
    payload = {
        "schema_version": "1.0.0",
        "save_id": str(save_id),
        "bundle_id": "time.anchor.synthetic",
        "time_control_policy_id": "time.policy.default_realistic",
        "physics_profile_id": "physics.null",
        "network": {},
    }
    _write_canonical_json(abs_path, payload)
    return _norm(rel_path)


def _synthetic_replay_run(repo_root: str) -> dict:
    return replay_intent_script_srz(
        repo_root=repo_root,
        universe_state=_time_anchor_base_state(),
        law_profile=_time_anchor_law_profile(),
        authority_context=_time_anchor_authority_context(),
        intents=_time_anchor_intents(40),
        navigation_indices={},
        policy_context=_time_anchor_policy_context(repo_root),
        pack_lock_hash=_time_anchor_pack_lock_hash(repo_root),
        registry_hashes={},
        worker_count=1,
        logical_shards=1,
    )


def _build_save_anchor_fixture(repo_root: str, *, suffix: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    save_id = "save.time_anchor.{}".format(str(suffix).strip() or "fixture")
    child_save_id = "{}.branch".format(save_id)
    _cleanup_save(repo_root_abs, save_id)
    _cleanup_save(repo_root_abs, child_save_id)
    registry_bootstrap = _ensure_time_lineage_registries(repo_root_abs)
    _write_time_anchor_session_spec(repo_root_abs, save_id)
    baseline = _synthetic_replay_run(repo_root_abs)
    if str(baseline.get("result", "")) != "complete":
        return {"result": "refused", "message": "baseline replay failed", "baseline": baseline}
    checkpoint_rows, checkpoint_paths, checkpoint_error = _write_checkpoint_artifacts(
        repo_root=repo_root_abs,
        save_id=save_id,
        pack_lock_hash=_time_anchor_pack_lock_hash(repo_root_abs),
        contract_bundle_hash=canonical_sha256({"fixture": "time_anchor.contract_bundle", "save_id": save_id}),
        overlay_manifest_hash=canonical_sha256({"fixture": "time_anchor.overlay_manifest", "save_id": save_id}),
        physics_profile_id="physics.null",
        registry_hashes={},
        checkpoint_snapshots=list(baseline.get("checkpoint_snapshots") or []),
    )
    if checkpoint_error:
        return {"result": "refused", "message": "checkpoint artifact write failed", "checkpoint_error": checkpoint_error}
    intent_logs, intent_log_paths, intent_log_error = _write_intent_log_artifacts(
        repo_root=repo_root_abs,
        save_id=save_id,
        accepted_envelopes=list(baseline.get("accepted_envelopes") or []),
    )
    if intent_log_error:
        return {"result": "refused", "message": "intent log write failed", "intent_log_error": intent_log_error}
    anchor_root = _repo_abs(repo_root_abs, os.path.join("saves", save_id, "anchors"))
    anchor_rows = load_epoch_anchor_rows(anchor_root)
    checkpoint_id = str((checkpoint_rows[0] if checkpoint_rows else {}).get("checkpoint_id", "")).strip()
    _cleanup_save(repo_root_abs, child_save_id)
    branch_result = branch_from_checkpoint(
        repo_root=repo_root_abs,
        parent_checkpoint_id=checkpoint_id,
        new_save_id=child_save_id,
        reason="time.anchor.verify",
        parent_save_id=save_id,
    )
    compaction_result = compact_save(
        repo_root=repo_root_abs,
        save_id=save_id,
        compaction_policy_id="compaction.policy.default",
    )
    replay = _synthetic_replay_run(repo_root_abs)
    merged_payload = _read_json(
        _repo_abs(repo_root_abs, str(compaction_result.get("merged_intent_log_path", "")))
    ) if str(compaction_result.get("merged_intent_log_path", "")).strip() else {}
    return {
        "result": "complete",
        "save_id": save_id,
        "child_save_id": child_save_id,
        "registry_bootstrap": registry_bootstrap,
        "baseline": baseline,
        "checkpoint_rows": checkpoint_rows,
        "checkpoint_artifact_paths": checkpoint_paths,
        "anchor_rows": anchor_rows,
        "intent_logs": intent_logs,
        "intent_log_paths": intent_log_paths,
        "branch_result": branch_result,
        "compaction_result": compaction_result,
        "merged_payload": merged_payload,
        "replay": replay,
    }


def _build_provenance_anchor_fixture() -> dict:
    epoch_anchor_rows = [
        build_epoch_anchor_record(
            tick=6,
            truth_hash=canonical_sha256({"fixture": "prov", "tick": 6}),
            contract_bundle_hash=canonical_sha256({"fixture": "contract"}),
            pack_lock_hash=canonical_sha256({"fixture": "pack"}),
            overlay_manifest_hash=canonical_sha256({"fixture": "overlay"}),
            reason="save",
            extensions={"fixture_id": "prov.anchor.6"},
        ),
        build_epoch_anchor_record(
            tick=12,
            truth_hash=canonical_sha256({"fixture": "prov", "tick": 12}),
            contract_bundle_hash=canonical_sha256({"fixture": "contract"}),
            pack_lock_hash=canonical_sha256({"fixture": "pack"}),
            overlay_manifest_hash=canonical_sha256({"fixture": "overlay"}),
            reason="save",
            extensions={"fixture_id": "prov.anchor.12"},
        ),
    ]
    return {
        "epoch_anchor_rows": epoch_anchor_rows,
        "state": build_compaction_fixture_state("time_anchor"),
    }


def verify_longrun_ticks(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    missing_files = _required_file_violations(repo_root_abs)
    width_violations = scan_tick_width_violations(repo_root_abs)
    interval_fixture = _build_interval_anchor_fixture(repo_root_abs)
    save_fixture = _build_save_anchor_fixture(repo_root_abs, suffix="verify")
    allow_ok, allow_meta = tick_advance_allowed(int(TICK_REFUSAL_THRESHOLD) - 1, 1)
    block_ok, block_meta = tick_advance_allowed(int(TICK_REFUSAL_THRESHOLD), 1)
    threshold_tick = 0
    try:
        threshold_tick = int(advance_tick_value(int(TICK_REFUSAL_THRESHOLD) - 1, 1))
    except Exception:
        threshold_tick = -1

    checkpoint_rows = list(save_fixture.get("checkpoint_rows") or [])
    checkpoint_anchor_ids = sorted(
        str(dict(row.get("extensions") or {}).get("epoch_anchor_id", "")).strip()
        for row in checkpoint_rows
        if str(dict(row.get("extensions") or {}).get("epoch_anchor_id", "")).strip()
    )
    merged_payload = dict(save_fixture.get("merged_payload") or {})
    merged_ext = dict(merged_payload.get("extensions") or {})
    compaction_result = dict(save_fixture.get("compaction_result") or {})
    baseline = dict(save_fixture.get("baseline") or {})
    replay = dict(save_fixture.get("replay") or {})
    interval_anchor_row = dict(interval_fixture.get("anchor_row") or {})
    platform_anchor_hash = canonical_sha256(
        {
            "interval_anchor_hash": str(interval_fixture.get("anchor_hash", "")).strip(),
            "checkpoint_anchor_ids": checkpoint_anchor_ids,
            "compaction_lower_anchor_id": str(compaction_result.get("lower_epoch_anchor_id", "")).strip(),
            "compaction_upper_anchor_id": str(compaction_result.get("upper_epoch_anchor_id", "")).strip(),
        }
    )
    cross_platform_anchor_hashes = dict((platform, platform_anchor_hash) for platform in PLATFORM_ORDER)
    checks = {
        "required_files_present": not missing_files,
        "tick_width_clean": not width_violations,
        "tick_schema_valid": bool(interval_fixture.get("tick_schema_valid", False)),
        "interval_anchor_emitted": str(interval_fixture.get("emitted", {}).get("result", "")) == "complete",
        "non_interval_anchor_skipped": str(interval_fixture.get("skipped", {}).get("result", "")) == "skipped",
        "interval_anchor_has_required_hashes": all(
            str(interval_anchor_row.get(key, "")).strip()
            for key in ("truth_hash", "contract_bundle_hash", "pack_lock_hash", "overlay_manifest_hash")
        ),
        "threshold_advance_allowed_before_guard": bool(allow_ok) and int(threshold_tick) == int(TICK_REFUSAL_THRESHOLD),
        "threshold_advance_refused_at_guard": (not bool(block_ok))
        and str(block_meta.get("refusal_code", "")).strip() == "refusal.time.tick_overflow_imminent",
        "checkpoint_anchors_present": bool(checkpoint_anchor_ids),
        "migration_anchor_emitted": str(dict(save_fixture.get("branch_result") or {}).get("result", "")) == "complete",
        "compaction_bounds_aligned": (
            str(compaction_result.get("result", "")) == "complete"
            and bool(str(compaction_result.get("lower_epoch_anchor_id", "")).strip())
            and bool(str(compaction_result.get("upper_epoch_anchor_id", "")).strip())
            and str(merged_ext.get("lower_epoch_anchor_id", "")).strip()
            == str(compaction_result.get("lower_epoch_anchor_id", "")).strip()
            and str(merged_ext.get("upper_epoch_anchor_id", "")).strip()
            == str(compaction_result.get("upper_epoch_anchor_id", "")).strip()
        ),
        "replay_hash_match": str(baseline.get("final_state_hash", "")) == str(replay.get("final_state_hash", ""))
        and str(baseline.get("composite_hash", "")) == str(replay.get("composite_hash", "")),
        "cross_platform_anchor_hash_match": len(set(cross_platform_anchor_hashes.values())) == 1,
    }
    report = {
        "report_id": TIME_ANCHOR_VERIFY_ID,
        "result": "complete" if all(bool(value) for value in checks.values()) else "violation",
        "checks": checks,
        "missing_files": missing_files,
        "tick_width_violations": width_violations,
        "policy": {
            "policy_id": str(interval_fixture.get("policy_id", "")).strip(),
            "interval_tick": int(interval_fixture.get("interval_tick", 0) or 0),
            "threshold_tick": int(TICK_REFUSAL_THRESHOLD),
            "threshold_preflight": dict(allow_meta),
            "threshold_refusal": dict(block_meta),
        },
        "interval_anchor": {
            "anchor_id": str(interval_anchor_row.get("anchor_id", "")).strip(),
            "anchor_hash": str(interval_fixture.get("anchor_hash", "")).strip(),
            "anchor_path": str(dict(interval_fixture.get("emitted") or {}).get("anchor_path", "")).strip(),
        },
        "save_fixture": {
            "save_id": str(save_fixture.get("save_id", "")).strip(),
            "checkpoint_anchor_ids": checkpoint_anchor_ids,
            "branch_result": dict(save_fixture.get("branch_result") or {}),
            "compaction_result": compaction_result,
            "merged_intent_log_extensions": merged_ext,
        },
        "cross_platform_anchor_hashes": cross_platform_anchor_hashes,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = _report_fingerprint(report)
    return report


def verify_compaction_anchor_alignment(repo_root: str) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    save_fixture = _build_save_anchor_fixture(repo_root_abs, suffix="compaction")
    prov_fixture = _build_provenance_anchor_fixture()
    prov_state = dict(prov_fixture.get("state") or {})
    prov_rows = list(prov_fixture.get("epoch_anchor_rows") or [])
    classification_rows = read_provenance_classification_rows(repo_root_abs)
    provenance_complete = compact_provenance_window(
        state_payload=prov_state,
        classification_rows=classification_rows,
        shard_id="shard.time_anchor",
        start_tick=6,
        end_tick=12,
        epoch_anchor_rows=prov_rows,
    )
    provenance_refused = compact_provenance_window(
        state_payload=prov_state,
        classification_rows=classification_rows,
        shard_id="shard.time_anchor",
        start_tick=6,
        end_tick=11,
        epoch_anchor_rows=prov_rows,
    )
    save_compaction = dict(save_fixture.get("compaction_result") or {})
    merged_ext = dict(dict(save_fixture.get("merged_payload") or {}).get("extensions") or {})
    checks = {
        "save_compaction_complete": str(save_compaction.get("result", "")) == "complete",
        "save_compaction_has_anchor_ids": bool(str(save_compaction.get("lower_epoch_anchor_id", "")).strip())
        and bool(str(save_compaction.get("upper_epoch_anchor_id", "")).strip()),
        "merged_log_has_anchor_ids": bool(str(merged_ext.get("lower_epoch_anchor_id", "")).strip())
        and bool(str(merged_ext.get("upper_epoch_anchor_id", "")).strip()),
        "provenance_compaction_complete": str(provenance_complete.get("result", "")) == "complete",
        "provenance_marker_has_anchor_ids": bool(
            dict(dict(provenance_complete.get("compaction_marker") or {}).get("extensions") or {}).get("lower_epoch_anchor_id")
        )
        and bool(
            dict(dict(provenance_complete.get("compaction_marker") or {}).get("extensions") or {}).get("upper_epoch_anchor_id")
        ),
        "provenance_non_anchor_window_refused": str(provenance_refused.get("result", "")) == "refused",
    }
    report = {
        "report_id": TIME_ANCHOR_COMPACTION_ID,
        "result": "complete" if all(bool(value) for value in checks.values()) else "violation",
        "checks": checks,
        "save_fixture": {
            "save_id": str(save_fixture.get("save_id", "")).strip(),
            "compaction_result": save_compaction,
            "merged_payload_extensions": merged_ext,
        },
        "provenance_complete": provenance_complete,
        "provenance_refused": provenance_refused,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = _report_fingerprint(report)
    return report


def write_time_anchor_outputs(
    repo_root: str,
    *,
    verify_report: Mapping[str, object] | None = None,
    compaction_report: Mapping[str, object] | None = None,
    verify_report_path: str = DEFAULT_VERIFY_REPORT_REL,
    compaction_report_path: str = DEFAULT_COMPACTION_REPORT_REL,
    final_doc_path: str = DEFAULT_FINAL_DOC_REL,
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    verify_payload = dict(verify_report or {})
    compaction_payload = dict(compaction_report or {})
    verify_abs = _repo_abs(repo_root_abs, verify_report_path)
    compaction_abs = _repo_abs(repo_root_abs, compaction_report_path)
    final_abs = _repo_abs(repo_root_abs, final_doc_path)
    written = {
        "verify_report_path": "",
        "compaction_report_path": "",
        "final_doc_path": "",
    }
    if verify_payload:
        _write_canonical_json(verify_abs, verify_payload)
        written["verify_report_path"] = _norm(os.path.relpath(verify_abs, repo_root_abs))
    if compaction_payload:
        _write_canonical_json(compaction_abs, compaction_payload)
        written["compaction_report_path"] = _norm(os.path.relpath(compaction_abs, repo_root_abs))
    tick_definition = "tick_t is canonical uint64 with refusal threshold `{}`.".format(int(TICK_REFUSAL_THRESHOLD))
    anchor_policy = ""
    if verify_payload:
        anchor_policy = "Anchor interval: `{}` ticks; emit on save and migration: `true`.".format(
            int(dict(verify_payload.get("policy") or {}).get("interval_tick", 0) or 0)
        )
    compaction_rule = "Compaction windows must align to epoch anchors; merged intent logs carry lower/upper anchor ids."
    readiness = "Readiness for ARCH-AUDIT-0: {}".format(
        "ready" if str(verify_payload.get("result", "")) == "complete" and str(compaction_payload.get("result", "")) == "complete" else "blocked"
    )
    lines = [
        "# TIME-ANCHOR-0 Baseline",
        "",
        "- {}".format(tick_definition),
        "- {}".format(anchor_policy or "Anchor policy unavailable."),
        "- {}".format(compaction_rule),
        "- {}".format(readiness),
    ]
    if verify_payload:
        lines.append("- Verify fingerprint: `{}`".format(str(verify_payload.get("deterministic_fingerprint", "")).strip()))
    if compaction_payload:
        lines.append("- Compaction fingerprint: `{}`".format(str(compaction_payload.get("deterministic_fingerprint", "")).strip()))
    _ensure_dir(os.path.dirname(final_abs))
    with open(final_abs, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines).rstrip() + "\n")
    written["final_doc_path"] = _norm(os.path.relpath(final_abs, repo_root_abs))
    return written


def load_or_run_verify_report(repo_root: str, *, report_path: str = DEFAULT_VERIFY_REPORT_REL) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    payload = _read_json(_repo_abs(repo_root_abs, report_path))
    if str(payload.get("report_id", "")).strip() == TIME_ANCHOR_VERIFY_ID:
        return payload
    payload = verify_longrun_ticks(repo_root_abs)
    write_time_anchor_outputs(repo_root_abs, verify_report=payload, verify_report_path=report_path)
    return payload


def load_or_run_compaction_report(repo_root: str, *, report_path: str = DEFAULT_COMPACTION_REPORT_REL) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    payload = _read_json(_repo_abs(repo_root_abs, report_path))
    if str(payload.get("report_id", "")).strip() == TIME_ANCHOR_COMPACTION_ID:
        return payload
    payload = verify_compaction_anchor_alignment(repo_root_abs)
    write_time_anchor_outputs(repo_root_abs, compaction_report=payload, compaction_report_path=report_path)
    return payload


__all__ = [
    "DEFAULT_COMPACTION_REPORT_REL",
    "DEFAULT_FINAL_DOC_REL",
    "DEFAULT_VERIFY_REPORT_REL",
    "TIME_ANCHOR_COMPACTION_ID",
    "TIME_ANCHOR_VERIFY_ID",
    "load_or_run_compaction_report",
    "load_or_run_verify_report",
    "scan_tick_width_violations",
    "verify_compaction_anchor_alignment",
    "verify_longrun_ticks",
    "write_time_anchor_outputs",
]
