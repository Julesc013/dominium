"""FAST test: policy registries compile deterministically and include default lab policies."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.registry.policy_determinism"
TEST_TAGS = ["smoke", "registry", "pack"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def _policy_ids(payload: dict, key: str):
    out = []
    rows = payload.get(key)
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        token = str(row.get("policy_id", "")).strip()
        if token:
            out.append(token)
    return sorted(set(out))


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
        use_cache=False,
    )
    second = compile_bundle(
        repo_root=repo_root,
        bundle_id="bundle.base.lab",
        out_dir_rel="build/registries",
        lockfile_out_rel="build/lockfile.json",
        packs_root_rel="packs",
        schema_repo_root=repo_root,
        use_cache=False,
    )
    if first.get("result") != "complete" or second.get("result") != "complete":
        return {"status": "fail", "message": "policy determinism compile failed"}

    hashes1 = dict(first.get("registry_hashes") or {})
    hashes2 = dict(second.get("registry_hashes") or {})
    for key in (
        "activation_policy_registry_hash",
        "budget_policy_registry_hash",
        "fidelity_policy_registry_hash",
    ):
        if str(hashes1.get(key, "")) != str(hashes2.get(key, "")):
            return {"status": "fail", "message": "policy registry hash drift for '{}'".format(key)}

    activation_payload = _load_json(os.path.join(repo_root, "build", "registries", "activation_policy.registry.json"))
    budget_payload = _load_json(os.path.join(repo_root, "build", "registries", "budget_policy.registry.json"))
    fidelity_payload = _load_json(os.path.join(repo_root, "build", "registries", "fidelity_policy.registry.json"))

    activation_ids = _policy_ids(activation_payload, "activation_policies")
    budget_ids = _policy_ids(budget_payload, "budget_policies")
    fidelity_ids = _policy_ids(fidelity_payload, "fidelity_policies")
    if "policy.activation.default_lab" not in activation_ids:
        return {"status": "fail", "message": "missing policy.activation.default_lab in activation registry"}
    if "policy.budget.default_lab" not in budget_ids:
        return {"status": "fail", "message": "missing policy.budget.default_lab in budget registry"}
    if "policy.fidelity.default_lab" not in fidelity_ids:
        return {"status": "fail", "message": "missing policy.fidelity.default_lab in fidelity registry"}

    return {"status": "pass", "message": "policy registry determinism checks passed"}
