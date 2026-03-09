"""E363 large data in Sol pin pack smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E363_LARGE_DATA_IN_PIN_PACK_SMELL"
PACK_MANIFEST_REL = "packs/official/pack.sol.pin_minimal/pack.json"
PATCH_DOC_REL = "packs/official/pack.sol.pin_minimal/data/overlay/sol_pin_patches.json"
DOC_REL = "docs/packs/sol/PACK_SOL_PIN_MINIMAL.md"
VERIFY_TOOL_REL = "tools/geo/tool_verify_sol_pin_overlay.py"
MAX_PATCH_COUNT = 96
MAX_TOTAL_BYTES = 73728
REQUIRED_DOC_TOKENS = (
    "Its purpose is limited to:",
    "It is not a catalog pack, terrain pack, or Earth geography pack.",
    "DEM or terrain height data",
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
    for rel_path in (PACK_MANIFEST_REL, PATCH_DOC_REL, DOC_REL, VERIFY_TOOL_REL):
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="packs.large_data_in_pin_pack_smell",
                severity="RISK",
                confidence=0.98,
                file_path=rel_path,
                line=1,
                evidence=["required Sol pin governed artifact is missing"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=["INV-SOL-PACK-MINIMAL-SIZE"],
                related_paths=[PACK_MANIFEST_REL, PATCH_DOC_REL, DOC_REL, VERIFY_TOOL_REL],
            )
        )
    patch_payload = _load_json(repo_root, PATCH_DOC_REL)
    if not isinstance(patch_payload, dict):
        return findings + [
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="packs.large_data_in_pin_pack_smell",
                severity="RISK",
                confidence=0.98,
                file_path=PATCH_DOC_REL,
                line=1,
                evidence=["Sol pin patch document is missing or invalid JSON"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=["INV-SOL-PACK-MINIMAL-SIZE"],
                related_paths=[PATCH_DOC_REL],
            )
        ]
    patch_rows = list(patch_payload.get("property_patches") or [])
    if len(patch_rows) > MAX_PATCH_COUNT:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="packs.large_data_in_pin_pack_smell",
                severity="RISK",
                confidence=0.96,
                file_path=PATCH_DOC_REL,
                line=1,
                evidence=["patch count {} exceeds max {}".format(len(patch_rows), MAX_PATCH_COUNT)],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-SOL-PACK-MINIMAL-SIZE"],
                related_paths=[PATCH_DOC_REL],
            )
        )
    total_bytes = 0
    for rel_path in (PACK_MANIFEST_REL, PATCH_DOC_REL, DOC_REL, VERIFY_TOOL_REL):
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            total_bytes += int(os.path.getsize(abs_path))
    if total_bytes > MAX_TOTAL_BYTES:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="packs.large_data_in_pin_pack_smell",
                severity="RISK",
                confidence=0.96,
                file_path=PATCH_DOC_REL,
                line=1,
                evidence=["governed Sol pin artifact bytes {} exceed max {}".format(total_bytes, MAX_TOTAL_BYTES)],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-SOL-PACK-MINIMAL-SIZE"],
                related_paths=[PACK_MANIFEST_REL, PATCH_DOC_REL, DOC_REL, VERIFY_TOOL_REL],
            )
        )
    doc_text = _read_text(repo_root, DOC_REL)
    missing_doc = [token for token in REQUIRED_DOC_TOKENS if token not in doc_text]
    if missing_doc:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="packs.large_data_in_pin_pack_smell",
                severity="RISK",
                confidence=0.93,
                file_path=DOC_REL,
                line=1,
                evidence=["missing Sol minimalism marker(s): {}".format(", ".join(missing_doc[:3]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-SOL-PACK-MINIMAL-SIZE"],
                related_paths=[DOC_REL, PATCH_DOC_REL],
            )
        )
    return findings
