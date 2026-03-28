"""E377 nondeterministic starfield smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E377_NONDETERMINISTIC_STARFIELD_SMELL"
ASTRONOMY_REL = "worldgen/earth/sky/astronomy_proxy_engine.py"
STARFIELD_REL = "worldgen/earth/sky/starfield_generator.py"
SKY_VIEW_REL = "worldgen/earth/sky/sky_view_engine.py"
PROBE_REL = "tools/worldgen/earth4_probe.py"
REPLAY_REL = "tools/worldgen/tool_replay_sky_view.py"
DOC_REL = "docs/worldgen/EARTH_SKY_STARFIELD_MODEL.md"
REQUIRED_TOKENS = {
    ASTRONOMY_REL: (
        "current_tick",
        "earth_orbit_phase_from_params(",
        "rotation_phase_from_params(",
        "lunar_phase_from_params(",
    ),
    STARFIELD_REL: (
        "build_starfield_snapshot(",
        '"stream_name": "rng.view.sky.starfield"',
        "sky_tick_bucket(",
        "galaxy_priors_rows",
    ),
    SKY_VIEW_REL: (
        "build_sky_view_surface(",
        "cache_key",
        '"cache_policy_id": "cache.sky.observer_tick_bucket"',
    ),
    PROBE_REL: (
        "verify_sky_view_replay",
        "sky_hash",
    ),
    REPLAY_REL: (
        "Verify EARTH-4 sky replay determinism.",
    ),
    DOC_REL: (
        "Same inputs must produce the same starfield.",
        "named stream",
        "wall-clock time is forbidden",
    ),
}
FORBIDDEN_TOKENS = ("random.", "uuid", "secrets.", "time.time(", "datetime.now(", "os.urandom(", "random.seed(", "time.sleep(")


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
    for rel_path, required_tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.nondeterministic_starfield_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EARTH-4 sky/starfield artifact is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-NO-WALLCLOCK-SKY", "INV-NO-CATALOG-DEPENDENCY"],
                    related_paths=list(REQUIRED_TOKENS.keys()),
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.nondeterministic_starfield_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing EARTH-4 starfield determinism marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-WALLCLOCK-SKY", "INV-NO-CATALOG-DEPENDENCY"],
                    related_paths=list(REQUIRED_TOKENS.keys()),
                )
            )

    for rel_path in (ASTRONOMY_REL, STARFIELD_REL, SKY_VIEW_REL, PROBE_REL, REPLAY_REL):
        text = _read_text(repo_root, rel_path)
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
                    category="worldgen.nondeterministic_starfield_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden sky/starfield nondeterminism token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-WALLCLOCK-SKY", "INV-NO-CATALOG-DEPENDENCY"],
                    related_paths=[ASTRONOMY_REL, STARFIELD_REL, SKY_VIEW_REL, PROBE_REL, REPLAY_REL, DOC_REL],
                )
            )
            break
    return findings
