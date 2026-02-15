"""FAST test: deterministic dist build smoke for bundle.base.lab."""

from __future__ import annotations

import os
import sys


TEST_ID = "testx.packaging.smoke"
TEST_TAGS = ["smoke", "registry", "bundle"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.packagingx import build_dist_layout, validate_dist_layout

    out_rel = "build/dist.testx.smoke"
    built = build_dist_layout(
        repo_root=repo_root,
        bundle_id="bundle.base.lab",
        out_dir=out_rel,
        use_cache=True,
    )
    if built.get("result") != "complete":
        return {"status": "fail", "message": "packaging smoke build refused"}
    checked = validate_dist_layout(repo_root=repo_root, dist_root=out_rel)
    if checked.get("result") != "complete":
        return {"status": "fail", "message": "packaging smoke validation refused"}

    required = (
        "bin",
        "packs",
        "bundles",
        "registries",
    )
    out_abs = os.path.join(repo_root, out_rel.replace("/", os.sep))
    for rel_dir in required:
        if not os.path.isdir(os.path.join(out_abs, rel_dir)):
            return {"status": "fail", "message": "missing dist directory '{}'".format(rel_dir)}
    for rel_file in ("lockfile.json", "manifest.json"):
        if not os.path.isfile(os.path.join(out_abs, rel_file)):
            return {"status": "fail", "message": "missing dist file '{}'".format(rel_file)}

    return {
        "status": "pass",
        "message": "packaging smoke build passed (content_hash={})".format(str(checked.get("canonical_content_hash", ""))),
    }

