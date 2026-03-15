"""FAST test: concurrency scan detects a threaded truth mutation fixture."""

from __future__ import annotations

import os


TEST_ID = "test_detect_threading_violation_fixture"
TEST_TAGS = ["fast", "concurrency", "audit"]


def run(repo_root: str):
    from tools.audit.arch_audit_common import scan_parallel_truth

    fixture_rel = os.path.join("build", "tmp", "concurrency_fixture_truth_violation.py")
    fixture_abs = os.path.join(repo_root, fixture_rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(fixture_abs), exist_ok=True)
    with open(fixture_abs, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(
            "\n".join(
                [
                    "from concurrent.futures import ThreadPoolExecutor",
                    "",
                    "def mutate_truth(state):",
                    "    with ThreadPoolExecutor(max_workers=2) as pool:",
                    "        pool.submit(lambda: state.__setitem__('truth_value', 1))",
                    "    return state",
                    "",
                ]
            )
        )
    report = scan_parallel_truth(repo_root, override_paths=[fixture_rel])
    rows = list(dict(report or {}).get("blocking_findings") or [])
    if not rows:
        return {"status": "fail", "message": "threaded truth mutation fixture was not detected"}
    snippets = " ".join(str(dict(row).get("snippet", "")).strip() for row in rows)
    if "ThreadPoolExecutor" not in snippets:
        return {"status": "fail", "message": "threaded truth mutation scan did not report the concurrency primitive"}
    return {"status": "pass", "message": "threaded truth mutation fixture detected"}
