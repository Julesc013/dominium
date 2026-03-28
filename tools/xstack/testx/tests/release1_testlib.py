"""Shared RELEASE-1 manifest TestX helpers."""

from __future__ import annotations

import json
import os
import tempfile
from contextlib import contextmanager

from release import build_release_manifest, verify_release_manifest, write_release_manifest
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


SEMANTIC_HASH = "1f" * 32
PACK_COMPAT_HASH = "2a" * 32


def _write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _write_json(path: str, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _descriptor_payload(product_id: str) -> dict:
    build_id = "build.test.{}".format(product_id)
    return {
        "product_id": str(product_id),
        "product_version": "0.0.0+{}".format(build_id),
        "extensions": {
            "official.build_id": build_id,
            "official.semantic_contract_registry_hash": SEMANTIC_HASH,
        },
    }


def _binary_script_text(product_id: str) -> str:
    descriptor = json.dumps(_descriptor_payload(product_id), sort_keys=True)
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
    with tempfile.TemporaryDirectory(prefix="dominium_release1_test_") as tmp_dir:
        root = os.path.join(tmp_dir, "dist")
        os.makedirs(os.path.join(root, "bin"), exist_ok=True)
        _write(os.path.join(root, "bin", "client"), _binary_script_text("client"))
        _write(os.path.join(root, "bin", "server"), _binary_script_text("server"))
        _write(os.path.join(root, "bin", "dom.cmd"), "@echo off\r\npython dom %*\r\n")

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
        _write_json(os.path.join(root, "manifest.json"), {"bundle_id": "bundle.base.test"})
        _write_json(os.path.join(root, "install.manifest.json"), {"install_id": "install.test"})
        yield root


def build_manifest_text(dist_root: str, *, platform_tag: str = "platform.portable") -> str:
    return canonical_json_text(build_release_manifest(dist_root, platform_tag=platform_tag, channel_id="mock"))


def build_manifest_payload(dist_root: str, *, platform_tag: str = "platform.portable") -> dict:
    return build_release_manifest(dist_root, platform_tag=platform_tag, channel_id="mock")


def write_and_verify_manifest(dist_root: str, *, platform_tag: str = "platform.portable") -> dict:
    payload = build_manifest_payload(dist_root, platform_tag=platform_tag)
    manifest_path = os.path.join(dist_root, "manifests", "release_manifest.json")
    write_release_manifest(dist_root, payload, manifest_path=manifest_path)
    return verify_release_manifest(dist_root, manifest_path, repo_root=os.getcwd())


def product_descriptor_hash(product_id: str) -> str:
    return canonical_sha256(_descriptor_payload(product_id))
