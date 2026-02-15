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

SIMULATION_MUTATION_TOKENS = (
    "universe_state",
    "truth_model",
    "simulation_time",
    "process_runtime",
    "set_simulation_time",
)

USER_SETTINGS_TOKENS = (
    "user_settings",
    "settings.json",
    "client_settings",
    "launcher_settings",
    "setup_settings",
)

DISPATCH_TOKENS = (
    "dispatch_command",
    "command_dispatch",
    "intent_pipeline",
    "submit_intent",
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
                    confidence=0.78,
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
        if _contains_any(text, MUTATION_TOKENS) and _contains_any(text, SIMULATION_MUTATION_TOKENS):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="ownership_boundary",
                    severity="VIOLATION",
                    confidence=0.84,
                    file_path=rel,
                    evidence=[
                        "Launcher appears to mutate simulation state directly.",
                        "Launcher must route mutation through canonical session/process boundaries.",
                    ],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-LAUNCHER-NO-SIM-MUTATION"],
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
                        confidence=0.82,
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

    ui_prefixes = ("client/", "launcher/", "tools/", "libs/")
    for prefix in ui_prefixes:
        for rel in _find_suspect_files(graph, prefix):
            lowered = rel.lower()
            if "/ui/" not in lowered and "/presentation/" not in lowered and "ui_" not in lowered:
                continue
            text = _read_file(repo_root, rel)
            has_command_ref = "command_id" in text.lower() or "client." in text.lower()
            if has_command_ref and not _contains_any(text, DISPATCH_TOKENS):
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="ownership_boundary",
                        severity="WARN",
                        confidence=0.63,
                        file_path=rel,
                        evidence=[
                            "UI-facing file references command IDs but dispatcher tokens were not detected.",
                            "Potential UI bypass of canonical command dispatcher.",
                        ],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="ADD_TEST",
                        related_invariants=["INV-CLI-CANONICAL-UI"],
                        related_paths=[rel],
                    )
                )

    return sorted(findings, key=lambda item: (item.location.file_path, item.severity))
