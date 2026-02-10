"""A6 UI parity/bypass analyzer."""

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "A6_UI_PARITY_BYPASS"

SOURCE_EXTS = (".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".py", ".json")
UI_PATH_HINTS = ("/ui/", "ui/", "_gui", "_tui", "views_gui", "views_tui")
CLI_HINTS = ("cli", "command line", "--mode cli")
DISPATCH_HINTS = ("dispatch_command", "command_dispatch", "command_id", "command graph", "command_graph")
COMMAND_ID_RE = re.compile(r"\b(?:client|launcher|setup|server|tool)\.[a-z0-9_.-]+\b")


def _is_ui_path(rel):
    lowered = rel.lower()
    if lowered.startswith(("docs/", "tests/", "legacy/")):
        return False
    return any(hint in lowered for hint in UI_PATH_HINTS)


def _read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _command_ref_map(graph):
    mapping = {}
    for edge in graph.edges:
        if edge.edge_type != "command_ref":
            continue
        src = edge.src.split(":", 1)[1] if ":" in edge.src else edge.src
        dst = edge.dst.split(":", 1)[1] if ":" in edge.dst else edge.dst
        mapping.setdefault(dst, set()).add(src)
    return mapping


def run(graph, repo_root, changed_files=None):
    del changed_files
    findings = []
    command_refs = _command_ref_map(graph)

    for command_id, files in sorted(command_refs.items()):
        if not files:
            continue
        ui_files = sorted(path for path in files if _is_ui_path(path))
        non_ui_files = sorted(path for path in files if not _is_ui_path(path))
        if not ui_files:
            continue
        if non_ui_files:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="ui_parity",
                severity="RISK",
                confidence=0.80,
                file_path=ui_files[0],
                evidence=[
                    "Command appears only in UI-facing files.",
                    "Command id: {}".format(command_id),
                    "No CLI/non-UI references discovered.",
                ],
                suggested_classification="INVALID",
                recommended_action="ADD_TEST",
                related_invariants=["INV-CLI-CANONICAL-UI"],
                related_paths=ui_files,
            )
        )
        if len(findings) >= 80:
            break

    file_nodes = sorted(
        [node for node in graph.nodes.values() if node.node_type == "file"],
        key=lambda item: item.label,
    )
    for node in file_nodes:
        rel = node.label
        if not _is_ui_path(rel):
            continue
        if not rel.lower().endswith(SOURCE_EXTS):
            continue
        text = _read_text(os.path.join(repo_root, rel.replace("/", os.sep))).lower()
        has_command = bool(COMMAND_ID_RE.search(text))
        has_dispatch = any(token in text for token in DISPATCH_HINTS)
        has_cli_anchor = any(token in text for token in CLI_HINTS)
        if has_command and not has_dispatch:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="ui_parity",
                    severity="WARN",
                    confidence=0.65,
                    file_path=rel,
                    evidence=[
                        "UI file references command IDs but dispatcher token was not detected.",
                        "Potential bypass of command graph dispatch path.",
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-CLI-CANONICAL-UI"],
                    related_paths=[rel],
                )
            )
        if ("gui" in rel.lower() or "tui" in rel.lower()) and not has_cli_anchor:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="ui_parity",
                    severity="INFO",
                    confidence=0.45,
                    file_path=rel,
                    evidence=[
                        "GUI/TUI file lacks obvious CLI parity reference tokens.",
                        "Verify this path is represented through canonical command metadata.",
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_TEST",
                    related_invariants=["INV-CLI-CANONICAL-UI"],
                    related_paths=[rel],
                )
            )
        if len(findings) >= 180:
            break

    return sorted(findings, key=lambda item: (item.location.file, item.severity, item.confidence))

