#!/usr/bin/env python3
import argparse
import json
import os
import tempfile
from typing import Dict, List

from dompkg_lib import DomPkgError, pack_package, refusal_payload


def _copy_inputs(input_files: List[str], root_prefix: str, staging_root: str) -> List[str]:
    rel_paths = []
    for src in sorted(set(input_files)):
        if not os.path.isfile(src):
            continue
        rel = os.path.relpath(src, root_prefix).replace("\\", "/")
        dst = os.path.join(staging_root, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(src, "rb") as in_handle:
            data = in_handle.read()
        with open(dst, "wb") as out_handle:
            out_handle.write(data)
        rel_paths.append(rel)
    return rel_paths


def _existing(paths: List[str]) -> List[str]:
    return [path for path in paths if os.path.isfile(path)]


def _group_specs(build_bin: str, build_lib: str, dist_tools: str, repo_root: str) -> List[Dict[str, object]]:
    return [
        {
            "group": "core-engine",
            "pkg_id": "org.dominium.pkg.core.engine",
            "requires": [],
            "provides": ["runtime.engine"],
            "files": _existing([os.path.join(build_lib, "domino_engine.lib")]),
        },
        {
            "group": "core-game",
            "pkg_id": "org.dominium.pkg.core.game",
            "requires": ["runtime.engine"],
            "provides": ["runtime.game"],
            "files": _existing([os.path.join(build_lib, "dominium_game.lib")]),
        },
        {
            "group": "core-client",
            "pkg_id": "org.dominium.pkg.core.client",
            "requires": ["runtime.game"],
            "provides": ["runtime.client"],
            "files": _existing([os.path.join(build_bin, "client.exe")]),
        },
        {
            "group": "core-server",
            "pkg_id": "org.dominium.pkg.core.server",
            "requires": ["runtime.game"],
            "provides": ["runtime.server"],
            "files": _existing([os.path.join(build_bin, "server.exe")]),
        },
        {
            "group": "core-launcher",
            "pkg_id": "org.dominium.pkg.core.launcher",
            "requires": ["runtime.client"],
            "provides": ["runtime.launcher"],
            "files": _existing([
                os.path.join(build_bin, "launcher.exe"),
                os.path.join(build_bin, "launcher_gui.exe"),
                os.path.join(build_bin, "launcher_tui.exe"),
            ]),
        },
        {
            "group": "core-setup",
            "pkg_id": "org.dominium.pkg.core.setup",
            "requires": [],
            "provides": ["runtime.setup"],
            "files": _existing([
                os.path.join(build_bin, "setup.exe"),
                os.path.join(build_bin, "setup_gui.exe"),
                os.path.join(build_bin, "setup_tui.exe"),
            ]),
        },
        {
            "group": "rend-soft",
            "pkg_id": "org.dominium.pkg.rend.soft",
            "requires": ["runtime.engine"],
            "provides": ["render.soft"],
            "files": _existing([
                os.path.join(build_lib, "dominium_game.lib"),
            ]),
        },
        {
            "group": "tools-ui",
            "pkg_id": "org.dominium.pkg.tools.ui",
            "requires": ["runtime.setup"],
            "provides": ["tool.ui.bind", "tool.ui.validate"],
            "files": _existing([
                os.path.join(dist_tools, "tool_ui_bind.exe"),
                os.path.join(dist_tools, "tool_ui_validate.exe"),
                os.path.join(dist_tools, "tool_ui_doc_annotate.exe"),
            ]),
        },
        {
            "group": "tools-pack",
            "pkg_id": "org.dominium.pkg.tools.pack",
            "requires": ["runtime.engine"],
            "provides": ["tool.pack.validate"],
            "files": _existing([
                os.path.join(build_bin, "validate_all.exe"),
                os.path.join(build_bin, "data_validate.exe"),
            ]),
        },
        {
            "group": "res-common",
            "pkg_id": "org.dominium.pkg.res.common",
            "requires": [],
            "provides": ["res.common"],
            "files": _existing([
                os.path.join(repo_root, "docs", "distribution", "PACK_TAXONOMY.md"),
                os.path.join(repo_root, "docs", "distribution", "PACK_SOURCES.md"),
            ]),
        },
        {
            "group": "locale-en",
            "pkg_id": "org.dominium.pkg.locale.en",
            "requires": ["res.common"],
            "provides": ["locale.en"],
            "files": _existing([
                os.path.join(repo_root, "tests", "distribution", "fixtures", "packs_maximal", "org.dominium.l10n.en_us", "pack_manifest.json"),
            ]),
        },
    ]


def _symbol_groups(build_bin: str) -> List[Dict[str, object]]:
    specs = []
    base = {
        "sym-client": ("org.dominium.pkg.sym.client", [os.path.join(build_bin, "client.pdb")]),
        "sym-server": ("org.dominium.pkg.sym.server", [os.path.join(build_bin, "server.pdb")]),
        "sym-launcher": ("org.dominium.pkg.sym.launcher", [os.path.join(build_bin, "launcher.pdb")]),
        "sym-setup": ("org.dominium.pkg.sym.setup", [os.path.join(build_bin, "setup.pdb")]),
    }
    for group, (pkg_id, files) in base.items():
        existing = _existing(files)
        if not existing:
            continue
        specs.append({
            "group": group,
            "pkg_id": pkg_id,
            "requires": [],
            "provides": [group.replace("-", ".")],
            "files": existing,
        })
    return specs


def main() -> int:
    parser = argparse.ArgumentParser(description="Pack build outputs into dompkg artifacts.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--build-bin", required=True)
    parser.add_argument("--build-lib", required=True)
    parser.add_argument("--dist-tools", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--arch", required=True)
    parser.add_argument("--abi", default="native")
    parser.add_argument("--pkg-version", default="0.1.0")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    build_bin = os.path.abspath(args.build_bin)
    build_lib = os.path.abspath(args.build_lib)
    dist_tools = os.path.abspath(args.dist_tools)
    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    specs = _group_specs(build_bin, build_lib, dist_tools, repo_root)
    specs.extend(_symbol_groups(build_bin))

    packed = []
    missing = []
    try:
        with tempfile.TemporaryDirectory(prefix="dompkg_pack_all_") as temp_root:
            for spec in specs:
                files = spec["files"]
                group = spec["group"]
                if not files:
                    missing.append(group)
                    continue
                stage_root = os.path.join(temp_root, group)
                os.makedirs(stage_root, exist_ok=True)
                # Use repo root for relative shaping when possible.
                roots = [repo_root, build_bin, build_lib, dist_tools]
                root_prefix = repo_root
                for candidate in roots:
                    if all(os.path.abspath(path).startswith(candidate) for path in files):
                        root_prefix = candidate
                        break
                _copy_inputs(files, root_prefix, stage_root)
                pkg_path = os.path.join(out_dir, group + ".dompkg")
                result = pack_package(
                    input_pairs=[],
                    output_pkg=pkg_path,
                    pkg_id=spec["pkg_id"],
                    pkg_version=args.pkg_version,
                    platform=args.platform,
                    arch=args.arch,
                    abi=args.abi,
                    requires_capabilities=spec["requires"],
                    provides_capabilities=spec["provides"],
                    entitlements=[],
                    optional_capabilities=[],
                    compression="deflate",
                    signature_payload=None,
                )
                # Re-pack using staged root so paths are deterministic and group-scoped.
                from dompkg_lib import collect_inputs  # local import keeps module single-file friendly
                input_pairs = collect_inputs(stage_root, [])
                result = pack_package(
                    input_pairs=input_pairs,
                    output_pkg=pkg_path,
                    pkg_id=spec["pkg_id"],
                    pkg_version=args.pkg_version,
                    platform=args.platform,
                    arch=args.arch,
                    abi=args.abi,
                    requires_capabilities=spec["requires"],
                    provides_capabilities=spec["provides"],
                    entitlements=[],
                    optional_capabilities=[],
                    compression="deflate",
                    signature_payload=None,
                )
                sidecar = pkg_path + ".manifest.json"
                with open(sidecar, "w", encoding="utf-8", newline="\n") as handle:
                    json.dump(result["manifest"], handle, indent=2, sort_keys=False)
                    handle.write("\n")
                packed.append({
                    "group": group,
                    "pkg_id": spec["pkg_id"],
                    "pkg_path": pkg_path.replace("\\", "/"),
                    "manifest_json": sidecar.replace("\\", "/"),
                    "content_hash": result["manifest"]["content_hash"],
                })
    except DomPkgError as exc:
        print(json.dumps(refusal_payload(exc.code, exc.message, exc.details), indent=2))
        return 3
    except Exception as exc:  # pragma: no cover
        print(json.dumps(refusal_payload("refuse.internal_error", "pkg_pack_all failed", {"error": str(exc)}), indent=2))
        return 1

    print(json.dumps({
        "result": "ok",
        "packed": packed,
        "missing_groups": sorted(missing),
        "output_dir": out_dir.replace("\\", "/"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
