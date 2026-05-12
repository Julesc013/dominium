"""Deterministic worldgen planning pipeline stages for constraint resolution."""

from __future__ import annotations

from typing import Dict, List

from .constraint_solver import solve_constraints


def run_worldgen_pipeline(
    repo_root: str,
    base_seed: str,
    module_registry_payload: dict,
    constraints_payload: dict | None = None,
) -> Dict[str, object]:
    """Run structural worldgen pipeline stage flow without committing runtime artifacts."""
    stage_log: List[dict] = []
    stage_log.append(
        {
            "stage_id": "stage.resolve_modules",
            "status": "pass",
            "message": "module registry loaded for deterministic DAG resolution",
        }
    )

    selected_seed = str(base_seed)
    search_plan = {}
    if isinstance(constraints_payload, dict):
        stage_log.append(
            {
                "stage_id": "stage.resolve_constraints",
                "status": "in_progress",
                "message": "evaluating deterministic candidate seeds",
            }
        )
        solved = solve_constraints(
            repo_root=repo_root,
            constraints_payload=constraints_payload,
            module_registry_payload=module_registry_payload,
            base_seed=str(base_seed),
        )
        if solved.get("result") != "complete":
            stage_log.append(
                {
                    "stage_id": "stage.resolve_constraints",
                    "status": "refused",
                    "message": str(((solved.get("refusal") or {}).get("reason_code", "refusal.constraints_unsatisfiable"))),
                }
            )
            return solved
        search_plan = dict(solved.get("search_plan") or {})
        selected_seed = str(search_plan.get("selected_seed", "")).strip() or str(base_seed)
        stage_log[-1]["status"] = "pass"
        stage_log[-1]["message"] = "constraints resolved deterministically"

    stage_log.append(
        {
            "stage_id": "stage.compile_world_artifacts",
            "status": "pass",
            "message": "artifact compile stage prepared with selected seed",
        }
    )
    return {
        "result": "complete",
        "selected_seed": str(selected_seed),
        "search_plan": search_plan,
        "stage_log": stage_log,
    }

