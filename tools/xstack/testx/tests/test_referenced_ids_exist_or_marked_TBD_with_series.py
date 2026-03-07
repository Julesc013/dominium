"""FAST test: referenced IDs resolve to registries or are explicit TBD with next_series."""

from __future__ import annotations


TEST_ID = "test_referenced_ids_exist_or_marked_TBD_with_series"
TEST_TAGS = ["fast", "meta", "genre", "matrix", "linkage"]


def _valid_or_tbd(token: str, known: set[str], next_series: str) -> bool:
    value = str(token or "").strip()
    if not value:
        return False
    if value in known:
        return True
    if value.startswith("TBD:") and str(next_series or "").strip():
        return True
    return False


def run(repo_root: str):
    from tools.xstack.testx.tests import meta_genre0_testlib

    payload, err = meta_genre0_testlib.load_matrix(repo_root)
    if err:
        return {"status": "fail", "message": "matrix payload missing or invalid"}
    demands = meta_genre0_testlib.matrix_demands(payload)
    known = meta_genre0_testlib.known_reference_ids(repo_root)

    for row in demands:
        demand_id = str(row.get("demand_id", "")).strip()
        next_series = str(row.get("next_series", "")).strip()
        for token in list(row.get("action_families") or []):
            if not _valid_or_tbd(token, known["action_families"], next_series):
                return {"status": "fail", "message": "{} invalid action_family ref: {}".format(demand_id, token)}
        for token in list(row.get("action_templates") or []):
            if not _valid_or_tbd(token, known["action_templates"], next_series):
                return {"status": "fail", "message": "{} invalid action_template ref: {}".format(demand_id, token)}
        for token in list(row.get("explain") or []):
            if not _valid_or_tbd(token, known["explain_contracts"], next_series):
                return {"status": "fail", "message": "{} invalid explain ref: {}".format(demand_id, token)}
        for token in list(row.get("rwam_affordances") or []):
            if not _valid_or_tbd(token, known["rwam_affordances"], next_series):
                return {"status": "fail", "message": "{} invalid rwam_affordance ref: {}".format(demand_id, token)}
        break_rules = dict(row.get("break_rules") or {})
        for token in list(break_rules.get("profiles") or []):
            if (
                not _valid_or_tbd(token, known["law_profiles"], next_series)
                and not _valid_or_tbd(token, known["physics_profiles"], next_series)
            ):
                return {"status": "fail", "message": "{} invalid profile ref: {}".format(demand_id, token)}
    return {"status": "pass", "message": "matrix references resolve or are explicit TBD"}
