"""FAST test: XI-4 never auto-applies core-concept convergence outside the planned canonical path."""

from __future__ import annotations


TEST_ID = "test_canonical_paths_used_for_core_concepts_smoke"
TEST_TAGS = ["fast", "xi", "convergence", "smoke"]


CORE_RISK_REASONS = {
    "ipc_attach",
    "pack_compat_install_resolver",
    "protocol_negotiation",
    "semantic_contracts",
    "time_anchor",
    "trust_enforcement",
    "worldgen_lock_or_overlay",
}


def run(repo_root: str):
    from tools.xstack.testx.tests.convergence_execution_testlib import committed_convergence_execution_log, committed_convergence_plan

    execution_log = committed_convergence_execution_log(repo_root)
    convergence_plan = committed_convergence_plan(repo_root)
    cluster_canonical = {}
    for row in list(convergence_plan.get("clusters") or []):
        if not isinstance(row, dict):
            continue
        cluster_id = str(row.get("cluster_id", "")).strip()
        canonical_file = str(dict(row.get("canonical_candidate") or {}).get("file_path", "")).replace("\\", "/").strip()
        if cluster_id and canonical_file:
            cluster_canonical[cluster_id] = canonical_file

    offenders = []
    for row in list(execution_log.get("entries") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("result", "")).strip() != "applied":
            continue
        if str(row.get("kind", "")).strip() not in {"keep", "merge", "rewire", "deprecate"}:
            continue
        risk_reasons = {str(item).strip() for item in list(row.get("risk_reasons") or []) if str(item).strip()}
        if not (risk_reasons & CORE_RISK_REASONS):
            continue
        cluster_id = str(row.get("cluster_id", "")).strip()
        canonical_file = str(row.get("canonical_file", "")).replace("\\", "/").strip()
        if cluster_canonical.get(cluster_id) != canonical_file:
            offenders.append(cluster_id or canonical_file)
    if offenders:
        return {"status": "fail", "message": "core-concept applied actions drifted from the planned canonical path: {}".format(", ".join(offenders[:6]))}
    return {"status": "pass", "message": "core-concept applied actions stay on the planned canonical path"}
