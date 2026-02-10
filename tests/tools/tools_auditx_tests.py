import argparse
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
    "created_utc",
    "fingerprint",
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


def _git_status(repo_root):
    if not shutil.which("git"):
        return None
    result = _run_cmd(["git", "status", "--porcelain"], cwd=repo_root)
    if result.returncode != 0:
        return None
    return [line.strip() for line in (result.stdout or "").splitlines() if line.strip()]


def _validate_findings_payload(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return "unable to parse {}".format(path)

    findings = payload.get("findings")
    if not isinstance(findings, list):
        return "findings list missing in {}".format(path)
    if "status" not in payload or "last_reviewed" not in payload:
        return "status metadata missing in {}".format(path)
    for idx, finding in enumerate(findings[:200]):
        missing = [key for key in REQUIRED_FINDING_KEYS if key not in finding]
        if missing:
            return "finding {} missing keys {}".format(idx, ",".join(missing))
    return ""


def main():
    parser = argparse.ArgumentParser(description="AuditX tool smoke tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    baseline_status = _git_status(repo_root)

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
    if not os.path.isfile(findings_path):
        print("missing findings artifact {}".format(findings_path))
        return 1
    validation_error = _validate_findings_payload(findings_path)
    if validation_error:
        print(validation_error)
        return 1
    post_scan_status = _git_status(repo_root)

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

    # Restore canonical findings artifacts and assert no tracked file drift.
    rescan = _run_auditx(repo_root, "scan")
    if rescan.returncode != 0:
        print("auditx rescan failed rc={}".format(rescan.returncode))
        return 1

    final_status = _git_status(repo_root)
    if post_scan_status is not None and final_status is not None and final_status != post_scan_status:
        print("auditx output determinism violated (status drift across rescans)")
        print("post_scan={}".format(post_scan_status))
        print("final={}".format(final_status))
        return 1
    if baseline_status is not None and baseline_status == [] and final_status is not None and final_status != []:
        print("auditx read-only contract violated on clean tree")
        print("final={}".format(final_status))
        return 1

    print("auditx tools smoke OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
