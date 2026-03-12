#!/usr/bin/env python3
"""Verify MVP stress proofs, replay invariants, and regression lock artifacts."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.mvp.stress_gate_common import (  # noqa: E402
    DEFAULT_BASELINE_REL,
    DEFAULT_FINAL_DOC_REL,
    DEFAULT_HASHES_REL,
    DEFAULT_MVP_STRESS_SEED,
    DEFAULT_PROOF_REPORT_REL,
    DEFAULT_REPORT_REL,
    load_json_if_present,
    maybe_load_cached_mvp_stress_proof_report,
    maybe_load_cached_mvp_stress_report,
    run_all_mvp_stress,
    verify_mvp_stress_proofs,
    write_mvp_stress_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--seed", type=int, default=DEFAULT_MVP_STRESS_SEED)
    parser.add_argument("--report-path", default=DEFAULT_REPORT_REL)
    parser.add_argument("--hashes-path", default=DEFAULT_HASHES_REL)
    parser.add_argument("--proof-report-path", default=DEFAULT_PROOF_REPORT_REL)
    parser.add_argument("--baseline-path", default=DEFAULT_BASELINE_REL)
    parser.add_argument("--final-doc-path", default=DEFAULT_FINAL_DOC_REL)
    parser.add_argument("--gate-results-path", default="")
    parser.add_argument("--write-baseline", action="store_true")
    parser.add_argument("--update-tag", default="")
    parser.add_argument("--prefer-cached", action="store_true")
    args = parser.parse_args(argv)

    report = {}
    if bool(args.prefer_cached):
        report = maybe_load_cached_mvp_stress_report(
            args.repo_root,
            report_path=str(args.report_path),
        )
    if not report:
        report = run_all_mvp_stress(args.repo_root, seed=int(args.seed))

    baseline_payload = load_json_if_present(args.repo_root, str(args.baseline_path))
    gate_results = load_json_if_present(args.repo_root, str(args.gate_results_path)) if str(args.gate_results_path).strip() else {}

    proof_report = {}
    if bool(args.prefer_cached):
        proof_report = maybe_load_cached_mvp_stress_proof_report(
            args.repo_root,
            report=report,
            proof_report_path=str(args.proof_report_path),
        )
    if not proof_report:
        proof_report = verify_mvp_stress_proofs(
            args.repo_root,
            report=report,
            baseline_payload=baseline_payload,
        )

    written = write_mvp_stress_outputs(
        args.repo_root,
        report=report,
        report_path=str(args.report_path),
        hashes_path=str(args.hashes_path),
        proof_report=proof_report,
        proof_report_path=str(args.proof_report_path),
        baseline_path=str(args.baseline_path),
        final_doc_path=str(args.final_doc_path),
        update_baseline=bool(args.write_baseline),
        update_tag=str(args.update_tag),
        gate_results=gate_results,
    )
    payload = dict(proof_report)
    payload["report"] = report
    payload["written_outputs"] = written
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if str(proof_report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
