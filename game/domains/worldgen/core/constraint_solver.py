"""Deterministic worldgen constraints solver and multi-seed search planner."""

from __future__ import annotations

import hashlib
from typing import Dict, List, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance

from .module_resolver import resolve_worldgen_module_order


def _refusal(reason_code: str, message: str, remediation_hint: str, relevant_ids: Dict[str, str], path: str = "$") -> Dict[str, object]:
    return {
        "result": "refused",
        "refusal": {
            "reason_code": str(reason_code),
            "message": str(message),
            "remediation_hint": str(remediation_hint),
            "relevant_ids": dict(sorted((relevant_ids or {}).items(), key=lambda item: str(item[0]))),
        },
        "errors": [
            {
                "code": str(reason_code),
                "message": str(message),
                "path": str(path),
            }
        ],
    }


def _to_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _stable_metric(seed: str, module_order: List[str], target: str, universe_scope: str) -> int:
    digest = hashlib.sha256(
        "{}|{}|{}|{}".format(
            str(seed),
            ",".join(str(item) for item in module_order),
            str(target),
            str(universe_scope),
        ).encode("utf-8")
    ).hexdigest()
    return int(digest[:16], 16) % 10000


def deterministic_candidate_seeds(base_seed: str, candidate_count: int, deterministic_seed_policy: str) -> List[str]:
    """Generate deterministic candidate seed list for single or multi policy."""
    base = str(base_seed).strip()
    count = max(1, _to_int(candidate_count, 1))
    policy = str(deterministic_seed_policy).strip()
    if policy == "single":
        return [base]
    rows = []
    for index in range(count):
        digest = hashlib.sha256(
            "rng.worldgen.constraints.search|{}|{}".format(base, index).encode("utf-8")
        ).hexdigest()
        rows.append(digest[:16])
    return rows


def _constraint_passes(constraint: dict, metric_value: int) -> Tuple[bool, str]:
    operator = str(constraint.get("operator", "")).strip()
    value = constraint.get("value")
    if operator == "eq":
        return (metric_value == _to_int(value, -1), "")
    if operator == "range":
        if not isinstance(value, dict):
            return False, "range operator requires object value with min/max"
        min_value = _to_int(value.get("min"), -(1 << 30))
        max_value = _to_int(value.get("max"), 1 << 30)
        return (min_value <= metric_value <= max_value, "")
    if operator == "min":
        return (metric_value >= _to_int(value, 0), "")
    if operator == "max":
        return (metric_value <= _to_int(value, 0), "")
    if operator == "set_membership":
        if isinstance(value, list):
            members = sorted(set(str(item).strip() for item in value if str(item).strip()))
            return (str(metric_value) in members, "")
        return (str(metric_value) == str(value), "")
    if operator == "custom_tag":
        threshold = _to_int(value, 0)
        return (metric_value % 100 >= threshold, "")
    return (False, "unsupported operator '{}'".format(operator))


def _soft_constraint_score(constraint: dict, metric_value: int) -> Tuple[int, str]:
    passed, error = _constraint_passes(constraint, metric_value)
    if error:
        return 0, error
    weight = _to_int(constraint.get("weight"), 0)
    if passed:
        return weight * 100, ""
    return -weight * 100, ""


def _scoring_function_score(scoring: dict, metric_value: int) -> Tuple[int, str]:
    operator = str(scoring.get("operator", "")).strip()
    weight = _to_int(scoring.get("weight"), 0)
    if operator == "maximize":
        return weight * metric_value, ""
    if operator == "minimize":
        return weight * (10000 - metric_value), ""
    if operator == "target":
        target_value = _to_int(scoring.get("target_value"), 0)
        return max(0, weight * (10000 - abs(metric_value - target_value))), ""
    return 0, "unsupported scoring operator '{}'".format(operator)


def _candidate_preview_metrics(seed: str, module_order: List[str], constraints_payload: dict) -> Dict[str, int]:
    scope = str(constraints_payload.get("universe_scope", "")).strip()
    targets = []
    for row in constraints_payload.get("hard_constraints") or []:
        if isinstance(row, dict):
            targets.append(str(row.get("target", "")).strip())
    for row in constraints_payload.get("soft_constraints") or []:
        if isinstance(row, dict):
            targets.append(str(row.get("target", "")).strip())
    for row in constraints_payload.get("scoring_functions") or []:
        if isinstance(row, dict):
            targets.append(str(row.get("metric", "")).strip())
    targets = sorted(set(token for token in targets if token))
    metrics = {}
    for target in targets:
        metrics[target] = _stable_metric(
            seed=seed,
            module_order=module_order,
            target=target,
            universe_scope=scope,
        )
    return metrics


def _rank_candidates(candidates: List[dict], tie_break_policy: str, tie_break_field: str) -> List[dict]:
    policy = str(tie_break_policy).strip()
    field_name = str(tie_break_field).strip()

    def tie_key(row: dict):
        seed = str(row.get("seed", ""))
        order_index = _to_int(row.get("seed_order"), 0)
        metrics = row.get("metrics") if isinstance(row.get("metrics"), dict) else {}
        explicit_metric = metrics.get(field_name)
        if policy == "seed_order":
            return (order_index, seed)
        if policy == "explicit_field":
            if isinstance(explicit_metric, (int, float)):
                return (-int(explicit_metric), seed)
            return (str(explicit_metric), seed)
        return (seed,)

    ranked = sorted(
        candidates,
        key=lambda row: (
            -_to_int(row.get("soft_score"), 0),
            -_to_int(row.get("hard_pass_count"), 0),
            tie_key(row),
        ),
    )
    for index, row in enumerate(ranked, start=1):
        row["rank"] = index
    return ranked


def build_worldgen_search_plan(
    repo_root: str,
    constraints_payload: dict,
    base_seed: str,
    module_order: List[str],
) -> Dict[str, object]:
    """Build deterministic search plan for a validated constraints payload."""
    constraints_valid = validate_instance(
        repo_root=repo_root,
        schema_name="worldgen_constraints",
        payload=constraints_payload,
        strict_top_level=True,
    )
    if not bool(constraints_valid.get("valid", False)):
        return _refusal(
            "refusal.constraints_invalid",
            "worldgen constraints payload failed schema validation",
            "Fix constraints artifact to satisfy schemas/worldgen_constraints.schema.json.",
            {"constraints_id": str(constraints_payload.get("constraints_id", ""))},
            "$.worldgen_constraints",
        )

    constraints_id = str(constraints_payload.get("constraints_id", "")).strip()
    policy = str(constraints_payload.get("deterministic_seed_policy", "")).strip()
    candidate_count = _to_int(constraints_payload.get("candidate_count"), 0)
    tie_break_policy = str(constraints_payload.get("tie_break_policy", "")).strip()
    tie_break_field = str(constraints_payload.get("tie_break_field", "")).strip()
    if policy == "single" and candidate_count != 1:
        return _refusal(
            "refusal.seed_policy_invalid",
            "single deterministic_seed_policy requires candidate_count == 1",
            "Set candidate_count to 1 for deterministic_seed_policy=single.",
            {"constraints_id": constraints_id},
            "$.candidate_count",
        )
    if candidate_count <= 0:
        return _refusal(
            "refusal.search_exhausted",
            "candidate_count exhausted before search evaluation",
            "Set candidate_count >= 1.",
            {"constraints_id": constraints_id},
            "$.candidate_count",
        )

    hard_constraints = [row for row in (constraints_payload.get("hard_constraints") or []) if isinstance(row, dict)]
    soft_constraints = [row for row in (constraints_payload.get("soft_constraints") or []) if isinstance(row, dict)]
    scoring_functions = [row for row in (constraints_payload.get("scoring_functions") or []) if isinstance(row, dict)]

    seeds = deterministic_candidate_seeds(
        base_seed=base_seed,
        candidate_count=candidate_count,
        deterministic_seed_policy=policy,
    )
    candidate_rows = []
    for index, seed in enumerate(seeds):
        metrics = _candidate_preview_metrics(seed=seed, module_order=module_order, constraints_payload=constraints_payload)
        hard_failures = []
        hard_pass_count = 0
        for hard in hard_constraints:
            target = str(hard.get("target", "")).strip()
            metric_value = _to_int(metrics.get(target), 0)
            passed, error = _constraint_passes(hard, metric_value)
            if error:
                hard_failures.append("{}:{}".format(str(hard.get("constraint_id", "")), error))
                continue
            if passed:
                hard_pass_count += 1
            else:
                hard_failures.append(str(hard.get("constraint_id", "")))
        hard_pass = len(hard_failures) == 0

        soft_score = 0
        for soft in soft_constraints:
            target = str(soft.get("target", "")).strip()
            metric_value = _to_int(metrics.get(target), 0)
            delta, error = _soft_constraint_score(soft, metric_value)
            if error:
                hard_pass = False
                hard_failures.append("{}:{}".format(str(soft.get("constraint_id", "")), error))
                continue
            soft_score += int(delta)
        for scoring in scoring_functions:
            metric_name = str(scoring.get("metric", "")).strip()
            metric_value = _to_int(metrics.get(metric_name), 0)
            delta, error = _scoring_function_score(scoring, metric_value)
            if error:
                hard_pass = False
                hard_failures.append("{}:{}".format(str(scoring.get("scoring_id", "")), error))
                continue
            soft_score += int(delta)

        candidate_rows.append(
            {
                "seed": seed,
                "seed_order": index,
                "metrics": metrics,
                "hard_pass": bool(hard_pass),
                "hard_failures": sorted(set(str(item) for item in hard_failures if str(item))),
                "hard_pass_count": int(hard_pass_count),
                "soft_score": int(soft_score),
            }
        )

    eligible = [row for row in candidate_rows if bool(row.get("hard_pass"))]
    if not eligible:
        refusal_code = "refusal.constraints_unsatisfiable" if hard_constraints else "refusal.search_exhausted"
        message = "no candidate satisfied hard constraints" if hard_constraints else "no candidate available after deterministic expansion"
        return _refusal(
            refusal_code,
            message,
            "Relax constraints or increase candidate_count.",
            {"constraints_id": constraints_id},
            "$.candidate_seeds",
        )

    ranked = _rank_candidates(eligible, tie_break_policy=tie_break_policy, tie_break_field=tie_break_field)
    selected = ranked[0]
    scoring_summary = {
        "candidate_results": [
            {
                "seed": str(row.get("seed", "")),
                "hard_pass": bool(row.get("hard_pass")),
                "hard_failures": list(row.get("hard_failures") or []),
                "soft_score": int(row.get("soft_score", 0) or 0),
                "rank": int(row.get("rank", 0) or 0),
            }
            for row in ranked
        ],
        "hard_constraint_failures": int(sum(1 for row in candidate_rows if not bool(row.get("hard_pass")))),
        "soft_score_totals": [
            {
                "seed": str(row.get("seed", "")),
                "score": int(row.get("soft_score", 0) or 0),
            }
            for row in ranked
        ],
    }
    plan = {
        "schema_version": "1.0.0",
        "plan_id": "plan.{}".format(constraints_id),
        "base_seed": str(base_seed),
        "candidate_seeds": [str(seed) for seed in seeds],
        "constraints_id": constraints_id,
        "module_order": [str(item) for item in module_order],
        "scoring_summary": scoring_summary,
        "selected_seed": str(selected.get("seed", "")),
        "deterministic_hash": "",
    }
    deterministic_hash = canonical_sha256(dict(plan, deterministic_hash=""))
    plan["deterministic_hash"] = deterministic_hash

    plan_valid = validate_instance(
        repo_root=repo_root,
        schema_name="worldgen_search_plan",
        payload=plan,
        strict_top_level=True,
    )
    if not bool(plan_valid.get("valid", False)):
        return _refusal(
            "refusal.search_plan_invalid",
            "generated worldgen search plan failed schema validation",
            "Inspect scoring summary and module order serialization for schema compliance.",
            {"constraints_id": constraints_id},
            "$.worldgen_search_plan",
        )

    return {
        "result": "complete",
        "search_plan": plan,
    }


def solve_constraints(
    repo_root: str,
    constraints_payload: dict,
    module_registry_payload: dict,
    base_seed: str,
) -> Dict[str, object]:
    """Resolve module DAG + deterministic candidate search and return search plan."""
    resolved = resolve_worldgen_module_order(registry_payload=module_registry_payload, include_experimental=True)
    if resolved.get("result") != "complete":
        return resolved
    return build_worldgen_search_plan(
        repo_root=repo_root,
        constraints_payload=constraints_payload,
        base_seed=base_seed,
        module_order=list(resolved.get("module_order") or []),
    )

