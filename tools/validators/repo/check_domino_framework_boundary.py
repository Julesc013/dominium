#!/usr/bin/env python3
"""Validate the Domino framework boundary without adding a framework root."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set

try:
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover
    tomllib = None


PUBLIC_SURFACE_CONTRACT = Path("contracts/public_surface/public_surface.contract.toml")

FORBIDDEN_TOP_LEVEL_ROOTS = {
    "framework",
    "profiles",
    "labs",
    "modules",
    "plugins",
    "services",
    "sdk",
}

REQUIRED_TRACKED_DIRS = {
    "contracts/public_surface": "framework public-surface registry",
    "contracts/abi": "framework ABI law",
    "contracts/service": "framework service law",
    "contracts/provider": "framework provider law",
    "contracts/capability": "framework capability law",
    "engine/include/domino": "Domino deterministic engine public header home",
    "runtime/include/domino": "Domino runtime public header home",
    "release/profiles": "build/release provider profile recipes",
    "content/profiles": "authored runtime/user/game profile payloads",
}

REQUIRED_PUBLIC_SURFACES = {
    "domino.engine.public_headers.v1": "engine/include/domino",
    "domino.runtime.public_headers.v1": "runtime/include/domino",
    "dominium.game.public_headers.v1": "game/include/dominium",
}

FORBIDDEN_PREFIXES = {
    "apps/client/rendered/raylib": "provider choice belongs in release/content profiles, not client product identity",
    "apps/client/raylib": "provider choice belongs in release/content profiles, not client product identity",
    "apps/client/sdl2": "provider choice belongs in release/content profiles, not client product identity",
    "apps/client/sdl2_opengl33": "provider choice belongs in release/content profiles, not client product identity",
    "apps/workbench/raylib": "Workbench must not hardwire provider identity",
    "apps/workbench/sdl2": "Workbench must not hardwire provider identity",
    "content/modules": "module payloads belong under content/packs or app/runtime owners",
    "content/builtin": "built-in payloads need pack/profile authority, not a broad content bucket",
    "contracts/raylib": "third-party libraries must not own contract roots",
    "contracts/sdl2": "third-party libraries must not own contract roots",
    "contracts/render/raylib": "render law must stay service-first",
    "contracts/render/rlgl": "render law must stay service-first",
    "contracts/render/rlsw": "render law must stay service-first",
    "contracts/services": "service law root is contracts/service",
    "runtime/raylib": "providers must live under runtime/<service>/providers/<provider>",
    "runtime/sdl2": "providers must live under runtime/<service>/providers/<provider>",
    "runtime/lua": "providers must live under runtime/<service>/providers/<provider>",
    "runtime/opengl33": "providers must live under runtime/<service>/providers/<provider>",
    "runtime/direct3d11": "providers must live under runtime/<service>/providers/<provider>",
}


def posix(path: Path | str) -> str:
    return str(path).replace("\\", "/").strip("/")


def finding(level: str, code: str, message: str, path: Optional[str] = None) -> Dict[str, Any]:
    item: Dict[str, Any] = {"level": level, "code": code, "message": message}
    if path:
        item["path"] = path
    return item


def git_ls_files(repo_root: Path) -> List[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=str(repo_root),
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")
    return [posix(line) for line in result.stdout.splitlines() if line.strip()]


def tracked_dirs(paths: Iterable[str]) -> Set[str]:
    dirs: Set[str] = set()
    for path in paths:
        parts = path.split("/")[:-1]
        for index in range(1, len(parts) + 1):
            dirs.add("/".join(parts[:index]))
    return dirs


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


def _parse_value(raw: str) -> Any:
    raw = raw.strip()
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1].replace('\\"', '"')
    if raw == "true":
        return True
    if raw == "false":
        return False
    return raw


def _minimal_surface_toml(text: str) -> Dict[str, Any]:
    root: Dict[str, Any] = {}
    current: Dict[str, Any] = root
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = _strip_comment(raw)
        if not line:
            continue
        if line == "[[surface]]":
            current = {}
            root.setdefault("surface", []).append(current)
            continue
        if line.startswith("[") and line.endswith("]"):
            current = root
            for part in line[1:-1].split("."):
                current = current.setdefault(part.strip(), {})
            continue
        if "=" not in line:
            raise ValueError(f"invalid TOML line {line_no}: {raw}")
        key, value = line.split("=", 1)
        current[key.strip()] = _parse_value(value)
    return root


def load_public_surfaces(repo_root: Path) -> Dict[str, str]:
    path = repo_root / PUBLIC_SURFACE_CONTRACT
    text = path.read_text(encoding="utf-8")
    if tomllib is not None:
        data = tomllib.loads(text)
    else:
        data = _minimal_surface_toml(text)
    surfaces: Dict[str, str] = {}
    for surface in data.get("surface", []):
        if isinstance(surface, dict) and surface.get("id") and surface.get("path"):
            surfaces[str(surface["id"])] = posix(str(surface["path"]))
    return surfaces


def prefix_match(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(prefix + "/")


def check_paths(paths: List[str]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    dirs = tracked_dirs(paths)
    tracked = set(paths) | dirs

    for path in paths:
        root = path.split("/", 1)[0]
        if root in FORBIDDEN_TOP_LEVEL_ROOTS:
            findings.append(
                finding(
                    "error",
                    "forbidden_top_level_root",
                    "Domino Framework is contracts plus public headers, not a new active source root",
                    root,
                )
            )
        for prefix, reason in FORBIDDEN_PREFIXES.items():
            if prefix_match(path, prefix):
                code = "provider_variant_product_path" if prefix.startswith("apps/") else "forbidden_framework_boundary_path"
                findings.append(finding("error", code, reason, path))
                break

    for required, purpose in sorted(REQUIRED_TRACKED_DIRS.items()):
        if required not in tracked:
            findings.append(
                finding(
                    "error",
                    "missing_framework_surface_dir",
                    f"missing required {purpose}: {required}",
                    required,
                )
            )
    return findings


def check_public_surface_contract(repo_root: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    path = repo_root / PUBLIC_SURFACE_CONTRACT
    if not path.exists():
        return [
            finding(
                "error",
                "missing_public_surface_contract",
                "Domino Framework public API homes must be registered in contracts/public_surface",
                PUBLIC_SURFACE_CONTRACT.as_posix(),
            )
        ]
    try:
        surfaces = load_public_surfaces(repo_root)
    except Exception as exc:
        return [
            finding(
                "error",
                "public_surface_contract_unreadable",
                f"public surface contract cannot be read: {exc}",
                PUBLIC_SURFACE_CONTRACT.as_posix(),
            )
        ]

    for surface_id, expected_path in sorted(REQUIRED_PUBLIC_SURFACES.items()):
        actual = surfaces.get(surface_id)
        if actual is None:
            findings.append(
                finding(
                    "error",
                    "missing_public_surface",
                    f"missing registered public surface {surface_id}",
                    PUBLIC_SURFACE_CONTRACT.as_posix(),
                )
            )
        elif actual != expected_path:
            findings.append(
                finding(
                    "error",
                    "public_surface_path_not_canonical",
                    f"{surface_id} must point at {expected_path}, not {actual}",
                    PUBLIC_SURFACE_CONTRACT.as_posix(),
                )
            )
    return findings


def build_report(repo_root: Path) -> Dict[str, Any]:
    paths = git_ls_files(repo_root)
    findings: List[Dict[str, Any]] = []
    findings.extend(check_paths(paths))
    findings.extend(check_public_surface_contract(repo_root))
    errors = [item for item in findings if item["level"] == "error"]
    warnings = [item for item in findings if item["level"] == "warning"]
    return {
        "validator": "check_domino_framework_boundary",
        "status": "BLOCKED" if errors else "PASS_WITH_WARNINGS" if warnings else "PASS",
        "summary": {"errors": len(errors), "warnings": len(warnings), "findings": len(findings)},
        "findings": findings,
    }


def print_text(report: Dict[str, Any]) -> None:
    print(f"Domino framework boundary: {report['status']}")
    print(f"errors: {report['summary']['errors']}")
    print(f"warnings: {report['summary']['warnings']}")
    for item in report["findings"]:
        path = f"{item['path']}: " if item.get("path") else ""
        print(f"{item['level']}: {path}{item['code']}: {item['message']}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--strict", action="store_true", help="Fail on error findings.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    report = build_report(repo_root)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text(report)
    return 1 if args.strict and report["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    sys.exit(main())
