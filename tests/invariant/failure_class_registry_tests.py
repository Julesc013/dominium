import argparse
import json
import os
import sys


def _load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _collect_test_names(text):
    names = set()
    marker = "dom_add_testx(NAME "
    offset = 0
    while True:
        idx = text.find(marker, offset)
        if idx < 0:
            break
        start = idx + len(marker)
        end = text.find("\n", start)
        if end < 0:
            break
        name = text[start:end].strip().split()[0]
        if name:
            names.add(name)
        offset = end + 1
    return names


def main():
    parser = argparse.ArgumentParser(description="Failure class registry contract tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    registry_path = os.path.join(repo_root, "data", "registries", "failure_classes.json")
    playbooks_path = os.path.join(repo_root, "data", "registries", "remediation_playbooks.json")
    if not os.path.isfile(registry_path):
        print("missing failure class registry")
        return 1
    if not os.path.isfile(playbooks_path):
        print("missing remediation playbook registry")
        return 1

    registry = _load_json(registry_path)
    playbooks = _load_json(playbooks_path)
    rows = registry.get("record", {}).get("classes", [])
    pb_rows = playbooks.get("record", {}).get("playbooks", [])
    if not isinstance(rows, list) or not rows:
        print("failure class list missing")
        return 1
    playbook_ids = {str(row.get("playbook_id", "")).strip() for row in pb_rows if isinstance(row, dict)}

    cmake_paths = (
        os.path.join(repo_root, "tests", "invariant", "CMakeLists.txt"),
        os.path.join(repo_root, "tests", "tools", "CMakeLists.txt"),
        os.path.join(repo_root, "tests", "regression", "historical_blockers", "CMakeLists.txt"),
    )
    all_tests = set()
    for path in cmake_paths:
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            all_tests.update(_collect_test_names(handle.read()))

    violations = []
    for row in rows:
        if not isinstance(row, dict):
            violations.append("non-object row in failure class registry")
            continue
        failure_class_id = str(row.get("failure_class_id", "")).strip()
        playbook_id = str(row.get("remediation_playbook_id", "")).strip()
        explanation = str(row.get("explanation_doc", "")).strip()
        tests = row.get("regression_tests", [])

        if not failure_class_id:
            violations.append("missing failure_class_id")
            continue
        if playbook_id not in playbook_ids:
            violations.append("{} references missing playbook {}".format(failure_class_id, playbook_id))
        if not explanation:
            violations.append("{} missing explanation_doc".format(failure_class_id))
        else:
            explanation_path = os.path.join(repo_root, explanation.split("#", 1)[0].replace("/", os.sep))
            if not os.path.isfile(explanation_path):
                violations.append("{} explanation doc missing {}".format(failure_class_id, explanation))
        if not isinstance(tests, list) or not tests:
            violations.append("{} missing regression_tests".format(failure_class_id))
        else:
            for test_name in tests:
                if str(test_name).strip() not in all_tests:
                    violations.append("{} references unknown regression test {}".format(failure_class_id, test_name))

    if violations:
        for item in violations:
            sys.stderr.write("FAIL: {}\n".format(item))
        return 1

    print("failure_class_registry_tests=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
