"""XStack extension hook loader and descriptor model."""

from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass
from typing import Dict, List

from tools.xstack.core.runners_base import BaseRunner


@dataclass(frozen=True)
class ExtensionDescriptor:
    extension_id: str
    runner: BaseRunner
    artifact_contract: List[str]
    scope_subtrees: List[str]
    cost_class: str


_CACHE: List[ExtensionDescriptor] | None = None


def _normalize_list(values: object) -> List[str]:
    if not isinstance(values, list):
        return []
    return sorted(set(str(item).replace("\\", "/").strip() for item in values if str(item).strip()))


def _load_module(path: str):
    spec = importlib.util.spec_from_file_location("xstack_extension_{}".format(abs(hash(path))), path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _iter_extension_modules() -> List[str]:
    root = os.path.dirname(os.path.abspath(__file__))
    out = []
    for name in sorted(os.listdir(root)):
        if name.startswith("_") or name in {"__pycache__"}:
            continue
        ext_dir = os.path.join(root, name)
        if not os.path.isdir(ext_dir):
            continue
        candidate = os.path.join(ext_dir, "extension.py")
        if os.path.isfile(candidate):
            out.append(candidate)
    return out


def _normalize_descriptor(raw: object) -> ExtensionDescriptor | None:
    if not isinstance(raw, dict):
        return None
    extension_id = str(raw.get("extension_id", "")).strip()
    runner = raw.get("runner")
    if not extension_id or not isinstance(runner, BaseRunner):
        return None
    cost_class = str(raw.get("cost_class", "")).strip().lower() or "low"
    if cost_class not in {"low", "medium", "high", "critical"}:
        cost_class = "low"
    return ExtensionDescriptor(
        extension_id=extension_id,
        runner=runner,
        artifact_contract=_normalize_list(raw.get("artifact_contract")),
        scope_subtrees=_normalize_list(raw.get("scope_subtrees")),
        cost_class=cost_class,
    )


def load_extensions(force_refresh: bool = False) -> List[ExtensionDescriptor]:
    global _CACHE
    if _CACHE is not None and not force_refresh:
        return list(_CACHE)
    rows: List[ExtensionDescriptor] = []
    for module_path in _iter_extension_modules():
        try:
            module = _load_module(module_path)
        except Exception:
            continue
        if module is None:
            continue
        register = getattr(module, "register_extensions", None)
        if not callable(register):
            continue
        try:
            raw_rows = register()
        except Exception:
            continue
        if not isinstance(raw_rows, list):
            continue
        for raw in raw_rows:
            descriptor = _normalize_descriptor(raw)
            if descriptor is None:
                continue
            rows.append(descriptor)
    rows.sort(key=lambda row: (row.extension_id, row.runner.runner_id()))
    _CACHE = rows
    return list(rows)


def extension_runner_map(force_refresh: bool = False) -> Dict[str, BaseRunner]:
    out: Dict[str, BaseRunner] = {}
    for row in load_extensions(force_refresh=force_refresh):
        out[row.runner.runner_id()] = row.runner
    return out


def extension_registry_definitions(force_refresh: bool = False) -> List[dict]:
    rows = []
    for descriptor in load_extensions(force_refresh=force_refresh):
        rows.append(
            {
                "extension_id": descriptor.extension_id,
                "runner_id": descriptor.runner.runner_id(),
                "artifact_contract": list(descriptor.artifact_contract),
                "scope_subtrees": list(descriptor.scope_subtrees),
                "cost_class": descriptor.cost_class,
                "version_hash": descriptor.runner.version_hash(),
            }
        )
    rows.sort(key=lambda row: (str(row.get("extension_id", "")), str(row.get("runner_id", ""))))
    return rows
