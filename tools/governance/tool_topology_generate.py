#!/usr/bin/env python3
"""Deterministic ARCH-REF-2 topology map generator."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from typing import Dict, Iterable, List, Set, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


MODULE_ROOTS = ("engine", "game", "client", "server", "platform", "src", "launcher", "setup")
SCHEMA_ROOTS = ("schema", "schemas")
REGISTRY_ROOTS = ("data/registries", "data/governance")
TOOL_ROOT = "tools"
PROCESS_RE = re.compile(r"\bprocess\.[A-Za-z0-9_.]+\b")
TEXT_EXTENSIONS = (".py", ".c", ".cc", ".cpp", ".h", ".hh", ".hpp", ".json", ".md", ".schema", ".schema.json")
CONTROL_PLANE_MODULE_ID = "module:src/control/control_plane_engine.py"
CONTROL_SUBSYSTEM_MODULES = (
    ("control_plane_engine", "src/control/control_plane_engine.py"),
    ("negotiation_kernel", "src/control/negotiation/negotiation_kernel.py"),
    ("control_ir_engine", "src/control/ir/control_ir_compiler.py"),
    ("view_engine", "src/control/view/view_engine.py"),
    ("fidelity_engine", "src/control/fidelity/fidelity_engine.py"),
    ("effect_engine", "src/control/effects/effect_engine.py"),
)
CONTROL_DEPENDENCY_TOKENS = (
    "from src.control",
    "import src.control",
    "src.control.",
    "build_control_intent(",
    "build_control_resolution(",
)

DOMAIN_TO_MODULE_NODE_ID = {
    "ELEC": "module:src/electric",
    "THERM": "module:src/thermal",
    "MOB": "module:src/mobility",
    "SIG": "module:src/signals",
    "PHYS": "module:src/physics",
    "FIELD": "module:src/fields",
    "MECH": "module:src/mechanics",
    "CTRL": "module:src/control",
}


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _ensure_dir(path: str) -> None:
    if path and not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def _read_text(path: str) -> str:
    try:
        return open(path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _read_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _run_git(repo_root: str, argv: List[str]) -> Tuple[int, str]:
    try:
        proc = subprocess.run(
            argv,
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
    except OSError:
        return 127, ""
    return int(proc.returncode), str(proc.stdout or "")


def _repository_hash(repo_root: str, explicit_commit_hash: str = "") -> str:
    commit_hash = str(explicit_commit_hash or "").strip()
    if commit_hash:
        return "COMMIT:{}".format(commit_hash)
    code, out = _run_git(repo_root, ["git", "rev-parse", "HEAD"])
    head = str(out).strip() if code == 0 else ""
    if head:
        return "HEAD:{}".format(head)
    file_tokens: List[str] = []
    for root in ("src", "schema", "schemas", "data/registries", "data/governance", "tools/xstack", "docs/architecture"):
        abs_root = os.path.join(repo_root, root.replace("/", os.sep))
        if not os.path.exists(abs_root):
            continue
        if os.path.isfile(abs_root):
            file_tokens.append(_norm(os.path.relpath(abs_root, repo_root)))
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
            for name in sorted(files):
                rel = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                if name.endswith(TEXT_EXTENSIONS):
                    file_tokens.append(rel)
    return "FALLBACK:{}".format(canonical_sha256(sorted(set(file_tokens))))


def _node(
    *,
    node_id: str,
    node_kind: str,
    path: str = "",
    version: str = "",
    tags: List[str] | None = None,
    owner_subsystem: str = "",
    extensions: Dict[str, object] | None = None,
) -> dict:
    return {
        "node_id": str(node_id),
        "node_kind": str(node_kind),
        "path": _norm(path) or None,
        "version": str(version).strip() or None,
        "tags": sorted(set(str(item).strip() for item in (tags or []) if str(item).strip())),
        "owner_subsystem": str(owner_subsystem).strip() or None,
        "extensions": dict(extensions or {}),
    }


def _edge(*, edge_kind: str, from_node_id: str, to_node_id: str, extensions: Dict[str, object] | None = None) -> dict:
    base = {
        "edge_kind": str(edge_kind),
        "from_node_id": str(from_node_id),
        "to_node_id": str(to_node_id),
    }
    edge_id = "edge.{}.{}".format(str(edge_kind), canonical_sha256(base)[:16])
    return {
        "edge_id": edge_id,
        "from_node_id": str(from_node_id),
        "to_node_id": str(to_node_id),
        "edge_kind": str(edge_kind),
        "extensions": dict(extensions or {}),
    }


def _deterministic_nodes(rows: List[dict]) -> List[dict]:
    unique: Dict[Tuple[str, str], dict] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        node_id = str(row.get("node_id", "")).strip()
        node_kind = str(row.get("node_kind", "")).strip()
        if not node_id or not node_kind:
            continue
        unique[(node_kind, node_id)] = row
    return [
        unique[key]
        for key in sorted(
            unique.keys(),
            key=lambda item: (str(item[0]), str(item[1])),
        )
    ]


def _deterministic_edges(rows: List[dict]) -> List[dict]:
    unique: Dict[Tuple[str, str, str], dict] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        edge_kind = str(row.get("edge_kind", "")).strip()
        from_node_id = str(row.get("from_node_id", "")).strip()
        to_node_id = str(row.get("to_node_id", "")).strip()
        if not edge_kind or not from_node_id or not to_node_id:
            continue
        unique[(edge_kind, from_node_id, to_node_id)] = _edge(
            edge_kind=edge_kind,
            from_node_id=from_node_id,
            to_node_id=to_node_id,
            extensions=dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
        )
    return [
        unique[key]
        for key in sorted(
            unique.keys(),
            key=lambda item: (str(item[0]), str(item[1]), str(item[2])),
        )
    ]


def _iter_rel_files(repo_root: str, rel_root: str, *, suffixes: Tuple[str, ...]) -> Iterable[str]:
    abs_root = os.path.join(repo_root, rel_root.replace("/", os.sep))
    if not os.path.isdir(abs_root):
        return []
    out: List[str] = []
    for walk_root, dirs, files in os.walk(abs_root):
        dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
        for name in sorted(files):
            if suffixes and not name.endswith(suffixes):
                continue
            out.append(_norm(os.path.relpath(os.path.join(walk_root, name), repo_root)))
    return out


def _schema_version_for(rel_path: str, repo_root: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    if rel_path.endswith(".schema"):
        for line in _read_text(abs_path).splitlines():
            token = str(line).strip()
            if token.startswith("schema_version:"):
                return token.split(":", 1)[1].strip()
        return ""
    payload = _read_json(abs_path)
    return str(payload.get("version", "")).strip() or str(payload.get("schema_version", "")).strip()


def _discover_process_families(repo_root: str) -> Dict[str, List[str]]:
    files: List[str] = []
    files.extend(_iter_rel_files(repo_root, "src", suffixes=TEXT_EXTENSIONS))
    files.extend(_iter_rel_files(repo_root, "tools/xstack/sessionx", suffixes=(".py",)))
    for registry_root in REGISTRY_ROOTS:
        files.extend(_iter_rel_files(repo_root, registry_root, suffixes=(".json",)))
    by_family: Dict[str, Set[str]] = {}
    for rel_path in sorted(set(files)):
        text = _read_text(os.path.join(repo_root, rel_path.replace("/", os.sep)))
        if not text:
            continue
        for process_id in sorted(set(PROCESS_RE.findall(text))):
            parts = str(process_id).split(".")
            family = str(parts[1]).strip() if len(parts) >= 2 else "unknown"
            if not family:
                family = "unknown"
            by_family.setdefault(family, set()).add(str(process_id))
    return dict((key, sorted(value)) for key, value in sorted(by_family.items(), key=lambda item: str(item[0])))


def _policy_ids_from_registry(payload: dict) -> List[str]:
    out: Set[str] = set()
    stack: List[object] = [payload]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            for key, value in item.items():
                token = str(key).strip().lower()
                if token.endswith("_policy_id") or token == "policy_id":
                    value_token = str(value).strip()
                    if value_token:
                        out.add(value_token)
                elif token.endswith("_contract_set_id") or token == "contract_set_id":
                    value_token = str(value).strip()
                    if value_token:
                        out.add(value_token)
                if isinstance(value, (dict, list)):
                    stack.append(value)
        elif isinstance(item, list):
            for value in item:
                if isinstance(value, (dict, list)):
                    stack.append(value)
    return sorted(out)


def generate_topology_map(
    *,
    repo_root: str,
    commit_hash: str = "",
    generated_tick: int = 0,
) -> dict:
    repo_root = os.path.normpath(os.path.abspath(repo_root))
    nodes: List[dict] = []
    edges: List[dict] = []

    # Runtime modules and hierarchy.
    for root in MODULE_ROOTS:
        abs_root = os.path.join(repo_root, root.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        root_node_id = "module:{}".format(root)
        nodes.append(
            _node(
                node_id=root_node_id,
                node_kind="module",
                path=root,
                tags=["runtime"],
                owner_subsystem=root.split("/", 1)[0],
            )
        )
        child_dirs = sorted(
            token
            for token in os.listdir(abs_root)
            if os.path.isdir(os.path.join(abs_root, token)) and not token.startswith(".") and token != "__pycache__"
        )
        for child in child_dirs:
            child_path = _norm("{}/{}".format(root, child))
            child_node_id = "module:{}".format(child_path)
            owner = child if root == "src" else root
            nodes.append(
                _node(
                    node_id=child_node_id,
                    node_kind="module",
                    path=child_path,
                    tags=["runtime", root],
                    owner_subsystem=owner,
                )
            )
            edges.append(_edge(edge_kind="depends_on", from_node_id=child_node_id, to_node_id=root_node_id))

    # CTRL-9 control subsystem declarations.
    for subsystem_id, rel_path in CONTROL_SUBSYSTEM_MODULES:
        token = _norm(rel_path)
        abs_path = os.path.join(repo_root, token.replace("/", os.sep))
        tags = ["runtime", "control", "control_subsystem", str(subsystem_id)]
        if not os.path.isfile(abs_path):
            tags.append("planned")
        node_id = "module:{}".format(token)
        nodes.append(
            _node(
                node_id=node_id,
                node_kind="module",
                path=token,
                tags=tags,
                owner_subsystem="control",
                extensions={"control_subsystem_id": str(subsystem_id)},
            )
        )
        edges.append(_edge(edge_kind="depends_on", from_node_id=node_id, to_node_id="module:src/control"))

    control_subsystem_node_ids = [
        "module:{}".format(_norm(path))
        for _, path in CONTROL_SUBSYSTEM_MODULES
    ]
    for dep_node_id in control_subsystem_node_ids:
        if dep_node_id == CONTROL_PLANE_MODULE_ID:
            continue
        edges.append(
            _edge(
                edge_kind="depends_on",
                from_node_id=CONTROL_PLANE_MODULE_ID,
                to_node_id=dep_node_id,
            )
        )
        edges.append(
            _edge(
                edge_kind="consumes",
                from_node_id=CONTROL_PLANE_MODULE_ID,
                to_node_id=dep_node_id,
            )
        )

    schema_nodes: List[dict] = []
    for root in SCHEMA_ROOTS:
        suffixes = (".schema",) if root == "schema" else (".schema.json",)
        for rel_path in sorted(_iter_rel_files(repo_root, root, suffixes=suffixes)):
            node_id = "schema:{}".format(rel_path)
            owner = ""
            parts = rel_path.split("/")
            if len(parts) >= 2 and parts[0] == "schema":
                owner = parts[1]
            version = _schema_version_for(rel_path, repo_root)
            schema_nodes.append(
                _node(
                    node_id=node_id,
                    node_kind="schema",
                    path=rel_path,
                    version=version,
                    tags=["schema", root],
                    owner_subsystem=owner,
                )
            )
    nodes.extend(schema_nodes)

    registry_nodes: List[dict] = []
    registry_names: Dict[str, str] = {}
    for registry_root in REGISTRY_ROOTS:
        for rel_path in sorted(_iter_rel_files(repo_root, registry_root, suffixes=(".json",))):
            registry_name = os.path.basename(rel_path).replace(".json", "")
            registry_names[registry_name] = rel_path
            payload = _read_json(os.path.join(repo_root, rel_path.replace("/", os.sep)))
            version = str(payload.get("schema_version", "")).strip()
            owner = "governance" if rel_path.startswith("data/governance/") else (
                registry_name.split("_", 1)[0] if "_" in registry_name else registry_name
            )
            registry_node_id = "registry:{}".format(registry_name)
            registry_nodes.append(
                _node(
                    node_id=registry_node_id,
                    node_kind="registry",
                    path=rel_path,
                    version=version,
                    tags=["registry", registry_root],
                    owner_subsystem=owner,
                )
            )
    nodes.extend(registry_nodes)

    tool_nodes: List[dict] = []
    tools_root_abs = os.path.join(repo_root, TOOL_ROOT.replace("/", os.sep))
    if os.path.isdir(tools_root_abs):
        for name in sorted(os.listdir(tools_root_abs)):
            abs_path = os.path.join(tools_root_abs, name)
            if not os.path.isdir(abs_path) or name.startswith("."):
                continue
            module_node_id = "tool:tools/{}".format(name)
            tool_nodes.append(
                _node(
                    node_id=module_node_id,
                    node_kind="tool",
                    path=_norm("tools/{}".format(name)),
                    tags=["tool", "module"],
                    owner_subsystem=name,
                )
            )
            for rel_path in _iter_rel_files(repo_root, _norm("tools/{}".format(name)), suffixes=(".py",)):
                base = os.path.basename(rel_path)
                if base == "__init__.py":
                    continue
                tool_node_id = "tool:{}".format(rel_path)
                tool_nodes.append(
                    _node(
                        node_id=tool_node_id,
                        node_kind="tool",
                        path=rel_path,
                        tags=["tool", "entrypoint"],
                        owner_subsystem=name,
                    )
                )
                edges.append(_edge(edge_kind="depends_on", from_node_id=tool_node_id, to_node_id=module_node_id))
    nodes.extend(tool_nodes)

    process_families = _discover_process_families(repo_root)
    for family, process_ids in process_families.items():
        node_id = "process_family:{}".format(family)
        nodes.append(
            _node(
                node_id=node_id,
                node_kind="process_family",
                tags=["process"],
                owner_subsystem=family,
                extensions={"process_count": len(process_ids), "process_ids": list(process_ids)[:64]},
            )
        )
        if any(node.get("node_id") == "module:tools/xstack/sessionx" for node in tool_nodes + nodes):
            edges.append(_edge(edge_kind="depends_on", from_node_id=node_id, to_node_id="module:tools/xstack/sessionx"))
        if "interaction_action_registry" in registry_names:
            edges.append(
                _edge(
                    edge_kind="consumes",
                    from_node_id=node_id,
                    to_node_id="registry:interaction_action_registry",
                )
            )

    # Contract and policy nodes from registries.
    for registry_name, rel_path in sorted(registry_names.items(), key=lambda item: str(item[0])):
        payload = _read_json(os.path.join(repo_root, rel_path.replace("/", os.sep)))
        if "contract_set" in registry_name:
            rows = _policy_ids_from_registry(payload)
            if not rows:
                rows = ["registry.{}".format(registry_name)]
            for contract_id in rows:
                node_id = "contract_set:{}".format(contract_id)
                nodes.append(
                    _node(
                        node_id=node_id,
                        node_kind="contract_set",
                        path=rel_path,
                        tags=["contract_set", registry_name],
                        owner_subsystem="governance",
                    )
                )
                edges.append(_edge(edge_kind="depends_on", from_node_id=node_id, to_node_id="registry:{}".format(registry_name)))
        if "policy" in registry_name:
            rows = _policy_ids_from_registry(payload)
            if not rows:
                rows = ["registry.{}".format(registry_name)]
            for policy_id in rows:
                node_id = "policy_set:{}".format(policy_id)
                nodes.append(
                    _node(
                        node_id=node_id,
                        node_kind="policy_set",
                        path=rel_path,
                        tags=["policy_set", registry_name],
                        owner_subsystem="policy",
                    )
                )
                edges.append(_edge(edge_kind="depends_on", from_node_id=node_id, to_node_id="registry:{}".format(registry_name)))

    # META-CONTRACT topology nodes/edges.
    existing_node_ids = set(str(node.get("node_id", "")) for node in nodes if isinstance(node, dict))
    meta_contract_specs = (
        ("tier_contract_registry", "tier_contracts", "tier", "subsystem_id"),
        ("coupling_contract_registry", "coupling_contracts", "coupling", ""),
        ("explain_contract_registry", "explain_contracts", "explain", ""),
    )
    for registry_name, rows_key, contract_kind, owner_field in meta_contract_specs:
        rel_path = registry_names.get(registry_name, "")
        if not rel_path:
            continue
        payload = _read_json(os.path.join(repo_root, rel_path.replace("/", os.sep)))
        rows = list((dict(payload.get("record") or {})).get(rows_key) or payload.get(rows_key) or [])
        registry_node_id = "registry:{}".format(registry_name)
        for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("contract_id", ""))):
            contract_id = str(row.get("contract_id", "")).strip()
            if not contract_id:
                continue
            node_id = "contract_set:{}".format(contract_id)
            owner_subsystem = str(row.get(owner_field, "")).strip().lower() if owner_field else "governance"
            nodes.append(
                _node(
                    node_id=node_id,
                    node_kind="contract_set",
                    path=rel_path,
                    tags=["contract_set", "meta_contract", contract_kind],
                    owner_subsystem=owner_subsystem or "governance",
                    extensions={"contract_kind": contract_kind},
                )
            )
            edges.append(_edge(edge_kind="depends_on", from_node_id=node_id, to_node_id=registry_node_id))

            if contract_kind == "tier":
                subsystem_id = str(row.get("subsystem_id", "")).strip().upper()
                module_node_id = DOMAIN_TO_MODULE_NODE_ID.get(subsystem_id, "")
                if module_node_id and module_node_id in existing_node_ids:
                    edges.append(_edge(edge_kind="enforces", from_node_id=node_id, to_node_id=module_node_id))
            elif contract_kind == "coupling":
                from_domain_id = str(row.get("from_domain_id", "")).strip().upper()
                to_domain_id = str(row.get("to_domain_id", "")).strip().upper()
                from_module_node_id = DOMAIN_TO_MODULE_NODE_ID.get(from_domain_id, "")
                to_module_node_id = DOMAIN_TO_MODULE_NODE_ID.get(to_domain_id, "")
                if from_module_node_id and from_module_node_id in existing_node_ids:
                    edges.append(_edge(edge_kind="enforces", from_node_id=node_id, to_node_id=from_module_node_id))
                if to_module_node_id and to_module_node_id in existing_node_ids:
                    edges.append(_edge(edge_kind="enforces", from_node_id=node_id, to_node_id=to_module_node_id))
                mechanism_id = str(row.get("mechanism_id", "")).strip()
                if mechanism_id:
                    edges.append(
                        _edge(
                            edge_kind="consumes",
                            from_node_id=node_id,
                            to_node_id=registry_node_id,
                            extensions={"mechanism_id": mechanism_id},
                        )
                    )
            elif contract_kind == "explain":
                event_kind_id = str(row.get("event_kind_id", "")).strip().lower()
                domain_prefix = str(event_kind_id.split(".", 1)[0] if event_kind_id else "").strip().upper()
                module_node_id = DOMAIN_TO_MODULE_NODE_ID.get(domain_prefix, "")
                if module_node_id and module_node_id in existing_node_ids:
                    edges.append(_edge(edge_kind="enforces", from_node_id=node_id, to_node_id=module_node_id))

    # Topology artifact ownership nodes/edges.
    topology_contract_node = _node(
        node_id="contract_set:governance.topology_map_artifact",
        node_kind="contract_set",
        path="docs/audit/TOPOLOGY_MAP.json",
        tags=["governance", "derived_artifact"],
        owner_subsystem="governance",
    )
    nodes.append(topology_contract_node)
    if any(node.get("node_id") == "tool:tools/governance/tool_topology_generate.py" for node in tool_nodes):
        edges.append(
            _edge(
                edge_kind="produces",
                from_node_id="tool:tools/governance/tool_topology_generate.py",
                to_node_id="contract_set:governance.topology_map_artifact",
            )
        )
    if any(node.get("node_id") == "tool:tools/governance/tool_semantic_impact.py" for node in tool_nodes):
        edges.append(
            _edge(
                edge_kind="consumes",
                from_node_id="tool:tools/governance/tool_semantic_impact.py",
                to_node_id="contract_set:governance.topology_map_artifact",
            )
        )

    # Tool validation/enforcement edges.
    schema_node_ids = sorted(
        set(str(node.get("node_id")) for node in nodes if str(node.get("node_kind", "")) == "schema")
    )
    policy_node_ids = sorted(
        set(str(node.get("node_id")) for node in nodes if str(node.get("node_kind", "")) == "policy_set")
    )
    contract_node_ids = sorted(
        set(str(node.get("node_id")) for node in nodes if str(node.get("node_kind", "")) == "contract_set")
    )
    for tool_node in sorted(set(str(node.get("node_id")) for node in nodes if str(node.get("node_kind", "")) == "tool")):
        lower_id = tool_node.lower()
        if "compatx" in lower_id:
            for schema_node_id in schema_node_ids:
                edges.append(_edge(edge_kind="validates", from_node_id=tool_node, to_node_id=schema_node_id))
        if "repox" in lower_id or "auditx" in lower_id:
            for target_id in policy_node_ids + contract_node_ids:
                edges.append(_edge(edge_kind="enforces", from_node_id=tool_node, to_node_id=target_id))
        if "testx" in lower_id:
            for target_id in policy_node_ids + contract_node_ids:
                edges.append(_edge(edge_kind="validates", from_node_id=tool_node, to_node_id=target_id))

    # Module/schema/registry textual dependency approximation.
    schema_tokens = dict(
        (
            os.path.basename(str(node.get("path") or "")).replace(".schema.json", "").replace(".schema", "").lower(),
            str(node.get("node_id")),
        )
        for node in nodes
        if str(node.get("node_kind", "")) == "schema" and str(node.get("path", "")).strip()
    )
    registry_tokens = dict((str(name).lower(), "registry:{}".format(name)) for name in registry_names.keys())
    module_nodes = [node for node in nodes if str(node.get("node_kind", "")) == "module" and str(node.get("path") or "").strip()]
    for module in sorted(module_nodes, key=lambda row: str(row.get("node_id", ""))):
        module_id = str(module.get("node_id", ""))
        module_path = str(module.get("path", "")).strip()
        abs_path = os.path.join(repo_root, module_path.replace("/", os.sep))
        candidate_files: List[str] = []
        if os.path.isfile(abs_path):
            candidate_files.append(_norm(module_path))
        elif os.path.isdir(abs_path):
            for walk_root, dirs, files in os.walk(abs_path):
                dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
                for name in sorted(files):
                    if not name.endswith(TEXT_EXTENSIONS):
                        continue
                    candidate_files.append(_norm(os.path.relpath(os.path.join(walk_root, name), repo_root)))
                    if len(candidate_files) >= 300:
                        break
                if len(candidate_files) >= 300:
                    break
        module_text = "\n".join(_read_text(os.path.join(repo_root, rel.replace("/", os.sep))) for rel in sorted(set(candidate_files)))
        lowered = module_text.lower()
        if not lowered:
            continue
        if module_id != CONTROL_PLANE_MODULE_ID and (not str(module_path).startswith("src/control/")):
            if any(token in lowered for token in CONTROL_DEPENDENCY_TOKENS):
                edges.append(
                    _edge(
                        edge_kind="depends_on",
                        from_node_id=module_id,
                        to_node_id=CONTROL_PLANE_MODULE_ID,
                    )
                )
                edges.append(
                    _edge(
                        edge_kind="consumes",
                        from_node_id=module_id,
                        to_node_id=CONTROL_PLANE_MODULE_ID,
                    )
                )
        for token, schema_node_id in sorted(schema_tokens.items(), key=lambda item: str(item[0])):
            if token and token in lowered:
                edges.append(_edge(edge_kind="consumes", from_node_id=module_id, to_node_id=schema_node_id))
        for token, registry_node_id in sorted(registry_tokens.items(), key=lambda item: str(item[0])):
            if token and token in lowered:
                edges.append(_edge(edge_kind="consumes", from_node_id=module_id, to_node_id=registry_node_id))

    nodes_out = _deterministic_nodes(nodes)
    edges_out = _deterministic_edges(edges)
    node_kind_counts = dict(sorted(Counter(str(node.get("node_kind", "")) for node in nodes_out).items(), key=lambda item: str(item[0])))
    edge_kind_counts = dict(sorted(Counter(str(edge.get("edge_kind", "")) for edge in edges_out).items(), key=lambda item: str(item[0])))
    payload = {
        "topology_id": "dominium.audit.topology_map",
        "generated_tick": int(max(0, int(generated_tick))),
        "repository_hash": _repository_hash(repo_root, explicit_commit_hash=commit_hash),
        "nodes": nodes_out,
        "edges": edges_out,
        "summary": {
            "node_count": len(nodes_out),
            "edge_count": len(edges_out),
            "node_kind_counts": node_kind_counts,
            "edge_kind_counts": edge_kind_counts,
        },
        "deterministic_fingerprint": "",
        "extensions": {
            "generator": "tools/governance/tool_topology_generate.py",
        },
    }
    fingerprint_payload = dict(payload)
    fingerprint_payload["generated_tick"] = 0
    fingerprint_payload["deterministic_fingerprint"] = ""
    payload["deterministic_fingerprint"] = canonical_sha256(fingerprint_payload)
    return payload


def _write_json(path: str, payload: dict) -> None:
    _ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(payload))
        handle.write("\n")


def _write_markdown(path: str, payload: dict) -> None:
    nodes = list(payload.get("nodes") or [])
    edges = list(payload.get("edges") or [])
    node_kind_counts = dict((dict(payload.get("summary") or {})).get("node_kind_counts") or {})
    edge_kind_counts = dict((dict(payload.get("summary") or {})).get("edge_kind_counts") or {})
    runtime_modules = [
        str(node.get("node_id", ""))
        for node in nodes
        if str(node.get("node_kind", "")) == "module" and "runtime" in set(str(t) for t in (node.get("tags") or []))
    ]
    lines: List[str] = [
        "Status: DERIVED",
        "Version: 1.0.0",
        "",
        "# System Topology Map",
        "",
        "- topology_id: `{}`".format(str(payload.get("topology_id", ""))),
        "- repository_hash: `{}`".format(str(payload.get("repository_hash", ""))),
        "- generated_tick: `{}`".format(int(payload.get("generated_tick", 0) or 0)),
        "- deterministic_fingerprint: `{}`".format(str(payload.get("deterministic_fingerprint", ""))),
        "",
        "## Counts",
        "- node_count: {}".format(int((dict(payload.get("summary") or {})).get("node_count", len(nodes)))),
        "- edge_count: {}".format(int((dict(payload.get("summary") or {})).get("edge_count", len(edges)))),
        "",
        "## Node Kinds",
    ]
    for key in sorted(node_kind_counts.keys(), key=lambda item: str(item)):
        lines.append("- {}: {}".format(str(key), int(node_kind_counts.get(key, 0) or 0)))
    lines.append("")
    lines.append("## Edge Kinds")
    for key in sorted(edge_kind_counts.keys(), key=lambda item: str(item)):
        lines.append("- {}: {}".format(str(key), int(edge_kind_counts.get(key, 0) or 0)))
    lines.append("")
    lines.append("## Major Runtime Modules")
    for token in sorted(set(runtime_modules))[:64]:
        lines.append("- `{}`".format(token))
    lines.append("")
    lines.append("## Control Subsystem Nodes")
    control_nodes = [
        str(node.get("node_id", ""))
        for node in nodes
        if str(node.get("node_kind", "")) == "module"
        and str((dict(node.get("extensions") or {})).get("control_subsystem_id", "")).strip()
    ]
    for token in sorted(set(control_nodes)):
        lines.append("- `{}`".format(token))
    lines.append("")
    lines.append("## Notes")
    lines.append("- Process-family discovery is best-effort via deterministic process token scanning.")
    lines.append("- Control dependency edges are synthesized for modules that reference control-plane APIs.")
    lines.append("- Artifact is governance-only and not loaded by runtime simulation code.")
    _ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines).rstrip() + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic architecture topology map artifacts.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--commit-hash", default="")
    parser.add_argument("--generated-tick", type=int, default=0)
    parser.add_argument("--out-json", default="docs/audit/TOPOLOGY_MAP.json")
    parser.add_argument("--out-md", default="docs/audit/TOPOLOGY_MAP.md")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(args.repo_root)) if str(args.repo_root).strip() else REPO_ROOT_HINT
    payload = generate_topology_map(
        repo_root=repo_root,
        commit_hash=str(args.commit_hash or ""),
        generated_tick=int(args.generated_tick or 0),
    )
    out_json_abs = os.path.join(repo_root, str(args.out_json).replace("/", os.sep))
    out_md_abs = os.path.join(repo_root, str(args.out_md).replace("/", os.sep))
    _write_json(out_json_abs, payload)
    _write_markdown(out_md_abs, payload)
    result = {
        "result": "complete",
        "out_json": _norm(os.path.relpath(out_json_abs, repo_root)),
        "out_md": _norm(os.path.relpath(out_md_abs, repo_root)),
        "node_count": int((dict(payload.get("summary") or {})).get("node_count", 0)),
        "edge_count": int((dict(payload.get("summary") or {})).get("edge_count", 0)),
        "deterministic_fingerprint": str(payload.get("deterministic_fingerprint", "")),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
