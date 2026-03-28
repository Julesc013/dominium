"""E371 random river smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E371_RANDOM_RIVER_SMELL"
HYDROLOGY_ENGINE_REL = "worldgen/earth/hydrology_engine.py"
HYDROLOGY_PROBE_REL = "tools/worldgen/earth1_probe.py"
HYDROLOGY_REPLAY_REL = "tools/worldgen/tool_replay_hydrology_window.py"
HYDROLOGY_DOC_REL = "docs/worldgen/EARTH_HYDROLOGY_MODEL.md"
REQUIRED_ENGINE_TOKENS = (
    "compute_hydrology_window(",
    "lower_neighbors.sort(",
    "sorted_for_accumulation",
    "drainage_accumulation_proxy",
    "river_flag",
)
REQUIRED_PROBE_TOKENS = (
    "verify_hydrology_window_replay",
    "verify_river_threshold_fixture",
    "verify_local_edit_hydrology_update",
)
REQUIRED_DOC_TOKENS = (
    "no random tie-breaking is allowed",
    "GEO neighbor iteration order must remain canonical",
    "Hydrology recompute must execute through the existing lawful process path",
)
FORBIDDEN_TOKENS = ("random.", "uuid", "secrets.", "time.time(", "datetime.now(", "os.urandom(", "random.seed(")


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
    probe_text = _read_text(repo_root, HYDROLOGY_PROBE_REL)
    replay_text = _read_text(repo_root, HYDROLOGY_REPLAY_REL)
    doc_text = _read_text(repo_root, HYDROLOGY_DOC_REL)

    for rel_path, text, required_tokens in (
        (HYDROLOGY_ENGINE_REL, engine_text, REQUIRED_ENGINE_TOKENS),
        (HYDROLOGY_PROBE_REL, probe_text, REQUIRED_PROBE_TOKENS),
        (HYDROLOGY_REPLAY_REL, replay_text, ("verify_hydrology_window_replay",)),
        (HYDROLOGY_DOC_REL, doc_text, REQUIRED_DOC_TOKENS),
    ):
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.random_river_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EARTH-1 hydrology artifact is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-HYDROLOGY-DETERMINISTIC", "INV-NO-RANDOM-FLOW"],
                    related_paths=[HYDROLOGY_ENGINE_REL, HYDROLOGY_PROBE_REL, HYDROLOGY_REPLAY_REL, HYDROLOGY_DOC_REL],
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.random_river_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing deterministic hydrology marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-HYDROLOGY-DETERMINISTIC", "INV-NO-RANDOM-FLOW"],
                    related_paths=[HYDROLOGY_ENGINE_REL, HYDROLOGY_PROBE_REL, HYDROLOGY_REPLAY_REL, HYDROLOGY_DOC_REL],
                )
            )

    for rel_path, text in ((HYDROLOGY_ENGINE_REL, engine_text), (HYDROLOGY_PROBE_REL, probe_text), (HYDROLOGY_REPLAY_REL, replay_text)):
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
                    category="worldgen.random_river_smell",
                    severity="RISK",
                    confidence=0.96,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden random-flow token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-RANDOM-FLOW"],
                    related_paths=[HYDROLOGY_ENGINE_REL, HYDROLOGY_PROBE_REL, HYDROLOGY_REPLAY_REL],
                )
            )
            break
    return findings
