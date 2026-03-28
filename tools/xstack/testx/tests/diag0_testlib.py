"""DIAG-0 TestX helpers."""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile


FIXTURE_CONTRACT_BUNDLE_HASH = "c" * 64
FIXTURE_OVERLAY_MANIFEST_HASH = "d" * 64


def ensure_repo_on_path(repo_root: str) -> None:
    token = os.path.abspath(str(repo_root))
    if token not in sys.path:
        sys.path.insert(0, token)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)


def make_temp_dir(prefix: str = "diag0_") -> str:
    return tempfile.mkdtemp(prefix=prefix)


def cleanup_temp_dir(path: str) -> None:
    if path and os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("expected JSON object in {}".format(path))
    return payload


def load_jsonl(path: str) -> list[dict]:
    rows = []
    if not os.path.isfile(path):
        return rows
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            text = str(line).strip()
            if not text:
                continue
            payload = json.loads(text)
            if isinstance(payload, dict):
                rows.append(payload)
    return rows


def _sample_contract_bundle_payload() -> dict:
    return {
        "schema_version": "1.0.0",
        "contract_worldgen_refinement_version": "contract.worldgen.refinement.v1",
        "contract_overlay_merge_version": "contract.overlay.merge.v1",
        "contract_logic_eval_version": "contract.logic.eval.v1",
        "contract_proc_capsule_version": "contract.proc.capsule.v1",
        "contract_sys_collapse_version": "contract.sys.collapse.v1",
        "contract_geo_metric_version": "contract.geo.metric.v1",
        "contract_geo_projection_version": "contract.geo.projection.v1",
        "contract_geo_partition_version": "contract.geo.partition.v1",
        "contract_appshell_lifecycle_version": "contract.appshell.lifecycle.v1",
        "deterministic_fingerprint": FIXTURE_CONTRACT_BUNDLE_HASH,
        "extensions": {},
    }


def _sample_session_spec_payload(*, pack_lock_hash: str, semantic_contract_registry_hash: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "session_template_id": "session.mvp_default",
        "pack_lock_hash": str(pack_lock_hash).strip(),
        "contract_bundle_hash": FIXTURE_CONTRACT_BUNDLE_HASH,
        "semantic_contract_registry_hash": str(semantic_contract_registry_hash).strip(),
        "selected_seed": "12345",
        "save_id": "save.diag0.fixture",
        "extensions": {},
    }


def _sample_run_manifest_payload(*, build_id: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "manifest_id": "run.diag0.fixture",
        "seed": "12345",
        "session_template_id": "session.mvp_default",
        "overlay_manifest_hash": FIXTURE_OVERLAY_MANIFEST_HASH,
        "processes": [
            {
                "product_id": "client",
                "binary_hash": str(build_id).strip(),
                "args_hash": "a" * 64,
                "pid_stub": "pid.client",
            },
            {
                "product_id": "server",
                "binary_hash": str(build_id).strip(),
                "args_hash": "b" * 64,
                "pid_stub": "pid.server",
            },
        ],
        "extensions": {},
    }


def capture_bundle(
    repo_root: str,
    *,
    out_dir: str,
    include_views: bool = False,
    inject_secret: bool = False,
) -> dict:
    ensure_repo_on_path(repo_root)

    from compat import emit_product_descriptor
    from diag import write_repro_bundle
    from tools.mvp.runtime_bundle import MVP_PACK_LOCK_REL

    descriptor = emit_product_descriptor(repo_root, product_id="client")
    server_descriptor = emit_product_descriptor(repo_root, product_id="server")
    build_id = str(dict(descriptor.get("version") or {}).get("build_id", "")).strip()
    semantic_contract_registry_hash = str(
        dict(dict(descriptor.get("descriptor") or {}).get("extensions", {}) or {}).get(
            "official.semantic_contract_registry_hash",
            "",
        )
    ).strip()

    pack_lock_payload = load_json(os.path.join(repo_root, MVP_PACK_LOCK_REL))
    session_spec_payload = _sample_session_spec_payload(
        pack_lock_hash=str(pack_lock_payload.get("pack_lock_hash", "")).strip(),
        semantic_contract_registry_hash=semantic_contract_registry_hash,
    )
    contract_bundle_payload = _sample_contract_bundle_payload()
    run_manifest_payload = _sample_run_manifest_payload(build_id=build_id)
    environment_summary = {
        "cpu_arch": "test-arch",
        "os_family": "TestOS",
        "os_version": "1",
        "python_major": "3.12",
    }

    if inject_secret:
        session_spec_payload["auth_token"] = "super-secret-token"
        session_spec_payload["machine_id"] = "machine-id-private"
        session_spec_payload["signing_key"] = "private-signing-key"
        session_spec_payload["nested_secret_payload"] = {
            "password": "top-secret-password",
            "credential_blob": "credential-hidden",
        }
        environment_summary["private_key"] = "private-key-material"

    return write_repro_bundle(
        repo_root=repo_root,
        created_by_product_id="client",
        build_id=build_id,
        out_dir=out_dir,
        window=16,
        include_views=include_views,
        descriptor_payloads=[descriptor, server_descriptor],
        run_manifest_payload=run_manifest_payload,
        session_spec_payload=session_spec_payload,
        contract_bundle_payload=contract_bundle_payload,
        pack_lock_payload=pack_lock_payload,
        semantic_contract_registry_hash=semantic_contract_registry_hash,
        contract_bundle_hash=FIXTURE_CONTRACT_BUNDLE_HASH,
        overlay_manifest_hash=FIXTURE_OVERLAY_MANIFEST_HASH,
        seed="12345",
        session_id="session.diag0.fixture",
        session_template_id="session.mvp_default",
        proof_anchor_rows=[
            {"proof_anchor_id": "proof.0001", "tick": 1, "tick_hash": "1" * 64},
            {"proof_anchor_id": "proof.0002", "tick": 2, "tick_hash": "2" * 64},
        ],
        canonical_event_rows=[
            {"event_id": "event.capture.0001", "tick": 1, "kind": "diag.capture", "product_id": "client"},
            {"event_id": "event.capture.0002", "tick": 2, "kind": "diag.capture", "product_id": "server"},
        ],
        log_events=[
            {"event_id": "log.0001", "tick": 1, "category": "diag", "message_key": "diag.capture.written", "severity": "info"},
            {"event_id": "log.0002", "tick": 2, "category": "compat", "message_key": "compat.negotiation.result", "severity": "info"},
        ],
        ipc_attach_rows=[
            {"event_id": "attach.0001", "tick": 2, "endpoint_id": "endpoint.server", "kind": "ipc.attach"},
        ],
        negotiation_records=[
            {"event_id": "neg.0001", "tick": 1, "compatibility_mode_id": "compat.full", "result": "complete"},
        ],
        view_fingerprints=[{"view_id": "view.fixture.0001", "fingerprint": "fixture.view.hash"}] if include_views else [],
        environment_summary=environment_summary,
    )


def list_bundle_files(bundle_dir: str) -> list[str]:
    rows = []
    for root, _, files in os.walk(bundle_dir):
        rel_root = os.path.relpath(root, bundle_dir)
        for name in files:
            rel = os.path.normpath(os.path.join(rel_root, name)) if rel_root != "." else name
            rows.append(rel.replace("\\", "/"))
    return sorted(rows)

