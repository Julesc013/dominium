"""FAST test: Ω-10 expected artifact checklist exposes the frozen release placeholders."""

from __future__ import annotations


TEST_ID = "test_expected_artifacts_list_valid"
TEST_TAGS = ["fast", "omega", "dist", "release"]


def run(repo_root: str):
    from tools.release.dist_final_common import DEFAULT_RELEASE_ID
    from tools.xstack.testx.tests.dist_final_testlib import committed_expected_artifacts

    payload = committed_expected_artifacts(repo_root)
    if str(payload.get("release_id", "")).strip() != DEFAULT_RELEASE_ID:
        return {"status": "fail", "message": "expected artifact checklist release_id drifted"}

    profile_ids = {
        str((row or {}).get("install_profile_id", "")).strip()
        for row in list(payload.get("install_profiles") or [])
        if str((row or {}).get("install_profile_id", "")).strip()
    }
    for required_id in ("install.profile.full", "install.profile.server", "install.profile.tools"):
        if required_id not in profile_ids:
            return {"status": "fail", "message": "missing install profile '{}'".format(required_id)}

    outputs = list(payload.get("expected_outputs") or [])
    output_ids = {
        str((row or {}).get("artifact_id", "")).strip()
        for row in outputs
        if str((row or {}).get("artifact_id", "")).strip()
    }
    for required_id in (
        "bundle.full.win64.root",
        "bundle.full.win64.release_manifest",
        "bundle.full.win64.release_index",
        "publication.archive.record",
        "offline_archive.bundle",
        "signoff.machine",
    ):
        if required_id not in output_ids:
            return {"status": "fail", "message": "missing expected output '{}'".format(required_id)}
    for row in outputs:
        if str((row or {}).get("sha256", "")) != "":
            return {"status": "fail", "message": "Ω-10 expected outputs must leave sha256 placeholders blank"}
    return {"status": "pass", "message": "Ω-10 expected artifact checklist exposes the frozen placeholders"}
