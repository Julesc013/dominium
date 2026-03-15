import os

from tools.xstack.testx.tests.performance_envelope_testlib import (
    baseline_doc_path,
    doctrine_doc_path,
    ensure_assets,
    report_doc_path,
    report_json_path,
    retro_doc_path,
)


def run(repo_root: str) -> dict:
    outputs = ensure_assets(repo_root)
    assert outputs["report"]["result"] == "complete"
    for path in (
        report_json_path(repo_root),
        report_doc_path(repo_root),
        baseline_doc_path(repo_root),
        retro_doc_path(repo_root),
        doctrine_doc_path(repo_root),
    ):
        assert os.path.isfile(path), path
    return {
        "status": "pass",
        "message": "performance envelope reports and doctrine artifacts are generated",
    }
