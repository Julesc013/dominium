"""A2 Ownership boundary analyzer."""

import os

from analyzers.base import make_finding


ANALYZER_ID = "A2_OWNERSHIP_BOUNDARY"

MUTATION_TOKENS = (
    "write(",
    "open(",
    "mkdir(",
    "makedirs(",
    "remove(",
    "unlink(",
    "rename(",
    "replace(",
)

INSTALL_TOKENS = (
    "install.manifest",
    "install_root",
    "package_store",
    "rollback",
    "cache-add",
)

USER_SETTINGS_TOKENS = (
    "user_settings",
    "settings.json",
    "client_settings",
    "launcher_settings",
    "setup_settings",
)


def _read_file(repo_root, rel):
    path = os.path.join(repo_root, rel.replace("/", os.sep))
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _contains_any(text, tokens):
    lowered = text.lower()
    return any(token.lower() in lowered for token in tokens)


def _find_suspect_files(graph, prefix):
    files = []
    for node in graph.nodes.values():
        if node.node_type != "file":
            continue
        if node.label.startswith(prefix):
            files.append(node.label)
    return sorted(files)


def run(graph, repo_root, changed_files=None):
    del changed_files
    findings = []

    for rel in _find_suspect_files(graph, "client/"):
        text = _read_file(repo_root, rel)
        if _contains_any(text, MUTATION_TOKENS) and _contains_any(text, INSTALL_TOKENS):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="ownership_boundary",
                    severity="RISK",
                    confidence=0.75,
                    file_path=rel,
                    evidence=[
                        "Client path appears to combine install tokens with mutation operations.",
                        "Client should remain presentation-only for install mutation.",
                    ],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-SETTINGS-OWNERSHIP"],
                    related_paths=[rel],
                )
            )

    for rel in _find_suspect_files(graph, "launcher/"):
        text = _read_file(repo_root, rel)
        if _contains_any(text, MUTATION_TOKENS) and _contains_any(text, INSTALL_TOKENS):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="ownership_boundary",
                    severity="RISK",
                    confidence=0.70,
                    file_path=rel,
                    evidence=[
                        "Launcher path appears to directly mutate install-managed artifacts.",
                        "Setup should be the install mutation authority.",
                    ],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-SETTINGS-OWNERSHIP"],
                    related_paths=[rel],
                )
            )

    for prefix in ("engine/", "game/"):
        for rel in _find_suspect_files(graph, prefix):
            text = _read_file(repo_root, rel)
            if _contains_any(text, USER_SETTINGS_TOKENS):
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="ownership_boundary",
                        severity="VIOLATION",
                        confidence=0.80,
                        file_path=rel,
                        evidence=[
                            "Engine/Game path appears to reference user settings payloads directly.",
                            "Runtime parameters should be explicit and injected by launcher/server.",
                        ],
                        suggested_classification="INVALID",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-NO-ENGINE-SETTINGS"],
                        related_paths=[rel],
                    )
                )

    for rel in _find_suspect_files(graph, "libs/"):
        if "/ui_" not in rel and "/ui/" not in rel:
            continue
        text = _read_file(repo_root, rel)
        if "dispatch_command" not in text and "command_dispatch" not in text and "command_id" in text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="ownership_boundary",
                    severity="WARN",
                    confidence=0.55,
                    file_path=rel,
                    evidence=[
                        "UI-related file references command IDs but no dispatcher token was found.",
                        "Potential UI bypass of canonical command dispatcher.",
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_TEST",
                    related_invariants=["INV-CLI-CANONICAL-UI"],
                    related_paths=[rel],
                )
            )

    return sorted(findings, key=lambda item: (item.location.file, item.severity))

