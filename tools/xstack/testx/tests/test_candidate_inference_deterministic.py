"""FAST test: PROC-7 candidate inference is deterministic for equivalent evidence."""

from __future__ import annotations

import sys


TEST_ID = "test_candidate_inference_deterministic"
TEST_TAGS = ["fast", "proc", "proc7", "inference", "determinism"]


def _experiment_rows(reversed_order: bool) -> list[dict]:
    rows = [
        {
            "result_id": "result.experiment.proc7.001",
            "experiment_id": "experiment.proc7.default",
            "run_id": "run.proc7.001",
            "measured_values": {"measurement.proc7.a": 40},
            "confidence_bounds": {},
        },
        {
            "result_id": "result.experiment.proc7.002",
            "experiment_id": "experiment.proc7.default",
            "run_id": "run.proc7.002",
            "measured_values": {"measurement.proc7.b": 19},
            "confidence_bounds": {},
        },
    ]
    return list(reversed(rows)) if reversed_order else rows


def _reverse_rows(reversed_order: bool) -> list[dict]:
    rows = [
        {
            "record_id": "record.reverse_engineering.proc7.001",
            "subject_id": "subject.proc7.researcher",
            "target_item_id": "item.proc7.alpha",
            "method": "scan",
            "destroyed": False,
            "produced_artifact_ids": ["artifact.observation.proc7.scan"],
            "tick": 4,
        },
        {
            "record_id": "record.reverse_engineering.proc7.002",
            "subject_id": "subject.proc7.researcher",
            "target_item_id": "item.proc7.beta",
            "method": "disassemble",
            "destroyed": True,
            "produced_artifact_ids": ["artifact.observation.proc7.disassemble"],
            "tick": 5,
        },
    ]
    return list(reversed(rows)) if reversed_order else rows


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.process.research import infer_candidate_artifacts

    first = infer_candidate_artifacts(
        current_tick=10,
        experiment_result_rows=_experiment_rows(False),
        reverse_engineering_record_rows=_reverse_rows(False),
        process_definition_ref_hint="proc.test.proc7@1.0.0",
        model_id_hint="model.proc7.stub",
        existing_candidate_rows=[],
        existing_candidate_model_binding_rows=[],
    )
    second = infer_candidate_artifacts(
        current_tick=10,
        experiment_result_rows=_experiment_rows(True),
        reverse_engineering_record_rows=_reverse_rows(True),
        process_definition_ref_hint="proc.test.proc7@1.0.0",
        model_id_hint="model.proc7.stub",
        existing_candidate_rows=[],
        existing_candidate_model_binding_rows=[],
    )

    if str(first.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first inference run did not complete"}
    if str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second inference run did not complete"}
    if first != second:
        return {"status": "fail", "message": "candidate inference output drifted for equivalent evidence"}
    if not list(first.get("produced_candidate_ids") or []):
        return {"status": "fail", "message": "candidate inference produced no candidate ids"}
    return {"status": "pass", "message": "PROC-7 candidate inference is deterministic"}

