"""Deterministic GAL-1 galaxy object stub probes for replay and TestX reuse."""

from __future__ import annotations

import os
import sys
from collections import Counter
from functools import lru_cache
from typing import Dict, Iterable, List, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.worldgen.galaxy import (  # noqa: E402
    MAX_GALAXY_OBJECT_STUBS_PER_CELL,
    build_galaxy_object_hazard_hooks,
    build_galaxy_object_layer_source_payloads,
    galaxy_object_stub_hash_chain,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402
from tools.xstack.testx.tests.geo8_testlib import run_worldgen_process, seed_worldgen_state  # noqa: E402


GAL1_SAMPLE_CELL_INDICES = (
    [0, 0, 0],
    [400, 0, 0],
    [800, 0, 0],
    [4200, 0, 0],
)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _cell_key_token(cell_key: Mapping[str, object]) -> str:
    key_row = _as_map(cell_key)
    index_tuple = [int(item) for item in list(key_row.get("index_tuple") or [])]
    while len(index_tuple) < 3:
        index_tuple.append(0)
    return "cell.{}.{}.{}".format(index_tuple[0], index_tuple[1], index_tuple[2])


def _rows_by_object_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for raw in list(rows or []):
        row = _as_map(raw)
        object_id = str(row.get("object_id", "")).strip()
        if object_id:
            out[object_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def run_galaxy_object_replay(
    repo_root: str,
    *,
    cell_indices: Iterable[Sequence[int]] = GAL1_SAMPLE_CELL_INDICES,
) -> dict:
    del repo_root
    state = seed_worldgen_state()
    result_rows = []
    for index_tuple in list(cell_indices or []):
        result = run_worldgen_process(
            state=state,
            index_tuple=[int(item) for item in list(index_tuple or [])],
            refinement_level=1,
            reason="query",
        )
        if str(result.get("result", "")).strip() != "complete":
            raise RuntimeError("GAL-1 worldgen process failed for {}".format(list(index_tuple or [])))
        result_rows.append(dict(result))
    artifact_rows = [dict(row) for row in list(state.get("worldgen_galaxy_object_stub_artifacts") or []) if isinstance(row, Mapping)]
    rows_by_object_id = _rows_by_object_id(artifact_rows)
    layer_payloads = build_galaxy_object_layer_source_payloads(artifact_rows)
    hazard_hooks = build_galaxy_object_hazard_hooks(artifact_rows)
    counts_by_cell = Counter(
        _cell_key_token(_as_map(_as_map(row.get("extensions")).get("geo_cell_key")))
        for row in artifact_rows
        if _as_map(_as_map(row.get("extensions")).get("geo_cell_key"))
    )
    kinds_by_object_id = dict(
        (object_id, str(_as_map(row).get("kind", "")).strip())
        for object_id, row in sorted(rows_by_object_id.items())
    )
    report = {
        "result": "complete",
        "requested_cell_count": int(len(list(cell_indices or []))),
        "worldgen_result_count": int(len(result_rows)),
        "object_count": int(len(artifact_rows)),
        "artifact_hash_chain": galaxy_object_stub_hash_chain(artifact_rows),
        "layer_payload_hash": canonical_sha256(layer_payloads),
        "hazard_hook_hash": canonical_sha256(hazard_hooks),
        "object_ids": sorted(rows_by_object_id.keys()),
        "kinds_by_object_id": kinds_by_object_id,
        "counts_by_cell": dict((key, int(counts_by_cell[key])) for key in sorted(counts_by_cell.keys())),
        "max_objects_per_cell": int(max([0] + [int(value) for value in counts_by_cell.values()])),
        "max_allowed_objects_per_cell": int(MAX_GALAXY_OBJECT_STUBS_PER_CELL),
        "central_black_hole_count": int(
            sum(1 for row in artifact_rows if str(_as_map(row).get("kind", "")).strip() == "kind.black_hole_stub")
        ),
        "layer_marker_rows": [dict(row) for row in _as_list(_as_map(layer_payloads.get("layer.galaxy_objects")).get("rows")) if isinstance(row, Mapping)],
        "hazard_hooks": [dict(row) for row in hazard_hooks],
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def verify_galaxy_object_replay(repo_root: str) -> dict:
    first = run_galaxy_object_replay(repo_root)
    second = run_galaxy_object_replay(repo_root)
    stable = (
        first.get("result") == "complete"
        and second.get("result") == "complete"
        and str(first.get("artifact_hash_chain", "")).strip() == str(second.get("artifact_hash_chain", "")).strip()
        and str(first.get("layer_payload_hash", "")).strip() == str(second.get("layer_payload_hash", "")).strip()
        and str(first.get("hazard_hook_hash", "")).strip() == str(second.get("hazard_hook_hash", "")).strip()
    )
    payload = {
        "result": "complete" if stable else "drift",
        "stable_across_repeated_runs": bool(stable),
        "first_run": dict(first),
        "second_run": dict(second),
        "combined_hash": canonical_sha256(
            {
                "artifact_hash_chain": str(first.get("artifact_hash_chain", "")).strip(),
                "layer_payload_hash": str(first.get("layer_payload_hash", "")).strip(),
                "hazard_hook_hash": str(first.get("hazard_hook_hash", "")).strip(),
            }
        ),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def central_black_hole_report(repo_root: str) -> dict:
    report = run_galaxy_object_replay(repo_root)
    central_rows = [
        dict(row)
        for row in list(_rows_by_object_id(_as_list(report.get("hazard_hooks"))).values())
        if str(_as_map(row).get("kind", "")).strip() == "kind.black_hole_stub"
    ]
    payload = {
        "result": "complete" if int(report.get("central_black_hole_count", 0)) == 1 else "mismatch",
        "central_black_hole_count": int(report.get("central_black_hole_count", 0) or 0),
        "object_ids": list(report.get("object_ids") or []),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def bounded_generation_report(repo_root: str) -> dict:
    report = run_galaxy_object_replay(repo_root)
    max_objects_per_cell = int(report.get("max_objects_per_cell", 0) or 0)
    max_allowed = int(report.get("max_allowed_objects_per_cell", MAX_GALAXY_OBJECT_STUBS_PER_CELL) or MAX_GALAXY_OBJECT_STUBS_PER_CELL)
    payload = {
        "result": "complete" if max_objects_per_cell <= max_allowed else "overflow",
        "max_objects_per_cell": max_objects_per_cell,
        "max_allowed_objects_per_cell": max_allowed,
        "counts_by_cell": dict(report.get("counts_by_cell") or {}),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


@lru_cache(maxsize=4)
def galaxy_object_hash(repo_root: str) -> str:
    return str(verify_galaxy_object_replay(repo_root).get("combined_hash", "")).strip()


__all__ = [
    "GAL1_SAMPLE_CELL_INDICES",
    "bounded_generation_report",
    "central_black_hole_report",
    "galaxy_object_hash",
    "run_galaxy_object_replay",
    "verify_galaxy_object_replay",
]
