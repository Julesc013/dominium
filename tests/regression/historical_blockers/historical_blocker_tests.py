import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile


def _run(cmd, cwd, env=None):
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )


def _canonical_hash(path):
    payload = json.load(open(path, "r", encoding="utf-8"))
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def case_tool_discovery(repo_root):
    gate_script = os.path.join(repo_root, "scripts", "dev", "gate.py")
    env = dict(os.environ)
    env["PATH"] = ""
    env.pop("DOM_HOST_PATH", None)
    tmp_dir = tempfile.mkdtemp(prefix="dom-hb-tooldiscovery-")
    try:
        proc = _run(
            [
                sys.executable,
                gate_script,
                "doctor",
                "--repo-root",
                repo_root,
                "--workspace-id",
                "hb-tooldiscovery",
            ],
            cwd=tmp_dir,
            env=env,
        )
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        return 1
    if "hb-tooldiscovery" not in proc.stdout:
        sys.stderr.write("FAIL: workspace id missing from doctor output\n")
        return 1
    print("historical_blocker_tool_discovery=ok")
    return 0


def case_derived_nondeterminism(repo_root):
    auditx_tool = os.path.join(repo_root, "tools", "auditx", "auditx.py")
    if not os.path.isfile(auditx_tool):
        print("historical_blocker_derived_nondeterminism=ok")
        return 0

    for _ in range(2):
        proc = _run([sys.executable, auditx_tool, "scan", "--repo-root", repo_root, "--format", "json"], cwd=repo_root)
        if proc.returncode != 0:
            sys.stderr.write(proc.stdout)
            return 1

    findings = os.path.join(repo_root, "docs", "audit", "auditx", "FINDINGS.json")
    invariant_map = os.path.join(repo_root, "docs", "audit", "auditx", "INVARIANT_MAP.json")
    if not os.path.isfile(findings) or not os.path.isfile(invariant_map):
        sys.stderr.write("FAIL: auditx canonical artifacts missing\n")
        return 1
    before = (_canonical_hash(findings), _canonical_hash(invariant_map))
    proc = _run([sys.executable, auditx_tool, "scan", "--repo-root", repo_root, "--format", "json"], cwd=repo_root)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        return 1
    after = (_canonical_hash(findings), _canonical_hash(invariant_map))
    if before != after:
        sys.stderr.write("FAIL: canonical audit artifacts drifted across runs\n")
        return 1
    print("historical_blocker_derived_nondeterminism=ok")
    return 0


def case_direct_gate_invocation(repo_root):
    allowed_paths = {
        "scripts/dev/gate.py",
        "scripts/dev/gate_shim.py",
        "scripts/dev/run_repox.py",
        "scripts/dev/run_testx.py",
        "scripts/dev/testx_proof_engine.py",
        "scripts/ci/check_repox_rules.py",
    }
    scan_roots = [
        os.path.join("scripts", "dev"),
        os.path.join("scripts", "ci"),
        os.path.join(".github", "workflows"),
    ]
    roots = [os.path.join(repo_root, rel) for rel in scan_roots]
    extensions = (".py", ".sh", ".cmd", ".bat", ".ps1", ".yml", ".yaml")
    violations = []
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                if not filename.lower().endswith(extensions):
                    continue
                abs_path = os.path.join(dirpath, filename)
                rel = os.path.relpath(abs_path, repo_root).replace("\\", "/")
                if rel in allowed_paths:
                    continue
                try:
                    text = open(abs_path, "r", encoding="utf-8", errors="ignore").read()
                except OSError:
                    continue
                lower = text.lower()
                if "scripts/ci/check_repox_rules.py" in lower:
                    violations.append(rel)
                    continue
                if "tool_ui_bind --check" in lower:
                    violations.append(rel)
                    continue
                if "ctest " in lower or "ctest\n" in lower:
                    violations.append(rel)
                    continue
    if violations:
        for rel in sorted(set(violations))[:20]:
            sys.stderr.write("FAIL: direct gate invocation pattern in {}\n".format(rel))
        return 1
    print("historical_blocker_direct_gate_invocation=ok")
    return 0


def case_stage_token(repo_root):
    repox_script = os.path.join(repo_root, "scripts", "ci", "check_repox_rules.py")
    proc = _run([sys.executable, repox_script, "--repo-root", repo_root], cwd=repo_root)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        return 1
    if "INV-CAPABILITY-NO-LEGACY-GATING-TOKENS" in proc.stdout:
        sys.stderr.write("FAIL: stage-token invariant reported in RepoX output\n")
        return 1
    print("historical_blocker_stage_token=ok")
    return 0


def case_identity_drift(repo_root):
    fingerprint = os.path.join(repo_root, "docs", "audit", "identity_fingerprint.json")
    explanation = os.path.join(repo_root, "docs", "audit", "identity_fingerprint_explanation.md")
    if not os.path.isfile(fingerprint):
        sys.stderr.write("FAIL: missing identity fingerprint artifact\n")
        return 1
    if not os.path.isfile(explanation):
        sys.stderr.write("FAIL: missing identity fingerprint explanation\n")
        return 1
    print("historical_blocker_identity_drift=ok")
    return 0


def case_identity_explanation_required(repo_root):
    repox = os.path.join(repo_root, "scripts", "ci", "check_repox_rules.py")
    explanation = os.path.join(repo_root, "docs", "audit", "identity_fingerprint_explanation.md")
    if not os.path.isfile(explanation):
        sys.stderr.write("FAIL: missing identity explanation artifact\n")
        return 1
    with open(explanation, "r", encoding="utf-8", errors="replace") as handle:
        text = handle.read().strip()
    if "identity_fingerprint" not in text:
        sys.stderr.write("FAIL: identity explanation missing identity_fingerprint reference\n")
        return 1

    backup = explanation + ".anb_tmp"
    if os.path.isfile(backup):
        os.remove(backup)
    os.replace(explanation, backup)
    try:
        proc = _run([sys.executable, repox, "--repo-root", repo_root], cwd=repo_root)
        failed = proc.returncode != 0 and "INV-IDENTITY-CHANGE-EXPLANATION" in proc.stdout
    finally:
        if os.path.isfile(backup):
            os.replace(backup, explanation)
    if not failed:
        sys.stderr.write("FAIL: RepoX did not enforce identity explanation requirement\n")
        return 1
    print("test_identity_explanation_required=ok")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Historical blocker regression tests.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--case",
        choices=(
            "tool_discovery",
            "derived_nondeterminism",
            "direct_gate_invocation",
            "stage_token",
            "identity_drift",
            "identity_explanation_required",
        ),
        required=True,
    )
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    if args.case == "tool_discovery":
        return case_tool_discovery(repo_root)
    if args.case == "derived_nondeterminism":
        return case_derived_nondeterminism(repo_root)
    if args.case == "direct_gate_invocation":
        return case_direct_gate_invocation(repo_root)
    if args.case == "stage_token":
        return case_stage_token(repo_root)
    if args.case == "identity_explanation_required":
        return case_identity_explanation_required(repo_root)
    return case_identity_drift(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
