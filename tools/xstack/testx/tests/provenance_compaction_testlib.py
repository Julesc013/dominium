"""Shared deterministic fixtures for PROV-0 compaction tests."""

from __future__ import annotations

import copy
import json
import os
from typing import Dict, List


def read_provenance_classification_rows(repo_root: str) -> List[dict]:
    rel_path = "data/registries/provenance_classification_registry.json"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    payload = json.load(open(abs_path, "r", encoding="utf-8"))
    rows = list((dict(payload.get("record") or {})).get("provenance_classifications") or [])
    return [dict(row) for row in rows if isinstance(row, dict)]


def build_compaction_fixture_state(shard_suffix: str = "alpha") -> Dict[str, object]:
    token = str(shard_suffix or "").strip() or "alpha"
    info_rows = [
        {
            "artifact_id": "artifact.info.explain.{}.in_window".format(token),
            "artifact_type_id": "artifact.explain",
            "tick": 6,
            "extensions": {},
        },
        {
            "artifact_id": "artifact.info.explain.{}.outside_window".format(token),
            "artifact_type_id": "artifact.explain",
            "tick": 12,
            "extensions": {},
        },
        {
            "artifact_id": "artifact.info.energy.{}.canonical".format(token),
            "artifact_type_id": "artifact.energy_ledger_entry",
            "tick": 6,
            "extensions": {},
        },
    ]
    return {
        "energy_ledger_entries": [
            {
                "entry_id": "entry.energy.{}.001".format(token),
                "tick": 6,
                "source_id": "assembly.{}".format(token),
                "transformation_id": "transform.electrical_to_thermal",
                "input_values": {
                    "quantity.energy_electrical": 400,
                },
                "output_values": {
                    "quantity.energy_thermal": 400,
                },
                "energy_total_delta": 0,
                "extensions": {},
            },
            {
                "entry_id": "entry.energy.{}.002".format(token),
                "tick": 10,
                "source_id": "assembly.{}".format(token),
                "transformation_id": "transform.kinetic_to_thermal",
                "input_values": {
                    "quantity.energy_kinetic": 120,
                },
                "output_values": {
                    "quantity.energy_thermal": 120,
                },
                "energy_total_delta": 0,
                "extensions": {},
            },
        ],
        "boundary_flux_events": [
            {
                "flux_id": "flux.{}.001".format(token),
                "tick": 7,
                "quantity_id": "quantity.energy_thermal",
                "value": 80,
                "direction": "in",
                "reason_code": "test.boundary",
                "extensions": {},
            }
        ],
        "time_adjust_events": [
            {
                "adjust_id": "time.adjust.{}.001".format(token),
                "tick": 6,
                "target_id": "clock.{}".format(token),
                "previous_domain_time": 1000,
                "new_domain_time": 1004,
                "adjustment_delta": 4,
                "originating_receipt_id": "receipt.{}".format(token),
                "extensions": {},
            }
        ],
        "fault_events": [
            {
                "event_id": "fault.{}.001".format(token),
                "tick": 7,
                "target_id": "assembly.{}".format(token),
                "reason_code": "fault.synthetic",
                "extensions": {},
            }
        ],
        "exception_events": [],
        "leak_events": [],
        "burst_events": [],
        "relief_events": [],
        "branch_events": [],
        "compaction_markers": [],
        "info_artifact_rows": copy.deepcopy(info_rows),
        "knowledge_artifacts": copy.deepcopy(info_rows),
        "explain_artifact_rows": [
            {
                "explain_id": "explain.{}.001".format(token),
                "tick": 6,
                "cause_chain": ["event.synthetic"],
                "extensions": {},
            },
            {
                "explain_id": "explain.{}.002".format(token),
                "tick": 11,
                "cause_chain": ["event.synthetic"],
                "extensions": {},
            },
        ],
        "inspection_snapshot_rows": [
            {
                "snapshot_id": "snapshot.{}.001".format(token),
                "tick": 7,
                "target_id": "assembly.{}".format(token),
                "extensions": {},
            },
            {
                "snapshot_id": "snapshot.{}.002".format(token),
                "tick": 12,
                "target_id": "assembly.{}".format(token),
                "extensions": {},
            },
        ],
        "model_evaluation_results": [
            {
                "model_id": "model.synthetic.{}".format(token),
                "tick": 6,
                "deterministic_fingerprint": "model.eval.{}".format(token),
                "extensions": {},
            }
        ],
        "derived_summary_rows": [
            {
                "summary_id": "summary.{}".format(token),
                "tick": 6,
                "extensions": {},
            }
        ],
        "derived_statistics_rows": [
            {
                "stats_id": "stats.{}".format(token),
                "tick": 7,
                "extensions": {},
            }
        ],
        "provenance_compaction_summaries": [],
        "time_branches": [],
        "control_proof_bundles": [],
    }
