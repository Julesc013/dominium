import argparse
import json
import os
import sys


def _load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _node_by_id(nodes, product_id):
    for node in nodes:
        if isinstance(node, dict) and node.get("product_id") == product_id:
            return node
    return {}


def _extract_profile_package_ids(profile_record):
    pkg_ids = []
    for entry in profile_record.get("package_refs") or []:
        if isinstance(entry, dict):
            pkg_id = entry.get("pkg_id")
            if isinstance(pkg_id, str):
                pkg_ids.append(pkg_id)
    return sorted(set(pkg_ids))


def main():
    parser = argparse.ArgumentParser(description="SDK distribution profile contract tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    product_graph_path = os.path.join(repo_root, "data", "registries", "product_graph.json")
    payload = _load_json(product_graph_path)
    record = payload.get("record", {})
    nodes = record.get("nodes", [])

    sdk_engine = _node_by_id(nodes, "dominium.product.sdk.engine")
    sdk_game = _node_by_id(nodes, "dominium.product.sdk.game")
    if not sdk_engine or not sdk_game:
        print("sdk product nodes missing")
        return 1

    engine_exports = set([str(v) for v in sdk_engine.get("provides_exports") or []])
    game_exports = set([str(v) for v in sdk_game.get("provides_exports") or []])
    if "export:lib.engine" not in engine_exports:
        print("sdk.engine missing export:lib.engine")
        return 1
    if "export:lib.game" not in game_exports:
        print("sdk.game missing export:lib.game")
        return 1

    sdk_game_requires = set([str(v) for v in sdk_game.get("requires_exports") or []])
    if "export:sdk.engine" not in sdk_game_requires:
        print("sdk.game missing export:sdk.engine dependency")
        return 1

    for node in (sdk_engine, sdk_game):
        requires_exports = [str(v) for v in node.get("requires_exports") or []]
        if "export:bin.setup" in requires_exports or "export:bin.launcher" in requires_exports:
            print("sdk node has forbidden setup/launcher dependency")
            return 1

    profiles_root = os.path.join(repo_root, "data", "profiles")
    sdk_engine_profile = _load_json(os.path.join(profiles_root, "profile.sdk_engine.json"))
    sdk_game_profile = _load_json(os.path.join(profiles_root, "profile.sdk_game.json"))
    if sdk_engine_profile.get("schema_id") != "dominium.schema.distribution.profile":
        print("sdk engine profile schema mismatch")
        return 1
    if sdk_game_profile.get("schema_id") != "dominium.schema.distribution.profile":
        print("sdk game profile schema mismatch")
        return 1

    engine_profile_pkgs = _extract_profile_package_ids(sdk_engine_profile.get("record", {}))
    game_profile_pkgs = _extract_profile_package_ids(sdk_game_profile.get("record", {}))
    if engine_profile_pkgs != ["org.dominium.sdk.engine"]:
        print("sdk engine profile package refs mismatch")
        return 1
    if game_profile_pkgs != ["org.dominium.sdk.engine", "org.dominium.sdk.game"]:
        print("sdk game profile package refs mismatch")
        return 1

    print("distribution sdk profile contracts OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
