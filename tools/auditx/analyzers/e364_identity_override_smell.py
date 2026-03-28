"""E364 identity override smell analyzer for the Sol pin pack."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E364_IDENTITY_OVERRIDE_SMELL"
PATCH_DOC_REL = "packs/official/pack.sol.pin_minimal/data/overlay/sol_pin_patches.json"
DOC_REL = "docs/packs/sol/PACK_SOL_PIN_MINIMAL.md"
OVERLAY_ENGINE_REL = "geo/overlay/overlay_merge_engine.py"
IMMUTABLE_PATHS = (
    "object_id",
    "identity_hash",
    "generator_version_id",
    "topology_profile_id",
    "metric_profile_id",
    "partition_profile_id",
    "projection_profile_id",
)
REQUIRED_DOC_TOKENS = (
    "replacing object identity",
    "patching immutable identity paths such as `object_id`",
    "deleting procedural objects",
)
REQUIRED_ENGINE_TOKENS = (
    "_IMMUTABLE_PROPERTY_PATHS",
    "immutable property path may not be patched",
)


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _load_json(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    patch_payload = _load_json(repo_root, PATCH_DOC_REL)
    doc_text = _read_text(repo_root, DOC_REL)
    engine_text = _read_text(repo_root, OVERLAY_ENGINE_REL)

    if not isinstance(patch_payload, dict):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="overlay.identity_override_smell",
                severity="RISK",
                confidence=0.98,
                file_path=PATCH_DOC_REL,
                line=1,
                evidence=["Sol pin patch document is missing or invalid JSON"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=["INV-NO-IDENTITY-OVERRIDE"],
                related_paths=[PATCH_DOC_REL],
            )
        )
        return findings

    for rel_path, text, required in (
        (DOC_REL, doc_text, REQUIRED_DOC_TOKENS),
        (OVERLAY_ENGINE_REL, engine_text, REQUIRED_ENGINE_TOKENS),
    ):
        missing = [token for token in required if token not in text]
        if not missing:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="overlay.identity_override_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["missing identity-override guard marker(s): {}".format(", ".join(missing[:3]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-IDENTITY-OVERRIDE"],
                related_paths=[PATCH_DOC_REL, DOC_REL, OVERLAY_ENGINE_REL],
            )
        )

    for row in list(patch_payload.get("property_patches") or []):
        if not isinstance(row, dict):
            continue
        property_path = str(row.get("property_path", "")).strip()
        operation = str(row.get("operation", "")).strip().lower()
        if property_path in IMMUTABLE_PATHS or operation == "remove":
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="overlay.identity_override_smell",
                    severity="RISK",
                    confidence=0.99,
                    file_path=PATCH_DOC_REL,
                    line=1,
                    evidence=[
                        "forbidden identity override marker detected",
                        "property_path={}".format(property_path or "<missing>"),
                        "operation={}".format(operation or "<missing>"),
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-IDENTITY-OVERRIDE"],
                    related_paths=[PATCH_DOC_REL, OVERLAY_ENGINE_REL],
                )
            )
            break
    return findings
