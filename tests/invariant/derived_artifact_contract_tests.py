import argparse
import hashlib
import json
import os
import subprocess
import sys


FORBIDDEN_KEYS = {
    "generated_utc",
    "last_reviewed",
    "duration_ms",
    "machine_name",
    "host_name",
    "run_id",
    "scan_id",
    "timestamp",
    "timestamps",
}


def _load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _canonical_hash(path, artifact_type):
    if artifact_type == "json":
        payload = _load_json(path)
        blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    else:
        with open(path, "rb") as handle:
            blob = handle.read()
    return hashlib.sha256(blob).hexdigest()


def _canonical_artifacts(repo_root):
    registry_path = os.path.join(repo_root, "data", "registries", "derived_artifacts.json")
    payload = _load_json(registry_path)
    artifacts = payload.get("record", {}).get("artifacts", [])
    out = []
    for entry in artifacts:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("artifact_class", "")).strip() != "CANONICAL":
            continue
        rel = str(entry.get("path", "")).strip()
        if not rel:
            continue
        artifact_type = "json" if rel.lower().endswith(".json") else "blob"
        out.append({"path": rel.replace("\\", "/"), "type": artifact_type})
    unique = {}
    for item in out:
        unique[item["path"]] = item
    return [unique[key] for key in sorted(unique)]


def _walk_forbidden(node, path, failures):
    if isinstance(node, dict):
        for key, value in node.items():
            next_path = "{}.{}".format(path, key) if path else key
            if key in FORBIDDEN_KEYS:
                failures.append(next_path)
            _walk_forbidden(value, next_path, failures)
        return
    if isinstance(node, list):
        for idx, value in enumerate(node):
            next_path = "{}[{}]".format(path, idx)
            _walk_forbidden(value, next_path, failures)


def _run_auditx_scan(repo_root):
    tool = os.path.join(repo_root, "tools", "auditx", "auditx.py")
    if not os.path.isfile(tool):
        return 0
    result = subprocess.run(
        [sys.executable, tool, "scan", "--repo-root", repo_root, "--format", "json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    return int(result.returncode)


def case_hash_stability(repo_root):
    artifacts = _canonical_artifacts(repo_root)
    if not artifacts:
        print("test_canonical_artifact_hash_stability=ok")
        return 0

    if _run_auditx_scan(repo_root) != 0:
        print("auditx scan failed while preparing canonical artifacts")
        return 1

    before = {}
    for artifact in artifacts:
        rel = artifact["path"]
        abs_path = os.path.join(repo_root, rel.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            continue
        before[rel] = _canonical_hash(abs_path, artifact["type"])

    if _run_auditx_scan(repo_root) != 0:
        print("auditx scan failed on second run")
        return 1

    after = {}
    artifact_index = {item["path"]: item for item in artifacts}
    for rel in sorted(before):
        abs_path = os.path.join(repo_root, rel.replace("/", os.sep))
        after[rel] = _canonical_hash(abs_path, artifact_index[rel]["type"])

    if before != after:
        print("canonical artifact hash stability mismatch")
        return 1

    print("test_canonical_artifact_hash_stability=ok")
    return 0


def case_no_timestamp(repo_root):
    artifacts = _canonical_artifacts(repo_root)
    failures = []
    for artifact in artifacts:
        if artifact["type"] != "json":
            continue
        rel = artifact["path"]
        abs_path = os.path.join(repo_root, rel.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            continue
        try:
            payload = _load_json(abs_path)
        except (OSError, ValueError):
            failures.append("{}:invalid_json".format(rel))
            continue
        _walk_forbidden(payload, rel, failures)
    if failures:
        print("forbidden timestamp-like fields found in canonical artifacts:")
        for item in failures[:20]:
            print(item)
        return 1

    print("test_no_timestamp_in_canonical=ok")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Derived artifact contract tests.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--case", choices=("hash_stability", "no_timestamp"), required=True)
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    if args.case == "hash_stability":
        return case_hash_stability(repo_root)
    return case_no_timestamp(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
