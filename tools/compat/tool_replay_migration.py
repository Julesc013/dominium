"""Replay deterministic PACK-COMPAT-2 artifact migrations."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.compat.data_format_loader import load_versioned_artifact, stamp_artifact_metadata  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


def _read_json(path: str) -> dict:
    payload = json.load(open(path, "r", encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON root must be object: {}".format(path.replace("\\", "/")))
    return dict(payload)


def migrate(
    repo_root: str,
    artifact_kind: str,
    payload: Dict[str, object],
    *,
    semantic_contract_bundle_hash: str = "",
) -> dict:
    legacy = dict(payload or {})
    legacy.pop("format_version", None)
    legacy.pop("engine_version_created", None)
    legacy.pop("deterministic_fingerprint", None)
    return stamp_artifact_metadata(
        repo_root=repo_root,
        artifact_kind=artifact_kind,
        payload=legacy,
        semantic_contract_bundle_hash=semantic_contract_bundle_hash,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Replay deterministic artifact migration chains.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--artifact-kind", required=True)
    parser.add_argument("--input-path", required=True)
    parser.add_argument("--semantic-contract-bundle-hash", default="")
    parser.add_argument("--allow-read-only", action="store_true")
    parser.add_argument("--output-path", default="")
    return parser


def main() -> int:
    args = _parser().parse_args()
    repo_root = os.path.abspath(str(args.repo_root))
    input_path = os.path.normpath(os.path.abspath(str(args.input_path)))
    original = _read_json(input_path)
    migrated, meta, error = load_versioned_artifact(
        repo_root=repo_root,
        artifact_kind=str(args.artifact_kind),
        path=input_path,
        semantic_contract_bundle_hash=str(args.semantic_contract_bundle_hash or "").strip(),
        allow_read_only=bool(args.allow_read_only),
        strip_loaded_metadata=False,
    )
    payload = {
        "result": "complete" if not error else "refused",
        "artifact_kind": str(args.artifact_kind),
        "input_path": input_path.replace("\\", "/"),
        "input_hash": canonical_sha256(original),
        "loaded_hash": canonical_sha256(migrated) if not error else "",
        "migration_events": list(meta.get("migration_events") or []) if not error else [],
        "read_only_applied": bool(meta.get("read_only_applied", False)) if not error else False,
        "read_only_mode": bool(meta.get("read_only_applied", False)) if not error else False,
        "law_profile_id_override": str(meta.get("law_profile_id_override", "")).strip() if not error else "",
        "deterministic_fingerprint": "",
        "refusal": dict(error.get("refusal") or {}) if error else {},
    }
    payload["deterministic_fingerprint"] = canonical_sha256(
        {
            "artifact_kind": str(payload.get("artifact_kind", "")),
            "input_hash": str(payload.get("input_hash", "")),
            "loaded_hash": str(payload.get("loaded_hash", "")),
            "migration_events": list(payload.get("migration_events") or []),
            "read_only_applied": bool(payload.get("read_only_applied", False)),
            "read_only_mode": bool(payload.get("read_only_mode", False)),
            "law_profile_id_override": str(payload.get("law_profile_id_override", "")),
            "refusal": dict(payload.get("refusal") or {}),
        }
    )
    if str(args.output_path or "").strip():
        out_abs = os.path.normpath(os.path.abspath(str(args.output_path)))
        os.makedirs(os.path.dirname(out_abs), exist_ok=True)
        with open(out_abs, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(canonical_json_text(payload))
            handle.write("\n")
    print(canonical_json_text(payload))
    print("")
    return 0 if not error else 1


if __name__ == "__main__":
    raise SystemExit(main())
