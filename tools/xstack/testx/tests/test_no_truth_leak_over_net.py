"""STRICT test: multiplayer net policies emit perceived transport artifacts only."""

from __future__ import annotations

import json
import os
import re
import sys


TEST_ID = "testx.net.no_truth_leak_over_net"
TEST_TAGS = ["strict", "net", "session"]

_FORBIDDEN_TOP_LEVEL = {"truth_model", "universe_state", "registry_payloads", "global_state"}
_STATIC_FORBIDDEN_PATTERNS = (
    r"send\([^\n]*(universe_state|truth_model|global_state)",
    r"(universe_state|truth_model|global_state)[^\n]*(socket|packet|wire|transport)",
)


def _load_json(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, str(rel_path).replace("/", os.sep))
    return json.load(open(abs_path, "r", encoding="utf-8"))


def _check_static_surface(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        text = open(abs_path, "r", encoding="utf-8").read()
    except OSError:
        return "missing file {}".format(rel_path)
    if "schema_name=\"net_perceived_delta\"" not in text:
        return "required perceived delta schema validation missing in {}".format(rel_path)
    lines = text.splitlines()
    for line_no, line in enumerate(lines, start=1):
        lower = str(line).lower()
        if "truth_snapshot_hash" in lower:
            continue
        for pattern in _STATIC_FORBIDDEN_PATTERNS:
            if re.search(pattern, str(line), flags=re.IGNORECASE):
                return "truth-over-net pattern in {}:{}".format(rel_path, line_no)
    return ""


def _check_delta_payloads(repo_root: str, deltas: list):
    for row in sorted((dict(item) for item in (deltas or []) if isinstance(item, dict)), key=lambda item: str(item.get("perceived_delta_id", ""))):
        if any(token in row for token in _FORBIDDEN_TOP_LEVEL):
            return "delta metadata leaked forbidden truth keys"
        payload_ref = str(row.get("payload_ref", "")).strip()
        if not payload_ref:
            return "delta metadata missing payload_ref"
        payload = _load_json(repo_root, payload_ref)
        if any(token in payload for token in _FORBIDDEN_TOP_LEVEL):
            return "delta payload leaked forbidden truth keys ({})".format(payload_ref)
        replace_payload = payload.get("replace")
        if not isinstance(replace_payload, dict):
            return "delta payload missing replace object ({})".format(payload_ref)
        if any(token in replace_payload for token in _FORBIDDEN_TOP_LEVEL):
            return "replace payload leaked forbidden truth keys ({})".format(payload_ref)
    return ""


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    static_targets = (
        "src/net/policies/policy_server_authoritative.py",
        "src/net/srz/shard_coordinator.py",
    )
    for rel_path in static_targets:
        error = _check_static_surface(repo_root, rel_path)
        if error:
            return {"status": "fail", "message": error}

    from src.net.policies.policy_server_authoritative import advance_authoritative_tick
    from src.net.policies.policy_srz_hybrid import advance_hybrid_tick
    from tools.xstack.testx.tests.net_authoritative_testlib import clone_runtime as clone_authoritative_runtime
    from tools.xstack.testx.tests.net_authoritative_testlib import prepare_authoritative_runtime_fixture
    from tools.xstack.testx.tests.net_hybrid_testlib import clone_runtime as clone_hybrid_runtime
    from tools.xstack.testx.tests.net_hybrid_testlib import prepare_hybrid_runtime_fixture

    authoritative_fixture = prepare_authoritative_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.no_truth_leak.auth",
        client_peer_id="peer.client.alpha",
    )
    authoritative_runtime = clone_authoritative_runtime(authoritative_fixture)
    authoritative_step = advance_authoritative_tick(repo_root=repo_root, runtime=authoritative_runtime)
    if str(authoritative_step.get("result", "")) != "complete":
        reason = str(((authoritative_step.get("refusal") or {}).get("reason_code", "")) if isinstance(authoritative_step, dict) else "")
        return {"status": "fail", "message": "authoritative tick refused during no-leak check ({})".format(reason)}
    error = _check_delta_payloads(repo_root, authoritative_step.get("perceived_deltas") or [])
    if error:
        return {"status": "fail", "message": "authoritative perceived delta leak check failed: {}".format(error)}

    hybrid_fixture = prepare_hybrid_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.no_truth_leak.hybrid",
        client_peer_id="peer.client.hybrid.alpha",
    )
    hybrid_runtime = clone_hybrid_runtime(hybrid_fixture)
    hybrid_step = advance_hybrid_tick(repo_root=repo_root, runtime=hybrid_runtime)
    if str(hybrid_step.get("result", "")) != "complete":
        reason = str(((hybrid_step.get("refusal") or {}).get("reason_code", "")) if isinstance(hybrid_step, dict) else "")
        return {"status": "fail", "message": "srz hybrid tick refused during no-leak check ({})".format(reason)}
    error = _check_delta_payloads(repo_root, hybrid_step.get("perceived_deltas") or [])
    if error:
        return {"status": "fail", "message": "srz hybrid perceived delta leak check failed: {}".format(error)}

    return {"status": "pass", "message": "network paths remain perceived-only without truth payload leakage"}

