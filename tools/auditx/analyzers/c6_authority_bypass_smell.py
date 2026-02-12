"""C6 Authority bypass smell analyzer."""

import os

from analyzers.base import make_finding


ANALYZER_ID = "C6_AUTHORITY_BYPASS_SMELL"


def _read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    schema_rel = "schema/authority/authority_context.schema"
    client_rel = "client/core/client_command_bridge.c"
    server_rel = "server/authority/dom_server_authority.cpp"

    schema_text = _read(os.path.join(repo_root, schema_rel.replace("/", os.sep)))
    client_text = _read(os.path.join(repo_root, client_rel.replace("/", os.sep)))
    server_text = _read(os.path.join(repo_root, server_rel.replace("/", os.sep)))

    if "authority_origin" not in schema_text or "law_profile_id" not in schema_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="authority_bypass_smell",
                severity="RISK",
                confidence=0.88,
                file_path=schema_rel,
                evidence=["AuthorityContext schema is missing baseline authority fields."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-AUTHORITY_CONTEXT_REQUIRED_FOR_INTENTS"],
                related_paths=[schema_rel],
            )
        )
        return findings

    for marker in ("authority_context_id", "refuse.entitlement_required"):
        if marker not in client_text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="authority_bypass_smell",
                    severity="WARN",
                    confidence=0.78,
                    file_path=client_rel,
                    evidence=["Client bridge missing authority marker '{}'".format(marker)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_TEST",
                    related_invariants=["INV-AUTHORITY_CONTEXT_REQUIRED_FOR_INTENTS"],
                    related_paths=[client_rel],
                )
            )

    for marker in ("dom_server_authority_check_with_context", "server_authoritative", "DOM_AUTH_REFUSE_PROFILE_INSUFFICIENT"):
        if marker not in server_text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="authority_bypass_smell",
                    severity="RISK",
                    confidence=0.82,
                    file_path=server_rel,
                    evidence=["Server authority path missing marker '{}'".format(marker)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-AUTHORITY_CONTEXT_REQUIRED_FOR_INTENTS"],
                    related_paths=[server_rel],
                )
            )

    return findings
