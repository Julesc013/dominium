#!/usr/bin/env python3
"""Deterministic MAT-8 reenactment artifact generator CLI."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.materials.commitments.commitment_engine import (  # noqa: E402
    CommitmentError,
    build_reenactment_artifact,
)
from src.materials.provenance.event_stream_index import (  # noqa: E402
    build_event_stream_index,
    normalize_event_stream_index_row,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


CACHE_ROOT_REL = os.path.join(".xstack_cache", "reenactment_cache")


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _ensure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def _read_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_json(path: str, payload: Dict[str, object]) -> None:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _load_rows(path: str, preferred_key: str) -> List[dict]:
    if not str(path).strip():
        return []
    payload = _read_json(os.path.abspath(path))
    if not payload:
        return []
    rows = payload.get(preferred_key)
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, dict)]
    if isinstance(payload.get("record"), dict):
        nested = (dict(payload.get("record") or {})).get(preferred_key)
        if isinstance(nested, list):
            return [dict(row) for row in nested if isinstance(row, dict)]
    if isinstance(payload.get("rows"), list):
        return [dict(row) for row in list(payload.get("rows") or []) if isinstance(row, dict)]
    return []


def _request_row(args: argparse.Namespace) -> tuple[dict, dict]:
    request_path = str(args.request_file).strip()
    if request_path:
        payload = _read_json(os.path.abspath(request_path))
        if not payload:
            return {}, {
                "result": "refused",
                "errors": [
                    {
                        "code": "refusal.reenactment.parameter_invalid",
                        "message": "request-file is missing or invalid JSON object",
                        "path": "$.request_file",
                    }
                ],
            }
        return dict(payload), {}
    target_id = str(args.target_id).strip()
    if not target_id:
        return {}, {
            "result": "refused",
            "errors": [
                {
                    "code": "refusal.reenactment.parameter_invalid",
                    "message": "target_id is required when --request-file is omitted",
                    "path": "$.target_id",
                }
            ],
        }
    start_tick = max(0, int(args.start_tick))
    end_tick = max(start_tick, int(args.end_tick))
    desired_fidelity = str(args.desired_fidelity).strip() or "macro"
    if desired_fidelity not in ("macro", "meso", "micro"):
        desired_fidelity = "macro"
    max_cost_units = max(0, int(args.max_cost_units))
    request_id = str(args.request_id).strip()
    if not request_id:
        request_id = "reenactment.request.{}".format(
            canonical_sha256(
                {
                    "target_id": target_id,
                    "tick_range": {"start_tick": int(start_tick), "end_tick": int(end_tick)},
                    "desired_fidelity": desired_fidelity,
                    "max_cost_units": int(max_cost_units),
                }
            )[:24]
        )
    return {
        "schema_version": "1.0.0",
        "request_id": request_id,
        "target_id": target_id,
        "tick_range": {
            "start_tick": int(start_tick),
            "end_tick": int(end_tick),
        },
        "desired_fidelity": desired_fidelity,
        "max_cost_units": int(max_cost_units),
        "requester_subject_id": str(args.requester_subject_id).strip() or "subject.tool.reenact",
        "extensions": {},
    }, {}


def _event_stream_row(args: argparse.Namespace, request_row: dict) -> tuple[dict, dict]:
    stream_path = str(args.event_stream_file).strip()
    if stream_path:
        payload = _read_json(os.path.abspath(stream_path))
        if not payload:
            return {}, {
                "result": "refused",
                "errors": [
                    {
                        "code": "refusal.reenactment.parameter_invalid",
                        "message": "event-stream-file is missing or invalid JSON object",
                        "path": "$.event_stream_file",
                    }
                ],
            }
        stream_row = normalize_event_stream_index_row(payload)
        stream_row["extensions"] = dict(payload.get("extensions") or {})
        return stream_row, {}

    events_path = str(args.events_file).strip()
    if not events_path:
        return {}, {
            "result": "refused",
            "errors": [
                {
                    "code": "refusal.reenactment.parameter_invalid",
                    "message": "either --event-stream-file or --events-file is required",
                    "path": "$.events_file",
                }
            ],
        }
    events_payload = _read_json(os.path.abspath(events_path))
    if not events_payload:
        return {}, {
            "result": "refused",
            "errors": [
                {
                    "code": "refusal.reenactment.parameter_invalid",
                    "message": "events-file is missing or invalid JSON object",
                    "path": "$.events_file",
                }
            ],
        }
    event_rows = []
    rows = events_payload.get("events")
    if isinstance(rows, list):
        event_rows = [dict(row) for row in rows if isinstance(row, dict)]
    elif isinstance(events_payload.get("rows"), list):
        event_rows = [dict(row) for row in list(events_payload.get("rows") or []) if isinstance(row, dict)]
    stream_row = build_event_stream_index(
        target_id=str(request_row.get("target_id", "")).strip(),
        events=event_rows,
        start_tick=int((dict(request_row.get("tick_range") or {})).get("start_tick", 0) or 0),
        end_tick=int((dict(request_row.get("tick_range") or {})).get("end_tick", 0) or 0),
    )
    return stream_row, {}


def _cache_paths(repo_root: str, inputs_hash: str) -> dict:
    root = os.path.join(repo_root, CACHE_ROOT_REL, str(inputs_hash))
    return {
        "root": root,
        "artifact": os.path.join(root, "reenactment_artifact.json"),
        "timeline": os.path.join(root, "reenactment_timeline.json"),
    }


def run_generate(args: argparse.Namespace) -> Dict[str, object]:
    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    request_row, request_error = _request_row(args)
    if request_error:
        return request_error
    stream_row, stream_error = _event_stream_row(args, request_row)
    if stream_error:
        return stream_error

    commitment_rows = _load_rows(str(args.commitments_file).strip(), "material_commitments")
    batch_lineage_rows = _load_rows(str(args.batch_lineage_file).strip(), "material_batches")
    max_cost_units = max(0, int(args.max_cost_units)) if int(args.max_cost_units) > 0 else int(request_row.get("max_cost_units", 0))
    allow_micro_detail = str(args.allow_micro_detail).strip().lower() in ("1", "true", "yes", "on")

    stream_extensions = dict(stream_row.get("extensions") or {})
    stream_for_build = dict(stream_row)
    stream_for_build["event_rows"] = [
        dict(row)
        for row in list(stream_extensions.get("event_rows") or [])
        if isinstance(row, dict)
    ]
    try:
        artifact_row, timeline_payload = build_reenactment_artifact(
            request_row=request_row,
            event_stream_row=stream_for_build,
            commitment_rows=commitment_rows,
            batch_lineage_rows=batch_lineage_rows,
            max_cost_units=int(max_cost_units),
            allow_micro_detail=bool(allow_micro_detail),
        )
    except CommitmentError as exc:
        return {
            "result": "refused",
            "errors": [
                {
                    "code": str(exc.reason_code),
                    "message": str(exc),
                    "path": "$.reenactment_generate",
                }
            ],
            "details": dict(exc.details),
        }

    reenactment_id = str(artifact_row.get("reenactment_id", "")).strip()
    output_timeline_ref = "timeline.{}".format(reenactment_id)
    artifact_row["output_timeline_ref"] = output_timeline_ref
    artifact_extensions = dict(artifact_row.get("extensions") or {})
    artifact_extensions["timeline"] = dict(timeline_payload)
    artifact_extensions["event_stream_id"] = str(stream_row.get("stream_id", "")).strip()
    artifact_extensions["derived_only"] = True
    artifact_row["extensions"] = artifact_extensions
    artifact_row["deterministic_fingerprint"] = canonical_sha256(
        dict(artifact_row, deterministic_fingerprint="")
    )
    inputs_hash = str(artifact_row.get("inputs_hash", "")).strip()

    cache_enabled = str(args.cache).strip().lower() != "off"
    cache_hit = False
    if cache_enabled and inputs_hash:
        paths = _cache_paths(repo_root, inputs_hash)
        cached_artifact = _read_json(paths["artifact"])
        cached_timeline = _read_json(paths["timeline"])
        if cached_artifact and cached_timeline:
            cache_hit = True
            artifact_row = dict(cached_artifact)
            timeline_payload = dict(cached_timeline)
        else:
            _ensure_dir(paths["root"])
            _write_json(paths["artifact"], artifact_row)
            _write_json(paths["timeline"], timeline_payload)

    out_dir_rel = str(args.out_dir).strip() or os.path.join("build", "reenactment")
    out_dir_abs = os.path.join(repo_root, out_dir_rel.replace("/", os.sep))
    _ensure_dir(out_dir_abs)
    prefix = reenactment_id or str(request_row.get("request_id", "reenactment")).replace("/", "_")
    artifact_out_abs = os.path.join(out_dir_abs, "{}.artifact.json".format(prefix))
    timeline_out_abs = os.path.join(out_dir_abs, "{}.timeline.json".format(prefix))
    stream_out_abs = os.path.join(out_dir_abs, "{}.event_stream.json".format(prefix))
    _write_json(artifact_out_abs, artifact_row)
    _write_json(timeline_out_abs, timeline_payload)
    _write_json(stream_out_abs, stream_row)

    return {
        "result": "complete",
        "tool_id": "tool.materials.tool_reenact_generate",
        "request_id": str(request_row.get("request_id", "")).strip(),
        "reenactment_id": reenactment_id,
        "inputs_hash": inputs_hash,
        "fidelity_achieved": str(artifact_row.get("fidelity_achieved", "")).strip(),
        "cache_hit": bool(cache_hit),
        "output_files": {
            "reenactment_artifact": _norm(os.path.relpath(artifact_out_abs, repo_root)),
            "timeline": _norm(os.path.relpath(timeline_out_abs, repo_root)),
            "event_stream": _norm(os.path.relpath(stream_out_abs, repo_root)),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic MAT-8 reenactment artifact from events/commitments.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--request-file", default="")
    parser.add_argument("--request-id", default="")
    parser.add_argument("--target-id", default="")
    parser.add_argument("--start-tick", type=int, default=0)
    parser.add_argument("--end-tick", type=int, default=0)
    parser.add_argument("--desired-fidelity", default="macro")
    parser.add_argument("--max-cost-units", type=int, default=0)
    parser.add_argument("--requester-subject-id", default="subject.tool.reenact")
    parser.add_argument("--event-stream-file", default="")
    parser.add_argument("--events-file", default="")
    parser.add_argument("--commitments-file", default="")
    parser.add_argument("--batch-lineage-file", default="")
    parser.add_argument("--allow-micro-detail", default="false")
    parser.add_argument("--out-dir", default=os.path.join("build", "reenactment"))
    parser.add_argument("--cache", choices=("on", "off"), default="on")
    args = parser.parse_args()

    result = run_generate(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")) == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
