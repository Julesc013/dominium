#!/usr/bin/env python3
"""Dry-run router for former bad-root cleanup.

The tool is intentionally no-apply for MOVE-SCRIPT-00. It produces deterministic
route candidates and skip ledgers from tracked files only.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


SCHEMA_VERSION = "dominium.move_script_00.routing_preview.v1"
SKIPPED_SCHEMA_VERSION = "dominium.move_script_00.skipped_ledger.v1"
ROOT_SUMMARY_SCHEMA_VERSION = "dominium.move_script_00.root_summary.v1"
BATCH_PLAN_SCHEMA_VERSION = "dominium.move_script_00.batch_plan.v1"

DEFAULT_RULES_PATH = os.path.join("tools", "migration", "bad_root_routing_rules.json")
DEFAULT_JSON_OUT = os.path.join(".aide", "reports", "MOVE-SCRIPT-00-routing-preview.json")
DEFAULT_MD_OUT = os.path.join(".aide", "reports", "MOVE-SCRIPT-00-routing-preview.md")
DEFAULT_SKIPPED_OUT = os.path.join(".aide", "reports", "MOVE-SCRIPT-00-skipped-ledger.json")
DEFAULT_ROOT_SUMMARY_OUT = os.path.join(".aide", "reports", "MOVE-SCRIPT-00-root-summary.json")
DEFAULT_BATCH_PLAN_OUT = os.path.join(".aide", "reports", "MOVE-SCRIPT-00-batch-plan.json")

DOC_EXTS = {".md", ".txt", ".rst", ".adoc"}
CODE_EXTS = {".py", ".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inl", ".inc", ".ipp"}
PY_EXTS = {".py"}
BUILD_EXTS = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".cmake"}
DATA_EXTS = {".json", ".jsonl", ".toml", ".yaml", ".yml", ".csv", ".tsv", ".schema", ".lock"}
ASSET_EXTS = {
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".ico",
    ".wav", ".ogg", ".mp3", ".flac",
    ".obj", ".fbx", ".gltf", ".glb", ".mtl",
    ".asc", ".bsp", ".tls",
}

IDENTITY_TOKENS = {
    "id", "identity", "fingerprint", "hash", "manifest", "registry", "lock",
    "pack", "packs", "profile", "profiles", "bundle", "bundles", "capability",
    "capabilities", "trust", "compat", "compatibility", "release", "version",
    "product", "contract", "schema", "protocol", "policy",
}
AUTHORITY_TOKENS = {
    "policy", "contract", "schema", "schemas", "registry", "registries", "ruleset",
    "rulesets", "security", "safety", "trust", "capability", "compatibility",
    "governance", "law", "canon", "authority", "protocol", "spec", "specs",
}
GENERATED_TOKENS = {
    "audit", "analysis", "generated", "evidence", "metrics", "reports",
    "runs", "planning", "restructure", "refactor", "regression",
    "cache", "output",
}
HISTORICAL_TOKENS = {"archive", "historical", "history", "legacy", "attic", "quarantine", "superseded"}
FIXTURE_TOKENS = {"fixture", "fixtures", "golden", "baseline", "baselines", "test", "tests", "vector", "vectors"}
EXAMPLE_TOKENS = {"example", "examples", "sample", "samples", "demo", "demos"}
RUNTIME_TOKENS = {"runtime", "transport", "network", "storage", "ipc", "platform", "shell", "supervisor"}
ENGINE_TOKENS = {"kernel", "determinism", "identity", "time", "math", "memory", "order", "schedule", "event", "state", "execution", "replay", "proof"}


def normalize(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def run_git(repo_root: str, args: Sequence[str], binary: bool = False) -> Any:
    cmd = ["git", "-C", repo_root] + list(args)
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        sys.stderr.write(result.stderr.decode("utf-8", errors="replace"))
        raise SystemExit(result.returncode)
    if binary:
        return result.stdout
    return result.stdout.decode("utf-8", errors="replace")


def git_ls_files(repo_root: str) -> List[str]:
    raw = run_git(repo_root, ["ls-files", "-z"], binary=True)
    paths = [normalize(part.decode("utf-8", errors="surrogateescape")) for part in raw.split(b"\0") if part]
    return sorted(paths)


def git_head(repo_root: str) -> str:
    return run_git(repo_root, ["rev-parse", "HEAD"]).strip()


def load_rules(repo_root: str, rel_or_abs: str) -> Dict[str, Any]:
    path = rel_or_abs
    if not os.path.isabs(path):
        path = os.path.join(repo_root, path)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def split_root(path: str) -> Tuple[str, str]:
    parts = normalize(path).split("/", 1)
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def path_parts(path: str) -> List[str]:
    return [part for part in normalize(path).split("/") if part]


def ext_of(path: str) -> str:
    return os.path.splitext(path_parts(path)[-1] if path_parts(path) else path)[1].lower()


def lower_parts(path: str) -> List[str]:
    return [part.lower() for part in path_parts(path)]


def name_lower(path: str) -> str:
    parts = path_parts(path)
    return parts[-1].lower() if parts else ""


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
    parts = path_parts(rest)
    return "/".join(parts[count:])


def join_target(prefix: str, rest: str = "") -> str:
    prefix = normalize(prefix)
    rest = normalize(rest)
    if not rest:
        return prefix
    return prefix + "/" + rest


def replace_first(rest: str, prefix: str) -> str:
    return join_target(prefix, drop_first(rest, 1))


def file_role(path: str) -> str:
    ext = ext_of(path)
    name = name_lower(path)
    if name == "cmakelists.txt" or ext == ".cmake":
        return "build_metadata"
    if ext in DOC_EXTS:
        return "documentation"
    if ext in PY_EXTS:
        return "python_module"
    if ext in {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}:
        return "compiled_source"
    if "schema" in token_text(path) or ext == ".schema":
        return "schema"
    if "registry" in token_text(path) or "ruleset" in token_text(path):
        return "registry"
    if ext in DATA_EXTS:
        return "data"
    if ext in ASSET_EXTS:
        return "asset"
    return "unknown"


def is_schema(path: str) -> bool:
    return file_role(path) == "schema" or has_any(path, {"schema", "schemas"})


def is_registry(path: str) -> bool:
    return has_any(path, {"registry", "registries", "ruleset", "rulesets"})


def is_contractlike(path: str) -> bool:
    return has_any(path, {"contract", "contracts", "policy", "matrix", "manifest", "capability", "capabilities"})


def is_markdown(path: str) -> bool:
    return ext_of(path) in DOC_EXTS


def is_python(path: str) -> bool:
    return ext_of(path) in PY_EXTS


def is_build_sensitive(path: str) -> bool:
    return (
        ext_of(path) in BUILD_EXTS
        or name_lower(path) == "cmakelists.txt"
        or has_any(path, {"cmake", "abi", "include", "ui_bind", "build", "appcore", "dom_contracts"})
    )


def is_identity_sensitive(path: str) -> bool:
    return has_any(path, IDENTITY_TOKENS)


def is_authority_sensitive(path: str, root: str) -> bool:
    return root in {"compat", "locks", "repo", "safety", "security", "specs", "updates", "governance"} or has_any(path, AUTHORITY_TOKENS)


def is_generated_evidence(path: str) -> bool:
    return has_any(path, GENERATED_TOKENS)


def is_historical(path: str) -> bool:
    return has_any(path, HISTORICAL_TOKENS)


def is_fixture(path: str) -> bool:
    return has_any(path, FIXTURE_TOKENS)


def is_example(path: str) -> bool:
    return has_any(path, EXAMPLE_TOKENS)


def target_root(path: Optional[str]) -> str:
    if not path:
        return ""
    return path_parts(path)[0] if path_parts(path) else ""


class Router:
    def __init__(self, rules: Dict[str, Any]) -> None:
        self.rules = rules
        self.bad_roots = list(rules.get("bad_roots", []))
        self.canonical_roots = set(rules.get("canonical_target_roots", []))
        self.forbidden_segments = set(rules.get("forbidden_target_segments", []))
        self.allowed_exceptions = set(rules.get("allowed_target_segment_exceptions", []))
        self.root_to_batch: Dict[str, str] = {}
        self.batch_meta: Dict[str, Dict[str, Any]] = {}
        for batch_name, meta in sorted((rules.get("batches") or {}).items()):
            self.batch_meta[batch_name] = dict(meta)
            for root in meta.get("roots", []):
                self.root_to_batch[root] = batch_name

    def batch_for_root(self, root: str) -> str:
        return self.root_to_batch.get(root, "unbatched")

    def validation_tier(self, batch: str) -> str:
        return str(self.batch_meta.get(batch, {}).get("validation_tier", "unassigned"))

    def route(self, source: str) -> Dict[str, Any]:
        root, rest = split_root(source)
        batch = self.batch_for_root(root)
        target, reason, identity_safe = self.propose(root, rest, source)
        risk = self.risk(root, source, target)
        role = file_role(source)
        decision = {
            "source": source,
            "target": target,
            "action": "move" if target else "skip",
            "batch": batch,
            "batch_id": self.batch_meta.get(batch, {}).get("batch_id", ""),
            "root": root,
            "risk": risk,
            "file_role": role,
            "reason": reason,
            "identity_sensitive": is_identity_sensitive(source),
            "identity_safe": bool(identity_safe),
            "build_sensitive": is_build_sensitive(source),
            "authority_sensitive": is_authority_sensitive(source, root),
            "generated_evidence": is_generated_evidence(source),
            "historical": is_historical(source),
            "requires_reference_rewrite": bool(target),
            "requires_import_rewrite": is_python(source) or (role == "compiled_source" and root in {"libs", "lib"}),
            "requires_shim": False,
            "validation_tier": self.validation_tier(batch),
            "skip_reason": None,
            "skip_reasons": [],
        }
        self.apply_safety(decision)
        return decision

    def propose(self, root: str, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        method = getattr(self, "route_" + root, None)
        if method is None:
            return None, "no routing rule for root", False
        return method(rest, source)

    def risk(self, root: str, source: str, target: Optional[str]) -> str:
        if not target:
            return "blocked"
        if root in {"core", "control", "net", "lib", "libs"} or is_build_sensitive(source):
            return "high"
        if is_identity_sensitive(source) or is_authority_sensitive(source, root):
            return "high"
        if is_generated_evidence(source):
            return "medium"
        return "low"

    def apply_safety(self, decision: Dict[str, Any]) -> None:
        target = decision.get("target")
        source = str(decision.get("source"))
        root = str(decision.get("root"))
        reasons: List[str] = []
        if not target:
            reasons.append("target_unknown")
        else:
            if target_root(str(target)) not in self.canonical_roots:
                reasons.append("target_root_not_canonical")
            forbidden = self.forbidden_target_reason(str(target))
            if forbidden:
                reasons.append(forbidden)
        if is_python(source) and root in {
            "core", "control", "compat", "lib", "packs", "safety", "security", "specs",
            "meta", "governance", "performance", "validation", "modding", "models", "net",
        }:
            reasons.append("active_python_package_requires_import_rewrite_or_shim_plan")
        if decision.get("identity_sensitive") and not decision.get("identity_safe"):
            reasons.append("identity_sensitive_without_clear_identity_safe_route")
        if decision.get("build_sensitive") and decision.get("validation_tier") == "unassigned":
            reasons.append("build_sensitive_without_validation_tier")
        if root == "specs" and is_markdown(source) and normalize(source).startswith("specs/reality/"):
            reasons.append("normative_specs_reality_docs_require_authority_review")
        if decision.get("authority_sensitive") and target and str(target).startswith("docs/") and root in {"repo", "safety", "security", "specs", "updates", "governance", "compat"}:
            reasons.append("authority_sensitive_docs_only_route_requires_review")
        if decision.get("generated_evidence") and target and not (str(target).startswith("archive/generated/") or str(target).startswith("archive/historical/")) and root == "data":
            reasons.append("generated_evidence_policy_unclear_for_non_archive_target")

        if reasons:
            decision["action"] = "skip"
            decision["skip_reasons"] = sorted(set(reasons))
            decision["skip_reason"] = decision["skip_reasons"][0]

    def forbidden_target_reason(self, target: str) -> Optional[str]:
        normalized = normalize(target)
        for allowed in self.allowed_exceptions:
            if normalized == allowed or normalized.startswith(allowed + "/"):
                return None
        for segment in path_parts(normalized):
            if segment.lower() in self.forbidden_segments:
                return "target_uses_forbidden_segment_{0}".format(segment.lower())
        return None

    def route_templates(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        if is_schema(source):
            return join_target("contracts/schema/templates", rest), "template schema", True
        if is_contractlike(source):
            return join_target("contracts/templates", rest), "template contract or manifest", True
        if is_example(source):
            return join_target("content/examples/templates", rest), "template example", True
        if is_markdown(source):
            return join_target("docs/development/templates", rest), "template documentation", True
        return join_target("content/templates", rest), "authored template payload", True

    def route_models(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        if is_schema(source):
            return join_target("contracts/schema/models", rest), "model schema", True
        if is_registry(source):
            return join_target("contracts/registry/models", rest), "model registry", True
        if ext_of(source) in ASSET_EXTS:
            return join_target("content/assets/models", rest), "model asset", True
        if is_markdown(source):
            return join_target("docs/domains/models", rest), "model documentation", True
        if ext_of(source) in DATA_EXTS:
            return join_target("content/domains/models", rest), "model domain data", True
        return join_target("content/domains/models", rest), "model payload fallback", False

    def route_modding(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        if is_schema(source):
            return join_target("contracts/schema/modding", rest), "modding schema", True
        if has_any(source, {"capability", "capabilities"}):
            return join_target("contracts/capability/modding", rest), "modding capability contract", True
        if is_contractlike(source):
            return join_target("contracts/package/modding", rest), "modding package contract", True
        if is_example(source):
            return join_target("content/examples/modding", rest), "modding example", True
        if is_markdown(source):
            return join_target("docs/modding", rest), "modding documentation", True
        return join_target("content/examples/modding", rest), "modding example fallback", False

    def route_data(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        first = first_part(rest)
        if first in {"audit", "analysis", "planning", "restructure", "refactor", "regression"} or is_generated_evidence(source):
            return join_target("archive/generated", rest), "generated retained evidence", True
        if first in {"capability", "capabilities"}:
            return join_target("contracts/capability", drop_first(rest)), "capability contract data", True
        if first in {"protocol", "protocols"}:
            return join_target("contracts/protocol", drop_first(rest)), "protocol contract data", True
        if first in {"profile", "profiles"}:
            return join_target("content/profiles", drop_first(rest)), "authored profile data", True
        if first in {"package", "packages"}:
            return join_target("contracts/package", drop_first(rest)), "package contract data", True
        if is_schema(source) or first in {"schema", "schemas"}:
            return join_target("contracts/schema", drop_first(rest) if first in {"schema", "schemas"} else rest), "data schema", True
        if is_registry(source) or first in {"registry", "registries"}:
            return join_target("contracts/registry", drop_first(rest) if first in {"registry", "registries"} else rest), "data registry", True
        if first in {"contracts", "contract"} or is_contractlike(source):
            return join_target("contracts", drop_first(rest) if first in {"contracts", "contract"} else rest), "data contract or manifest", True
        if first == "packs":
            return join_target("content/packs", drop_first(rest)), "authored pack data", True
        if first == "bundles":
            return join_target("content/bundles", drop_first(rest)), "authored bundle data", True
        if first in {"world", "worldgen", "domain", "domains", "reality", "earth", "sol", "milky_way"}:
            return join_target("content/domains", rest), "domain data", True
        if is_fixture(source) or first in {"fixtures", "fixture", "golden", "test", "tests"}:
            return join_target("tests/fixtures", rest), "fixture or baseline data", True
        if is_example(source) or first in {"examples", "example", "samples"}:
            return join_target("content/examples", rest), "example data", True
        if first in {"assets", "asset", "media", "locale", "locales"} or ext_of(source) in ASSET_EXTS:
            return join_target("content/assets", drop_first(rest) if first in {"assets", "asset", "media"} else rest), "asset data", True
        if first in {"archive", "history", "historical"} or is_historical(source):
            return join_target("archive/historical/data", drop_first(rest) if first in {"archive", "history", "historical"} else rest), "historical data", True
        if first in {"baselines", "baseline"}:
            return join_target("tests/fixtures", rest), "baseline fixture data", True
        if first in {"release", "releases"}:
            return join_target("release/manifests", drop_first(rest)), "release metadata", True
        if is_markdown(source):
            return join_target("docs/content", rest), "content documentation", True
        return join_target("content/data", rest), "data fallback route", False

    def route_packs(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        if is_markdown(source):
            return join_target("docs/content/packs", rest), "pack documentation", True
        if is_python(source):
            return join_target("tools/package", rest), "pack Python tooling candidate", False
        return join_target("content/packs", rest), "pack payload and manifest", True

    def route_profiles(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        return join_target("content/profiles", rest), "profile payload", True

    def route_bundles(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        if is_markdown(source):
            return join_target("docs/content/bundles", rest), "bundle documentation", True
        if has_any(source, {"recipe", "release", "packaging"}):
            return join_target("release/packaging/bundles", rest), "release bundle recipe", True
        return join_target("content/bundles", rest), "bundle payload", True

    def route_compat(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        if is_schema(source):
            return join_target("contracts/schema/compatibility", rest), "compatibility schema", True
        if is_python(source):
            return join_target("tools/validators/compatibility", rest), "compatibility Python candidate", False
        if is_markdown(source):
            return join_target("docs/compatibility", rest), "compatibility documentation", True
        return join_target("contracts/compatibility", rest), "compatibility contract or policy", True

    def route_locks(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        if is_schema(source):
            return join_target("contracts/schema/locks", rest), "lock schema", True
        if has_any(source, {"pack"}):
            return join_target("contracts/package/locks", rest), "pack lock contract", True
        if has_any(source, {"profile"}):
            return join_target("contracts/profile/locks", rest), "profile lock contract", True
        if has_any(source, {"runtime", "ipc", "process"}):
            return join_target("runtime/storage/locks", rest), "runtime lock", True
        if has_any(source, {"transaction", "update", "rollback"}):
            return join_target("release/updates/locks", rest), "update transaction lock", True
        if is_markdown(source):
            return join_target("docs/runtime/locks", rest), "lock documentation", True
        return join_target("contracts/lock", rest), "lock contract fallback", False

    def route_repo(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        if is_schema(source):
            return join_target("contracts/repo/schema", rest), "repo schema", True
        if is_python(source):
            return join_target("tools/validators/repo", rest), "repo validator candidate", False
        if is_markdown(source):
            return join_target("docs/repo", rest), "repo documentation", True
        return join_target("contracts/repo", rest), "repo contract or policy", True

    def route_safety(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        if is_schema(source):
            return join_target("contracts/safety/schema", rest), "safety schema", True
        if is_python(source):
            return join_target("tools/validators/safety", rest), "safety Python candidate", False
        if is_markdown(source):
            return join_target("docs/safety", rest), "safety documentation", True
        return join_target("contracts/safety", rest), "safety contract or policy", True

    def route_security(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        if is_schema(source):
            return join_target("contracts/security/schema", rest), "security schema", True
        if is_python(source):
            return join_target("tools/validators/security", rest), "security Python candidate", False
        if is_markdown(source):
            return join_target("docs/security", rest), "security documentation", True
        return join_target("contracts/security", rest), "security contract or policy", True

    def route_specs(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        if is_schema(source):
            return join_target("contracts/schema", rest), "spec schema", True
        if has_any(source, {"protocol"}):
            return join_target("contracts/protocol", rest), "protocol spec", True
        if has_any(source, {"abi"}):
            return join_target("contracts/abi", rest), "ABI spec", True
        if has_any(source, {"package", "pack"}):
            return join_target("contracts/package", rest), "package spec", True
        if has_any(source, {"profile"}):
            return join_target("contracts/profile", rest), "profile spec", True
        if has_any(source, {"replay"}):
            return join_target("contracts/replay", rest), "replay spec", True
        if has_any(source, {"capability"}):
            return join_target("contracts/capability", rest), "capability spec", True
        if is_markdown(source):
            return join_target("docs/specs", rest), "spec documentation candidate", False
        if is_python(source):
            return join_target("tools/repo/specs", rest), "spec Python candidate", False
        return join_target("contracts/specs", rest), "spec contract fallback", False

    def route_updates(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        if is_schema(source):
            return join_target("contracts/update/schema", rest), "update schema", True
        if is_python(source):
            return join_target("tools/update", rest), "update tool", False
        if is_markdown(source):
            return join_target("docs/release/updates", rest), "update documentation", True
        if is_contractlike(source):
            return join_target("contracts/update", rest), "update contract or policy", True
        return join_target("release/updates", rest), "update feed or manifest", True

    def route_validation(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        if is_schema(source):
            return join_target("contracts/schema/validation", rest), "validation schema", True
        if is_markdown(source):
            return join_target("docs/validation", rest), "validation documentation", True
        return join_target("tools/validators/validation", rest), "validation tool candidate", False

    def route_meta(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        if first_part(rest) == "identity" and is_schema(source):
            return join_target("contracts/schema/identity", drop_first(rest)), "identity schema", True
        if first_part(rest) == "identity" and ext_of(source) in DATA_EXTS:
            return join_target("contracts/identity", drop_first(rest)), "identity contract data", True
        if first_part(rest) == "stability" and is_schema(source):
            return join_target("contracts/schema/stability", drop_first(rest)), "stability schema", True
        if first_part(rest) == "stability" and ext_of(source) in DATA_EXTS:
            return join_target("contracts/stability", drop_first(rest)), "stability contract data", True
        if has_any(source, {"version"}):
            return join_target("contracts/version", rest), "version contract", True
        if has_any(source, {"release"}):
            return join_target("contracts/release", rest), "release metadata", True
        if is_markdown(source):
            return join_target("docs/repo/meta", rest), "meta documentation", True
        if is_python(source):
            return join_target("tools/repo/meta", rest), "meta Python candidate", False
        return join_target("contracts/registry/meta", rest), "meta registry fallback", False

    def route_governance(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        if is_schema(source):
            return join_target("contracts/governance/schema", rest), "governance schema", True
        if is_python(source):
            return join_target("tools/governance", rest), "governance Python candidate", False
        if is_markdown(source):
            return join_target("docs/governance", rest), "governance documentation", True
        return join_target("contracts/governance", rest), "governance contract or policy", True

    def route_performance(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        if is_fixture(source):
            return join_target("tests/fixtures/performance", rest), "performance fixture", True
        if is_markdown(source):
            return join_target("docs/performance", rest), "performance documentation", True
        if ext_of(source) in DATA_EXTS:
            return join_target("tests/performance", rest), "performance data", True
        return join_target("tools/performance", rest), "performance tool candidate", False

    def route_core(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        first = first_part(rest)
        if is_schema(source) or has_any(source, {"contract", "protocol"}):
            return join_target("contracts/core", rest), "core contract candidate", False
        if is_markdown(source):
            return join_target("docs/architecture/core", rest), "core documentation", True
        if first in {"state", "schedule"}:
            return join_target("engine", rest), "deterministic engine substrate", False
        if first in {"spatial"}:
            return join_target("engine/math", rest), "deterministic math substrate", False
        if first in {"constraints", "flow", "graph"}:
            return join_target("engine/execution", rest), "deterministic execution substrate", False
        if first in {"hazards"}:
            return join_target("game/domain", rest), "domain hazard logic candidate", False
        return join_target("engine", rest), "core deterministic substrate fallback", False

    def route_control(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        first = first_part(rest)
        if is_markdown(source):
            return join_target("docs/runtime/control", rest), "control documentation", True
        if first == "capability":
            return join_target("runtime/capability", drop_first(rest)), "runtime capability control", False
        if first in {"ir", "command"}:
            return join_target("contracts/command", rest), "control command contract candidate", False
        if first == "proof":
            return join_target("engine/proof", rest), "control proof candidate", False
        if first in {"effects", "fidelity", "negotiation", "planning", "view"}:
            return join_target("runtime/shell", rest), "runtime shell control candidate", False
        return join_target("runtime/shell", rest), "control runtime shell fallback", False

    def route_net(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        first = first_part(rest)
        if is_schema(source):
            return join_target("contracts/schema/network", rest), "network schema", True
        if is_markdown(source):
            return join_target("docs/runtime/network", rest), "network documentation", True
        if first in {"policies", "policy"}:
            return join_target("contracts/protocol/network", rest), "network protocol policy candidate", False
        if first in {"anti_cheat"}:
            return join_target("contracts/capability/network", rest), "network capability candidate", False
        if first in {"testing", "tests"}:
            return join_target("tools/validators/network", rest), "network test tooling candidate", False
        return join_target("runtime/network", rest), "runtime network candidate", False

    def route_lib(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        if is_markdown(source):
            return join_target("docs/development/libraries", rest), "library documentation", True
        if has_any(source, {"abi"}):
            return join_target("contracts/abi", rest), "library ABI contract", True
        if has_any(source, {"external", "vendor", "third_party"}):
            return join_target("external", rest), "external library", True
        if is_python(source):
            return join_target("tools/libraries", rest), "Python library candidate", False
        return None, "library ownership unclear", False

    def route_libs(self, rest: str, source: str) -> Tuple[Optional[str], str, bool]:
        first = first_part(rest)
        if not rest or name_lower(source) == "cmakelists.txt" and not first:
            return None, "top-level libs CMake requires explicit build plan", False
        if is_markdown(source):
            return join_target("docs/development/libraries", rest), "library documentation", True
        if first == "appcore":
            if "ui_bind" in lower_parts(rest):
                return join_target("runtime/shell/appcore", drop_first(rest)), "appcore UI bind requires UI-bind plan", False
            return join_target("runtime/shell/appcore", drop_first(rest)), "AppCore runtime shell library", True
        if first == "build_identity":
            return join_target("engine/identity/build_identity", drop_first(rest)), "build identity engine support library", True
        if first == "contracts":
            return join_target("contracts/abi/dom_contracts", drop_first(rest)), "dom_contracts ABI surface", True
        if first == "ui_backends":
            return join_target("runtime/ui/backends", drop_first(rest)), "runtime UI backend", True
        if has_any(source, {"external", "vendor", "third_party"}):
            return join_target("external", rest), "external library", True
        return None, "libs ownership unclear", False


def apply_collision_refusals(routes: List[Dict[str, Any]], tracked: set) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    target_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for route in routes:
        if route.get("action") == "move" and route.get("target"):
            target_groups[str(route["target"])].append(route)

    collisions: List[Dict[str, Any]] = []
    collision_sources = set()
    for target, items in sorted(target_groups.items()):
        if target in tracked and all(item["source"] != target for item in items):
            collisions.append({
                "target": target,
                "collision_type": "tracked_target_exists",
                "sources": sorted(item["source"] for item in items),
            })
            collision_sources.update(item["source"] for item in items)
        if len(items) > 1:
            collisions.append({
                "target": target,
                "collision_type": "duplicate_planned_target",
                "sources": sorted(item["source"] for item in items),
            })
            collision_sources.update(item["source"] for item in items)

    final_routes: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []
    for route in routes:
        if route["source"] in collision_sources:
            route = dict(route)
            route["action"] = "skip"
            reasons = set(route.get("skip_reasons") or [])
            reasons.add("target_collision")
            route["skip_reasons"] = sorted(reasons)
            route["skip_reason"] = route["skip_reasons"][0]
        if route.get("action") == "move":
            final_routes.append(route)
        else:
            skipped.append(route)
    return final_routes, skipped, collisions


def summarize_roots(bad_roots: Sequence[str], routes: List[Dict[str, Any]], skipped: List[Dict[str, Any]], all_bad_paths: List[str]) -> List[Dict[str, Any]]:
    by_root_paths = Counter(split_root(path)[0] for path in all_bad_paths)
    route_counts = Counter(item["root"] for item in routes)
    skip_counts = Counter(item["root"] for item in skipped)
    risk_counts: Dict[str, Counter] = defaultdict(Counter)
    skip_reason_counts: Dict[str, Counter] = defaultdict(Counter)
    batch_by_root: Dict[str, str] = {}
    for item in routes + skipped:
        risk_counts[item["root"]][item.get("risk", "unknown")] += 1
        batch_by_root[item["root"]] = item.get("batch", "unbatched")
        for reason in item.get("skip_reasons") or []:
            skip_reason_counts[item["root"]][reason] += 1
    summaries = []
    for root in sorted(bad_roots):
        tracked = by_root_paths[root]
        summaries.append({
            "root": root,
            "tracked_file_count": tracked,
            "route_candidate_count": route_counts[root],
            "skipped_count": skip_counts[root],
            "batch": batch_by_root.get(root, ""),
            "risk_counts": dict(sorted(risk_counts[root].items())),
            "skip_reason_counts": dict(sorted(skip_reason_counts[root].items())),
            "status": "empty_or_retired" if tracked == 0 else ("all_routed" if tracked and skip_counts[root] == 0 else "has_deferred_items"),
        })
    return summaries


def summarize_batches(router: Router, routes: List[Dict[str, Any]], skipped: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    route_counts = Counter(item["batch"] for item in routes)
    skip_counts = Counter(item["batch"] for item in skipped)
    root_counts: Dict[str, Counter] = defaultdict(Counter)
    for item in routes + skipped:
        root_counts[item["batch"]][item["root"]] += 1
    plans = []
    for batch_name, meta in sorted(router.batch_meta.items(), key=lambda item: item[1].get("batch_id", item[0])):
        plans.append({
            "batch": batch_name,
            "batch_id": meta.get("batch_id", ""),
            "title": meta.get("title", ""),
            "roots": meta.get("roots", []),
            "validation_tier": meta.get("validation_tier", ""),
            "route_candidate_count": route_counts[batch_name],
            "skipped_count": skip_counts[batch_name],
            "root_file_counts": dict(sorted(root_counts[batch_name].items())),
            "next_gate": meta.get("next_gate", "MOVE-BULK-BG-REFINEMENT-00"),
            "apply_authorized": False,
            "status": "dry_run_only",
        })
    return plans


def write_json(path: str, payload: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def md_path_for(json_path: str) -> str:
    base, _ = os.path.splitext(json_path)
    return base + ".md"


def markdown_preview(payload: Dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-05-18",
        "Supersedes: none",
        "Superseded By: none",
        "",
        "# MOVE-SCRIPT-00 Routing Preview",
        "",
        "Mode: `dry_run`.",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        "| Bad-root tracked files | {0} |".format(summary["bad_root_tracked_files"]),
        "| Route candidates | {0} |".format(summary["route_candidate_count"]),
        "| Skipped/deferred | {0} |".format(summary["skipped_count"]),
        "| Collisions | {0} |".format(summary["collision_count"]),
        "",
        "## Route Candidates By Batch",
        "",
        "| Batch | Count |",
        "| --- | ---: |",
    ]
    for batch, count in sorted(summary["route_candidates_by_batch"].items()):
        lines.append("| `{0}` | {1} |".format(batch, count))
    lines.extend(["", "## Top Skip Reasons", "", "| Reason | Count |", "| --- | ---: |"])
    for reason, count in sorted(summary["skips_by_reason"].items(), key=lambda item: (-item[1], item[0]))[:20]:
        lines.append("| `{0}` | {1} |".format(reason, count))
    lines.extend(["", "## First Route Candidates", "", "| Source | Target | Batch | Risk |", "| --- | --- | --- | --- |"])
    for item in payload["routes"][:40]:
        lines.append("| `{source}` | `{target}` | `{batch}` | `{risk}` |".format(**item))
    if len(payload["routes"]) > 40:
        lines.append("")
        lines.append("Additional route candidates are recorded in the JSON report.")
    lines.append("")
    return "\n".join(lines)


def markdown_skipped(payload: Dict[str, Any]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-05-18",
        "Supersedes: none",
        "Superseded By: none",
        "",
        "# MOVE-SCRIPT-00 Skipped Ledger",
        "",
        "Skipped items are deferred, not failed moves. MOVE-SCRIPT-00 is dry-run only.",
        "",
        "| Reason | Count |",
        "| --- | ---: |",
    ]
    for reason, count in sorted(payload["summary"]["skips_by_reason"].items(), key=lambda item: (-item[1], item[0])):
        lines.append("| `{0}` | {1} |".format(reason, count))
    lines.extend(["", "## First Skipped Items", "", "| Source | Proposed Target | Reasons |", "| --- | --- | --- |"])
    for item in payload["skipped"][:80]:
        lines.append("| `{0}` | `{1}` | `{2}` |".format(
            item["source"],
            item.get("target") or "",
            ", ".join(item.get("skip_reasons") or []),
        ))
    if len(payload["skipped"]) > 80:
        lines.append("")
        lines.append("Additional skipped items are recorded in the JSON report.")
    lines.append("")
    return "\n".join(lines)


def markdown_root_summary(payload: Dict[str, Any]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-05-18",
        "Supersedes: none",
        "Superseded By: none",
        "",
        "# MOVE-SCRIPT-00 Root Summary",
        "",
        "| Root | Tracked | Routes | Skipped | Status |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for item in payload["roots"]:
        lines.append("| `{root}` | {tracked_file_count} | {route_candidate_count} | {skipped_count} | `{status}` |".format(**item))
    lines.append("")
    return "\n".join(lines)


def markdown_batch_plan(payload: Dict[str, Any]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-05-18",
        "Supersedes: none",
        "Superseded By: none",
        "",
        "# MOVE-SCRIPT-00 Batch Plan",
        "",
        "No batch is authorized to apply by this report.",
        "",
        "| Batch | Title | Routes | Skipped | Validation | Next Gate |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for item in payload["batches"]:
        lines.append("| `{0}` | {1} | {2} | {3} | {4} | `{5}` |".format(
            item["batch_id"],
            item["title"],
            item["route_candidate_count"],
            item["skipped_count"],
            item["validation_tier"],
            item["next_gate"],
        ))
    lines.append("")
    return "\n".join(lines)


def build_summary(routes: List[Dict[str, Any]], skipped: List[Dict[str, Any]], collisions: List[Dict[str, Any]], all_bad_paths: List[str]) -> Dict[str, Any]:
    return {
        "bad_root_tracked_files": len(all_bad_paths),
        "route_candidate_count": len(routes),
        "skipped_count": len(skipped),
        "collision_count": len(collisions),
        "route_candidates_by_batch": dict(sorted(Counter(item["batch"] for item in routes).items())),
        "skipped_by_batch": dict(sorted(Counter(item["batch"] for item in skipped).items())),
        "skips_by_reason": dict(sorted(Counter(reason for item in skipped for reason in (item.get("skip_reasons") or ["unspecified"])).items())),
        "routes_by_root": dict(sorted(Counter(item["root"] for item in routes).items())),
        "skipped_by_root": dict(sorted(Counter(item["root"] for item in skipped).items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a dry-run route plan for former bad roots.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json-out", default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", default=DEFAULT_MD_OUT)
    parser.add_argument("--skipped-out", default=DEFAULT_SKIPPED_OUT)
    parser.add_argument("--root-summary-out", default=DEFAULT_ROOT_SUMMARY_OUT)
    parser.add_argument("--batch-plan-out", default=DEFAULT_BATCH_PLAN_OUT)
    parser.add_argument("--rules", default=DEFAULT_RULES_PATH)
    parser.add_argument("--include-root", action="append", default=[])
    parser.add_argument("--fail-on-collision", action="store_true")
    parser.add_argument("--fail-on-unknown", action="store_true")
    parser.add_argument("--dry-run", action="store_true", default=True)
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    rules = load_rules(repo_root, args.rules)
    router = Router(rules)
    include_roots = set(args.include_root or [])
    bad_roots = [root for root in router.bad_roots if not include_roots or root in include_roots]
    bad_root_set = set(bad_roots)

    tracked = set(git_ls_files(repo_root))
    head = git_head(repo_root)
    all_bad_paths = sorted(path for path in tracked if split_root(path)[0] in bad_root_set)

    preliminary = [router.route(path) for path in all_bad_paths]
    routes, skipped, collisions = apply_collision_refusals(preliminary, tracked)
    routes = sorted(routes, key=lambda item: (item["batch"], item["root"], item["source"]))
    skipped = sorted(skipped, key=lambda item: (item["root"], item["source"], item.get("skip_reason") or ""))
    collisions = sorted(collisions, key=lambda item: (item["target"], item["collision_type"]))
    root_summaries = summarize_roots(bad_roots, routes, skipped, all_bad_paths)
    batch_plans = summarize_batches(router, routes, skipped)
    summary = build_summary(routes, skipped, collisions, all_bad_paths)

    preview = {
        "schema_version": SCHEMA_VERSION,
        "task_id": "MOVE-SCRIPT-00",
        "mode": "dry_run",
        "dry_run_only": True,
        "head": head,
        "rules_schema_version": rules.get("schema_version", ""),
        "bad_roots": bad_roots,
        "routes": routes,
        "skipped": skipped,
        "collisions": collisions,
        "summary": summary,
        "no_apply_invariants": {
            "moves_applied": False,
            "deletes_applied": False,
            "renames_applied": False,
            "imports_rewritten": False,
            "references_rewritten": False,
            "shims_created": False,
            "exceptions_retired": False,
            "move_maps_applied": False,
            "salvage_maps_applied": False,
        },
    }
    skipped_payload = {
        "schema_version": SKIPPED_SCHEMA_VERSION,
        "task_id": "MOVE-SCRIPT-00",
        "mode": "dry_run",
        "head": head,
        "skipped": skipped,
        "summary": summary,
    }
    root_payload = {
        "schema_version": ROOT_SUMMARY_SCHEMA_VERSION,
        "task_id": "MOVE-SCRIPT-00",
        "mode": "dry_run",
        "head": head,
        "roots": root_summaries,
        "summary": summary,
    }
    batch_payload = {
        "schema_version": BATCH_PLAN_SCHEMA_VERSION,
        "task_id": "MOVE-SCRIPT-00",
        "mode": "dry_run",
        "head": head,
        "batches": batch_plans,
        "summary": summary,
        "apply_authorized": False,
    }

    write_json(os.path.join(repo_root, args.json_out), preview)
    write_text(os.path.join(repo_root, args.md_out), markdown_preview(preview))
    write_json(os.path.join(repo_root, args.skipped_out), skipped_payload)
    write_text(os.path.join(repo_root, md_path_for(args.skipped_out)), markdown_skipped(skipped_payload))
    write_json(os.path.join(repo_root, args.root_summary_out), root_payload)
    write_text(os.path.join(repo_root, md_path_for(args.root_summary_out)), markdown_root_summary(root_payload))
    write_json(os.path.join(repo_root, args.batch_plan_out), batch_payload)
    write_text(os.path.join(repo_root, md_path_for(args.batch_plan_out)), markdown_batch_plan(batch_payload))

    print(json.dumps({
        "status": "PASS_WITH_WARNINGS" if skipped else "PASS",
        "bad_root_tracked_files": len(all_bad_paths),
        "route_candidate_count": len(routes),
        "skipped_count": len(skipped),
        "collision_count": len(collisions),
    }, sort_keys=True))

    if args.fail_on_collision and collisions:
        return 2
    if args.fail_on_unknown and any("target_unknown" in (item.get("skip_reasons") or []) for item in skipped):
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
