import os

from tools.release.archive_policy_common import DEFAULT_RELEASE_ID
from tools.xstack.testx.tests.archive_policy_testlib import load_json, prepare_fixture_bundle, rerun_archive, write_json


def run(repo_root: str) -> dict:
    fixture = prepare_fixture_bundle(repo_root, "no_overwrite")
    release_index_path = os.path.join(fixture["bundle_root"], "manifests", "release_index.json")
    payload = load_json(release_index_path)
    payload.setdefault("extensions", {})
    payload["extensions"]["archive_policy_test_marker"] = "mutated"
    write_json(release_index_path, payload)
    try:
        rerun_archive(repo_root, fixture["bundle_root"], release_id=DEFAULT_RELEASE_ID, write_offline_bundle=False)
    except ValueError as exc:
        assert "overwrite forbidden" in str(exc)
        return {
            "status": "pass",
            "message": "archive tool refuses to overwrite a retained release-index history snapshot with different content",
        }
    raise AssertionError("archive tool must refuse release-index history overwrite")
