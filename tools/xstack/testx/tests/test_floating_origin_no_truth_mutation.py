"""FAST test: GEO-2 floating-origin rebasing is render-only and does not mutate truth refs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_floating_origin_no_truth_mutation"
TEST_TAGS = ["fast", "geo", "render", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.geo import apply_floating_origin, frame_graph_hash, position_ref_hash
    from tools.xstack.testx.tests.geo2_testlib import baseline_frame_nodes, baseline_frame_transforms, poi_position, surface_position

    nodes = baseline_frame_nodes()
    transforms = baseline_frame_transforms()
    camera = surface_position()
    target = poi_position()
    camera_before = copy.deepcopy(camera)
    target_before = copy.deepcopy(target)
    camera_hash = position_ref_hash(camera)
    target_hash = position_ref_hash(target)
    version = frame_graph_hash(frame_nodes=nodes, frame_transform_rows=transforms)

    result = apply_floating_origin(
        target,
        camera,
        frame_nodes=nodes,
        frame_transform_rows=transforms,
        graph_version=version,
        rebase_quantum_mm=1000,
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "floating origin conversion failed"}
    if dict(camera) != camera_before or dict(target) != target_before:
        return {"status": "fail", "message": "floating origin mutated truth refs"}
    if position_ref_hash(camera) != camera_hash or position_ref_hash(target) != target_hash:
        return {"status": "fail", "message": "floating origin changed truth position hashes"}
    if not bool(result.get("render_only", False)):
        return {"status": "fail", "message": "floating origin result is not marked render-only"}
    return {"status": "pass", "message": "GEO-2 floating origin does not mutate truth"}
