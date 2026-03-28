"""Repo import bridge for pre-XI top-level source aliases."""

from __future__ import annotations

import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import json
import os
import sys
from functools import lru_cache


_EXCLUDED_TOP_LEVEL = {"platform", "time", "tools"}
_INSTALLED_BY_ROOT: dict[str, bool] = {}
_V4_LOCK_REL = os.path.join("data", "restructure", "src_domain_mapping_lock_approved_v4.json")


class _SrcAliasLoader(importlib.abc.Loader):
    def create_module(self, spec):
        alias = str((spec.loader_state or {}).get("alias") or "").strip()
        if not alias:
            return None
        module = importlib.import_module(alias)
        sys.modules[spec.name] = module
        return module

    def exec_module(self, module) -> None:
        return None


class _SrcAliasFinder(importlib.abc.MetaPathFinder):
    def __init__(self, repo_root: str):
        self.repo_root = os.path.normpath(os.path.abspath(repo_root))
        self.src_root = os.path.join(self.repo_root, "src")
        self.top_level_aliases = self._discover_top_level_aliases()

    def _discover_top_level_aliases(self) -> set[str]:
        names: set[str] = set()
        if not os.path.isdir(self.src_root):
            return names
        for entry in sorted(os.listdir(self.src_root)):
            if not entry or entry.startswith(".") or entry in _EXCLUDED_TOP_LEVEL:
                continue
            entry_path = os.path.join(self.src_root, entry)
            if os.path.isfile(entry_path) and entry.endswith(".py") and entry != "__init__.py":
                names.add(entry[:-3])
            elif os.path.isfile(entry_path) and entry.endswith(".pyc") and entry != "__init__.pyc":
                names.add(entry[:-4])
            elif os.path.isdir(entry_path) and (
                os.path.isfile(os.path.join(entry_path, "__init__.py"))
                or os.path.isfile(os.path.join(entry_path, "__init__.pyc"))
            ):
                names.add(entry)
        return names

    def _repo_has_concrete_module(self, fullname: str) -> bool:
        token = str(fullname or "").strip().replace(".", os.sep)
        if not token:
            return False
        module_path = os.path.join(self.repo_root, token + ".py")
        module_path_pyc = os.path.join(self.repo_root, token + ".pyc")
        package_init = os.path.join(self.repo_root, token, "__init__.py")
        package_init_pyc = os.path.join(self.repo_root, token, "__init__.pyc")
        return (
            os.path.isfile(module_path)
            or os.path.isfile(module_path_pyc)
            or os.path.isfile(package_init)
            or os.path.isfile(package_init_pyc)
        )

    @staticmethod
    def _is_namespace_stub(spec) -> bool:
        if spec is None:
            return False
        return (
            spec.loader is None
            and getattr(spec, "origin", None) is None
            and spec.submodule_search_locations is not None
        )

    def _alias_name(self, fullname: str) -> str:
        token = str(fullname or "").strip()
        if not token or token == "src" or token.startswith("src.") or token == "tools" or token.startswith("tools."):
            return ""
        if self._repo_has_concrete_module(token):
            return ""
        if token == "engine.platform" or token.startswith("engine.platform."):
            return "engine.platform" + token[len("engine.platform") :]
        if token == "engine.time" or token.startswith("engine.time."):
            return "engine.time" + token[len("engine.time") :]
        head, dot, tail = token.partition(".")
        if head not in self.top_level_aliases:
            return ""
        return "src." + head + (dot + tail if tail else "")

    def find_spec(self, fullname: str, path=None, target=None):
        if fullname in sys.modules:
            return None
        alias = self._alias_name(fullname)
        if not alias:
            return None
        native_spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        if native_spec is not None and not self._is_namespace_stub(native_spec):
            return None
        try:
            alias_spec = importlib.util.find_spec(alias)
        except (ImportError, AttributeError, ValueError):
            return None
        if alias_spec is None:
            return None
        spec = importlib.util.spec_from_loader(
            fullname,
            _SrcAliasLoader(),
            is_package=alias_spec.submodule_search_locations is not None,
        )
        if spec is None:
            return None
        spec.loader_state = {"alias": alias}
        if alias_spec.submodule_search_locations is not None:
            spec.submodule_search_locations = list(alias_spec.submodule_search_locations)
        return spec


def install_src_aliases(repo_root: str) -> None:
    root = os.path.normpath(os.path.abspath(repo_root))
    if _INSTALLED_BY_ROOT.get(root):
        return
    finder = _SrcAliasFinder(root)
    sys.meta_path.insert(0, finder)
    _INSTALLED_BY_ROOT[root] = True


@lru_cache(maxsize=None)
def _v4_target_to_source(repo_root: str) -> dict[str, str]:
    root = os.path.normpath(os.path.abspath(repo_root))
    lock_path = os.path.join(root, _V4_LOCK_REL.replace("/", os.sep))
    try:
        payload = json.load(open(lock_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    rows = list(dict(payload or {}).get("approved_for_xi5") or [])
    out: dict[str, str] = {}
    for row in rows:
        row_map = dict(row or {})
        source_path = str(row_map.get("source_path") or "").strip().replace("\\", "/")
        target_path = str(row_map.get("target_path") or "").strip().replace("\\", "/")
        if source_path and target_path:
            out[target_path] = source_path
    return out


def resolve_repo_path_equivalent(repo_root: str, rel_path: str) -> str:
    root = os.path.normpath(os.path.abspath(repo_root))
    token = str(rel_path or "").strip().replace("\\", "/")
    if not token:
        return token
    target_abs = os.path.join(root, token.replace("/", os.sep))
    if os.path.exists(target_abs):
        return token
    source_token = _v4_target_to_source(root).get(token, "")
    if source_token:
        source_abs = os.path.join(root, source_token.replace("/", os.sep))
        if os.path.exists(source_abs):
            return source_token
    return token


__all__ = ["install_src_aliases", "resolve_repo_path_equivalent"]
