"""A5 Capability misuse analyzer."""

import os
import re
import json

from analyzers.base import make_finding


ANALYZER_ID = "A5_CAPABILITY_MISUSE"

SOURCE_EXTS = (".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".py")
REGISTRY_EXTS = (".json", ".schema", ".md")
PLATFORM_CHECK_RE = re.compile(
    r"(#\s*(?:if|ifdef|ifndef)\s+.*(?:_WIN32|_WIN64|__linux__|__APPLE__|__EMSCRIPTEN__))|"
    r"(?:platform\s*==\s*[\"'][A-Za-z0-9_.:-]+[\"'])|"
    r"(?:arch\s*==\s*[\"'][A-Za-z0-9_.:-]+[\"'])",
    re.IGNORECASE,
)
CAPABILITY_ID_RE = re.compile(r"\b(?:capability\.[a-z0-9_.:-]+|cap:[a-z0-9_.:-]+)\b", re.IGNORECASE)
COMMAND_REGISTRY_HINTS = ("command_registry", "commands_registry", "command graph", "command_graph")
REQUIRED_CAPABILITY_HINTS = ("required_capabilities", "required_capability", "capability_requirements")
COMMAND_ID_TOKEN = "command_id"


def _read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _iter_file_nodes(graph):
    return sorted(
        [node for node in graph.nodes.values() if node.node_type == "file"],
        key=lambda item: item.label,
    )


def _collect_declared_capabilities(repo_root, file_nodes):
    declared = set()
    for node in file_nodes:
        rel = node.label
        if not rel.startswith(("data/", "schema/", "docs/")):
            continue
        if not rel.lower().endswith(REGISTRY_EXTS):
            continue
        text = _read_text(os.path.join(repo_root, rel.replace("/", os.sep)))
        for match in CAPABILITY_ID_RE.finditer(text):
            declared.add(match.group(0).lower())
    return declared


def _collect_capability_references(repo_root, file_nodes):
    references = {}
    for node in file_nodes:
        rel = node.label
        if rel.startswith(("data/", "schema/", "docs/")):
            continue
        if not rel.lower().endswith(SOURCE_EXTS):
            continue
        text = _read_text(os.path.join(repo_root, rel.replace("/", os.sep)))
        caps = set(match.group(0).lower() for match in CAPABILITY_ID_RE.finditer(text))
        if caps:
            references[rel] = caps
    return references


def run(graph, repo_root, changed_files=None):
    del changed_files
    findings = []
    file_nodes = _iter_file_nodes(graph)

    for node in file_nodes:
        rel = node.label
        if rel.startswith(("legacy/", "docs/", "tests/", "dist/", "out/", "build/")):
            continue
        if not rel.lower().endswith(SOURCE_EXTS):
            continue
        text = _read_text(os.path.join(repo_root, rel.replace("/", os.sep)))
        if PLATFORM_CHECK_RE.search(text):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="capability_misuse",
                    severity="WARN",
                    confidence=0.70,
                    file_path=rel,
                    evidence=[
                        "Direct platform/arch conditional detected in runtime-facing source.",
                        "Prefer capability-based gating where possible.",
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-CAPABILITY-GATED-RUNTIME"],
                    related_paths=[rel],
                )
            )
            if len(findings) >= 60:
                break

    for node in file_nodes:
        rel = node.label.lower()
        if not rel.endswith(SOURCE_EXTS):
            continue
        if not any(hint in rel for hint in COMMAND_REGISTRY_HINTS):
            continue
        text = _read_text(os.path.join(repo_root, node.label.replace("/", os.sep))).lower()
        if "command" not in text:
            continue
        if any(hint in text for hint in REQUIRED_CAPABILITY_HINTS):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="capability_misuse",
                severity="RISK",
                confidence=0.65,
                file_path=node.label,
                evidence=[
                    "Command registry-like file does not advertise required capability metadata.",
                    "Commands should declare required_capabilities for deterministic refusal paths.",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-COMMAND-CAPABILITY-DECLARED"],
                related_paths=[node.label],
            )
        )
        if len(findings) >= 120:
            break

    declared_capabilities = _collect_declared_capabilities(repo_root, file_nodes)
    reference_map = _collect_capability_references(repo_root, file_nodes)
    referenced_capabilities = set()
    for caps in reference_map.values():
        referenced_capabilities.update(caps)

    missing_refs = sorted(cap for cap in declared_capabilities if cap not in referenced_capabilities)
    for capability_id in missing_refs[:80]:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="capability_misuse",
                severity="INFO",
                confidence=0.45,
                file_path="data/registries",
                evidence=[
                    "Declared capability appears unreferenced in runtime/tool source scans.",
                    "Capability id: {}".format(capability_id),
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_TEST",
                related_invariants=["INV-CAPABILITY-GATED-RUNTIME"],
                related_paths=["data/registries"],
            )
        )

    registries_root = os.path.join(repo_root, "data", "registries")
    if os.path.isdir(registries_root):
        for name in sorted(os.listdir(registries_root)):
            if not name.endswith(".json"):
                continue
            rel = "data/registries/{}".format(name)
            abs_path = os.path.join(registries_root, name)
            try:
                payload = json.load(open(abs_path, "r", encoding="utf-8"))
            except (OSError, ValueError):
                continue
            rows = []
            if isinstance(payload, dict):
                if isinstance(payload.get("records"), list):
                    rows = [row for row in payload.get("records") if isinstance(row, dict)]
                elif isinstance((payload.get("record") or {}).get("entries"), list):
                    rows = [row for row in (payload.get("record") or {}).get("entries") if isinstance(row, dict)]
            for row in rows:
                if COMMAND_ID_TOKEN not in row:
                    continue
                command_id = str(row.get(COMMAND_ID_TOKEN, "")).strip()
                caps = row.get("required_capabilities")
                if isinstance(caps, list) and any(str(item).strip() for item in caps):
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="capability_misuse",
                        severity="RISK",
                        confidence=0.72,
                        file_path=rel,
                        evidence=[
                            "Command '{}' is declared without required_capabilities metadata.".format(command_id or "<unknown>"),
                            "Commands should be capability-gated for deterministic refusal behavior.",
                        ],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-COMMAND-CAPABILITY-DECLARED"],
                        related_paths=[rel],
                    )
                )
                if len(findings) >= 200:
                    break
            if len(findings) >= 200:
                break

    return sorted(findings, key=lambda item: (item.location.file_path, item.severity, item.confidence))
