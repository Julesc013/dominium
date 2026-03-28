"""E241 missing compaction marker smell analyzer."""

from __future__ import annotations

import json
import os
from typing import List

from analyzers.base import make_finding


ANALYZER_ID = "E241_MISSING_COMPACTION_MARKER_SMELL"


class MissingCompactionMarkerSmell:
    analyzer_id = ANALYZER_ID


WATCH_PREFIXES = (
    "meta/provenance/compaction_engine.py",
    "schemas/control_proof_bundle.schema.json",
    "tools/meta/tool_verify_replay_from_anchor.py",
)

_ENGINE_REL = "meta/provenance/compaction_engine.py"
_PROOF_SCHEMA_REL = "schemas/control_proof_bundle.schema.json"
_REPLAY_TOOL_REL = "tools/meta/tool_verify_replay_from_anchor.py"


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _read_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files

    findings: List[object] = []

    engine_text = _read_text(repo_root, _ENGINE_REL)
    required_engine_tokens = (
        "def compact_provenance_window(",
        "build_compaction_marker(",
        "compaction_markers",
        "compaction_marker_hash_chain",
    )
    for token in required_engine_tokens:
        if token in engine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_compaction_marker_smell",
                severity="RISK",
                confidence=0.93,
                file_path=_ENGINE_REL,
                line=1,
                evidence=["missing required compaction marker token", token],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-COMPACTION-MARKER-REQUIRED"],
                related_paths=[_ENGINE_REL, _PROOF_SCHEMA_REL, _REPLAY_TOOL_REL],
            )
        )
        break

    schema_payload = _read_json(repo_root, _PROOF_SCHEMA_REL)
    required_fields = set(str(token).strip() for token in list(schema_payload.get("required") or []))
    for field in (
        "compaction_marker_hash_chain",
        "compaction_pre_anchor_hash",
        "compaction_post_anchor_hash",
    ):
        if field in required_fields:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_compaction_marker_smell",
                severity="RISK",
                confidence=0.95,
                file_path=_PROOF_SCHEMA_REL,
                line=1,
                evidence=["control proof schema missing compaction witness field", field],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-COMPACTION-MARKER-REQUIRED"],
                related_paths=[_ENGINE_REL, _PROOF_SCHEMA_REL],
            )
        )
        break

    tool_abs = os.path.join(repo_root, _REPLAY_TOOL_REL.replace("/", os.sep))
    if not os.path.isfile(tool_abs):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_compaction_marker_smell",
                severity="RISK",
                confidence=0.97,
                file_path=_REPLAY_TOOL_REL,
                line=1,
                evidence=["missing replay-from-anchor verifier"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-COMPACTION-MARKER-REQUIRED"],
                related_paths=[_REPLAY_TOOL_REL],
            )
        )

    return findings
