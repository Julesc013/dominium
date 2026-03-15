import os

from tools.release.archive_policy_common import DEFAULT_RELEASE_ID
from tools.xstack.testx.tests.archive_policy_testlib import load_json, prepare_fixture_bundle, rerun_archive


def run(repo_root: str) -> dict:
    fixture = prepare_fixture_bundle(repo_root, "history_preserved")
    first = load_json(fixture["archive_record_path"])
    history_rel = first["extensions"]["release_index_history_rel"]
    history_path = os.path.join(fixture["archive_root"], history_rel.replace("/", os.sep))
    assert os.path.isfile(history_path)
    initial_hash = first["release_index_hash"]
    second = rerun_archive(repo_root, fixture["bundle_root"], release_id=DEFAULT_RELEASE_ID, write_offline_bundle=False)
    assert second["archive_record"]["release_index_hash"] == initial_hash
    assert second["release_index_history_rel"] == history_rel
    assert os.path.isfile(history_path)
    return {
        "status": "pass",
        "message": "release index history is preserved and reused without overwrite for identical releases",
    }
