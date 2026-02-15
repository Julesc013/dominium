"""Typed contribution parsing for Pack System v1 pack manifests."""

from __future__ import annotations

import os
import json
from typing import Dict, List

from tools.xstack.pack_loader.constants import SUPPORTED_CONTRIBUTION_TYPES
from tools.xstack.pack_loader.errors import build_error, result_complete, result_refused


def _norm(path: str) -> str:
    return path.replace("\\", "/")


def _safe_contrib_path(pack_dir: str, rel_path: str) -> str:
    joined = os.path.normpath(os.path.join(pack_dir, rel_path))
    pack_dir_norm = os.path.normpath(pack_dir)
    try:
        common = os.path.commonpath([pack_dir_norm, joined])
    except ValueError:
        return ""
    if common != pack_dir_norm:
        return ""
    return joined


def parse_contributions(repo_root: str, packs: List[dict]) -> Dict[str, object]:
    errors: List[Dict[str, str]] = []
    rows: List[dict] = []
    seen_ids: Dict[str, dict] = {}
    supported = set(SUPPORTED_CONTRIBUTION_TYPES)

    for pack in sorted(packs or [], key=lambda row: str(row.get("pack_id", ""))):
        pack_id = str(pack.get("pack_id", "")).strip()
        pack_dir = str(pack.get("pack_dir", "")).strip()
        manifest = pack.get("manifest") or {}
        contributions = manifest.get("contributions") or []
        if not isinstance(contributions, list):
            errors.append(
                build_error(
                    "refuse.pack_contrib.invalid_contributions_shape",
                    "pack '{}' has non-list contributions field".format(pack_id),
                    "$.packs.{}.contributions".format(pack_id),
                )
            )
            continue

        for item in contributions:
            if not isinstance(item, dict):
                errors.append(
                    build_error(
                        "refuse.pack_contrib.invalid_entry",
                        "pack '{}' contribution entry must be an object".format(pack_id),
                        "$.packs.{}.contributions".format(pack_id),
                    )
                )
                continue
            contrib_type = str(item.get("type", "")).strip()
            contrib_id = str(item.get("id", "")).strip()
            contrib_path = str(item.get("path", "")).strip()

            if contrib_type not in supported:
                errors.append(
                    build_error(
                        "refuse.pack_contrib.unsupported_type",
                        "pack '{}' contribution '{}' has unsupported type '{}'".format(
                            pack_id,
                            contrib_id or "<missing_id>",
                            contrib_type or "<missing_type>",
                        ),
                        "$.packs.{}.contributions".format(pack_id),
                    )
                )
                continue

            if not contrib_id:
                errors.append(
                    build_error(
                        "refuse.pack_contrib.missing_id",
                        "pack '{}' has contribution with missing id".format(pack_id),
                        "$.packs.{}.contributions".format(pack_id),
                    )
                )
                continue

            existing = seen_ids.get(contrib_id)
            if existing:
                errors.append(
                    build_error(
                        "refuse.pack_contrib.duplicate_id",
                        "duplicate contribution id '{}' in packs '{}' and '{}'".format(
                            contrib_id,
                            str(existing.get("pack_id", "")),
                            pack_id,
                        ),
                        "$.packs.{}.contributions".format(pack_id),
                    )
                )
                continue

            if not contrib_path:
                errors.append(
                    build_error(
                        "refuse.pack_contrib.missing_path",
                        "pack '{}' contribution '{}' is missing path".format(pack_id, contrib_id),
                        "$.packs.{}.contributions".format(pack_id),
                    )
                )
                continue

            resolved = _safe_contrib_path(pack_dir, contrib_path)
            if not resolved:
                errors.append(
                    build_error(
                        "refuse.pack_contrib.path_outside_pack",
                        "pack '{}' contribution '{}' path escapes pack directory".format(pack_id, contrib_id),
                        "$.packs.{}.contributions".format(pack_id),
                    )
                )
                continue
            if not os.path.isfile(resolved):
                errors.append(
                    build_error(
                        "refuse.pack_contrib.missing_path",
                        "pack '{}' contribution '{}' references missing path '{}'".format(
                            pack_id,
                            contrib_id,
                            _norm(os.path.relpath(resolved, repo_root)),
                        ),
                        "$.packs.{}.contributions".format(pack_id),
                    )
                )
                continue

            try:
                payload = json.load(open(resolved, "r", encoding="utf-8"))
            except (OSError, ValueError):
                errors.append(
                    build_error(
                        "refuse.pack_contrib.invalid_payload_json",
                        "pack '{}' contribution '{}' payload must be valid JSON at '{}'".format(
                            pack_id,
                            contrib_id,
                            _norm(os.path.relpath(resolved, repo_root)),
                        ),
                        "$.packs.{}.contributions".format(pack_id),
                    )
                )
                continue

            row = {
                "pack_id": pack_id,
                "pack_category": str(pack.get("category", "")).strip(),
                "contrib_type": contrib_type,
                "id": contrib_id,
                "path": _norm(os.path.relpath(resolved, repo_root)),
                "payload": payload,
            }
            rows.append(row)
            seen_ids[contrib_id] = row

    if errors:
        return result_refused({"contribution_count": len(rows), "contributions": []}, errors)

    rows = sorted(
        rows,
        key=lambda row: (
            str(row.get("contrib_type", "")),
            str(row.get("id", "")),
            str(row.get("pack_id", "")),
        ),
    )
    return result_complete(
        {
            "contribution_count": len(rows),
            "contributions": rows,
        }
    )
