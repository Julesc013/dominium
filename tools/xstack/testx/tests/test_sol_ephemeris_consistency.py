"""FAST test: compiled Sol ephemeris registry remains structurally consistent and deterministic."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.data.sol_ephemeris_consistency"
TEST_TAGS = ["smoke", "registry", "session"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def _sorted_supported_bodies(repo_root: str):
    payload = _load_json(os.path.join(repo_root, "packs", "source", "org.dominium.sol.spice", "data", "ephemeris_source.json"))
    return sorted(set(str(item).strip() for item in (payload.get("supported_bodies") or []) if str(item).strip()))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.registry_compile.compiler import compile_bundle

    first = compile_bundle(
        repo_root=repo_root,
        bundle_id="bundle.base.lab",
        out_dir_rel="build/registries",
        lockfile_out_rel="build/lockfile.json",
        packs_root_rel="packs",
        schema_repo_root=repo_root,
        use_cache=True,
    )
    if first.get("result") != "complete":
        return {"status": "fail", "message": "initial compile failed for ephemeris consistency test"}
    second = compile_bundle(
        repo_root=repo_root,
        bundle_id="bundle.base.lab",
        out_dir_rel="build/registries",
        lockfile_out_rel="build/lockfile.json",
        packs_root_rel="packs",
        schema_repo_root=repo_root,
        use_cache=True,
    )
    if second.get("result") != "complete":
        return {"status": "fail", "message": "repeat compile failed for ephemeris consistency test"}
    if not bool(second.get("cache_hit", False)):
        return {"status": "fail", "message": "repeat compile expected cache hit for unchanged Sol ephemeris inputs"}

    lockfile = _load_json(os.path.join(repo_root, "build", "lockfile.json"))
    ephemeris_registry = _load_json(os.path.join(repo_root, "build", "registries", "ephemeris.registry.json"))
    expected_hash = str((lockfile.get("registries") or {}).get("ephemeris_registry_hash", "")).strip()
    actual_hash = str(ephemeris_registry.get("registry_hash", "")).strip()
    if not expected_hash or expected_hash != actual_hash:
        return {"status": "fail", "message": "lockfile ephemeris_registry_hash mismatch"}

    tables = list(ephemeris_registry.get("tables") or [])
    if not tables:
        return {"status": "fail", "message": "ephemeris registry has no tables"}
    table_by_body = {}
    for row in tables:
        if not isinstance(row, dict):
            return {"status": "fail", "message": "ephemeris table row must be object"}
        body_id = str(row.get("body_id", "")).strip()
        if not body_id:
            return {"status": "fail", "message": "ephemeris table row missing body_id"}
        table_by_body[body_id] = row

    missing = [body for body in _sorted_supported_bodies(repo_root) if body not in table_by_body]
    if missing:
        return {"status": "fail", "message": "ephemeris registry missing supported bodies: {}".format(", ".join(missing))}

    for body_id in sorted(table_by_body.keys()):
        row = table_by_body[body_id]
        time_range = dict(row.get("time_range") or {})
        step_ticks = int(time_range.get("step_ticks", 0) or 0)
        if step_ticks < 1:
            return {"status": "fail", "message": "ephemeris table '{}' has invalid step_ticks".format(body_id)}
        samples = list(row.get("samples") or [])
        if not samples:
            return {"status": "fail", "message": "ephemeris table '{}' has no samples".format(body_id)}
        ticks = []
        for sample in samples:
            if not isinstance(sample, dict):
                return {"status": "fail", "message": "ephemeris sample for '{}' must be object".format(body_id)}
            position = sample.get("position_mm")
            if not isinstance(position, dict):
                return {"status": "fail", "message": "ephemeris sample for '{}' missing position_mm object".format(body_id)}
            for axis in ("x", "y", "z"):
                if not isinstance(position.get(axis), int):
                    return {"status": "fail", "message": "ephemeris sample '{}' axis '{}' must be integer".format(body_id, axis)}
            ticks.append(int(sample.get("tick", 0) or 0))
        if ticks != sorted(ticks):
            return {"status": "fail", "message": "ephemeris sample ticks are not sorted for '{}'".format(body_id)}
        if len(ticks) > 1 and any((ticks[i] - ticks[i - 1]) != step_ticks for i in range(1, len(ticks))):
            return {"status": "fail", "message": "ephemeris sample spacing mismatch for '{}'".format(body_id)}

    return {"status": "pass", "message": "Sol ephemeris registry consistency checks passed"}
