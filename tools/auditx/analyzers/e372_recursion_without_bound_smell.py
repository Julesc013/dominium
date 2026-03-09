"""E372 recursion without bound smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E372_RECURSION_WITHOUT_BOUND_SMELL"
HYDROLOGY_ENGINE_REL = "src/worldgen/earth/hydrology_engine.py"
HYDROLOGY_DOC_REL = "docs/worldgen/EARTH_HYDROLOGY_MODEL.md"
HYDROLOGY_PROBE_REL = "tools/worldgen/earth1_probe.py"
REQUIRED_ENGINE_TOKENS = (
    "analysis_radius",
    "max_window_tiles",
    "sorted_for_accumulation",
    "for cell_hash, snapshot in sorted_for_accumulation:",
    "accumulation_by_hash",
)
REQUIRED_DOC_TOKENS = (
    "no recursion is allowed",
    "the window must remain bounded and deterministic",
    "small edits must not require whole-planet recompute",
)
FORBIDDEN_TOKENS = ("sys.setrecursionlimit", "recursionlimit", "def _accumulate(", "return _accumulate(", "def recurse(")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    engine_text = _read_text(repo_root, HYDROLOGY_ENGINE_REL)
    doc_text = _read_text(repo_root, HYDROLOGY_DOC_REL)
    probe_text = _read_text(repo_root, HYDROLOGY_PROBE_REL)

    for rel_path, text, required_tokens in (
        (HYDROLOGY_ENGINE_REL, engine_text, REQUIRED_ENGINE_TOKENS),
        (HYDROLOGY_DOC_REL, doc_text, REQUIRED_DOC_TOKENS),
        (HYDROLOGY_PROBE_REL, probe_text, ("generate_hydrology_window_fixture", "verify_local_edit_hydrology_update")),
    ):
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.recursion_without_bound_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required bounded-hydrology artifact is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-HYDROLOGY-DETERMINISTIC"],
                    related_paths=[HYDROLOGY_ENGINE_REL, HYDROLOGY_DOC_REL, HYDROLOGY_PROBE_REL],
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.recursion_without_bound_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing bounded-hydrology marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-HYDROLOGY-DETERMINISTIC"],
                    related_paths=[HYDROLOGY_ENGINE_REL, HYDROLOGY_DOC_REL, HYDROLOGY_PROBE_REL],
                )
            )

    for rel_path, text in ((HYDROLOGY_ENGINE_REL, engine_text), (HYDROLOGY_PROBE_REL, probe_text)):
        for line_no, line in enumerate(str(text or "").splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            token = next((item for item in FORBIDDEN_TOKENS if item in snippet), "")
            if not token:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.recursion_without_bound_smell",
                    severity="RISK",
                    confidence=0.96,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden recursive/unbounded token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-HYDROLOGY-DETERMINISTIC"],
                    related_paths=[HYDROLOGY_ENGINE_REL, HYDROLOGY_PROBE_REL],
                )
            )
            break
    return findings
