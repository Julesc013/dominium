#!/usr/bin/env python3
"""Rank draft move-wave candidates from reconciliation evidence."""

from __future__ import print_function

import argparse
import json
import sys
from pathlib import Path

from root_recycling_common import load_json, write_json


PREFERRED = {
    "ide": 100,
    "performance": 95,
    "validation": 75,
    "governance": 60,
    "meta": 55,
}

SENSITIVE_FLAGS = {
    "identity_sensitive",
    "pack_identity",
    "profile_identity",
    "bundle_identity",
    "authority_sensitive",
    "security_sensitive",
    "safety_sensitive",
    "spec_sensitive",
    "runtime_sensitive",
    "network_sensitive",
    "deterministic_sensitive",
    "ABI_sensitive",
    "build_sensitive",
}


def risk_value(risk_counts):
    if risk_counts.get("protected", 0):
        return "protected"
    if risk_counts.get("high", 0):
        return "high"
    if risk_counts.get("unknown", 0):
        return "unknown"
    if risk_counts.get("medium", 0):
        return "medium"
    return "low"


def reference_complexity(count):
    if count == 0:
        return "none"
    if count < 10:
        return "low"
    if count < 50:
        return "medium"
    return "high"


def score_root(root):
    name = root["root"]
    score = PREFERRED.get(name, 10)
    sensitivity = root.get("sensitivity_counts", {})
    sensitive_total = sum(int(sensitivity.get(flag, 0)) for flag in SENSITIVE_FLAGS)
    preserve_unknown = int(root.get("fate_counts", {}).get("preserve_unknown", 0))
    refs = int(root.get("reference_count", 0))
    if not root.get("inventory_present") or not root.get("classification_present") or not root.get("salvage_map_present"):
        return -1000
    if root.get("apply_allowed") or root.get("approval_status") not in ("not_approved", "draft"):
        return -1000
    score -= min(sensitive_total, 100)
    score -= min(preserve_unknown // 5, 80)
    score -= min(refs, 80)
    if risk_value(root.get("risk_counts", {})) in ("protected", "high"):
        score -= 100
    return score


def select(reconciliation):
    candidates = []
    for root in reconciliation.get("roots", []):
        score = score_root(root)
        risk = risk_value(root.get("risk_counts", {}))
        subtree = "docs-or-evidence-only subset"
        sensitivity = "docs/tooling" if root["root"] in PREFERRED else "protected_or_unknown"
        if root["root"] == "ide":
            risk = "low"
            subtree = "docs/architecture/IDE_PROJECTIONS.md only; keep ide/manifests deferred"
            sensitivity = "docs/projection"
        elif root["root"] == "performance":
            subtree = "performance docs/evidence subset only; Python helpers deferred"
            sensitivity = "tooling/performance"
        refs = reference_complexity(root.get("reference_count", 0))
        recommendation = "plan_move" if score > 0 and risk not in ("protected", "high", "unknown") else "defer"
        if score <= 0:
            recommendation = "inventory_more" if root["root"] in PREFERRED else "defer"
        candidates.append({
            "root": root["root"],
            "subtree": subtree,
            "score": score,
            "risk": risk,
            "value": "medium" if root["root"] in PREFERRED else "low",
            "reference_complexity": refs,
            "sensitivity": sensitivity,
            "validation_coverage": "medium",
            "reversibility": "easy" if root["root"] in ("ide", "performance") else "medium",
            "recommended_action": recommendation,
            "apply_allowed": False,
            "approval_status": "not_approved",
        })
    candidates.sort(key=lambda item: (-item["score"], item["root"]))
    selected = next((item for item in candidates if item["recommended_action"] == "plan_move"), None)
    if selected is None and candidates:
        selected = {
            "root": None,
            "subtree": None,
            "risk": None,
            "recommended_action": "inventory_more",
            "reason": "No candidate is low-risk enough for move planning.",
        }
    else:
        selected = dict(selected)
        selected["reason"] = "Selected as the narrowest low-risk docs/projection/evidence candidate; still not approved for application."
    return {
        "schema_version": "dominium.aide.move_wave_candidates.v1",
        "task_id": "AIDE-ROOT-06",
        "candidates": candidates,
        "selected": selected,
        "moves_applied": False,
        "deletes_applied": False,
        "renames_applied": False,
        "reference_rewrites_applied": False,
        "apply_allowed": False,
        "approval_status": "not_approved",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--reconciliation", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    rec_path = Path(args.reconciliation)
    if not rec_path.is_absolute():
        rec_path = repo_root / rec_path
    data = select(load_json(rec_path))
    if args.out:
        out = Path(args.out)
        if not out.is_absolute():
            out = repo_root / out
        write_json(out, data)
    if args.json or not args.out:
        sys.stdout.write(json.dumps(data, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
