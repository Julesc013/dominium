"""FAST test: the Sol pin pack stays within the bounded minimal-data envelope."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_pin_pack_size_under_threshold"
TEST_TAGS = ["fast", "sol", "pack", "size"]


def run(repo_root: str):
    scripts_ci = os.path.join(repo_root, "scripts", "ci")
    for candidate in (repo_root, scripts_ci):
        if candidate not in sys.path:
            sys.path.insert(0, candidate)
    import check_repox_rules as repox

    patch_path = os.path.join(repo_root, repox.SOL_PIN_PATCHES_REL.replace("/", os.sep))
    if not os.path.isfile(patch_path):
        return {"status": "fail", "message": "missing Sol pin patch document"}
    with open(patch_path, "r", encoding="utf-8") as handle:
        patch_payload = json.load(handle)
    patch_count = len(list(dict(patch_payload).get("property_patches") or []))
    total_bytes = sum(
        int(os.path.getsize(os.path.join(repo_root, rel.replace("/", os.sep))))
        for rel in (
            repox.SOL_PIN_PACK_MANIFEST_REL,
            repox.SOL_PIN_OVERLAY_LAYER_REL,
            repox.SOL_PIN_PATCHES_REL,
            repox.SOL_PIN_DOC_REL,
            repox.SOL_PIN_VERIFY_TOOL_REL,
        )
        if os.path.isfile(os.path.join(repo_root, rel.replace("/", os.sep)))
    )
    if patch_count > repox.SOL_PIN_MAX_PATCH_COUNT:
        return {"status": "fail", "message": "Sol pin patch count {} exceeds max {}".format(patch_count, repox.SOL_PIN_MAX_PATCH_COUNT)}
    if total_bytes > repox.SOL_PIN_MAX_TOTAL_BYTES:
        return {"status": "fail", "message": "Sol pin governed bytes {} exceed max {}".format(total_bytes, repox.SOL_PIN_MAX_TOTAL_BYTES)}
    return {"status": "pass", "message": "Sol pin pack remains inside the bounded minimal-data envelope"}

