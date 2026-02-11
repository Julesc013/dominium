"""Prompt parsing for ControlX."""

from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, List


RAW_TOOL_PATTERNS = (
    (re.compile(r"\bscripts[\\/]+ci[\\/]+check_repox_rules\.py\b", re.IGNORECASE), "raw_repox_call"),
    (re.compile(r"(^|\s)ctest(\s|$)", re.IGNORECASE), "raw_testx_call"),
    (re.compile(r"(^|\s)tool_ui_bind(?:\.exe)?(\s|$)", re.IGNORECASE), "raw_tool_ui_bind_call"),
    (re.compile(r"(^|\s)tool_ui_validate(?:\.exe)?(\s|$)", re.IGNORECASE), "raw_tool_ui_validate_call"),
    (re.compile(r"(^|\s)tool_ui_doc_annotate(?:\.exe)?(\s|$)", re.IGNORECASE), "raw_tool_ui_doc_annotate_call"),
    (re.compile(r"\btools[\\/]+performx[\\/]+performx\.py\b", re.IGNORECASE), "raw_performx_call"),
    (re.compile(r"(^|\s)performx\.py(\s|$)", re.IGNORECASE), "raw_performx_call"),
)

SUBSYSTEM_KEYWORDS = {
    "engine": ("engine/", "domino_engine"),
    "game": ("game/", "dominium_game"),
    "client": ("client/", "dominium_client", "ui"),
    "server": ("server/",),
    "launcher": ("launcher/",),
    "setup": ("setup/",),
    "tools": ("tools/",),
    "schema": ("schema/", ".schema"),
    "data": ("data/", ".json"),
    "docs": ("docs/", ".md"),
    "tests": ("tests/", "ctest", "testx"),
}


def _sha256_text(value: str) -> str:
    return hashlib.sha256((value or "").encode("utf-8")).hexdigest()


def _policy_forbidden_patterns(policy: Dict[str, Any]) -> List[Dict[str, str]]:
    record = policy.get("record", {}) if isinstance(policy, dict) else {}
    rows = record.get("forbidden_patterns", [])
    out: List[Dict[str, str]] = []
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        pattern = str(row.get("pattern", "")).strip()
        if not pattern:
            continue
        out.append(
            {
                "pattern_id": str(row.get("pattern_id", "")).strip() or "policy.pattern",
                "pattern": pattern,
                "reason": str(row.get("reason", "")).strip(),
            }
        )
    return out


def parse_prompt(prompt_text: str, policy: Dict[str, Any]) -> Dict[str, Any]:
    text = str(prompt_text or "")
    lines = text.splitlines()
    forbidden_defs = _policy_forbidden_patterns(policy)
    forbidden: List[Dict[str, Any]] = []
    raw_tool_calls: List[Dict[str, Any]] = []
    subsystems = set()

    compiled_policy = []
    for item in forbidden_defs:
        try:
            compiled_policy.append((re.compile(item["pattern"], re.IGNORECASE), item))
        except re.error:
            continue

    for line_no, line in enumerate(lines, start=1):
        lower = line.lower()
        for subsystem, keys in SUBSYSTEM_KEYWORDS.items():
            for key in keys:
                if key.lower() in lower:
                    subsystems.add(subsystem)
                    break

        for regex, payload in compiled_policy:
            if regex.search(line):
                forbidden.append(
                    {
                        "line": line_no,
                        "directive": payload["pattern_id"],
                        "reason": payload.get("reason", ""),
                        "text": line.strip(),
                    }
                )

        for regex, directive in RAW_TOOL_PATTERNS:
            if regex.search(line):
                raw_tool_calls.append(
                    {
                        "line": line_no,
                        "directive": directive,
                        "text": line.strip(),
                    }
                )

    return {
        "prompt_hash": _sha256_text(text),
        "line_count": len(lines),
        "forbidden_directives": forbidden,
        "raw_tool_calls": raw_tool_calls,
        "requested_subsystems": sorted(subsystems),
        "prompt_text": text,
    }
