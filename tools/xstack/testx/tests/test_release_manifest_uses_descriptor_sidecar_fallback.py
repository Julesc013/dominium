"""FAST test: release manifest verification falls back to descriptor sidecars."""

from __future__ import annotations

import json
import os


TEST_ID = "test_release_manifest_uses_descriptor_sidecar_fallback"
TEST_TAGS = ["fast", "release", "verification"]


def _write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _write_json(path: str, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def run(repo_root: str):
    from tools.xstack.testx.tests.release1_testlib import _descriptor_payload, build_manifest_payload, release_fixture
    from release import verify_release_manifest, write_release_manifest

    with release_fixture() as dist_root:
        client_path = os.path.join(dist_root, "bin", "client")
        sidecar_path = client_path + ".descriptor.json"
        _write_json(sidecar_path, _descriptor_payload("client"))
        _write(
            client_path,
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "raise SystemExit(1)",
                    "",
                ]
            ),
        )
        payload = build_manifest_payload(dist_root)
        manifest_path = os.path.join(dist_root, "manifests", "release_manifest.json")
        write_release_manifest(dist_root, payload, manifest_path=manifest_path)
        report = verify_release_manifest(dist_root, manifest_path, repo_root=repo_root)

    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "verification failed even though descriptor sidecar was present"}
    codes = {str(dict(row or {}).get("code", "")).strip() for row in list(report.get("errors") or [])}
    if "refusal.release_manifest.descriptor_unavailable" in codes:
        return {"status": "fail", "message": "descriptor sidecar fallback did not suppress descriptor_unavailable"}
    return {"status": "pass", "message": "release manifest verifier falls back to descriptor sidecars"}
