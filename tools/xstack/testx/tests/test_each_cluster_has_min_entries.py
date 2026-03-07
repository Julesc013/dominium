"""FAST test: each demand cluster has at least ten entries."""

from __future__ import annotations

from collections import Counter


TEST_ID = "test_each_cluster_has_min_entries"
TEST_TAGS = ["fast", "meta", "genre", "matrix", "clusters"]


REQUIRED_CLUSTERS = {
    "survival_primitive_tech",
    "crafting_engineering_realism",
    "factory_automation",
    "cities_infrastructure",
    "transport_logistics",
    "space_engineering",
    "cyber_automation_hacking",
    "military_defense_sabotage",
    "science_research_invention",
    "sandbox_creative_magic_alt_physics",
}


def run(repo_root: str):
    from tools.xstack.testx.tests import meta_genre0_testlib

    payload, err = meta_genre0_testlib.load_matrix(repo_root)
    if err:
        return {"status": "fail", "message": "matrix payload missing or invalid"}
    demands = meta_genre0_testlib.matrix_demands(payload)

    counts = Counter()
    for row in demands:
        for cluster_id in list(row.get("clusters") or []):
            token = str(cluster_id).strip()
            if token:
                counts[token] += 1

    missing_clusters = sorted(cluster_id for cluster_id in REQUIRED_CLUSTERS if counts[cluster_id] < 10)
    if missing_clusters:
        return {
            "status": "fail",
            "message": "cluster minimum entries missing: {}".format(
                ",".join("{}={}".format(cid, counts[cid]) for cid in missing_clusters)
            ),
        }
    return {"status": "pass", "message": "all required clusters meet minimum entries"}
