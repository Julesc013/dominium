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


def _run_auditx(repo_root, *args):
    tool = os.path.join(repo_root, "tools", "auditx", "auditx.py")
    cmd = [sys.executable, tool]
    cmd.extend(args)
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


def main():
    parser = argparse.ArgumentParser(description="AuditX tool smoke tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    scan = _run_auditx(repo_root, "scan")
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

    findings_path = os.path.join(repo_root, "docs", "audit", "auditx", "FINDINGS.json")
    invariant_path = os.path.join(repo_root, "docs", "audit", "auditx", "INVARIANT_MAP.json")
    promotion_path = os.path.join(repo_root, "docs", "audit", "auditx", "PROMOTION_CANDIDATES.json")
    trends_path = os.path.join(repo_root, "docs", "audit", "auditx", "TRENDS.json")
    run_meta_path = os.path.join(repo_root, "docs", "audit", "auditx", "RUN_META.json")
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

    findings_hash_before, _ = _canonical_hash(findings_path)
    invariant_hash_before, _ = _canonical_hash(invariant_path)
    promotion_hash_before, _ = _canonical_hash(promotion_path)
    trends_hash_before, _ = _canonical_hash(trends_path)

    rescan = _run_auditx(repo_root, "scan")
    if rescan.returncode != 0:
        print("auditx rescan failed rc={}".format(rescan.returncode))
        print(rescan.stdout)
        return 1
    findings_hash_after, _ = _canonical_hash(findings_path)
    invariant_hash_after, _ = _canonical_hash(invariant_path)
    promotion_hash_after, _ = _canonical_hash(promotion_path)
    trends_hash_after, _ = _canonical_hash(trends_path)
    if findings_hash_before != findings_hash_after:
        print("FINDINGS.json canonical hash drift across rescans")
        print("before={}".format(findings_hash_before))
        print("after={}".format(findings_hash_after))
        return 1
    if invariant_hash_before != invariant_hash_after:
        print("INVARIANT_MAP.json canonical hash drift across rescans")
        print("before={}".format(invariant_hash_before))
        print("after={}".format(invariant_hash_after))
        return 1
    if promotion_hash_before != promotion_hash_after:
        print("PROMOTION_CANDIDATES.json canonical hash drift across rescans")
        print("before={}".format(promotion_hash_before))
        print("after={}".format(promotion_hash_after))
        return 1
    if trends_hash_before != trends_hash_after:
        print("TRENDS.json canonical hash drift across rescans")
        print("before={}".format(trends_hash_before))
        print("after={}".format(trends_hash_after))
        return 1

    changed = _run_auditx(repo_root, "scan", "--changed-only")
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

    print("auditx tools smoke OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
