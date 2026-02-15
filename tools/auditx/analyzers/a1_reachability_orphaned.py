"""A1 Reachability / orphaned code analyzer."""

from analyzers.base import make_finding


ANALYZER_ID = "A1_REACHABILITY_ORPHANED"
SOURCE_EXTS = (".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".py")
IGNORE_PREFIXES = (
    "tests/",
    "docs/",
    "schema/",
    "data/",
    "legacy/",
    "build/",
    "out/",
    "dist/",
)


def _is_candidate(path):
    lower = path.lower()
    if not lower.endswith(SOURCE_EXTS):
        return False
    for prefix in IGNORE_PREFIXES:
        if lower.startswith(prefix):
            return False
    return True


def run(graph, repo_root, changed_files=None):
    del repo_root
    del changed_files

    incoming = {}
    for edge in graph.edges:
        incoming.setdefault(edge.dst, []).append(edge)

    findings = []
    file_nodes = [node for node in graph.nodes.values() if node.node_type == "file"]
    for node in sorted(file_nodes, key=lambda item: item.label):
        path = node.label
        if not _is_candidate(path):
            continue
        refs = [
            edge for edge in incoming.get(node.node_id, [])
            if not edge.src.startswith("file:tests/") and not edge.src.startswith("file:docs/")
        ]
        if refs:
            continue
        severity = "WARN"
        confidence = 0.70
        classification = "PROTOTYPE"
        if path.startswith(("engine/", "game/", "server/")):
            severity = "RISK"
            confidence = 0.82
            classification = "LEGACY"
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="reachability",
                severity=severity,
                confidence=confidence,
                file_path=path,
                evidence=[
                    "No non-test or non-doc incoming references found.",
                    "Likely orphaned or prototype leakage candidate.",
                ],
                suggested_classification=classification,
                recommended_action="RETIRE",
                related_invariants=["NO_SINGLE_USE_CODE_PATHS"],
                related_paths=[path],
            )
        )
        if len(findings) >= 80:
            break
    return findings
