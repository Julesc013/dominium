#!/usr/bin/env python3
from __future__ import print_function

import argparse
import os
import sys


REQUIRED_DOCS = [
    "schema/life/SPEC_LIFE_CONTINUITY.md",
    "schema/life/SPEC_DEATH_AND_ESTATE.md",
    "schema/life/SPEC_CONTROL_AUTHORITY.md",
    "schema/life/SPEC_CONTINUATION_POLICIES.md",
    "schema/life/SPEC_BIRTH_LINEAGE_OVERVIEW.md",
    "schema/civ/SPEC_COHORTS_MINIMAL.md",
    "schema/civ/SPEC_NEEDS_MINIMAL.md",
    "schema/civ/SPEC_POPULATION_COHORTS.md",
    "schema/civ/SPEC_HOUSEHOLDS.md",
    "schema/civ/SPEC_MIGRATION.md",
    "schema/civ/SPEC_CITIES.md",
    "schema/civ/SPEC_BUILDINGS_MACHINES.md",
    "schema/civ/SPEC_PRODUCTION_CHAINS.md",
    "schema/civ/SPEC_LOGISTICS_FLOWS.md",
    "schema/governance/SPEC_JURISDICTIONS.md",
    "schema/governance/SPEC_LEGITIMACY.md",
    "schema/governance/SPEC_POLICY_SYSTEM.md",
    "schema/governance/SPEC_ENFORCEMENT.md",
    "schema/governance/SPEC_STANDARD_RESOLUTION_GOV.md",
    "schema/knowledge/SPEC_KNOWLEDGE_ITEMS.md",
    "schema/knowledge/SPEC_RESEARCH_PROCESSES.md",
    "schema/knowledge/SPEC_DIFFUSION.md",
    "schema/knowledge/SPEC_SECRECY.md",
    "schema/technology/SPEC_TECH_EFFECTS.md",
    "schema/technology/SPEC_TECH_PREREQUISITES.md",
    "schema/scale/SPEC_SCALE_DOMAINS.md",
    "schema/scale/SPEC_INTERPLANETARY_LOGISTICS.md",
    "schema/scale/SPEC_INTERSTELLAR_LOGISTICS.md",
    "schema/scale/SPEC_SCALE_TIME_WARP.md",
    "docs/CIV0a_SURVIVAL_LOOP.md",
    "docs/OFFLINE_AND_LOCAL_MP.md",
    "docs/CIV0_POPULATION_GENESIS.md",
    "docs/CIV1_CITIES_INFRA.md",
    "docs/CIV2_GOVERNANCE.md",
    "docs/CIV3_KNOWLEDGE_TECH.md",
    "docs/CIV4_SCALE_AND_LOGISTICS.md",
    "docs/DETERMINISM_TEST_MATRIX.md",
    "docs/VALIDATION_AND_GOVERNANCE.md",
]

REQUIRED_TEST_SOURCES = [
    "game/tests/life/dom_life_continuation_tests.cpp",
    "game/tests/life/dom_life_death_pipeline_tests.cpp",
    "game/tests/life/dom_life_birth_tests.cpp",
    "game/tests/life/dom_life_remains_salvage_tests.cpp",
    "game/tests/civ0a/dom_civ0a_survival_tests.cpp",
    "game/tests/civ0/dom_civ0_population_tests.cpp",
    "game/tests/civ1/dom_civ1_city_infra_tests.cpp",
    "game/tests/civ2/civ2_governance_tests.cpp",
    "game/tests/civ3/dom_civ3_knowledge_tests.cpp",
    "game/tests/civ4/dom_civ4_scale_tests.cpp",
    "game/tests/mp0/dom_mp0_parity_tests.cpp",
]

REQUIRED_CI_IDS = [
    "LIFE-CONT-DET-001",
    "LIFE-CONT-AUTH-001",
    "LIFE-CONT-NOFAB-001",
    "LIFE-DEATH-DET-001",
    "LIFE-LEDGER-001",
    "LIFE-INH-SCHED-001",
    "LIFE-ESTATE-AUTH-001",
    "LIFE-EPIS-001",
    "LIFE-REPLAY-001",
    "LIFE-BIRTH-DET-001",
    "LIFE-BIRTH-RES-001",
    "LIFE-LINEAGE-DET-001",
    "LIFE-COHORT-001",
    "LIFE-BIRTH-EPIS-001",
    "LIFE-BIRTH-BATCH-001",
    "LIFE-REM-DET-001",
    "LIFE-REM-DECAY-001",
    "LIFE-REM-RIGHTS-001",
    "LIFE-REM-LEDGER-001",
    "LIFE-REM-EPIS-001",
    "LIFE-REM-COUNT-001",
    "CIV0a-EVENT-001",
    "CIV0a-NOGLOB-001",
    "CIV0-NOGLOB-001",
    "CIV0-NEXTDUE-001",
    "CIV0-DET-001",
    "CIV1-PROD-DET-001",
    "CIV1-BATCH-001",
    "CIV1-LOG-DET-001",
    "CIV1-NOGLOB-001",
    "CIV1-FID-001",
    "CIV2-JURIS-DET-001",
    "CIV2-NEXTDUE-001",
    "CIV2-LEGIT-DET-001",
    "CIV2-POLICY-T4-001",
    "CIV2-STAND-RES-001",
    "CIV2-EPIS-001",
    "CIV3-RES-DET-001",
    "CIV3-BATCH-001",
    "CIV3-DIFF-DET-001",
    "CIV3-SECRECY-001",
    "CIV3-TECH-001",
    "CIV3-NOGLOB-001",
    "CIV4-FLOW-DET-001",
    "CIV4-BATCH-001",
    "CIV4-INT-001",
    "CIV4-WARP-001",
    "CIV4-HANDOFF-001",
    "MP0-PARITY-001",
    "MP0-LOCKSTEP-001",
    "MP0-SERVERAUTH-001",
    "GOV-VAL-001",
    "GOV-VAL-REND-002",
    "GOV-VAL-EPIS-003",
    "GOV-VAL-PROV-004",
    "GOV-VAL-PERF-005",
]


def repo_root_from_script():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


def check_files(repo_root, rel_paths, label, failures):
    for rel in rel_paths:
        path = os.path.join(repo_root, rel)
        if not os.path.isfile(path):
            failures.append("{0} missing: {1}".format(label, rel))


def check_ci_matrix(repo_root, failures):
    matrix_path = os.path.join(repo_root, "docs", "CI_ENFORCEMENT_MATRIX.md")
    try:
        with open(matrix_path, "r", errors="ignore") as handle:
            content = handle.read()
    except IOError:
        failures.append("CI matrix missing: docs/CI_ENFORCEMENT_MATRIX.md")
        return
    for check_id in REQUIRED_CI_IDS:
        if check_id not in content:
            failures.append("CI matrix missing ID: {0}".format(check_id))


def main():
    parser = argparse.ArgumentParser(description="Phase 6 audit gates (docs + CI matrix + test assets).")
    parser.add_argument("--repo-root", default=None, help="Repository root path")
    args = parser.parse_args()

    repo_root = args.repo_root or repo_root_from_script()
    failures = []

    check_files(repo_root, REQUIRED_DOCS, "doc", failures)
    check_files(repo_root, REQUIRED_TEST_SOURCES, "test source", failures)
    check_ci_matrix(repo_root, failures)

    if failures:
        for item in sorted(failures):
            print("PH6-AUDIT-001: {0}".format(item))
        return 1

    print("PH6-AUDIT-001: Phase 6 audit checks OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
