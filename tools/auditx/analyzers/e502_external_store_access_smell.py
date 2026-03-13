"""E502 external store access clean-room smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.dist.clean_room_common import clean_room_violations


ANALYZER_ID = "E502_EXTERNAL_STORE_ACCESS_SMELL"
_RELEVANT_CODES = {
    "refusal.clean_room.external_store_access",
    "refusal.clean_room.absolute_path_leak",
}


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in clean_room_violations(repo_root, platform_tag="win64"):
        item = dict(row or {})
        code = str(item.get("code", "")).strip()
        if code not in _RELEVANT_CODES:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="dist.external_store_access_smell",
                severity="RISK",
                confidence=0.98,
                file_path=rel_path or "data/audit/clean_room_win64.json",
                evidence=[
                    code,
                    str(item.get("message", "")).strip() or "clean-room run escaped the portable bundle",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="KEEP_RUNTIME_OUTPUTS_INSIDE_BUNDLE",
                related_invariants=[str(item.get("rule_id", "")).strip() or "INV-CLEAN-ROOM-MUST-PASS-BEFORE-ARCHIVE"],
                related_paths=[rel_path or "data/audit/clean_room_win64.json", "tools/dist/clean_room_common.py"],
            )
        )
    return findings
