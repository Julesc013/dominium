"""AIDE wrapper command helpers.

This module intentionally uses only the Python standard library. The TOML
reader is limited to the simple contract/registry shape used by AIDE command
contracts so the wrapper runner can work on Python 3.8 without extra packages.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional


REGISTRY_PATH = Path(".aide/tools/command-registry.toml")
MUTATING_TERMS = {
    "apply",
    "archive",
    "build",
    "clean",
    "commit",
    "delete",
    "deploy",
    "generate",
    "move",
    "mv",
    "package",
    "publish",
    "push",
    "release",
    "remove",
    "rename",
    "rm",
    "tag",
    "upload",
    "write",
}
NETWORK_TERMS = {
    "api.github.com",
    "curl",
    "download",
    "fetch",
    "gh",
    "git",
    "github",
    "http://",
    "https://",
    "invoke-webrequest",
    "network",
    "pull",
    "push",
    "upload",
    "wget",
}


class WrapperError(Exception):
    """Raised for contract, registry, or safety-policy errors."""


@dataclass
class CommandSpec:
    name: str
    contract_path: str
    registry_status: str
    registry_notes: str
    metadata: Dict[str, Any]

    @property
    def underlying(self) -> List[str]:
        value = self.metadata.get("underlying", [])
        if not isinstance(value, list) or not all(isinstance(part, str) for part in value):
            raise WrapperError("underlying command must be a list of strings")
        return value

    @property
    def execution_allowed(self) -> bool:
        return bool(self.metadata.get("execution_allowed", False))

    @property
    def apply_allowed(self) -> bool:
        return bool(self.metadata.get("apply_allowed", False))

    @property
    def network_allowed(self) -> bool:
        return bool(self.metadata.get("network_allowed", False))

    @property
    def timeout_seconds(self) -> int:
        value = self.metadata.get("timeout_seconds", 60)
        if not isinstance(value, int):
            raise WrapperError("timeout_seconds must be an integer")
        return value


def resolve_repo_root(repo_root: str) -> Path:
    root = Path(repo_root).resolve()
    if not root.exists() or not root.is_dir():
        raise WrapperError("repo root does not exist")
    if not (root / ".git").exists():
        raise WrapperError("repo root must contain .git")
    if not (root / ".aide").exists():
        raise WrapperError("repo root must contain .aide")
    return root


def _split_section(section: str) -> List[str]:
    parts: List[str] = []
    token: List[str] = []
    in_quote = False
    escape = False
    for char in section:
        if escape:
            token.append(char)
            escape = False
            continue
        if char == "\\" and in_quote:
            escape = True
            continue
        if char == '"':
            in_quote = not in_quote
            continue
        if char == "." and not in_quote:
            parts.append("".join(token))
            token = []
            continue
        token.append(char)
    if in_quote:
        raise WrapperError("unterminated quoted TOML section")
    parts.append("".join(token))
    return parts


def _strip_comment(line: str) -> str:
    in_quote = False
    escape = False
    result: List[str] = []
    for char in line:
        if escape:
            result.append(char)
            escape = False
            continue
        if char == "\\" and in_quote:
            result.append(char)
            escape = True
            continue
        if char == '"':
            in_quote = not in_quote
            result.append(char)
            continue
        if char == "#" and not in_quote:
            break
        result.append(char)
    return "".join(result).strip()


def _parse_string(value: str) -> str:
    if not (value.startswith('"') and value.endswith('"')):
        raise WrapperError("expected TOML string")
    inner = value[1:-1]
    return bytes(inner, "utf-8").decode("unicode_escape")


def _parse_array(value: str) -> List[Any]:
    if value == "[]":
        return []
    if not (value.startswith("[") and value.endswith("]")):
        raise WrapperError("expected TOML array")
    body = value[1:-1].strip()
    if not body:
        return []
    items: List[Any] = []
    token: List[str] = []
    in_quote = False
    escape = False
    for char in body:
        if escape:
            token.append(char)
            escape = False
            continue
        if char == "\\" and in_quote:
            token.append(char)
            escape = True
            continue
        if char == '"':
            in_quote = not in_quote
            token.append(char)
            continue
        if char == "," and not in_quote:
            items.append(_parse_value("".join(token).strip()))
            token = []
            continue
        token.append(char)
    if in_quote:
        raise WrapperError("unterminated TOML array string")
    if token:
        items.append(_parse_value("".join(token).strip()))
    return items


def _parse_value(value: str) -> Any:
    value = value.strip()
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith('"'):
        return _parse_string(value)
    if value.startswith("["):
        return _parse_array(value)
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    raise WrapperError("unsupported TOML value: {0}".format(value))


def load_simple_toml(path: Path) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    current: MutableMapping[str, Any] = data
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = _strip_comment(raw_line)
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            current = data
            for part in _split_section(line[1:-1]):
                next_value = current.setdefault(part, {})
                if not isinstance(next_value, dict):
                    raise WrapperError("{0}:{1}: section collides with value".format(path, line_number))
                current = next_value
            continue
        if "=" not in line:
            raise WrapperError("{0}:{1}: expected key/value".format(path, line_number))
        key, value = [piece.strip() for piece in line.split("=", 1)]
        current[key] = _parse_value(value)
    return data


def load_commands(repo_root: Path) -> Dict[str, CommandSpec]:
    registry_file = repo_root / REGISTRY_PATH
    if not registry_file.exists():
        raise WrapperError("missing command registry: {0}".format(REGISTRY_PATH))
    registry = load_simple_toml(registry_file)
    registry_commands = registry.get("commands", {})
    if not isinstance(registry_commands, dict):
        raise WrapperError("registry commands must be a table")

    commands: Dict[str, CommandSpec] = {}
    contracts: Dict[str, Mapping[str, Any]] = {}
    for name in sorted(registry_commands):
        entry = registry_commands[name]
        if not isinstance(entry, dict):
            raise WrapperError("registry entry must be a table: {0}".format(name))
        contract_path = str(entry.get("contract", ""))
        if not contract_path:
            raise WrapperError("registry entry missing contract: {0}".format(name))
        if contract_path not in contracts:
            contract_file = repo_root / contract_path
            if not contract_file.exists():
                raise WrapperError("missing contract for {0}: {1}".format(name, contract_path))
            contracts[contract_path] = load_simple_toml(contract_file)
        contract_commands = contracts[contract_path].get("commands", {})
        if not isinstance(contract_commands, dict) or name not in contract_commands:
            raise WrapperError("contract does not define command: {0}".format(name))
        metadata = contract_commands[name]
        if not isinstance(metadata, dict):
            raise WrapperError("contract command must be a table: {0}".format(name))
        commands[name] = CommandSpec(
            name=name,
            contract_path=contract_path,
            registry_status=str(entry.get("status", "planned")),
            registry_notes=str(entry.get("notes", "")),
            metadata=dict(metadata),
        )
    return commands


def command_to_dict(spec: CommandSpec) -> Dict[str, Any]:
    result = dict(spec.metadata)
    result.update(
        {
            "name": spec.name,
            "contract": spec.contract_path,
            "registry_status": spec.registry_status,
            "registry_notes": spec.registry_notes,
        }
    )
    return result


def _contains_term(parts: Iterable[str], terms: Iterable[str]) -> Optional[str]:
    for part in parts:
        lower = part.lower()
        for term in terms:
            if lower == term or term in lower:
                return term
    return None


def check_safety(spec: CommandSpec) -> None:
    underlying = spec.underlying
    if not underlying:
        raise WrapperError("underlying command is empty: {0}".format(spec.name))
    if not spec.apply_allowed:
        mutating = _contains_term(underlying, MUTATING_TERMS)
        if mutating:
            raise WrapperError(
                "refusing {0}: apply_allowed=false and command appears mutating ({1})".format(
                    spec.name, mutating
                )
            )
    if not spec.network_allowed:
        network = _contains_term(underlying, NETWORK_TERMS)
        if network:
            raise WrapperError(
                "refusing {0}: network_allowed=false and command appears network-related ({1})".format(
                    spec.name, network
                )
            )


def summarize_text(text: str, max_chars: int = 3000) -> str:
    if len(text) <= max_chars:
        return text
    head = text[: max_chars // 2].rstrip()
    tail = text[-max_chars // 2 :].lstrip()
    return head + "\n...[truncated]...\n" + tail


def run_command(repo_root: Path, spec: CommandSpec, dry_run: bool = False) -> Dict[str, Any]:
    underlying = spec.underlying
    if dry_run:
        return {
            "command": spec.name,
            "dry_run": True,
            "underlying": underlying,
            "returncode": 0,
            "stdout": " ".join(underlying),
            "stderr": "",
        }
    if not spec.execution_allowed:
        raise WrapperError("execution is not allowed for command: {0}".format(spec.name))
    check_safety(spec)
    try:
        completed = subprocess.run(
            underlying,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=spec.timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "command": spec.name,
            "dry_run": False,
            "underlying": underlying,
            "returncode": 124,
            "stdout": summarize_text(exc.stdout or ""),
            "stderr": summarize_text((exc.stderr or "") + "\nwrapper timeout expired"),
            "timeout": True,
        }
    return {
        "command": spec.name,
        "dry_run": False,
        "underlying": underlying,
        "returncode": completed.returncode,
        "stdout": summarize_text(completed.stdout),
        "stderr": summarize_text(completed.stderr),
        "timeout": False,
    }


def dumps_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True)
