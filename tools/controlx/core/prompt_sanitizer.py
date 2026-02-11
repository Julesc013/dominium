"""Prompt sanitizer for ControlX prompt firewall."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List


def _execution_plan(policy: Dict[str, Any]) -> List[str]:
    record = policy.get("record", {}) if isinstance(policy, dict) else {}
    run_mode = record.get("run_mode", {}) if isinstance(record.get("run_mode"), dict) else {}
    precheck = str(run_mode.get("precheck", "precheck")).strip() or "precheck"
    taskcheck = str(run_mode.get("taskcheck", "taskcheck")).strip() or "taskcheck"
    exitcheck = str(run_mode.get("exitcheck", "exitcheck")).strip() or "exitcheck"
    return [
        "python scripts/dev/gate.py {}".format(precheck),
        "apply.sanitized_changes",
        "python scripts/dev/gate.py {}".format(taskcheck),
        "python scripts/dev/gate.py {}".format(exitcheck),
    ]


def sanitize_prompt(parsed_prompt: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
    text = str(parsed_prompt.get("prompt_text", "") or "")
    lines = text.splitlines()
    forbidden = list(parsed_prompt.get("forbidden_directives", []))
    raw_tool_calls = list(parsed_prompt.get("raw_tool_calls", []))
    blocked_lines = set()
    actions: List[Dict[str, Any]] = []

    for row in forbidden:
        line = int(row.get("line", 0) or 0)
        if line > 0:
            blocked_lines.add(line)
            actions.append(
                {
                    "action": "remove_forbidden_directive",
                    "line": line,
                    "directive": row.get("directive", ""),
                    "reason": row.get("reason", ""),
                }
            )

    for row in raw_tool_calls:
        line = int(row.get("line", 0) or 0)
        if line > 0:
            blocked_lines.add(line)
            actions.append(
                {
                    "action": "remove_raw_tool_call",
                    "line": line,
                    "directive": row.get("directive", ""),
                }
            )

    sanitized_lines = []
    for idx, line in enumerate(lines, start=1):
        if idx in blocked_lines:
            continue
        sanitized_lines.append(line)

    if not sanitized_lines:
        sanitized_lines = ["# controlx: sanitized prompt body intentionally empty"]

    return {
        "prompt_hash": parsed_prompt.get("prompt_hash", ""),
        "sanitized_prompt": "\n".join(sanitized_lines).strip() + "\n",
        "actions": sorted(actions, key=lambda item: (int(item.get("line", 0) or 0), str(item.get("action", "")))),
        "execution_plan": _execution_plan(policy),
    }


def write_sanitization_report(path: str, parsed_prompt: Dict[str, Any], sanitized_prompt: Dict[str, Any]) -> None:
    import os

    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("Status: DERIVED\n")
        handle.write("Last Reviewed: {}\n".format(datetime.utcnow().strftime("%Y-%m-%d")))
        handle.write("Supersedes: none\n")
        handle.write("Superseded By: none\n\n")
        handle.write("# ControlX Sanitization Report\n\n")
        handle.write("- prompt_hash: `{}`\n".format(parsed_prompt.get("prompt_hash", "")))
        handle.write("- forbidden_directive_count: `{}`\n".format(len(parsed_prompt.get("forbidden_directives", []))))
        handle.write("- raw_tool_call_count: `{}`\n".format(len(parsed_prompt.get("raw_tool_calls", []))))
        handle.write("\n## Actions\n\n")
        actions = sanitized_prompt.get("actions", [])
        if not actions:
            handle.write("- none\n")
        else:
            for item in actions:
                handle.write(
                    "- line {}: {} `{}`\n".format(
                        item.get("line", 0),
                        item.get("action", ""),
                        item.get("directive", ""),
                    )
                )
        handle.write("\n## Execution Plan\n\n")
        for item in sanitized_prompt.get("execution_plan", []):
            handle.write("- `{}`\n".format(item))
