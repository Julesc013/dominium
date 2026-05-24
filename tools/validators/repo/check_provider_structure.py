#!/usr/bin/env python3
"""Validate service-first provider structure and third-party fencing."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set

try:
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover
    tomllib = None


PROVIDER_REGISTRY = Path("contracts/provider/provider.registry.json")
PLANNED_PROVIDER_REGISTRY = Path("contracts/provider/provider_plans.registry.json")
PROVIDER_STRUCTURE_CONTRACT = Path("contracts/provider/provider_structure.contract.toml")
THIRD_PARTY_MANIFEST = Path("external/manifests/third_party.toml")
RELEASE_PROFILE_ROOT = Path("release/profiles")

FORBIDDEN_TOP_LEVEL_ROOTS = {"framework", "profiles", "labs", "modules", "plugins", "services", "sdk"}
SERVICE_ROOTS = {
    "platform",
    "input",
    "render",
    "audio",
    "asset",
    "script",
    "ui",
    "storage",
    "diagnostics",
    "command",
    "view",
    "projection",
    "package",
    "network",
    "shell",
}
PENDING_STRUCTURE_STATUSES = {
    "service_surface_pending_provider_split",
    "planned_workbench_surface",
    "planned_provider_no_code",
}
PROVIDER_ID_RE = re.compile(r"^(domino|dominium)\.provider(?:\.[a-z0-9][a-z0-9_]*)+\.v[0-9]+$")
PROVIDER_FOLDER_RE = re.compile(r"^[a-z0-9][a-z0-9_]*[a-z0-9]$|^[a-z0-9]$")
VENDOR_SHAPED_PATTERNS = (
    re.compile(r"^runtime/(raylib|sdl|sdl2|sdl3|lua|lua54|lua55)(/|$)"),
    re.compile(r"^contracts/(raylib|sdl|sdl2|sdl3|lua|lua54|lua55)(/|$)"),
    re.compile(r"^contracts/render/(raylib|rlgl|rlsw)(/|$)"),
    re.compile(r"^contracts/services(/|$)"),
    re.compile(r"^apps/[^/]+/(raylib|sdl2|lua|rendered/raylib)(/|$)"),
)
FORBIDDEN_INCLUDE_ROOTS = (
    "engine/",
    "game/",
    "contracts/",
    "content/",
    "runtime/include/",
    "tests/replay/",
    "tests/compat/",
)
CODE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".ipp", ".m", ".mm"}
THIRD_PARTY_INCLUDE_RE = re.compile(
    r"^\s*#\s*include\s*[<\"](?:raylib|raymath|rlgl|raygui|raudio|SDL|SDL2/SDL|lua|lauxlib|lualib)\.h[>\"]",
    re.MULTILINE,
)


def finding(level: str, code: str, message: str, path: Optional[str] = None) -> Dict[str, Any]:
    item: Dict[str, Any] = {"level": level, "code": code, "message": message}
    if path:
        item["path"] = path
    return item


def posix(path: Path | str) -> str:
    return str(path).replace("\\", "/")


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
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def tracked_dirs(paths: Iterable[str]) -> Set[str]:
    dirs: Set[str] = set()
    for path in paths:
        parts = path.split("/")[:-1]
        for index in range(1, len(parts) + 1):
            dirs.add("/".join(parts[:index]))
    return dirs


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def minimal_toml_load(text: str) -> Dict[str, Any]:
    root: Dict[str, Any] = {}
    current: Dict[str, Any] = root
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            current = root
            for part in line[1:-1].split("."):
                current = current.setdefault(part.strip(), {})
            continue
        if "=" not in line:
            raise ValueError(f"invalid TOML line: {raw_line}")
        key, value = line.split("=", 1)
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            current[key.strip()] = value[1:-1]
        elif value in {"true", "false"}:
            current[key.strip()] = value == "true"
        else:
            current[key.strip()] = value
    return root


def load_toml(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    if tomllib is not None:
        return tomllib.loads(text)
    return minimal_toml_load(text)


def check_required_policy_files(repo_root: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for rel in (PROVIDER_STRUCTURE_CONTRACT, THIRD_PARTY_MANIFEST):
        path = repo_root / rel
        if not path.exists():
            findings.append(finding("error", "missing_policy_file", f"missing provider structure policy file: {rel.as_posix()}"))
            continue
        try:
            load_toml(path)
        except Exception as exc:
            findings.append(finding("error", "invalid_toml", f"{rel.as_posix()} does not parse as TOML: {exc}", rel.as_posix()))
    return findings


def check_paths(paths: List[str]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    dirs = tracked_dirs(paths)
    paths_and_dirs = set(paths) | dirs
    for path in paths:
        root = path.split("/", 1)[0]
        if root in FORBIDDEN_TOP_LEVEL_ROOTS:
            findings.append(finding("error", "forbidden_top_level_root", "provider/profile/module roots must stay under canonical owners", root))
        for pattern in VENDOR_SHAPED_PATTERNS:
            if pattern.search(path):
                findings.append(finding("error", "vendor_shaped_path", "vendor or provider family appears as an owning architecture root", path))
                break

    for direct in ("runtime/render/null", "runtime/render/software"):
        if direct in paths_and_dirs:
            findings.append(finding("error", "provider_direct_runtime_leaf", "render providers must live under runtime/render/providers/<provider>", direct))

    for directory in sorted(dirs):
        parts = directory.split("/")
        if len(parts) >= 4 and parts[0] == "runtime" and parts[2] == "providers":
            service = parts[1]
            provider = parts[3]
            if service not in SERVICE_ROOTS:
                findings.append(finding("error", "unknown_provider_service_root", f"unknown provider service root: {service}", directory))
            if not PROVIDER_FOLDER_RE.match(provider):
                findings.append(finding("error", "bad_provider_folder_name", f"provider folder is not an exact lowercase API token: {provider}", directory))
    return findings


def provider_ids(repo_root: Path) -> Set[str]:
    data = load_json(repo_root / PROVIDER_REGISTRY)
    return {
        str(item.get("provider_id"))
        for item in data.get("providers", [])
        if isinstance(item, dict) and item.get("provider_id")
    }


def planned_provider_ids(repo_root: Path) -> Set[str]:
    path = repo_root / PLANNED_PROVIDER_REGISTRY
    if not path.exists():
        return set()
    data = load_json(path)
    return {
        str(item.get("provider_id"))
        for item in data.get("providers", [])
        if isinstance(item, dict) and item.get("provider_id")
    }


def validate_planned_provider_registry(repo_root: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    path = repo_root / PLANNED_PROVIDER_REGISTRY
    if not path.exists():
        findings.append(finding("warning", "planned_provider_registry_absent", "planned provider registry is absent", PLANNED_PROVIDER_REGISTRY.as_posix()))
        return findings
    try:
        data = load_json(path)
    except Exception as exc:
        return [finding("error", "planned_provider_registry_unreadable", f"planned provider registry cannot be read: {exc}", PLANNED_PROVIDER_REGISTRY.as_posix())]
    if data.get("support_claim") is not False:
        findings.append(finding("error", "planned_registry_support_claim", "planned provider registry must explicitly declare support_claim=false", PLANNED_PROVIDER_REGISTRY.as_posix()))
    seen: Set[str] = set()
    for index, provider in enumerate(data.get("providers", [])):
        record_path = f"{PLANNED_PROVIDER_REGISTRY.as_posix()}#{index}"
        if not isinstance(provider, dict):
            findings.append(finding("error", "planned_provider_not_object", "planned provider entry must be an object", record_path))
            continue
        provider_id = str(provider.get("provider_id") or "")
        implementation_path = str(provider.get("implementation_path") or "").replace("\\", "/")
        service_root = str(provider.get("service_root") or "").replace("\\", "/")
        if provider_id in seen:
            findings.append(finding("error", "duplicate_planned_provider", f"duplicate planned provider_id: {provider_id}", record_path))
        seen.add(provider_id)
        if not PROVIDER_ID_RE.match(provider_id):
            findings.append(finding("error", "planned_provider_id_not_versioned", "planned provider_id must be versioned", record_path))
        if provider.get("planned") is not True or provider.get("support_claim") is not False:
            findings.append(finding("error", "planned_provider_support_claim", "planned provider entries must declare planned=true and support_claim=false", record_path))
        parts = implementation_path.split("/")
        canonical = len(parts) >= 4 and parts[0] == "runtime" and parts[2] == "providers"
        if not canonical:
            findings.append(finding("error", "planned_provider_path_not_canonical", "planned provider path must use runtime/<service>/providers/<provider>", record_path))
            continue
        if parts[1] not in SERVICE_ROOTS:
            findings.append(finding("error", "unknown_planned_provider_service", f"unknown planned provider service root: {parts[1]}", record_path))
        if service_root and service_root != f"runtime/{parts[1]}":
            findings.append(finding("error", "planned_provider_service_root_mismatch", "planned provider service_root does not match implementation_path", record_path))
        provider_api = str(provider.get("provider_api") or "")
        if provider_api and provider_api != parts[3]:
            findings.append(finding("error", "planned_provider_api_path_mismatch", "planned provider_api must match implementation folder", record_path))
    return findings


def validate_provider_registry(repo_root: Path) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    try:
        data = load_json(repo_root / PROVIDER_REGISTRY)
    except Exception as exc:
        return [finding("error", "provider_registry_unreadable", f"provider registry cannot be read: {exc}", PROVIDER_REGISTRY.as_posix())]

    for index, provider in enumerate(data.get("providers", [])):
        if not isinstance(provider, dict):
            findings.append(finding("error", "provider_record_not_object", "provider registry entry must be an object", f"{PROVIDER_REGISTRY.as_posix()}#{index}"))
            continue
        provider_id = str(provider.get("provider_id") or "")
        path = str(provider.get("implementation_path") or "").replace("\\", "/")
        record_path = f"{PROVIDER_REGISTRY.as_posix()}#{provider_id or index}"
        if not PROVIDER_ID_RE.match(provider_id):
            findings.append(finding("error", "provider_id_not_versioned", "provider_id must be a versioned semantic provider id", record_path))
        if provider.get("implementation_path_is_identity") is True:
            findings.append(finding("error", "implementation_path_as_identity", "implementation_path must not define provider identity", record_path))
        if path.startswith("runtime/"):
            parts = path.split("/")
            canonical = len(parts) >= 4 and parts[0] == "runtime" and parts[2] == "providers"
            status = str(provider.get("provider_structure_status") or "")
            if canonical:
                service = parts[1]
                provider_folder = parts[3]
                if service not in SERVICE_ROOTS:
                    findings.append(finding("error", "unknown_provider_service_root", f"unknown provider service root: {service}", record_path))
                service_root = str(provider.get("service_root") or "")
                if service_root and service_root != f"runtime/{service}":
                    findings.append(finding("error", "provider_service_root_mismatch", "service_root does not match implementation_path", record_path))
                provider_api = str(provider.get("provider_api") or provider.get("provider_family") or "")
                if provider_api and provider_api != provider_folder:
                    findings.append(finding("warning", "provider_api_path_mismatch", "provider_api does not match provider implementation folder", record_path))
            elif status in PENDING_STRUCTURE_STATUSES:
                findings.append(finding("warning", "provider_split_pending", "provider descriptor uses a service path pending a later provider split", record_path))
            else:
                findings.append(finding("error", "runtime_provider_path_not_canonical", "runtime provider implementation_path must use runtime/<service>/providers/<provider>", record_path))
        if path and not (repo_root / path).exists() and not provider.get("planned"):
            findings.append(finding("warning", "provider_path_missing", "provider implementation_path does not exist in this checkout", record_path))
    return findings


def validate_release_profiles(repo_root: Path, known_providers: Set[str], planned_providers: Set[str]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    root = repo_root / RELEASE_PROFILE_ROOT
    if not root.exists():
        findings.append(finding("warning", "release_profiles_absent", "release/profiles is absent; provider choices must not move to top-level profiles", RELEASE_PROFILE_ROOT.as_posix()))
        return findings
    for path in sorted(root.rglob("*.toml")):
        rel = path.relative_to(repo_root).as_posix()
        try:
            data = load_toml(path)
        except Exception as exc:
            findings.append(finding("error", "invalid_release_profile_toml", f"release profile does not parse as TOML: {exc}", rel))
            continue
        profile = data.get("profile", {})
        if not isinstance(profile, dict) or not str(profile.get("id") or "").startswith("dominium.profile."):
            findings.append(finding("error", "release_profile_bad_id", "release provider profile must declare dominium.profile.* id", rel))
        support_claim = bool(profile.get("support_claim")) if isinstance(profile, dict) else False
        providers = data.get("providers", {})
        if not isinstance(providers, dict) or not providers:
            findings.append(finding("error", "release_profile_missing_providers", "release provider profile must declare [providers]", rel))
            continue
        for service, provider_ref in providers.items():
            if str(service) not in SERVICE_ROOTS:
                findings.append(finding("warning", "release_profile_unknown_service", f"profile provider service is not in the known service root set: {service}", rel))
            provider_ref = str(provider_ref)
            if provider_ref in planned_providers and support_claim:
                findings.append(finding("error", "release_profile_planned_provider_support_claim", f"profile claims support while referencing planned provider: {provider_ref}", rel))
            if provider_ref not in known_providers and provider_ref not in planned_providers:
                findings.append(finding("error", "release_profile_unknown_provider", f"profile references unknown provider: {provider_ref}", rel))
    return findings


def validate_include_leakage(repo_root: Path, paths: List[str]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for path in paths:
        if not path.startswith(FORBIDDEN_INCLUDE_ROOTS):
            continue
        rel = Path(path)
        if rel.suffix.lower() not in CODE_SUFFIXES:
            continue
        full = repo_root / rel
        try:
            text = full.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if THIRD_PARTY_INCLUDE_RE.search(text):
            findings.append(finding("error", "third_party_include_leak", "third-party provider header included outside provider/external boundary", path))
    return findings


def build_report(repo_root: Path) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    paths = git_ls_files(repo_root)
    known_providers = provider_ids(repo_root)
    planned_providers = planned_provider_ids(repo_root)
    findings.extend(check_required_policy_files(repo_root))
    findings.extend(check_paths(paths))
    findings.extend(validate_provider_registry(repo_root))
    findings.extend(validate_planned_provider_registry(repo_root))
    findings.extend(validate_release_profiles(repo_root, known_providers, planned_providers))
    findings.extend(validate_include_leakage(repo_root, paths))
    errors = [item for item in findings if item["level"] == "error"]
    warnings = [item for item in findings if item["level"] == "warning"]
    return {
        "validator": "check_provider_structure",
        "status": "BLOCKED" if errors else "PASS_WITH_WARNINGS" if warnings else "PASS",
        "summary": {"errors": len(errors), "warnings": len(warnings), "findings": len(findings)},
        "findings": findings,
    }


def print_text(report: Dict[str, Any]) -> None:
    print(f"provider structure: {report['status']}")
    print(f"errors: {report['summary']['errors']}")
    print(f"warnings: {report['summary']['warnings']}")
    for item in report["findings"]:
        path = f"{item['path']}: " if item.get("path") else ""
        print(f"{item['level']}: {path}{item['code']}: {item['message']}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--strict", action="store_true", help="Fail on blocker/error findings")
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
