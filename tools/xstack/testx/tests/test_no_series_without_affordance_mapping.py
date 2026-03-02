"""STRICT test: every discovered series has RWAM affordance mapping."""

from __future__ import annotations

import json
import os
import re


TEST_ID = "test_no_series_without_affordance_mapping"
TEST_TAGS = ["strict", "meta", "affordance", "rwam"]


def _load_json(path: str):
    try:
        return json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def run(repo_root: str):
    matrix_rel = "data/meta/real_world_affordance_matrix.json"
    matrix_path = os.path.join(repo_root, matrix_rel.replace("/", os.sep))
    if not os.path.isfile(matrix_path):
        return {"status": "fail", "message": "{} missing".format(matrix_rel)}

    payload = _load_json(matrix_path)
    affordances = list((payload if isinstance(payload, dict) else {}).get("affordances") or [])
    series_rows = list((payload if isinstance(payload, dict) else {}).get("series_affordance_coverage") or [])

    covered = set()
    for row in affordances:
        if not isinstance(row, dict):
            continue
        for token in list(row.get("series_implemented") or []):
            series_id = str(token).strip()
            if series_id:
                covered.add(series_id)
        for token in list(row.get("series_planned") or []):
            series_id = str(token).strip()
            if series_id:
                covered.add(series_id)
    for row in series_rows:
        if not isinstance(row, dict):
            continue
        series_id = str(row.get("series_id", "")).strip()
        if series_id:
            covered.add(series_id)

    retro_dir = os.path.join(repo_root, "docs", "audit")
    discovered = set()
    retro_re = re.compile(r"^([A-Z]+)\d+_RETRO_AUDIT\.md$")
    if os.path.isdir(retro_dir):
        for name in os.listdir(retro_dir):
            match = retro_re.fullmatch(str(name).strip())
            if match:
                discovered.add(str(match.group(1)).strip())

    missing = sorted(series_id for series_id in discovered if series_id not in covered)
    if missing:
        return {
            "status": "fail",
            "message": "series missing RWAM mapping: {}".format(",".join(missing)),
        }
    return {"status": "pass", "message": "all discovered series declare RWAM mapping"}
