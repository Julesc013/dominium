"""A4 Derived Artifact Contract Analyzer."""

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "A4_DERIVED_ARTIFACT_CONTRACT"
WATCH_PREFIXES = ("data/registries/derived_artifacts.json", "docs/audit/")
FORBIDDEN = {
    "created_utc",
    "generated_utc",
    "host_name",
    "last_reviewed",
    "machine_name",
    "run_id",
    "scan_id",
    "timestamp",
    "timestamps",
}


def _load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def _walk_forbidden(node, path_prefix, out):
    if isinstance(node, dict):
        for key in sorted(node.keys()):
            value = node[key]
            next_path = "{}.{}".format(path_prefix, key) if path_prefix else key
            if key in FORBIDDEN:
                out.append(next_path)
            _walk_forbidden(value, next_path, out)
        return
    if isinstance(node, list):
        for idx, value in enumerate(node):
            _walk_forbidden(value, "{}[{}]".format(path_prefix, idx), out)


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files

    registry_path = os.path.join(repo_root, "data", "registries", "derived_artifacts.json")
    payload = _load_json(registry_path)
    if not isinstance(payload, dict):
        return []
    artifacts = payload.get("record", {}).get("artifacts", [])
    if not isinstance(artifacts, list):
        return []

    findings = []
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        if str(artifact.get("artifact_class", "")).strip() != "CANONICAL":
            continue
        rel = str(artifact.get("path", "")).strip().replace("\\", "/")
        if not rel or not rel.lower().endswith(".json"):
            continue
        abs_path = os.path.join(repo_root, rel.replace("/", os.sep))
        doc = _load_json(abs_path)
        if not isinstance(doc, dict):
            continue
        forbidden_paths = []
        _walk_forbidden(doc, "", forbidden_paths)
        if not forbidden_paths:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="semantic.derived_artifact_contract",
                severity="VIOLATION",
                confidence=0.98,
                file_path=rel,
                evidence=[
                    "Canonical artifact contains forbidden run-meta fields.",
                    "Sample keys: {}".format(", ".join(sorted(forbidden_paths[:5]))),
                ],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-DERIVED-ARTIFACT-CONTRACT"],
                related_paths=[rel],
            )
        )
    return findings

