"""FAST test: EMB-0 lens profiles remain entitlement-gated."""

from __future__ import annotations

import sys


TEST_ID = "test_lens_switch_profile_gated"
TEST_TAGS = ["fast", "embodiment", "lens", "epistemic"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from embodiment import resolve_authorized_lens_profile
    from tools.xstack.testx.tests.emb0_testlib import authority_context

    allowed = resolve_authorized_lens_profile(
        requested_lens_profile_id="lens.freecam",
        authority_context=authority_context(
            ["entitlement.control.camera", "lens.nondiegetic.access"],
            privilege_level="operator",
        ),
    )
    allowed_repeat = resolve_authorized_lens_profile(
        requested_lens_profile_id="lens.freecam",
        authority_context=authority_context(
            ["entitlement.control.camera", "lens.nondiegetic.access"],
            privilege_level="operator",
        ),
    )
    refused = resolve_authorized_lens_profile(
        requested_lens_profile_id="lens.inspect",
        authority_context=authority_context(
            ["entitlement.control.camera", "lens.nondiegetic.access"],
            privilege_level="observer",
        ),
    )
    if str(allowed.get("result", "")) != "complete":
        return {"status": "fail", "message": "freecam lens profile should authorize for dev-style entitlements"}
    if str(refused.get("result", "")) != "refused":
        return {"status": "fail", "message": "inspect lens profile should refuse without observer truth and override entitlements"}
    if str((dict(refused.get("details") or {})).get("lens_profile_id", "")) != "lens.inspect":
        return {"status": "fail", "message": "inspect lens refusal must name lens.inspect"}
    if dict(allowed) != dict(allowed_repeat):
        return {"status": "fail", "message": "authorized lens profile resolution must be deterministic"}
    return {"status": "pass", "message": "EMB-0 lens profile gating check passed"}
