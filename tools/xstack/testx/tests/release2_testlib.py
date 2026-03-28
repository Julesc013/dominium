"""Shared RELEASE-2 reproducible-build and signing test helpers."""

from __future__ import annotations

import json
import os
import tempfile
from contextlib import contextmanager

from release import (
    build_build_id_input_payload,
    build_id_identity_from_input_payload,
    build_mock_signature_block,
    build_release_manifest,
    verify_release_manifest,
    write_release_manifest,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


SEMANTIC_HASH = "6a" * 32
PACK_COMPAT_HASH = "2a" * 32


def _write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _write_json(path: str, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _compilation_options(product_id: str, *, build_configuration: str = "release") -> dict:
    return {
        "descriptor_schema_version": "1.0.0",
        "product_id": str(product_id).strip(),
        "runtime_family": "python.portable",
        "build_configuration": str(build_configuration).strip() or "release",
        "protocol_ids": ["protocol.loopback.control"],
        "feature_capabilities": ["cap.ui.cli", "cap.ui.tui"],
        "source": "RELEASE2-TEST",
    }


def descriptor_payload(
    product_id: str,
    *,
    source_revision_id: str = "rev.fixture",
    platform_tag: str = "platform.portable",
    build_configuration: str = "release",
) -> dict:
    compilation_options = _compilation_options(product_id, build_configuration=build_configuration)
    compilation_options_hash = canonical_sha256(compilation_options)
    identity = build_id_identity_from_input_payload(
        build_build_id_input_payload(
            product_id=str(product_id).strip(),
            semantic_contract_registry_hash=SEMANTIC_HASH,
            compilation_options_hash=compilation_options_hash,
            source_revision_id_value=str(source_revision_id).strip(),
            explicit_build_number="",
            platform_tag=str(platform_tag).strip(),
        )
    )
    build_id = str(identity.get("build_id", "")).strip()
    inputs_hash = str(identity.get("inputs_hash", "")).strip()
    return {
        "product_id": str(product_id).strip(),
        "product_version": "0.0.0+{}".format(build_id),
        "extensions": {
            "official.build_id": build_id,
            "official.inputs_hash": inputs_hash,
            "official.git_commit_hash": str(source_revision_id).strip(),
            "official.semantic_contract_registry_hash": SEMANTIC_HASH,
            "official.compilation_options_hash": compilation_options_hash,
            "official.source_revision_id": str(source_revision_id).strip(),
            "official.explicit_build_number": "",
            "official.platform_tag": str(platform_tag).strip(),
            "official.build_configuration": str(build_configuration).strip() or "release",
            "official.build_input_selection": "source_revision_id",
        },
    }


def _binary_script_text(product_id: str, *, source_revision_id: str = "rev.fixture") -> str:
    descriptor = json.dumps(descriptor_payload(product_id, source_revision_id=source_revision_id), sort_keys=True)
    return "\n".join(
        [
            "#!/usr/bin/env python3",
            "import sys",
            "if '--descriptor' in sys.argv:",
            "    sys.stdout.write({!r})".format(descriptor),
            "    sys.stdout.write('\\n')",
            "    raise SystemExit(0)",
            "raise SystemExit(0)",
            "",
        ]
    )


@contextmanager
def release_fixture():
    with tempfile.TemporaryDirectory(prefix="dominium_release2_test_") as tmp_dir:
        root = os.path.join(tmp_dir, "dist")
        os.makedirs(os.path.join(root, "bin"), exist_ok=True)
        _write(os.path.join(root, "bin", "client"), _binary_script_text("client"))
        _write(os.path.join(root, "bin", "server"), _binary_script_text("server"))

        pack_dir = os.path.join(root, "packs", "official", "pack.test")
        os.makedirs(pack_dir, exist_ok=True)
        _write_json(
            os.path.join(pack_dir, "pack.alias.json"),
            {
                "pack_alias_id": "pack.test",
                "canonical_hash": "3b" * 32,
                "distribution_channel": "official",
                "runtime_version": "0.0.0",
                "source_packs": [
                    {
                        "pack_id": "pack.test.source",
                        "compat_manifest_hash": PACK_COMPAT_HASH,
                    }
                ],
            },
        )
        _write(os.path.join(pack_dir, "payload.txt"), "fixture-pack\n")

        _write_json(os.path.join(root, "profiles", "bundle.test.json"), {"profile_bundle_id": "bundle.test"})
        _write_json(os.path.join(root, "locks", "pack_lock.test.json"), {"pack_lock_hash": "4c" * 32})
        _write_json(os.path.join(root, "bundles", "bundle.base.test", "bundle.json"), {"bundle_id": "bundle.base.test"})
        _write_json(
            os.path.join(root, "manifest.json"),
            {
                "bundle_id": "bundle.base.test",
                "semantic_contract_registry_hash": SEMANTIC_HASH,
            },
        )
        _write_json(os.path.join(root, "install.manifest.json"), {"install_id": "install.test"})
        yield root


def build_manifest_payload(dist_root: str, *, platform_tag: str = "platform.portable") -> dict:
    return build_release_manifest(
        dist_root,
        platform_tag=platform_tag,
        channel_id="mock",
        verify_build_ids=True,
    )


def build_manifest_text(dist_root: str, *, platform_tag: str = "platform.portable") -> str:
    return canonical_json_text(build_manifest_payload(dist_root, platform_tag=platform_tag))


def verify_without_signature(dist_root: str, *, platform_tag: str = "platform.portable") -> dict:
    payload = build_manifest_payload(dist_root, platform_tag=platform_tag)
    manifest_path = os.path.join(dist_root, "manifests", "release_manifest.json")
    write_release_manifest(dist_root, payload, manifest_path=manifest_path)
    return verify_release_manifest(dist_root, manifest_path, repo_root=os.getcwd())


def signed_manifest_payload(dist_root: str, *, platform_tag: str = "platform.portable") -> dict:
    unsigned = build_manifest_payload(dist_root, platform_tag=platform_tag)
    signature = build_mock_signature_block(
        signer_id="signer.mock.release2",
        signed_hash=str(unsigned.get("manifest_hash", "")).strip(),
    )
    return build_release_manifest(
        dist_root,
        platform_tag=platform_tag,
        channel_id="mock",
        signatures=[signature],
        verify_build_ids=True,
    )


def build_id_for_source(product_id: str, source_revision_id: str) -> str:
    return str(descriptor_payload(product_id, source_revision_id=source_revision_id).get("extensions", {}).get("official.build_id", "")).strip()
