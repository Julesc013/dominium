"""AuditX analyzer registry."""

from analyzers import a1_reachability_orphaned
from analyzers import a2_ownership_boundary
from analyzers import a3_canon_drift
from analyzers import a4_schema_usage


ANALYZERS = (
    a1_reachability_orphaned,
    a2_ownership_boundary,
    a3_canon_drift,
    a4_schema_usage,
)


def run_analyzers(graph, repo_root, changed_files=None):
    findings = []
    for analyzer in ANALYZERS:
        findings.extend(analyzer.run(graph, repo_root, changed_files=changed_files))
    return findings

