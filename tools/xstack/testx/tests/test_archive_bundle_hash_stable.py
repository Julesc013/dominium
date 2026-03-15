from tools.release.archive_policy_common import DEFAULT_RELEASE_ID
from tools.xstack.testx.tests.archive_policy_testlib import prepare_fixture_bundle, rerun_archive


def run(repo_root: str) -> dict:
    fixture = prepare_fixture_bundle(repo_root, "bundle_hash_stable")
    first = rerun_archive(repo_root, fixture["bundle_root"], release_id=DEFAULT_RELEASE_ID, write_offline_bundle=True)
    second = rerun_archive(repo_root, fixture["bundle_root"], release_id=DEFAULT_RELEASE_ID, write_offline_bundle=True)
    assert first["offline_bundle"]["bundle_hash"] == second["offline_bundle"]["bundle_hash"]
    return {
        "status": "pass",
        "message": "offline archive bundle hash is stable across identical archive runs",
    }
