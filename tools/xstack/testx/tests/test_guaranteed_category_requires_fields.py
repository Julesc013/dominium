"""FAST test: guaranteed observability categories enforce required fields in strict mode."""

from __future__ import annotations


TEST_ID = "test_guaranteed_category_requires_fields"
TEST_TAGS = ["fast", "observability", "logging"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell2_testlib import ensure_repo_on_path

    ensure_repo_on_path(repo_root)
    from src.appshell.logging import create_log_engine

    engine = create_log_engine(
        product_id="setup",
        build_id="build.test",
        repo_root=repo_root,
        console_enabled=False,
        strict_guarantees=True,
    )
    try:
        engine.emit(
            category="refusal",
            severity="error",
            message_key="appshell.refusal",
            params={
                "refusal_code": "refusal.test.missing_fields",
                "reason": "fixture refusal without remediation",
            },
        )
    except ValueError:
        return {"status": "pass", "message": "strict guaranteed-category enforcement rejected the incomplete refusal log"}
    return {"status": "fail", "message": "strict guaranteed-category enforcement accepted a refusal without remediation_hint"}
