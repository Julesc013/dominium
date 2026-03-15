"""E531 secrets in log smell analyzer for OBSERVABILITY-0."""

from __future__ import annotations

import os
import re


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding


ANALYZER_ID = "E531_SECRETS_IN_LOG_SMELL"
RULE_ID = "INV-NO-SECRETS-IN-LOGS"
SCAN_FILES = (
    "src/appshell/logging/log_engine.py",
    "src/appshell/bootstrap.py",
    "src/appshell/commands/command_engine.py",
    "tools/setup/setup_cli.py",
    "src/appshell/supervisor/supervisor_engine.py",
)
SECRET_RE = re.compile(r"(password|private_key|signing_key|auth_token|credential|secret)", re.IGNORECASE)


def _file_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for rel_path in SCAN_FILES:
        text = _file_text(repo_root, rel_path)
        if not text:
            continue
        if rel_path == "src/appshell/logging/log_engine.py" and "redact_observability_mapping(" not in text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="observability.secrets_in_log_smell",
                    severity="RISK",
                    confidence=0.99,
                    file_path=rel_path,
                    evidence=["structured log engine is missing deterministic secret redaction"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ROUTE_LOG_FIELDS_THROUGH_THE_OBSERVABILITY_REDACTION_HELPER",
                    related_invariants=[RULE_ID],
                    related_paths=[rel_path],
                )
            )
            continue
        if rel_path != "src/appshell/logging/log_engine.py" and SECRET_RE.search(text) and "appshell.refusal" not in text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="observability.secrets_in_log_smell",
                    severity="RISK",
                    confidence=0.75,
                    file_path=rel_path,
                    evidence=["secret-like token appears in a governed logging surface"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REDACT_OR_REMOVE_SECRET-LIKE_FIELDS_FROM_LOGGING_PAYLOADS",
                    related_invariants=[RULE_ID],
                    related_paths=[rel_path, "src/appshell/logging/log_engine.py"],
                )
            )
    return findings
