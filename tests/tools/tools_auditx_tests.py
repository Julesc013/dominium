import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys


REQUIRED_FINDING_KEYS = (
    "finding_id",
    "category",
    "severity",
    "confidence",
    "status",
    "location",
    "evidence",
    "suggested_classification",
    "recommended_action",
    "related_invariants",
    "related_paths",
    "fingerprint",
)

CANONICAL_FORBIDDEN_KEYS = {
    "created_utc",
    "last_reviewed",
    "generated_utc",
    "duration_ms",
    "host_name",
    "machine_name",
    "scan_id",
    "run_id",
}

CANONICAL_ARTIFACTS = (
    "FINDINGS.json",
    "INVARIANT_MAP.json",
    "PROMOTION_CANDIDATES.json",
    "TRENDS.json",
)


def _run_cmd(cmd, cwd):
    return subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _run_auditx(repo_root, *args, output_root=""):
    tool = os.path.join(repo_root, "tools", "auditx", "auditx.py")
    cmd = [sys.executable, tool]
    cmd.extend(args)
    if output_root:
        cmd.extend(["--output-root", output_root])
    cmd.extend(["--repo-root", repo_root, "--format", "json"])
    return _run_cmd(cmd, cwd=repo_root)


def _parse_json_stdout(result):
    try:
        return json.loads(result.stdout or "{}")
    except ValueError:
        return None


def _load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _canonical_hash(path):
    payload = _load_json(path)
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest(), payload


def _case_output_dir(repo_root, case_name):
    return os.path.join(repo_root, ".dominium.local", "ctest", "auditx", case_name)


def _clean_case_output_dir(repo_root, case_name):
    output_dir = _case_output_dir(repo_root, case_name)
    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)
    return output_dir


def _artifact_path(output_dir, name):
    return os.path.join(output_dir, name)


def _walk_forbidden_keys(node, failures, prefix=""):
    if isinstance(node, dict):
        for key, value in node.items():
            full = "{}.{}".format(prefix, key) if prefix else key
            if key in CANONICAL_FORBIDDEN_KEYS:
                failures.append(full)
            _walk_forbidden_keys(value, failures, prefix=full)
        return
    if isinstance(node, list):
        for idx, value in enumerate(node):
            _walk_forbidden_keys(value, failures, prefix="{}[{}]".format(prefix, idx))


def _validate_findings_payload(path):
    try:
        payload = _load_json(path)
    except (OSError, ValueError):
        return "unable to parse {}".format(path)

    if payload.get("artifact_class") != "CANONICAL":
        return "artifact_class must be CANONICAL in {}".format(path)
    findings = payload.get("findings")
    if not isinstance(findings, list):
        return "findings list missing in {}".format(path)
    for idx, finding in enumerate(findings[:200]):
        missing = [key for key in REQUIRED_FINDING_KEYS if key not in finding]
        if missing:
            return "finding {} missing keys {}".format(idx, ",".join(missing))

    failures = []
    _walk_forbidden_keys(payload, failures)
    if failures:
        return "canonical payload includes forbidden run-meta keys: {}".format(", ".join(failures[:5]))
    return ""


def _validate_invariant_payload(path):
    try:
        payload = _load_json(path)
    except (OSError, ValueError):
        return "unable to parse {}".format(path)
    if payload.get("artifact_class") != "CANONICAL":
        return "artifact_class must be CANONICAL in {}".format(path)
    if "invariants" not in payload or not isinstance(payload.get("invariants"), dict):
        return "invariants map missing in {}".format(path)
    failures = []
    _walk_forbidden_keys(payload, failures)
    if failures:
        return "canonical invariant map includes forbidden run-meta keys: {}".format(", ".join(failures[:5]))
    return ""


def _validate_promotion_payload(path):
    try:
        payload = _load_json(path)
    except (OSError, ValueError):
        return "unable to parse {}".format(path)
    if payload.get("artifact_class") != "CANONICAL":
        return "artifact_class must be CANONICAL in {}".format(path)
    candidates = payload.get("candidates")
    if not isinstance(candidates, list):
        return "candidates list missing in {}".format(path)
    for idx, item in enumerate(candidates[:200]):
        if not isinstance(item, dict):
            return "candidate {} invalid in {}".format(idx, path)
        for required in ("rule_type", "rationale", "evidence_paths", "suggested_ruleset", "risk_score"):
            if required not in item:
                return "candidate {} missing {} in {}".format(idx, required, path)
    failures = []
    _walk_forbidden_keys(payload, failures)
    if failures:
        return "canonical promotion payload includes forbidden run-meta keys: {}".format(", ".join(failures[:5]))
    return ""


def _validate_trends_payload(path):
    try:
        payload = _load_json(path)
    except (OSError, ValueError):
        return "unable to parse {}".format(path)
    if payload.get("artifact_class") != "CANONICAL":
        return "artifact_class must be CANONICAL in {}".format(path)
    if "category_frequency" not in payload or not isinstance(payload.get("category_frequency"), dict):
        return "category_frequency missing in {}".format(path)
    if "severity_distribution" not in payload or not isinstance(payload.get("severity_distribution"), dict):
        return "severity_distribution missing in {}".format(path)
    failures = []
    _walk_forbidden_keys(payload, failures)
    if failures:
        return "canonical trends payload includes forbidden run-meta keys: {}".format(", ".join(failures[:5]))
    return ""


def _validate_run_meta(path):
    try:
        payload = _load_json(path)
    except (OSError, ValueError):
        return "unable to parse {}".format(path)
    if payload.get("artifact_class") != "RUN_META":
        return "artifact_class must be RUN_META in {}".format(path)
    if payload.get("status") != "DERIVED":
        return "status must be DERIVED in {}".format(path)
    if "generated_utc" not in payload:
        return "RUN_META must include generated_utc in {}".format(path)
    return ""


def _validate_artifacts(repo_root):
    output_dir = _clean_case_output_dir(repo_root, "scan_artifacts")
    scan = _run_auditx(repo_root, "scan", output_root=output_dir)
    if scan.returncode != 0:
        print("auditx scan failed rc={}".format(scan.returncode))
        print(scan.stdout)
        print(scan.stderr)
        return 1
    payload = _parse_json_stdout(scan)
    if payload is None or payload.get("result") != "scan_complete":
        print("auditx scan payload invalid")
        print(scan.stdout)
        return 1

    findings_path = _artifact_path(output_dir, "FINDINGS.json")
    invariant_path = _artifact_path(output_dir, "INVARIANT_MAP.json")
    promotion_path = _artifact_path(output_dir, "PROMOTION_CANDIDATES.json")
    trends_path = _artifact_path(output_dir, "TRENDS.json")
    run_meta_path = _artifact_path(output_dir, "RUN_META.json")
    for required in (findings_path, invariant_path, promotion_path, trends_path, run_meta_path):
        if not os.path.isfile(required):
            print("missing artifact {}".format(required))
            return 1

    for validator, path in (
        (_validate_findings_payload, findings_path),
        (_validate_invariant_payload, invariant_path),
        (_validate_promotion_payload, promotion_path),
        (_validate_trends_payload, trends_path),
        (_validate_run_meta, run_meta_path),
    ):
        error = validator(path)
        if error:
            print(error)
            return 1
    print("auditx scan artifacts OK")
    return 0


def _canonical_hashes(output_dir):
    hashes = {}
    for name in CANONICAL_ARTIFACTS:
        path = _artifact_path(output_dir, name)
        if not os.path.isfile(path):
            raise OSError("missing artifact {}".format(path))
        hashes[name], _payload = _canonical_hash(path)
    return hashes


def _hash_stability(repo_root):
    output_dir = _clean_case_output_dir(repo_root, "hash_stability")
    baseline = _run_auditx(repo_root, "scan", output_root=output_dir)
    if baseline.returncode != 0:
        print("auditx baseline scan failed rc={}".format(baseline.returncode))
        print(baseline.stdout)
        return 1
    try:
        hashes_before = _canonical_hashes(output_dir)
    except (OSError, ValueError) as exc:
        print(str(exc))
        return 1
    rescan = _run_auditx(repo_root, "scan", output_root=output_dir)
    if rescan.returncode != 0:
        print("auditx rescan failed rc={}".format(rescan.returncode))
        print(rescan.stdout)
        return 1
    try:
        hashes_after = _canonical_hashes(output_dir)
    except (OSError, ValueError) as exc:
        print(str(exc))
        return 1
    for name in CANONICAL_ARTIFACTS:
        if hashes_before[name] != hashes_after[name]:
            print("{} canonical hash drift across rescans".format(name))
            print("before={}".format(hashes_before[name]))
            print("after={}".format(hashes_after[name]))
            return 1
    print("auditx canonical hash stability OK")
    return 0


def _changed_only(repo_root):
    output_dir = _clean_case_output_dir(repo_root, "changed_only")
    changed = _run_auditx(repo_root, "scan", "--changed-only", output_root=output_dir)
    changed_payload = _parse_json_stdout(changed)
    if shutil.which("git"):
        if changed.returncode != 0:
            print("auditx changed-only failed rc={}".format(changed.returncode))
            print(changed.stdout)
            print(changed.stderr)
            return 1
        if changed_payload is None or changed_payload.get("result") != "scan_complete":
            print("changed-only payload invalid")
            print(changed.stdout)
            return 1
    else:
        if changed.returncode == 0:
            print("changed-only expected deterministic refusal without git")
            return 1
        if changed_payload is None or changed_payload.get("refusal_code") != "refuse.git_unavailable":
            print("changed-only refusal payload invalid")
            print(changed.stdout)
            return 1
    print("auditx changed-only OK")
    return 0


def main():
    parser = argparse.ArgumentParser(description="AuditX tool smoke tests.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--case",
        choices=("all", "scan_artifacts", "hash_stability", "changed_only"),
        default="all",
    )
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    cases = {
        "scan_artifacts": _validate_artifacts,
        "hash_stability": _hash_stability,
        "changed_only": _changed_only,
    }
    selected = ("scan_artifacts", "hash_stability", "changed_only") if args.case == "all" else (args.case,)
    for case_name in selected:
        result = cases[case_name](repo_root)
        if result != 0:
            return result
    print("auditx tools smoke OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
