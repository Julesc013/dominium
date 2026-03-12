"""E471 direct simulation start smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.entrypoint_unify_common import entrypoint_unify_violations


ANALYZER_ID = "E471_DIRECT_SIMULATION_START_SMELL"
WATCH_PREFIXES = (
    "src/server/",
    "tools/launcher/",
    "tools/mvp/",
    "tools/setup/",
    "tools/release/",
)
TARGET_CODES = {"direct_simulation_start", "multiplexer_bypass", "product_not_unified"}


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in entrypoint_unify_violations(repo_root):
        item = dict(row or {})
        code = str(item.get("code", "")).strip()
        if code not in TARGET_CODES:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="appshell.direct_simulation_start_smell",
                severity="RISK",
                confidence=0.98,
                file_path=rel_path,
                evidence=[
                    "code={}".format(code),
                    str(item.get("message", "")).strip() or "entrypoint bypasses AppShell bootstrap discipline",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="UNIFY_ENTRYPOINT",
                related_invariants=[str(item.get("rule_id", "")).strip() or "INV-ALL-PRODUCTS-USE-APPSHELL"],
                related_paths=[rel_path],
            )
        )
    return findings
