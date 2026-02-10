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
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="reachability",
                severity="WARN",
                confidence=0.70,
                file_path=path,
                evidence=[
                    "No non-test or non-doc incoming references found.",
                    "Likely orphaned or prototype leakage candidate.",
                ],
                suggested_classification="PROTOTYPE",
                recommended_action="RETIRE",
                related_invariants=["NO_SINGLE_USE_CODE_PATHS"],
                related_paths=[path],
            )
        )
        if len(findings) >= 80:
            break
    return findings

