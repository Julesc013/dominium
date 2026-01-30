import argparse
import json
import os
import sys


def read_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_template_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()
    replacements = {
        "{{seed}}": "0",
        "{{spawn_x}}": "0",
        "{{spawn_y}}": "0",
        "{{spawn_z}}": "0",
        "{{movement_policies}}": "[]",
        "{{authority_policies}}": "[]",
        "{{mode_policies}}": "[]",
        "{{debug_policies}}": "[]",
        "{{playtest_policies}}": "[]",
        "{{camera_policies}}": "[]",
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    return json.loads(text)


def require(condition, message):
    if not condition:
        sys.stderr.write("FAIL: {}\n".format(message))
        return False
    return True


def count_nodes_edges(worlddef):
    topology = worlddef.get("topology", {})
    nodes = topology.get("nodes", []) or []
    edges = topology.get("edges", []) or []
    return len(nodes), len(edges)


def main():
    parser = argparse.ArgumentParser(description="Exploration scaling fixture contracts.")
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "perf", "exploration_fixtures")
    config_path = os.path.join(fixture_root, "fixtures.json")

    ok = True
    ok = ok and require(os.path.isfile(config_path), "fixtures.json missing")
    if not ok:
        return 1

    cfg = read_json(config_path)
    nav_script = cfg.get("nav_script_template", "")
    ui_script = cfg.get("ui_script", "")
    status_script = cfg.get("status_script_template", "")

    ok = ok and require("{save_path}" in nav_script, "nav_script_template missing {save_path}")
    ok = ok and require("{save2_path}" in nav_script, "nav_script_template missing {save2_path}")
    ok = ok and require("{replay_path}" in nav_script, "nav_script_template missing {replay_path}")
    ok = ok and require("{save_path}" in status_script, "status_script_template missing {save_path}")
    ok = ok and require("load-world" in ui_script, "ui_script missing load-world")

    fixtures = cfg.get("fixtures", [])
    ok = ok and require(fixtures, "fixtures list missing")

    for entry in fixtures:
        fixture_id = entry.get("id", "")
        root = entry.get("root", "")
        expected_nodes = entry.get("expected_nodes", 0)
        expected_edges = entry.get("expected_edges", 0)
        if not fixture_id or not root:
            ok = ok and require(False, "fixture entry missing id/root")
            continue
        fixture_dir = os.path.join(fixture_root, root)
        template_path = os.path.join(
            fixture_dir, "data", "world", "templates", "exploration_baseline.worlddef.json"
        )
        ok = ok and require(os.path.isdir(fixture_dir), "fixture folder missing {}".format(fixture_dir))
        ok = ok and require(os.path.isfile(template_path), "fixture template missing {}".format(template_path))
        if not os.path.isfile(template_path):
            continue

        try:
            worlddef = load_template_json(template_path)
        except Exception as exc:
            ok = ok and require(False, "fixture JSON unreadable {} ({})".format(template_path, exc))
            continue

        nodes, edges = count_nodes_edges(worlddef)
        ok = ok and require(nodes == expected_nodes,
                            "node count mismatch {} ({} != {})".format(fixture_id, nodes, expected_nodes))
        ok = ok and require(edges == expected_edges,
                            "edge count mismatch {} ({} != {})".format(fixture_id, edges, expected_edges))

        spawn = worlddef.get("spawn_spec", {})
        spawn_node = spawn.get("spawn_node_ref", {}).get("node_id", "")
        ok = ok and require(spawn_node == "body.earth",
                            "spawn node mismatch {} ({})".format(fixture_id, spawn_node))

        extensions = worlddef.get("extensions", {})
        ok = ok and require("earth_radius_m" in extensions,
                            "earth_radius_m missing in {}".format(fixture_id))
        ok = ok and require("camera_modes" in extensions,
                            "camera_modes missing in {}".format(fixture_id))

        policy_sets = worlddef.get("policy_sets", {})
        required_sets = [
            "movement_policies",
            "authority_policies",
            "mode_policies",
            "debug_policies",
            "playtest_policies",
            "camera_policies",
        ]
        for key in required_sets:
            ok = ok and require(key in policy_sets,
                                "policy set {} missing in {}".format(key, fixture_id))

        if worlddef.get("initial_fields") not in ([], None):
            ok = ok and require(False, "initial_fields not empty in {}".format(fixture_id))

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
