from tools.xstack.testx.tests.archive_policy_testlib import build_report, ensure_assets, load_json, report_json_path


def run(repo_root: str) -> dict:
    ensure_assets(repo_root)
    report = build_report(repo_root)
    report_payload = load_json(report_json_path(repo_root))
    assert report_payload["result"] == "complete"
    assert report["archive_record_hash"] == report_payload["archive_record_hash"]
    assert len(report_payload["archive_record_hash"]) == 64
    assert len(report_payload["release_index_hash"]) == 64
    assert len(report_payload["release_manifest_hash"]) == 64
    assert len(report_payload["component_graph_hash"]) == 64
    assert len(report_payload["governance_profile_hash"]) == 64
    assert report_payload["mirror_list"]
    return {
        "status": "pass",
        "message": "archive record report exposes the required immutable release hashes",
    }
