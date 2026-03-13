"""FAST test: legacy validate_all wrapper routes through the unified validation pipeline."""

from __future__ import annotations


TEST_ID = "test_legacy_validator_calls_unified_pipeline"
TEST_TAGS = ["fast", "validation", "shims", "compat"]


def run(repo_root: str):
    from tools.xstack.testx.tests.repo_layout1_testlib import run_legacy_validator

    report = run_legacy_validator(repo_root, strict=False)
    validation_id = str(report.get("validation_id", "")).strip()
    if not validation_id.startswith("validation.pipeline."):
        return {"status": "fail", "message": "legacy validation shim did not return the unified validation result schema"}
    shim = dict(dict(report.get("extensions") or {}).get("legacy_shim") or {})
    if str(shim.get("legacy_surface", "")).strip() != "tools/ci/validate_all.py":
        return {"status": "fail", "message": "legacy validation shim metadata is missing the legacy surface id"}
    if "validate --all" not in str(shim.get("replacement_surface", "")):
        return {"status": "fail", "message": "legacy validation shim metadata is missing the canonical replacement surface"}
    if not list(report.get("suite_results") or []):
        return {"status": "fail", "message": "legacy validation shim did not return unified suite results"}
    return {"status": "pass", "message": "legacy validate_all wrapper routes through the unified validation pipeline"}
