import argparse
import os
import sys


DOCS_REQUIRED = {
    "docs/architecture/DIRECTORY_STRUCTURE.md": [
        "repo/",
        "data/",
        "--data-root",
        "packs/",
        "modpacks/",
        "workspaces/",
        "index/",
    ],
    "docs/architecture/PACK_FORMAT.md": [
        "pack.toml",
        "no executable code",
        "no hardcoded paths",
        "no implicit load-order",
        "schema/pack_manifest.schema",
    ],
    "docs/modding/MOD_ECOSYSTEM.md": [
        "mods are packs",
        "mods never write files",
        "missing mods",
    ],
    "docs/architecture/SAVE_FORMAT.md": [
        "WORLDDEF",
        "ENGINE_STATE",
        "GAME_STATE",
        "MOD_STATE",
        "EVENT_LOG",
        "REPLAY_STREAM",
    ],
    "docs/architecture/REPLAY_FORMAT.md": [
        "WORLDDEF",
        "EVENT_LOG",
    ],
    "docs/architecture/LOCKFILES.md": [
        "capabilities.lock",
        "capability_lockfile.schema",
        "missing capability",
    ],
    "docs/architecture/CAPABILITY_BASELINES.md": [
        "BASELINE_LEGACY_CORE",
        "BASELINE_MAINLINE_CORE",
        "BASELINE_MODERN_UI",
        "BASELINE_SERVER_MIN",
    ],
    "docs/architecture/SKU_MATRIX.md": [
        "legacy_core",
        "mainline_core",
        "modern_ui",
        "server_min",
    ],
    "docs/architecture/LANGUAGE_STRATEGY.md": [
        "c abi spine",
        "c89/c++98",
        "capability list printed by every binary",
    ],
    "docs/architecture/TRANSITION_PLAYBOOK.md": [
        "c abi spine",
        "multi-sku",
        "refusal",
    ],
    "docs/architecture/DISTRIBUTION_LAYOUT.md": [
        "no content installed by default",
        "--data-root",
    ],
    "docs/architecture/INSTALLER_CONTRACT.md": [
        "offline install",
        "no content installed by default",
    ],
    "docs/architecture/LAUNCHER_CONTRACT.md": [
        "launchers manipulate",
        "data/",
        "preflight",
    ],
    "docs/architecture/WORKSPACES.md": [
        "workspace.toml",
        "workspaces are pack-like overlays",
        "workspaces are optional",
    ],
    "docs/architecture/MODPACK_FORMAT.md": [
        "modpack.toml",
        "capabilities.lock",
    ],
    "docs/architecture/INDEXING_POLICY.md": [
        "optional caches",
        "safe to delete",
    ],
    "docs/architecture/NAMESPACING_RULES.md": [
        "reverse-dns",
        "capabilities",
        "fields",
        "processes",
        "chunk types",
        "policies",
        "metrics",
        "units",
    ],
    "docs/architecture/UNIT_SYSTEM_POLICY.md": [
        "fixed-point",
        "unit identifiers",
        "unit tags",
    ],
}


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def main():
    parser = argparse.ArgumentParser(description="HARDEN-1 docs contracts.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    failures = []
    for rel_path, required in DOCS_REQUIRED.items():
        path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(path):
            failures.append("missing doc: {}".format(rel_path))
            continue
        text = read_text(path).lower()
        for token in required:
            if token.lower() not in text:
                failures.append("doc missing '{}': {}".format(token, rel_path))

    if failures:
        for item in failures:
            print("FAIL: {}".format(item))
        return 1

    print("HARDEN-1 docs OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
