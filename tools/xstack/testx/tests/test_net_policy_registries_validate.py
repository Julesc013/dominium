"""FAST test: multiplayer policy registries compile and cross-link deterministically."""

from __future__ import annotations

import json
import os
import re
import sys


TEST_ID = "testx.net.policy_registries_validate"
TEST_TAGS = ["smoke", "registry", "net"]


SHA256_RE = re.compile(r"^[A-Fa-f0-9]{64}$")


def _read_json(path: str):
    try:
        return json.load(open(path, "r", encoding="utf-8")), ""
    except (OSError, ValueError):
        return {}, "invalid json"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.registry_compile.compiler import compile_bundle

    source_paths = [
        "data/registries/net_replication_policy_registry.json",
        "data/registries/net_resync_strategy_registry.json",
        "data/registries/net_server_policy_registry.json",
        "data/registries/anti_cheat_policy_registry.json",
        "data/registries/anti_cheat_module_registry.json",
    ]
    for rel in source_paths:
        payload, err = _read_json(os.path.join(repo_root, rel.replace("/", os.sep)))
        if err:
            return {"status": "fail", "message": "invalid source registry JSON '{}'".format(rel)}
        record = payload.get("record")
        if not isinstance(record, dict):
            return {"status": "fail", "message": "source registry '{}' missing record object".format(rel)}

    compile_result = compile_bundle(
        repo_root=repo_root,
        bundle_id="bundle.base.lab",
        out_dir_rel="build/registries",
        lockfile_out_rel="build/lockfile.json",
        packs_root_rel="packs",
        schema_repo_root=repo_root,
        use_cache=True,
    )
    if compile_result.get("result") != "complete":
        return {"status": "fail", "message": "compile_bundle failed for multiplayer registry validation"}

    expected = [
        ("build/registries/net_replication_policy.registry.json", "net_replication_policy_registry", "policies"),
        ("build/registries/net_resync_strategy.registry.json", "net_resync_strategy_registry", "strategies"),
        ("build/registries/net_server_policy.registry.json", "net_server_policy_registry", "policies"),
        ("build/registries/anti_cheat_policy.registry.json", "anti_cheat_policy_registry", "policies"),
        ("build/registries/anti_cheat_module.registry.json", "anti_cheat_module_registry", "modules"),
    ]
    payloads = {}
    for rel, schema_name, key in expected:
        payload, err = _read_json(os.path.join(repo_root, rel.replace("/", os.sep)))
        if err:
            return {"status": "fail", "message": "derived registry '{}' missing/invalid".format(rel)}
        payloads[schema_name] = payload
        from tools.xstack.compatx.validator import validate_instance

        checked = validate_instance(
            repo_root=repo_root,
            schema_name=schema_name,
            payload=payload,
            strict_top_level=True,
        )
        if not bool(checked.get("valid", False)):
            return {"status": "fail", "message": "derived registry '{}' failed schema validation".format(rel)}
        if not isinstance(payload.get(key), list):
            return {"status": "fail", "message": "derived registry '{}' missing '{}' list".format(rel, key)}
        digest = str(payload.get("registry_hash", "")).strip()
        if not SHA256_RE.fullmatch(digest):
            return {"status": "fail", "message": "derived registry '{}' has invalid registry_hash".format(rel)}

    module_ids = set(
        str(row.get("module_id", "")).strip()
        for row in payloads["anti_cheat_module_registry"].get("modules") or []
        if isinstance(row, dict)
    )
    for row in payloads["anti_cheat_policy_registry"].get("policies") or []:
        if not isinstance(row, dict):
            continue
        for module_id in row.get("modules_enabled") or []:
            if str(module_id).strip() not in module_ids:
                return {"status": "fail", "message": "anti-cheat policy references unknown module id"}
        for module_id in (row.get("default_actions") or {}).keys():
            if str(module_id).strip() not in module_ids:
                return {"status": "fail", "message": "anti-cheat default_actions references unknown module id"}

    resync_ids = set(
        str(row.get("strategy_id", "")).strip()
        for row in payloads["net_resync_strategy_registry"].get("strategies") or []
        if isinstance(row, dict)
    )
    replication_ids = set(
        str(row.get("policy_id", "")).strip()
        for row in payloads["net_replication_policy_registry"].get("policies") or []
        if isinstance(row, dict)
    )
    for row in payloads["net_replication_policy_registry"].get("policies") or []:
        if not isinstance(row, dict):
            continue
        if str(row.get("resync_strategy_id", "")).strip() not in resync_ids:
            return {"status": "fail", "message": "net policy references unknown resync strategy"}
    for row in payloads["net_resync_strategy_registry"].get("strategies") or []:
        if not isinstance(row, dict):
            continue
        for policy_id in row.get("supported_policies") or []:
            if str(policy_id).strip() not in replication_ids:
                return {"status": "fail", "message": "resync strategy references unknown replication policy"}

    anti_cheat_ids = set(
        str(row.get("policy_id", "")).strip()
        for row in payloads["anti_cheat_policy_registry"].get("policies") or []
        if isinstance(row, dict)
    )
    for row in payloads["net_server_policy_registry"].get("policies") or []:
        if not isinstance(row, dict):
            continue
        for policy_id in row.get("allowed_replication_policy_ids") or []:
            if str(policy_id).strip() not in replication_ids:
                return {"status": "fail", "message": "server policy references unknown replication policy"}
        for policy_id in row.get("allowed_anti_cheat_policy_ids") or []:
            if str(policy_id).strip() not in anti_cheat_ids:
                return {"status": "fail", "message": "server policy references unknown anti-cheat policy"}
        required_anti_cheat = str(row.get("required_anti_cheat_policy_id", "")).strip()
        if required_anti_cheat and required_anti_cheat not in anti_cheat_ids:
            return {"status": "fail", "message": "server policy required anti-cheat policy is unknown"}

    return {"status": "pass", "message": "multiplayer policy registries validate and cross-link deterministically"}
