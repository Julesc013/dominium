#!/usr/bin/env python3
"""Run Dominium test/proof tiers and write evidence."""

from __future__ import annotations

import argparse
import ast
import datetime as _dt
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - older Python fallback.
    tomllib = None  # type: ignore[assignment]


CONTRACT_REL = Path("contracts") / "testing" / "test_tiers.contract.toml"
TASK_JSON_REL = Path(".aide") / "reports" / "FAST-STRICT-TEST-TIER-01-run.json"
TASK_MD_REL = Path(".aide") / "reports" / "FAST-STRICT-TEST-TIER-01-run.md"
GENERATED_STAGE_PREFIXES = (
    ".dominium.local/",
    ".aide.local/",
    ".xstack_cache/",
    "build/",
    "out/",
    "dist/",
    "artifacts/",
    "tmp/",
    "__pycache__/",
    "archive/generated/artifacts/",
    "run_meta/",
)
FORBIDDEN_TOP_LEVEL_ROOTS = ("src", "source", "sources", "common_source")
OUTPUT_LIMIT = 4000


def _repo_root(value: str | None) -> Path:
    if value:
        return Path(value).resolve()
    return Path(__file__).resolve().parents[2]


def _load_contract(repo_root: Path) -> dict[str, Any]:
    path = repo_root / CONTRACT_REL
    if tomllib is None:
        return _load_toml_fallback(path)
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _strip_comment(line: str) -> str:
    in_string = False
    escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_string:
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if char == "#" and not in_string:
            return line[:index]
    return line


def _parse_value(text: str) -> Any:
    value = text.strip()
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith('"') and value.endswith('"'):
        return ast.literal_eval(value)
    if value.startswith("[") and value.endswith("]"):
        return ast.literal_eval(value)
    try:
        return int(value)
    except ValueError:
        return value


def _target(root: dict[str, Any], parts: list[str]) -> dict[str, Any]:
    current = root
    for part in parts:
        child = current.setdefault(part, {})
        if not isinstance(child, dict):
            raise ValueError(f"TOML table conflicts with scalar: {'.'.join(parts)}")
        current = child
    return current


def _logical_lines(path: Path) -> list[str]:
    lines: list[str] = []
    pending = ""
    balance = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = _strip_comment(raw).strip()
        if not line:
            continue
        if pending:
            pending += " " + line
        else:
            pending = line
        balance += line.count("[") - line.count("]")
        if balance <= 0:
            lines.append(pending)
            pending = ""
            balance = 0
    if pending:
        lines.append(pending)
    return lines


def _load_toml_fallback(path: Path) -> dict[str, Any]:
    root: dict[str, Any] = {}
    current = root
    for line in _logical_lines(path):
        if line.startswith("[[") and line.endswith("]]"):
            parts = [part.strip() for part in line[2:-2].split(".") if part.strip()]
            if not parts:
                raise ValueError("empty TOML array table")
            parent = _target(root, parts[:-1]) if len(parts) > 1 else root
            commands = parent.setdefault(parts[-1], [])
            if not isinstance(commands, list):
                raise ValueError(f"{'.'.join(parts)} must be an array")
            current = {}
            commands.append(current)
            continue
        if line.startswith("[") and line.endswith("]"):
            parts = [part.strip() for part in line[1:-1].split(".") if part.strip()]
            current = _target(root, parts)
            continue
        if "=" not in line:
            raise ValueError(f"invalid TOML assignment: {line}")
        key, value = line.split("=", 1)
        current[key.strip()] = _parse_value(value)
    return root


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_git(repo_root: Path, args: list[str]) -> tuple[int, list[str], str]:
    try:
        completed = subprocess.run(
            ["git"] + args,
            cwd=str(repo_root),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
        )
    except Exception as exc:  # noqa: BLE001
        return 1, [], str(exc)
    lines = [line.strip() for line in (completed.stdout or "").splitlines() if line.strip()]
    return completed.returncode, lines, completed.stdout or ""


def _changed_paths(repo_root: Path) -> list[str]:
    paths: set[str] = set()
    for args in (
        ["diff", "--name-only"],
        ["diff", "--cached", "--name-only"],
        ["ls-files", "--others", "--exclude-standard"],
    ):
        _code, lines, _out = _run_git(repo_root, args)
        for line in lines:
            if " -> " in line:
                for part in line.split(" -> "):
                    paths.add(part.replace("\\", "/"))
            else:
                paths.add(line.replace("\\", "/"))
    return sorted(paths)


def _staged_paths(repo_root: Path) -> list[str]:
    _code, lines, _out = _run_git(repo_root, ["diff", "--cached", "--name-only"])
    return sorted(line.replace("\\", "/") for line in lines)


def _tracked_paths(repo_root: Path) -> list[str]:
    _code, lines, _out = _run_git(repo_root, ["ls-files"])
    return sorted(line.replace("\\", "/") for line in lines)


def _summary(text: str, limit: int = OUTPUT_LIMIT) -> str:
    text = text.replace("\r\n", "\n")
    if len(text) <= limit:
        return text
    head = limit // 2
    tail = limit - head
    return text[:head] + "\n...[truncated]...\n" + text[-tail:]


def _builtin_staged_generated_output_check(repo_root: Path) -> tuple[str, int, str]:
    bad = []
    for path in _staged_paths(repo_root):
        normalized = path.replace("\\", "/")
        for prefix in GENERATED_STAGE_PREFIXES:
            if normalized == prefix.rstrip("/") or normalized.startswith(prefix):
                bad.append(normalized)
                break
    if bad:
        return "fail", 1, "forbidden staged generated/local paths:\n" + "\n".join(bad)
    return "pass", 0, "no forbidden generated/local output paths are staged"


def _builtin_changed_json_parse(repo_root: Path) -> tuple[str, int, str]:
    failures = []
    checked = []
    for rel in _changed_paths(repo_root):
        path = repo_root / rel
        if not path.is_file():
            continue
        lower = rel.lower()
        if not (lower.endswith(".json") or lower.endswith(".jsonl")):
            continue
        checked.append(rel)
        try:
            if lower.endswith(".jsonl"):
                with path.open("r", encoding="utf-8") as handle:
                    for line_number, line in enumerate(handle, 1):
                        if line.strip():
                            json.loads(line)
            else:
                with path.open("r", encoding="utf-8") as handle:
                    json.load(handle)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{rel}: {exc}")
    if failures:
        return "fail", 1, "JSON parse failures:\n" + "\n".join(failures)
    return "pass", 0, f"parsed {len(checked)} changed JSON/JSONL file(s)"


def _builtin_changed_toml_parse(repo_root: Path) -> tuple[str, int, str]:
    failures = []
    checked = []
    for rel in _changed_paths(repo_root):
        path = repo_root / rel
        if not path.is_file() or not rel.lower().endswith(".toml"):
            continue
        checked.append(rel)
        try:
            if tomllib is None:
                _load_toml_fallback(path)
            else:
                with path.open("rb") as handle:
                    tomllib.load(handle)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{rel}: {exc}")
    if failures:
        return "fail", 1, "TOML parse failures:\n" + "\n".join(failures)
    return "pass", 0, f"parsed {len(checked)} changed TOML file(s)"


def _builtin_forbidden_active_roots(repo_root: Path) -> tuple[str, int, str]:
    bad = []
    tracked = _tracked_paths(repo_root)
    for root in FORBIDDEN_TOP_LEVEL_ROOTS:
        if (repo_root / root).exists():
            bad.append(f"{root}/ exists on filesystem")
        prefix = root + "/"
        if any(path.startswith(prefix) for path in tracked):
            bad.append(f"{root}/ has tracked files")
    if bad:
        return "fail", 1, "forbidden active top-level roots:\n" + "\n".join(sorted(set(bad)))
    return "pass", 0, "no forbidden active top-level src/source/sources roots found"


BUILTINS = {
    "staged_generated_output_check": _builtin_staged_generated_output_check,
    "changed_json_parse": _builtin_changed_json_parse,
    "changed_toml_parse": _builtin_changed_toml_parse,
    "forbidden_active_roots": _builtin_forbidden_active_roots,
}


def _resolve_argv(argv: list[str], repo_root: Path) -> list[str]:
    replacements = {
        "{python}": sys.executable,
        "{repo_root}": str(repo_root),
    }
    return [replacements.get(item, item) for item in argv]


def _missing_executable(argv: list[str], repo_root: Path) -> str | None:
    if not argv:
        return "empty argv"
    executable = argv[0]
    if executable == sys.executable:
        return None
    if os.path.isabs(executable) or "/" in executable or "\\" in executable:
        candidate = Path(executable)
        if not candidate.is_absolute():
            candidate = repo_root / candidate
        return None if candidate.exists() else str(candidate)
    return None if shutil.which(executable) else executable


def _missing_command_path(argv: list[str], repo_root: Path) -> str | None:
    if not argv:
        return "empty argv"
    candidate_index = None
    if argv[0] == sys.executable:
        candidate_index = 1
    elif argv[0].lower() == "python":
        candidate_index = 1
    elif argv[0].lower() == "py" and len(argv) > 2 and argv[1] == "-3":
        candidate_index = 2
    if candidate_index is None or candidate_index >= len(argv):
        return None
    candidate = argv[candidate_index]
    if not (
        candidate.endswith(".py")
        or "/" in candidate
        or "\\" in candidate
    ):
        return None
    path = Path(candidate)
    if not path.is_absolute():
        path = repo_root / path
    return None if path.exists() else str(path)


def _command_status_from_code(code: int, required: bool) -> str:
    if code == 0:
        return "pass"
    return "fail" if required else "warning"


def _run_command(command: dict[str, Any], repo_root: Path, dry_run: bool, timeout_override: int | None) -> dict[str, Any]:
    started = time.monotonic()
    required = bool(command.get("required", False))
    timeout = int(timeout_override or command.get("timeout_seconds") or 300)
    result: dict[str, Any] = {
        "id": command.get("id"),
        "tier": command.get("tier"),
        "name": command.get("name"),
        "owner": command.get("owner"),
        "required": required,
        "type": command.get("type"),
        "timeout_seconds": timeout,
        "failure_policy": command.get("failure_policy"),
        "warning_policy": command.get("warning_policy"),
    }

    if dry_run:
        result.update(
            {
                "status": "skipped_by_policy",
                "returncode": None,
                "elapsed_seconds": 0.0,
                "output_summary": "dry run; command not executed",
            }
        )
        if command.get("type") == "argv":
            result["argv"] = _resolve_argv(list(command.get("argv") or []), repo_root)
        else:
            result["builtin"] = command.get("builtin")
        return result

    if command.get("type") == "builtin":
        builtin_name = str(command.get("builtin", ""))
        func = BUILTINS.get(builtin_name)
        if func is None:
            status = "missing" if required else "warning"
            result.update(
                {
                    "status": status,
                    "returncode": 1,
                    "elapsed_seconds": round(time.monotonic() - started, 3),
                    "builtin": builtin_name,
                    "output_summary": f"unknown builtin {builtin_name}",
                }
            )
            return result
        status, code, output = func(repo_root)
        if status == "fail" and not required:
            status = "warning"
        result.update(
            {
                "status": status,
                "returncode": code,
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "builtin": builtin_name,
                "output_summary": _summary(output),
            }
        )
        return result

    argv = _resolve_argv(list(command.get("argv") or []), repo_root)
    result["argv"] = argv
    missing = _missing_executable(argv, repo_root)
    if missing is None:
        missing = _missing_command_path(argv, repo_root)
    if missing:
        result.update(
            {
                "status": "missing" if required else "warning",
                "returncode": 127,
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "output_summary": f"missing executable or path: {missing}",
            }
        )
        return result

    try:
        completed = subprocess.run(
            argv,
            cwd=str(repo_root),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        output = completed.stdout or ""
        status = _command_status_from_code(completed.returncode, required)
        result.update(
            {
                "status": status,
                "returncode": completed.returncode,
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "output_summary": _summary(output),
            }
        )
        return result
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode(errors="replace")
        result.update(
            {
                "status": "fail" if required else "warning",
                "returncode": None,
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "output_summary": _summary(f"command timed out after {timeout} seconds\n{output}"),
            }
        )
        return result


def _select_commands(contract: dict[str, Any], gate: str | None, tiers: list[str]) -> tuple[str, list[str], list[dict[str, Any]], list[dict[str, Any]]]:
    commands = list(contract.get("commands") or [])
    if tiers:
        selected_tiers = tiers
        mode = "tier"
        selected = [cmd for cmd in commands if str(cmd.get("tier")) in selected_tiers]
    else:
        gate_id = gate or str(contract.get("default_gate", "fast_strict"))
        gates = contract.get("gates") or {}
        if gate_id not in gates:
            raise ValueError(f"unknown gate {gate_id}")
        selected_tiers = list((gates.get(gate_id) or {}).get("tiers") or [])
        mode = gate_id
        selected = [
            cmd
            for cmd in commands
            if str(cmd.get("tier")) in selected_tiers and gate_id in list(cmd.get("gates") or [])
        ]
    selected_ids = {str(cmd.get("id")) for cmd in selected}
    not_run = [
        {
            "id": cmd.get("id"),
            "tier": cmd.get("tier"),
            "name": cmd.get("name"),
            "status": "not_run",
        }
        for cmd in commands
        if str(cmd.get("id")) not in selected_ids
    ]
    return mode, selected_tiers, selected, not_run


def _overall_status(results: list[dict[str, Any]], dry_run: bool) -> str:
    if dry_run:
        return "DRY_RUN"
    hard = [
        item
        for item in results
        if bool(item.get("required")) and str(item.get("status")) in {"fail", "missing"}
    ]
    if hard:
        return "FAIL"
    warnings = [item for item in results if str(item.get("status")) == "warning"]
    if warnings:
        return "WARNING"
    return "PASS"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Fast Strict Test Tier Result",
        "",
        f"- status: `{payload['status']}`",
        f"- mode: `{payload['mode']}`",
        f"- repo root: `{payload['repo_root']}`",
        f"- started: `{payload['started_at_utc']}`",
        f"- completed: `{payload['completed_at_utc']}`",
        f"- elapsed seconds: `{payload['elapsed_seconds']}`",
        f"- selected tiers: `{', '.join(payload['selected_tiers'])}`",
        "",
        "## Commands",
        "",
        "| ID | Tier | Required | Status | Seconds |",
        "| --- | --- | --- | --- | ---: |",
    ]
    for item in payload["commands"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                item.get("id"),
                item.get("tier"),
                str(bool(item.get("required"))).lower(),
                item.get("status"),
                item.get("elapsed_seconds"),
            )
        )
    failures = [
        item
        for item in payload["commands"]
        if str(item.get("status")) in {"fail", "missing", "warning"}
    ]
    if failures:
        lines.extend(["", "## Findings", ""])
        for item in failures:
            lines.append(f"### {item.get('id')}")
            lines.append("")
            lines.append(f"- status: `{item.get('status')}`")
            lines.append(f"- returncode: `{item.get('returncode')}`")
            lines.append("")
            lines.append("```text")
            lines.append(str(item.get("output_summary") or "").strip())
            lines.append("```")
            lines.append("")
    if payload.get("not_run_commands"):
        lines.extend(["", "## Not Run", ""])
        lines.append(f"{len(payload['not_run_commands'])} command(s) were outside the selected mode.")
    return "\n".join(lines).rstrip() + "\n"


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_markdown(payload), encoding="utf-8")


def _print_list(contract: dict[str, Any]) -> None:
    print("Gates:")
    for gate_id, gate in (contract.get("gates") or {}).items():
        print(f"  {gate_id}: {', '.join(gate.get('tiers') or [])} - {gate.get('purpose', '')}")
    print("\nTiers:")
    for tier_id, tier in (contract.get("tiers") or {}).items():
        print(f"  {tier_id}: {tier.get('name')} - {tier.get('purpose')}")
    print("\nCommands:")
    for command in contract.get("commands") or []:
        print(f"  {command.get('id')} [{command.get('tier')}] required={command.get('required')}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--tier", action="append", default=[], choices=["T0", "T1", "T2", "T3", "T4"])
    parser.add_argument("--gate", default=None)
    parser.add_argument("--all", action="store_true", help="Run all tiers through the full gate.")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json-out", default=None)
    parser.add_argument("--md-out", default=None)
    parser.add_argument("--continue-on-fail", action="store_true")
    parser.add_argument("--timeout", "--timeout-seconds", dest="timeout_seconds", type=int, default=None)
    args = parser.parse_args(argv)

    repo_root = _repo_root(args.repo_root)
    contract = _load_contract(repo_root)
    if args.list:
        _print_list(contract)
        return 0

    started_wall = _utc_now()
    started = time.monotonic()
    gate = "full" if args.all else args.gate
    mode, selected_tiers, selected, not_run = _select_commands(contract, gate, list(args.tier or []))

    results: list[dict[str, Any]] = []
    for command in selected:
        result = _run_command(command, repo_root, dry_run=bool(args.dry_run), timeout_override=args.timeout_seconds)
        results.append(result)
        print(
            f"{result['status']}: {result['id']} ({result.get('elapsed_seconds')}s)",
            flush=True,
        )
        if (
            not args.continue_on_fail
            and not args.dry_run
            and bool(result.get("required"))
            and str(result.get("status")) in {"fail", "missing"}
        ):
            break

    payload = {
        "schema_version": "dominium.fast_strict_result.v1",
        "status": _overall_status(results, dry_run=bool(args.dry_run)),
        "mode": mode,
        "repo_root": str(repo_root),
        "started_at_utc": started_wall,
        "completed_at_utc": _utc_now(),
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "selected_tiers": selected_tiers,
        "continue_on_fail": bool(args.continue_on_fail),
        "dry_run": bool(args.dry_run),
        "commands": results,
        "not_run_commands": not_run,
        "known_full_gate_debt_policy": (contract.get("policy") or {}).get("known_debt_policy"),
    }

    json_out = repo_root / (args.json_out or TASK_JSON_REL)
    md_out = repo_root / (args.md_out or TASK_MD_REL)
    _write_json(json_out, payload)
    _write_markdown(md_out, payload)
    print(f"wrote JSON evidence: {json_out}", flush=True)
    print(f"wrote Markdown evidence: {md_out}", flush=True)
    print(
        "summary: status={} commands={} elapsed_seconds={}".format(
            payload["status"],
            len(payload["commands"]),
            payload["elapsed_seconds"],
        ),
        flush=True,
    )

    if payload["status"] in {"PASS", "WARNING", "DRY_RUN"}:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
