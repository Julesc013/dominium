"""FAST test: player demand matrix payload matches required structural contract."""

from __future__ import annotations

import os


TEST_ID = "test_player_demand_matrix_schema_valid"
TEST_TAGS = ["fast", "meta", "genre", "matrix", "schema"]


def run(repo_root: str):
    from tools.xstack.testx.tests import meta_genre0_testlib

    payload, err = meta_genre0_testlib.load_matrix(repo_root)
    if err:
        return {"status": "fail", "message": "matrix payload missing or invalid: {}".format(err)}
    if str(payload.get("version", "")).strip() != "1.0.0":
        return {"status": "fail", "message": "matrix version must be 1.0.0"}

    demands = meta_genre0_testlib.matrix_demands(payload)
    if not demands:
        return {"status": "fail", "message": "matrix demands list is empty"}

    required_fields = {
        "demand_id",
        "title",
        "fantasy",
        "clusters",
        "verbs",
        "action_families",
        "action_templates",
        "proc",
        "sys",
        "sig_logic",
        "domains",
        "tiers",
        "epistemics",
        "break_rules",
        "collapse",
        "explain",
        "rwam_affordances",
        "coverage_status",
        "next_series",
        "notes",
        "deterministic_fingerprint",
    }
    for row in demands:
        missing = sorted(field for field in required_fields if field not in row)
        if missing:
            return {
                "status": "fail",
                "message": "demand {} missing required fields: {}".format(
                    str(row.get("demand_id", "<unknown>")),
                    ",".join(missing),
                ),
            }
        for list_field in (
            "clusters",
            "verbs",
            "action_families",
            "action_templates",
            "domains",
            "tiers",
            "explain",
            "rwam_affordances",
        ):
            if not isinstance(row.get(list_field), list):
                return {
                    "status": "fail",
                    "message": "demand {} field {} must be list".format(
                        str(row.get("demand_id", "<unknown>")),
                        list_field,
                    ),
                }
        for map_field in ("proc", "sys", "sig_logic", "epistemics", "break_rules", "collapse"):
            if not isinstance(row.get(map_field), dict):
                return {
                    "status": "fail",
                    "message": "demand {} field {} must be map".format(
                        str(row.get("demand_id", "<unknown>")),
                        map_field,
                    ),
                }

    schema_rel = "schema/meta/player_demand_matrix.schema"
    if not os.path.isfile(os.path.join(repo_root, schema_rel.replace("/", os.sep))):
        return {"status": "fail", "message": "{} missing".format(schema_rel)}
    return {"status": "pass", "message": "player demand matrix shape valid"}
