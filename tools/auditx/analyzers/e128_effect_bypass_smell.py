"""E128 effect bypass smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E128_EFFECT_BYPASS_SMELL"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


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

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    control_rel = "src/control/control_plane_engine.py"
    runtime_text = _read_text(repo_root, runtime_rel)
    control_text = _read_text(repo_root, control_rel)
    if not runtime_text or not control_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.effect_bypass_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=runtime_rel if not runtime_text else control_rel,
                line=1,
                evidence=["missing required runtime/control file for effect enforcement"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-EFFECT-USES-ENGINE"],
                related_paths=[runtime_rel, control_rel],
            )
        )
        return findings

    for token in (
        'elif process_id == "process.effect_apply":',
        'elif process_id == "process.effect_remove":',
    ):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.effect_bypass_smell",
                severity="VIOLATION",
                confidence=0.91,
                file_path=runtime_rel,
                line=1,
                evidence=["missing effect process handler token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-EFFECT-USES-ENGINE"],
                related_paths=[runtime_rel],
            )
        )

    if "get_effective_modifier_map(" not in control_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.effect_bypass_smell",
                severity="VIOLATION",
                confidence=0.9,
                file_path=control_rel,
                line=1,
                evidence=["control plane missing effect modifier query usage"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-EFFECT-USES-ENGINE"],
                related_paths=[control_rel],
            )
        )

    runtime_roots = (
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
        "docs/",
    )
    for root in runtime_roots:
        if not os.path.isdir(root):
            continue
        for walk_root, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path.startswith(skip_prefixes):
                    continue
                if rel_path == runtime_rel:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if "state[\"effect_rows\"]" not in snippet and "state['effect_rows']" not in snippet:
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.effect_bypass_smell",
                            severity="RISK",
                            confidence=0.86,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["direct effect_rows mutation outside process runtime", snippet[:140]],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="ADD_RULE",
                            related_invariants=["INV-EFFECT-USES-ENGINE"],
                            related_paths=[rel_path, runtime_rel],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

