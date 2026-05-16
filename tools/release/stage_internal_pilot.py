#!/usr/bin/env python3
"""Stage a local-only Dominium internal pilot release proof tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from typing import Dict, Iterable, List, Mapping, Optional


DEFAULT_PROJECTION_ROOT = os.path.join(
    ".dominium.local",
    "projections",
    "post-converge-12",
    "v0.0.0-post-converge-12",
    "win64",
    "dominium",
)
DEFAULT_RELEASE_ROOT = os.path.join(".dominium.local", "releases", "internal-pilot-0")
DEFAULT_RELEASE_ID = "internal-pilot-0"

PRODUCT_BINARIES = ("setup.exe", "launcher.exe", "client.exe", "server.exe", "tools.exe")
PROJECTION_MANIFESTS = (
    "install.manifest.json",
    "semantic_contract_registry.json",
    "release.manifest.json",
)
PROOF_INPUTS = (
    ("docs/release/NATIVE_BINARY_PROOF.md", "proof/native_binary_proof.md"),
    ("docs/release/PRODUCT_BOOT_PROOF.md", "proof/product_boot_proof.md"),
    ("docs/release/PORTABLE_PROJECTION_PROOF.md", "proof/portable_projection_proof.md"),
    (".aide/reports/latest-warning-disposition.md", "proof/warning_ledger.md"),
    (".aide/reports/latest-dominium-status.md", "proof/latest_dominium_status.md"),
)


def _norm(path: str) -> str:
    return path.replace(os.sep, "/")


def _repo_rel(repo_root: str, path: str) -> str:
    return _norm(os.path.relpath(path, repo_root))


def _abs(repo_root: str, path: str) -> str:
    return os.path.normpath(os.path.abspath(path if os.path.isabs(path) else os.path.join(repo_root, path)))


def _is_relative_to(path: str, parent: str) -> bool:
    path_abs = os.path.normcase(os.path.normpath(os.path.abspath(path)))
    parent_abs = os.path.normcase(os.path.normpath(os.path.abspath(parent)))
    try:
        return os.path.commonpath([path_abs, parent_abs]) == parent_abs
    except ValueError:
        return False


def _safe_release_root(repo_root: str, release_root: str) -> str:
    release_abs = _abs(repo_root, release_root)
    allowed_root = _abs(repo_root, os.path.join(".dominium.local", "releases"))
    if not _is_relative_to(release_abs, allowed_root):
        raise ValueError("release root must be under .dominium.local/releases")
    return release_abs


def _git_output(repo_root: str, args: List[str]) -> str:
    try:
        completed = subprocess.run(
            ["git"] + args,
            cwd=repo_root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return completed.stdout.strip()


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _write_json(path: str, payload: Mapping[str, object]) -> None:
    _ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _write_text(path: str, text: str) -> None:
    _ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text.rstrip() + "\n")


def _sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _iter_files(root: str) -> Iterable[str]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(name for name in dirnames if name != "__pycache__")
        for filename in sorted(filenames):
            yield os.path.join(dirpath, filename)


def _copy_required_proofs(repo_root: str, release_root: str) -> List[Dict[str, object]]:
    copied: List[Dict[str, object]] = []
    for src_rel, dst_rel in PROOF_INPUTS:
        src = os.path.join(repo_root, src_rel.replace("/", os.sep))
        dst = os.path.join(release_root, dst_rel.replace("/", os.sep))
        present = os.path.isfile(src)
        if present:
            _ensure_dir(os.path.dirname(dst))
            shutil.copy2(src, dst)
        copied.append(
            {
                "source": _norm(src_rel),
                "staged_path": _norm(dst_rel),
                "present": present,
            }
        )
    return copied


def _write_operator_docs(release_root: str, release_id: str) -> List[str]:
    docs = {
        "docs/README_INTERNAL_PILOT.md": """# Dominium Internal Pilot Release 0

This is a local-only internal pilot release proof staged from a previously
validated portable projection. It is not a public release, tag, installer,
GitHub release, or published package.

Use `manifest/internal_pilot_release.manifest.json` and
`manifest/checksums.sha256` to inspect the staged payload. Product binaries
are under `projection/bin/`.
""",
        "docs/RUNBOOK.md": """# Internal Pilot Runbook

1. Verify checksums with `python tools/validators/check_internal_pilot_release.py --repo-root . --release-root .dominium.local/releases/internal-pilot-0 --strict`.
2. Inspect `projection/install.manifest.json`, `projection/release.manifest.json`, and `projection/semantic_contract_registry.json`.
3. Run safe command surfaces from `projection/bin/` only, such as `--help`, `--version`, `--status`, or `--smoke`.
4. Do not publish, tag, upload, or convert this proof tree into an installer.
""",
        "docs/ROLLBACK.md": """# Internal Pilot Cleanup

This staging root is generated local evidence under `.dominium.local/releases`.
It may be removed by deleting `.dominium.local/releases/internal-pilot-0/`.

No source files, git tags, public releases, installer outputs, or published
packages are created by this proof.
""",
    }
    written = []
    for rel_path, text in docs.items():
        _write_text(os.path.join(release_root, rel_path.replace("/", os.sep)), text)
        written.append(rel_path)
    return written


def _checksum_manifest(release_root: str) -> List[Dict[str, str]]:
    checksum_rel = "manifest/checksums.sha256"
    rows: List[Dict[str, str]] = []
    for path in _iter_files(release_root):
        rel_path = _norm(os.path.relpath(path, release_root))
        if rel_path == checksum_rel:
            continue
        rows.append({"path": rel_path, "sha256": _sha256(path)})
    rows.sort(key=lambda row: row["path"])
    text = "".join("{}  {}\n".format(row["sha256"], row["path"]) for row in rows)
    _write_text(os.path.join(release_root, checksum_rel.replace("/", os.sep)), text)
    return rows


def _projection_inventory(projection_root: str) -> Dict[str, object]:
    manifests = []
    binaries = []
    for rel_path in PROJECTION_MANIFESTS:
        manifests.append({"path": rel_path, "present": os.path.isfile(os.path.join(projection_root, rel_path))})
    for name in PRODUCT_BINARIES:
        rel_path = "bin/{}".format(name)
        binaries.append({"path": rel_path, "present": os.path.isfile(os.path.join(projection_root, "bin", name))})
    return {"manifests": manifests, "binaries": binaries}


def stage_internal_pilot(repo_root: str, projection_root: str, release_root: str, release_id: str) -> Dict[str, object]:
    repo_root_abs = os.path.normpath(os.path.abspath(repo_root))
    projection_abs = _abs(repo_root_abs, projection_root)
    release_abs = _safe_release_root(repo_root_abs, release_root)
    if not os.path.isdir(projection_abs):
        raise FileNotFoundError("projection root does not exist: {}".format(projection_abs))

    if os.path.exists(release_abs):
        if not _is_relative_to(release_abs, os.path.join(repo_root_abs, ".dominium.local", "releases")):
            raise ValueError("refusing to remove release root outside .dominium.local/releases")
        shutil.rmtree(release_abs)

    _ensure_dir(release_abs)
    projection_stage = os.path.join(release_abs, "projection")
    shutil.copytree(projection_abs, projection_stage)

    proofs = _copy_required_proofs(repo_root_abs, release_abs)
    operator_docs = _write_operator_docs(release_abs, release_id)

    head = _git_output(repo_root_abs, ["rev-parse", "HEAD"])
    origin_main = _git_output(repo_root_abs, ["rev-parse", "origin/main"])
    projection_inventory = _projection_inventory(projection_stage)

    manifest = {
        "schema_version": "dominium.release_00.internal_pilot_manifest.v1",
        "release_id": release_id,
        "publication_status": "local_internal_only",
        "repo_head": head,
        "origin_main": origin_main,
        "source_projection_root": _repo_rel(repo_root_abs, projection_abs),
        "staged_projection_root": "projection",
        "manifests": [row["path"] for row in projection_inventory["manifests"]],
        "product_binaries": [row["path"] for row in projection_inventory["binaries"]],
        "proof_reports": [row["staged_path"] for row in proofs],
        "operator_docs": operator_docs,
        "warnings": [
            "full promotion CTest was not run for RELEASE-00",
            "no public release, installer, tag, upload, or package publication was created",
            "release staging root is local ignored proof evidence only",
        ],
    }
    _write_json(os.path.join(release_abs, "manifest", "internal_pilot_release.manifest.json"), manifest)

    provenance = {
        "schema_version": "dominium.release_00.internal_pilot_provenance.v1",
        "release_id": release_id,
        "repo_head": head,
        "origin_main": origin_main,
        "input_projection_root": _repo_rel(repo_root_abs, projection_abs),
        "release_root": _repo_rel(repo_root_abs, release_abs),
        "generator": "tools/release/stage_internal_pilot.py",
        "validator": "tools/validators/check_internal_pilot_release.py",
        "local_only": True,
        "public_release_created": False,
        "git_tag_created": False,
        "installer_created": False,
        "uploaded": False,
    }
    _write_json(os.path.join(release_abs, "manifest", "provenance.json"), provenance)

    validation_report = {
        "schema_version": "dominium.release_00.internal_pilot_staging_report.v1",
        "release_id": release_id,
        "projection_root": "projection",
        "projection_inventory": projection_inventory,
        "proofs": proofs,
        "operator_docs": operator_docs,
        "blockers": [],
        "status": "STAGED",
    }
    _write_json(os.path.join(release_abs, "proof", "validation_report.json"), validation_report)

    checksums = _checksum_manifest(release_abs)
    return {
        "result": "complete",
        "release_id": release_id,
        "release_root": _repo_rel(repo_root_abs, release_abs),
        "projection_input": _repo_rel(repo_root_abs, projection_abs),
        "checksum_count": len(checksums),
        "proof_count": len(proofs),
        "manifest_path": "manifest/internal_pilot_release.manifest.json",
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Stage a local-only Dominium internal pilot release proof tree.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--projection-root", default=DEFAULT_PROJECTION_ROOT)
    parser.add_argument("--release-root", default=DEFAULT_RELEASE_ROOT)
    parser.add_argument("--release-id", default=DEFAULT_RELEASE_ID)
    args = parser.parse_args(argv)

    try:
        result = stage_internal_pilot(
            repo_root=args.repo_root,
            projection_root=args.projection_root,
            release_root=args.release_root,
            release_id=args.release_id,
        )
    except Exception as exc:  # noqa: BLE001 - command-line proof tool reports a structured blocker.
        sys.stderr.write("stage_internal_pilot failed: {}\n".format(exc))
        return 1

    sys.stdout.write(json.dumps(result, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
