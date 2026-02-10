"""A7 Legacy contamination analyzer."""

import os

from analyzers.base import make_finding


ANALYZER_ID = "A7_LEGACY_CONTAMINATION"
SOURCE_EXTS = (".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".py", ".json")


def _read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _label(node_id):
    return node_id.split(":", 1)[1] if ":" in node_id else node_id


def run(graph, repo_root, changed_files=None):
    del changed_files
    findings = []
    canonical_roots = ("client/", "launcher/", "setup/", "engine/", "game/", "libs/", "tools/", "app/")

    for edge in graph.edges:
        if edge.edge_type not in ("include", "import"):
            continue
        src = _label(edge.src)
        dst = _label(edge.dst)
        if not src.startswith(canonical_roots):
            continue
        if not dst.startswith("legacy/"):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="legacy_contamination",
                severity="VIOLATION",
                confidence=0.90,
                file_path=src,
                evidence=[
                    "Canonical code path imports/includes a legacy path.",
                    "Edge: {} -> {}".format(src, dst),
                ],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-LEGACY-CODE-QUARANTINED"],
                related_paths=[src, dst],
            )
        )
        if len(findings) >= 80:
            break

    file_nodes = sorted(
        [node for node in graph.nodes.values() if node.node_type == "file"],
        key=lambda item: item.label,
    )
    for node in file_nodes:
        rel = node.label
        if not rel.startswith(canonical_roots):
            continue
        if not rel.lower().endswith(SOURCE_EXTS):
            continue
        text = _read_text(os.path.join(repo_root, rel.replace("/", os.sep)))
        if "legacy/" not in text and "legacy\\" not in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="legacy_contamination",
                severity="RISK",
                confidence=0.70,
                file_path=rel,
                evidence=[
                    "Canonical file contains direct legacy path token.",
                    "Potential legacy coupling not captured by include/import graph.",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_TEST",
                related_invariants=["INV-LEGACY-CODE-QUARANTINED"],
                related_paths=[rel],
            )
        )
        if len(findings) >= 160:
            break

    return sorted(findings, key=lambda item: (item.location.file, item.severity, item.confidence))

