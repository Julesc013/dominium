import argparse
import json
import os
import sys


def _load_env_tools(repo_root):
    dev_root = os.path.join(repo_root, "scripts", "dev")
    if dev_root not in sys.path:
        sys.path.insert(0, dev_root)
    import env_tools_lib

    return env_tools_lib


def _require(condition, message):
    if condition:
        return True
    sys.stderr.write("FAIL: {}\n".format(message))
    return False


def case_build(repo_root):
    env_tools = _load_env_tools(repo_root)
    dirs_a = env_tools.canonical_workspace_dirs(repo_root, ws_id="isolation-a")
    dirs_b = env_tools.canonical_workspace_dirs(repo_root, ws_id="isolation-b")
    checks = [
        _require(dirs_a["build_root"] != dirs_b["build_root"], "workspace build roots must differ"),
        _require(dirs_a["build_root"].replace("\\", "/").startswith(repo_root.replace("\\", "/") + "/out/build/"),
                 "workspace build root must be under out/build"),
        _require("/out/build/isolation-a" in dirs_a["build_root"].replace("\\", "/"),
                 "workspace A build root must include ws id"),
        _require("/out/build/isolation-b" in dirs_b["build_root"].replace("\\", "/"),
                 "workspace B build root must include ws id"),
    ]
    if not all(checks):
        return 1
    print("test_workspace_isolation_build=ok")
    return 0


def case_dist(repo_root):
    env_tools = _load_env_tools(repo_root)
    dirs_a = env_tools.canonical_workspace_dirs(repo_root, ws_id="isolation-a")
    dirs_b = env_tools.canonical_workspace_dirs(repo_root, ws_id="isolation-b")
    checks = [
        _require(dirs_a["dist_root"] != dirs_b["dist_root"], "workspace dist roots must differ"),
        _require(dirs_a["dist_root"].replace("\\", "/").startswith(repo_root.replace("\\", "/") + "/dist/ws/"),
                 "workspace dist root must be under dist/ws"),
        _require("/dist/ws/isolation-a" in dirs_a["dist_root"].replace("\\", "/"),
                 "workspace A dist root must include ws id"),
        _require("/dist/ws/isolation-b" in dirs_b["dist_root"].replace("\\", "/"),
                 "workspace B dist root must include ws id"),
    ]
    if not all(checks):
        return 1
    print("test_workspace_isolation_dist=ok")
    return 0


def case_no_global_write(repo_root):
    policy_path = os.path.join(repo_root, "data", "registries", "gate_policy.json")
    with open(policy_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    gates = payload.get("record", {}).get("gates", [])
    violations = []
    for gate in gates:
        command = gate.get("command", [])
        if not isinstance(command, list):
            continue
        joined = " ".join(str(item) for item in command)
        lowered = joined.lower()
        if "out/build/vs2026" in lowered:
            violations.append("hardcoded legacy build path in gate {}".format(gate.get("gate_id", "<unknown>")))
        if "dist/sys/" in lowered or "dist\\sys\\" in lowered:
            violations.append("hardcoded global dist/sys path in gate {}".format(gate.get("gate_id", "<unknown>")))
    if violations:
        for item in violations:
            sys.stderr.write("FAIL: {}\n".format(item))
        return 1
    print("test_no_global_write=ok")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Workspace isolation contract tests.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--case", choices=("build", "dist", "no_global_write"), required=True)
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    if args.case == "build":
        return case_build(repo_root)
    if args.case == "dist":
        return case_dist(repo_root)
    return case_no_global_write(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
