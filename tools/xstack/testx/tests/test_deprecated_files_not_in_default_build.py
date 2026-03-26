"""FAST test: XI-4 applied deprecations are not left in the default build graph."""

from __future__ import annotations


TEST_ID = "test_deprecated_files_not_in_default_build"
TEST_TAGS = ["fast", "xi", "convergence", "deprecations"]


def run(repo_root: str):
    from tools.xstack.testx.tests.convergence_execution_testlib import committed_build_graph, committed_convergence_execution_log

    build_graph = committed_build_graph(repo_root)
    execution_log = committed_convergence_execution_log(repo_root)
    build_sources = {
        str(source).replace("\\", "/")
        for target in list(build_graph.get("targets") or [])
        if isinstance(target, dict)
        for source in list(target.get("sources") or [])
        if str(source).strip()
    }
    offenders = []
    for row in list(execution_log.get("entries") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("kind", "")).strip() != "deprecate":
            continue
        if str(row.get("result", "")).strip() != "applied":
            continue
        secondary_file = str(row.get("secondary_file", "")).replace("\\", "/").strip()
        if secondary_file and secondary_file in build_sources:
            offenders.append(secondary_file)
    if offenders:
        return {"status": "fail", "message": "deprecated files still appear in default build targets: {}".format(", ".join(sorted(set(offenders))[:6]))}
    return {"status": "pass", "message": "applied deprecated files are not present in the default build graph"}
