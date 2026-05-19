#!/usr/bin/env python3
from __future__ import print_function

import argparse
import os
import sys


REQUIRED_DOCS = [
    "contracts/schema/life/SPEC_LIFE_CONTINUITY.md",
    "contracts/schema/life/SPEC_DEATH_AND_ESTATE.md",
    "contracts/schema/life/SPEC_CONTROL_AUTHORITY.md",
    "contracts/schema/life/SPEC_CONTINUATION_POLICIES.md",
    "contracts/schema/life/SPEC_BIRTH_LINEAGE_OVERVIEW.md",
    "contracts/schema/domain/civilization/SPEC_COHORTS_MINIMAL.md",
    "contracts/schema/domain/civilization/SPEC_NEEDS_MINIMAL.md",
    "contracts/schema/domain/civilization/SPEC_POPULATION_COHORTS.md",
    "contracts/schema/domain/civilization/SPEC_HOUSEHOLDS.md",
    "contracts/schema/domain/civilization/SPEC_MIGRATION.md",
    "contracts/schema/domain/civilization/SPEC_CITIES.md",
    "contracts/schema/domain/civilization/SPEC_BUILDINGS_MACHINES.md",
    "contracts/schema/domain/civilization/SPEC_PRODUCTION_CHAINS.md",
    "contracts/schema/domain/civilization/SPEC_LOGISTICS_FLOWS.md",
    "contracts/schema/governance/SPEC_JURISDICTIONS.md",
    "contracts/schema/governance/SPEC_LEGITIMACY.md",
    "contracts/schema/governance/SPEC_POLICY_SYSTEM.md",
    "contracts/schema/governance/SPEC_ENFORCEMENT.md",
    "contracts/schema/governance/SPEC_STANDARD_RESOLUTION_GOV.md",
    "contracts/schema/knowledge/SPEC_KNOWLEDGE_ITEMS.md",
    "contracts/schema/knowledge/SPEC_RESEARCH_PROCESSES.md",
    "contracts/schema/knowledge/SPEC_DIFFUSION.md",
    "contracts/schema/knowledge/SPEC_SECRECY.md",
    "contracts/schema/technology/SPEC_TECH_EFFECTS.md",
    "contracts/schema/technology/SPEC_TECH_PREREQUISITES.md",
    "contracts/schema/scale/SPEC_SCALE_DOMAINS.md",
    "contracts/schema/scale/SPEC_INTERPLANETARY_LOGISTICS.md",
    "contracts/schema/scale/SPEC_INTERSTELLAR_LOGISTICS.md",
    "contracts/schema/scale/SPEC_SCALE_TIME_WARP.md",
    "docs/specs/CIV0a_SURVIVAL_LOOP.md",
    "docs/guides/OFFLINE_AND_LOCAL_MP.md",
    "docs/specs/CIV0_POPULATION_GENESIS.md",
    "docs/specs/CIV1_CITIES_INFRA.md",
    "docs/specs/CIV2_GOVERNANCE.md",
    "docs/specs/CIV3_KNOWLEDGE_TECH.md",
    "docs/specs/CIV4_SCALE_AND_LOGISTICS.md",
    "docs/ci/DETERMINISM_TEST_MATRIX.md",
    "docs/policies/VALIDATION_AND_GOVERNANCE.md",
]

REQUIRED_TEST_SOURCES = [
    "tests/game/life/dom_life_continuation_tests.cpp",
    "tests/game/life/dom_life_death_pipeline_tests.cpp",
    "tests/game/life/dom_life_birth_tests.cpp",
    "tests/game/life/dom_life_remains_salvage_tests.cpp",
    "tests/game/civ0a/dom_civ0a_survival_tests.cpp",
    "tests/game/civ0/dom_civ0_population_tests.cpp",
    "tests/game/civ1/dom_civ1_city_infra_tests.cpp",
    "tests/game/civ2/civ2_governance_tests.cpp",
    "tests/game/civ3/dom_civ3_knowledge_tests.cpp",
    "tests/game/civ4/dom_civ4_scale_tests.cpp",
    "tests/game/mp0/dom_mp0_parity_tests.cpp",
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
    matrix_path = os.path.join(repo_root, "docs", "ci", "CI_ENFORCEMENT_MATRIX.md")
    try:
        with open(matrix_path, "r", errors="ignore") as handle:
            content = handle.read()
    except IOError:
        failures.append("CI matrix missing: docs/ci/CI_ENFORCEMENT_MATRIX.md")
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
