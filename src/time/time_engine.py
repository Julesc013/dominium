"""Deterministic simulation-time engine for RS-3 tick/dt governance."""

from __future__ import annotations

from typing import Dict, List, Tuple

from .tick_t import TickOverflowImminentError, TickT, advance_tick_value, normalize_tick_t


DEFAULT_RATE_PERMILLE = 1000
DEFAULT_DT_PERMILLE = 1000
DEFAULT_TIME_CONTROL_POLICY_ID = "time.policy.null"
DEFAULT_DT_RULE_ID = "dt.rule.single_tick"
DEFAULT_ROUNDING_RULE = "round.nearest.lower_tie"
MAX_RATE_PERMILLE = 10000
MAX_TIME_TICK_LOG_ITEMS = 1024


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _allowed_dt_values(rule: dict) -> List[int]:
    values = []
    for raw in list(rule.get("allowed_dt_values") or []):
        token = _as_int(raw, 0)
        if token > 0:
            values.append(int(token))
    deduped = sorted(set(values))
    return deduped


def _quantize_dt(target: int, allowed: List[int], default_dt: int, rounding_rule: str) -> int:
    if target <= 0:
        return 0
    values = [int(token) for token in list(allowed or []) if int(token) > 0]
    if not values:
        return max(1, int(default_dt))
    ordered = sorted(set(values))

    if str(rounding_rule) == "round.exact_only":
        if int(target) in ordered:
            return int(target)
        return max(1, int(default_dt))

    # round.nearest.lower_tie default:
    best = int(ordered[0])
    best_dist = abs(int(best) - int(target))
    for token in ordered[1:]:
        dist = abs(int(token) - int(target))
        if dist < best_dist:
            best = int(token)
            best_dist = int(dist)
            continue
        if dist == best_dist and int(token) < best:
            best = int(token)
            best_dist = int(dist)
    return max(1, int(best))


def _policy_from_context(policy_context: dict | None) -> dict:
    if not isinstance(policy_context, dict):
        return {}
    payload = policy_context.get("time_control_policy")
    return dict(payload) if isinstance(payload, dict) else {}


def _dt_rule_from_context(policy_context: dict | None) -> dict:
    if not isinstance(policy_context, dict):
        return {}
    payload = policy_context.get("dt_quantization_rule")
    return dict(payload) if isinstance(payload, dict) else {}


def _policy_rate_bounds(policy: dict) -> Tuple[int, int]:
    bounds = dict(policy.get("allowed_rate_range") or {}) if isinstance(policy.get("allowed_rate_range"), dict) else {}
    min_rate = max(0, _as_int(bounds.get("min", DEFAULT_RATE_PERMILLE), DEFAULT_RATE_PERMILLE))
    max_rate = max(0, _as_int(bounds.get("max", DEFAULT_RATE_PERMILLE), DEFAULT_RATE_PERMILLE))
    if max_rate < min_rate:
        max_rate = min_rate
    min_rate = min(int(min_rate), MAX_RATE_PERMILLE)
    max_rate = min(int(max_rate), MAX_RATE_PERMILLE)
    return int(min_rate), int(max_rate)


def _clamp(value: int, low: int, high: int) -> int:
    return min(max(int(value), int(low)), int(high))


def _resolved_rate_permille(control: dict, policy: dict) -> int:
    allow_rate_change = bool(policy.get("allow_rate_change", False))
    min_rate, max_rate = _policy_rate_bounds(policy)
    requested = max(0, _as_int(control.get("rate_permille", DEFAULT_RATE_PERMILLE), DEFAULT_RATE_PERMILLE))
    if not allow_rate_change:
        requested = max(min_rate, min(max_rate, DEFAULT_RATE_PERMILLE))
    return int(_clamp(requested, min_rate, max_rate))


def ensure_simulation_time(state: dict) -> dict:
    payload = state.get("simulation_time")
    if not isinstance(payload, dict):
        payload = {"tick": 0, "timestamp_utc": "1970-01-01T00:00:00Z"}
        state["simulation_time"] = payload
    payload["tick"] = int(normalize_tick_t(payload.get("tick", 0), 0))
    payload["timestamp_utc"] = str(payload.get("timestamp_utc", "1970-01-01T00:00:00Z"))
    payload["sim_time_permille"] = max(0, _as_int(payload.get("sim_time_permille", 0), 0))
    payload["last_dt_permille"] = max(0, _as_int(payload.get("last_dt_permille", DEFAULT_DT_PERMILLE), DEFAULT_DT_PERMILLE))
    return payload


def ensure_time_control(state: dict) -> dict:
    payload = state.get("time_control")
    if not isinstance(payload, dict):
        payload = {
            "rate_permille": DEFAULT_RATE_PERMILLE,
            "paused": False,
            "accumulator_permille": 0,
        }
        state["time_control"] = payload
    payload["rate_permille"] = max(0, _as_int(payload.get("rate_permille", DEFAULT_RATE_PERMILLE), DEFAULT_RATE_PERMILLE))
    payload["paused"] = bool(payload.get("paused", False))
    payload["accumulator_permille"] = max(0, _as_int(payload.get("accumulator_permille", 0), 0))
    payload["current_rate_permille"] = max(0, _as_int(payload.get("current_rate_permille", payload.get("rate_permille", DEFAULT_RATE_PERMILLE)), DEFAULT_RATE_PERMILLE))
    payload["current_dt_permille"] = max(0, _as_int(payload.get("current_dt_permille", DEFAULT_DT_PERMILLE), DEFAULT_DT_PERMILLE))
    payload["time_control_policy_id"] = str(payload.get("time_control_policy_id", DEFAULT_TIME_CONTROL_POLICY_ID) or DEFAULT_TIME_CONTROL_POLICY_ID)
    payload["dt_rule_id"] = str(payload.get("dt_rule_id", DEFAULT_DT_RULE_ID) or DEFAULT_DT_RULE_ID)
    return payload


def policy_allows_pause(policy_context: dict | None) -> bool:
    policy = _policy_from_context(policy_context)
    if not policy:
        return True
    return bool(policy.get("allow_pause", False))


def policy_allows_rate_change(policy_context: dict | None) -> bool:
    policy = _policy_from_context(policy_context)
    if not policy:
        return True
    return bool(policy.get("allow_rate_change", False))


def policy_rate_bounds(policy_context: dict | None) -> Tuple[int, int]:
    policy = _policy_from_context(policy_context)
    if not policy:
        return 0, MAX_RATE_PERMILLE
    return _policy_rate_bounds(policy)


def clamp_rate_to_policy(policy_context: dict | None, rate_permille: int) -> int:
    policy = _policy_from_context(policy_context)
    if not policy:
        return max(0, min(MAX_RATE_PERMILLE, _as_int(rate_permille, DEFAULT_RATE_PERMILLE)))
    min_rate, max_rate = _policy_rate_bounds(policy)
    return int(_clamp(_as_int(rate_permille, DEFAULT_RATE_PERMILLE), min_rate, max_rate))


def _tick_dt_permille(control: dict, policy: dict, dt_rule: dict) -> int:
    paused = bool(control.get("paused", False))
    allow_pause = bool(policy.get("allow_pause", True)) if policy else True
    if paused and allow_pause:
        return 0

    effective_rate = _resolved_rate_permille(control, policy)
    allow_variable_dt = bool(policy.get("allow_variable_dt", False)) if policy else False
    default_dt = max(1, _as_int(dt_rule.get("default_dt", DEFAULT_DT_PERMILLE), DEFAULT_DT_PERMILLE))
    allowed_dt = _allowed_dt_values(dt_rule)
    rounding_rule = str(dt_rule.get("deterministic_rounding_rule", DEFAULT_ROUNDING_RULE) or DEFAULT_ROUNDING_RULE)

    if not allow_variable_dt:
        return int(default_dt)

    requested_dt = max(1, int(int(default_dt) * int(effective_rate) // 1000))
    return int(_quantize_dt(requested_dt, allowed_dt, default_dt, rounding_rule))


def _time_tick_log(state: dict) -> List[dict]:
    rows = state.get("time_tick_log")
    if not isinstance(rows, list):
        rows = []
        state["time_tick_log"] = rows
    normalized: List[dict] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        tick = max(0, _as_int(row.get("tick", 0), 0))
        normalized.append(
            {
                "tick": int(tick),
                "dt_sim_permille": max(0, _as_int(row.get("dt_sim_permille", 0), 0)),
                "rate_permille": max(0, _as_int(row.get("rate_permille", DEFAULT_RATE_PERMILLE), DEFAULT_RATE_PERMILLE)),
                "paused": bool(row.get("paused", False)),
                "time_control_policy_id": str(row.get("time_control_policy_id", DEFAULT_TIME_CONTROL_POLICY_ID) or DEFAULT_TIME_CONTROL_POLICY_ID),
                "dt_rule_id": str(row.get("dt_rule_id", DEFAULT_DT_RULE_ID) or DEFAULT_DT_RULE_ID),
            }
        )
    normalized = sorted(normalized, key=lambda item: int(item.get("tick", 0)))
    state["time_tick_log"] = normalized[-MAX_TIME_TICK_LOG_ITEMS:]
    return state["time_tick_log"]


def advance_time(state: dict, policy_context: dict | None = None, steps: int = 1) -> dict:
    sim = ensure_simulation_time(state)
    control = ensure_time_control(state)
    policy = _policy_from_context(policy_context)
    dt_rule = _dt_rule_from_context(policy_context)
    log_rows = _time_tick_log(state)

    policy_id = str(
        (policy.get("time_control_policy_id") if isinstance(policy, dict) else "")
        or control.get("time_control_policy_id", DEFAULT_TIME_CONTROL_POLICY_ID)
        or DEFAULT_TIME_CONTROL_POLICY_ID
    )
    dt_rule_id = str(
        (dt_rule.get("dt_rule_id") if isinstance(dt_rule, dict) else "")
        or control.get("dt_rule_id", DEFAULT_DT_RULE_ID)
        or DEFAULT_DT_RULE_ID
    )

    step_count = max(0, int(steps))
    last_tick_meta = {
        "tick": int(sim.get("tick", 0)),
        "dt_sim_permille": int(sim.get("last_dt_permille", DEFAULT_DT_PERMILLE)),
        "rate_permille": int(control.get("rate_permille", DEFAULT_RATE_PERMILLE)),
        "paused": bool(control.get("paused", False)),
        "time_control_policy_id": policy_id,
        "dt_rule_id": dt_rule_id,
        "advanced": False,
    }

    for _ in range(step_count):
        if bool(control.get("paused", False)) and policy_allows_pause(policy_context):
            control["current_rate_permille"] = _resolved_rate_permille(control, policy)
            control["current_dt_permille"] = 0
            control["time_control_policy_id"] = policy_id
            control["dt_rule_id"] = dt_rule_id
            last_tick_meta = {
                "tick": int(sim.get("tick", 0)),
                "dt_sim_permille": 0,
                "rate_permille": int(control.get("current_rate_permille", DEFAULT_RATE_PERMILLE)),
                "paused": True,
                "time_control_policy_id": policy_id,
                "dt_rule_id": dt_rule_id,
                "advanced": False,
            }
            continue

        effective_rate = _resolved_rate_permille(control, policy)
        dt_permille = _tick_dt_permille(control, policy, dt_rule)

        try:
            next_tick: TickT = advance_tick_value(sim.get("tick", 0), 1)
        except TickOverflowImminentError:
            raise
        sim["tick"] = int(next_tick)
        sim["sim_time_permille"] = int(sim.get("sim_time_permille", 0)) + int(dt_permille)
        sim["last_dt_permille"] = int(dt_permille)

        control["current_rate_permille"] = int(effective_rate)
        control["current_dt_permille"] = int(dt_permille)
        control["time_control_policy_id"] = policy_id
        control["dt_rule_id"] = dt_rule_id

        tick_meta = {
            "tick": int(sim.get("tick", 0)),
            "dt_sim_permille": int(dt_permille),
            "rate_permille": int(effective_rate),
            "paused": bool(control.get("paused", False)),
            "time_control_policy_id": policy_id,
            "dt_rule_id": dt_rule_id,
        }
        log_rows.append(dict(tick_meta))
        if len(log_rows) > MAX_TIME_TICK_LOG_ITEMS:
            del log_rows[0 : len(log_rows) - MAX_TIME_TICK_LOG_ITEMS]
        last_tick_meta = dict(tick_meta)
        last_tick_meta["advanced"] = True

    state["time_tick_log"] = log_rows
    return last_tick_meta
