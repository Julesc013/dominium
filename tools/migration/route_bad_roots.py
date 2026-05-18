#!/usr/bin/env python3
"""Deterministic dry-run router for former bad roots.

MOVE-ROUTER-00 is no-apply. The router reads the repo-local routing
contract, scans tracked files with git ls-files, and emits reviewable move
plans. Unknown or ambiguous files route to archive/quarantine/<root>/ instead
of staying in bad roots or being guessed into active owners.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


DRY_RUN_SCHEMA = "dominium.move_router_00.dry_run.v1"
ROUTE_TABLE_SCHEMA = "dominium.move_router_00.route_table.v1"

DEFAULT_CONTRACT = os.path.join("contracts", "repo", "bad_root_routing.contract.toml")
DEFAULT_JSON_OUT = os.path.join(".aide", "reports", "MOVE-ROUTER-00-dry-run.json")
DEFAULT_MD_OUT = os.path.join(".aide", "reports", "MOVE-ROUTER-00-dry-run.md")
DEFAULT_ROUTE_TABLE_OUT = os.path.join(".aide", "reports", "MOVE-ROUTER-00-route-table.json")
DEFAULT_SKIPPED_OUT = os.path.join(".aide", "reports", "MOVE-ROUTER-00-skipped-or-quarantined.md")
DEFAULT_COLLISIONS_OUT = os.path.join(".aide", "reports", "MOVE-ROUTER-00-target-collisions.md")

DOC_EXTS = {".md", ".txt", ".rst", ".adoc"}
DATA_EXTS = {".json", ".jsonl", ".toml", ".yaml", ".yml", ".csv", ".tsv", ".lock", ".tlv", ".dwrl"}
CODE_EXTS = {".py", ".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inl", ".inc", ".ipp"}
ASSET_EXTS = {
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".ico",
    ".wav", ".ogg", ".mp3", ".flac",
    ".obj", ".fbx", ".gltf", ".glb", ".mtl",
    ".asc", ".bsp", ".tls",
}

FORBIDDEN_DIR_REPLACEMENTS = {
    "src": "source_payload",
    "source": "source_payload",
    "sources": "source_payloads",
    "code": "code_payload",
    "impl": "implementation_payload",
    "common": "common_payload",
    "shared": "shared_payload",
    "misc": "misc_payload",
    "new": "new_payload",
    "old": "old_payload",
    "future": "future_payload",
    "modern": "modern_payload",
    "legacy": "legacy_payload",
    "classic": "classic_payload",
    "universal": "universal_payload",
    "experimental": "experimental_payload",
    "research": "research_payload",
    "v2": "version_2_payload",
    "v3": "version_3_payload",
    "compat": "compatibility_payload",
}

IDENTITY_TOKENS = {
    "id", "identity", "fingerprint", "hash", "manifest", "registry", "lock",
    "pack", "profile", "bundle", "capability", "trust", "compat", "compatibility",
    "release", "version", "product", "contract", "schema", "protocol", "policy",
}
AUTHORITY_TOKENS = {
    "policy", "contract", "schema", "registry", "ruleset", "security", "safety",
    "trust", "capability", "compatibility", "governance", "law", "canon",
    "authority", "protocol", "spec",
}
EXAMPLE_TOKENS = {"example", "examples", "sample", "samples", "demo", "demos"}
FIXTURE_TOKENS = {"fixture", "fixtures", "golden", "baseline", "baselines", "test", "tests", "vector", "vectors"}
GENERATED_TOKENS = {"audit", "analysis", "generated", "evidence", "metrics", "reports", "runs", "cache", "output"}


def normalize(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def path_parts(path: str) -> List[str]:
    return [part for part in normalize(path).split("/") if part]


def split_root(path: str) -> Tuple[str, str]:
    parts = normalize(path).split("/", 1)
    return (parts[0], parts[1] if len(parts) > 1 else "")


def ext_of(path: str) -> str:
    parts = path_parts(path)
    return os.path.splitext(parts[-1] if parts else path)[1].lower()


def name_lower(path: str) -> str:
    parts = path_parts(path)
    return parts[-1].lower() if parts else ""


def lower_parts(path: str) -> List[str]:
    return [part.lower() for part in path_parts(path)]


def token_text(path: str) -> str:
    return normalize(path).lower().replace("-", "_").replace(".", "_")


def has_any(path: str, tokens: Iterable[str]) -> bool:
    text = token_text(path)
    parts = lower_parts(path)
    for token in tokens:
        low = token.lower()
        if low in parts or low in text:
            return True
    return False


def first_part(rest: str) -> str:
    parts = lower_parts(rest)
    return parts[0] if parts else ""


def drop_first(rest: str, count: int = 1) -> str:
    return "/".join(path_parts(rest)[count:])


def join_target(prefix: str, rest: str = "") -> str:
    prefix = normalize(prefix)
    rest = normalize(rest)
    return prefix if not rest else prefix + "/" + rest


def replace_first(rest: str, prefix: str) -> str:
    return join_target(prefix, drop_first(rest))


def run_git(repo_root: str, args: Sequence[str], binary: bool = False) -> Any:
    result = subprocess.run(["git", "-C", repo_root] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        sys.stderr.write(result.stderr.decode("utf-8", errors="replace"))
        raise SystemExit(result.returncode)
    return result.stdout if binary else result.stdout.decode("utf-8", errors="replace")


def git_ls_files(repo_root: str) -> List[str]:
    raw = run_git(repo_root, ["ls-files", "-z"], binary=True)
    return sorted(normalize(part.decode("utf-8", errors="surrogateescape")) for part in raw.split(b"\0") if part)


def git_head(repo_root: str) -> str:
    return run_git(repo_root, ["rev-parse", "HEAD"]).strip()


def parse_toml_arrays(path: str) -> Dict[str, Any]:
    """Parse the small TOML surface this tool needs using stdlib only."""
    values: Dict[str, Any] = {}
    current_key: Optional[str] = None
    current_items: List[str] = []
    with open(path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.split("#", 1)[0].strip()
            if not line:
                continue
            if current_key:
                if "]" in line:
                    before = line.split("]", 1)[0]
                    current_items.extend(_quoted_values(before))
                    values[current_key] = current_items
                    current_key = None
                    current_items = []
                else:
                    current_items.extend(_quoted_values(line))
                continue
            if "=" not in line:
                continue
            key, value = [part.strip() for part in line.split("=", 1)]
            key = key.strip('"')
            if value.startswith("[") and "]" not in value:
                current_key = key
                current_items = _quoted_values(value)
            elif value.startswith("["):
                values[key] = _quoted_values(value)
            elif value.startswith('"') and value.endswith('"'):
                values[key] = value.strip('"')
            elif value.lower() in {"true", "false"}:
                values[key] = value.lower() == "true"
    return values


def _quoted_values(text: str) -> List[str]:
    values: List[str] = []
    in_quote = False
    buf: List[str] = []
    for char in text:
        if char == '"':
            if in_quote:
                values.append("".join(buf))
                buf = []
                in_quote = False
            else:
                in_quote = True
            continue
        if in_quote:
            buf.append(char)
    return values


def load_contract(repo_root: str, rel_or_abs: str) -> Dict[str, Any]:
    path = rel_or_abs if os.path.isabs(rel_or_abs) else os.path.join(repo_root, rel_or_abs)
    if not os.path.exists(path):
        raise SystemExit("Routing contract not found: {0}".format(path))
    data = parse_toml_arrays(path)
    return {
        "schema_version": data.get("schema_version", "dominium.repo.bad_root_routing.contract.v1"),
        "bad_roots": data.get("bad_roots", []),
        "canonical_roots": data.get("canonical_roots", []),
        "forbidden_directory_names": data.get("forbidden_directory_names", []),
        "allowed_directory_exceptions": data.get("allowed_directory_exceptions", []),
    }


def is_schema(path: str) -> bool:
    return ".schema." in name_lower(path) or has_any(path, {"schema", "schemas"})


def is_registry(path: str) -> bool:
    return has_any(path, {"registry", "registries", "ruleset", "rulesets"})


def is_manifest(path: str) -> bool:
    return has_any(path, {"manifest", "manifests"})


def is_policy(path: str) -> bool:
    return has_any(path, {"policy", "policies"})


def is_contractlike(path: str) -> bool:
    return has_any(path, {"contract", "contracts", "matrix", "capability", "capabilities"}) or is_manifest(path) or is_policy(path)


def is_markdown(path: str) -> bool:
    return ext_of(path) in DOC_EXTS


def is_python(path: str) -> bool:
    return ext_of(path) == ".py"


def is_data(path: str) -> bool:
    return ext_of(path) in DATA_EXTS or is_schema(path) or is_registry(path) or is_manifest(path)


def is_code(path: str) -> bool:
    return ext_of(path) in CODE_EXTS or name_lower(path) == "cmakelists.txt" or ext_of(path) == ".cmake"


def is_asset(path: str) -> bool:
    return ext_of(path) in ASSET_EXTS


def is_identity_sensitive(path: str) -> bool:
    return has_any(path, IDENTITY_TOKENS)


def is_authority_sensitive(path: str, root: str) -> bool:
    return root in {"compat", "locks", "repo", "safety", "security", "specs", "updates", "governance"} or has_any(path, AUTHORITY_TOKENS)


def is_build_sensitive(path: str) -> bool:
    return is_code(path) or has_any(path, {"cmake", "abi", "include", "ui_bind", "build", "appcore"})


def is_fixture(path: str) -> bool:
    return has_any(path, FIXTURE_TOKENS)


def is_example(path: str) -> bool:
    return has_any(path, EXAMPLE_TOKENS)


def quarantine_target(root: str, rest: str) -> str:
    quarantine_root = "compatibility" if root == "compat" else root
    return join_target("archive/quarantine/" + quarantine_root, rest)


def target_root(path: str) -> str:
    parts = path_parts(path)
    return parts[0] if parts else ""


def sanitize_target_dirs(target: Optional[str]) -> Tuple[Optional[str], bool]:
    if not target:
        return target, False
    parts = path_parts(target)
    if len(parts) <= 1:
        return target, False
    changed = False
    sanitized: List[str] = []
    for index, part in enumerate(parts):
        if index < len(parts) - 1:
            replacement = FORBIDDEN_DIR_REPLACEMENTS.get(part.lower())
            if replacement:
                sanitized.append(replacement)
                changed = True
                continue
        sanitized.append(part)
    return "/".join(sanitized), changed


class Router:
    def __init__(self, contract: Dict[str, Any], include_quarantine: bool = True) -> None:
        self.bad_roots = list(contract["bad_roots"])
        self.canonical_roots = set(contract["canonical_roots"])
        self.forbidden_dirs = set(contract["forbidden_directory_names"])
        self.allowed_exceptions = set(contract["allowed_directory_exceptions"])
        self.include_quarantine = include_quarantine

    def route(self, source: str) -> Dict[str, Any]:
        root, rest = split_root(source)
        target, reason, route_type = self._propose(root, rest, source)
        if not target and self.include_quarantine:
            target = quarantine_target(root, rest)
            reason = "unknown or ambiguous file routed to parent-root quarantine"
            route_type = "quarantine"
        target, sanitized = sanitize_target_dirs(target)
        entry = {
            "source": source,
            "target": target,
            "root": root,
            "action": "move" if target else "skip",
            "route_type": route_type if target else "impossible",
            "risk": self._risk(source, root, route_type),
            "reason": reason,
            "identity_sensitive": is_identity_sensitive(source),
            "authority_sensitive": is_authority_sensitive(source, root),
            "build_sensitive": is_build_sensitive(source),
            "requires_reference_rewrite": bool(target),
            "requires_import_rewrite": is_code(source),
            "requires_shim": self._shim_candidate(source, root, target),
            "target_path_sanitized": sanitized,
            "skip_reasons": [],
        }
        self._apply_target_validation(entry)
        return entry

    def _propose(self, root: str, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        method = getattr(self, "route_" + root, None)
        if method is None:
            return None, "no bad-root routing rule", "quarantine"
        return method(rest, source)

    def _risk(self, source: str, root: str, route_type: str) -> str:
        if route_type == "quarantine":
            return "medium"
        if root in {"core", "control", "net", "lib", "libs"} or is_build_sensitive(source):
            return "high"
        if is_identity_sensitive(source) or is_authority_sensitive(source, root):
            return "high"
        return "low"

    def _shim_candidate(self, source: str, root: str, target: Optional[str]) -> bool:
        if not target or target.startswith("archive/quarantine/"):
            return False
        return is_python(source) and root in {"validation", "meta", "governance", "core", "control", "net", "lib", "compat"}

    def _apply_target_validation(self, entry: Dict[str, Any]) -> None:
        target = entry.get("target")
        if not target:
            entry["skip_reasons"].append("no_target")
        else:
            if target_root(str(target)) not in self.canonical_roots:
                entry["skip_reasons"].append("target_root_not_canonical")
            forbidden = self._forbidden_dir_reason(str(target))
            if forbidden:
                entry["skip_reasons"].append(forbidden)
        if entry["skip_reasons"]:
            entry["action"] = "skip"
            entry["route_type"] = "impossible"

    def _forbidden_dir_reason(self, target: str) -> Optional[str]:
        normalized = normalize(target)
        for allowed in self.allowed_exceptions:
            if normalized == allowed or normalized.startswith(allowed + "/"):
                return None
        parts = path_parts(normalized)
        for segment in parts[:-1]:
            low = segment.lower()
            if low in self.forbidden_dirs:
                return "target_uses_forbidden_directory_{0}".format(low)
        return None

    def route_ide(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        if rest == "manifests/projection_manifest.schema.json":
            return "contracts/projection/ide/projection_manifest.schema.json", "IDE projection manifest schema", "canonical"
        if rest.startswith("manifests/projection_manifest_examples/") and source.endswith(".projection.json"):
            return join_target("contracts/projection/ide/examples", rest.split("/", 2)[-1]), "IDE projection manifest example", "canonical"
        if rest.lower() == "readme.md":
            return "docs/architecture/IDE_PROJECTIONS.md", "IDE projection documentation", "canonical"
        return None, "unknown IDE material", "quarantine"

    def route_templates(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        if is_schema(source):
            return join_target("contracts/schema/templates", rest), "template schema", "canonical"
        if is_contractlike(source):
            return join_target("contracts/templates", rest), "template contract or manifest", "canonical"
        if is_example(source):
            return join_target("content/examples/templates", rest), "template example", "canonical"
        if is_markdown(source):
            return join_target("docs/development/templates", rest), "template documentation", "canonical"
        if is_data(source) or is_asset(source):
            return join_target("content/templates", rest), "reusable template payload", "canonical"
        return None, "template role unclear", "quarantine"

    def route_models(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        if is_schema(source):
            return join_target("contracts/schema/models", rest), "model schema", "canonical"
        if is_registry(source):
            return join_target("contracts/registry/models", rest), "model registry", "canonical"
        if is_asset(source) or has_any(source, {"asset", "assets"}):
            return join_target("content/assets/models", rest), "model asset", "canonical"
        if is_markdown(source):
            return join_target("docs/domains/models", rest), "model documentation", "canonical"
        if is_data(source) or has_any(source, {"domain", "domains"}):
            return join_target("content/domains/models", rest), "model domain data", "canonical"
        return None, "model role unclear", "quarantine"

    def route_modding(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        if is_schema(source):
            return join_target("contracts/schema/modding", rest), "modding schema", "canonical"
        if has_any(source, {"capability", "capabilities"}):
            return join_target("contracts/capability/modding", rest), "modding capability contract", "canonical"
        if is_contractlike(source):
            return join_target("contracts/package/modding", rest), "modding package contract", "canonical"
        if is_example(source):
            return join_target("content/examples/modding", rest), "modding example", "canonical"
        if is_markdown(source):
            return join_target("docs/modding", rest), "modding documentation", "canonical"
        return None, "modding role unclear", "quarantine"

    def route_data(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        first = first_part(rest)
        if first in {"schemas", "schema"} or is_schema(source):
            return join_target("contracts/schema", drop_first(rest) if first in {"schemas", "schema"} else rest), "data schema", "canonical"
        if first in {"registries", "registry"} or is_registry(source):
            return join_target("contracts/registry", drop_first(rest) if first in {"registries", "registry"} else rest), "data registry", "canonical"
        if first in {"capability", "capabilities"}:
            return join_target("contracts/capability", drop_first(rest)), "data capability contract material", "canonical"
        if first in {"contracts", "contract"} or is_contractlike(source):
            return join_target("contracts", drop_first(rest) if first in {"contracts", "contract"} else rest), "data contract or manifest", "canonical"
        if first == "packs":
            return join_target("content/packs", drop_first(rest)), "authored pack data", "canonical"
        if first == "profiles":
            return join_target("content/profiles", drop_first(rest)), "authored profile data", "canonical"
        if first == "bundles":
            return join_target("content/bundles", drop_first(rest)), "authored bundle data", "canonical"
        if first == "worldgen":
            return join_target("content/domains/worldgen", drop_first(rest)), "worldgen domain data", "canonical"
        if first in {"domains", "domain", "reality", "earth", "sol", "milky_way"}:
            return join_target("content/domains", drop_first(rest) if first in {"domains", "domain"} else rest), "domain data", "canonical"
        if first in {"fixtures", "fixture"} or is_fixture(source):
            return join_target("tests/fixtures", drop_first(rest) if first in {"fixtures", "fixture"} else rest), "fixture data", "canonical"
        if first in {"examples", "example"} or is_example(source):
            return join_target("content/examples", drop_first(rest) if first in {"examples", "example"} else rest), "example data", "canonical"
        if first in {"assets", "asset"} or is_asset(source):
            return join_target("content/assets", drop_first(rest) if first in {"assets", "asset"} else rest), "asset data", "canonical"
        if is_markdown(source):
            return join_target("docs/content", rest), "content documentation", "canonical"
        if is_data(source):
            return join_target("content/data", rest), "authored data", "canonical"
        return None, "data role unclear", "quarantine"

    def route_packs(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        if first_part(rest) == "source":
            return join_target("content/packs", drop_first(rest)), "pack source payload with forbidden source segment removed", "canonical"
        return join_target("content/packs", rest), "pack material", "canonical"

    def route_profiles(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        return join_target("content/profiles", rest), "profile material", "canonical"

    def route_bundles(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        if has_any(source, {"recipe", "release", "packaging"}):
            return join_target("release/packaging/bundles", rest), "release bundle recipe", "canonical"
        return join_target("content/bundles", rest), "authored bundle material", "canonical"

    def route_compat(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        if is_schema(source):
            return join_target("contracts/schema/compatibility", rest), "compatibility schema", "canonical"
        if is_python(source) or has_any(source, {"validator", "validators"}):
            return join_target("tools/validators/compatibility", rest), "compatibility validator", "canonical"
        if is_markdown(source):
            return join_target("docs/compatibility", rest), "compatibility documentation", "canonical"
        if is_contractlike(source) or is_data(source):
            return join_target("contracts/compatibility", rest), "compatibility contract material", "canonical"
        return None, "compatibility role unclear", "quarantine"

    def route_locks(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        if is_schema(source):
            return join_target("contracts/schema/lock", rest), "lock schema", "canonical"
        if has_any(source, {"pack"}):
            return join_target("contracts/package/locks", rest), "pack lock", "canonical"
        if has_any(source, {"profile"}):
            return join_target("contracts/profile/locks", rest), "profile lock", "canonical"
        if has_any(source, {"content"}):
            return join_target("content/data/locks", rest), "content lock", "canonical"
        if has_any(source, {"runtime"}):
            return join_target("runtime/storage/lock", rest), "runtime lock", "canonical"
        if has_any(source, {"transaction"}):
            return join_target("release/updates/locks", rest), "update transaction lock", "canonical"
        if is_markdown(source):
            return join_target("docs/runtime/locks", rest), "lock documentation", "canonical"
        if is_data(source):
            return join_target("contracts/lock", rest), "lock contract material", "canonical"
        return None, "lock role unclear", "quarantine"

    def route_repo(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        if is_schema(source):
            return join_target("contracts/schema/repo", rest), "repo schema", "canonical"
        if is_python(source) or has_any(source, {"validator", "validators"}):
            return join_target("tools/repo", rest), "repo tool", "canonical"
        if is_markdown(source):
            return join_target("docs/repo", rest), "repo documentation", "canonical"
        if is_contractlike(source) or has_any(source, {"layout"}):
            return join_target("contracts/repo", rest), "repo contract or policy", "canonical"
        if is_data(source):
            return join_target("contracts/repo", rest), "repo policy data", "canonical"
        return None, "repo role unclear", "quarantine"

    def route_safety(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        if is_schema(source):
            return join_target("contracts/schema/safety", rest), "safety schema", "canonical"
        if is_python(source) or has_any(source, {"validator", "validators"}):
            return join_target("tools/validators/safety", rest), "safety validator", "canonical"
        if is_markdown(source):
            return join_target("docs/safety", rest), "safety documentation", "canonical"
        if is_contractlike(source) or is_data(source):
            return join_target("contracts/safety", rest), "safety contract material", "canonical"
        return None, "safety role unclear", "quarantine"

    def route_security(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        if is_schema(source):
            return join_target("contracts/schema/security", rest), "security schema", "canonical"
        if is_python(source) or has_any(source, {"validator", "validators"}):
            return join_target("tools/validators/security", rest), "security validator", "canonical"
        if is_markdown(source):
            return join_target("docs/security", rest), "security documentation", "canonical"
        if is_contractlike(source) or is_data(source):
            return join_target("contracts/security", rest), "security contract material", "canonical"
        return None, "security role unclear", "quarantine"

    def route_specs(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        if is_schema(source):
            return join_target("contracts/schema", rest), "schema spec", "canonical"
        if has_any(source, {"protocol"}):
            return join_target("contracts/protocol", rest), "protocol spec", "canonical"
        if has_any(source, {"abi"}):
            return join_target("contracts/abi", rest), "ABI spec", "canonical"
        if has_any(source, {"package"}):
            return join_target("contracts/package", rest), "package spec", "canonical"
        if has_any(source, {"profile"}):
            return join_target("contracts/profile", rest), "profile spec", "canonical"
        if has_any(source, {"replay"}):
            return join_target("contracts/replay", rest), "replay spec", "canonical"
        if has_any(source, {"capability"}):
            return join_target("contracts/capability", rest), "capability spec", "canonical"
        if is_markdown(source):
            return join_target("docs/specs", rest), "human spec", "canonical"
        if is_contractlike(source) or is_data(source):
            return join_target("contracts/specs", rest), "contract spec", "canonical"
        return None, "spec role unclear", "quarantine"

    def route_updates(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        if is_schema(source):
            return join_target("contracts/schema/update", rest), "update schema", "canonical"
        if is_contractlike(source) or is_policy(source):
            return join_target("contracts/update", rest), "update contract or policy", "canonical"
        if is_manifest(source):
            return join_target("release/updates/manifests", rest), "update manifest", "canonical"
        if has_any(source, {"recipe"}):
            return join_target("release/updates/recipes", rest), "update recipe", "canonical"
        if is_python(source):
            return join_target("tools/update", rest), "update tool", "canonical"
        if is_markdown(source):
            return join_target("docs/release/updates", rest), "update documentation", "canonical"
        if is_data(source):
            return join_target("release/updates", rest), "update material", "canonical"
        return None, "update role unclear", "quarantine"

    def route_validation(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        if is_python(source):
            return join_target("tools/validators/validation", rest), "validation Python validator", "canonical"
        if is_schema(source):
            return join_target("contracts/schema/validation", rest), "validation schema", "canonical"
        if is_markdown(source):
            return join_target("docs/validation", rest), "validation documentation", "canonical"
        if is_data(source):
            target = "tests/fixtures/validation" if is_fixture(source) else "contracts/registry/validation"
            return join_target(target, rest), "validation data", "canonical"
        return None, "validation role unclear", "quarantine"

    def route_meta(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        first = first_part(rest)
        if first == "identity":
            if is_python(source):
                return join_target("tools/validators/identity", drop_first(rest)), "identity validator", "canonical"
            if is_schema(source):
                return join_target("contracts/schema/identity", drop_first(rest)), "identity schema", "canonical"
            if is_data(source):
                return join_target("contracts/identity", drop_first(rest)), "identity contract data", "canonical"
        if first == "stability":
            if is_python(source):
                return join_target("tools/validators/stability", drop_first(rest)), "stability validator", "canonical"
            if is_schema(source):
                return join_target("contracts/schema/stability", drop_first(rest)), "stability schema", "canonical"
            if is_data(source):
                return join_target("contracts/stability", drop_first(rest)), "stability contract data", "canonical"
        if first == "versioning":
            return join_target("contracts/version", drop_first(rest)), "versioning metadata", "canonical"
        if first == "release":
            return join_target("release/manifests", drop_first(rest)), "release metadata", "canonical"
        if is_python(source):
            return join_target("tools/repo/meta", rest), "metadata tool", "canonical"
        if is_markdown(source):
            return join_target("docs/repo/meta", rest), "metadata documentation", "canonical"
        if is_data(source):
            return join_target("contracts/registry/meta", rest), "metadata registry material", "canonical"
        return None, "metadata role unclear", "quarantine"

    def route_governance(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        if rest == "__init__.py":
            return quarantine_target("governance", rest), "governance root package exports require merge or shim review", "quarantine"
        if is_schema(source):
            return join_target("contracts/schema/governance", rest), "governance schema", "canonical"
        if is_python(source):
            return join_target("tools/governance", rest), "governance tool", "canonical"
        if is_markdown(source):
            return join_target("docs/governance", rest), "governance documentation", "canonical"
        if is_contractlike(source) or is_data(source):
            return join_target("contracts/governance", rest), "governance contract material", "canonical"
        return None, "governance role unclear", "quarantine"

    def route_performance(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        if is_python(source):
            return join_target("tools/performance", rest), "performance tool", "canonical"
        if has_any(source, {"benchmark"}):
            return join_target("tests/performance", rest), "performance benchmark", "canonical"
        if is_fixture(source):
            return join_target("tests/fixtures/performance", rest), "performance fixture", "canonical"
        if is_markdown(source):
            return join_target("docs/performance", rest), "performance documentation", "canonical"
        if is_data(source):
            return join_target("tests/performance", rest), "performance data", "canonical"
        return None, "performance role unclear", "quarantine"

    def route_core(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        mapping = [
            ("deterministic", "engine/determinism"), ("kernel", "engine/kernel"),
            ("time", "engine/time"), ("id", "engine/identity"), ("identity", "engine/identity"),
            ("math", "engine/math"), ("state", "engine/state"), ("replay", "engine/replay"),
            ("proof", "engine/proof"), ("execution", "engine/execution"), ("memory", "engine/memory"),
            ("diagnostic", "engine/diagnostics"), ("domain", "game/domain"), ("rule", "game/rule"),
            ("process", "game/process"), ("runtime", "runtime"),
            ("contract", "contracts"),
        ]
        for token, prefix in mapping:
            if has_any(source, {token}):
                return join_target(prefix, rest), "core {0} ownership".format(token), "canonical"
        if is_python(source):
            return join_target("tools/core", rest), "core Python tool", "canonical"
        if is_markdown(source):
            return join_target("docs/architecture/core", rest), "core documentation", "canonical"
        return None, "core role unclear", "quarantine"

    def route_control(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        if rest == "__init__.py":
            return quarantine_target("control", rest), "control root package exports require ownership review", "quarantine"
        if has_any(source, {"appshell", "shell"}):
            return join_target("runtime/shell", rest), "control shell material", "canonical"
        if has_any(source, {"command"}):
            target = "contracts/command" if is_schema(source) or is_contractlike(source) else "runtime/shell/command"
            return join_target(target, rest), "control command material", "canonical"
        if has_any(source, {"capability"}):
            target = "contracts/capability" if is_schema(source) or is_contractlike(source) else "runtime/capability"
            return join_target(target, rest), "control capability material", "canonical"
        if has_any(source, {"supervisor"}):
            return join_target("runtime/supervisor", rest), "runtime supervisor", "canonical"
        if is_policy(source):
            return join_target("contracts/governance", rest), "control policy", "canonical"
        if is_python(source):
            return join_target("tools/governance", rest), "control governance tool", "canonical"
        if is_markdown(source):
            return join_target("docs/runtime/control", rest), "control documentation", "canonical"
        return None, "control role unclear", "quarantine"

    def route_net(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        if has_any(source, {"protocol"}):
            return join_target("contracts/protocol/network", rest), "network protocol", "canonical"
        if is_schema(source):
            return join_target("contracts/schema/network", rest), "network schema", "canonical"
        if has_any(source, {"capability"}):
            return join_target("contracts/capability/network", rest), "network capability", "canonical"
        if is_python(source):
            return join_target("tools/network", rest), "network tool", "canonical"
        if is_markdown(source):
            return join_target("docs/runtime/network", rest), "network documentation", "canonical"
        if is_code(source) or has_any(source, {"runtime", "transport", "server", "client"}):
            return join_target("runtime/network", rest), "runtime network material", "canonical"
        return None, "network role unclear", "quarantine"

    def route_lib(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        if has_any(source, {"abi"}):
            return join_target("contracts/abi", rest), "library ABI", "canonical"
        if has_any(source, {"external", "third_party", "vendor"}):
            return join_target("external", rest), "external library", "canonical"
        if has_any(source, {"engine"}):
            return join_target("engine", rest), "engine library", "canonical"
        if has_any(source, {"runtime"}):
            return join_target("runtime", rest), "runtime library", "canonical"
        if is_python(source) or has_any(source, {"tool"}):
            return join_target("tools/libraries", rest), "library tool", "canonical"
        if is_markdown(source):
            return join_target("docs/development/libraries", rest), "library documentation", "canonical"
        return None, "library role unclear", "quarantine"

    def route_libs(self, rest: str, source: str) -> Tuple[Optional[str], str, str]:
        first = first_part(rest)
        if first == "appcore":
            return join_target("runtime/shell", drop_first(rest)), "shell runtime library", "canonical"
        if has_any(source, {"abi"}):
            return join_target("contracts/abi", rest), "library ABI", "canonical"
        if has_any(source, {"external", "third_party", "vendor"}):
            return join_target("external", rest), "external library", "canonical"
        if has_any(source, {"engine"}):
            return join_target("engine", rest), "engine library", "canonical"
        if has_any(source, {"runtime"}):
            return join_target("runtime", rest), "runtime library", "canonical"
        if is_python(source) or has_any(source, {"tool"}):
            return join_target("tools/libraries", rest), "library tool", "canonical"
        if is_markdown(source):
            return join_target("docs/development/libraries", rest), "library documentation", "canonical"
        return None, "libs role unclear", "quarantine"


def apply_collisions(entries: List[Dict[str, Any]], tracked: set) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    target_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for item in entries:
        if item["action"] == "move":
            target_groups[item["target"]].append(item)
    collisions: List[Dict[str, Any]] = []
    collision_sources = set()
    for target, items in sorted(target_groups.items()):
        if target in tracked and all(item["source"] != target for item in items):
            collisions.append({"target": target, "collision_type": "tracked_target_exists", "sources": sorted(item["source"] for item in items)})
            collision_sources.update(item["source"] for item in items)
        if len(items) > 1:
            collisions.append({"target": target, "collision_type": "duplicate_planned_target", "sources": sorted(item["source"] for item in items)})
            collision_sources.update(item["source"] for item in items)
    for item in entries:
        if item["source"] in collision_sources:
            item["action"] = "skip"
            item["route_type"] = "impossible"
            item["skip_reasons"] = sorted(set(item["skip_reasons"] + ["target_collision"]))
    return entries, collisions


def summarize(entries: List[Dict[str, Any]], collisions: List[Dict[str, Any]]) -> Dict[str, Any]:
    movable = [item for item in entries if item["action"] == "move"]
    skipped = [item for item in entries if item["action"] != "move"]
    quarantine = [item for item in movable if item["route_type"] == "quarantine"]
    canonical = [item for item in movable if item["route_type"] == "canonical"]
    return {
        "bad_root_tracked_files": len(entries),
        "routed_count": len(movable),
        "known_canonical_count": len(canonical),
        "quarantine_count": len(quarantine),
        "skipped_impossible_count": len(skipped),
        "collision_count": len(collisions),
        "counts_by_root": dict(sorted(Counter(item["root"] for item in entries).items())),
        "counts_by_route_type": dict(sorted(Counter(item["route_type"] for item in entries).items())),
        "counts_by_target_root": dict(sorted(Counter(target_root(item["target"]) for item in movable).items())),
        "counts_by_risk": dict(sorted(Counter(item["risk"] for item in entries).items())),
        "shim_candidate_count": sum(1 for item in entries if item.get("requires_shim")),
        "target_path_sanitized_count": sum(1 for item in entries if item.get("target_path_sanitized")),
        "import_rewrite_candidate_count": sum(1 for item in entries if item.get("requires_import_rewrite")),
        "reference_rewrite_candidate_count": sum(1 for item in entries if item.get("requires_reference_rewrite")),
    }


def write_json(path: str, payload: Dict[str, Any]) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_text(path: str, text: str) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def md_for_json(path: str) -> str:
    base, _ = os.path.splitext(path)
    return base + ".md"


def render_summary_md(title: str, payload: Dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-05-18",
        "Task: MOVE-ROUTER-00",
        "",
        "# " + title,
        "",
        "Mode: `dry_run`; no files were moved.",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        "| Bad-root tracked files | {0} |".format(summary["bad_root_tracked_files"]),
        "| Routed files | {0} |".format(summary["routed_count"]),
        "| Known canonical routes | {0} |".format(summary["known_canonical_count"]),
        "| Quarantine routes | {0} |".format(summary["quarantine_count"]),
        "| Skipped/impossible | {0} |".format(summary["skipped_impossible_count"]),
        "| Target collisions | {0} |".format(summary["collision_count"]),
        "| Sanitized target paths | {0} |".format(summary["target_path_sanitized_count"]),
        "| Import rewrite candidates | {0} |".format(summary["import_rewrite_candidate_count"]),
        "| Shim candidates | {0} |".format(summary["shim_candidate_count"]),
        "",
        "## Counts By Route Type",
        "",
        "| Route type | Count |",
        "| --- | ---: |",
    ]
    for route_type, count in summary["counts_by_route_type"].items():
        lines.append("| `{0}` | {1} |".format(route_type, count))
    lines.extend(["", "## Counts By Root", "", "| Root | Count |", "| --- | ---: |"])
    for root, count in summary["counts_by_root"].items():
        lines.append("| `{0}` | {1} |".format(root, count))
    lines.append("")
    return "\n".join(lines)


def render_route_table_md(entries: List[Dict[str, Any]]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-05-18",
        "Task: MOVE-ROUTER-00",
        "",
        "# MOVE-ROUTER-00 Route Table",
        "",
        "| Source | Target | Type | Risk |",
        "| --- | --- | --- | --- |",
    ]
    for item in entries[:300]:
        lines.append("| `{0}` | `{1}` | `{2}` | `{3}` |".format(item["source"], item.get("target") or "", item["route_type"], item["risk"]))
    if len(entries) > 300:
        lines.extend(["", "Route table truncated in Markdown; full table is in JSON."])
    lines.append("")
    return "\n".join(lines)


def render_skipped_md(entries: List[Dict[str, Any]]) -> str:
    quarantine = [item for item in entries if item["route_type"] == "quarantine"]
    skipped = [item for item in entries if item["action"] != "move"]
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-05-18",
        "Task: MOVE-ROUTER-00",
        "",
        "# MOVE-ROUTER-00 Skipped Or Quarantined",
        "",
        "Unknown and ambiguous files are routed to `archive/quarantine/<root>/` instead of staying in bad roots.",
        "",
        "- Quarantine routes: {0}".format(len(quarantine)),
        "- Skipped/impossible routes: {0}".format(len(skipped)),
        "",
        "## Quarantine Routes",
        "",
        "| Source | Target | Reason |",
        "| --- | --- | --- |",
    ]
    for item in quarantine[:200]:
        lines.append("| `{0}` | `{1}` | {2} |".format(item["source"], item["target"], item["reason"]))
    if len(quarantine) > 200:
        lines.append("| ... | ... | Full quarantine list is in JSON route table. |")
    lines.extend(["", "## Skipped / Impossible", "", "| Source | Target | Reasons |", "| --- | --- | --- |"])
    for item in skipped:
        lines.append("| `{0}` | `{1}` | `{2}` |".format(item["source"], item.get("target") or "", ", ".join(item.get("skip_reasons") or [])))
    if not skipped:
        lines.append("| none |  |  |")
    lines.append("")
    return "\n".join(lines)


def render_collisions_md(collisions: List[Dict[str, Any]]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-05-18",
        "Task: MOVE-ROUTER-00",
        "",
        "# MOVE-ROUTER-00 Target Collisions",
        "",
    ]
    if not collisions:
        lines.extend(["Target collisions: `0`.", ""])
        return "\n".join(lines)
    lines.extend(["| Target | Type | Sources |", "| --- | --- | --- |"])
    for item in collisions:
        lines.append("| `{0}` | `{1}` | `{2}` |".format(item["target"], item["collision_type"], ", ".join(item["sources"])))
    lines.append("")
    return "\n".join(lines)


def render_compat_root_summary(entries: List[Dict[str, Any]], summary: Dict[str, Any], head: str) -> Dict[str, Any]:
    roots = []
    by_root: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for item in entries:
        by_root[item["root"]].append(item)
    for root in sorted(by_root):
        items = by_root[root]
        roots.append({
            "root": root,
            "tracked_file_count": len(items),
            "route_candidate_count": sum(1 for item in items if item["action"] == "move"),
            "quarantine_count": sum(1 for item in items if item["route_type"] == "quarantine"),
            "skipped_count": sum(1 for item in items if item["action"] != "move"),
            "status": "dry_run_routed",
        })
    return {
        "schema_version": "dominium.move_router_00.root_summary_compat.v1",
        "task_id": "MOVE-ROUTER-00",
        "mode": "dry_run",
        "head": head,
        "roots": roots,
        "summary": summary,
    }


def render_compat_batch_plan(entries: List[Dict[str, Any]], summary: Dict[str, Any], head: str) -> Dict[str, Any]:
    groups = {
        "templates_models_modding": {"templates", "models", "modding"},
        "content_identity": {"data", "packs", "profiles", "bundles"},
        "authority_policy": {"compat", "locks", "repo", "safety", "security", "specs", "updates"},
        "active_tools": {"validation", "meta", "governance", "performance"},
        "runtime_core_net": {"core", "control", "net"},
        "libs_abi": {"lib", "libs"},
        "ide_regression": {"ide"},
    }
    batches = []
    for name, roots in groups.items():
        items = [item for item in entries if item["root"] in roots]
        batches.append({
            "batch": name,
            "roots": sorted(roots),
            "route_candidate_count": sum(1 for item in items if item["action"] == "move"),
            "quarantine_count": sum(1 for item in items if item["route_type"] == "quarantine"),
            "skipped_count": sum(1 for item in items if item["action"] != "move"),
            "apply_authorized": False,
            "status": "dry_run_only",
        })
    return {
        "schema_version": "dominium.move_router_00.batch_plan_compat.v1",
        "task_id": "MOVE-ROUTER-00",
        "mode": "dry_run",
        "head": head,
        "batches": batches,
        "summary": summary,
        "apply_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a dry-run route table for former bad roots.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--contract", default=DEFAULT_CONTRACT)
    parser.add_argument("--rules", default=None, help="Deprecated compatibility option; contract is authoritative.")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--include-quarantine", action="store_true", default=False)
    parser.add_argument("--json-out", default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", default=DEFAULT_MD_OUT)
    parser.add_argument("--route-table-out", default=DEFAULT_ROUTE_TABLE_OUT)
    parser.add_argument("--skipped-out", default=DEFAULT_SKIPPED_OUT)
    parser.add_argument("--target-collisions-out", default=DEFAULT_COLLISIONS_OUT)
    parser.add_argument("--root-summary-out", default=None, help="Compatibility output for MOVE-SCRIPT-00 callers.")
    parser.add_argument("--batch-plan-out", default=None, help="Compatibility output for MOVE-SCRIPT-00 callers.")
    parser.add_argument("--include-root", action="append", default=[])
    parser.add_argument("--fail-on-collision", action="store_true")
    parser.add_argument("--fail-on-unknown", action="store_true", help="Compatibility flag; quarantine routes are not unknown failures.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if args.apply:
        raise SystemExit("--apply is intentionally disabled by MOVE-ROUTER-00; use a later reviewed apply task.")

    repo_root = os.path.abspath(args.repo_root)
    contract = load_contract(repo_root, args.contract)
    router = Router(contract, include_quarantine=True if args.include_quarantine or args.dry_run else False)
    tracked = set(git_ls_files(repo_root))
    head = git_head(repo_root)
    bad_roots = set(router.bad_roots)
    include_roots = set(args.include_root or [])
    bad_paths = sorted(
        path for path in tracked
        if split_root(path)[0] in bad_roots and (not include_roots or split_root(path)[0] in include_roots)
    )

    entries = [router.route(path) for path in bad_paths]
    entries, collisions = apply_collisions(entries, tracked)
    entries = sorted(entries, key=lambda item: (item["root"], item["source"]))
    summary = summarize(entries, collisions)

    payload = {
        "schema_version": DRY_RUN_SCHEMA,
        "task_id": "MOVE-ROUTER-00",
        "mode": "dry_run",
        "head": head,
        "contract": normalize(args.contract),
        "summary": summary,
        "routes": entries,
        "collisions": collisions,
        "no_apply_invariants": {
            "moves_applied": False,
            "deletes_applied": False,
            "renames_applied": False,
            "imports_rewritten": False,
            "references_rewritten": False,
            "shims_created": False,
            "exceptions_retired": False,
        },
    }
    route_table = {
        "schema_version": ROUTE_TABLE_SCHEMA,
        "task_id": "MOVE-ROUTER-00",
        "mode": "dry_run",
        "head": head,
        "summary": summary,
        "routes": entries,
    }

    write_json(os.path.join(repo_root, args.json_out), payload)
    write_text(os.path.join(repo_root, args.md_out), render_summary_md("MOVE-ROUTER-00 Dry Run", payload))
    write_json(os.path.join(repo_root, args.route_table_out), route_table)
    write_text(os.path.join(repo_root, md_for_json(args.route_table_out)), render_route_table_md(entries))
    write_text(os.path.join(repo_root, args.skipped_out), render_skipped_md(entries))
    write_text(os.path.join(repo_root, args.target_collisions_out), render_collisions_md(collisions))
    if args.root_summary_out:
        root_payload = render_compat_root_summary(entries, summary, head)
        write_json(os.path.join(repo_root, args.root_summary_out), root_payload)
        write_text(os.path.join(repo_root, md_for_json(args.root_summary_out)), render_summary_md("MOVE-ROUTER-00 Root Summary Compatibility Report", root_payload))
    if args.batch_plan_out:
        batch_payload = render_compat_batch_plan(entries, summary, head)
        write_json(os.path.join(repo_root, args.batch_plan_out), batch_payload)
        write_text(os.path.join(repo_root, md_for_json(args.batch_plan_out)), render_summary_md("MOVE-ROUTER-00 Batch Plan Compatibility Report", batch_payload))

    print(json.dumps({
        "status": "PASS" if not collisions and summary["skipped_impossible_count"] == 0 else "PASS_WITH_WARNINGS",
        "bad_root_tracked_files": summary["bad_root_tracked_files"],
        "routed_count": summary["routed_count"],
        "known_canonical_count": summary["known_canonical_count"],
        "quarantine_count": summary["quarantine_count"],
        "skipped_impossible_count": summary["skipped_impossible_count"],
        "collision_count": summary["collision_count"],
    }, sort_keys=True))

    if args.fail_on_collision and collisions:
        return 2
    if args.fail_on_unknown and summary["skipped_impossible_count"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
