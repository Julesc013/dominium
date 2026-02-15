"""Deterministic dependency resolution for Pack System v1 manifests."""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Set, Tuple

from .errors import build_error, result_complete, result_refused


DEPENDENCY_TOKEN_RE = re.compile(r"^([a-zA-Z0-9._-]+)(?:@(\d+\.\d+\.\d+))?$")


def parse_dependency_token(raw_token: str) -> Tuple[str, str]:
    token = str(raw_token or "").strip()
    match = DEPENDENCY_TOKEN_RE.fullmatch(token)
    if not match:
        return "", ""
    pack_id = str(match.group(1) or "").strip()
    version = str(match.group(2) or "").strip()
    return pack_id, version


def _selected_pack_ids(
    packs_by_id: Dict[str, dict],
    bundle_selection: Optional[List[str]],
    errors: List[Dict[str, str]],
) -> Set[str]:
    if bundle_selection is None:
        return set(packs_by_id.keys())

    selected = set()
    for item in sorted(set(str(value).strip() for value in bundle_selection if str(value).strip())):
        if item not in packs_by_id:
            errors.append(
                build_error(
                    "refuse.pack.selection_missing_pack",
                    "bundle selection references missing pack '{}'".format(item),
                    "$.bundle_selection",
                )
            )
            continue
        selected.add(item)
    return selected


def _expand_dependencies(
    selected_ids: Set[str],
    packs_by_id: Dict[str, dict],
    errors: List[Dict[str, str]],
) -> Set[str]:
    pending = sorted(selected_ids)
    seen = set(selected_ids)
    while pending:
        pack_id = pending.pop(0)
        row = packs_by_id.get(pack_id, {})
        dependency_specs = row.get("dependency_specs") or []
        for dep in sorted(dependency_specs, key=lambda spec: str(spec.get("pack_id", ""))):
            dep_id = str(dep.get("pack_id", "")).strip()
            if not dep_id:
                errors.append(
                    build_error(
                        "refuse.pack.invalid_dependency_token",
                        "pack '{}' has invalid dependency token '{}'".format(
                            pack_id,
                            str(dep.get("raw", "")),
                        ),
                        "$.packs.{}.dependencies".format(pack_id),
                    )
                )
                continue
            if dep_id not in packs_by_id:
                errors.append(
                    build_error(
                        "refuse.pack.missing_dependency",
                        "pack '{}' requires missing dependency '{}'".format(pack_id, dep_id),
                        "$.packs.{}.dependencies".format(pack_id),
                    )
                )
                continue
            if dep_id not in seen:
                seen.add(dep_id)
                pending.append(dep_id)
                pending.sort()
    return seen


def resolve_packs(packs: List[dict], bundle_selection: Optional[List[str]] = None) -> Dict[str, object]:
    packs_by_id: Dict[str, dict] = {}
    errors: List[Dict[str, str]] = []
    for row in sorted(packs or [], key=lambda item: str(item.get("pack_id", ""))):
        pack_id = str(row.get("pack_id", "")).strip()
        if not pack_id:
            errors.append(build_error("refuse.pack.missing_pack_id", "pack record is missing pack_id", "$.packs"))
            continue
        packs_by_id[pack_id] = row

    selected_ids = _selected_pack_ids(packs_by_id, bundle_selection, errors)
    selected_ids = _expand_dependencies(selected_ids, packs_by_id, errors)

    if errors:
        return result_refused(
            {
                "ordered_pack_list": [],
                "pack_count": len(selected_ids),
            },
            errors,
        )

    outgoing: Dict[str, Set[str]] = {pack_id: set() for pack_id in sorted(selected_ids)}
    indegree: Dict[str, int] = {pack_id: 0 for pack_id in sorted(selected_ids)}

    for pack_id in sorted(selected_ids):
        row = packs_by_id.get(pack_id, {})
        dependency_specs = row.get("dependency_specs") or []
        for spec in sorted(dependency_specs, key=lambda item: str(item.get("pack_id", ""))):
            dep_id = str(spec.get("pack_id", "")).strip()
            req_version = str(spec.get("required_version", "")).strip()
            if dep_id not in selected_ids:
                errors.append(
                    build_error(
                        "refuse.pack.missing_dependency",
                        "pack '{}' requires missing dependency '{}'".format(pack_id, dep_id),
                        "$.packs.{}.dependencies".format(pack_id),
                    )
                )
                continue
            dep_version = str((packs_by_id.get(dep_id) or {}).get("version", "")).strip()
            if req_version and dep_version != req_version:
                errors.append(
                    build_error(
                        "refuse.pack.version_incompatibility",
                        "pack '{}' requires '{}' at version '{}' but found '{}'".format(
                            pack_id,
                            dep_id,
                            req_version,
                            dep_version or "unknown",
                        ),
                        "$.packs.{}.dependencies".format(pack_id),
                    )
                )
                continue
            if pack_id not in outgoing[dep_id]:
                outgoing[dep_id].add(pack_id)
                indegree[pack_id] += 1

    if errors:
        return result_refused(
            {
                "ordered_pack_list": [],
                "pack_count": len(selected_ids),
            },
            errors,
        )

    ready = sorted([pack_id for pack_id, deg in indegree.items() if deg == 0])
    ordered: List[str] = []
    while ready:
        current = ready.pop(0)
        ordered.append(current)
        for neighbor in sorted(outgoing.get(current, set())):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                ready.append(neighbor)
        ready = sorted(set(ready))

    if len(ordered) != len(selected_ids):
        remaining = sorted(pack_id for pack_id in selected_ids if pack_id not in set(ordered))
        return result_refused(
            {
                "ordered_pack_list": [],
                "pack_count": len(selected_ids),
            },
            [
                build_error(
                    "refuse.pack.circular_dependency",
                    "circular dependency detected among packs: {}".format(",".join(remaining)),
                    "$.packs",
                )
            ],
        )

    ordered_rows = [packs_by_id[pack_id] for pack_id in ordered]
    return result_complete(
        {
            "ordered_pack_list": ordered_rows,
            "ordered_pack_ids": ordered,
            "pack_count": len(ordered_rows),
        }
    )
