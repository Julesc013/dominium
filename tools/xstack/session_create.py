#!/usr/bin/env python3
"""CLI: create deterministic SessionSpec + UniverseIdentity + UniverseState artifacts."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.registry_compile.constants import DEFAULT_BUNDLE_ID  # noqa: E402
from tools.xstack.sessionx.creator import (  # noqa: E402
    DEFAULT_BUDGET_POLICY_ID,
    DEFAULT_EXPERIENCE_ID,
    DEFAULT_FIDELITY_POLICY_ID,
    DEFAULT_LAW_PROFILE_ID,
    DEFAULT_PARAMETER_BUNDLE_ID,
    DEFAULT_PRIVILEGE_LEVEL,
    DEFAULT_SCENARIO_ID,
    create_session_spec,
)


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def main() -> int:
    parser = argparse.ArgumentParser(description="Create deterministic session bootstrap artifacts under saves/<save_id>/.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--save-id", required=True)
    parser.add_argument("--bundle", default=DEFAULT_BUNDLE_ID)
    parser.add_argument("--scenario-id", default=DEFAULT_SCENARIO_ID)
    parser.add_argument("--mission-id", default="")
    parser.add_argument("--experience-id", default=DEFAULT_EXPERIENCE_ID)
    parser.add_argument("--law-profile-id", default=DEFAULT_LAW_PROFILE_ID)
    parser.add_argument("--parameter-bundle-id", default=DEFAULT_PARAMETER_BUNDLE_ID)
    parser.add_argument("--budget-policy-id", default=DEFAULT_BUDGET_POLICY_ID)
    parser.add_argument("--fidelity-policy-id", default=DEFAULT_FIDELITY_POLICY_ID)
    parser.add_argument("--rng-root", action="append", default=[])
    parser.add_argument("--rng-seed-string", default="seed.session.default")
    parser.add_argument("--universe-identity-file", default="")
    parser.add_argument("--universe-seed-string", default="seed.universe.default")
    parser.add_argument("--universe-id", default="")
    parser.add_argument("--entitlement", action="append", default=[])
    parser.add_argument("--epistemic-scope-id", default="epistemic.lab.placeholder")
    parser.add_argument("--visibility-level", default="placeholder")
    parser.add_argument("--privilege-level", default=DEFAULT_PRIVILEGE_LEVEL, choices=("observer", "operator", "system"))
    parser.add_argument("--compile-outputs", default="on", choices=("on", "off"))
    parser.add_argument("--saves-root", default="saves", help=argparse.SUPPRESS)
    args = parser.parse_args()

    repo_root = _repo_root(args.repo_root)
    result = create_session_spec(
        repo_root=repo_root,
        save_id=str(args.save_id),
        bundle_id=str(args.bundle),
        scenario_id=str(args.scenario_id),
        mission_id=str(args.mission_id),
        experience_id=str(args.experience_id),
        law_profile_id=str(args.law_profile_id),
        parameter_bundle_id=str(args.parameter_bundle_id),
        budget_policy_id=str(args.budget_policy_id),
        fidelity_policy_id=str(args.fidelity_policy_id),
        rng_seed_string=str(args.rng_seed_string),
        rng_roots=list(args.rng_root or []),
        universe_identity_path=str(args.universe_identity_file),
        universe_seed_string=str(args.universe_seed_string),
        universe_id=str(args.universe_id),
        entitlements=list(args.entitlement or []),
        epistemic_scope_id=str(args.epistemic_scope_id),
        visibility_level=str(args.visibility_level),
        privilege_level=str(args.privilege_level),
        compile_outputs=str(args.compile_outputs).strip().lower() != "off",
        saves_root_rel=str(args.saves_root),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("result") == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
