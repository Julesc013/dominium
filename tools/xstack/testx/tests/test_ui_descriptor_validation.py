"""FAST test: UI window descriptors validate against schemas/ui_window.schema.json."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.ui.descriptor.validation"
TEST_TAGS = ["smoke", "schema", "ui"]


def _find_descriptor_paths(repo_root: str):
    roots = [
        os.path.join(repo_root, "packs"),
        os.path.join(repo_root, "tools", "xstack", "testdata", "packs"),
    ]
    out = []
    for root in roots:
        if not os.path.isdir(root):
            continue
        for walk_root, _dirs, files in os.walk(root):
            if os.path.basename(walk_root) != "ui":
                continue
            for name in sorted(files):
                if not name.startswith("window.") or not name.endswith(".json"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = abs_path[len(repo_root) + 1 :].replace("\\", "/")
                out.append((rel_path, abs_path))
    return sorted(set(out), key=lambda row: row[0])


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.ui_host import validate_ui_window_descriptor

    descriptor_paths = _find_descriptor_paths(repo_root)
    if not descriptor_paths:
        return {"status": "fail", "message": "no ui/window.*.json descriptors were discovered"}

    for rel_path, abs_path in descriptor_paths:
        payload = _load_json(abs_path)
        if not isinstance(payload, dict):
            return {"status": "fail", "message": "descriptor '{}' root must be object".format(rel_path)}
        result = validate_ui_window_descriptor(repo_root=repo_root, payload=payload)
        if not bool(result.get("valid", False)):
            return {
                "status": "fail",
                "message": "descriptor '{}' failed schema validation".format(rel_path),
            }

    return {
        "status": "pass",
        "message": "validated {} ui window descriptors".format(len(descriptor_paths)),
    }
