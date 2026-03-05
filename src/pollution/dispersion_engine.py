"""POLL-1 deterministic dispersion, deposition, and exposure helpers."""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_POLLUTION_DISPERSION_INVALID = "REFUSAL_POLLUTION_DISPERSION_INVALID"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _sanitize_token(value: object) -> str:
    token = str(value or "").strip().lower()
    token = re.sub(r"[^a-z0-9_]+", "_", token)
    token = re.sub(r"_+", "_", token)
    return token.strip("_")


def concentration_field_id_for_pollutant(pollutant_id: object) -> str:
    token = str(pollutant_id or "").strip()
    if not token:
        return ""
    if token.startswith("pollutant."):
        token = token.split(".", 1)[1]
    token = _sanitize_token(token)
    if not token:
        return ""
    return "field.pollution.{}_concentration".format(token)


def pollution_decay_models_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = dict(registry_payload or {})
    record = _as_map(payload.get("record"))
    rows = record.get("decay_models")
    if not isinstance(rows, list):
        rows = []
    ids = list(record.get("decay_model_ids") or [])

    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("model_id", ""))):
        model_id = str(row.get("model_id", "")).strip()
        if not model_id:
            continue
        ext = _as_map(row.get("extensions"))
        out[model_id] = {
            "model_id": model_id,
            "kind": str(row.get("kind", "none")).strip() or "none",
            "half_life_ticks": int(max(1, _as_int(row.get("half_life_ticks", ext.get("half_life_ticks", 16)), 16))),
            "deposition_permille": int(
                max(0, min(1000, _as_int(row.get("deposition_permille", ext.get("deposition_permille", 0)), 0)))
            ),
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": ext,
        }

    # Ensure baseline IDs resolve even when registry is ids-only.
    for model_id in _sorted_tokens(ids):
        if model_id in out:
            continue
        if model_id == "model.poll_decay_half_life_stub":
            out[model_id] = {
                "model_id": model_id,
                "kind": "half_life",
                "half_life_ticks": 16,
                "deposition_permille": 0,
                "deterministic_fingerprint": "",
                "extensions": {"source": "default"},
            }
        elif model_id == "model.poll_deposition_stub":
            out[model_id] = {
                "model_id": model_id,
                "kind": "deposition",
                "half_life_ticks": 1,
                "deposition_permille": 120,
                "deterministic_fingerprint": "",
                "extensions": {"source": "default"},
            }
        else:
            out[model_id] = {
                "model_id": model_id,
                "kind": "none",
                "half_life_ticks": 1,
                "deposition_permille": 0,
                "deterministic_fingerprint": "",
                "extensions": {"source": "default"},
            }

    # Hard defaults for null/empty registries.
    for model_id, row in (
        (
            "model.poll_decay_none",
            {
                "model_id": "model.poll_decay_none",
                "kind": "none",
                "half_life_ticks": 1,
                "deposition_permille": 0,
                "deterministic_fingerprint": "",
                "extensions": {"source": "default"},
            },
        ),
        (
            "model.poll_decay_half_life_stub",
            {
                "model_id": "model.poll_decay_half_life_stub",
                "kind": "half_life",
                "half_life_ticks": 16,
                "deposition_permille": 0,
                "deterministic_fingerprint": "",
                "extensions": {"source": "default"},
            },
        ),
        (
            "model.poll_deposition_stub",
            {
                "model_id": "model.poll_deposition_stub",
                "kind": "deposition",
                "half_life_ticks": 1,
                "deposition_permille": 120,
                "deterministic_fingerprint": "",
                "extensions": {"source": "default"},
            },
        ),
    ):
        if model_id not in out:
            out[model_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def build_pollution_dispersion_step_row(
    *,
    step_id: str,
    tick: int,
    pollutant_id: str,
    spatial_scope_id: str,
    concentration_before: int,
    concentration_after: int,
    injected_mass: int,
    diffusion_term: int,
    decay_mass: int,
    deposition_mass: int,
    policy_id: str,
    decay_model_id: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    pollutant_token = str(pollutant_id or "").strip()
    scope_token = str(spatial_scope_id or "").strip()
    policy_token = str(policy_id or "").strip() or "poll.policy.none"
    decay_model_token = str(decay_model_id or "").strip() or "model.poll_decay_none"
    if (not pollutant_token) or (not scope_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "step_id": str(step_id or "").strip(),
        "tick": int(max(0, _as_int(tick, 0))),
        "pollutant_id": pollutant_token,
        "spatial_scope_id": scope_token,
        "concentration_before": int(max(0, _as_int(concentration_before, 0))),
        "concentration_after": int(max(0, _as_int(concentration_after, 0))),
        "injected_mass": int(max(0, _as_int(injected_mass, 0))),
        "diffusion_term": int(_as_int(diffusion_term, 0)),
        "decay_mass": int(max(0, _as_int(decay_mass, 0))),
        "deposition_mass": int(max(0, _as_int(deposition_mass, 0))),
        "policy_id": policy_token,
        "decay_model_id": decay_model_token,
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["step_id"]:
        payload["step_id"] = "poll.dispersion.step.{}".format(
            canonical_sha256(
                {
                    "tick": int(payload["tick"]),
                    "pollutant_id": pollutant_token,
                    "spatial_scope_id": scope_token,
                    "policy_id": policy_token,
                    "decay_model_id": decay_model_token,
                }
            )[:16]
        )
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_pollution_dispersion_step_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("pollutant_id", "")),
            str(item.get("spatial_scope_id", "")),
            str(item.get("step_id", "")),
        ),
    ):
        normalized = build_pollution_dispersion_step_row(
            step_id=str(row.get("step_id", "")).strip(),
            tick=int(max(0, _as_int(row.get("tick", 0), 0))),
            pollutant_id=str(row.get("pollutant_id", "")).strip(),
            spatial_scope_id=str(row.get("spatial_scope_id", "")).strip(),
            concentration_before=int(max(0, _as_int(row.get("concentration_before", 0), 0))),
            concentration_after=int(max(0, _as_int(row.get("concentration_after", 0), 0))),
            injected_mass=int(max(0, _as_int(row.get("injected_mass", 0), 0))),
            diffusion_term=int(_as_int(row.get("diffusion_term", 0), 0)),
            decay_mass=int(max(0, _as_int(row.get("decay_mass", 0), 0))),
            deposition_mass=int(max(0, _as_int(row.get("deposition_mass", 0), 0))),
            policy_id=str(row.get("policy_id", "")).strip(),
            decay_model_id=str(row.get("decay_model_id", "")).strip(),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        step_id = str(normalized.get("step_id", "")).strip()
        if step_id:
            out[step_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_pollution_deposition_row(
    *,
    deposition_id: str,
    tick: int,
    pollutant_id: str,
    spatial_scope_id: str,
    deposited_mass: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    pollutant_token = str(pollutant_id or "").strip()
    scope_token = str(spatial_scope_id or "").strip()
    if (not pollutant_token) or (not scope_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "deposition_id": str(deposition_id or "").strip(),
        "tick": int(max(0, _as_int(tick, 0))),
        "pollutant_id": pollutant_token,
        "spatial_scope_id": scope_token,
        "deposited_mass": int(max(0, _as_int(deposited_mass, 0))),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deposition_id"]:
        payload["deposition_id"] = "poll.deposition.{}".format(
            canonical_sha256(
                {
                    "tick": int(payload["tick"]),
                    "pollutant_id": pollutant_token,
                    "spatial_scope_id": scope_token,
                }
            )[:16]
        )
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_pollution_deposition_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("pollutant_id", "")),
            str(item.get("spatial_scope_id", "")),
            str(item.get("deposition_id", "")),
        ),
    ):
        normalized = build_pollution_deposition_row(
            deposition_id=str(row.get("deposition_id", "")).strip(),
            tick=int(max(0, _as_int(row.get("tick", 0), 0))),
            pollutant_id=str(row.get("pollutant_id", "")).strip(),
            spatial_scope_id=str(row.get("spatial_scope_id", "")).strip(),
            deposited_mass=int(max(0, _as_int(row.get("deposited_mass", 0), 0))),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        deposition_id = str(normalized.get("deposition_id", "")).strip()
        if deposition_id:
            out[deposition_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_pollution_exposure_state_row(
    *,
    subject_id: str,
    pollutant_id: str,
    accumulated_exposure: int,
    last_update_tick: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    subject_token = str(subject_id or "").strip()
    pollutant_token = str(pollutant_id or "").strip()
    if (not subject_token) or (not pollutant_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "subject_id": subject_token,
        "pollutant_id": pollutant_token,
        "accumulated_exposure": int(max(0, _as_int(accumulated_exposure, 0))),
        "last_update_tick": int(max(0, _as_int(last_update_tick, 0))),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_pollution_exposure_state_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("subject_id", "")),
            str(item.get("pollutant_id", "")),
        ),
    ):
        normalized = build_pollution_exposure_state_row(
            subject_id=str(row.get("subject_id", "")).strip(),
            pollutant_id=str(row.get("pollutant_id", "")).strip(),
            accumulated_exposure=int(max(0, _as_int(row.get("accumulated_exposure", 0), 0))),
            last_update_tick=int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        subject_id = str(normalized.get("subject_id", "")).strip()
        pollutant_id = str(normalized.get("pollutant_id", "")).strip()
        if subject_id and pollutant_id:
            out["{}::{}".format(subject_id, pollutant_id)] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def pollution_exposure_rows_by_key(rows: object) -> Dict[str, dict]:
    normalized = normalize_pollution_exposure_state_rows(rows)
    out: Dict[str, dict] = {}
    for row in normalized:
        subject_id = str(row.get("subject_id", "")).strip()
        pollutant_id = str(row.get("pollutant_id", "")).strip()
        if subject_id and pollutant_id:
            out["{}::{}".format(subject_id, pollutant_id)] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _wind_by_cell(field_cell_rows: object, *, field_id: str) -> Dict[str, dict]:
    if not isinstance(field_cell_rows, list):
        field_cell_rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in field_cell_rows if isinstance(item, Mapping)),
        key=lambda item: str(item.get("cell_id", "")),
    ):
        if str(row.get("field_id", "")).strip() != str(field_id).strip():
            continue
        cell_id = str(row.get("cell_id", "")).strip()
        if not cell_id:
            continue
        value = _as_map(row.get("value"))
        out[cell_id] = {
            "x": int(_as_int(value.get("x", 0), 0)),
            "y": int(_as_int(value.get("y", 0), 0)),
            "z": int(_as_int(value.get("z", 0), 0)),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _scalar_by_cell(field_cell_rows: object, *, field_id: str) -> Dict[str, int]:
    if not isinstance(field_cell_rows, list):
        field_cell_rows = []
    out: Dict[str, int] = {}
    for row in sorted(
        (dict(item) for item in field_cell_rows if isinstance(item, Mapping)),
        key=lambda item: str(item.get("cell_id", "")),
    ):
        if str(row.get("field_id", "")).strip() != str(field_id).strip():
            continue
        cell_id = str(row.get("cell_id", "")).strip()
        if not cell_id:
            continue
        out[cell_id] = int(max(0, _as_int(row.get("value", 0), 0)))
    return dict((key, int(out[key])) for key in sorted(out.keys()))


def _pollutant_profile(
    *,
    pollutant_row: Mapping[str, object],
    pollution_policies_by_id: Mapping[str, Mapping[str, object]],
    decay_models_by_id: Mapping[str, Mapping[str, object]],
) -> dict:
    row = dict(pollutant_row or {})
    ext = _as_map(row.get("extensions"))
    policy_id = str(row.get("default_dispersion_policy_id", "")).strip() or "poll.policy.none"
    policy_row = dict(pollution_policies_by_id.get(policy_id) or {})
    decay_model_id = str(row.get("default_decay_model_id", "")).strip() or "model.poll_decay_none"
    decay_row = dict(decay_models_by_id.get(decay_model_id) or {})
    diffusion_permille = int(
        max(
            0,
            min(
                1000,
                _as_int(
                    ext.get("diffusion_coeff_permille", ext.get("diffusion_coefficient_permille", 120)),
                    120,
                ),
            ),
        )
    )
    wind_bias_permille = int(max(0, min(1000, _as_int(ext.get("wind_bias_permille", 80), 80))))
    return {
        "policy_id": policy_id,
        "policy_row": policy_row,
        "decay_model_id": decay_model_id,
        "decay_row": decay_row,
        "diffusion_permille": diffusion_permille,
        "wind_bias_permille": wind_bias_permille,
        "tier": str(policy_row.get("tier", "P0")).strip() or "P0",
    }


def _split_cell_work(
    *,
    cell_ids: List[str],
    current_tick: int,
    max_cell_updates_per_tick: int,
) -> Tuple[List[str], List[str]]:
    normalized = [str(token).strip() for token in sorted(cell_ids) if str(token).strip()]
    limit = int(max(0, _as_int(max_cell_updates_per_tick, 0)))
    if limit <= 0 or len(normalized) <= limit:
        return list(normalized), []
    bucket_count = max(1, (len(normalized) + max(1, limit) - 1) // max(1, limit))
    bucket_index = int(max(0, _as_int(current_tick, 0))) % int(bucket_count)
    selected = [cell_id for idx, cell_id in enumerate(normalized) if (idx % bucket_count) == bucket_index]
    deferred = [cell_id for cell_id in normalized if cell_id not in set(selected)]
    return selected[:limit], deferred


def evaluate_pollution_dispersion(
    *,
    current_tick: int,
    pollutant_types_by_id: Mapping[str, Mapping[str, object]],
    pollution_policies_by_id: Mapping[str, Mapping[str, object]],
    decay_models_by_id: Mapping[str, Mapping[str, object]],
    pollution_source_event_rows: object,
    processed_source_event_ids: object,
    field_cell_rows: object,
    neighbor_map_by_cell: Mapping[str, object] | None = None,
    wind_field_id: str = "field.wind",
    max_cell_updates_per_tick: int = 0,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    processed = set(_sorted_tokens(list(processed_source_event_ids or [])))
    source_rows = []
    for row in sorted(
        (dict(item) for item in list(pollution_source_event_rows or []) if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("source_event_id", "")),
        ),
    ):
        source_event_id = str(row.get("source_event_id", "")).strip()
        if not source_event_id:
            continue
        source_rows.append(dict(row))

    wind_by_cell = _wind_by_cell(field_cell_rows, field_id=str(wind_field_id or "").strip() or "field.wind")
    neighbor_map = dict(neighbor_map_by_cell or {})

    updates: List[dict] = []
    dispersion_steps: List[dict] = []
    deposition_rows: List[dict] = []
    deferred_cells: List[str] = []
    processed_now: List[str] = []
    degraded = False
    degraded_reasons: List[str] = []

    for pollutant_id in sorted(str(token).strip() for token in pollutant_types_by_id.keys() if str(token).strip()):
        pollutant_row = dict(pollutant_types_by_id.get(pollutant_id) or {})
        profile = _pollutant_profile(
            pollutant_row=pollutant_row,
            pollution_policies_by_id=pollution_policies_by_id,
            decay_models_by_id=decay_models_by_id,
        )
        field_id = concentration_field_id_for_pollutant(pollutant_id)
        if not field_id:
            continue
        policy_row = dict(profile.get("policy_row") or {})
        tier = str(profile.get("tier", "P0")).strip() or "P0"
        if tier not in {"P1", "P2"}:
            continue
        concentration_by_cell = _scalar_by_cell(field_cell_rows, field_id=field_id)

        injections_by_cell: Dict[str, int] = {}
        for source_row in source_rows:
            source_event_id = str(source_row.get("source_event_id", "")).strip()
            if source_event_id in processed:
                continue
            if int(max(0, _as_int(source_row.get("tick", 0), 0))) > tick:
                continue
            if str(source_row.get("pollutant_id", "")).strip() != pollutant_id:
                continue
            cell_id = str(source_row.get("spatial_scope_id", "")).strip()
            if not cell_id:
                continue
            injections_by_cell[cell_id] = int(max(0, _as_int(injections_by_cell.get(cell_id, 0), 0))) + int(
                max(0, _as_int(source_row.get("emitted_mass", 0), 0))
            )
            processed_now.append(source_event_id)

        work_cells = sorted(set(list(concentration_by_cell.keys()) + list(injections_by_cell.keys())))
        selected_cells, deferred = _split_cell_work(
            cell_ids=work_cells,
            current_tick=tick,
            max_cell_updates_per_tick=max_cell_updates_per_tick,
        )
        if deferred:
            degraded = True
            deferred_cells.extend(list(deferred))
            degraded_reasons.append("degrade.pollution.cell_budget")

        decay_model_id = str(profile.get("decay_model_id", "")).strip() or "model.poll_decay_none"
        decay_row = dict(profile.get("decay_row") or {})
        decay_kind = str(decay_row.get("kind", "none")).strip() or "none"
        diffusion_permille = int(max(0, min(1000, _as_int(profile.get("diffusion_permille", 120), 120))))
        wind_bias_permille = int(max(0, min(1000, _as_int(profile.get("wind_bias_permille", 80), 80))))
        wind_enabled = bool(policy_row.get("wind_modifier_enabled", False))

        for cell_id in selected_cells:
            current_value = int(max(0, _as_int(concentration_by_cell.get(cell_id, 0), 0)))
            injected = int(max(0, _as_int(injections_by_cell.get(cell_id, 0), 0)))
            neighbor_ids = _sorted_tokens(list(neighbor_map.get(cell_id) or []))
            neighbor_values = [
                int(max(0, _as_int(concentration_by_cell.get(neighbor_id, 0), 0)))
                for neighbor_id in neighbor_ids
            ]
            gradient_sum = int(sum(int(value - current_value) for value in neighbor_values))
            diffusion_term = 0
            if neighbor_values:
                diffusion_term = int((gradient_sum * diffusion_permille) // (1000 * len(neighbor_values)))
            if wind_enabled:
                wind = dict(wind_by_cell.get(cell_id) or {"x": 0, "y": 0, "z": 0})
                wind_strength = int(
                    min(
                        1000,
                        max(
                            0,
                            abs(int(_as_int(wind.get("x", 0), 0)))
                            + abs(int(_as_int(wind.get("y", 0), 0)))
                            + abs(int(_as_int(wind.get("z", 0), 0))),
                        ),
                    )
                )
                if wind_strength > 0 and gradient_sum != 0:
                    wind_term = int(
                        (gradient_sum * wind_strength * wind_bias_permille)
                        // (1000 * 1000 * max(1, len(neighbor_values)))
                    )
                    diffusion_term += int(wind_term)

            before_losses = int(current_value + injected + diffusion_term)
            if before_losses < 0:
                before_losses = 0

            decay_mass = 0
            deposition_mass = 0
            if decay_kind == "half_life":
                half_life_ticks = int(max(1, _as_int(decay_row.get("half_life_ticks", 16), 16)))
                decay_mass = int(before_losses // half_life_ticks)
            elif decay_kind == "deposition":
                deposition_permille = int(max(0, min(1000, _as_int(decay_row.get("deposition_permille", 120), 120))))
                deposition_mass = int((before_losses * deposition_permille) // 1000)
            elif decay_kind == "mixed":
                half_life_ticks = int(max(1, _as_int(decay_row.get("half_life_ticks", 32), 32)))
                deposition_permille = int(max(0, min(1000, _as_int(decay_row.get("deposition_permille", 60), 60))))
                decay_mass = int(before_losses // half_life_ticks)
                deposition_mass = int((before_losses * deposition_permille) // 1000)

            total_losses = int(decay_mass + deposition_mass)
            if total_losses > before_losses:
                total_losses = before_losses
            next_value = int(max(0, before_losses - total_losses))

            updates.append(
                {
                    "field_id": field_id,
                    "spatial_node_id": cell_id,
                    "sampled_value": int(next_value),
                    "extensions": {
                        "source_process_id": "process.pollution_dispersion_tick",
                        "pollutant_id": pollutant_id,
                        "policy_id": str(profile.get("policy_id", "poll.policy.none")),
                    },
                }
            )
            dispersion_steps.append(
                build_pollution_dispersion_step_row(
                    step_id="",
                    tick=tick,
                    pollutant_id=pollutant_id,
                    spatial_scope_id=cell_id,
                    concentration_before=current_value,
                    concentration_after=next_value,
                    injected_mass=injected,
                    diffusion_term=diffusion_term,
                    decay_mass=decay_mass,
                    deposition_mass=deposition_mass,
                    policy_id=str(profile.get("policy_id", "poll.policy.none")),
                    decay_model_id=decay_model_id,
                    deterministic_fingerprint="",
                    extensions={
                        "neighbor_count": len(neighbor_ids),
                        "wind_enabled": bool(wind_enabled),
                    },
                )
            )
            if deposition_mass > 0:
                deposition_rows.append(
                    build_pollution_deposition_row(
                        deposition_id="",
                        tick=tick,
                        pollutant_id=pollutant_id,
                        spatial_scope_id=cell_id,
                        deposited_mass=deposition_mass,
                        deterministic_fingerprint="",
                        extensions={
                            "policy_id": str(profile.get("policy_id", "poll.policy.none")),
                            "decay_model_id": decay_model_id,
                        },
                    )
                )

    updates = sorted(
        [dict(row) for row in updates if isinstance(row, Mapping)],
        key=lambda row: (str(row.get("field_id", "")), str(row.get("spatial_node_id", ""))),
    )
    dispersion_steps = normalize_pollution_dispersion_step_rows(dispersion_steps)
    deposition_rows = normalize_pollution_deposition_rows(deposition_rows)
    processed_now_tokens = _sorted_tokens(list(processed_now))
    return {
        "field_updates": updates,
        "dispersion_step_rows": dispersion_steps,
        "deposition_rows": deposition_rows,
        "processed_source_event_ids": processed_now_tokens,
        "degraded": bool(degraded),
        "degrade_reason": (
            None if not degraded_reasons else ",".join(_sorted_tokens(list(degraded_reasons)))
        ),
        "deferred_cell_ids": _sorted_tokens(list(deferred_cells)),
        "cost_units_used": int(len(updates)),
        "deterministic_fingerprint": canonical_sha256(
            {
                "tick": tick,
                "field_updates": [dict(row) for row in updates],
                "processed_source_event_ids": list(processed_now_tokens),
                "degraded": bool(degraded),
                "deferred_cell_ids": _sorted_tokens(list(deferred_cells)),
            }
        ),
    }


def accumulate_pollution_exposure(
    *,
    current_tick: int,
    subject_rows: object,
    field_cell_rows: object,
    pollutant_types_by_id: Mapping[str, Mapping[str, object]],
    exposure_state_rows: object,
    default_exposure_factor_permille: int = 1000,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    if not isinstance(subject_rows, list):
        subject_rows = []

    normalized_subjects: List[dict] = []
    for row in sorted(
        (dict(item) for item in subject_rows if isinstance(item, Mapping)),
        key=lambda item: (str(item.get("subject_id", "")), str(item.get("spatial_scope_id", item.get("cell_id", "")))),
    ):
        subject_id = str(row.get("subject_id", "")).strip()
        cell_id = str(row.get("spatial_scope_id", row.get("cell_id", ""))).strip()
        if (not subject_id) or (not cell_id):
            continue
        factor_permille = int(
            max(
                0,
                _as_int(row.get("exposure_factor_permille", default_exposure_factor_permille), default_exposure_factor_permille),
            )
        )
        normalized_subjects.append(
            {
                "subject_id": subject_id,
                "spatial_scope_id": cell_id,
                "exposure_factor_permille": factor_permille,
                "extensions": _as_map(row.get("extensions")),
            }
        )

    concentration_by_field_and_cell: Dict[str, Dict[str, int]] = {}
    for pollutant_id in sorted(str(token).strip() for token in pollutant_types_by_id.keys() if str(token).strip()):
        field_id = concentration_field_id_for_pollutant(pollutant_id)
        if not field_id:
            continue
        concentration_by_field_and_cell[field_id] = _scalar_by_cell(field_cell_rows, field_id=field_id)

    by_key = pollution_exposure_rows_by_key(exposure_state_rows)
    increments: List[dict] = []
    for subject_row in normalized_subjects:
        subject_id = str(subject_row.get("subject_id", "")).strip()
        cell_id = str(subject_row.get("spatial_scope_id", "")).strip()
        factor_permille = int(max(0, _as_int(subject_row.get("exposure_factor_permille", default_exposure_factor_permille), default_exposure_factor_permille)))
        for pollutant_id in sorted(str(token).strip() for token in pollutant_types_by_id.keys() if str(token).strip()):
            field_id = concentration_field_id_for_pollutant(pollutant_id)
            concentration = int(
                max(
                    0,
                    _as_int((dict(concentration_by_field_and_cell.get(field_id) or {})).get(cell_id, 0), 0),
                )
            )
            increment = int((concentration * factor_permille) // 1000)
            if increment <= 0:
                continue
            key = "{}::{}".format(subject_id, pollutant_id)
            existing = dict(by_key.get(key) or {})
            accumulated_before = int(max(0, _as_int(existing.get("accumulated_exposure", 0), 0)))
            accumulated_after = int(accumulated_before + increment)
            ext = _as_map(existing.get("extensions"))
            ext["last_spatial_scope_id"] = cell_id
            ext["last_exposure_factor_permille"] = factor_permille
            ext["last_concentration"] = concentration
            updated = build_pollution_exposure_state_row(
                subject_id=subject_id,
                pollutant_id=pollutant_id,
                accumulated_exposure=accumulated_after,
                last_update_tick=tick,
                deterministic_fingerprint="",
                extensions=ext,
            )
            if not updated:
                continue
            by_key[key] = dict(updated)
            increments.append(
                {
                    "schema_version": "1.0.0",
                    "tick": tick,
                    "subject_id": subject_id,
                    "pollutant_id": pollutant_id,
                    "spatial_scope_id": cell_id,
                    "concentration": concentration,
                    "exposure_factor_permille": factor_permille,
                    "increment": increment,
                    "accumulated_exposure": accumulated_after,
                    "deterministic_fingerprint": canonical_sha256(
                        {
                            "tick": tick,
                            "subject_id": subject_id,
                            "pollutant_id": pollutant_id,
                            "spatial_scope_id": cell_id,
                            "increment": increment,
                            "accumulated_exposure": accumulated_after,
                        }
                    ),
                    "extensions": {
                        "source_process_id": "process.pollution_dispersion_tick",
                        "hazard_hook": "hazard.health_risk_stub",
                    },
                }
            )

    exposure_rows = normalize_pollution_exposure_state_rows(list(by_key.values()))
    increments = sorted(
        [dict(row) for row in increments if isinstance(row, Mapping)],
        key=lambda row: (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("subject_id", "")),
            str(row.get("pollutant_id", "")),
        ),
    )
    return {
        "exposure_state_rows": exposure_rows,
        "exposure_increment_rows": increments,
        "deterministic_fingerprint": canonical_sha256(
            {
                "tick": tick,
                "exposure_state_rows": [dict(row) for row in exposure_rows],
                "exposure_increment_rows": [dict(row) for row in increments],
            }
        ),
    }


def pollution_field_hash_chain(
    *,
    field_cell_rows: object,
    pollutant_types_by_id: Mapping[str, Mapping[str, object]],
) -> str:
    rows = []
    for pollutant_id in sorted(str(token).strip() for token in pollutant_types_by_id.keys() if str(token).strip()):
        field_id = concentration_field_id_for_pollutant(pollutant_id)
        if not field_id:
            continue
        by_cell = _scalar_by_cell(field_cell_rows, field_id=field_id)
        for cell_id in sorted(by_cell.keys()):
            rows.append(
                {
                    "field_id": field_id,
                    "pollutant_id": pollutant_id,
                    "cell_id": cell_id,
                    "concentration": int(max(0, _as_int(by_cell.get(cell_id, 0), 0))),
                }
            )
    return canonical_sha256(list(rows))


def pollution_deposition_hash_chain(deposition_rows: object) -> str:
    normalized = normalize_pollution_deposition_rows(deposition_rows)
    return canonical_sha256(
        [
            {
                "deposition_id": str(row.get("deposition_id", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "pollutant_id": str(row.get("pollutant_id", "")).strip(),
                "spatial_scope_id": str(row.get("spatial_scope_id", "")).strip(),
                "deposited_mass": int(max(0, _as_int(row.get("deposited_mass", 0), 0))),
            }
            for row in normalized
        ]
    )


__all__ = [
    "REFUSAL_POLLUTION_DISPERSION_INVALID",
    "accumulate_pollution_exposure",
    "build_pollution_deposition_row",
    "build_pollution_dispersion_step_row",
    "build_pollution_exposure_state_row",
    "concentration_field_id_for_pollutant",
    "evaluate_pollution_dispersion",
    "normalize_pollution_deposition_rows",
    "normalize_pollution_dispersion_step_rows",
    "normalize_pollution_exposure_state_rows",
    "pollution_decay_models_by_id",
    "pollution_deposition_hash_chain",
    "pollution_exposure_rows_by_key",
    "pollution_field_hash_chain",
]
