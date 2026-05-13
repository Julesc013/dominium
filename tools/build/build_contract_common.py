#!/usr/bin/env python3
"""Shared helpers for Dominium build contract tools."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


STATUS_VALUES = {"available", "planned", "research", "blocked", "unknown"}
PROOF_VALUES = {"none", "probe", "configure", "build", "test", "package"}
FORBIDDEN_ID_WORDS = {
    "legacy",
    "modern",
    "universal",
    "compat",
    "broad_compatibility",
    "early_modern_desktop",
}


def utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def norm(path: str) -> str:
    return path.replace(os.sep, "/")


def relpath(path: str, repo_root: str) -> str:
    try:
        return norm(os.path.relpath(path, repo_root))
    except ValueError:
        return norm(path)


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def write_json(path: str, payload: Mapping[str, Any]) -> None:
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def run_command(args: Sequence[str], cwd: Optional[str] = None, timeout: int = 30) -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            list(args),
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
        return {
            "command": list(args),
            "returncode": int(proc.returncode),
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "ok": proc.returncode == 0,
        }
    except FileNotFoundError:
        return {
            "command": list(args),
            "returncode": 127,
            "stdout": "",
            "stderr": "command not found",
            "ok": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": list(args),
            "returncode": 124,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "command timed out",
            "ok": False,
        }


def _strip_comment(line: str) -> str:
    in_quote = False
    escaped = False
    out: List[str] = []
    for char in line:
        if escaped:
            out.append(char)
            escaped = False
            continue
        if char == "\\" and in_quote:
            out.append(char)
            escaped = True
            continue
        if char == '"':
            in_quote = not in_quote
            out.append(char)
            continue
        if char == "#" and not in_quote:
            break
        out.append(char)
    return "".join(out).strip()


def _split_section(section: str) -> List[str]:
    parts: List[str] = []
    current: List[str] = []
    in_quote = False
    escaped = False
    for char in section:
        if escaped:
            current.append(char)
            escaped = False
            continue
        if char == "\\" and in_quote:
            escaped = True
            continue
        if char == '"':
            in_quote = not in_quote
            continue
        if char == "." and not in_quote:
            parts.append("".join(current))
            current = []
            continue
        current.append(char)
    parts.append("".join(current))
    return [part for part in parts if part]


def _parse_value(raw: str) -> Any:
    value = raw.strip()
    if value == "true":
        return True
    if value == "false":
        return False
    if value.startswith('"') and value.endswith('"'):
        return bytes(value[1:-1], "utf-8").decode("unicode_escape")
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        items: List[Any] = []
        token: List[str] = []
        in_quote = False
        escaped = False
        for char in inner:
            if escaped:
                token.append(char)
                escaped = False
                continue
            if char == "\\" and in_quote:
                token.append(char)
                escaped = True
                continue
            if char == '"':
                in_quote = not in_quote
                token.append(char)
                continue
            if char == "," and not in_quote:
                if "".join(token).strip():
                    items.append(_parse_value("".join(token).strip()))
                token = []
                continue
            token.append(char)
        if "".join(token).strip():
            items.append(_parse_value("".join(token).strip()))
        return items
    return value


def parse_toml(path: str) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    current: Dict[str, Any] = data
    for raw_line in read_text(path).splitlines():
        line = _strip_comment(raw_line)
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            parts = _split_section(line[1:-1].strip())
            current = data
            for part in parts:
                next_value = current.setdefault(part, {})
                if not isinstance(next_value, dict):
                    raise ValueError("section collides with scalar: {}".format(line))
                current = next_value
            continue
        if "=" not in line:
            raise ValueError("unsupported TOML line in {}: {}".format(path, raw_line))
        key, raw_value = line.split("=", 1)
        current[key.strip()] = _parse_value(raw_value)
    return data


def load_build_contracts(repo_root: str) -> Dict[str, Dict[str, Any]]:
    root = os.path.join(repo_root, "contracts", "build")
    files = {
        "floors": os.path.join(root, "floors.toml"),
        "toolchains": os.path.join(root, "toolchains.toml"),
        "tuples": os.path.join(root, "tuples.toml"),
        "artifacts": os.path.join(root, "artifacts.toml"),
    }
    return {name: parse_toml(path) for name, path in files.items()}


def entry_map(contract: Mapping[str, Any], key: str) -> Dict[str, Dict[str, Any]]:
    raw = contract.get(key) or {}
    if not isinstance(raw, dict):
        return {}
    return {str(name): dict(value) for name, value in raw.items() if isinstance(value, dict)}


def tuple_entries(repo_root: str) -> Dict[str, Dict[str, Any]]:
    contracts = load_build_contracts(repo_root)
    return entry_map(contracts["tuples"], "tuples")


def command_line(args: Sequence[str]) -> str:
    return " ".join(args)


def extract_cmake_generators(help_text: str) -> List[str]:
    generators: List[str] = []
    in_generators = False
    for raw in help_text.splitlines():
        if raw.strip() == "Generators":
            in_generators = True
            continue
        if not in_generators:
            continue
        line = raw.rstrip()
        if not line.strip():
            continue
        if "=" not in line:
            continue
        left = line.split("=", 1)[0].strip()
        if left.startswith("*"):
            left = left[1:].strip()
        if left:
            generators.append(left)
    return generators


def cmake_version_from_output(text: str) -> str:
    match = re.search(r"cmake version\s+([^\s]+)", text)
    return match.group(1) if match else ""
