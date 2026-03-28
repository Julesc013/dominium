"""Helpers for PACK-COMPAT-2 FAST tests."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from typing import Tuple


def ensure_repo_on_path(repo_root: str) -> None:
    token = os.path.abspath(str(repo_root))
    if token not in sys.path:
        sys.path.insert(0, token)


def make_temp_dir(prefix: str = "pack_compat2_") -> str:
    return tempfile.mkdtemp(prefix=prefix)


def cleanup_temp_dir(path: str) -> None:
    if path and os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)


def write_canonical_json_file(path: str, payload: dict) -> None:
    from tools.xstack.compatx.canonical_json import canonical_json_text

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(payload))
        handle.write("\n")


def base_save_payload() -> dict:
    from tools.xstack.sessionx.creator import _initial_universe_state

    return _initial_universe_state(
        save_id="save.test.pack_compat2",
        law_profile_id="law.lab.unrestricted",
        camera_assembly=None,
        instrument_assemblies=[],
        budget_policy_id="policy.budget.default_lab",
        fidelity_policy_id="policy.fidelity.default_lab",
        activation_policy_id="policy.activation.default_lab",
        max_compute_units_per_tick=0,
    )


def current_save_payload(repo_root: str, *, contract_hash: str = "b" * 64, engine_version_created: str = "0.0.0+build.test") -> dict:
    from compat.data_format_loader import stamp_artifact_metadata

    return stamp_artifact_metadata(
        repo_root=repo_root,
        artifact_kind="save_file",
        payload=base_save_payload(),
        semantic_contract_bundle_hash=str(contract_hash),
        engine_version_created=str(engine_version_created),
    )


def legacy_save_payload() -> dict:
    return base_save_payload()


def future_save_payload(repo_root: str, *, contract_hash: str = "b" * 64) -> dict:
    from compat.data_format_loader import artifact_deterministic_fingerprint

    payload = current_save_payload(repo_root, contract_hash=contract_hash)
    payload["format_version"] = "9.0.0"
    payload["deterministic_fingerprint"] = artifact_deterministic_fingerprint(payload)
    return payload


def write_fixture(path_root: str, file_name: str, payload: dict) -> str:
    out_path = os.path.join(path_root, file_name)
    write_canonical_json_file(out_path, payload)
    return out_path


def load_fixture(repo_root: str, artifact_kind: str, path: str, *, contract_hash: str = "", allow_read_only: bool = False) -> Tuple[dict, dict, dict]:
    from compat.data_format_loader import load_versioned_artifact

    return load_versioned_artifact(
        repo_root=repo_root,
        artifact_kind=artifact_kind,
        path=path,
        semantic_contract_bundle_hash=str(contract_hash or "").strip(),
        allow_read_only=bool(allow_read_only),
        strip_loaded_metadata=False,
    )
