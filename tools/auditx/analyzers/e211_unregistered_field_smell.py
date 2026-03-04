"""E211 unregistered field smell analyzer."""

from __future__ import annotations

import json
import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E211_UNREGISTERED_FIELD_SMELL"


class UnregisteredFieldSmell:
    analyzer_id = ANALYZER_ID


_FIELD_TOKEN_PATTERN = re.compile(r"\bfield\.[A-Za-z0-9_.-]+\b")


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _registered_field_ids(repo_root: str) -> set[str]:
    rel_path = "data/registries/field_type_registry.json"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    rows = list((dict(payload.get("record") or {})).get("field_types") or [])
    out: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        field_type_id = str(row.get("field_type_id", "")).strip()
        field_id = str(row.get("field_id", "")).strip()
        if field_type_id:
            out.add(field_type_id)
        if field_id:
            out.add(field_id)
    return out


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    registered_field_ids = _registered_field_ids(repo_root)
    if not registered_field_ids:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unregistered_field_smell",
                severity="RISK",
                confidence=0.9,
                file_path="data/registries/field_type_registry.json",
                line=1,
                evidence=["field_type_registry missing/invalid; field registration cannot be enforced"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-FIELD-TYPE-REGISTERED"],
                related_paths=["data/registries/field_type_registry.json"],
            )
        )
        return findings

    allowed_non_field_tokens = {
        "field.static",
        "field.static_default",
        "field.scheduled",
        "field.scheduled_linear",
        "field.profile_defined",
        "field.flow_linked",
        "field.hazard_linked",
        "field.update_policy_guard",
        "field.free_motion.influence",
    }
    field_id_context_markers = (
        "field_id",
        "field_type_id",
        "input_id",
        "get_field_value(",
        "field_type_rows",
    )

    scan_roots = (
        os.path.join(repo_root, "src", "fields"),
        os.path.join(repo_root, "src", "models"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )

    for root in scan_roots:
        if not os.path.isdir(root):
            continue
        for walk_root, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path.startswith(skip_prefixes):
                    continue
                if rel_path not in {
                    "src/models/model_engine.py",
                    "tools/xstack/sessionx/process_runtime.py",
                } and not rel_path.startswith("src/fields/"):
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if "refusal.field." in snippet.lower():
                        continue
                    if not any(marker in snippet.lower() for marker in field_id_context_markers):
                        continue
                    unknown_tokens = []
                    for token in _FIELD_TOKEN_PATTERN.findall(snippet):
                        candidate = str(token).strip().rstrip(".,:;")
                        lowered = candidate.lower()
                        if lowered.endswith(".json") or lowered.endswith(".schema") or lowered.endswith(".schema.json"):
                            continue
                        if candidate in allowed_non_field_tokens:
                            continue
                        if candidate in registered_field_ids:
                            continue
                        unknown_tokens.append(candidate)
                    if not unknown_tokens:
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.unregistered_field_smell",
                            severity="RISK",
                            confidence=0.8,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["field token is not registered in field_type_registry", ",".join(sorted(set(unknown_tokens)))],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=["INV-FIELD-TYPE-REGISTERED"],
                            related_paths=[rel_path, "data/registries/field_type_registry.json"],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
