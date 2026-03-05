"""Deterministic PROV-0 provenance compaction engine."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


_DERIVED_STATE_KEYS = (
    "explain_artifact_rows",
    "explain_cache_rows",
    "model_evaluation_results",
    "mobility_inspection_snapshots",
    "inspection_snapshot_cache_rows",
    "inspection_snapshot_rows",
    "derived_summary_rows",
    "derived_statistics_rows",
)

_BRANCH_OPEN_STATUSES = {"open", "pending", "active"}

_CANONICAL_EVENT_KEYS = (
    "energy_ledger_entries",
    "boundary_flux_events",
    "exception_events",
    "time_adjust_events",
    "fault_events",
    "leak_events",
    "burst_events",
    "relief_events",
    "branch_events",
    "compaction_markers",
)


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _row_tick(row: Mapping[str, object]) -> int | None:
    payload = dict(row or {})
    ext = _as_map(payload.get("extensions"))
    candidates = (
        payload.get("tick"),
        payload.get("start_tick"),
        payload.get("acquired_tick"),
        payload.get("last_update_tick"),
        ext.get("tick"),
        ext.get("source_tick"),
        ext.get("acquired_tick"),
        ext.get("last_update_tick"),
    )
    for value in candidates:
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return None


def _artifact_type_id(row: Mapping[str, object]) -> str:
    payload = dict(row or {})
    token = str(payload.get("artifact_type_id", "")).strip()
    if token:
        return token
    ext = _as_map(payload.get("extensions"))
    return str(ext.get("artifact_type_id", "")).strip()


def _sorted_rows(rows: Iterable[Mapping[str, object]]) -> List[dict]:
    return sorted(
        (dict(row) for row in rows if isinstance(row, Mapping)),
        key=lambda row: (
            str(row.get("artifact_id", "")),
            int(_as_int(row.get("tick", 0), 0)),
            canonical_sha256(dict(row)),
        ),
    )


def _window_contains_tick(*, tick: int | None, start_tick: int, end_tick: int) -> bool:
    if tick is None:
        return False
    return int(start_tick) <= int(tick) <= int(end_tick)


def normalize_provenance_classification_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        payload = dict(row)
        artifact_type_id = str(payload.get("artifact_type_id", "")).strip()
        if not artifact_type_id:
            continue
        classification = str(payload.get("classification", "")).strip().lower()
        if classification not in {"canonical", "derived"}:
            continue
        compaction_allowed = bool(payload.get("compaction_allowed", False))
        if classification == "canonical":
            compaction_allowed = False
        normalized = {
            "schema_version": "1.0.0",
            "artifact_type_id": artifact_type_id,
            "classification": classification,
            "compaction_allowed": compaction_allowed,
            "deterministic_fingerprint": "",
            "extensions": _as_map(payload.get("extensions")),
        }
        normalized["deterministic_fingerprint"] = canonical_sha256(
            dict(normalized, deterministic_fingerprint="")
        )
        out[artifact_type_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def _classification_index(rows: object) -> Dict[str, dict]:
    normalized = normalize_provenance_classification_rows(rows)
    return {
        str(row.get("artifact_type_id", "")).strip(): dict(row)
        for row in normalized
        if str(row.get("artifact_type_id", "")).strip()
    }


def build_compaction_marker(
    *,
    marker_id: str,
    shard_id: str,
    start_tick: int,
    end_tick: int,
    pre_compaction_hash: str,
    post_compaction_hash: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    start_value = int(max(0, _as_int(start_tick, 0)))
    end_value = int(max(start_value, _as_int(end_tick, start_value)))
    payload = {
        "schema_version": "1.0.0",
        "marker_id": str(marker_id or "").strip(),
        "shard_id": str(shard_id or "").strip() or "shard.unknown",
        "start_tick": start_value,
        "end_tick": end_value,
        "pre_compaction_hash": str(pre_compaction_hash or "").strip().lower(),
        "post_compaction_hash": str(post_compaction_hash or "").strip().lower(),
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    if not payload["marker_id"]:
        payload["marker_id"] = "compaction.marker.{}".format(
            canonical_sha256(
                {
                    "shard_id": payload["shard_id"],
                    "start_tick": start_value,
                    "end_tick": end_value,
                    "pre_compaction_hash": payload["pre_compaction_hash"],
                    "post_compaction_hash": payload["post_compaction_hash"],
                    "extensions": dict(payload["extensions"]),
                }
            )[:16]
        )
    payload["deterministic_fingerprint"] = canonical_sha256(
        dict(payload, deterministic_fingerprint="")
    )
    return payload


def normalize_compaction_marker_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        marker = build_compaction_marker(
            marker_id=str(row.get("marker_id", "")).strip(),
            shard_id=str(row.get("shard_id", "")).strip() or "shard.unknown",
            start_tick=int(max(0, _as_int(row.get("start_tick", 0), 0))),
            end_tick=int(max(0, _as_int(row.get("end_tick", 0), 0))),
            pre_compaction_hash=str(row.get("pre_compaction_hash", "")).strip(),
            post_compaction_hash=str(row.get("post_compaction_hash", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        out[str(marker.get("marker_id", "")).strip()] = marker
    return sorted(
        [dict(out[key]) for key in sorted(out.keys())],
        key=lambda row: (
            str(row.get("shard_id", "")),
            int(max(0, _as_int(row.get("start_tick", 0), 0))),
            str(row.get("marker_id", "")),
        ),
    )


def _anchor_projection(state_payload: Mapping[str, object]) -> dict:
    payload = dict(state_payload or {})
    out = {}
    for key in _CANONICAL_EVENT_KEYS:
        rows = payload.get(key)
        if not isinstance(rows, list):
            continue
        out[key] = _sorted_rows(rows)
    return out


def _replay_projection_without_derived(state_payload: Mapping[str, object]) -> dict:
    payload = dict(state_payload or {})
    out = {}
    for key in _CANONICAL_EVENT_KEYS:
        rows = payload.get(key)
        if not isinstance(rows, list):
            continue
        if key == "compaction_markers":
            # Replay-equivalence checks are anchored to truth events, independent from marker witness rows.
            continue
        out[key] = _sorted_rows(rows)
    return out


def _replay_projection_up_to_tick_without_derived(
    state_payload: Mapping[str, object],
    *,
    end_tick: int,
) -> dict:
    payload = dict(state_payload or {})
    tick_limit = int(max(0, _as_int(end_tick, 0)))
    out = {}
    for key in _CANONICAL_EVENT_KEYS:
        rows = payload.get(key)
        if not isinstance(rows, list):
            continue
        if key == "compaction_markers":
            # Marker rows are proof witnesses, not part of replay-equivalence truth projection.
            continue
        filtered_rows = []
        for row in _sorted_rows(rows):
            tick = _row_tick(row)
            if tick is None:
                # Tick-less canonical rows are treated as globally visible for conservative replay checks.
                filtered_rows.append(dict(row))
                continue
            if int(tick) <= tick_limit:
                filtered_rows.append(dict(row))
        out[key] = filtered_rows
    return out


def _refresh_compaction_hashes(state_payload: dict) -> None:
    markers = normalize_compaction_marker_rows(state_payload.get("compaction_markers"))
    state_payload["compaction_markers"] = [dict(row) for row in markers]
    state_payload["compaction_marker_hash_chain"] = canonical_sha256(
        [
            {
                "marker_id": str(row.get("marker_id", "")).strip(),
                "shard_id": str(row.get("shard_id", "")).strip(),
                "start_tick": int(max(0, _as_int(row.get("start_tick", 0), 0))),
                "end_tick": int(max(0, _as_int(row.get("end_tick", 0), 0))),
                "pre_compaction_hash": str(row.get("pre_compaction_hash", "")).strip().lower(),
                "post_compaction_hash": str(row.get("post_compaction_hash", "")).strip().lower(),
                "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip().lower(),
            }
            for row in markers
        ]
    )
    if markers:
        latest = markers[-1]
        state_payload["compaction_pre_anchor_hash"] = str(
            latest.get("pre_compaction_hash", "")
        ).strip().lower()
        state_payload["compaction_post_anchor_hash"] = str(
            latest.get("post_compaction_hash", "")
        ).strip().lower()
    else:
        state_payload["compaction_pre_anchor_hash"] = canonical_sha256([])
        state_payload["compaction_post_anchor_hash"] = canonical_sha256([])


def _validate_compaction_window(
    *,
    state_payload: Mapping[str, object],
    start_tick: int,
    end_tick: int,
) -> Tuple[bool, str]:
    for row in list(state_payload.get("time_branches") or state_payload.get("branch_rows") or []):
        if not isinstance(row, Mapping):
            continue
        fork_tick = int(
            _as_int(
                dict(row).get("fork_tick", dict(row).get("divergence_tick", -1)),
                -1,
            )
        )
        if fork_tick < int(start_tick) or fork_tick > int(end_tick):
            continue
        status = str(dict(row).get("status", "")).strip().lower()
        if status in _BRANCH_OPEN_STATUSES:
            return (
                False,
                "open branch intersects compaction window at tick {}".format(fork_tick),
            )

    for row in list(state_payload.get("control_proof_bundles") or []):
        if not isinstance(row, Mapping):
            continue
        tick_range = _as_map(dict(row).get("tick_range"))
        start = int(max(0, _as_int(tick_range.get("start_tick", 0), 0)))
        end = int(max(start, _as_int(tick_range.get("end_tick", start), start)))
        overlaps = not (end < int(start_tick) or start > int(end_tick))
        if not overlaps:
            continue
        ext = _as_map(dict(row).get("extensions"))
        sealed = bool(ext.get("proof_window_sealed", True))
        if not sealed:
            return (
                False,
                "unsealed proof window intersects compaction window [{}-{}]".format(start, end),
            )
    return True, ""


def _compact_rows_in_window(rows: object, *, start_tick: int, end_tick: int) -> Tuple[List[dict], List[dict]]:
    if not isinstance(rows, list):
        return [], []
    keep: List[dict] = []
    removed: List[dict] = []
    for row in _sorted_rows(rows):
        tick = _row_tick(row)
        if _window_contains_tick(tick=tick, start_tick=start_tick, end_tick=end_tick):
            removed.append(dict(row))
        else:
            keep.append(dict(row))
    return keep, removed


def _compact_info_artifacts(
    rows: object,
    *,
    classification_index: Mapping[str, Mapping[str, object]],
    start_tick: int,
    end_tick: int,
) -> Tuple[List[dict], List[dict]]:
    if not isinstance(rows, list):
        return [], []
    keep: List[dict] = []
    removed: List[dict] = []
    for row in _sorted_rows(rows):
        artifact_type_id = _artifact_type_id(row)
        class_row = dict(classification_index.get(artifact_type_id, {}) or {})
        classification = str(class_row.get("classification", "")).strip().lower()
        compaction_allowed = bool(class_row.get("compaction_allowed", False))
        tick = _row_tick(row)
        if classification == "derived" and compaction_allowed and _window_contains_tick(
            tick=tick,
            start_tick=start_tick,
            end_tick=end_tick,
        ):
            removed.append(dict(row))
            continue
        keep.append(dict(row))
    return keep, removed


def compact_provenance_window(
    *,
    state_payload: Mapping[str, object],
    classification_rows: object,
    shard_id: str,
    start_tick: int,
    end_tick: int,
    emit_summary: bool = True,
) -> dict:
    state = dict(state_payload or {})
    window_start = int(max(0, _as_int(start_tick, 0)))
    window_end = int(max(window_start, _as_int(end_tick, window_start)))
    shard_token = str(shard_id or "").strip() or "shard.unknown"
    class_index = _classification_index(classification_rows)

    valid_window, reason = _validate_compaction_window(
        state_payload=state,
        start_tick=window_start,
        end_tick=window_end,
    )
    if not valid_window:
        return {
            "result": "refused",
            "reason_code": "refusal.provenance.compaction_window_invalid",
            "message": reason,
            "state": state,
        }

    pre_replay_hash = canonical_sha256(_replay_projection_without_derived(state))
    pre_anchor_hash = canonical_sha256(_anchor_projection(state))

    removed_count = 0
    removed_by_key: Dict[str, int] = {}

    for key in _DERIVED_STATE_KEYS:
        keep_rows, removed_rows = _compact_rows_in_window(
            state.get(key),
            start_tick=window_start,
            end_tick=window_end,
        )
        if not isinstance(state.get(key), list):
            continue
        state[key] = [dict(row) for row in keep_rows]
        if removed_rows:
            removed_by_key[key] = int(len(removed_rows))
            removed_count += int(len(removed_rows))

    info_keep, info_removed = _compact_info_artifacts(
        state.get("info_artifact_rows"),
        classification_index=class_index,
        start_tick=window_start,
        end_tick=window_end,
    )
    if isinstance(state.get("info_artifact_rows"), list):
        state["info_artifact_rows"] = [dict(row) for row in info_keep]
        if isinstance(state.get("knowledge_artifacts"), list):
            state["knowledge_artifacts"] = [dict(row) for row in info_keep]
        if info_removed:
            removed_by_key["info_artifact_rows"] = int(len(info_removed))
            removed_count += int(len(info_removed))

    if emit_summary and removed_count > 0:
        summary = {
            "schema_version": "1.0.0",
            "summary_id": "derived.compaction.summary.{}".format(
                canonical_sha256(
                    {
                        "shard_id": shard_token,
                        "start_tick": window_start,
                        "end_tick": window_end,
                        "removed_by_key": dict(removed_by_key),
                    }
                )[:16]
            ),
            "shard_id": shard_token,
            "start_tick": window_start,
            "end_tick": window_end,
            "removed_by_key": dict(removed_by_key),
            "removed_total": int(removed_count),
            "deterministic_fingerprint": "",
            "extensions": {},
        }
        summary["deterministic_fingerprint"] = canonical_sha256(
            dict(summary, deterministic_fingerprint="")
        )
        existing = [
            dict(row)
            for row in list(state.get("provenance_compaction_summaries") or [])
            if isinstance(row, Mapping)
        ]
        existing.append(summary)
        state["provenance_compaction_summaries"] = sorted(
            existing,
            key=lambda row: (
                str(row.get("shard_id", "")),
                int(_as_int(row.get("start_tick", 0), 0)),
                str(row.get("summary_id", "")),
            ),
        )

    post_replay_hash = canonical_sha256(_replay_projection_without_derived(state))
    if post_replay_hash != pre_replay_hash:
        return {
            "result": "violation",
            "reason_code": "refusal.provenance.replay_mismatch_after_compaction",
            "message": "replay projection changed after derived-only compaction",
            "pre_replay_hash": pre_replay_hash,
            "post_replay_hash": post_replay_hash,
            "state": state,
        }

    marker = build_compaction_marker(
        marker_id="",
        shard_id=shard_token,
        start_tick=window_start,
        end_tick=window_end,
        pre_compaction_hash=pre_anchor_hash,
        post_compaction_hash=canonical_sha256(_anchor_projection(state)),
        extensions={
            "derived_removed_total": int(removed_count),
            "derived_removed_by_key": dict(removed_by_key),
            "replay_hash_before": pre_replay_hash,
            "replay_hash_after": post_replay_hash,
        },
    )
    marker_rows = [
        dict(row) for row in list(state.get("compaction_markers") or []) if isinstance(row, Mapping)
    ]
    marker_rows.append(marker)
    state["compaction_markers"] = [dict(row) for row in normalize_compaction_marker_rows(marker_rows)]
    _refresh_compaction_hashes(state)

    return {
        "result": "complete",
        "shard_id": shard_token,
        "start_tick": window_start,
        "end_tick": window_end,
        "removed_total": int(removed_count),
        "removed_by_key": dict(removed_by_key),
        "pre_replay_hash": pre_replay_hash,
        "post_replay_hash": post_replay_hash,
        "compaction_marker": dict(marker),
        "compaction_marker_hash_chain": str(state.get("compaction_marker_hash_chain", "")),
        "pre_compaction_hash": str(state.get("compaction_pre_anchor_hash", "")),
        "post_compaction_hash": str(state.get("compaction_post_anchor_hash", "")),
        "state": state,
    }


def verify_replay_from_compaction_anchor(
    *,
    state_payload: Mapping[str, object],
    marker_id: str,
) -> dict:
    state = dict(state_payload or {})
    marker_token = str(marker_id or "").strip()
    marker_rows = normalize_compaction_marker_rows(state.get("compaction_markers"))
    marker = {}
    for row in marker_rows:
        if str(row.get("marker_id", "")).strip() == marker_token:
            marker = dict(row)
            break
    if not marker:
        return {
            "result": "refused",
            "reason_code": "refusal.provenance.compaction_marker_missing",
            "message": "marker_id '{}' was not found".format(marker_token),
        }

    replay_hash = canonical_sha256(_replay_projection_without_derived(state))
    marker_end_tick = int(max(0, _as_int(marker.get("end_tick", 0), 0)))
    anchor_replay_hash = canonical_sha256(
        _replay_projection_up_to_tick_without_derived(
            state,
            end_tick=marker_end_tick,
        )
    )
    marker_extensions = _as_map(marker.get("extensions"))
    expected_replay_hash = str(marker_extensions.get("replay_hash_after", "")).strip().lower()
    if not expected_replay_hash:
        expected_replay_hash = str(marker_extensions.get("replay_hash_before", "")).strip().lower()
    replay_match_mode = "none"
    if expected_replay_hash:
        if replay_hash == expected_replay_hash:
            replay_match_mode = "current_state"
        elif anchor_replay_hash == expected_replay_hash:
            replay_match_mode = "historical_anchor"
        else:
            return {
                "result": "violation",
                "reason_code": "refusal.provenance.anchor_replay_mismatch",
                "message": "replay hash from anchor diverged",
                "marker_id": marker_token,
                "expected_replay_hash": expected_replay_hash,
                "observed_replay_hash": replay_hash,
                "observed_anchor_replay_hash": anchor_replay_hash,
                "marker_end_tick": marker_end_tick,
            }

    _refresh_compaction_hashes(state)
    return {
        "result": "complete",
        "marker_id": marker_token,
        "replay_hash": replay_hash,
        "anchor_replay_hash": anchor_replay_hash,
        "replay_match_mode": replay_match_mode,
        "marker_end_tick": marker_end_tick,
        "compaction_marker_hash_chain": str(state.get("compaction_marker_hash_chain", "")),
        "pre_compaction_hash": str(state.get("compaction_pre_anchor_hash", "")),
        "post_compaction_hash": str(state.get("compaction_post_anchor_hash", "")),
    }
