"""FAST test: material batch creation is deterministic for equivalent inputs."""

from __future__ import annotations

import sys


TEST_ID = "testx.materials.material_batch_creation_deterministic"
TEST_TAGS = ["fast", "materials", "batch"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.materials.composition_engine import create_material_batch

    left = create_material_batch(
        material_id="material.iron",
        quantity_mass_raw=1024,
        origin_process_id="process.test.material_batch",
        origin_tick=17,
        parent_batch_ids=["batch.parent.b", "batch.parent.a"],
        quality_distribution={"quality_distribution_model_id": "quality.uniform_stub"},
    )
    right = create_material_batch(
        material_id="material.iron",
        quantity_mass_raw=1024,
        origin_process_id="process.test.material_batch",
        origin_tick=17,
        parent_batch_ids=["batch.parent.a", "batch.parent.b"],
        quality_distribution={"quality_distribution_model_id": "quality.uniform_stub"},
    )
    if left != right:
        return {"status": "fail", "message": "deterministic material batch creation diverged"}
    return {"status": "pass", "message": "material batch creation deterministic"}
