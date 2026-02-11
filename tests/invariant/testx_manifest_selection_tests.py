import argparse
import json
import os
import sys


def _load_runner(repo_root):
    scripts_dev = os.path.join(repo_root, "scripts", "dev")
    if scripts_dev not in sys.path:
        sys.path.insert(0, scripts_dev)
    import testx_proof_engine

    return testx_proof_engine


def _require(condition, message):
    if condition:
        return True
    sys.stderr.write("FAIL: {}\n".format(message))
    return False


def run_selection_logic(repo_root):
    runner = _load_runner(repo_root)
    registry, refusal = runner.load_suite_registry(repo_root)
    if not _require(registry is not None, "failed to load suite registry: {}".format(refusal)):
        return 1
    suite = registry["index"].get("testx_fast")
    if not _require(isinstance(suite, dict), "missing testx_fast suite"):
        return 1

    manifest = {
        "required_test_tags": ["manifest", "workspace"],
    }
    selection = runner.select_tests_for_suite("testx_fast", suite, manifest)
    selected = set(selection.get("selected_tests", []))
    required_tags = set(selection.get("required_test_tags", []))
    checks = [
        _require("manifest" in required_tags, "manifest tag missing from required tags"),
        _require("workspace" in required_tags, "workspace tag missing from required tags"),
        _require("test_manifest_selection_logic" in selected, "manifest tag did not select manifest test"),
        _require("test_workspace_isolation_build" in selected, "workspace tag did not select workspace test"),
    ]
    if not all(checks):
        return 1
    print("test_manifest_selection_logic=ok")
    return 0


def run_fallback_when_missing(repo_root):
    runner = _load_runner(repo_root)
    registry, refusal = runner.load_suite_registry(repo_root)
    if not _require(registry is not None, "failed to load suite registry: {}".format(refusal)):
        return 1
    suite = registry["index"].get("testx_fast")
    if not _require(isinstance(suite, dict), "missing testx_fast suite"):
        return 1

    selection = runner.select_tests_for_suite("testx_fast", suite, manifest_payload=None)
    selected = set(selection.get("selected_tests", []))
    tags = set(selection.get("required_test_tags", []))

    defaults = suite.get("extensions", {}).get("default_tests", [])
    checks = [
        _require(bool(defaults), "default_tests missing from suite registry"),
        _require(set(defaults).issubset(selected), "fallback selection missing default tests"),
        _require(bool(tags), "fallback required_test_tags should not be empty"),
        _require(selection.get("manifest_used") is False, "fallback should report manifest_used=false"),
    ]
    if not all(checks):
        return 1
    print("test_manifest_fallback_when_missing=ok")
    return 0


def main():
    parser = argparse.ArgumentParser(description="TestX manifest selection tests.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--case", choices=("selection_logic", "fallback_when_missing"), required=True)
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    if args.case == "selection_logic":
        return run_selection_logic(repo_root)
    return run_fallback_when_missing(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
