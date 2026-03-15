#!/usr/bin/env python3
"""Run the deterministic MVP smoke harness and write the regression artifacts."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.mvp.mvp_smoke_common import (  # noqa: E402
    DEFAULT_BASELINE_REL,
    DEFAULT_FINAL_DOC_REL,
    DEFAULT_HASHES_REL,
    DEFAULT_MVP_SMOKE_SEED,
    DEFAULT_REPORT_REL,
    DEFAULT_SCENARIO_REL,
    load_json_if_present,
    maybe_load_cached_mvp_smoke_report,
    run_mvp_smoke,
    write_generated_mvp_smoke_inputs,
    write_mvp_smoke_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--seed", type=int, default=DEFAULT_MVP_SMOKE_SEED)
    parser.add_argument("--scenario-path", default=DEFAULT_SCENARIO_REL)
    parser.add_argument("--hashes-path", default=DEFAULT_HASHES_REL)
    parser.add_argument("--report-path", default=DEFAULT_REPORT_REL)
    parser.add_argument("--final-doc-path", default=DEFAULT_FINAL_DOC_REL)
    parser.add_argument("--baseline-path", default=DEFAULT_BASELINE_REL)
    parser.add_argument("--gate-results-path", default="")
    parser.add_argument("--write-baseline", action="store_true")
    parser.add_argument("--update-tag", default="")
    parser.add_argument("--prefer-cached", action="store_true")
    args = parser.parse_args(argv)

    generated = write_generated_mvp_smoke_inputs(
        args.repo_root,
        seed=int(args.seed),
        scenario_path=str(args.scenario_path),
        hashes_path=str(args.hashes_path),
    )
    scenario = dict(generated.get("scenario") or {})
    expected_hashes = dict(generated.get("expected_hashes") or {})
    baseline_payload = load_json_if_present(args.repo_root, str(args.baseline_path))
    gate_results = load_json_if_present(args.repo_root, str(args.gate_results_path)) if str(args.gate_results_path).strip() else {}

    report = {}
    if bool(args.prefer_cached):
        report = maybe_load_cached_mvp_smoke_report(
            args.repo_root,
            scenario=scenario,
            expected_hashes=expected_hashes,
            report_path=str(args.report_path),
        )
    if not report:
        report = run_mvp_smoke(
            args.repo_root,
            seed=int(args.seed),
            scenario=scenario,
            expected_hashes=expected_hashes,
            baseline_payload=baseline_payload,
        )

    written = write_mvp_smoke_outputs(
        args.repo_root,
        report=report,
        report_path=str(args.report_path),
        final_doc_path=str(args.final_doc_path),
        baseline_path=str(args.baseline_path),
        update_baseline=bool(args.write_baseline),
        update_tag=str(args.update_tag),
        gate_results=gate_results,
    )
    summary = {
        "result": str(report.get("result", "")).strip(),
        "scenario_id": str(report.get("scenario_id", "")).strip(),
        "scenario_seed": int(report.get("scenario_seed", args.seed) or args.seed),
        "refusal_count": int(report.get("refusal_count", 0) or 0),
        "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
        "written_outputs": {
            "report_path": str(written.get("report_path", "")).strip(),
            "final_doc_path": str(written.get("final_doc_path", "")).strip(),
            "baseline_path": str(written.get("baseline_path", "")).strip(),
            "baseline_written": bool(written.get("baseline_written", False)),
            "deterministic_fingerprint": str(written.get("deterministic_fingerprint", "")).strip(),
        },
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
