"""STRICT test: offline archive bundle contains all required CAS and support surfaces."""

from __future__ import annotations

import os


TEST_ID = "test_archive_contains_all_required_artifacts"
TEST_TAGS = ["strict", "omega", "archive", "contents"]


def run(repo_root: str):
    from tools.xstack.testx.tests.offline_archive_testlib import build_and_verify, load_archive_record_from_build, unpack_archive

    build_report, _verify_report = build_and_verify(repo_root, "shared")
    record = load_archive_record_from_build(build_report)
    extracted_root = unpack_archive(str(build_report.get("archive_bundle_path", "")).strip())

    required_surface_ids = {
        "worldgen.seed",
        "worldgen.snapshot",
        "universe.instance_manifest",
        "universe.snapshot",
        "gameplay.snapshot",
        "disaster.baseline",
        "ecosystem.baseline",
        "update_sim.baseline",
        "trust_strict.baseline",
        "performance.envelope_baseline",
    }
    archived_surface_ids = {str(dict(row or {}).get("surface_id", "")).strip() for row in list(record.get("bundled_support_surfaces") or [])}
    if not required_surface_ids.issubset(archived_surface_ids):
        return {"status": "fail", "message": "offline archive record is missing required support surfaces"}

    for row in list(record.get("artifacts") or []):
        cas_rel = str(dict(row or {}).get("cas_rel", "")).strip().replace("/", os.sep)
        if not cas_rel:
            return {"status": "fail", "message": "offline archive record contains artifact without cas_rel"}
        if not os.path.exists(os.path.join(extracted_root, cas_rel)):
            return {"status": "fail", "message": "offline archive bundle is missing '{}'".format(cas_rel.replace("\\", "/"))}
    return {"status": "pass", "message": "offline archive bundle contains all required CAS and support surfaces"}
