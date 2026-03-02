"""SIG-5 deterministic trust and belief engine."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


VERIFICATION_STATE_VERIFIED = "verified"
VERIFICATION_STATE_DISPUTED = "disputed"
VERIFICATION_STATE_FAILED = "failed"
VERIFICATION_STATE_UNVERIFIED = "unverified"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_float(value: object, default_value: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _clamp_weight(value: object, default_value: float = 0.5) -> float:
    token = _as_float(value, default_value)
    if token < 0.0:
        return 0.0
    if token > 1.0:
        return 1.0
    return float(token)


def _verification_state(value: object) -> str:
    token = str(value or "").strip().lower()
    if token in {VERIFICATION_STATE_VERIFIED, VERIFICATION_STATE_DISPUTED, VERIFICATION_STATE_FAILED}:
        return token
    return VERIFICATION_STATE_UNVERIFIED


def _with_fingerprint(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    payload["deterministic_fingerprint"] = ""
    out = dict(payload)
    out["deterministic_fingerprint"] = canonical_sha256(payload)
    return out


def _edge_sort_key(row: Mapping[str, object]) -> tuple[str, str]:
    payload = dict(row or {})
    return (
        str(payload.get("from_subject_id", "")).strip(),
        str(payload.get("to_subject_id", "")).strip(),
    )


def build_trust_edge(
    *,
    from_subject_id: str,
    to_subject_id: str,
    trust_weight: float,
    evidence_count: int,
    last_updated_tick: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "from_subject_id": str(from_subject_id or "").strip(),
        "to_subject_id": str(to_subject_id or "").strip(),
        "trust_weight": float(_clamp_weight(trust_weight, 0.5)),
        "evidence_count": int(max(0, _as_int(evidence_count, 0))),
        "last_updated_tick": int(max(0, _as_int(last_updated_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    if (not payload["from_subject_id"]) or (not payload["to_subject_id"]):
        return {}
    return _with_fingerprint(payload)


def normalize_trust_edge_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=_edge_sort_key):
        edge_row = build_trust_edge(
            from_subject_id=str(row.get("from_subject_id", "")).strip(),
            to_subject_id=str(row.get("to_subject_id", "")).strip(),
            trust_weight=_as_float(row.get("trust_weight", 0.5), 0.5),
            evidence_count=_as_int(row.get("evidence_count", 0), 0),
            last_updated_tick=_as_int(row.get("last_updated_tick", 0), 0),
            extensions=_as_map(row.get("extensions")),
        )
        if not edge_row:
            continue
        key = "{}::{}".format(edge_row["from_subject_id"], edge_row["to_subject_id"])
        out[key] = edge_row
    return [dict(out[key]) for key in sorted(out.keys())]


def build_trust_graph(
    *,
    graph_id: str,
    edges: object,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "graph_id": str(graph_id or "").strip(),
        "edges": normalize_trust_edge_rows(edges),
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    if not payload["graph_id"]:
        return {}
    return _with_fingerprint(payload)


def normalize_trust_graph_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("graph_id", ""))):
        graph_row = build_trust_graph(
            graph_id=str(row.get("graph_id", "")).strip(),
            edges=row.get("edges"),
            extensions=_as_map(row.get("extensions")),
        )
        graph_id = str(graph_row.get("graph_id", "")).strip()
        if graph_id:
            out[graph_id] = graph_row
    return [dict(out[key]) for key in sorted(out.keys())]


def trust_edge_rows_by_pair(rows: object) -> Dict[tuple[str, str], dict]:
    out: Dict[tuple[str, str], dict] = {}
    for row in normalize_trust_edge_rows(rows):
        key = (
            str(row.get("from_subject_id", "")).strip(),
            str(row.get("to_subject_id", "")).strip(),
        )
        if key[0] and key[1]:
            out[key] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def trust_weight_for_pair(
    *,
    trust_edge_rows: object,
    from_subject_id: str,
    to_subject_id: str,
    default_weight: float = 0.5,
) -> float:
    key = (str(from_subject_id or "").strip(), str(to_subject_id or "").strip())
    edge = dict(trust_edge_rows_by_pair(trust_edge_rows).get(key) or {})
    if not edge:
        return float(_clamp_weight(default_weight, 0.5))
    return float(_clamp_weight(edge.get("trust_weight", default_weight), default_weight))


def belief_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("belief_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("belief_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("belief_policy_id", ""))):
        belief_policy_id = str(row.get("belief_policy_id", "")).strip()
        if not belief_policy_id:
            continue
        out[belief_policy_id] = {
            "schema_version": "1.0.0",
            "belief_policy_id": belief_policy_id,
            "acceptance_threshold": float(_clamp_weight(row.get("acceptance_threshold", 0.5), 0.5)),
            "decay_rate_per_tick": float(_clamp_weight(row.get("decay_rate_per_tick", 0.0), 0.0)),
            "update_rule_id": str(row.get("update_rule_id", "")).strip() or "update.linear_adjust",
            "extensions": _as_map(row.get("extensions")),
        }
    if "belief.default" not in out:
        out["belief.default"] = {
            "schema_version": "1.0.0",
            "belief_policy_id": "belief.default",
            "acceptance_threshold": 0.5,
            "decay_rate_per_tick": 0.0,
            "update_rule_id": "update.linear_adjust",
            "extensions": {},
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def trust_update_rule_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("trust_update_rules")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("trust_update_rules")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("update_rule_id", ""))):
        update_rule_id = str(row.get("update_rule_id", "")).strip()
        if not update_rule_id:
            continue
        out[update_rule_id] = {
            "schema_version": "1.0.0",
            "update_rule_id": update_rule_id,
            "description": str(row.get("description", "")).strip(),
            "extensions": _as_map(row.get("extensions")),
        }
    if "update.linear_adjust" not in out:
        out["update.linear_adjust"] = {
            "schema_version": "1.0.0",
            "update_rule_id": "update.linear_adjust",
            "description": "default deterministic fixed-step adjustment",
            "extensions": {
                "model": "linear_adjust",
                "delta_verified": 0.1,
                "delta_disputed": -0.08,
                "delta_failed": -0.15,
            },
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def deterministic_verification_result_id(
    *,
    artifact_id: str,
    verifier_subject_id: str,
    verification_state: str,
    tick: int,
) -> str:
    digest = canonical_sha256(
        {
            "artifact_id": str(artifact_id or "").strip(),
            "verifier_subject_id": str(verifier_subject_id or "").strip(),
            "verification_state": _verification_state(verification_state),
            "tick": int(max(0, _as_int(tick, 0))),
        }
    )
    return "verification.{}".format(digest[:16])


def build_verification_result(
    *,
    result_id: str,
    artifact_id: str,
    verifier_subject_id: str,
    verification_state: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "result_id": str(result_id or "").strip(),
        "artifact_id": str(artifact_id or "").strip(),
        "verifier_subject_id": str(verifier_subject_id or "").strip(),
        "verification_state": _verification_state(verification_state),
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    if (not payload["result_id"]) or (not payload["artifact_id"]) or (not payload["verifier_subject_id"]):
        return {}
    return _with_fingerprint(payload)


def normalize_verification_result_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("result_id", ""))):
        result_row = build_verification_result(
            result_id=str(row.get("result_id", "")).strip(),
            artifact_id=str(row.get("artifact_id", "")).strip(),
            verifier_subject_id=str(row.get("verifier_subject_id", "")).strip(),
            verification_state=str(row.get("verification_state", VERIFICATION_STATE_UNVERIFIED)).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        result_id = str(result_row.get("result_id", "")).strip()
        if result_id:
            out[result_id] = result_row
    return [dict(out[key]) for key in sorted(out.keys())]


def trust_delta_from_verification(
    *,
    verification_state: str,
    update_rule_row: Mapping[str, object],
    evidence_count: int,
) -> float:
    state_token = _verification_state(verification_state)
    ext = _as_map(update_rule_row.get("extensions"))
    base_delta = 0.0
    if state_token == VERIFICATION_STATE_VERIFIED:
        base_delta = _as_float(ext.get("delta_verified", 0.1), 0.1)
    elif state_token == VERIFICATION_STATE_DISPUTED:
        base_delta = _as_float(ext.get("delta_disputed", -0.08), -0.08)
    elif state_token == VERIFICATION_STATE_FAILED:
        base_delta = _as_float(ext.get("delta_failed", -0.15), -0.15)
    model = str(ext.get("model", "")).strip().lower() or "linear_adjust"
    if model == "bayesian_stub":
        return float(base_delta / float(max(1, int(max(0, _as_int(evidence_count, 0))) + 1)))
    return float(base_delta)


def _upsert_edge_row(rows: object, row: Mapping[str, object]) -> List[dict]:
    target = dict(row or {})
    key = "{}::{}".format(
        str(target.get("from_subject_id", "")).strip(),
        str(target.get("to_subject_id", "")).strip(),
    )
    if not str(target.get("from_subject_id", "")).strip() or not str(target.get("to_subject_id", "")).strip():
        return normalize_trust_edge_rows(rows)
    out: Dict[str, dict] = {}
    for item in normalize_trust_edge_rows(rows):
        edge_key = "{}::{}".format(
            str(item.get("from_subject_id", "")).strip(),
            str(item.get("to_subject_id", "")).strip(),
        )
        out[edge_key] = dict(item)
    out[key] = build_trust_edge(
        from_subject_id=str(target.get("from_subject_id", "")).strip(),
        to_subject_id=str(target.get("to_subject_id", "")).strip(),
        trust_weight=_as_float(target.get("trust_weight", 0.5), 0.5),
        evidence_count=_as_int(target.get("evidence_count", 0), 0),
        last_updated_tick=_as_int(target.get("last_updated_tick", 0), 0),
        extensions=_as_map(target.get("extensions")),
    )
    return [dict(out[item]) for item in sorted(out.keys()) if out[item]]


def evaluate_receipt_acceptance(
    *,
    trust_weight: float,
    belief_policy_row: Mapping[str, object] | None,
) -> dict:
    policy = dict(belief_policy_row or {})
    threshold = float(_clamp_weight(policy.get("acceptance_threshold", 0.5), 0.5))
    weight = float(_clamp_weight(trust_weight, 0.5))
    accepted = bool(weight >= threshold)
    return {
        "accepted": accepted,
        "acceptance_threshold": threshold,
        "trust_weight": weight,
    }


def process_trust_update(
    *,
    current_tick: int,
    from_subject_id: str,
    to_subject_id: str,
    verification_result_row: Mapping[str, object],
    trust_edge_rows: object,
    belief_policy_registry: Mapping[str, object] | None,
    trust_update_rule_registry: Mapping[str, object] | None,
    belief_policy_id: str = "belief.default",
    decision_log_rows: object = None,
) -> dict:
    from_token = str(from_subject_id or "").strip()
    to_token = str(to_subject_id or "").strip()
    if (not from_token) or (not to_token):
        return {
            "trust_edge_rows": normalize_trust_edge_rows(trust_edge_rows),
            "updated_edge_row": None,
            "decision_log_rows": [dict(item) for item in list(decision_log_rows or []) if isinstance(item, Mapping)],
            "decision_log_entry": None,
        }

    policies = belief_policy_rows_by_id(belief_policy_registry)
    policy = dict(policies.get(str(belief_policy_id or "").strip()) or policies.get("belief.default") or {})
    update_rules = trust_update_rule_rows_by_id(trust_update_rule_registry)
    update_rule = dict(update_rules.get(str(policy.get("update_rule_id", "")).strip()) or update_rules.get("update.linear_adjust") or {})

    edges_by_pair = trust_edge_rows_by_pair(trust_edge_rows)
    current_edge = dict(edges_by_pair.get((from_token, to_token)) or {})
    old_weight = float(_clamp_weight(current_edge.get("trust_weight", policy.get("extensions", {}).get("initial_trust_weight", 0.5)), 0.5))
    old_evidence = int(max(0, _as_int(current_edge.get("evidence_count", 0), 0)))

    verification_state = _verification_state(dict(verification_result_row or {}).get("verification_state"))
    delta = trust_delta_from_verification(
        verification_state=verification_state,
        update_rule_row=update_rule,
        evidence_count=old_evidence,
    )
    new_weight = float(_clamp_weight(old_weight + float(delta), old_weight))
    new_evidence = int(old_evidence + 1)

    updated_edge = build_trust_edge(
        from_subject_id=from_token,
        to_subject_id=to_token,
        trust_weight=new_weight,
        evidence_count=new_evidence,
        last_updated_tick=int(max(0, _as_int(current_tick, 0))),
        extensions={
            **_as_map(current_edge.get("extensions")),
            "last_verification_state": verification_state,
            "last_verification_result_id": str(dict(verification_result_row or {}).get("result_id", "")).strip() or None,
            "last_delta": float(delta),
        },
    )
    next_edges = _upsert_edge_row(trust_edge_rows, updated_edge)

    decision_entry = {
        "decision_id": "decision.trust_update.{}".format(
            canonical_sha256(
                {
                    "tick": int(max(0, _as_int(current_tick, 0))),
                    "from_subject_id": from_token,
                    "to_subject_id": to_token,
                    "verification_result_id": str(dict(verification_result_row or {}).get("result_id", "")).strip(),
                    "verification_state": verification_state,
                }
            )[:16]
        ),
        "tick": int(max(0, _as_int(current_tick, 0))),
        "process_id": "process.trust_update",
        "from_subject_id": from_token,
        "to_subject_id": to_token,
        "belief_policy_id": str(policy.get("belief_policy_id", "belief.default")).strip() or "belief.default",
        "update_rule_id": str(update_rule.get("update_rule_id", "update.linear_adjust")).strip() or "update.linear_adjust",
        "verification_result_id": str(dict(verification_result_row or {}).get("result_id", "")).strip() or None,
        "verification_state": verification_state,
        "trust_weight_before": float(old_weight),
        "trust_weight_after": float(new_weight),
        "evidence_count_before": int(old_evidence),
        "evidence_count_after": int(new_evidence),
        "extensions": {},
    }
    decisions = [dict(item) for item in list(decision_log_rows or []) if isinstance(item, Mapping)]
    by_id = dict(
        (str(item.get("decision_id", "")).strip(), dict(item))
        for item in decisions
        if str(item.get("decision_id", "")).strip()
    )
    by_id[str(decision_entry["decision_id"]).strip()] = dict(decision_entry)
    next_decisions = [dict(by_id[key]) for key in sorted(by_id.keys())]
    return {
        "trust_edge_rows": next_edges,
        "updated_edge_row": dict(updated_edge),
        "decision_log_rows": next_decisions,
        "decision_log_entry": dict(decision_entry),
    }


def process_trust_decay_tick(
    *,
    current_tick: int,
    trust_edge_rows: object,
    belief_policy_registry: Mapping[str, object] | None,
    belief_policy_id: str = "belief.default",
    max_updates: int | None = None,
) -> dict:
    policies = belief_policy_rows_by_id(belief_policy_registry)
    policy = dict(policies.get(str(belief_policy_id or "").strip()) or policies.get("belief.default") or {})
    decay_rate = float(_clamp_weight(policy.get("decay_rate_per_tick", 0.0), 0.0))

    sorted_edges = normalize_trust_edge_rows(trust_edge_rows)
    if int(max_updates or 0) > 0:
        processed = sorted_edges[: int(max_updates)]
        deferred = sorted_edges[int(max_updates) :]
    else:
        processed = list(sorted_edges)
        deferred = []

    decayed: List[dict] = []
    for edge in processed:
        row = dict(edge)
        old_weight = float(_clamp_weight(row.get("trust_weight", 0.5), 0.5))
        new_weight = float(_clamp_weight(old_weight * (1.0 - decay_rate), old_weight))
        decayed_row = build_trust_edge(
            from_subject_id=str(row.get("from_subject_id", "")).strip(),
            to_subject_id=str(row.get("to_subject_id", "")).strip(),
            trust_weight=new_weight,
            evidence_count=int(max(0, _as_int(row.get("evidence_count", 0), 0))),
            last_updated_tick=int(max(0, _as_int(current_tick, 0))),
            extensions={
                **_as_map(row.get("extensions")),
                "decayed": bool(decay_rate > 0.0),
                "decay_rate_per_tick": float(decay_rate),
                "previous_trust_weight": float(old_weight),
            },
        )
        if decayed_row:
            decayed.append(decayed_row)

    next_rows = normalize_trust_edge_rows(decayed + deferred)
    return {
        "trust_edge_rows": next_rows,
        "decayed_count": int(len(decayed)),
        "deferred_count": int(len(deferred)),
        "belief_policy_id": str(policy.get("belief_policy_id", "belief.default")).strip() or "belief.default",
        "decay_rate_per_tick": float(decay_rate),
    }


__all__ = [
    "VERIFICATION_STATE_DISPUTED",
    "VERIFICATION_STATE_FAILED",
    "VERIFICATION_STATE_UNVERIFIED",
    "VERIFICATION_STATE_VERIFIED",
    "belief_policy_rows_by_id",
    "build_trust_edge",
    "build_trust_graph",
    "build_verification_result",
    "deterministic_verification_result_id",
    "evaluate_receipt_acceptance",
    "normalize_trust_edge_rows",
    "normalize_trust_graph_rows",
    "normalize_verification_result_rows",
    "process_trust_decay_tick",
    "process_trust_update",
    "trust_delta_from_verification",
    "trust_edge_rows_by_pair",
    "trust_update_rule_rows_by_id",
    "trust_weight_for_pair",
]
