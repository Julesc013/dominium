"""STRICT test: auditx scan emits valid deterministic findings payload."""

from __future__ import annotations

import json
import os
import subprocess
import sys


TEST_ID = "testx.auditx.smoke"
TEST_TAGS = ["strict", "auditx", "smoke"]


def run(repo_root: str):
    out_rel = "build/auditx/smoke"
    out_abs = os.path.join(repo_root, out_rel.replace("/", os.sep))
    os.makedirs(out_abs, exist_ok=True)
    findings_path = os.path.join(out_abs, "FINDINGS.json")
    if os.path.isfile(findings_path):
        try:
            os.remove(findings_path)
        except OSError:
            pass

    proc = subprocess.run(
        [
            sys.executable,
            os.path.join(repo_root, "tools", "auditx", "auditx.py"),
            "scan",
            "--repo-root",
            repo_root,
            "--format",
            "json",
            "--output-root",
            out_rel,
        ],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    if int(proc.returncode) != 0:
        tail = (proc.stdout or "").splitlines()[-15:]
        return {"status": "fail", "message": "auditx scan failed: {}".format(" | ".join(tail))}
    if not os.path.isfile(findings_path):
        return {"status": "fail", "message": "missing FINDINGS.json from auditx scan"}

    try:
        payload = json.load(open(findings_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "invalid JSON in auditx FINDINGS.json"}
    rows = payload.get("findings")
    if not isinstance(rows, list):
        return {"status": "fail", "message": "findings payload missing findings list"}

    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.auditx.model import validate_finding_record

    for idx, row in enumerate(rows[:80]):
        if not isinstance(row, dict):
            return {"status": "fail", "message": "finding {} is not object".format(idx)}
        errors = validate_finding_record(row)
        if errors:
            return {"status": "fail", "message": "finding {} invalid: {}".format(idx, "; ".join(errors[:3]))}
    return {"status": "pass", "message": "auditx smoke scan produced valid finding structure"}
