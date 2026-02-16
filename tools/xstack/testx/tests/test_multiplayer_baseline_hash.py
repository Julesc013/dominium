"""STRICT regression lock: multiplayer baseline hashes and fingerprints remain stable."""

from __future__ import annotations

import json
import os
import subprocess
import sys


TEST_ID = "testx.regression.multiplayer_baseline_hash"
TEST_TAGS = ["strict", "regression", "net", "multiplayer", "security"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def _fingerprint_hashes(repo_root: str):
    from tools.xstack.compatx.canonical_json import canonical_sha256
    from tools.xstack.testx.tests.net_anti_cheat_testlib import apply_anti_cheat_policy
    from tools.xstack.testx.tests.net_authoritative_testlib import clone_runtime, prepare_authoritative_runtime_fixture
    from tools.xstack.testx.tests.test_ac_adversarial_detect_only import _run_cases as run_detect_cases
    from tools.xstack.testx.tests.test_ac_adversarial_rank_strict import _run_cases as run_rank_cases

    fixture = prepare_authoritative_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.regression.multiplayer.ac_fingerprint",
        client_peer_id="peer.client.alpha",
    )

    runtime_detect = clone_runtime(fixture)
    ok, err = apply_anti_cheat_policy(runtime_detect, dict(fixture.get("payloads") or {}), "policy.ac.detect_only")
    if not ok:
        return {}, err
    run_detect_cases(repo_root=repo_root, runtime=runtime_detect)
    detect_events = [
        str((row or {}).get("deterministic_fingerprint", ""))
        for row in sorted((runtime_detect.get("server") or {}).get("anti_cheat_events") or [], key=lambda row: str((row or {}).get("event_id", "")))
    ]

    runtime_rank = clone_runtime(fixture)
    ok, err = apply_anti_cheat_policy(runtime_rank, dict(fixture.get("payloads") or {}), "policy.ac.rank_strict")
    if not ok:
        return {}, err
    run_rank_cases(repo_root=repo_root, runtime=runtime_rank)
    rank_events = [
        str((row or {}).get("deterministic_fingerprint", ""))
        for row in sorted((runtime_rank.get("server") or {}).get("anti_cheat_events") or [], key=lambda row: str((row or {}).get("event_id", "")))
    ]
    rank_actions = [
        str((row or {}).get("deterministic_fingerprint", ""))
        for row in sorted((runtime_rank.get("server") or {}).get("anti_cheat_enforcement_actions") or [], key=lambda row: str((row or {}).get("action_id", "")))
    ]
    return {
        "detect_only_event_fingerprint_hash": canonical_sha256(detect_events),
        "rank_strict_event_fingerprint_hash": canonical_sha256(rank_events),
        "rank_strict_action_fingerprint_hash": canonical_sha256(rank_actions),
    }, ""


def _matrix_hash(repo_root: str):
    tool = os.path.join(repo_root, "tools", "net", "tool_handshake_matrix_report.py")
    proc = subprocess.run(
        [sys.executable, tool, "--repo-root", repo_root],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    if int(proc.returncode) != 0:
        return "", "handshake matrix tool failed"
    try:
        payload = json.loads(str(proc.stdout or "{}"))
    except ValueError:
        return "", "handshake matrix tool output was not valid JSON"
    return str(payload.get("matrix_hash", "")), ""


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.net_mp9_testlib import (
        run_authoritative_full_stack,
        run_hybrid_full_stack,
        run_lockstep_full_stack,
    )

    baseline = _load_json(os.path.join(repo_root, "data", "regression", "multiplayer_baseline.json"))
    lockstep = run_lockstep_full_stack(
        repo_root=repo_root,
        save_id="save.testx.regression.multiplayer.lockstep",
        ticks=4,
        disorder_profile_id="disorder.reorder_light",
        induce_divergence_tick=2,
    )
    authoritative = run_authoritative_full_stack(
        repo_root=repo_root,
        save_id="save.testx.regression.multiplayer.authoritative",
        ticks=4,
        disorder_profile_id="disorder.reorder_light",
    )
    hybrid = run_hybrid_full_stack(
        repo_root=repo_root,
        save_id="save.testx.regression.multiplayer.hybrid",
        ticks=4,
        disorder_profile_id="disorder.reorder_light",
    )
    for row in (lockstep, authoritative, hybrid):
        if str(row.get("result", "")) != "complete":
            return {"status": "fail", "message": "multiplayer baseline scenario refused unexpectedly"}

    expected = dict(baseline.get("policy_baselines") or {})
    actual = {
        "policy.net.lockstep": str(lockstep.get("final_composite_hash", "")),
        "policy.net.server_authoritative": str(authoritative.get("final_composite_hash", "")),
        "policy.net.srz_hybrid": str(hybrid.get("final_composite_hash", "")),
    }
    for policy_id in sorted(actual.keys()):
        expected_hash = str(((expected.get(policy_id) or {}).get("final_composite_hash", "")))
        if str(actual.get(policy_id, "")) != expected_hash:
            return {"status": "fail", "message": "multiplayer baseline final hash mismatch for '{}'".format(policy_id)}

    matrix_hash, err = _matrix_hash(repo_root)
    if err:
        return {"status": "fail", "message": err}
    if matrix_hash != str(baseline.get("ranked_handshake_matrix_hash", "")):
        return {"status": "fail", "message": "ranked handshake matrix hash drifted from multiplayer baseline"}

    fp_hashes, err = _fingerprint_hashes(repo_root)
    if err:
        return {"status": "fail", "message": err}
    expected_fp = dict(baseline.get("anti_cheat_fingerprint_hashes") or {})
    for key in sorted(fp_hashes.keys()):
        if str(fp_hashes.get(key, "")) != str(expected_fp.get(key, "")):
            return {"status": "fail", "message": "anti-cheat fingerprint baseline mismatch for '{}'".format(key)}

    return {"status": "pass", "message": "multiplayer regression lock baseline hashes are stable"}

