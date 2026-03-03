"""Deterministic ELEC-3 storage-state helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_ELEC_STORAGE_INVALID = "refusal.elec.storage_invalid"
SOC_SCALE = 1_000_000


class ElectricStorageError(ValueError):
    """Deterministic electrical storage refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code or REFUSAL_ELEC_STORAGE_INVALID)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda token: str(token)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def build_storage_state(
    *,
    node_id: str,
    state_of_charge: int,
    capacity_energy: int,
    last_update_tick: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    node_token = str(node_id or "").strip()
    if not node_token:
        raise ElectricStorageError(
            REFUSAL_ELEC_STORAGE_INVALID,
            "storage_state requires node_id",
            {},
        )
    payload = {
        "schema_version": "1.0.0",
        "node_id": node_token,
        "state_of_charge": int(max(0, min(SOC_SCALE, _as_int(state_of_charge, 0)))),
        "capacity_energy": int(max(0, _as_int(capacity_energy, 0))),
        "last_update_tick": int(max(0, _as_int(last_update_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_storage_state_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("node_id", ""))):
        node_id = str(row.get("node_id", "")).strip()
        if not node_id:
            continue
        try:
            out[node_id] = build_storage_state(
                node_id=node_id,
                state_of_charge=int(_as_int(row.get("state_of_charge", 0), 0)),
                capacity_energy=int(_as_int(row.get("capacity_energy", 0), 0)),
                last_update_tick=int(_as_int(row.get("last_update_tick", 0), 0)),
                extensions=_as_map(row.get("extensions")),
            )
        except ElectricStorageError:
            continue
    return [dict(out[key]) for key in sorted(out.keys())]


def storage_state_rows_by_node_id(rows: object) -> Dict[str, dict]:
    return dict((str(row.get("node_id", "")).strip(), dict(row)) for row in normalize_storage_state_rows(rows))


def _energy_from_soc(*, state_of_charge: int, capacity_energy: int) -> int:
    soc = int(max(0, min(SOC_SCALE, _as_int(state_of_charge, 0))))
    cap = int(max(0, _as_int(capacity_energy, 0)))
    if cap <= 0 or soc <= 0:
        return 0
    return int((soc * cap) // SOC_SCALE)


def _soc_from_energy(*, energy: int, capacity_energy: int) -> int:
    cap = int(max(0, _as_int(capacity_energy, 0)))
    if cap <= 0:
        return 0
    clamped = int(max(0, min(cap, _as_int(energy, 0))))
    return int(max(0, min(SOC_SCALE, (clamped * SOC_SCALE) // cap)))


def apply_storage_charge(
    *,
    storage_rows: object,
    node_id: str,
    energy_delta: int,
    current_tick: int,
) -> dict:
    node_token = str(node_id or "").strip()
    if not node_token:
        raise ElectricStorageError(REFUSAL_ELEC_STORAGE_INVALID, "storage_charge requires node_id", {})
    requested = int(max(0, _as_int(energy_delta, 0)))
    rows_by_node = storage_state_rows_by_node_id(storage_rows)
    row = dict(rows_by_node.get(node_token) or {})
    if not row:
        row = build_storage_state(
            node_id=node_token,
            state_of_charge=0,
            capacity_energy=0,
            last_update_tick=int(max(0, _as_int(current_tick, 0))),
            extensions={"created_by": "process.storage_charge"},
        )
    cap = int(max(0, _as_int(row.get("capacity_energy", 0), 0)))
    current_energy = _energy_from_soc(
        state_of_charge=int(_as_int(row.get("state_of_charge", 0), 0)),
        capacity_energy=cap,
    )
    accepted = int(max(0, min(requested, max(0, cap - current_energy))))
    updated_energy = int(current_energy + accepted)
    updated = build_storage_state(
        node_id=node_token,
        state_of_charge=_soc_from_energy(energy=updated_energy, capacity_energy=cap),
        capacity_energy=cap,
        last_update_tick=int(max(0, _as_int(current_tick, 0))),
        extensions=dict(_as_map(row.get("extensions"))),
    )
    rows_by_node[node_token] = updated
    return {
        "storage_rows": [dict(rows_by_node[key]) for key in sorted(rows_by_node.keys())],
        "node_id": node_token,
        "accepted_energy_delta": int(accepted),
        "requested_energy_delta": int(requested),
        "result_row": dict(updated),
    }


def apply_storage_discharge(
    *,
    storage_rows: object,
    node_id: str,
    energy_delta: int,
    current_tick: int,
) -> dict:
    node_token = str(node_id or "").strip()
    if not node_token:
        raise ElectricStorageError(REFUSAL_ELEC_STORAGE_INVALID, "storage_discharge requires node_id", {})
    requested = int(max(0, _as_int(energy_delta, 0)))
    rows_by_node = storage_state_rows_by_node_id(storage_rows)
    row = dict(rows_by_node.get(node_token) or {})
    if not row:
        raise ElectricStorageError(
            REFUSAL_ELEC_STORAGE_INVALID,
            "storage_state missing for discharge",
            {"node_id": node_token},
        )
    cap = int(max(0, _as_int(row.get("capacity_energy", 0), 0)))
    current_energy = _energy_from_soc(
        state_of_charge=int(_as_int(row.get("state_of_charge", 0), 0)),
        capacity_energy=cap,
    )
    accepted = int(max(0, min(requested, current_energy)))
    updated_energy = int(max(0, current_energy - accepted))
    updated = build_storage_state(
        node_id=node_token,
        state_of_charge=_soc_from_energy(energy=updated_energy, capacity_energy=cap),
        capacity_energy=cap,
        last_update_tick=int(max(0, _as_int(current_tick, 0))),
        extensions=dict(_as_map(row.get("extensions"))),
    )
    rows_by_node[node_token] = updated
    return {
        "storage_rows": [dict(rows_by_node[key]) for key in sorted(rows_by_node.keys())],
        "node_id": node_token,
        "accepted_energy_delta": int(accepted),
        "requested_energy_delta": int(requested),
        "result_row": dict(updated),
    }


__all__ = [
    "ElectricStorageError",
    "REFUSAL_ELEC_STORAGE_INVALID",
    "SOC_SCALE",
    "apply_storage_charge",
    "apply_storage_discharge",
    "build_storage_state",
    "normalize_storage_state_rows",
    "storage_state_rows_by_node_id",
]
