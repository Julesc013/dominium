"""FAST test: governed native adapters, when present, remain thin command/UI-model bindings."""

from __future__ import annotations


TEST_ID = "test_native_adapter_only_calls_command_engine"
TEST_TAGS = ["fast", "ui", "audit"]


def run(repo_root: str):
    from tools.xstack.testx.tests.ui_reconcile_testlib import build_report, violations

    report = build_report(repo_root)
    adapter_violations = [
        dict(row)
        for row in violations(repo_root)
        if str(dict(row).get("code", "")).strip() in {"native_adapter_not_command_only", "ui_adapter_business_logic"}
    ]
    if adapter_violations:
        first = dict(adapter_violations[0])
        return {
            "status": "fail",
            "message": "native/governed UI adapter violation at {} ({})".format(
                str(first.get("file_path", "")).strip(),
                str(first.get("code", "")).strip(),
            ),
        }
    native_rows = [
        dict(row)
        for row in list(report.get("legacy_surfaces") or [])
        if "native_" in str(dict(row).get("path", "")).strip()
    ]
    if not native_rows:
        return {"status": "pass", "message": "no governed native adapters are present; deterministic fallback remains in effect"}
    return {"status": "pass", "message": "native adapters remain thin command/UI-model bindings"}

