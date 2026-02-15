"""STRICT test: SRZ hybrid resync path is deterministic for missing and available snapshot cases."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.srz_hybrid.resync_snapshot_stub"
TEST_TAGS = ["strict", "net", "session", "srz"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.net.policies.policy_srz_hybrid import prepare_hybrid_baseline, request_hybrid_resync
    from tools.xstack.testx.tests.net_hybrid_testlib import clone_runtime, prepare_hybrid_runtime_fixture

    fixture = prepare_hybrid_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.srz_hybrid.resync",
        client_peer_id="peer.client.hybrid.alpha",
    )
    runtime = clone_runtime(fixture)

    pre_a = request_hybrid_resync(
        repo_root=repo_root,
        runtime=runtime,
        peer_id="peer.client.hybrid.alpha",
        snapshot_id="",
    )
    pre_b = request_hybrid_resync(
        repo_root=repo_root,
        runtime=runtime,
        peer_id="peer.client.hybrid.alpha",
        snapshot_id="",
    )
    if str(pre_a.get("result", "")) != "refused" or str(pre_b.get("result", "")) != "refused":
        return {"status": "fail", "message": "resync without snapshots must refuse deterministically"}
    pre_reason = str((pre_a.get("refusal") or {}).get("reason_code", ""))
    if pre_reason != "refusal.net.resync_required":
        return {"status": "fail", "message": "missing snapshot refusal must use refusal.net.resync_required"}
    if dict(pre_a.get("refusal") or {}) != dict(pre_b.get("refusal") or {}):
        return {"status": "fail", "message": "missing snapshot refusal payload changed across identical calls"}

    baseline = prepare_hybrid_baseline(repo_root=repo_root, runtime=runtime)
    if str(baseline.get("result", "")) != "complete":
        return {"status": "fail", "message": "baseline preparation failed before hybrid resync check"}
    snapshot_id = str((baseline.get("snapshot") or {}).get("snapshot_id", ""))
    if not snapshot_id:
        return {"status": "fail", "message": "baseline snapshot_id missing before hybrid resync check"}

    post = request_hybrid_resync(
        repo_root=repo_root,
        runtime=runtime,
        peer_id="peer.client.hybrid.alpha",
        snapshot_id=snapshot_id,
    )
    if str(post.get("result", "")) != "complete":
        reason = str((post.get("refusal") or {}).get("reason_code", ""))
        return {"status": "fail", "message": "hybrid resync with available snapshot refused ({})".format(reason)}
    if str(((post.get("snapshot") or {}).get("snapshot_id", ""))) != snapshot_id:
        return {"status": "fail", "message": "hybrid resync returned unexpected snapshot_id"}
    return {"status": "pass", "message": "srz hybrid resync deterministic behavior check passed"}

