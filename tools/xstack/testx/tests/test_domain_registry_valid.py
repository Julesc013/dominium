"""STRICT test: domain foundation registry validates with no errors."""

from __future__ import annotations

import sys


TEST_ID = "testx.domain.registry_valid"
TEST_TAGS = ["strict", "schema", "repox"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.domain.tool_domain_validate import validate_domain_foundation

    result = validate_domain_foundation(repo_root=repo_root)
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "domain foundation validator returned refusal"}
    summary = dict(result.get("summary") or {})
    if int(summary.get("domain_count", 0) or 0) < 10:
        return {"status": "fail", "message": "domain registry has fewer than expected baseline rows"}
    return {"status": "pass", "message": "domain registry validation passed"}
