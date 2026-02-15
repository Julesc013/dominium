"""E8 Precision leak smell analyzer."""

from __future__ import annotations

import json
import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E8_PRECISION_LEAK_SMELL"
OBSERVATION_PATH = "tools/xstack/sessionx/observation.py"
NET_FILES = (
    "src/net/policies/policy_server_authoritative.py",
    "src/net/srz/shard_coordinator.py",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    return open(abs_path, "r", encoding="utf-8").read()


def _read_json_object(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid_json"
    if not isinstance(payload, dict):
        return {}, "invalid_root"
    return payload, ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    try:
        observation_text = _read_text(repo_root, OBSERVATION_PATH)
    except OSError:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.precision_leak_smell",
                severity="RISK",
                confidence=0.9,
                file_path=OBSERVATION_PATH,
                line=1,
                evidence=["observation kernel file missing for precision leak checks"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NET-PERCEIVED-ONLY"],
                related_paths=[OBSERVATION_PATH],
            )
        )
        return findings

    required_tokens = (
        "def _apply_precision_quantization",
        "position_quantization_mm",
        "orientation_quantization_mdeg",
        "_quantize_int",
    )
    for token in required_tokens:
        if token not in observation_text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="net.precision_leak_smell",
                    severity="RISK",
                    confidence=0.88,
                    file_path=OBSERVATION_PATH,
                    line=1,
                    evidence=["missing precision-guard token '{}'".format(token)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NET-PERCEIVED-ONLY"],
                    related_paths=[OBSERVATION_PATH],
                )
            )

    float_leak_pattern = re.compile(r"(\{:\.\d+f\}|round\()")
    for rel_path in NET_FILES:
        try:
            text = _read_text(repo_root, rel_path)
        except OSError:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            lower = str(line).lower()
            if "perceived_delta" not in lower and "camera" not in lower:
                continue
            if float_leak_pattern.search(str(line)):
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="net.precision_leak_smell",
                        severity="WARN",
                        confidence=0.7,
                        file_path=rel_path,
                        line=line_no,
                        evidence=[
                            "potential non-registry precision formatting in net path",
                            str(line).strip()[:200],
                        ],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-NET-PERCEIVED-ONLY"],
                        related_paths=[rel_path],
                    )
                )

    registry_path = "data/registries/epistemic_policy_registry.json"
    registry_payload, registry_err = _read_json_object(repo_root, registry_path)
    if registry_err:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.precision_leak_smell",
                severity="WARN",
                confidence=0.65,
                file_path=registry_path,
                line=1,
                evidence=["unable to parse epistemic policy registry for precision rules coverage"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="DOC_FIX",
                related_invariants=["INV-EPISTEMIC-POLICY-REQUIRED"],
                related_paths=[registry_path],
            )
        )
    else:
        rows = (((registry_payload.get("record") or {}).get("policies")) or [])
        for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("epistemic_policy_id", ""))):
            policy_id = str(row.get("epistemic_policy_id", "")).strip()
            if not policy_id:
                continue
            allowed = set(str(item).strip() for item in (row.get("allowed_observation_channels") or []) if str(item).strip())
            if "ch.camera.state" not in allowed:
                continue
            precision_rows = [
                dict(item)
                for item in (row.get("max_precision_rules") or [])
                if isinstance(item, dict) and str(item.get("channel_id", "")).strip() == "ch.camera.state"
            ]
            if not precision_rows:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="net.precision_leak_smell",
                        severity="WARN",
                        confidence=0.74,
                        file_path=registry_path,
                        line=1,
                        evidence=[
                            "camera channel enabled without precision rule coverage",
                            "policy_id={}".format(policy_id),
                        ],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-EPISTEMIC-POLICY-REQUIRED"],
                        related_paths=[registry_path],
                    )
                )

    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )

