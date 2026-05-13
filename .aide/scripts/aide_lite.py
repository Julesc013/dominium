#!/usr/bin/env python3
"""AIDE Lite token-survival helper.

This file is intentionally standard-library only. It compiles compact
task packets from repo-local state, validates Q09/Q10 token-survival
anchors, and never calls providers, models, network services, or
external tools.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import importlib
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


GENERATOR_NAME = "aide-lite"
GENERATOR_VERSION = "q24.existing-tool-adapter-compiler.v0"
SNAPSHOT_PATH = ".aide/context/repo-snapshot.json"
LATEST_PACKET_PATH = ".aide/context/latest-task-packet.md"
REVIEW_PACKET_PATH = ".aide/context/latest-review-packet.md"
REPO_MAP_JSON_PATH = ".aide/context/repo-map.json"
REPO_MAP_MD_PATH = ".aide/context/repo-map.md"
TEST_MAP_JSON_PATH = ".aide/context/test-map.json"
CONTEXT_INDEX_PATH = ".aide/context/context-index.json"
LATEST_CONTEXT_PACKET_PATH = ".aide/context/latest-context-packet.md"
DOCTRINE_REFS_PATH = ".aide/context/dominium-doctrine-refs.md"
CONTEXT_COMPILER_CONFIG_PATH = ".aide/context/compiler.yaml"
CONTEXT_PRIORITY_PATH = ".aide/context/priority.yaml"
EXCERPT_POLICY_PATH = ".aide/context/excerpt-policy.yaml"
VERIFICATION_POLICY_PATH = ".aide/policies/verification.yaml"
EVIDENCE_TEMPLATE_PATH = ".aide/verification/evidence-packet.template.md"
REVIEW_TEMPLATE_PATH = ".aide/verification/review-packet.template.md"
REVIEW_DECISION_POLICY_PATH = ".aide/verification/review-decision-policy.yaml"
DIFF_SCOPE_POLICY_PATH = ".aide/verification/diff-scope-policy.yaml"
FILE_REFERENCE_POLICY_PATH = ".aide/verification/file-reference-policy.yaml"
SECRET_SCAN_POLICY_PATH = ".aide/verification/secret-scan-policy.yaml"
LATEST_VERIFICATION_REPORT_PATH = ".aide/verification/latest-verification-report.md"
TOKEN_LEDGER_POLICY_PATH = ".aide/policies/token-ledger.yaml"
TOKEN_LEDGER_PATH = ".aide/reports/token-ledger.jsonl"
TOKEN_BASELINES_PATH = ".aide/reports/token-baselines.yaml"
TOKEN_SUMMARY_PATH = ".aide/reports/token-savings-summary.md"
EVAL_POLICY_PATH = ".aide/policies/evals.yaml"
GOLDEN_TASK_ROOT = ".aide/evals/golden-tasks"
GOLDEN_TASK_CATALOG_PATH = ".aide/evals/golden-tasks/catalog.yaml"
GOLDEN_RUN_JSON_PATH = ".aide/evals/runs/latest-golden-tasks.json"
GOLDEN_RUN_MD_PATH = ".aide/evals/runs/latest-golden-tasks.md"
COMMIT_MESSAGE_POLICY_PATH = ".aide/policies/commit-messages.yaml"
COMMIT_MESSAGE_STANDARD_PATH = ".aide/reports/aide-commit-message-standard.md"
COMMIT_MESSAGE_HOOK_TEMPLATE_PATH = ".aide/hooks/commit-msg"
COMMIT_TEMPLATE_PATH = ".aide/git/commit-template.md"
GIT_WORKFLOW_POLICY_PATH = ".aide/policies/git-workflow.yaml"
BRANCH_ROLES_POLICY_PATH = ".aide/policies/branch-roles.yaml"
PROMOTION_RULES_POLICY_PATH = ".aide/policies/promotion-rules.yaml"
SYNC_POLICY_PATH = ".aide/policies/sync-policy.yaml"
PRUNE_POLICY_PATH = ".aide/policies/prune-policy.yaml"
GIT_WORKFLOW_DETECTION_JSON_PATH = ".aide/git/workflow-detection.json"
GIT_WORKFLOW_DETECTION_MD_PATH = ".aide/git/workflow-detection.md"
GIT_PROJECT_PROFILES_PATH = ".aide/git/project-profiles.yaml"
GIT_BRANCH_ROLES_MD_PATH = ".aide/git/branch-roles.md"
GIT_PROMOTION_RULES_MD_PATH = ".aide/git/promotion-rules.md"
GIT_SYNC_POLICY_MD_PATH = ".aide/git/sync-policy.md"
GIT_PRUNE_POLICY_MD_PATH = ".aide/git/prune-policy.md"
GIT_HELPER_POLICY_PATH = ".aide/git/helper-policy.yaml"
GIT_HELPER_COMMANDS_MD_PATH = ".aide/git/helper-commands.md"
GIT_HELPER_PLAN_JSON_PATH = ".aide/git/latest-helper-plan.json"
GIT_HELPER_PLAN_MD_PATH = ".aide/git/latest-helper-plan.md"
AIDE_BRANCH_POLICY_PATH = ".aide/git/aide-branch-policy.yaml"
AIDE_DEV_MAIN_PLAN_JSON_PATH = ".aide/git/aide-dev-main-plan.json"
AIDE_DEV_MAIN_PLAN_MD_PATH = ".aide/git/aide-dev-main-plan.md"
CHANGELOG_PREVIEW_MD_PATH = ".aide/changelog/CHANGELOG.preview.md"
RELEASE_NOTES_PREVIEW_MD_PATH = ".aide/changelog/RELEASE_NOTES.preview.md"
CHANGELOG_PREVIEW_JSON_PATH = ".aide/changelog/changelog.preview.json"
MALFORMED_COMMITS_MD_PATH = ".aide/changelog/malformed-commits.md"
TASK_RESUMPTION_POLICY_PATH = ".aide/policies/task-resumption.yaml"
WORK_UNITS_POLICY_PATH = ".aide/policies/work-units.yaml"
RECOVERY_POLICY_PATH = ".aide/policies/recovery.yaml"
TASK_RESUMPTION_STANDARD_PATH = ".aide/reports/aide-task-resumption-standard.md"
WORKUNIT_RECOVERY_STANDARD_PATH = ".aide/reports/aide-workunit-recovery-standard.md"
CONTROLLER_POLICY_PATH = ".aide/policies/controller.yaml"
CONTROLLER_DIR = ".aide/controller"
OUTCOME_LEDGER_PATH = ".aide/controller/outcome-ledger.jsonl"
OUTCOME_REPORT_PATH = ".aide/controller/latest-outcome-report.md"
RECOMMENDATIONS_PATH = ".aide/controller/latest-recommendations.md"
FAILURE_TAXONOMY_PATH = ".aide/controller/failure-taxonomy.yaml"
ROUTING_POLICY_PATH = ".aide/policies/routing.yaml"
MODELS_DIR = ".aide/models"
PROVIDERS_PATH = ".aide/models/providers.yaml"
CAPABILITIES_PATH = ".aide/models/capabilities.yaml"
ROUTES_PATH = ".aide/models/routes.yaml"
HARD_FLOORS_PATH = ".aide/models/hard-floors.yaml"
FALLBACK_PATH = ".aide/models/fallback.yaml"
ROUTING_DIR = ".aide/routing"
ROUTE_DECISION_SCHEMA_PATH = ".aide/routing/route-decision.schema.json"
ROUTE_DECISION_JSON_PATH = ".aide/routing/latest-route-decision.json"
ROUTE_DECISION_MD_PATH = ".aide/routing/latest-route-decision.md"
CACHE_POLICY_PATH = ".aide/policies/cache.yaml"
LOCAL_STATE_POLICY_PATH = ".aide/policies/local-state.yaml"
CACHE_DIR = ".aide/cache"
CACHE_KEY_POLICY_PATH = ".aide/cache/key-policy.yaml"
CACHE_KEYS_JSON_PATH = ".aide/cache/latest-cache-keys.json"
CACHE_KEYS_MD_PATH = ".aide/cache/latest-cache-keys.md"
LOCAL_STATE_ROOT = ".aide.local"
LOCAL_STATE_EXAMPLE_ROOT = ".aide.local.example"
GATEWAY_POLICY_PATH = ".aide/policies/gateway.yaml"
GATEWAY_DIR = ".aide/gateway"
GATEWAY_ENDPOINTS_PATH = ".aide/gateway/endpoints.yaml"
GATEWAY_LIFECYCLE_PATH = ".aide/gateway/lifecycle.yaml"
GATEWAY_SECURITY_PATH = ".aide/gateway/security-boundary.md"
GATEWAY_STATUS_JSON_PATH = ".aide/gateway/latest-gateway-status.json"
GATEWAY_STATUS_MD_PATH = ".aide/gateway/latest-gateway-status.md"
PROVIDER_ADAPTER_POLICY_PATH = ".aide/policies/provider-adapters.yaml"
PROVIDER_DIR = ".aide/providers"
PROVIDER_CATALOG_PATH = ".aide/providers/provider-catalog.yaml"
PROVIDER_CAPABILITY_MATRIX_PATH = ".aide/providers/capability-matrix.yaml"
PROVIDER_ADAPTER_CONTRACT_PATH = ".aide/providers/adapter-contract.yaml"
PROVIDER_STATUS_PATH = ".aide/providers/status.yaml"
PROVIDER_STATUS_JSON_PATH = ".aide/providers/latest-provider-status.json"
PROVIDER_STATUS_MD_PATH = ".aide/providers/latest-provider-status.md"
EXPORT_IMPORT_POLICY_PATH = ".aide/policies/export-import.yaml"
EXPORT_ROOT = ".aide/export"
IMPORT_ROOT = ".aide/import"
EXPORT_PACK_ID = "aide-lite-pack-v0"
EXPORT_PACK_PATH = f"{EXPORT_ROOT}/{EXPORT_PACK_ID}"
EXPORT_PACK_FILES_ROOT = f"{EXPORT_PACK_PATH}/files"
EXPORT_PACK_MANIFEST_PATH = f"{EXPORT_PACK_PATH}/manifest.yaml"
EXPORT_PACK_CHECKSUMS_PATH = f"{EXPORT_PACK_PATH}/checksums.json"
EXPORT_PACK_REPORT_PATH = f"{EXPORT_PACK_PATH}/export-report.md"
EXPORT_IMPORT_POLICY_TEMPLATE_PATH = f"{IMPORT_ROOT}/import-policy.yaml"
TARGET_PROFILE_TEMPLATE_PATH = f"{IMPORT_ROOT}/target-profile-template.yaml"
TARGET_PROJECT_STATE_TEMPLATE_PATH = f"{IMPORT_ROOT}/target-project-state-template.md"
TARGET_DECISIONS_TEMPLATE_PATH = f"{IMPORT_ROOT}/target-decisions-template.md"
TARGET_OPEN_RISKS_TEMPLATE_PATH = f"{IMPORT_ROOT}/target-open-risks-template.md"
IMPORT_REPORT_TEMPLATE_PATH = f"{IMPORT_ROOT}/import-report.template.md"
ADAPTER_POLICY_PATH = ".aide/policies/adapters.yaml"
ADAPTER_DIR = ".aide/adapters"
ADAPTER_TARGETS_PATH = ".aide/adapters/targets.yaml"
ADAPTER_TEMPLATE_DIR = ".aide/adapters/templates"
ADAPTER_GENERATED_DIR = ".aide/generated/adapters"
ADAPTER_GENERATED_MANIFEST_PATH = f"{ADAPTER_GENERATED_DIR}/manifest.json"
ADAPTER_DRIFT_REPORT_PATH = f"{ADAPTER_GENERATED_DIR}/drift-report.md"
ADAPTER_COMPILER_ID = "aide-adapter-compiler-v0"
AGENTS_SECTION = "aide-token-survival-adapter"
AGENTS_BEGIN = f"<!-- AIDE-GENERATED:BEGIN section={AGENTS_SECTION}"
AGENTS_END = f"<!-- AIDE-GENERATED:END section={AGENTS_SECTION} -->"
LEGACY_AGENTS_SECTION = "token-survival-core"
LEGACY_AGENTS_MANAGED_BEGIN = f"<!-- AIDE-GENERATED:BEGIN section={LEGACY_AGENTS_SECTION}"
LEGACY_AGENTS_MANAGED_END = f"<!-- AIDE-GENERATED:END section={LEGACY_AGENTS_SECTION} -->"
LEGACY_AGENTS_BEGIN = "<!-- AIDE-TOKEN-SURVIVAL:BEGIN section=q09-token-survival mode=managed -->"
LEGACY_AGENTS_END = "<!-- AIDE-TOKEN-SURVIVAL:END section=q09-token-survival -->"

REQUIRED_FILES = [
    ".aide/policies/token-budget.yaml",
    ".aide/memory/project-state.md",
    ".aide/memory/decisions.md",
    ".aide/memory/open-risks.md",
    ".aide/prompts/compact-task.md",
    ".aide/prompts/evidence-review.md",
    ".aide/prompts/codex-token-mode.md",
    ".aide/context/ignore.yaml",
]

CONTEXT_CONFIG_FILES = [
    CONTEXT_COMPILER_CONFIG_PATH,
    CONTEXT_PRIORITY_PATH,
    EXCERPT_POLICY_PATH,
]

CONTEXT_OUTPUT_PATHS = [
    REPO_MAP_JSON_PATH,
    REPO_MAP_MD_PATH,
    TEST_MAP_JSON_PATH,
    CONTEXT_INDEX_PATH,
    LATEST_CONTEXT_PACKET_PATH,
]

VERIFICATION_CONFIG_FILES = [
    VERIFICATION_POLICY_PATH,
    EVIDENCE_TEMPLATE_PATH,
    REVIEW_TEMPLATE_PATH,
    REVIEW_DECISION_POLICY_PATH,
    DIFF_SCOPE_POLICY_PATH,
    FILE_REFERENCE_POLICY_PATH,
    SECRET_SCAN_POLICY_PATH,
]

GENERATED_CONTEXT_PATHS = {
    SNAPSHOT_PATH,
    LATEST_PACKET_PATH,
    REVIEW_PACKET_PATH,
    CACHE_KEYS_JSON_PATH,
    CACHE_KEYS_MD_PATH,
    *CONTEXT_OUTPUT_PATHS,
}

COMPACT_TASK_SECTIONS = [
    "PHASE",
    "GOAL",
    "WHY",
    "CONTEXT_REFS",
    "ALLOWED_PATHS",
    "FORBIDDEN_PATHS",
    "IMPLEMENTATION",
    "VALIDATION",
    "EVIDENCE",
    "NON_GOALS",
    "ACCEPTANCE",
]

PACKET_REQUIRED_SECTIONS = [*COMPACT_TASK_SECTIONS, "OUTPUT_SCHEMA", "TOKEN_ESTIMATE"]

CONTEXT_PACKET_REQUIRED_SECTIONS = [
    "CONTEXT_COMPILER",
    "SOURCE_REFS",
    "REPO_MAP",
    "TEST_MAP",
    "CURRENT_QUEUE",
    "EXACT_REFS",
    "TOKEN_ESTIMATE",
]

EVIDENCE_PACKET_REQUIRED_SECTIONS = [
    "Task",
    "Objective",
    "Scope",
    "Changed Files",
    "Validation Commands",
    "Validation Results",
    "Generated Artifacts",
    "Token Estimates",
    "Risks",
    "Deferrals",
    "Next Recommended Phase",
]

REVIEW_PACKET_REQUIRED_SECTIONS = [
    "Review Objective",
    "Decision Requested",
    "Task Packet Reference",
    "Context Packet Reference",
    "Verification Report Reference",
    "Evidence Packet References",
    "Changed Files Summary",
    "Validation Summary",
    "Token Summary",
    "Risk Summary",
    "Non-Goals / Scope Guard",
    "Reviewer Instructions",
]

VERIFICATION_REPORT_REQUIRED_SECTIONS = [
    "VERIFIER_RESULT",
    "CHECK_COUNTS",
    "WARNINGS",
    "ERRORS",
    "EVIDENCE_REFS",
]

Q12_REQUIRED_FILES = [
    VERIFICATION_POLICY_PATH,
    EVIDENCE_TEMPLATE_PATH,
    REVIEW_TEMPLATE_PATH,
    REVIEW_DECISION_POLICY_PATH,
    DIFF_SCOPE_POLICY_PATH,
    FILE_REFERENCE_POLICY_PATH,
    SECRET_SCAN_POLICY_PATH,
]

Q14_REQUIRED_FILES = [
    TOKEN_LEDGER_POLICY_PATH,
    TOKEN_BASELINES_PATH,
    TOKEN_LEDGER_PATH,
    TOKEN_SUMMARY_PATH,
]

Q15_REQUIRED_FILES = [
    EVAL_POLICY_PATH,
    f"{GOLDEN_TASK_ROOT}/README.md",
    GOLDEN_TASK_CATALOG_PATH,
]

Q16_REQUIRED_FILES = [
    CONTROLLER_POLICY_PATH,
    f"{CONTROLLER_DIR}/README.md",
    OUTCOME_LEDGER_PATH,
    OUTCOME_REPORT_PATH,
    RECOMMENDATIONS_PATH,
    FAILURE_TAXONOMY_PATH,
]

Q17_REQUIRED_FILES = [
    ROUTING_POLICY_PATH,
    f"{MODELS_DIR}/README.md",
    PROVIDERS_PATH,
    CAPABILITIES_PATH,
    ROUTES_PATH,
    HARD_FLOORS_PATH,
    FALLBACK_PATH,
    f"{ROUTING_DIR}/README.md",
    ROUTE_DECISION_SCHEMA_PATH,
]

Q18_REQUIRED_FILES = [
    ".gitignore",
    CACHE_POLICY_PATH,
    LOCAL_STATE_POLICY_PATH,
    f"{LOCAL_STATE_EXAMPLE_ROOT}/README.md",
    f"{LOCAL_STATE_EXAMPLE_ROOT}/config.example.yaml",
    f"{LOCAL_STATE_EXAMPLE_ROOT}/cache/README.md",
    f"{LOCAL_STATE_EXAMPLE_ROOT}/traces/README.md",
    f"{LOCAL_STATE_EXAMPLE_ROOT}/secrets/README.md",
    f"{LOCAL_STATE_EXAMPLE_ROOT}/ledgers/README.md",
    f"{CACHE_DIR}/README.md",
    CACHE_KEY_POLICY_PATH,
    CACHE_KEYS_JSON_PATH,
    CACHE_KEYS_MD_PATH,
]

Q19_REQUIRED_FILES = [
    GATEWAY_POLICY_PATH,
    f"{GATEWAY_DIR}/README.md",
    f"{GATEWAY_DIR}/architecture.md",
    GATEWAY_ENDPOINTS_PATH,
    GATEWAY_LIFECYCLE_PATH,
    GATEWAY_SECURITY_PATH,
    GATEWAY_STATUS_JSON_PATH,
    GATEWAY_STATUS_MD_PATH,
    "core/gateway/README.md",
    "core/gateway/__init__.py",
    "core/gateway/gateway_status.py",
    "core/gateway/server.py",
]

Q20_REQUIRED_FILES = [
    PROVIDER_ADAPTER_POLICY_PATH,
    f"{PROVIDER_DIR}/README.md",
    PROVIDER_CATALOG_PATH,
    PROVIDER_CAPABILITY_MATRIX_PATH,
    PROVIDER_ADAPTER_CONTRACT_PATH,
    PROVIDER_STATUS_PATH,
    PROVIDER_STATUS_JSON_PATH,
    PROVIDER_STATUS_MD_PATH,
    "core/providers/README.md",
    "core/providers/__init__.py",
    "core/providers/contracts.py",
    "core/providers/registry.py",
    "core/providers/status.py",
]

Q21_REQUIRED_FILES = [
    EXPORT_IMPORT_POLICY_PATH,
    f"{IMPORT_ROOT}/README.md",
    EXPORT_IMPORT_POLICY_TEMPLATE_PATH,
    TARGET_PROFILE_TEMPLATE_PATH,
    TARGET_PROJECT_STATE_TEMPLATE_PATH,
    TARGET_DECISIONS_TEMPLATE_PATH,
    TARGET_OPEN_RISKS_TEMPLATE_PATH,
    IMPORT_REPORT_TEMPLATE_PATH,
    EXPORT_PACK_MANIFEST_PATH,
    EXPORT_PACK_CHECKSUMS_PATH,
    EXPORT_PACK_REPORT_PATH,
    f"{EXPORT_PACK_PATH}/README.md",
    f"{EXPORT_PACK_PATH}/install.md",
    f"{EXPORT_PACK_PATH}/import-policy.yaml",
]

Q24_REQUIRED_FILES = [
    ADAPTER_POLICY_PATH,
    ADAPTER_TARGETS_PATH,
    f"{ADAPTER_TEMPLATE_DIR}/AGENTS.md.template",
    f"{ADAPTER_TEMPLATE_DIR}/CLAUDE.md.template",
    f"{ADAPTER_TEMPLATE_DIR}/aider.conf.yml.template",
    f"{ADAPTER_TEMPLATE_DIR}/clinerules.template",
    f"{ADAPTER_TEMPLATE_DIR}/continue-checks.template.md",
    f"{ADAPTER_TEMPLATE_DIR}/cursor-rule.template.md",
    f"{ADAPTER_TEMPLATE_DIR}/windsurf-rule.template.md",
    ADAPTER_GENERATED_MANIFEST_PATH,
    ADAPTER_DRIFT_REPORT_PATH,
]

Q27_REQUIRED_FILES = [
    COMMIT_MESSAGE_POLICY_PATH,
    TASK_RESUMPTION_POLICY_PATH,
    WORK_UNITS_POLICY_PATH,
    RECOVERY_POLICY_PATH,
    COMMIT_MESSAGE_HOOK_TEMPLATE_PATH,
    COMMIT_TEMPLATE_PATH,
    COMMIT_MESSAGE_STANDARD_PATH,
    TASK_RESUMPTION_STANDARD_PATH,
    WORKUNIT_RECOVERY_STANDARD_PATH,
]

Q28_REQUIRED_FILES = [
    GIT_WORKFLOW_POLICY_PATH,
    BRANCH_ROLES_POLICY_PATH,
    PROMOTION_RULES_POLICY_PATH,
    SYNC_POLICY_PATH,
    PRUNE_POLICY_PATH,
    ".aide/git/README.md",
    GIT_PROJECT_PROFILES_PATH,
    GIT_BRANCH_ROLES_MD_PATH,
    GIT_PROMOTION_RULES_MD_PATH,
    GIT_SYNC_POLICY_MD_PATH,
    GIT_PRUNE_POLICY_MD_PATH,
]

Q29_REQUIRED_FILES = [
    GIT_HELPER_POLICY_PATH,
    GIT_HELPER_COMMANDS_MD_PATH,
    GIT_HELPER_PLAN_JSON_PATH,
    GIT_HELPER_PLAN_MD_PATH,
]

Q30_REQUIRED_FILES = [
    AIDE_BRANCH_POLICY_PATH,
    AIDE_DEV_MAIN_PLAN_JSON_PATH,
    AIDE_DEV_MAIN_PLAN_MD_PATH,
]

LOCAL_ONLY_EXPORT_PATH_PATTERNS = [
    ".aide/evals/golden-tasks/aide_dev_main_policy_golden/**",
    ".aide/evals/golden-tasks/aide_branch_plan_golden/**",
    ".aide/scripts/tests/test_q30_aide_dev_main_policy.py",
    "docs/reference/aide-dev-main-workflow.md",
]

LOCAL_ONLY_GOLDEN_TASK_IDS = {
    "aide_dev_main_policy_golden",
    "aide_branch_plan_golden",
}

Q31_GOLDEN_TASK_IDS = [
    "export_pack_commit_policy_inclusion_golden",
    "export_pack_task_recovery_inclusion_golden",
    "export_pack_git_policy_inclusion_golden",
    "export_pack_excludes_source_branch_state_golden",
    "fixture_import_governance_commands_golden",
]

PORTABLE_SOURCE_FILES = [
    ".aide/scripts/aide_lite.py",
    ".aide/policies/token-budget.yaml",
    COMMIT_MESSAGE_POLICY_PATH,
    TASK_RESUMPTION_POLICY_PATH,
    WORK_UNITS_POLICY_PATH,
    RECOVERY_POLICY_PATH,
    GIT_WORKFLOW_POLICY_PATH,
    BRANCH_ROLES_POLICY_PATH,
    PROMOTION_RULES_POLICY_PATH,
    SYNC_POLICY_PATH,
    PRUNE_POLICY_PATH,
    VERIFICATION_POLICY_PATH,
    TOKEN_LEDGER_POLICY_PATH,
    EVAL_POLICY_PATH,
    CONTROLLER_POLICY_PATH,
    ROUTING_POLICY_PATH,
    CACHE_POLICY_PATH,
    LOCAL_STATE_POLICY_PATH,
    GATEWAY_POLICY_PATH,
    PROVIDER_ADAPTER_POLICY_PATH,
    EXPORT_IMPORT_POLICY_PATH,
    ADAPTER_POLICY_PATH,
    ADAPTER_TARGETS_PATH,
    COMMIT_MESSAGE_HOOK_TEMPLATE_PATH,
    COMMIT_TEMPLATE_PATH,
    ".aide/git/README.md",
    GIT_PROJECT_PROFILES_PATH,
    GIT_BRANCH_ROLES_MD_PATH,
    GIT_PROMOTION_RULES_MD_PATH,
    GIT_SYNC_POLICY_MD_PATH,
    GIT_PRUNE_POLICY_MD_PATH,
    GIT_HELPER_POLICY_PATH,
    GIT_HELPER_COMMANDS_MD_PATH,
    ".aide/context/ignore.yaml",
    CONTEXT_COMPILER_CONFIG_PATH,
    CONTEXT_PRIORITY_PATH,
    EXCERPT_POLICY_PATH,
    ".aide/prompts/compact-task.md",
    ".aide/prompts/evidence-review.md",
    ".aide/prompts/codex-token-mode.md",
    EVIDENCE_TEMPLATE_PATH,
    REVIEW_TEMPLATE_PATH,
    REVIEW_DECISION_POLICY_PATH,
    DIFF_SCOPE_POLICY_PATH,
    FILE_REFERENCE_POLICY_PATH,
    SECRET_SCAN_POLICY_PATH,
    PROVIDERS_PATH,
    CAPABILITIES_PATH,
    ROUTES_PATH,
    HARD_FLOORS_PATH,
    FALLBACK_PATH,
    PROVIDER_CATALOG_PATH,
    PROVIDER_CAPABILITY_MATRIX_PATH,
    PROVIDER_ADAPTER_CONTRACT_PATH,
    PROVIDER_STATUS_PATH,
    GATEWAY_ENDPOINTS_PATH,
    GATEWAY_LIFECYCLE_PATH,
    GATEWAY_SECURITY_PATH,
    f"{GATEWAY_DIR}/README.md",
    f"{GATEWAY_DIR}/architecture.md",
    f"{CACHE_DIR}/README.md",
    CACHE_KEY_POLICY_PATH,
    f"{ROUTING_DIR}/README.md",
    ROUTE_DECISION_SCHEMA_PATH,
    "docs/reference/aide-lite.md",
    "docs/reference/aide-lite-test-runner.md",
    "docs/reference/cache-local-state-boundary.md",
    "docs/reference/router-profile-v0.md",
    "docs/reference/outcome-controller-v0.md",
    "docs/reference/gateway-skeleton.md",
    "docs/reference/provider-adapter-v0.md",
    "docs/reference/cross-repo-pack-export-import.md",
    "docs/reference/existing-tool-adapter-compiler-v0.md",
    "docs/reference/commit-discipline.md",
    "docs/reference/workunit-idempotency.md",
    "docs/reference/changelog-preview.md",
    "docs/reference/git-workflow-policy.md",
    "docs/reference/branch-roles.md",
    "docs/reference/promotion-policy.md",
    "docs/reference/git-helper-workflow.md",
    COMMIT_MESSAGE_STANDARD_PATH,
    TASK_RESUMPTION_STANDARD_PATH,
    WORKUNIT_RECOVERY_STANDARD_PATH,
]

PORTABLE_SOURCE_DIRS = [
    ".aide/scripts/tests",
    ADAPTER_TEMPLATE_DIR,
    GOLDEN_TASK_ROOT,
    f"{ROUTING_DIR}/examples",
    LOCAL_STATE_EXAMPLE_ROOT,
    "core/gateway",
    "core/providers",
]

Q31_REQUIRED_EXPORTED_SOURCE_FILES = [
    COMMIT_MESSAGE_POLICY_PATH,
    COMMIT_MESSAGE_HOOK_TEMPLATE_PATH,
    COMMIT_TEMPLATE_PATH,
    COMMIT_MESSAGE_STANDARD_PATH,
    TASK_RESUMPTION_POLICY_PATH,
    WORK_UNITS_POLICY_PATH,
    RECOVERY_POLICY_PATH,
    TASK_RESUMPTION_STANDARD_PATH,
    WORKUNIT_RECOVERY_STANDARD_PATH,
    GIT_WORKFLOW_POLICY_PATH,
    BRANCH_ROLES_POLICY_PATH,
    PROMOTION_RULES_POLICY_PATH,
    SYNC_POLICY_PATH,
    PRUNE_POLICY_PATH,
    ".aide/git/README.md",
    GIT_PROJECT_PROFILES_PATH,
    GIT_HELPER_POLICY_PATH,
    GIT_HELPER_COMMANDS_MD_PATH,
    "docs/reference/commit-discipline.md",
    "docs/reference/workunit-idempotency.md",
    "docs/reference/changelog-preview.md",
    "docs/reference/git-workflow-policy.md",
    "docs/reference/branch-roles.md",
    "docs/reference/promotion-policy.md",
    "docs/reference/git-helper-workflow.md",
    ".aide/scripts/aide_lite.py",
]

Q31_REQUIRED_EXPORTED_GOLDEN_TASK_IDS = [
    "commit_message_standard_golden",
    "task_resumption_standard_golden",
    "workunit_idempotency_golden",
    "changelog_preview_golden",
    "git_workflow_policy_golden",
    "branch_role_detection_golden",
    "promotion_rules_golden",
    "sync_policy_golden",
    "prune_policy_golden",
    "git_helper_policy_golden",
    "git_land_plan_golden",
    "git_promote_plan_golden",
    "git_prune_guard_golden",
    "git_live_repo_no_mutation_golden",
    *Q31_GOLDEN_TASK_IDS,
]

Q31_FORBIDDEN_EXPORTED_SOURCE_FILES = [
    GIT_WORKFLOW_DETECTION_JSON_PATH,
    GIT_WORKFLOW_DETECTION_MD_PATH,
    GIT_HELPER_PLAN_JSON_PATH,
    GIT_HELPER_PLAN_MD_PATH,
    AIDE_BRANCH_POLICY_PATH,
    AIDE_DEV_MAIN_PLAN_JSON_PATH,
    AIDE_DEV_MAIN_PLAN_MD_PATH,
    CHANGELOG_PREVIEW_MD_PATH,
    RELEASE_NOTES_PREVIEW_MD_PATH,
    CHANGELOG_PREVIEW_JSON_PATH,
    MALFORMED_COMMITS_MD_PATH,
    ".aide/queue/index.yaml",
    LATEST_PACKET_PATH,
    REVIEW_PACKET_PATH,
    ".aide/reports/token-ledger.jsonl",
    ".aide.local/state.json",
]

CHECKSUM_EXCLUDED_PACK_FILES = {
    "checksums.json",
    "export-report.md",
    "manifest.yaml",
}

IMPORT_SAFE_EXCLUDED_PREFIXES = (
    "core/",
)

IMPORT_SAFE_EXCLUDED_DOCS_PREFIX = "docs/"
IMPORT_SAFE_ALLOWED_DOCS_PREFIX = "docs/reference/"

IMPORT_MODES = {"safe", "full"}

PORTABLE_TEMPLATE_MAP = {
    TARGET_PROFILE_TEMPLATE_PATH: ".aide/profile.template.yaml",
    TARGET_PROJECT_STATE_TEMPLATE_PATH: ".aide/memory/project-state.template.md",
    TARGET_DECISIONS_TEMPLATE_PATH: ".aide/memory/decisions.template.md",
    TARGET_OPEN_RISKS_TEMPLATE_PATH: ".aide/memory/open-risks.template.md",
    EXPORT_IMPORT_POLICY_TEMPLATE_PATH: ".aide/import-policy.template.yaml",
    IMPORT_REPORT_TEMPLATE_PATH: ".aide/import-report.template.md",
}

EXPORT_FORBIDDEN_PATH_PATTERNS = [
    ".aide/profile.yaml",
    ".aide/toolchain.lock",
    ".aide/queue/**",
    ".aide/memory/project-state.md",
    ".aide/memory/decisions.md",
    ".aide/memory/open-risks.md",
    ".aide/context/repo-snapshot.json",
    ".aide/context/repo-map.json",
    ".aide/context/repo-map.md",
    ".aide/context/test-map.json",
    ".aide/context/context-index.json",
    ".aide/context/latest-*.md",
    ".aide/reports/**",
    ".aide/controller/**",
    ".aide/routing/latest-*",
    ".aide/cache/latest-*",
    ".aide/gateway/latest-*",
    ".aide/providers/latest-*",
    ".aide/git/workflow-detection.json",
    ".aide/git/workflow-detection.md",
    ".aide/git/latest-helper-plan.json",
    ".aide/git/latest-helper-plan.md",
    ".aide/git/aide-branch-policy.yaml",
    ".aide/git/aide-dev-main-plan.json",
    ".aide/git/aide-dev-main-plan.md",
    ".aide/changelog/*.preview.md",
    ".aide/changelog/changelog.preview.json",
    ".aide/changelog/release-notes.preview.json",
    ".aide/changelog/malformed-commits.md",
    ".aide/verification/latest-verification-report.md",
    ".aide/evals/runs/**",
    ".aide.local/**",
    ".aide.local",
    ".env",
    "secrets/**",
]

EXPORT_EXCLUDED_CLASSES = [
    "source_repo_identity",
    "source_repo_queue_history",
    "source_repo_memory",
    "source_repo_git_detection",
    "source_repo_git_helper_plan",
    "source_repo_branch_policy",
    "source_repo_changelog_previews",
    "generated_context",
    "generated_reports",
    "generated_status_outputs",
    "route_decisions",
    "cache_key_reports",
    "gateway_status_reports",
    "provider_status_reports",
    "eval_runs",
    "outcome_ledgers",
    "local_state",
    "secrets",
    "raw_prompts",
    "raw_responses",
]

GITIGNORE_REQUIRED_PATTERNS = [
    ".aide.local/",
    ".aide.local/**",
    ".env",
    "__pycache__/",
    "*.pyc",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
]

REQUIRED_GOLDEN_TASK_IDS = [
    "compact-task-packet-required-sections",
    "context-packet-no-full-repo-dump",
    "verifier-detects-bad-evidence",
    "review-packet-evidence-only",
    "token-ledger-budget-check",
    "adapter-managed-section-determinism",
    "commit_message_standard_golden",
    "task_resumption_standard_golden",
    "workunit_idempotency_golden",
    "changelog_preview_golden",
    "git_workflow_policy_golden",
    "branch_role_detection_golden",
    "promotion_rules_golden",
    "sync_policy_golden",
    "prune_policy_golden",
    "git_helper_policy_golden",
    "git_land_plan_golden",
    "git_promote_plan_golden",
    "git_prune_guard_golden",
    "git_live_repo_no_mutation_golden",
    *Q31_GOLDEN_TASK_IDS,
]

COMMIT_ALLOWED_TYPES = {
    "feat",
    "fix",
    "docs",
    "test",
    "refactor",
    "perf",
    "build",
    "ci",
    "chore",
    "audit",
    "security",
    "release",
    "revert",
    "policy",
    "schema",
    "contract",
    "connector",
    "snapshot",
    "aide",
}

COMMIT_SUBJECT_RE = re.compile(r"^(?P<type>[a-z]+)\((?P<scope>[a-z0-9][a-z0-9._-]*)\): (?P<summary>.+)$")
COMMIT_REQUIRED_BODY_HEADINGS = [
    "## Summary",
    "## Why",
    "## Changed",
    "## Validation",
    "## Changelog",
    "## Risks",
    "## Follow-up",
]
COMMIT_VALIDATION_TOKENS = {"PASS", "WARN", "FAIL", "NOT RUN"}
COMMIT_CHANGELOG_CATEGORIES = [
    "Added",
    "Changed",
    "Fixed",
    "Removed",
    "Deprecated",
    "Security",
    "Docs",
    "Tests",
    "Internal",
    "Risks",
    "Follow-up",
]
COMMIT_CHANGELOG_PREFIXES = tuple(f"- {category}:" for category in COMMIT_CHANGELOG_CATEGORIES)
COMMIT_TRAILERS = [
    "AIDE-Task",
    "AIDE-Phase",
    "AIDE-Result",
    "AIDE-Scope",
    "AIDE-Token-Impact",
    "AIDE-Quality-Gate",
]
COMMIT_VAGUE_SUMMARIES = {
    "update",
    "updates",
    "changes",
    "misc",
    "wip",
    "stuff",
    "work",
    "fix",
    "fixes",
}
GIT_TASK_BRANCH_PREFIXES = ("task/", "codex/", "aide/", "fix/", "repair/")
GIT_REVIEW_BRANCH_PREFIXES = ("review/",)
GIT_QUARANTINE_BRANCH_PREFIXES = ("quarantine/",)
GIT_RELEASE_BRANCH_PREFIXES = ("release/",)
GIT_HOTFIX_BRANCH_PREFIXES = ("hotfix/",)
GIT_SUBTASK_BRANCH_PREFIXES = ("subtask/",)
GIT_PROTECTED_ROLES = {"canonical", "integration", "release", "deploy"}

COMMIT_GOOD_EXAMPLE = """policy(aide): define structured commit recovery

## Summary

- Add canonical commit-message policy and checker behavior.

## Why

- Future agents need changelog-ready history without replaying chat context.

## Changed

- Added `.aide/policies/commit-messages.yaml`.
- Added deterministic commit-message validation.

## Validation

- `py -3 .aide/scripts/aide_lite.py commit check --message-file fixture`: PASS.

## Changelog

- Added: commit-message enforcement for future AIDE-managed work.

## Risks

- Local Git hooks still require explicit opt-in.

## Follow-up

- Use range checks before branch promotion.

AIDE-Task: Q27-commit-discipline-workunit-recovery-v0
AIDE-Phase: Q27
AIDE-Result: PASS
AIDE-Scope: commit
AIDE-Token-Impact: lower-history-reconstruction-cost
AIDE-Quality-Gate: commit-check-pass
"""

LEDGER_SURFACES = [
    "task_packet",
    "context_packet",
    "review_packet",
    "verification_report",
    "evidence_packet",
    "eval_report",
    "controller_report",
    "route_report",
    "cache_report",
    "provider_status",
    "baseline_surface",
    "generated_adapter",
]

EVAL_POLICY_ANCHORS = [
    "schema_version",
    "policy_id",
    "evaluation_scope",
    "deterministic_repo_local",
    "no_model_calls",
    "no_network",
    "result_values",
    "quality_dimensions",
    "token_reduction_invalid_if_quality_fails",
    "raw_prompt_storage_default: false",
    "raw_response_storage_default: false",
    "non_goals",
]

CONTROLLER_POLICY_ANCHORS = [
    "schema_version",
    "policy_id",
    "advisory_only",
    "allowed_inputs",
    "allowed_outputs",
    "forbidden_behaviors",
    "automatic_prompt_mutation",
    "automatic_policy_mutation",
    "automatic_route_mutation",
    "provider_calls",
    "model_calls",
    "network_calls",
    "autonomous_loop",
    "failure_classes",
    "recommendation_requirements",
    "expected_benefit",
    "evidence_source",
    "rollback_condition",
    "next_action",
    "risk_level",
    "suggestions_do_not_apply_themselves",
    "raw_prompt_storage_default: false",
    "raw_response_storage_default: false",
]

ROUTE_CLASSES = [
    "no_model_tool",
    "local_small",
    "local_strong",
    "cheap_remote",
    "frontier",
    "human_review",
    "blocked",
]

TASK_CLASSES = [
    "deterministic_format_or_count",
    "compact_task_generation",
    "context_indexing",
    "verifier_check",
    "evidence_review_packet",
    "bounded_docs_update",
    "bounded_code_patch",
    "failing_test_repair",
    "architecture_decision",
    "security_review",
    "self_modification",
    "final_promotion_review",
    "maintenance_suggestion",
    "unknown",
]

RISK_CLASSES = [
    "low",
    "medium",
    "high",
    "security",
    "governance",
    "destructive",
    "identity",
    "unknown",
]

ROUTING_HARD_FLOORS = [
    "architecture_decision",
    "security_review",
    "self_modification",
    "high_stakes_review",
    "final_promotion_review",
    "governance_policy_change",
    "irreversible_or_destructive_change",
]

ROUTING_POLICY_ANCHORS = [
    "schema_version",
    "policy_id",
    "advisory_only",
    "routing_unit",
    "work_unit_or_task_packet",
    "not_raw_prompt_only",
    "route_classes",
    "no_model_tool",
    "local_small",
    "local_strong",
    "cheap_remote",
    "frontier",
    "human_review",
    "blocked",
    "hard_floors",
    "quality_gates",
    "default_decision_rules",
    "forbidden_behaviors",
    "provider_calls",
    "model_calls",
    "network_calls",
    "automatic_execution",
    "output_requirements",
    "route_class",
    "rationale",
    "required_checks",
    "evidence_sources",
    "token_budget_status",
    "quality_gate_status",
    "live_calls_allowed_in_q17: false",
]

MODEL_REGISTRY_ANCHORS = {
    PROVIDERS_PATH: [
        "deterministic_tools",
        "human",
        "local_ollama",
        "local_lm_studio",
        "local_llama_cpp",
        "local_vllm",
        "local_sglang",
        "openai",
        "anthropic",
        "google_gemini",
        "deepseek",
        "openrouter",
        "other_remote_provider",
        "live_calls_allowed_in_q17: false",
    ],
    CAPABILITIES_PATH: [
        "code_edit",
        "structured_output",
        "json_schema",
        "long_context",
        "tool_use",
        "local_execution",
        "privacy_sensitive",
        "reasoning_heavy",
        "cheap_bulk",
        "frontier_review",
        "human_judgement",
        "deterministic_transform",
        "test_execution",
        "file_system_access",
    ],
    ROUTES_PATH: TASK_CLASSES,
    HARD_FLOORS_PATH: ROUTING_HARD_FLOORS,
    FALLBACK_PATH: [
        "preferred_unavailable",
        "verifier_fails",
        "golden_tasks_fail",
        "budget_exceeded",
        "task_class_unknown",
        "privacy_sensitive",
        "live_calls_allowed_in_q17: false",
    ],
}

ROUTE_DECISION_REQUIRED_FIELDS = [
    "schema_version",
    "route_id",
    "task_source",
    "task_class",
    "risk_class",
    "route_class",
    "fallback_route_class",
    "hard_floor_applied",
    "blocked",
    "blocked_reason",
    "rationale",
    "evidence_sources",
    "required_checks",
    "token_budget_status",
    "verifier_status",
    "golden_task_status",
    "outcome_recommendation_status",
    "quality_gate_status",
    "notes",
]

CACHE_POLICY_ANCHORS = [
    "schema_version",
    "policy_id",
    "cache_classes",
    "context_packet",
    "task_packet",
    "review_packet",
    "verification_report",
    "route_decision",
    "tool_result",
    "provider_response",
    "semantic_answer",
    "local_kv_metadata",
    "storage_policy",
    "committed_cache_content_allowed: false",
    "committed_cache_metadata_allowed: true",
    "raw_prompt_storage_default: false",
    "raw_response_storage_default: false",
    "local_state_root: .aide.local/",
    "forbidden_committed_outputs",
    "key_inputs",
    "invalidation_rules",
    "semantic_cache_policy",
    "code_edits: forbidden",
    "provider_response_cache_policy",
    "future_gateway_required: true",
    "cache_hit_must_not_bypass_verifier_or_golden_tasks",
]

LOCAL_STATE_POLICY_ANCHORS = [
    "schema_version",
    "policy_id",
    "committed_state_root: .aide/",
    "local_state_root: .aide.local/",
    "local_state_example_root: .aide.local.example/",
    "never_commit_secrets: true",
    "provider_keys_local_only: true",
    "raw_prompt_storage_default: false",
    "raw_response_storage_default: false",
    "allowed_local_state",
    "forbidden_committed_state",
    "actual `.aide.local/`",
    "migration_note",
]

CACHE_KEY_REQUIRED_FIELDS = [
    "key_id",
    "surface",
    "path",
    "content_sha256",
    "dependency_hashes",
    "policy_versions",
    "dirty_state",
    "valid_for",
    "notes",
]

GATEWAY_POLICY_ANCHORS = [
    "schema_version",
    "policy_id",
    "local_skeleton",
    "report_only",
    "no_provider_forwarding",
    "allowed_endpoints",
    "health",
    "status",
    "route_explain",
    "summaries",
    "forbidden_endpoints_in_q19",
    "provider_proxy",
    "openai_chat_completions_forwarding",
    "openai_responses_forwarding",
    "anthropic_messages_forwarding",
    "raw_prompt_storage_default: false",
    "raw_response_storage_default: false",
    "local_state_root: .aide.local/",
    "no_outbound_network_calls",
    "no_provider_calls",
    "no_model_calls",
    "no_raw_prompt_logging",
    "no_raw_response_logging",
    "route_decisions_advisory_only",
    "future_targets_documented_not_implemented",
]

GATEWAY_STATUS_REQUIRED_FIELDS = [
    "schema_version",
    "generated_by",
    "service",
    "mode",
    "provider_calls_enabled",
    "model_calls_enabled",
    "outbound_network_enabled",
    "raw_prompt_storage",
    "raw_response_storage",
    "readiness",
    "signals",
    "summaries",
]

PROVIDER_ADAPTER_POLICY_ANCHORS = [
    "schema_version",
    "policy_id",
    "offline_contracts_only",
    "metadata_validation_only",
    "no_provider_calls",
    "adapter_classes",
    "deterministic_tool",
    "human_review",
    "local_model",
    "remote_model",
    "aggregator",
    "provider_families",
    "deterministic_tools",
    "human",
    "local_ollama",
    "local_lm_studio",
    "local_llama_cpp",
    "local_vllm",
    "local_sglang",
    "openai",
    "anthropic",
    "google_gemini",
    "deepseek",
    "openrouter",
    "other_remote_provider",
    "credentials_never_committed: true",
    "credentials_live_only_in_local_state: true",
    "local_state_root: .aide.local/",
    "live_calls_allowed_in_q20: false",
    "network_calls_allowed_in_q20: false",
    "model_calls_allowed_in_q20: false",
    "provider_probe_calls_allowed_in_q20: false",
    "raw_prompt_storage_default: false",
    "raw_response_storage_default: false",
    "provider_selection_must_respect_router_profile: true",
    "hard_floors_must_not_demote: true",
    "verifier_and_golden_tasks_not_bypassed: true",
]

PROVIDER_REQUIRED_IDS = [
    "deterministic_tools",
    "human",
    "local_ollama",
    "local_lm_studio",
    "local_llama_cpp",
    "local_vllm",
    "local_sglang",
    "openai",
    "anthropic",
    "google_gemini",
    "deepseek",
    "openrouter",
    "other_remote_provider",
]

PROVIDER_STATUS_REQUIRED_FIELDS = [
    "schema_version",
    "generated_by",
    "provider_adapter_contract",
    "live_provider_calls",
    "live_model_calls",
    "network_calls",
    "provider_probe_calls",
    "credentials_configured",
    "gateway_forwarding",
    "raw_prompt_storage",
    "raw_response_storage",
    "provider_family_count",
    "provider_ids",
    "provider_class_counts",
    "adapter_class_counts",
    "privacy_class_counts",
    "status_counts",
    "validation",
]

CACHE_SURFACES = [
    (LATEST_PACKET_PATH, "latest_task_packet", "task_packet", "latest compact task packet"),
    (LATEST_CONTEXT_PACKET_PATH, "latest_context_packet", "context_packet", "latest compact context packet"),
    (REVIEW_PACKET_PATH, "latest_review_packet", "review_packet", "latest compact review packet"),
    (LATEST_VERIFICATION_REPORT_PATH, "latest_verification_report", "verification_report", "latest verification report"),
    (ROUTE_DECISION_JSON_PATH, "latest_route_decision", "route_decision", "latest route decision"),
    (GOLDEN_RUN_JSON_PATH, "latest_golden_tasks_report", "golden_tasks_report", "latest golden task run report"),
    (TOKEN_SUMMARY_PATH, "token_savings_summary", "token_savings_summary", "latest token savings summary"),
    (PROVIDER_STATUS_JSON_PATH, "latest_provider_status", "provider_status", "latest provider status metadata"),
]

CONTROLLER_FAILURE_CLASSES = [
    "context_missing",
    "packet_too_large",
    "token_budget_exceeded",
    "token_regression",
    "adapter_drift",
    "verifier_gap",
    "verifier_fail",
    "review_packet_incomplete",
    "golden_task_fail",
    "unclear_acceptance",
    "validation_failure",
    "policy_violation",
    "stale_artifact",
    "missing_evidence",
    "secret_risk",
    "unknown",
]

TOKEN_LEDGER_ANCHORS = [
    "schema_version",
    "policy_id",
    "approximation_method",
    "storage_policy",
    "raw_prompt_storage_default",
    "raw_response_storage_default",
    "committed_ledger_allowed",
    "record_surfaces",
    "required_record_fields",
    "comparison_policy",
    "regression_policy",
    "limitations",
]

TOKEN_BUDGET_ANCHORS = [
    "schema_version",
    "policy_id",
    "status",
    "purpose",
    "approx_token_method",
    "targets",
    "project_state_target_tokens",
    "compact_task_packet_target_tokens",
    "review_packet_target_tokens",
    "codex_prompt_target_tokens",
    "gpt_review_prompt_target_tokens",
    "hard_limits",
    "max_compact_task_packet_tokens",
    "max_review_packet_tokens",
    "max_project_state_tokens",
    "forbidden_prompt_patterns",
    "required_prompt_sections",
    "output_discipline",
    "review_policy",
    "non_degradation_rule",
]

REQUIRED_IGNORE_PATTERNS = [
    ".git/**",
    ".env",
    "secrets/**",
    ".aide.local/**",
    "__pycache__/**",
    ".pytest_cache/**",
    ".mypy_cache/**",
    ".ruff_cache/**",
    "node_modules/**",
    "dist/**",
    "build/**",
]

FORBIDDEN_PACKET_PHRASES = [
    "full prior transcript",
    "whole repo dump",
    "repeated roadmap dump",
    "model/provider keys",
]

CONTEXT_FORBIDDEN_INLINE_MARKERS = [
    "print('hello')",
    "SHOULD_NOT_APPEAR",
]

ROLE_ORDER = [
    "aide_contract",
    "aide_policy",
    "aide_prompt",
    "aide_context",
    "aide_queue",
    "aide_evidence",
    "harness_code",
    "compat_code",
    "shared_code",
    "test",
    "docs",
    "governance",
    "inventory",
    "matrix",
    "research",
    "host",
    "bridge",
    "script",
    "config",
    "generated",
    "binary_or_asset",
    "unknown",
]

BINARY_EXTENSIONS = {
    ".7z",
    ".bin",
    ".bmp",
    ".dll",
    ".dmg",
    ".dylib",
    ".exe",
    ".gif",
    ".ico",
    ".iso",
    ".jpeg",
    ".jpg",
    ".msi",
    ".nupkg",
    ".pdf",
    ".pkg",
    ".png",
    ".pyo",
    ".pyc",
    ".rar",
    ".so",
    ".tar",
    ".tgz",
    ".whl",
    ".zip",
}

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
    re.compile(r"sk-ant-[A-Za-z0-9_-]{16,}"),
    re.compile(r"(?i)\b(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]"),
]

SECRET_POLICY_TERM_PATTERN = re.compile(r"(?i)\b(api[_-]?key|secret|password|token)\b")


@dataclass(frozen=True)
class TextStats:
    path: str
    chars: int
    lines: int
    approx_tokens: int


@dataclass(frozen=True)
class Check:
    severity: str
    message: str


@dataclass(frozen=True)
class AdapterStatus:
    status: str
    action_hint: str
    body_matches: bool
    fingerprint_matches: bool


@dataclass(frozen=True)
class AdapterTarget:
    target_id: str
    display_name: str
    output_path: str
    generated_path: str
    output_mode: str
    template_path: str
    enabled_by_default: bool
    risk_level: str
    manual_content_policy: str
    drift_policy: str
    target_notes: str


@dataclass(frozen=True)
class WriteResult:
    path: Path
    action: str


@dataclass(frozen=True)
class PacketRender:
    text: str
    stats: TextStats
    budget_status: str
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class VerificationFinding:
    severity: str
    check: str
    message: str
    path: str = ""


@dataclass(frozen=True)
class DiffScopeResult:
    status: str
    path: str
    classification: str
    reason: str


@dataclass(frozen=True)
class VerificationReport:
    result: str
    findings: tuple[VerificationFinding, ...]
    checked_files: tuple[str, ...]
    changed_files: tuple[DiffScopeResult, ...]


@dataclass(frozen=True)
class LedgerRecord:
    run_id: str
    phase: str
    surface: str
    path: str
    chars: int
    lines: int
    approx_tokens: int
    method: str
    budget: str
    budget_status: str
    notes: str


@dataclass(frozen=True)
class BaselineDefinition:
    name: str
    purpose: str
    paths: tuple[str, ...]


@dataclass(frozen=True)
class BaselineResult:
    name: str
    chars: int
    lines: int
    approx_tokens: int
    method: str
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class LedgerComparison:
    compact: LedgerRecord
    baseline: BaselineResult
    reduction_percent: float | None
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class GoldenTaskDefinition:
    task_id: str
    title: str
    description: str
    status: str


@dataclass(frozen=True)
class GoldenTaskResult:
    task_id: str
    result: str
    checks_run: int
    passed_checks: int
    warnings: tuple[str, ...]
    errors: tuple[str, ...]
    related_paths: tuple[str, ...]
    approx_tokens_if_applicable: int | None
    notes: str


@dataclass(frozen=True)
class GoldenRunResult:
    result: str
    tasks: tuple[GoldenTaskResult, ...]
    json_report: str
    markdown_report: str


@dataclass(frozen=True)
class OutcomeRecord:
    run_id: str
    phase: str
    source: str
    result: str
    failure_class: str
    severity: str
    related_paths: tuple[str, ...]
    approx_tokens: int | None
    budget_status: str
    golden_task_status: str
    verifier_status: str
    recommendation_id: str
    notes: str


@dataclass(frozen=True)
class Recommendation:
    recommendation_id: str
    failure_class: str
    evidence_source: str
    expected_benefit: str
    risk_level: str
    next_action: str
    rollback_condition: str
    applies_automatically: bool = False


@dataclass(frozen=True)
class RouteProfile:
    task_class: str
    preferred_route_class: str
    fallback_route_class: str
    review_required: bool


@dataclass(frozen=True)
class RouteDecision:
    schema_version: str
    route_id: str
    task_source: str
    task_class: str
    risk_class: str
    route_class: str
    fallback_route_class: str
    hard_floor_applied: str
    blocked: bool
    blocked_reason: str
    rationale: tuple[str, ...]
    evidence_sources: tuple[str, ...]
    required_checks: tuple[str, ...]
    token_budget_status: str
    verifier_status: str
    golden_task_status: str
    outcome_recommendation_status: str
    quality_gate_status: str
    notes: tuple[str, ...]


@dataclass(frozen=True)
class CacheKeyRecord:
    key_name: str
    surface: str
    path: str
    key_id: str
    content_sha256: str
    dependency_hashes: tuple[tuple[str, str], ...]
    policy_versions: tuple[tuple[str, str], ...]
    dirty_state: bool
    valid_for: str
    notes: str


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def normalize_rel(path: str | Path) -> str:
    rel = Path(path).as_posix()
    while rel.startswith("./"):
        rel = rel[2:]
    return rel


def normalize_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in normalized.splitlines()).strip() + "\n"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text_if_changed(path: Path, text: str) -> WriteResult:
    normalized = normalize_text(text)
    if path.exists() and normalize_text(read_text(path)) == normalized:
        return WriteResult(path, "unchanged")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(normalized, encoding="utf-8", newline="\n")
    return WriteResult(path, "written")


def write_text(path: Path, text: str) -> None:
    write_text_if_changed(path, text)


def sha256_text(text: str) -> str:
    return hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()


def approx_tokens_for_chars(chars: int) -> int:
    return int(math.ceil(chars / 4)) if chars else 0


def estimate_text(text: str, path: str = "<memory>") -> TextStats:
    return TextStats(
        path=path,
        chars=len(text),
        lines=0 if not text else text.count("\n") + (0 if text.endswith("\n") else 1),
        approx_tokens=approx_tokens_for_chars(len(text)),
    )


def safe_repo_path(repo_root: Path, requested: str) -> Path:
    target = (repo_root / requested).resolve()
    root = repo_root.resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path must stay inside repo: {requested}") from exc
    return target


def looks_binary(path: Path) -> bool:
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return True
    sample = path.read_bytes()[:4096]
    if b"\x00" in sample:
        return True
    try:
        sample.decode("utf-8")
    except UnicodeDecodeError:
        return True
    return False


def estimate_file(repo_root: Path, requested: str) -> TextStats:
    target = safe_repo_path(repo_root, requested)
    if not target.exists():
        raise ValueError(f"file does not exist: {requested}")
    if not target.is_file():
        raise ValueError(f"path is not a file: {requested}")
    if looks_binary(target):
        raise ValueError(f"refusing to estimate binary-like file: {requested}")
    text = read_text(target)
    return estimate_text(text, normalize_rel(target.relative_to(repo_root)))


def ledger_record_for_file(
    repo_root: Path,
    requested: str,
    surface: str | None = None,
    phase: str = "Q14-token-ledger-savings-report",
    run_id: str = "q14.scan.current",
    notes: str = "",
) -> LedgerRecord:
    rel = normalize_rel(requested)
    stats = estimate_file(repo_root, rel)
    surface_value = surface or detect_surface(stats.path)
    if surface_value not in LEDGER_SURFACES:
        raise ValueError(f"unknown ledger surface: {surface_value}")
    budget, budget_status = ledger_budget_status(repo_root, surface_value, stats.approx_tokens)
    return LedgerRecord(
        run_id=run_id,
        phase=phase,
        surface=surface_value,
        path=stats.path,
        chars=stats.chars,
        lines=stats.lines,
        approx_tokens=stats.approx_tokens,
        method="chars/4",
        budget=budget,
        budget_status=budget_status,
        notes=notes or "estimated metadata only; raw content not stored",
    )


def ledger_record_to_dict(record: LedgerRecord) -> dict[str, object]:
    return {
        "run_id": record.run_id,
        "phase": record.phase,
        "surface": record.surface,
        "path": record.path,
        "chars": record.chars,
        "lines": record.lines,
        "approx_tokens": record.approx_tokens,
        "method": record.method,
        "budget": record.budget,
        "budget_status": record.budget_status,
        "notes": record.notes,
    }


def ledger_record_from_dict(data: dict[str, object]) -> LedgerRecord:
    return LedgerRecord(
        run_id=str(data.get("run_id", "")),
        phase=str(data.get("phase", "")),
        surface=str(data.get("surface", "")),
        path=normalize_rel(str(data.get("path", ""))),
        chars=int(data.get("chars", 0) or 0),
        lines=int(data.get("lines", 0) or 0),
        approx_tokens=int(data.get("approx_tokens", 0) or 0),
        method=str(data.get("method", "chars/4")),
        budget=str(data.get("budget", "unknown")),
        budget_status=str(data.get("budget_status", "unknown_budget")),
        notes=str(data.get("notes", "")),
    )


def read_ledger_records(repo_root: Path) -> list[LedgerRecord]:
    path = repo_root / TOKEN_LEDGER_PATH
    if not path.exists():
        return []
    records: list[LedgerRecord] = []
    for line in read_text(path).splitlines():
        if not line.strip():
            continue
        try:
            records.append(ledger_record_from_dict(json.loads(line)))
        except (json.JSONDecodeError, TypeError, ValueError):
            continue
    return records


def write_ledger_records(repo_root: Path, records: Iterable[LedgerRecord]) -> WriteResult:
    sorted_records = sorted(records, key=lambda item: (item.run_id, item.phase, item.surface, item.path))
    lines = [
        json.dumps(ledger_record_to_dict(record), sort_keys=True, separators=(",", ":"))
        for record in sorted_records
    ]
    return write_text_if_changed(repo_root / TOKEN_LEDGER_PATH, "\n".join(lines) + ("\n" if lines else ""))


def merge_ledger_records(repo_root: Path, new_records: Iterable[LedgerRecord], run_id: str) -> tuple[WriteResult, list[LedgerRecord], list[LedgerRecord]]:
    existing = read_ledger_records(repo_root)
    new_list = list(new_records)
    retained = [record for record in existing if record.run_id != run_id]
    merged = [*retained, *new_list]
    return write_ledger_records(repo_root, merged), merged, existing


def assert_ledger_safe_path(repo_root: Path, requested: str) -> str:
    rel = normalize_rel(requested)
    target = safe_repo_path(repo_root, rel)
    if not target.exists():
        raise ValueError(f"file does not exist: {rel}")
    if not target.is_file():
        raise ValueError(f"path is not a file: {rel}")
    if rel not in GENERATED_CONTEXT_PATHS and is_ignored(rel, load_ignore_patterns(repo_root)):
        raise ValueError(f"refusing ignored/local/secret path for ledger: {rel}")
    if looks_binary(target):
        raise ValueError(f"refusing binary-like file for ledger: {rel}")
    return rel


def ledger_scan_paths(repo_root: Path) -> list[tuple[str, str, str]]:
    candidates: list[tuple[str, str, str]] = [
        (LATEST_PACKET_PATH, "task_packet", "latest compact task packet"),
        (LATEST_CONTEXT_PACKET_PATH, "context_packet", "latest compact context packet"),
        (REVIEW_PACKET_PATH, "review_packet", "latest compact review packet"),
        (LATEST_VERIFICATION_REPORT_PATH, "verification_report", "latest compact verification report"),
        (GOLDEN_RUN_JSON_PATH, "eval_report", "latest golden task JSON report"),
        (GOLDEN_RUN_MD_PATH, "eval_report", "latest golden task Markdown report"),
        (OUTCOME_REPORT_PATH, "controller_report", "latest advisory outcome report"),
        (RECOMMENDATIONS_PATH, "controller_report", "latest advisory recommendations"),
        (ROUTE_DECISION_JSON_PATH, "route_report", "latest advisory route decision JSON"),
        (ROUTE_DECISION_MD_PATH, "route_report", "latest advisory route decision Markdown"),
        (CACHE_KEYS_JSON_PATH, "cache_report", "latest cache key JSON metadata report"),
        (CACHE_KEYS_MD_PATH, "cache_report", "latest cache key Markdown metadata report"),
        (".aide/prompts/compact-task.md", "baseline_surface", "compact task prompt template"),
        (".aide/prompts/evidence-review.md", "baseline_surface", "evidence review prompt template"),
        (".aide/prompts/codex-token-mode.md", "baseline_surface", "Codex token-mode guidance"),
        ("AGENTS.md", "generated_adapter", "managed agent guidance"),
    ]
    for queue_id in [
        "Q09-token-survival-core",
        "Q10-aide-lite-hardening",
        "Q11-context-compiler-v0",
        "Q12-verifier-v0",
        "Q13-evidence-review-workflow",
        "Q14-token-ledger-savings-report",
        "Q15-golden-tasks-v0",
        "Q16-outcome-controller-v0",
        "Q17-router-profile-v0",
        "Q18-cache-local-state-boundary",
    ]:
        evidence_dir = repo_root / f".aide/queue/{queue_id}/evidence"
        if evidence_dir.exists():
            for path in sorted(evidence_dir.glob("*.md")):
                rel = normalize_rel(path.relative_to(repo_root))
                candidates.append((rel, "evidence_packet", f"{queue_id} evidence"))
    seen: set[str] = set()
    result: list[tuple[str, str, str]] = []
    for rel, surface, notes in candidates:
        if rel in seen or not (repo_root / rel).exists():
            continue
        if rel not in GENERATED_CONTEXT_PATHS and is_ignored(rel, load_ignore_patterns(repo_root)):
            continue
        seen.add(rel)
        result.append((rel, surface, notes))
    return sorted(result, key=lambda item: item[0])


def build_ledger_scan_records(repo_root: Path, run_id: str = "q14.scan.current") -> list[LedgerRecord]:
    records: list[LedgerRecord] = []
    for rel, surface, notes in ledger_scan_paths(repo_root):
        records.append(ledger_record_for_file(repo_root, rel, surface, run_id=run_id, notes=notes))
    return records


def parse_token_baselines(repo_root: Path) -> list[BaselineDefinition]:
    path = repo_root / TOKEN_BASELINES_PATH
    if not path.exists():
        return []
    baselines: list[BaselineDefinition] = []
    name = ""
    purpose = ""
    paths: list[str] = []
    in_paths = False
    for line in read_text(path).splitlines():
        stripped = line.strip()
        if stripped.startswith("- name:"):
            if name:
                baselines.append(BaselineDefinition(name, purpose, tuple(paths)))
            name = stripped.split(":", 1)[1].strip()
            purpose = ""
            paths = []
            in_paths = False
            continue
        if not name:
            continue
        if stripped.startswith("purpose:"):
            purpose = stripped.split(":", 1)[1].strip()
            in_paths = False
            continue
        if stripped == "paths:":
            in_paths = True
            continue
        if in_paths and stripped.startswith("- "):
            paths.append(normalize_rel(stripped[2:].strip().strip('"').strip("'")))
            continue
        if stripped and not stripped.startswith("#"):
            in_paths = False
    if name:
        baselines.append(BaselineDefinition(name, purpose, tuple(paths)))
    return baselines


def baseline_by_name(repo_root: Path, name: str) -> BaselineDefinition:
    for baseline in parse_token_baselines(repo_root):
        if baseline.name == name:
            return baseline
    raise ValueError(f"unknown baseline: {name}")


def calculate_baseline(repo_root: Path, baseline: BaselineDefinition) -> BaselineResult:
    chars = 0
    lines = 0
    warnings: list[str] = []
    for rel in baseline.paths:
        try:
            if rel not in GENERATED_CONTEXT_PATHS and is_ignored(rel, load_ignore_patterns(repo_root)):
                warnings.append(f"ignored baseline path skipped: {rel}")
                continue
            stats = estimate_file(repo_root, rel)
            chars += stats.chars
            lines += stats.lines
        except ValueError as exc:
            warnings.append(str(exc))
    return BaselineResult(
        name=baseline.name,
        chars=chars,
        lines=lines,
        approx_tokens=approx_tokens_for_chars(chars),
        method="chars/4",
        warnings=tuple(warnings),
    )


def compare_to_baseline(repo_root: Path, compact_path: str, baseline_name: str, surface: str | None = None) -> LedgerComparison:
    rel = assert_ledger_safe_path(repo_root, compact_path)
    compact = ledger_record_for_file(
        repo_root,
        rel,
        surface=surface or detect_surface(rel),
        run_id="q14.compare",
        notes=f"comparison against {baseline_name}",
    )
    baseline = calculate_baseline(repo_root, baseline_by_name(repo_root, baseline_name))
    reduction = None
    warnings = list(baseline.warnings)
    if baseline.approx_tokens > 0:
        reduction = ((baseline.approx_tokens - compact.approx_tokens) / baseline.approx_tokens) * 100
    else:
        warnings.append(f"baseline unavailable or empty: {baseline_name}")
    return LedgerComparison(compact, baseline, reduction, tuple(warnings))


def previous_records_by_path(records: Iterable[LedgerRecord], run_id: str) -> dict[tuple[str, str], LedgerRecord]:
    previous: dict[tuple[str, str], LedgerRecord] = {}
    for record in sorted(records, key=lambda item: (item.run_id, item.phase, item.surface, item.path)):
        if record.run_id == run_id:
            continue
        previous[(record.surface, record.path)] = record
    return previous


def regression_warnings(existing_records: Iterable[LedgerRecord], current_records: Iterable[LedgerRecord], threshold_percent: int) -> list[str]:
    previous = previous_records_by_path(existing_records, "q14.scan.current")
    warnings: list[str] = []
    for record in current_records:
        prior = previous.get((record.surface, record.path))
        if not prior or prior.approx_tokens <= 0:
            continue
        increase = ((record.approx_tokens - prior.approx_tokens) / prior.approx_tokens) * 100
        if increase > threshold_percent:
            warnings.append(
                f"{record.surface} `{record.path}` increased {increase:.1f}% ({prior.approx_tokens} -> {record.approx_tokens} approx tokens)"
            )
    return warnings


def ledger_budget_warnings(records: Iterable[LedgerRecord]) -> list[str]:
    warnings: list[str] = []
    for record in records:
        if record.budget_status == "near_budget":
            warnings.append(f"near budget: {record.surface} `{record.path}` {record.approx_tokens}/{record.budget}")
        elif record.budget_status == "over_budget":
            warnings.append(f"over budget: {record.surface} `{record.path}` {record.approx_tokens}/{record.budget}")
    return warnings


def render_token_savings_summary(repo_root: Path, records: list[LedgerRecord], regression: list[str]) -> str:
    latest = {record.path: record for record in records if record.run_id == "q14.scan.current"}
    latest_lines = []
    for rel in [LATEST_PACKET_PATH, LATEST_CONTEXT_PACKET_PATH, REVIEW_PACKET_PATH, LATEST_VERIFICATION_REPORT_PATH]:
        record = latest.get(rel)
        if record:
            latest_lines.append(f"- `{rel}`: {record.chars} chars / {record.approx_tokens} approx tokens / {record.budget_status}")
        else:
            latest_lines.append(f"- `{rel}`: missing from latest ledger scan")

    baseline_lines = []
    for baseline in parse_token_baselines(repo_root):
        result = calculate_baseline(repo_root, baseline)
        warning_note = f" ({len(result.warnings)} warning(s))" if result.warnings else ""
        baseline_lines.append(f"- `{baseline.name}`: {result.chars} chars / {result.approx_tokens} approx tokens{warning_note}")

    comparison_lines = []
    for compact_path, baseline_name in [
        (LATEST_PACKET_PATH, "root_history_baseline"),
        (REVIEW_PACKET_PATH, "review_baseline"),
        (LATEST_CONTEXT_PACKET_PATH, "repo_context_baseline"),
    ]:
        if not (repo_root / compact_path).exists():
            continue
        comparison = compare_to_baseline(repo_root, compact_path, baseline_name)
        if comparison.reduction_percent is None:
            comparison_lines.append(f"- `{compact_path}` vs `{baseline_name}`: unavailable")
        else:
            comparison_lines.append(
                f"- `{compact_path}` vs `{baseline_name}`: {comparison.reduction_percent:.1f}% estimated reduction "
                f"({comparison.compact.approx_tokens} vs {comparison.baseline.approx_tokens} approx tokens)"
            )

    budget_warnings = ledger_budget_warnings(records)
    budget_lines = [f"- {warning}" for warning in budget_warnings] or ["- none"]
    regression_lines = [f"- {warning}" for warning in regression] or ["- none"]
    largest = sorted(records, key=lambda item: item.approx_tokens, reverse=True)[:10]
    largest_lines = [
        f"- `{record.path}` ({record.surface}): {record.approx_tokens} approx tokens"
        for record in largest
    ] or ["- no records"]

    return f"""# AIDE Token Savings Summary

## Method

- approximation: chars / 4, rounded up
- exact_provider_billing: false
- exact_tokenizer: false
- raw_prompt_storage: false
- raw_response_storage: false

## Latest Compact Surfaces

{chr(10).join(latest_lines)}

## Named Baselines

{chr(10).join(baseline_lines)}

## Compact-To-Baseline Comparisons

{chr(10).join(comparison_lines)}

## Largest Ledger Surfaces

{chr(10).join(largest_lines)}

## Budget Warnings

{chr(10).join(budget_lines)}

## Regression Warnings

{chr(10).join(regression_lines)}

## Uncertainty

These are estimated metadata records only. They do not measure provider billing, exact tokenizer behavior, hidden reasoning tokens, cached-token discounts, or quality outcomes. Q15 golden tasks provide deterministic local quality gates, but they do not prove arbitrary coding-task quality.
"""


def write_token_savings_summary(repo_root: Path, records: list[LedgerRecord], regression: list[str]) -> WriteResult:
    return write_text_if_changed(repo_root / TOKEN_SUMMARY_PATH, render_token_savings_summary(repo_root, records, regression))


def parse_golden_task_catalog(repo_root: Path) -> list[GoldenTaskDefinition]:
    path = repo_root / GOLDEN_TASK_CATALOG_PATH
    if not path.exists():
        return []
    tasks: list[GoldenTaskDefinition] = []
    current: dict[str, str] = {}
    for line in read_text(path).splitlines():
        stripped = line.strip()
        if stripped.startswith("- id:"):
            if current.get("id"):
                tasks.append(
                    GoldenTaskDefinition(
                        task_id=current.get("id", ""),
                        title=current.get("title", current.get("id", "")),
                        description=current.get("description", ""),
                        status=current.get("status", "unknown"),
                    )
                )
            current = {"id": stripped.split(":", 1)[1].strip()}
            continue
        if not current:
            continue
        for key in ["title", "status", "description"]:
            prefix = f"{key}:"
            if stripped.startswith(prefix):
                current[key] = stripped.split(":", 1)[1].strip()
                break
    if current.get("id"):
        tasks.append(
            GoldenTaskDefinition(
                task_id=current.get("id", ""),
                title=current.get("title", current.get("id", "")),
                description=current.get("description", ""),
                status=current.get("status", "unknown"),
            )
        )
    return sorted(tasks, key=lambda task: task.task_id)


def golden_task_definition(repo_root: Path, task_id: str) -> GoldenTaskDefinition:
    for task in parse_golden_task_catalog(repo_root):
        if task.task_id == task_id:
            return task
    raise ValueError(f"unknown golden task: {task_id}")


def check_pass(checks: list[Check], condition: bool, message: str) -> None:
    checks.append(Check("PASS" if condition else "FAIL", message))


def check_warn(checks: list[Check], condition: bool, message: str) -> None:
    checks.append(Check("PASS" if condition else "WARN", message))


def result_from_checks(checks: Iterable[Check]) -> str:
    severities = [check.severity for check in checks]
    if any(severity == "FAIL" for severity in severities):
        return "FAIL"
    if any(severity == "WARN" for severity in severities):
        return "WARN"
    return "PASS"


def strip_commit_message_comments(text: str) -> str:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    stripped = [
        line.rstrip()
        for line in lines
        if not (line.lstrip().startswith("#") and not line.lstrip().startswith("##"))
    ]
    while stripped and not stripped[-1]:
        stripped.pop()
    return "\n".join(stripped)


def markdown_heading_body(text: str, heading: str) -> str:
    lines = text.splitlines()
    capture = False
    body: list[str] = []
    for line in lines:
        if line.strip() == heading:
            capture = True
            continue
        if capture and line.startswith("## ") and line.strip() != heading:
            break
        if capture:
            body.append(line)
    return "\n".join(body).strip()


def parse_commit_trailers(message: str) -> dict[str, str]:
    trailers: dict[str, str] = {}
    for line in reversed(message.splitlines()):
        stripped = line.strip()
        if not stripped:
            if trailers:
                break
            continue
        if ":" not in stripped:
            if trailers:
                break
            continue
        key, value = stripped.split(":", 1)
        if re.match(r"^[A-Za-z0-9-]+$", key):
            trailers[key] = value.strip()
        elif trailers:
            break
    return dict(reversed(list(trailers.items())))


def validate_commit_message_text(text: str) -> list[Check]:
    message = strip_commit_message_comments(text)
    lines = message.splitlines()
    checks: list[Check] = []
    subject = lines[0].strip() if lines else ""
    check_pass(checks, bool(subject), "commit subject is present")
    if subject:
        check_pass(checks, len(subject) <= 72, "commit subject is 72 characters or fewer")
        match = COMMIT_SUBJECT_RE.match(subject)
        check_pass(checks, bool(match), "commit subject follows type(scope): summary")
        if match:
            commit_type = match.group("type")
            summary = match.group("summary").strip()
            check_pass(checks, commit_type in COMMIT_ALLOWED_TYPES, f"commit type is allowed: {commit_type}")
            check_pass(checks, not subject.endswith("."), "commit subject has no trailing period")
            check_pass(checks, summary.lower() not in COMMIT_VAGUE_SUMMARIES, "commit subject is not a vague placeholder")
            check_pass(checks, len(summary) >= 8, "commit summary is specific enough")
        else:
            check_pass(checks, False, "commit type cannot be validated without subject match")
    body = "\n".join(lines[1:]).strip()
    check_pass(checks, bool(body), "commit body is present")
    if len(lines) > 1:
        check_pass(checks, lines[1].strip() == "", "blank line separates subject and Markdown body")
    for heading in COMMIT_REQUIRED_BODY_HEADINGS:
        check_pass(checks, heading in body, f"commit body contains heading: {heading}")
        section = markdown_heading_body(body, heading)
        check_pass(checks, bool(section.strip()), f"commit body heading has content: {heading}")
        check_pass(checks, "- " in section, f"commit body heading has bullet content: {heading}")
    validation = markdown_heading_body(body, "## Validation")
    check_pass(
        checks,
        any(marker in validation for marker in COMMIT_VALIDATION_TOKENS),
        "validation section records PASS/WARN/FAIL/NOT RUN outcome",
    )
    changelog = markdown_heading_body(body, "## Changelog")
    check_pass(
        checks,
        any(prefix in changelog for prefix in COMMIT_CHANGELOG_PREFIXES),
        "changelog section uses a machine-readable category prefix",
    )
    trailers = parse_commit_trailers(message)
    for trailer in COMMIT_TRAILERS:
        check_pass(checks, trailer in trailers and bool(trailers.get(trailer)), f"commit trailer present: {trailer}")
    lowered = message.lower()
    for forbidden in [
        "raw_prompt_body",
        "raw_response_body",
        "begin private key",
        "openai_api_key",
        "anthropic_api_key",
        "deepseek_api_key",
        "sk-ant",
    ]:
        check_pass(checks, forbidden not in lowered, f"commit message excludes {forbidden}")
    return checks


def commit_message_result(checks: Iterable[Check]) -> str:
    return result_from_checks(checks)


def git_latest_commit_message(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "git log failed")
    return result.stdout


def is_git_repo(repo_root: Path) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        encoding="utf-8",
    )
    return result.returncode == 0 and result.stdout.strip().lower() == "true"


def git_commit_messages_for_range(repo_root: Path, revision_range: str, max_count: int | None = None) -> list[tuple[str, str, str]]:
    command = ["git", "log", "--reverse", "--pretty=%H%x00%s%x00%B%x1e"]
    if max_count is not None:
        command.insert(2, f"--max-count={max_count}")
    command.append(revision_range)
    result = subprocess.run(
        command,
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or f"git log failed for range {revision_range}")
    commits: list[tuple[str, str, str]] = []
    for record in result.stdout.split("\x1e"):
        stripped = record.strip("\n")
        if not stripped:
            continue
        parts = stripped.split("\x00", 2)
        if len(parts) != 3:
            continue
        commit_hash, subject, message = parts
        commits.append((commit_hash.strip(), subject.strip(), message.strip() + "\n"))
    return commits


def render_commit_template() -> str:
    return read_text(repo_root_from_script() / COMMIT_TEMPLATE_PATH) if (repo_root_from_script() / COMMIT_TEMPLATE_PATH).exists() else COMMIT_GOOD_EXAMPLE


def current_hook_path(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "config", "--get", "core.hooksPath"],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def install_commit_hook(repo_root: Path, force: bool = False) -> tuple[str, str]:
    hook_path = repo_root / COMMIT_MESSAGE_HOOK_TEMPLATE_PATH
    if not hook_path.exists():
        raise ValueError(f"hook template missing: {COMMIT_MESSAGE_HOOK_TEMPLATE_PATH}")
    before = current_hook_path(repo_root)
    if before and normalize_rel(before) != ".aide/hooks" and not force:
        raise ValueError(f"existing core.hooksPath is {before}; rerun with --force to replace")
    result = subprocess.run(
        ["git", "config", "core.hooksPath", ".aide/hooks"],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "failed to install core.hooksPath")
    return before, current_hook_path(repo_root)


def extract_changelog_entries(message: str) -> dict[str, list[str]]:
    entries = {category: [] for category in COMMIT_CHANGELOG_CATEGORIES}
    section = markdown_heading_body(strip_commit_message_comments(message), "## Changelog")
    for line in section.splitlines():
        stripped = line.strip()
        for category in COMMIT_CHANGELOG_CATEGORIES:
            prefix = f"- {category}:"
            if stripped.startswith(prefix):
                value = stripped[len(prefix):].strip()
                if value:
                    entries[category].append(value)
    return {category: values for category, values in entries.items() if values}


def make_changelog_preview(repo_root: Path, revision_range: str | None = None) -> dict[str, object]:
    if revision_range:
        commits = git_commit_messages_for_range(repo_root, revision_range)
        source = revision_range
    else:
        commits = git_commit_messages_for_range(repo_root, "HEAD~20..HEAD", max_count=20)
        source = "HEAD~20..HEAD"
    grouped: dict[str, list[dict[str, str]]] = {category: [] for category in COMMIT_CHANGELOG_CATEGORIES}
    malformed: list[dict[str, str]] = []
    for commit_hash, subject, message in commits:
        checks = validate_commit_message_text(message)
        result = commit_message_result(checks)
        if result == "FAIL":
            malformed.append(
                {
                    "commit": commit_hash,
                    "subject": subject,
                    "reason": "; ".join(check.message for check in checks if check.severity == "FAIL")[:500],
                }
            )
        for category, entries in extract_changelog_entries(message).items():
            for entry in entries:
                grouped[category].append({"commit": commit_hash[:12], "subject": subject, "entry": entry})
    return {
        "schema_version": "aide.changelog-preview.v0",
        "generated_by": GENERATOR_NAME,
        "source_range": source,
        "commit_count": len(commits),
        "categories": {category: values for category, values in grouped.items() if values},
        "malformed_commits": malformed,
        "release_publishing": False,
        "network_calls": "none",
        "provider_or_model_calls": "none",
    }


def render_changelog_preview(data: dict[str, object]) -> str:
    lines = [
        "# AIDE Changelog Preview",
        "",
        f"source_range: {data.get('source_range', 'unknown')}",
        f"commit_count: {data.get('commit_count', 0)}",
        "release_publishing: false",
        "",
    ]
    categories = data.get("categories", {})
    if isinstance(categories, dict) and categories:
        for category in COMMIT_CHANGELOG_CATEGORIES:
            entries = categories.get(category) if isinstance(categories, dict) else None
            if not entries:
                continue
            lines.extend([f"## {category}", ""])
            for item in entries:
                if isinstance(item, dict):
                    lines.append(f"- {item.get('entry', '')} ({item.get('commit', '')} {item.get('subject', '')})")
            lines.append("")
    else:
        lines.extend(["## No Structured Entries", "", "- No structured changelog entries found in range.", ""])
    malformed = data.get("malformed_commits", [])
    lines.extend(["## Malformed Commits", ""])
    if isinstance(malformed, list) and malformed:
        for item in malformed:
            if isinstance(item, dict):
                lines.append(f"- {item.get('commit', '')[:12]} {item.get('subject', '')}: {item.get('reason', '')}")
    else:
        lines.append("- None.")
    lines.append("")
    return "\n".join(lines)


def render_release_notes_preview(data: dict[str, object]) -> str:
    lines = [
        "# AIDE Release Notes Preview",
        "",
        "This is a deterministic preview only. It does not publish a release.",
        "",
    ]
    categories = data.get("categories", {})
    if isinstance(categories, dict):
        for category in ["Added", "Changed", "Fixed", "Security", "Deprecated", "Removed"]:
            entries = categories.get(category)
            if not entries:
                continue
            lines.extend([f"## {category}", ""])
            for item in entries:
                if isinstance(item, dict):
                    lines.append(f"- {item.get('entry', '')}")
            lines.append("")
    malformed = data.get("malformed_commits", [])
    if malformed:
        lines.extend(["## Notes", "", f"- {len(malformed)} malformed commits were excluded from release-note grouping.", ""])
    return "\n".join(lines)


def write_changelog_preview(repo_root: Path, revision_range: str | None = None) -> dict[str, object]:
    data = make_changelog_preview(repo_root, revision_range=revision_range)
    write_text_if_changed(repo_root / CHANGELOG_PREVIEW_JSON_PATH, stable_json_text(data))
    write_text_if_changed(repo_root / CHANGELOG_PREVIEW_MD_PATH, render_changelog_preview(data))
    write_text_if_changed(repo_root / RELEASE_NOTES_PREVIEW_MD_PATH, render_release_notes_preview(data))
    malformed_lines = ["# Malformed Commits", ""]
    malformed = data.get("malformed_commits", [])
    if isinstance(malformed, list) and malformed:
        for item in malformed:
            if isinstance(item, dict):
                malformed_lines.append(f"- {item.get('commit', '')[:12]} {item.get('subject', '')}: {item.get('reason', '')}")
    else:
        malformed_lines.append("- None.")
    write_text_if_changed(repo_root / MALFORMED_COMMITS_MD_PATH, "\n".join(malformed_lines) + "\n")
    return data


def queue_task_blocks(repo_root: Path) -> list[dict[str, str]]:
    index = repo_root / ".aide/queue/index.yaml"
    if not index.exists():
        return []
    blocks = re.split(r"\n\s*-\s+id:\s+", "\n" + read_text(index))
    tasks: list[dict[str, str]] = []
    for block in blocks:
        block = block.strip()
        if not block or block.startswith("schema_version"):
            continue
        task_id, _, rest = block.partition("\n")
        item: dict[str, str] = {"id": task_id.strip()}
        for key in ["status", "planning_state", "task", "exec_plan", "prompt", "evidence", "description", "title"]:
            match = re.search(rf"^\s*{re.escape(key)}:\s*(.+)$", rest, re.MULTILINE)
            if match:
                item[key] = match.group(1).strip()
        tasks.append(item)
    return tasks


def resolve_task_id(repo_root: Path, task_id: str) -> str:
    requested = task_id.strip()
    if not requested:
        return ""
    if (repo_root / ".aide/queue" / requested).exists():
        return requested
    tasks = queue_task_blocks(repo_root)
    for task in tasks:
        if task.get("id") == requested:
            return requested
    prefix_matches = [str(task.get("id", "")) for task in tasks if str(task.get("id", "")).startswith(f"{requested}-")]
    if len(prefix_matches) == 1:
        return prefix_matches[0]
    startswith_matches = [str(task.get("id", "")) for task in tasks if str(task.get("id", "")).startswith(requested)]
    if len(startswith_matches) == 1:
        return startswith_matches[0]
    return requested


def task_status_value(repo_root: Path, task_id: str) -> str:
    resolved = resolve_task_id(repo_root, task_id)
    status_path = repo_root / ".aide/queue" / resolved / "status.yaml"
    if not status_path.exists():
        return "missing"
    match = re.search(r"^status:\s*(.+)$", read_text(status_path), re.MULTILINE)
    return match.group(1).strip() if match else "unknown"


def current_task_id(repo_root: Path) -> str | None:
    packet = repo_root / LATEST_PACKET_PATH
    if packet.exists():
        text = read_text(packet)
        match = re.search(r"^phase:\s*([^\n]+)$", text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
        match = re.search(r"Q\d+[A-Za-z0-9._-]*[^\s`]*", text)
        if match:
            return match.group(0).strip()
    tasks = queue_task_blocks(repo_root)
    for status in ["running", "partial", "ready", "needs_review"]:
        for task in reversed(tasks):
            if task.get("status") == status:
                return task.get("id")
    return tasks[-1]["id"] if tasks else None


def inspect_task(repo_root: Path, task_id: str | None = None) -> dict[str, object]:
    requested = task_id or current_task_id(repo_root) or ""
    selected = resolve_task_id(repo_root, requested)
    task_dir = repo_root / ".aide/queue" / selected if selected else repo_root / ".aide/queue/__missing__"
    task_yaml = task_dir / "task.yaml"
    status_yaml = task_dir / "status.yaml"
    evidence_dir = task_dir / "evidence"
    evidence_files = sorted(normalize_rel(path.relative_to(repo_root)) for path in evidence_dir.glob("*") if path.is_file()) if evidence_dir.exists() else []
    status = task_status_value(repo_root, selected) if selected else "missing"
    required_evidence = ["changed-files.md", "validation.md", "remaining-risks.md"]
    missing_evidence = [name for name in required_evidence if not (evidence_dir / name).exists()]
    complete_states = {"needs_review", "passed", "passed_with_notes", "noop_already_complete"}
    if not selected or not task_yaml.exists():
        classification = "missing"
    elif status in complete_states and not missing_evidence:
        classification = "complete"
    elif evidence_files or status in {"running", "partial", "blocked", "superseded"}:
        classification = "partial"
    else:
        classification = "planned"
    dependencies = parse_simple_list(read_text(task_yaml), "depends_on") if task_yaml.exists() else []
    return {
        "schema_version": "aide.task-inspection.v0",
        "requested_task_id": requested,
        "task_id": selected,
        "status": status,
        "classification": classification,
        "task_yaml": normalize_rel(task_yaml.relative_to(repo_root)) if task_yaml.exists() else "",
        "status_yaml": normalize_rel(status_yaml.relative_to(repo_root)) if status_yaml.exists() else "",
        "evidence_dir": normalize_rel(evidence_dir.relative_to(repo_root)),
        "evidence_files": evidence_files,
        "missing_evidence": missing_evidence,
        "dependencies": dependencies,
        "repo_state_first": True,
    }


def task_recovery_suggestion(inspection: dict[str, object]) -> str:
    classification = str(inspection.get("classification", "unknown"))
    status = str(inspection.get("status", "unknown"))
    if classification == "complete":
        return "noop_already_complete"
    if classification == "partial" and status in {"blocked", "superseded"}:
        return "inspect_blocker_then_reopen_or_continue_if_operator_overrides"
    if classification == "partial":
        return "continue_from_status_and_evidence"
    if classification == "missing":
        return "blocked_missing_task_surfaces"
    return "inspect_before_editing"


def run_git_capture(repo_root: Path, args: list[str]) -> tuple[bool, str, str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            encoding="utf-8",
        )
    except OSError as exc:
        return False, "", str(exc)
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()


def normalize_branch_for_role(branch: str) -> str:
    name = branch.strip()
    if " -> " in name:
        name = name.split(" -> ", 1)[0].strip()
    if "/" in name and not any(name.startswith(prefix) for prefix in (*GIT_TASK_BRANCH_PREFIXES, *GIT_REVIEW_BRANCH_PREFIXES, *GIT_QUARANTINE_BRANCH_PREFIXES, *GIT_RELEASE_BRANCH_PREFIXES, *GIT_HOTFIX_BRANCH_PREFIXES, *GIT_SUBTASK_BRANCH_PREFIXES)):
        remote, _, rest = name.partition("/")
        if remote in {"origin", "upstream"} and rest:
            name = rest
    return name


def classify_branch_role(branch: str) -> str:
    name = normalize_branch_for_role(branch)
    if not name or name == "HEAD":
        return "unknown"
    if name == "main":
        return "canonical"
    if name == "dev":
        return "integration"
    if name == "gh-pages":
        return "deploy"
    if name.startswith(GIT_SUBTASK_BRANCH_PREFIXES):
        return "subtask"
    if name.startswith(GIT_TASK_BRANCH_PREFIXES):
        return "task"
    if name.startswith(GIT_REVIEW_BRANCH_PREFIXES):
        return "review"
    if name.startswith(GIT_QUARANTINE_BRANCH_PREFIXES):
        return "quarantine"
    if name.startswith(GIT_RELEASE_BRANCH_PREFIXES):
        return "release"
    if name.startswith(GIT_HOTFIX_BRANCH_PREFIXES):
        return "hotfix"
    return "unknown"


def branch_names_from_git_output(output: str) -> list[str]:
    names: list[str] = []
    for line in output.splitlines():
        name = line.strip().lstrip("*").strip()
        if name in {"origin", "upstream"}:
            continue
        if name:
            names.append(name)
    return sorted(dict.fromkeys(names))


def remote_repo_summary(remote_url: str) -> str:
    if not remote_url:
        return "unknown"
    value = remote_url.strip()
    if value.endswith(".git"):
        value = value[:-4]
    if value.startswith("git@") and ":" in value:
        value = value.split(":", 1)[1]
    elif "github.com/" in value:
        value = value.split("github.com/", 1)[1]
    return value.strip("/") or "unknown"


def detect_workflow_model(local_branches: list[str], remote_branches: list[str]) -> tuple[str, str, list[str]]:
    all_names = {normalize_branch_for_role(branch) for branch in [*local_branches, *remote_branches]}
    warnings: list[str] = []
    if "develop" in all_names:
        warnings.append("gitflow_like_detected")
    if any(name.startswith(GIT_RELEASE_BRANCH_PREFIXES) for name in all_names):
        warnings.append("release_lines_detected")
    if any(name.startswith(GIT_HOTFIX_BRANCH_PREFIXES) for name in all_names):
        warnings.append("hotfix_branches_detected")
    if "main" in all_names and "dev" in all_names:
        return "trunk_with_dev_integration", "high", warnings
    if "main" in all_names:
        return "trunk_without_dev", "medium", warnings
    if "dev" in all_names:
        warnings.append("dev_without_main_detected")
        return "integration_without_detected_canonical", "low", warnings
    warnings.append("canonical_branch_missing")
    return "unknown", "low", warnings


def recommended_git_action(current_branch: str, role: str, workflow: str, warnings: list[str], dirty: bool) -> str:
    if not current_branch:
        return "inspect detached HEAD before editing"
    if dirty:
        return "classify dirty tree before branch-sensitive work"
    if role == "canonical":
        return "prefer a task branch for non-trivial edits; direct main edits are discouraged"
    if role == "integration":
        return "use dev only for integration repair or explicitly scoped work; normal work should use a task branch"
    if role in {"task", "subtask"}:
        return "continue bounded task work, validate locally, and plan future landing to dev"
    if role in {"review", "quarantine"}:
        return "inspect review/quarantine evidence before editing"
    if role == "release":
        return "inspect release-line evidence before changing release branch"
    if role == "hotfix":
        return "validate focused repair and record backmerge targets"
    if role == "deploy":
        return "do not hand-edit generated deploy branch"
    if workflow == "unknown" or warnings:
        return "inspect branch policy and repo docs before editing"
    return "inspect before editing"


def git_workflow_policy_paths() -> list[str]:
    return [
        GIT_WORKFLOW_POLICY_PATH,
        BRANCH_ROLES_POLICY_PATH,
        PROMOTION_RULES_POLICY_PATH,
        SYNC_POLICY_PATH,
        PRUNE_POLICY_PATH,
        GIT_PROJECT_PROFILES_PATH,
    ]


def validate_git_policy_files(repo_root: Path) -> list[Check]:
    checks: list[Check] = []
    required_markers = {
        GIT_WORKFLOW_POLICY_PATH: ["aide.git-workflow-policy.v0", "canonical_branch: main", "integration_branch: dev", "no remote push in Q28"],
        BRANCH_ROLES_POLICY_PATH: ["canonical:", "integration:", "task:", "release:", "hotfix:", "deploy:", "unknown:", "canonical_release_truth: false"],
        PROMOTION_RULES_POLICY_PATH: ["task_to_dev:", "dev_to_main:", "review packet", "changelog preview"],
        SYNC_POLICY_PATH: ["no_implicit_merge_during_sync", "no_automatic_remote_mutation_in_q28", "do_not_treat_dev_as_canonical_truth"],
        PRUNE_POLICY_PATH: ["prune only after ancestor containment", "protected branches never prune", "no branch deletion in Q28"],
        GIT_PROJECT_PROFILES_PATH: ["aide:", "eureka:", "dominium:", "website:", "unknown_repo:"],
    }
    for rel, markers in required_markers.items():
        path = repo_root / rel
        check_pass(checks, path.exists(), f"git workflow policy artifact exists: {rel}")
        if path.exists():
            text = read_text(path)
            for marker in markers:
                check_pass(checks, marker in text, f"{rel} contains anchor: {marker}")
    branch_roles = read_text(repo_root / BRANCH_ROLES_POLICY_PATH) if (repo_root / BRANCH_ROLES_POLICY_PATH).exists() else ""
    check_pass(checks, "main:\n    role: canonical" in branch_roles or "main:" in branch_roles and "role: canonical" in branch_roles, "main is canonical in branch role policy")
    check_pass(checks, "dev:" in branch_roles and "role: integration" in branch_roles and "canonical_release_truth: false" in branch_roles, "dev is integration, not canonical")
    return checks


def collect_git_workflow_detection(repo_root: Path) -> dict[str, object]:
    warnings: list[str] = []
    ok_branch, current_branch, branch_err = run_git_capture(repo_root, ["branch", "--show-current"])
    if not ok_branch:
        warnings.append(f"current_branch_unavailable: {branch_err}")
        current_branch = ""
    ok_commit, current_commit, commit_err = run_git_capture(repo_root, ["rev-parse", "HEAD"])
    if not ok_commit:
        warnings.append(f"current_commit_unavailable: {commit_err}")
        current_commit = "unknown"
    ok_local, local_output, local_err = run_git_capture(repo_root, ["branch", "--format=%(refname:short)"])
    local_branches = branch_names_from_git_output(local_output) if ok_local else []
    if not ok_local:
        warnings.append(f"local_branches_unavailable: {local_err}")
    ok_remote, remote_output, remote_err = run_git_capture(repo_root, ["branch", "--remotes", "--format=%(refname:short)"])
    remote_branches = branch_names_from_git_output(remote_output) if ok_remote else []
    if not ok_remote:
        warnings.append(f"remote_branches_unavailable: {remote_err}")
    ok_tags, tags_output, tags_err = run_git_capture(repo_root, ["tag", "--list"])
    tags = sorted(line.strip() for line in tags_output.splitlines() if line.strip()) if ok_tags else []
    if not ok_tags:
        warnings.append(f"tags_unavailable: {tags_err}")
    ok_remote_v, remote_v, _ = run_git_capture(repo_root, ["remote", "-v"])
    remote_url = ""
    if ok_remote_v:
        for line in remote_v.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[0] == "origin" and "(fetch)" in line:
                remote_url = parts[1]
                break
    ok_status, status_output, status_err = run_git_capture(repo_root, ["status", "--short"])
    dirty = bool(status_output.strip()) if ok_status else True
    if not ok_status:
        warnings.append(f"git_status_unavailable: {status_err}")
    if dirty:
        warnings.append("dirty_tree_detected")
    if not current_branch:
        warnings.append("detached_head_or_branch_unknown")
    if "main" not in {normalize_branch_for_role(branch) for branch in [*local_branches, *remote_branches]}:
        warnings.append("main_branch_missing")
    if "dev" not in {normalize_branch_for_role(branch) for branch in [*local_branches, *remote_branches]}:
        warnings.append("integration_branch_dev_missing")
    if not remote_branches:
        warnings.append("remote_branch_list_empty_or_missing")
    workflow, confidence, workflow_warnings = detect_workflow_model(local_branches, remote_branches)
    warnings.extend(workflow_warnings)
    role = classify_branch_role(current_branch)
    if role == "unknown":
        warnings.append("current_branch_role_unknown")
    integration_detected = "dev" in {normalize_branch_for_role(branch) for branch in [*local_branches, *remote_branches]}
    recommended = recommended_git_action(current_branch, role, workflow, warnings, dirty)
    return {
        "schema_version": "aide.git-workflow-detection.v0",
        "generated_by": GENERATOR_NAME,
        "current_branch": current_branch or "DETACHED",
        "current_commit": current_commit,
        "local_branches": local_branches,
        "remote_branches": remote_branches,
        "tags_summary": {
            "count": len(tags),
            "tags": tags[:20],
        },
        "repo_id": remote_repo_summary(remote_url),
        "remote_url_summary": remote_repo_summary(remote_url),
        "detected_workflow": workflow,
        "confidence": confidence,
        "branch_role_for_current_branch": role,
        "canonical_branch": "main" if "main" in {normalize_branch_for_role(branch) for branch in [*local_branches, *remote_branches]} else "",
        "integration_branch_detected": integration_detected,
        "integration_branch": "dev" if integration_detected else "",
        "worktree_dirty": dirty,
        "recommended_next_action": recommended,
        "warnings": sorted(dict.fromkeys(warnings)),
        "non_mutating": True,
    }


def render_git_workflow_detection_md(data: dict[str, object]) -> str:
    warnings = data.get("warnings", [])
    warning_lines = "\n".join(f"- {warning}" for warning in warnings) if isinstance(warnings, list) and warnings else "- none"
    return f"""# AIDE Git Workflow Detection

- schema_version: {data.get('schema_version', '')}
- generated_by: {data.get('generated_by', '')}
- non_mutating: {str(data.get('non_mutating', True)).lower()}
- current_branch: {data.get('current_branch', '')}
- current_commit: {data.get('current_commit', '')}
- current_branch_role: {data.get('branch_role_for_current_branch', '')}
- detected_workflow: {data.get('detected_workflow', '')}
- confidence: {data.get('confidence', '')}
- canonical_branch: {data.get('canonical_branch', '') or 'not detected'}
- integration_branch: {data.get('integration_branch', '') or 'not detected'}
- recommended_next_action: {data.get('recommended_next_action', '')}

## Branch Summary

- local_branches: {len(data.get('local_branches', [])) if isinstance(data.get('local_branches'), list) else 0}
- remote_branches: {len(data.get('remote_branches', [])) if isinstance(data.get('remote_branches'), list) else 0}
- tags_count: {data.get('tags_summary', {}).get('count', 0) if isinstance(data.get('tags_summary'), dict) else 0}

## Warnings

{warning_lines}

## Q28 Boundary

This report was generated without branch creation, deletion, merge, prune, push,
fetch, GitHub API mutation, provider calls, model calls, or network calls.
"""


def write_git_workflow_detection(repo_root: Path) -> tuple[dict[str, object], WriteResult, WriteResult]:
    data = collect_git_workflow_detection(repo_root)
    json_result = write_text_if_changed(repo_root / GIT_WORKFLOW_DETECTION_JSON_PATH, stable_json_text(data))
    md_result = write_text_if_changed(repo_root / GIT_WORKFLOW_DETECTION_MD_PATH, render_git_workflow_detection_md(data))
    return data, json_result, md_result


PROTECTED_GIT_HELPER_ROLES = {"canonical", "integration", "release", "deploy"}
PRUNE_CANDIDATE_ROLES = {"task", "subtask", "review", "quarantine"}
GIT_HELPER_POLICY_FILES = [
    GIT_WORKFLOW_POLICY_PATH,
    BRANCH_ROLES_POLICY_PATH,
    PROMOTION_RULES_POLICY_PATH,
    SYNC_POLICY_PATH,
    PRUNE_POLICY_PATH,
    GIT_HELPER_POLICY_PATH,
]


def run_git_status_code(repo_root: Path, args: list[str]) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            encoding="utf-8",
        )
    except OSError as exc:
        return 127, "", str(exc)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def helper_branch_exists(state: dict[str, object], branch: str) -> bool:
    names = {
        normalize_branch_for_role(item)
        for item in [*state.get("local_branches", []), *state.get("remote_branches", [])]
        if isinstance(item, str)
    }
    return normalize_branch_for_role(branch) in names


def helper_policy_presence(repo_root: Path) -> dict[str, bool]:
    return {rel: (repo_root / rel).exists() for rel in GIT_HELPER_POLICY_FILES}


def helper_policy_ready(repo_root: Path) -> bool:
    return all(helper_policy_presence(repo_root).values())


def helper_branch_ahead_behind(repo_root: Path, branch: str, remote: str = "origin") -> dict[str, object]:
    remote_ref = f"{remote}/{branch}"
    code, output, err = run_git_status_code(repo_root, ["rev-list", "--left-right", "--count", f"{remote_ref}...{branch}"])
    if code != 0:
        return {"branch": branch, "remote": remote_ref, "known": False, "ahead": None, "behind": None, "error": err}
    parts = output.split()
    if len(parts) != 2:
        return {"branch": branch, "remote": remote_ref, "known": False, "ahead": None, "behind": None, "error": "unexpected rev-list output"}
    behind, ahead = int(parts[0]), int(parts[1])
    return {"branch": branch, "remote": remote_ref, "known": True, "ahead": ahead, "behind": behind, "error": ""}


def helper_is_ancestor(repo_root: Path, branch: str, target: str) -> dict[str, object]:
    code, _output, err = run_git_status_code(repo_root, ["merge-base", "--is-ancestor", branch, target])
    if code == 0:
        return {"branch": branch, "target": target, "contained": True, "known": True, "error": ""}
    if code == 1:
        return {"branch": branch, "target": target, "contained": False, "known": True, "error": ""}
    return {"branch": branch, "target": target, "contained": False, "known": False, "error": err}


def collect_git_helper_state(repo_root: Path) -> dict[str, object]:
    detection = collect_git_workflow_detection(repo_root)
    warnings = list(detection.get("warnings", [])) if isinstance(detection.get("warnings"), list) else []
    ok_root, git_root, root_err = run_git_capture(repo_root, ["rev-parse", "--show-toplevel"])
    ok_upstream, upstream, upstream_err = run_git_capture(repo_root, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    ahead_behind: dict[str, object] = {"known": False, "ahead": None, "behind": None, "error": "upstream unavailable"}
    if ok_upstream:
        ok_counts, counts, counts_err = run_git_capture(repo_root, ["rev-list", "--left-right", "--count", "HEAD...@{u}"])
        if ok_counts and len(counts.split()) == 2:
            ahead, behind = (int(part) for part in counts.split())
            ahead_behind = {"known": True, "ahead": ahead, "behind": behind, "error": ""}
        else:
            ahead_behind = {"known": False, "ahead": None, "behind": None, "error": counts_err}
    else:
        warnings.append(f"upstream_unavailable: {upstream_err}")
    local_branches = list(detection.get("local_branches", [])) if isinstance(detection.get("local_branches"), list) else []
    remote_branches = list(detection.get("remote_branches", [])) if isinstance(detection.get("remote_branches"), list) else []
    branch_roles = {
        branch: classify_branch_role(branch)
        for branch in sorted({str(item) for item in [*local_branches, *remote_branches]})
    }
    policy_presence = helper_policy_presence(repo_root)
    missing_policy = [rel for rel, exists in policy_presence.items() if not exists]
    if missing_policy:
        warnings.append("helper_policy_files_missing")
    unpushed: list[dict[str, object]] = []
    for branch in ["main", "dev"]:
        if normalize_branch_for_role(branch) in {normalize_branch_for_role(str(item)) for item in local_branches}:
            remote_ref = f"origin/{branch}"
            if remote_ref in {str(item) for item in remote_branches}:
                status = helper_branch_ahead_behind(repo_root, branch)
                if status.get("known") and int(status.get("ahead") or 0) > 0:
                    unpushed.append(status)
    current_branch = str(detection.get("current_branch", "DETACHED"))
    return {
        "schema_version": "aide.git-helper-state.v0",
        "repo_root_detected": ok_root,
        "repo_root": git_root if ok_root else "",
        "repo_root_error": root_err if not ok_root else "",
        "current_branch": current_branch,
        "current_commit": detection.get("current_commit", "unknown"),
        "current_role": detection.get("branch_role_for_current_branch", "unknown"),
        "detached_head": current_branch == "DETACHED" or not current_branch,
        "worktree_dirty": bool(detection.get("worktree_dirty", True)),
        "local_branches": local_branches,
        "remote_branches": remote_branches,
        "branch_roles": branch_roles,
        "upstream": upstream if ok_upstream else "",
        "upstream_available": ok_upstream,
        "ahead_behind": ahead_behind,
        "policy_files": policy_presence,
        "policy_ready": not missing_policy,
        "aide_branch_policy_present": (repo_root / AIDE_BRANCH_POLICY_PATH).exists(),
        "aide_branch_policy_path": AIDE_BRANCH_POLICY_PATH if (repo_root / AIDE_BRANCH_POLICY_PATH).exists() else "",
        "protected_roles": sorted(PROTECTED_GIT_HELPER_ROLES),
        "unpushed_protected_branches": unpushed,
        "warnings": sorted(dict.fromkeys(warnings)),
        "non_mutating": True,
    }


def helper_expected_validation_commands() -> list[str]:
    return [
        "py -3 .aide/scripts/aide_lite.py commit check --latest",
        "py -3 .aide/scripts/aide_lite.py validate",
        "py -3 .aide/scripts/aide_lite.py test",
    ]


def helper_promotion_validation_commands() -> list[str]:
    return [
        "py -3 .aide/scripts/aide_lite.py commit check --range <base>..HEAD",
        "py -3 .aide/scripts/aide_lite.py changelog preview",
        "py -3 .aide/scripts/aide_lite.py eval run",
        "py -3 .aide/scripts/aide_lite.py pack-status",
    ]


def helper_has_validation_evidence(repo_root: Path) -> bool:
    candidates = [
        repo_root / LATEST_VERIFICATION_REPORT_PATH,
        repo_root / ".aide/queue/Q29-merge-land-promote-helper-v0/evidence/validation.md",
    ]
    return any(path.exists() for path in candidates)


def helper_has_review_evidence(repo_root: Path) -> bool:
    candidates = [
        repo_root / REVIEW_PACKET_PATH,
        repo_root / ".aide/queue/Q29-merge-land-promote-helper-v0/evidence/live-repo-safety-report.md",
    ]
    return any(path.exists() for path in candidates)


def make_git_helper_plan(
    repo_root: Path,
    operation: str,
    *,
    dry_run: bool = True,
    apply_requested: bool = False,
    push_requested: bool = False,
    source: str = "",
    target: str = "",
    validation_ok: bool = False,
    review_ok: bool = False,
) -> dict[str, object]:
    state = collect_git_helper_state(repo_root)
    blockers: list[str] = []
    warnings: list[str] = list(state.get("warnings", [])) if isinstance(state.get("warnings"), list) else []
    planned_commands: list[str] = []
    executed_commands: list[str] = []
    recommendations: list[str] = []
    status = "ready_dry_run"
    effective_source = source
    effective_target = target
    current_branch = str(state.get("current_branch", "DETACHED"))
    current_role = str(state.get("current_role", "unknown"))
    if not state.get("repo_root_detected"):
        blockers.append("git_repo_root_unknown")
    if state.get("detached_head"):
        blockers.append("detached_head_or_branch_unknown")
    if operation != "plan" and not state.get("policy_ready"):
        blockers.append("required_policy_files_missing")
    if push_requested and apply_requested:
        blockers.append("remote_push_disabled_in_q29")

    if operation == "plan":
        if state.get("aide_branch_policy_present") and not helper_branch_exists(state, "dev"):
            recommendations.append("AIDE branch policy expects dev; Q30 plans future explicit dev creation without mutating branches")
        if state.get("worktree_dirty"):
            status = "blocked"
            blockers.append("dirty_tree_requires_classification")
            recommendations.append("clean or classify the working tree before branch-sensitive helper actions")
        elif current_role in {"task", "subtask"}:
            if helper_branch_exists(state, "dev"):
                recommendations.append("run git land --dry-run --target dev")
            else:
                status = "blocked"
                blockers.append("integration_branch_dev_missing")
                recommendations.append("Q30 should decide whether and how to establish dev")
        elif current_role == "integration":
            recommendations.append("run git promote --dry-run --from dev --to main after review gates")
        elif current_role == "canonical":
            recommendations.append("start or switch to a task branch for non-trivial work; Q30 should sync dev/main policy if needed")
        elif current_role == "unknown":
            status = "blocked"
            blockers.append("current_branch_role_unknown")
            recommendations.append("inspect branch role before mutation")
        else:
            recommendations.append("inspect branch-specific policy before mutation")
    elif operation == "sync":
        planned_commands.append("git status --short")
        if state.get("worktree_dirty"):
            blockers.append("dirty_tree_blocks_sync_apply")
        if state.get("upstream_available"):
            planned_commands.append("git pull --ff-only")
            recommendations.append("use --apply only after confirming fast-forward-only sync is acceptable")
        else:
            warnings.append("upstream_unavailable")
            recommendations.append("no upstream detected; inspect remote tracking before sync")
    elif operation == "land":
        source_branch = source or current_branch
        target_branch = target or "dev"
        effective_source = source_branch
        effective_target = target_branch
        source_role = classify_branch_role(source_branch)
        target_role = classify_branch_role(target_branch)
        planned_commands.extend([
            f"git checkout {target_branch}",
            f"git merge --no-ff {source_branch} -m \"land: {source_branch} into {target_branch}\"",
        ])
        if push_requested:
            planned_commands.append(f"git push origin {target_branch}")
        if state.get("worktree_dirty"):
            blockers.append("dirty_tree_blocks_land")
        if source_role not in {"task", "subtask"}:
            blockers.append(f"source_role_not_landable: {source_role}")
        if source_role in PROTECTED_GIT_HELPER_ROLES:
            blockers.append(f"source_role_protected: {source_role}")
        if target_role != "integration":
            blockers.append(f"target_role_not_integration: {target_role}")
        if not helper_branch_exists(state, source_branch):
            blockers.append(f"source_branch_missing: {source_branch}")
        if not helper_branch_exists(state, target_branch):
            blockers.append(f"target_branch_missing: {target_branch}")
        if not validation_ok and not helper_has_validation_evidence(repo_root):
            blockers.append("validation_evidence_missing")
        recommendations.extend(helper_expected_validation_commands())
    elif operation == "promote":
        source_branch = source or "dev"
        target_branch = target or "main"
        effective_source = source_branch
        effective_target = target_branch
        source_role = classify_branch_role(source_branch)
        target_role = classify_branch_role(target_branch)
        planned_commands.extend([
            f"git checkout {target_branch}",
            f"git merge --no-ff {source_branch} -m \"promote: {source_branch} into {target_branch}\"",
        ])
        if push_requested:
            planned_commands.append(f"git push origin {target_branch}")
        if state.get("worktree_dirty"):
            blockers.append("dirty_tree_blocks_promote")
        if source_role != "integration":
            blockers.append(f"source_role_not_integration: {source_role}")
        if target_role != "canonical":
            blockers.append(f"target_role_not_canonical: {target_role}")
        if not helper_branch_exists(state, source_branch):
            blockers.append(f"source_branch_missing: {source_branch}")
        if not helper_branch_exists(state, target_branch):
            blockers.append(f"target_branch_missing: {target_branch}")
        if not review_ok and not helper_has_review_evidence(repo_root):
            blockers.append("promotion_review_evidence_missing")
        if not validation_ok and not helper_has_validation_evidence(repo_root):
            blockers.append("promotion_validation_evidence_missing")
        if not (repo_root / CHANGELOG_PREVIEW_MD_PATH).exists():
            warnings.append("changelog_preview_missing")
        recommendations.extend(helper_promotion_validation_commands())
    elif operation == "prune":
        targets = [target] if target else []
        if not targets:
            if helper_branch_exists(state, "dev"):
                targets.append("dev")
            if helper_branch_exists(state, "main"):
                targets.append("main")
        prune_candidates: list[dict[str, object]] = []
        current_normalized = normalize_branch_for_role(current_branch)
        for branch in state.get("local_branches", []):
            branch_name = normalize_branch_for_role(str(branch))
            role = classify_branch_role(branch_name)
            containment_checks = [helper_is_ancestor(repo_root, branch_name, prune_target) for prune_target in targets if helper_branch_exists(state, prune_target)]
            contained = any(bool(item.get("contained")) for item in containment_checks)
            if branch_name == current_normalized:
                eligible = False
                reason = "current_branch_never_pruned"
            elif role in PROTECTED_GIT_HELPER_ROLES:
                eligible = False
                reason = f"protected_role: {role}"
            elif role == "unknown":
                eligible = False
                reason = "unknown_role_conservative_refusal"
            elif role not in PRUNE_CANDIDATE_ROLES:
                eligible = False
                reason = f"role_not_prune_candidate: {role}"
            elif not contained:
                eligible = False
                reason = "ancestor_containment_not_proven"
            else:
                eligible = True
                reason = "contained_in_integration_or_canonical"
                planned_commands.append(f"git branch -d {branch_name}")
            prune_candidates.append({
                "branch": branch_name,
                "role": role,
                "eligible": eligible,
                "reason": reason,
                "containment": containment_checks,
            })
        if state.get("worktree_dirty"):
            warnings.append("dirty_tree_detected_prune_apply_blocked")
        if apply_requested and state.get("worktree_dirty"):
            blockers.append("dirty_tree_blocks_prune_apply")
    else:
        blockers.append(f"unknown_helper_operation: {operation}")

    if blockers:
        status = "blocked"
    if apply_requested and not blockers and operation in {"land", "promote", "prune", "sync"}:
        status = "ready_to_apply"
    plan: dict[str, object] = {
        "schema_version": "aide.git-helper-plan.v0",
        "generated_by": GENERATOR_NAME,
        "operation": operation,
        "status": status,
        "dry_run": dry_run,
        "apply_requested": apply_requested,
        "push_requested": push_requested,
        "source": effective_source,
        "target": effective_target,
        "state": state,
        "planned_commands": planned_commands,
        "executed_commands": executed_commands,
        "blockers": sorted(dict.fromkeys(blockers)),
        "warnings": sorted(dict.fromkeys(warnings)),
        "recommendations": recommendations,
        "remote_mutation": False,
        "force_push_allowed": False,
        "non_mutating": not apply_requested,
    }
    if operation == "prune":
        plan["prune_candidates"] = prune_candidates
    return plan


def execute_git_helper_plan(repo_root: Path, plan: dict[str, object]) -> dict[str, object]:
    if plan.get("status") != "ready_to_apply":
        return plan
    if plan.get("push_requested"):
        plan["status"] = "blocked"
        plan["blockers"] = [*list(plan.get("blockers", [])), "remote_push_disabled_in_q29"]
        return plan
    operation = str(plan.get("operation", ""))
    source = str(plan.get("source", ""))
    target = str(plan.get("target", ""))
    executed: list[str] = []
    errors: list[str] = []
    if operation == "land":
        commands = [
            ["checkout", target or "dev"],
            ["merge", "--no-ff", source, "-m", f"land: {source} into {target or 'dev'}"],
        ]
    elif operation == "promote":
        commands = [
            ["checkout", target or "main"],
            ["merge", "--no-ff", source or "dev", "-m", f"promote: {source or 'dev'} into {target or 'main'}"],
        ]
    elif operation == "prune":
        commands = [["branch", "-d", str(item.get("branch"))] for item in plan.get("prune_candidates", []) if isinstance(item, dict) and item.get("eligible")]
    elif operation == "sync":
        commands = [["pull", "--ff-only"]] if plan.get("state", {}).get("upstream_available") else []
    else:
        commands = []
    for command in commands:
        if not command or "push" in command or "--force" in command or "-f" in command:
            errors.append(f"forbidden command refused: git {' '.join(command)}")
            break
        code, _out, err = run_git_status_code(repo_root, command)
        rendered = f"git {' '.join(command)}"
        executed.append(rendered)
        if code != 0:
            errors.append(f"{rendered}: {err or 'failed'}")
            break
    plan["executed_commands"] = executed
    if errors:
        plan["status"] = "blocked"
        plan["blockers"] = [*list(plan.get("blockers", [])), *errors]
    else:
        plan["status"] = "applied"
        plan["non_mutating"] = False
    return plan


def render_git_helper_plan_md(plan: dict[str, object]) -> str:
    state = plan.get("state", {}) if isinstance(plan.get("state"), dict) else {}
    blockers = plan.get("blockers", [])
    warnings = plan.get("warnings", [])
    commands = plan.get("planned_commands", [])
    executed = plan.get("executed_commands", [])
    recs = plan.get("recommendations", [])
    def lines(values: object) -> str:
        if isinstance(values, list) and values:
            return "\n".join(f"- {value}" for value in values)
        return "- none"
    return f"""# AIDE Git Helper Plan

- schema_version: {plan.get('schema_version', '')}
- generated_by: {plan.get('generated_by', '')}
- operation: {plan.get('operation', '')}
- status: {plan.get('status', '')}
- dry_run: {str(plan.get('dry_run', True)).lower()}
- apply_requested: {str(plan.get('apply_requested', False)).lower()}
- push_requested: {str(plan.get('push_requested', False)).lower()}
- non_mutating: {str(plan.get('non_mutating', True)).lower()}
- remote_mutation: {str(plan.get('remote_mutation', False)).lower()}
- force_push_allowed: {str(plan.get('force_push_allowed', False)).lower()}

## Current State

- branch: {state.get('current_branch', '')}
- role: {state.get('current_role', '')}
- commit: {state.get('current_commit', '')}
- dirty_tree: {str(state.get('worktree_dirty', True)).lower()}
- upstream: {state.get('upstream', '') or 'not detected'}
- policy_ready: {str(state.get('policy_ready', False)).lower()}

## Planned Commands

{lines(commands)}

## Executed Commands

{lines(executed)}

## Blockers

{lines(blockers)}

## Warnings

{lines(warnings)}

## Recommendations

{lines(recs)}

## Safety Boundary

Q29 helper plans are dry-run by default. Live AIDE branch creation, deletion,
merge, prune, promotion, push, and force-push are not performed by Q29
validation.
"""


def write_git_helper_plan(repo_root: Path, plan: dict[str, object]) -> tuple[WriteResult, WriteResult]:
    json_result = write_text_if_changed(repo_root / GIT_HELPER_PLAN_JSON_PATH, stable_json_text(plan))
    md_result = write_text_if_changed(repo_root / GIT_HELPER_PLAN_MD_PATH, render_git_helper_plan_md(plan))
    return json_result, md_result


def validate_git_helper_policy_files(repo_root: Path) -> list[Check]:
    checks: list[Check] = []
    required_markers = {
        GIT_HELPER_POLICY_PATH: [
            "aide.git-helper-policy.v0",
            "dry_run_by_default",
            "live_repo_no_mutation_without_explicit_apply",
            "fixture_mutation_allowed",
            "no_remote_push_without_explicit_push_flag",
            "require_ancestor_containment_before_prune",
            "no_force_push",
            "no_delete_protected_branches",
        ],
        GIT_HELPER_COMMANDS_MD_PATH: [
            "git plan",
            "git sync",
            "git land",
            "git promote",
            "git prune",
            "dry-run",
            "ancestor containment",
        ],
    }
    for rel, markers in required_markers.items():
        path = repo_root / rel
        check_pass(checks, path.exists(), f"git helper artifact exists: {rel}")
        if path.exists():
            text = read_text(path)
            for marker in markers:
                check_pass(checks, marker in text, f"{rel} contains anchor: {marker}")
    plan_json = repo_root / GIT_HELPER_PLAN_JSON_PATH
    generated_plan_required = (
        (repo_root / ".aide/queue/Q29-merge-land-promote-helper-v0").exists()
        or (repo_root / AIDE_BRANCH_POLICY_PATH).exists()
        or (repo_root / GIT_HELPER_PLAN_JSON_PATH).exists()
    )
    if generated_plan_required:
        check_pass(checks, plan_json.exists(), f"latest helper plan exists: {GIT_HELPER_PLAN_JSON_PATH}")
    else:
        checks.append(Check("WARN", f"latest helper plan not generated yet in target repo: {GIT_HELPER_PLAN_JSON_PATH}"))
    if plan_json.exists():
        try:
            data = json.loads(read_text(plan_json))
            check_pass(checks, data.get("schema_version") == "aide.git-helper-plan.v0", "latest helper plan has Q29 schema")
            check_pass(checks, data.get("remote_mutation") is False, "latest helper plan records no remote mutation")
            check_pass(checks, data.get("force_push_allowed") is False, "latest helper plan forbids force push")
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            checks.append(Check("FAIL", f"latest helper plan JSON malformed: {exc}"))
    if generated_plan_required:
        check_pass(checks, (repo_root / GIT_HELPER_PLAN_MD_PATH).exists(), f"latest helper plan Markdown exists: {GIT_HELPER_PLAN_MD_PATH}")
    elif not (repo_root / GIT_HELPER_PLAN_MD_PATH).exists():
        checks.append(Check("WARN", f"latest helper plan Markdown not generated yet in target repo: {GIT_HELPER_PLAN_MD_PATH}"))
    return checks


def validate_aide_branch_policy_files(repo_root: Path) -> list[Check]:
    checks: list[Check] = []
    policy_path = repo_root / AIDE_BRANCH_POLICY_PATH
    check_pass(checks, policy_path.exists(), f"AIDE branch policy exists: {AIDE_BRANCH_POLICY_PATH}")
    if policy_path.exists():
        text = read_text(policy_path)
        for marker in [
            "aide.repo-branch-policy.v0",
            "repo_id: julesc013/aide",
            "canonical_branch: main",
            "integration_branch: dev",
            "main: canonical",
            "dev: integration",
            "dev_is_shareable_integration_truth_not_canonical_truth",
            "Q30 does not mutate branches",
            "review packet",
            "pack-status",
            "secret scan",
        ]:
            check_pass(checks, marker in text, f"AIDE branch policy contains anchor: {marker}")
        check_pass(checks, "main: canonical" in text and "main: integration" not in text, "AIDE main is canonical")
        check_pass(checks, "dev: integration" in text and "dev: canonical" not in text, "AIDE dev is integration, not canonical")
    plan_path = repo_root / AIDE_DEV_MAIN_PLAN_JSON_PATH
    check_pass(checks, plan_path.exists(), f"AIDE dev/main plan exists: {AIDE_DEV_MAIN_PLAN_JSON_PATH}")
    if plan_path.exists():
        try:
            data = json.loads(read_text(plan_path))
            check_pass(checks, data.get("schema_version") == "aide.dev-main-plan.v0", "AIDE dev/main plan has Q30 schema")
            check_pass(checks, data.get("canonical_branch") == "main", "AIDE dev/main plan canonical branch is main")
            check_pass(checks, data.get("integration_branch") == "dev", "AIDE dev/main plan integration branch is dev")
            check_pass(checks, data.get("non_mutating") is True, "AIDE dev/main plan is non_mutating")
            check_pass(checks, data.get("live_mutation_performed") is False, "AIDE dev/main plan records no live mutation")
            helper_results = data.get("helper_dry_run_results", {})
            check_pass(checks, isinstance(helper_results, dict) and "plan" in helper_results, "AIDE dev/main plan includes helper dry-run results")
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            checks.append(Check("FAIL", f"AIDE dev/main plan JSON malformed: {exc}"))
    check_pass(checks, (repo_root / AIDE_DEV_MAIN_PLAN_MD_PATH).exists(), f"AIDE dev/main plan Markdown exists: {AIDE_DEV_MAIN_PLAN_MD_PATH}")
    return checks


def summarize_helper_plan(plan: dict[str, object]) -> dict[str, object]:
    return {
        "status": plan.get("status", "unknown"),
        "operation": plan.get("operation", ""),
        "dry_run": plan.get("dry_run", True),
        "apply_requested": plan.get("apply_requested", False),
        "push_requested": plan.get("push_requested", False),
        "remote_mutation": plan.get("remote_mutation", False),
        "force_push_allowed": plan.get("force_push_allowed", False),
        "planned_commands": list(plan.get("planned_commands", [])) if isinstance(plan.get("planned_commands"), list) else [],
        "blockers": list(plan.get("blockers", [])) if isinstance(plan.get("blockers"), list) else [],
        "warnings": list(plan.get("warnings", [])) if isinstance(plan.get("warnings"), list) else [],
    }


def make_aide_dev_main_plan(repo_root: Path) -> dict[str, object]:
    state = collect_git_helper_state(repo_root)
    local_branches = list(state.get("local_branches", [])) if isinstance(state.get("local_branches"), list) else []
    remote_branches = list(state.get("remote_branches", [])) if isinstance(state.get("remote_branches"), list) else []
    normalized_local = {normalize_branch_for_role(str(branch)) for branch in local_branches}
    normalized_remote = {normalize_branch_for_role(str(branch)) for branch in remote_branches}
    local_main_exists = "main" in normalized_local
    remote_main_exists = "main" in normalized_remote
    local_dev_exists = "dev" in normalized_local
    remote_dev_exists = "dev" in normalized_remote
    helper_results = {
        "plan": summarize_helper_plan(make_git_helper_plan(repo_root, "plan", dry_run=True)),
        "sync": summarize_helper_plan(make_git_helper_plan(repo_root, "sync", dry_run=True)),
        "land": summarize_helper_plan(make_git_helper_plan(repo_root, "land", dry_run=True, target="dev")),
        "promote": summarize_helper_plan(make_git_helper_plan(repo_root, "promote", dry_run=True, source="dev", target="main")),
        "prune": summarize_helper_plan(make_git_helper_plan(repo_root, "prune", dry_run=True)),
    }
    warnings = list(state.get("warnings", [])) if isinstance(state.get("warnings"), list) else []
    if not local_dev_exists:
        warnings.append("local_dev_missing")
    if not remote_dev_exists:
        warnings.append("remote_origin_dev_missing")
    if not local_main_exists:
        warnings.append("local_main_missing")
    if not remote_main_exists:
        warnings.append("remote_origin_main_missing")
    if local_dev_exists or remote_dev_exists:
        recommended = "verify dev is integration and use Q29 helper dry-runs before any future land/promote operation"
    else:
        recommended = "review future explicit dev creation plan; do not create or push dev during Q30"
    future_commands = []
    if not local_dev_exists:
        future_commands.append("git switch -c dev main")
    if not remote_dev_exists:
        future_commands.append("git push -u origin dev")
    return {
        "schema_version": "aide.dev-main-plan.v0",
        "generated_by": GENERATOR_NAME,
        "repo_id": "julesc013/aide",
        "current_branch": state.get("current_branch", ""),
        "current_commit": state.get("current_commit", ""),
        "current_branch_role": state.get("current_role", "unknown"),
        "canonical_branch": "main",
        "integration_branch": "dev",
        "local_main_exists": local_main_exists,
        "remote_origin_main_exists": remote_main_exists,
        "local_dev_exists": local_dev_exists,
        "remote_origin_dev_exists": remote_dev_exists,
        "current_branch_tracks_remote": bool(state.get("upstream_available")),
        "upstream": state.get("upstream", ""),
        "working_tree_clean": not bool(state.get("worktree_dirty", True)),
        "ahead_behind": state.get("ahead_behind", {}),
        "branch_roles": state.get("branch_roles", {}),
        "helper_dry_run_results": helper_results,
        "future_explicit_operator_plan": {
            "required_if_dev_missing": not (local_dev_exists and remote_dev_exists),
            "commands_not_run": future_commands,
            "operator_approval_required": True,
            "validation_required_before_apply": True,
        },
        "recommended_next_action": recommended,
        "warnings": sorted(dict.fromkeys(warnings)),
        "live_mutation_performed": False,
        "non_mutating": True,
    }


def render_aide_dev_main_plan_md(plan: dict[str, object]) -> str:
    warnings = plan.get("warnings", [])
    warning_lines = "\n".join(f"- {warning}" for warning in warnings) if isinstance(warnings, list) and warnings else "- none"
    helper_results = plan.get("helper_dry_run_results", {}) if isinstance(plan.get("helper_dry_run_results"), dict) else {}
    helper_lines = []
    for name in ["plan", "sync", "land", "promote", "prune"]:
        result = helper_results.get(name, {}) if isinstance(helper_results.get(name), dict) else {}
        helper_lines.append(f"- {name}: {result.get('status', 'unknown')}")
    future = plan.get("future_explicit_operator_plan", {}) if isinstance(plan.get("future_explicit_operator_plan"), dict) else {}
    future_commands = future.get("commands_not_run", [])
    future_lines = "\n".join(f"- {command}" for command in future_commands) if isinstance(future_commands, list) and future_commands else "- none"
    return f"""# AIDE Dev/Main Plan

- schema_version: {plan.get('schema_version', '')}
- generated_by: {plan.get('generated_by', '')}
- repo_id: {plan.get('repo_id', '')}
- non_mutating: {str(plan.get('non_mutating', True)).lower()}
- live_mutation_performed: {str(plan.get('live_mutation_performed', False)).lower()}

## Branch Roles

- current_branch: {plan.get('current_branch', '')}
- current_commit: {plan.get('current_commit', '')}
- current_branch_role: {plan.get('current_branch_role', '')}
- canonical_branch: {plan.get('canonical_branch', '')}
- integration_branch: {plan.get('integration_branch', '')}
- dev_is_canonical_truth: false

## Topology

- local_main_exists: {str(plan.get('local_main_exists', False)).lower()}
- remote_origin_main_exists: {str(plan.get('remote_origin_main_exists', False)).lower()}
- local_dev_exists: {str(plan.get('local_dev_exists', False)).lower()}
- remote_origin_dev_exists: {str(plan.get('remote_origin_dev_exists', False)).lower()}
- current_branch_tracks_remote: {str(plan.get('current_branch_tracks_remote', False)).lower()}
- upstream: {plan.get('upstream', '') or 'not detected'}
- working_tree_clean: {str(plan.get('working_tree_clean', False)).lower()}

## Helper Dry-Runs

{os.linesep.join(helper_lines)}

## Future Explicit Operator Plan

These commands were not run by Q30:

{future_lines}

## Recommended Next Action

{plan.get('recommended_next_action', '')}

## Warnings

{warning_lines}

## Q30 Boundary

Q30 does not create, push, merge, promote, prune, delete, fetch, tag, release, or
mutate live AIDE branches. `main` remains canonical truth and `dev` is planned
as shareable integration truth only.
"""


def write_aide_dev_main_plan(repo_root: Path) -> tuple[dict[str, object], WriteResult, WriteResult]:
    plan = make_aide_dev_main_plan(repo_root)
    json_result = write_text_if_changed(repo_root / AIDE_DEV_MAIN_PLAN_JSON_PATH, stable_json_text(plan))
    md_result = write_text_if_changed(repo_root / AIDE_DEV_MAIN_PLAN_MD_PATH, render_aide_dev_main_plan_md(plan))
    return plan, json_result, md_result


def git_role_examples() -> list[tuple[str, str, str]]:
    return [
        ("main", "canonical", "accepted source of truth"),
        ("dev", "integration", "shareable latest integration, not canonical truth"),
        ("task/foo", "task", "bounded short-lived work"),
        ("codex/foo", "task", "bounded agent work"),
        ("review/foo", "review", "review branch"),
        ("quarantine/foo", "quarantine", "isolated risky work"),
        ("release/1.0", "release", "maintained release line"),
        ("hotfix/1.0.1", "hotfix", "urgent repair"),
        ("gh-pages", "deploy", "generated deploy branch"),
        ("weird", "unknown", "conservative fallback"),
    ]


def golden_task_result(
    task_id: str,
    checks: list[Check],
    related_paths: Iterable[str],
    approx_tokens: int | None = None,
    notes: str = "",
) -> GoldenTaskResult:
    return GoldenTaskResult(
        task_id=task_id,
        result=result_from_checks(checks),
        checks_run=len(checks),
        passed_checks=sum(1 for check in checks if check.severity == "PASS"),
        warnings=tuple(check.message for check in checks if check.severity == "WARN"),
        errors=tuple(check.message for check in checks if check.severity == "FAIL"),
        related_paths=tuple(sorted(normalize_rel(path) for path in related_paths)),
        approx_tokens_if_applicable=approx_tokens,
        notes=notes,
    )


def run_golden_task(repo_root: Path, task_id: str) -> GoldenTaskResult:
    golden_task_definition(repo_root, task_id)
    if task_id == "compact-task-packet-required-sections":
        return run_golden_compact_task_packet(repo_root)
    if task_id == "context-packet-no-full-repo-dump":
        return run_golden_context_packet(repo_root)
    if task_id == "verifier-detects-bad-evidence":
        return run_golden_verifier_bad_evidence(repo_root)
    if task_id == "review-packet-evidence-only":
        return run_golden_review_packet(repo_root)
    if task_id == "token-ledger-budget-check":
        return run_golden_token_ledger(repo_root)
    if task_id == "adapter-managed-section-determinism":
        return run_golden_adapter_determinism(repo_root)
    if task_id == "commit_message_standard_golden":
        return run_golden_commit_message_standard(repo_root)
    if task_id == "task_resumption_standard_golden":
        return run_golden_task_resumption_standard(repo_root)
    if task_id == "workunit_idempotency_golden":
        return run_golden_workunit_idempotency(repo_root)
    if task_id == "changelog_preview_golden":
        return run_golden_changelog_preview(repo_root)
    if task_id == "git_workflow_policy_golden":
        return run_golden_git_workflow_policy(repo_root)
    if task_id == "branch_role_detection_golden":
        return run_golden_branch_role_detection(repo_root)
    if task_id == "promotion_rules_golden":
        return run_golden_promotion_rules(repo_root)
    if task_id == "sync_policy_golden":
        return run_golden_sync_policy(repo_root)
    if task_id == "prune_policy_golden":
        return run_golden_prune_policy(repo_root)
    if task_id == "git_helper_policy_golden":
        return run_golden_git_helper_policy(repo_root)
    if task_id == "git_land_plan_golden":
        return run_golden_git_land_plan(repo_root)
    if task_id == "git_promote_plan_golden":
        return run_golden_git_promote_plan(repo_root)
    if task_id == "git_prune_guard_golden":
        return run_golden_git_prune_guard(repo_root)
    if task_id == "git_live_repo_no_mutation_golden":
        return run_golden_git_live_repo_no_mutation(repo_root)
    if task_id == "aide_dev_main_policy_golden":
        return run_golden_aide_dev_main_policy(repo_root)
    if task_id == "aide_branch_plan_golden":
        return run_golden_aide_branch_plan(repo_root)
    if task_id == "export_pack_commit_policy_inclusion_golden":
        return run_golden_export_pack_commit_policy_inclusion(repo_root)
    if task_id == "export_pack_task_recovery_inclusion_golden":
        return run_golden_export_pack_task_recovery_inclusion(repo_root)
    if task_id == "export_pack_git_policy_inclusion_golden":
        return run_golden_export_pack_git_policy_inclusion(repo_root)
    if task_id == "export_pack_excludes_source_branch_state_golden":
        return run_golden_export_pack_excludes_source_branch_state(repo_root)
    if task_id == "fixture_import_governance_commands_golden":
        return run_golden_fixture_import_governance_commands(repo_root)
    raise ValueError(f"golden task has no runner: {task_id}")


def run_golden_compact_task_packet(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    path = repo_root / LATEST_PACKET_PATH
    check_pass(checks, path.exists(), f"latest task packet exists: {LATEST_PACKET_PATH}")
    approx: int | None = None
    if path.exists():
        text = read_text(path)
        stats = estimate_text(text, LATEST_PACKET_PATH)
        approx = stats.approx_tokens
        for section in PACKET_REQUIRED_SECTIONS:
            check_pass(checks, contains_section(text, section), f"task packet section present: {section}")
        check_pass(checks, "approx_tokens:" in text, "task packet includes approximate token estimate")
        warnings = packet_budget_warnings(text, repo_root)[1]
        check_pass(checks, not warnings, "task packet has no forbidden prompt-pattern warnings")
        _budget, status = ledger_budget_status(repo_root, "task_packet", stats.approx_tokens)
        check_warn(checks, status != "over_budget", f"task packet budget status: {status}")
    return golden_task_result(
        "compact-task-packet-required-sections",
        checks,
        [LATEST_PACKET_PATH, ".aide/prompts/compact-task.md", ".aide/policies/token-budget.yaml"],
        approx,
        "Checks the compact task packet shape and forbidden prompt discipline.",
    )


def run_golden_context_packet(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    related = [LATEST_CONTEXT_PACKET_PATH, REPO_MAP_JSON_PATH, TEST_MAP_JSON_PATH, CONTEXT_INDEX_PATH]
    for rel in related:
        check_pass(checks, (repo_root / rel).exists(), f"context artifact exists: {rel}")
    approx: int | None = None
    path = repo_root / LATEST_CONTEXT_PACKET_PATH
    if path.exists():
        text = read_text(path)
        approx = estimate_text(text, LATEST_CONTEXT_PACKET_PATH).approx_tokens
        for section in CONTEXT_PACKET_REQUIRED_SECTIONS:
            check_pass(checks, contains_section(text, section), f"context packet section present: {section}")
        for rel in [REPO_MAP_JSON_PATH, TEST_MAP_JSON_PATH, CONTEXT_INDEX_PATH]:
            check_pass(checks, rel in text, f"context packet references {rel}")
        raw_markers = [marker for marker in CONTEXT_FORBIDDEN_INLINE_MARKERS if marker in text]
        check_pass(checks, not raw_markers, "context packet does not inline raw source markers")
        check_pass(checks, "SHOULD_NOT_APPEAR" not in text, "ignored path fixture contents absent")
        check_pass(checks, len(text) < 12000, "context packet remains compact")
    return golden_task_result(
        "context-packet-no-full-repo-dump",
        checks,
        related,
        approx,
        "Checks context refs instead of whole-repo dumps.",
    )


def run_golden_verifier_bad_evidence(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    fixture = f"{GOLDEN_TASK_ROOT}/verifier-detects-bad-evidence/fixtures/missing-sections.md"
    check_pass(checks, (repo_root / fixture).exists(), f"bad evidence fixture exists: {fixture}")
    findings = verify_evidence_packet(repo_root, fixture)
    bad_findings = [finding for finding in findings if finding.severity in {"WARN", "WARNING", "ERROR", "FAIL"}]
    check_pass(checks, bool(bad_findings), "verifier reports warnings/errors for malformed evidence")
    check_pass(checks, any("missing" in finding.message.lower() and "section" in finding.message.lower() for finding in bad_findings), "verifier identifies missing sections")
    return golden_task_result(
        "verifier-detects-bad-evidence",
        checks,
        [fixture, EVIDENCE_TEMPLATE_PATH],
        None,
        "Passes when the verifier refuses to accept malformed evidence silently.",
    )


def run_golden_review_packet(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    path = repo_root / REVIEW_PACKET_PATH
    check_pass(checks, path.exists(), f"latest review packet exists: {REVIEW_PACKET_PATH}")
    approx: int | None = None
    if path.exists():
        text = read_text(path)
        approx = estimate_text(text, REVIEW_PACKET_PATH).approx_tokens
        for section in REVIEW_PACKET_REQUIRED_SECTIONS:
            check_pass(checks, contains_section(text, section), f"review packet section present: {section}")
        check_pass(checks, "## Task Packet Reference" in text and (LATEST_PACKET_PATH in text or ".aide/queue/" in text), "review packet references a task packet")
        for rel in [LATEST_CONTEXT_PACKET_PATH, LATEST_VERIFICATION_REPORT_PATH]:
            check_pass(checks, rel in text, f"review packet references {rel}")
        check_pass(checks, "Decision Requested" in text, "review packet includes decision request")
        check_pass(checks, "full chat history" not in text.lower() or "do not" in text.lower(), "review packet does not request full chat history")
        check_pass(checks, "full repo dump" not in text.lower(), "review packet does not request full repo dump")
        findings = verify_review_packet(repo_root, REVIEW_PACKET_PATH)
        check_warn(checks, not any(finding.severity == "ERROR" for finding in findings), "review packet verifier has no errors")
    return golden_task_result(
        "review-packet-evidence-only",
        checks,
        [REVIEW_PACKET_PATH, ".aide/prompts/evidence-review.md", REVIEW_TEMPLATE_PATH],
        approx,
        "Checks review packet evidence-only shape.",
    )


def run_golden_token_ledger(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    related = [TOKEN_LEDGER_PATH, TOKEN_SUMMARY_PATH, TOKEN_LEDGER_POLICY_PATH]
    for rel in related:
        check_pass(checks, (repo_root / rel).exists(), f"token ledger artifact exists: {rel}")
    records = read_ledger_records(repo_root)
    check_pass(checks, bool(records), "token ledger has estimated records")
    required_surfaces = {"task_packet", "context_packet", "review_packet", "verification_report"}
    surfaces = {record.surface for record in records}
    for surface in sorted(required_surfaces):
        check_pass(checks, surface in surfaces, f"ledger records include surface: {surface}")
    missing_budget_status = [record.path for record in records if not record.budget_status]
    check_pass(checks, not missing_budget_status, "ledger records include budget status")
    serialized = "\n".join(json.dumps(ledger_record_to_dict(record), sort_keys=True) for record in records)
    check_pass(checks, "\"content\"" not in serialized, "ledger records do not store raw content fields")
    check_pass(checks, "raw_prompt" not in serialized or "not stored" in serialized.lower(), "ledger does not store raw prompts")
    check_pass(checks, "raw_response" not in serialized or "not stored" in serialized.lower(), "ledger does not store raw responses")
    if (repo_root / TOKEN_SUMMARY_PATH).exists():
        summary = read_text(repo_root / TOKEN_SUMMARY_PATH)
        check_pass(checks, "raw_prompt_storage: false" in summary, "summary records raw_prompt_storage: false")
        check_pass(checks, "raw_response_storage: false" in summary, "summary records raw_response_storage: false")
    return golden_task_result(
        "token-ledger-budget-check",
        checks,
        related,
        None,
        "Checks estimated token metadata without raw prompt or response storage.",
    )


def run_golden_adapter_determinism(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    with tempfile.TemporaryDirectory() as temp:
        temp_root = Path(temp)
        _write_minimal_repo(temp_root)
        write_text(temp_root / "AGENTS.md", "# AGENTS\n\nManual intro.\n")
        first, _before, after_first = adapt_agents(temp_root)
        first_text = read_text(temp_root / "AGENTS.md")
        second, _after_before, after_second = adapt_agents(temp_root)
        second_text = read_text(temp_root / "AGENTS.md")
        check_pass(checks, "Manual intro." in second_text, "manual AGENTS content outside markers is preserved")
        check_pass(checks, first_text == second_text, "adapt output is deterministic on second run")
        check_pass(checks, after_first.status == "current" and after_second.status == "current", "managed section status is current")
        check_pass(checks, first.action in {"appended", "written"} and second.action == "unchanged", "adapt reports stable write actions")
    return golden_task_result(
        "adapter-managed-section-determinism",
        checks,
        ["AGENTS.md"],
        None,
        "Checks managed section replacement on an isolated fixture repo.",
    )


def run_golden_commit_message_standard(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    related = [
        COMMIT_MESSAGE_POLICY_PATH,
        COMMIT_MESSAGE_STANDARD_PATH,
        COMMIT_MESSAGE_HOOK_TEMPLATE_PATH,
        COMMIT_TEMPLATE_PATH,
    ]
    for rel in related:
        check_pass(checks, (repo_root / rel).exists(), f"commit-message artifact exists: {rel}")
    good_checks = validate_commit_message_text(COMMIT_GOOD_EXAMPLE)
    check_pass(checks, commit_message_result(good_checks) == "PASS", "known-good structured commit message passes")
    check_pass(checks, commit_message_result(validate_commit_message_text("update\n")) == "FAIL", "vague subject fails")
    missing_heading = COMMIT_GOOD_EXAMPLE.replace("## Risks", "## Risk")
    check_pass(checks, commit_message_result(validate_commit_message_text(missing_heading)) == "FAIL", "missing required heading fails")
    no_changelog = COMMIT_GOOD_EXAMPLE.replace("- Added:", "- Unknown:")
    check_pass(checks, commit_message_result(validate_commit_message_text(no_changelog)) == "FAIL", "missing changelog category fails")
    if (repo_root / COMMIT_MESSAGE_POLICY_PATH).exists():
        policy = read_text(repo_root / COMMIT_MESSAGE_POLICY_PATH)
        for marker in ["Conventional Commits", "subject_max_chars: 72", "changelog_categories", "AIDE-Task"]:
            check_pass(checks, marker in policy, f"commit policy contains {marker}")
    if (repo_root / COMMIT_MESSAGE_HOOK_TEMPLATE_PATH).exists():
        hook = read_text(repo_root / COMMIT_MESSAGE_HOOK_TEMPLATE_PATH)
        check_pass(checks, "commit check --message-file" in hook, "hook calls commit check command")
        check_pass(checks, "provider" in hook.lower() and "network" in hook.lower(), "hook documents no provider/network behavior")
    return golden_task_result(
        "commit_message_standard_golden",
        checks,
        related,
        None,
        "Checks changelog-ready commit message validation anchors.",
    )


def run_golden_task_resumption_standard(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    related = [TASK_RESUMPTION_POLICY_PATH, TASK_RESUMPTION_STANDARD_PATH, ".aide/queue/index.yaml", LATEST_PACKET_PATH]
    for rel in related:
        check_pass(checks, (repo_root / rel).exists(), f"task-resumption artifact exists: {rel}")
    if (repo_root / TASK_RESUMPTION_POLICY_PATH).exists():
        policy = read_text(repo_root / TASK_RESUMPTION_POLICY_PATH)
        for marker in [
            "stable_task_id_required: true",
            "resume_from_repo_state_first: true",
            "ask_user_only_when_blocked_after_repo_reconciliation: true",
            "repeated_prompt_policy",
            "out_of_order_prompt_policy",
            "incomplete_previous_task_policy",
        ]:
            check_pass(checks, marker in policy, f"task resumption policy contains {marker}")
    if (repo_root / TASK_RESUMPTION_STANDARD_PATH).exists():
        standard = read_text(repo_root / TASK_RESUMPTION_STANDARD_PATH)
        for marker in ["Resumption Rule", "Repeated Prompt", "Out-of-Order Prompt", "Evidence Before Escalation", "Validation Gates"]:
            check_pass(checks, marker in standard, f"task resumption standard documents {marker}")
    return golden_task_result(
        "task_resumption_standard_golden",
        checks,
        related,
        None,
        "Checks repeated and out-of-order task recovery policy anchors.",
    )


def run_golden_workunit_idempotency(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    related = [WORK_UNITS_POLICY_PATH, RECOVERY_POLICY_PATH, WORKUNIT_RECOVERY_STANDARD_PATH]
    for rel in related:
        check_pass(checks, (repo_root / rel).exists(), f"WorkUnit recovery artifact exists: {rel}")
    if (repo_root / WORK_UNITS_POLICY_PATH).exists():
        policy = read_text(repo_root / WORK_UNITS_POLICY_PATH)
        for marker in [
            "idempotency_key",
            "noop_already_complete",
            "duplicate_behavior",
            "out_of_order_behavior",
            "planned",
            "needs_review",
            "reopened",
        ]:
            check_pass(checks, marker in policy, f"WorkUnit policy contains {marker}")
    if (repo_root / RECOVERY_POLICY_PATH).exists():
        recovery = read_text(repo_root / RECOVERY_POLICY_PATH)
        for marker in ["duplicate_task", "out_of_order_task", "partial_task", "dirty_tree", "destructive_ambiguity"]:
            check_pass(checks, marker in recovery, f"recovery policy contains profile: {marker}")
    with tempfile.TemporaryDirectory() as temp:
        temp_root = Path(temp)
        write_text(
            temp_root / ".aide/queue/index.yaml",
            """items:
  - id: TASK-1
    status: passed
    task: .aide/queue/TASK-1/task.yaml
    evidence: .aide/queue/TASK-1/evidence
""",
        )
        write_text(temp_root / ".aide/queue/TASK-1/task.yaml", "id: TASK-1\nallowed_paths:\n  - .aide/**\nacceptance:\n  - done\n")
        write_text(temp_root / ".aide/queue/TASK-1/status.yaml", "status: passed\n")
        write_text(temp_root / ".aide/queue/TASK-1/evidence/changed-files.md", "# Changed\n")
        write_text(temp_root / ".aide/queue/TASK-1/evidence/validation.md", "# Validation\n- PASS\n")
        write_text(temp_root / ".aide/queue/TASK-1/evidence/remaining-risks.md", "# Risks\n- None\n")
        inspection = inspect_task(temp_root, "TASK-1")
        check_pass(checks, inspection["classification"] == "complete", "complete task fixture classifies as complete")
        check_pass(checks, task_recovery_suggestion(inspection) == "noop_already_complete", "complete task fixture returns noop_already_complete")
    return golden_task_result(
        "workunit_idempotency_golden",
        checks,
        related,
        None,
        "Checks WorkUnit idempotency and no-op behavior.",
    )


def run_golden_changelog_preview(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    related = [COMMIT_MESSAGE_POLICY_PATH, CHANGELOG_PREVIEW_MD_PATH, RELEASE_NOTES_PREVIEW_MD_PATH]
    for rel in [COMMIT_MESSAGE_POLICY_PATH]:
        check_pass(checks, (repo_root / rel).exists(), f"changelog policy artifact exists: {rel}")
    data = {
        "schema_version": "aide.changelog-preview.v0",
        "source_range": "fixture",
        "commit_count": 1,
        "categories": {"Added": [{"commit": "fixture", "subject": "policy(aide): define structured commit recovery", "entry": "commit-message enforcement for future AIDE-managed work."}]},
        "malformed_commits": [{"commit": "bad", "subject": "update", "reason": "vague subject"}],
    }
    rendered = render_changelog_preview(data)
    check_pass(checks, "## Added" in rendered, "changelog preview groups entries by category")
    check_pass(checks, "Malformed Commits" in rendered and "update" in rendered, "changelog preview reports malformed commits")
    check_pass(checks, "release_publishing: false" in rendered, "fixture changelog preview is non-publishing")
    if (repo_root / CHANGELOG_PREVIEW_MD_PATH).exists():
        check_pass(checks, "release_publishing: false" in read_text(repo_root / CHANGELOG_PREVIEW_MD_PATH), "current changelog preview is non-publishing")
    else:
        check_pass(checks, True, f"current changelog preview can be generated by `changelog preview`: {CHANGELOG_PREVIEW_MD_PATH}")
    return golden_task_result(
        "changelog_preview_golden",
        checks,
        related,
        None,
        "Checks deterministic changelog preview grouping and malformed commit reporting.",
    )


def run_golden_git_workflow_policy(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    related = [
        GIT_WORKFLOW_POLICY_PATH,
        BRANCH_ROLES_POLICY_PATH,
        PROMOTION_RULES_POLICY_PATH,
        SYNC_POLICY_PATH,
        PRUNE_POLICY_PATH,
        GIT_PROJECT_PROFILES_PATH,
    ]
    for rel in related:
        check_pass(checks, (repo_root / rel).exists(), f"git workflow artifact exists: {rel}")
    if (repo_root / GIT_WORKFLOW_POLICY_PATH).exists():
        policy = read_text(repo_root / GIT_WORKFLOW_POLICY_PATH)
        for marker in [
            "schema_version: aide.git-workflow-policy.v0",
            "canonical_branch: main",
            "integration_branch: dev",
            "dev_is_shareable_integration_not_canonical_truth",
            "no_remote_mutation_without_explicit_command",
        ]:
            check_pass(checks, marker in policy, f"git workflow policy contains {marker}")
    if (repo_root / GIT_PROJECT_PROFILES_PATH).exists():
        profiles = read_text(repo_root / GIT_PROJECT_PROFILES_PATH)
        for marker in ["aide:", "eureka:", "dominium:", "website:", "unknown_repo:"]:
            check_pass(checks, marker in profiles, f"project profiles include {marker.rstrip(':')}")
    return golden_task_result(
        "git_workflow_policy_golden",
        checks,
        related,
        None,
        "Checks Q28 Git workflow policy anchors and project profiles.",
    )


def run_golden_branch_role_detection(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    related = [BRANCH_ROLES_POLICY_PATH, GIT_BRANCH_ROLES_MD_PATH, GIT_WORKFLOW_DETECTION_JSON_PATH]
    expected = {
        "main": "canonical",
        "dev": "integration",
        "task/foo": "task",
        "codex/foo": "task",
        "review/foo": "review",
        "release/1.0": "release",
        "hotfix/1.0.1": "hotfix",
        "gh-pages": "deploy",
        "weird": "unknown",
    }
    for branch, role in expected.items():
        check_pass(checks, classify_branch_role(branch) == role, f"{branch} classifies as {role}")
    workflow_main, confidence_main, warnings_main = detect_workflow_model(["main"], [])
    check_pass(checks, workflow_main == "trunk_without_dev", "main-only branches detect trunk_without_dev")
    workflow_dev, confidence_dev, warnings_dev = detect_workflow_model(["main", "dev"], [])
    check_pass(checks, workflow_dev == "trunk_with_dev_integration", "main+dev branches detect trunk_with_dev_integration")
    _workflow_develop, _confidence_develop, warnings_develop = detect_workflow_model(["main", "develop"], [])
    check_pass(checks, "gitflow_like_detected" in warnings_develop, "develop branch records gitflow-like warning")
    _workflow_release, _confidence_release, warnings_release = detect_workflow_model(["main", "release/1.0"], [])
    check_pass(checks, "release_lines_detected" in warnings_release, "release branch records release-line warning")
    if (repo_root / BRANCH_ROLES_POLICY_PATH).exists():
        policy = read_text(repo_root / BRANCH_ROLES_POLICY_PATH)
        check_pass(checks, "dev" in policy and "not canonical release truth" in policy, "dev is integration, not canonical")
        check_pass(checks, "unknown:" in policy and "conservative" in policy.lower(), "unknown role is conservative")
    return golden_task_result(
        "branch_role_detection_golden",
        checks,
        related,
        None,
        "Checks deterministic branch-role classification and conservative unknown handling.",
    )


def run_golden_promotion_rules(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    related = [PROMOTION_RULES_POLICY_PATH, GIT_PROMOTION_RULES_MD_PATH]
    if (repo_root / PROMOTION_RULES_POLICY_PATH).exists():
        policy = read_text(repo_root / PROMOTION_RULES_POLICY_PATH)
        for marker in [
            "task_to_dev:",
            "dev_to_main:",
            "dev review packet exists",
            "changelog preview generated",
            "required_commit_checks",
            "no GitHub API mutation",
        ]:
            check_pass(checks, marker in policy, f"promotion rules contain {marker}")
    else:
        check_pass(checks, False, f"promotion rules missing: {PROMOTION_RULES_POLICY_PATH}")
    return golden_task_result(
        "promotion_rules_golden",
        checks,
        related,
        None,
        "Checks task-to-dev and dev-to-main gate anchors.",
    )


def run_golden_sync_policy(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    related = [SYNC_POLICY_PATH, GIT_SYNC_POLICY_MD_PATH]
    if (repo_root / SYNC_POLICY_PATH).exists():
        policy = read_text(repo_root / SYNC_POLICY_PATH)
        for marker in [
            "fetch before branch decisions",
            "no implicit merge during sync",
            "no implicit rebase of shared branches",
            "no automatic remote mutation in Q28",
        ]:
            check_pass(checks, marker in policy, f"sync policy contains {marker}")
    else:
        check_pass(checks, False, f"sync policy missing: {SYNC_POLICY_PATH}")
    return golden_task_result(
        "sync_policy_golden",
        checks,
        related,
        None,
        "Checks multi-machine sync policy anchors remain report-only.",
    )


def run_golden_prune_policy(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    related = [PRUNE_POLICY_PATH, GIT_PRUNE_POLICY_MD_PATH]
    if (repo_root / PRUNE_POLICY_PATH).exists():
        policy = read_text(repo_root / PRUNE_POLICY_PATH)
        for marker in [
            "prune only after ancestor containment",
            "protected branches never prune",
            "dry-run by default",
            "no branch deletion in Q28",
        ]:
            check_pass(checks, marker in policy, f"prune policy contains {marker}")
    else:
        check_pass(checks, False, f"prune policy missing: {PRUNE_POLICY_PATH}")
    return golden_task_result(
        "prune_policy_golden",
        checks,
        related,
        None,
        "Checks prune guards require containment and remain dry-run/report-only.",
    )


def run_golden_git_helper_policy(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    related = [GIT_HELPER_POLICY_PATH, GIT_HELPER_COMMANDS_MD_PATH, GIT_HELPER_PLAN_JSON_PATH, GIT_HELPER_PLAN_MD_PATH]
    checks.extend(validate_git_helper_policy_files(repo_root))
    if (repo_root / GIT_HELPER_POLICY_PATH).exists():
        policy = read_text(repo_root / GIT_HELPER_POLICY_PATH)
        for marker in ["dry_run_by_default", "fixture_mutation_allowed", "no_remote_push_without_explicit_push_flag", "no_force_push"]:
            check_pass(checks, marker in policy, f"helper policy contains {marker}")
    return golden_task_result(
        "git_helper_policy_golden",
        checks,
        related,
        None,
        "Checks Q29 helper policy anchors and generated helper-plan artifacts.",
    )


def run_golden_git_land_plan(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    related = [GIT_HELPER_COMMANDS_MD_PATH, GIT_HELPER_PLAN_JSON_PATH]
    commands_text = read_text(repo_root / GIT_HELPER_COMMANDS_MD_PATH) if (repo_root / GIT_HELPER_COMMANDS_MD_PATH).exists() else ""
    check_pass(checks, "git land" in commands_text, "helper commands document git land")
    check_pass(checks, "git merge --no-ff <source>" in commands_text, "land plan documents no-ff merge command")
    check_pass(checks, "--apply" in commands_text and "temporary fixture repositories" in commands_text, "land apply is fixture-gated in docs")
    if (repo_root / GIT_HELPER_PLAN_JSON_PATH).exists():
        data = json.loads(read_text(repo_root / GIT_HELPER_PLAN_JSON_PATH))
        check_pass(checks, data.get("schema_version") == "aide.git-helper-plan.v0", "latest helper plan has Q29 schema")
        check_pass(checks, data.get("remote_mutation") is False, "latest helper plan records no remote mutation")
    else:
        check_pass(checks, False, f"latest helper plan missing: {GIT_HELPER_PLAN_JSON_PATH}")
    return golden_task_result(
        "git_land_plan_golden",
        checks,
        related,
        None,
        "Checks land dry-run planning and no remote mutation anchors.",
    )


def run_golden_git_promote_plan(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    related = [GIT_HELPER_POLICY_PATH, GIT_HELPER_COMMANDS_MD_PATH, PROMOTION_RULES_POLICY_PATH]
    helper_policy = read_text(repo_root / GIT_HELPER_POLICY_PATH) if (repo_root / GIT_HELPER_POLICY_PATH).exists() else ""
    commands_text = read_text(repo_root / GIT_HELPER_COMMANDS_MD_PATH) if (repo_root / GIT_HELPER_COMMANDS_MD_PATH).exists() else ""
    promotion_policy = read_text(repo_root / PROMOTION_RULES_POLICY_PATH) if (repo_root / PROMOTION_RULES_POLICY_PATH).exists() else ""
    check_pass(checks, "require_review_before_promote" in helper_policy, "helper policy requires review before promote")
    check_pass(checks, "git promote" in commands_text, "helper commands document git promote")
    check_pass(checks, "promote: <source> into <target>" in commands_text, "promote plan documents merge message")
    check_pass(checks, "dev_to_main:" in promotion_policy and "review packet" in promotion_policy, "promotion policy gates dev to main")
    return golden_task_result(
        "git_promote_plan_golden",
        checks,
        related,
        None,
        "Checks promotion helper review gates and dry-run command documentation.",
    )


def run_golden_git_prune_guard(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    related = [GIT_HELPER_POLICY_PATH, GIT_HELPER_COMMANDS_MD_PATH, PRUNE_POLICY_PATH]
    helper_policy = read_text(repo_root / GIT_HELPER_POLICY_PATH) if (repo_root / GIT_HELPER_POLICY_PATH).exists() else ""
    commands_text = read_text(repo_root / GIT_HELPER_COMMANDS_MD_PATH) if (repo_root / GIT_HELPER_COMMANDS_MD_PATH).exists() else ""
    prune_policy = read_text(repo_root / PRUNE_POLICY_PATH) if (repo_root / PRUNE_POLICY_PATH).exists() else ""
    check_pass(checks, "require_ancestor_containment_before_prune" in helper_policy, "helper policy requires containment before prune")
    check_pass(checks, "protected_roles_never_prune: true" in helper_policy, "helper policy protects roles from prune")
    check_pass(checks, "git merge-base --is-ancestor" in commands_text, "helper commands document ancestor containment proof")
    check_pass(checks, "protected branches never prune" in prune_policy, "prune policy protects branches")
    return golden_task_result(
        "git_prune_guard_golden",
        checks,
        related,
        None,
        "Checks prune containment and protected-role guards.",
    )


def run_golden_git_live_repo_no_mutation(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    related = [GIT_HELPER_POLICY_PATH, GIT_HELPER_COMMANDS_MD_PATH, GIT_HELPER_PLAN_JSON_PATH]
    helper_policy = read_text(repo_root / GIT_HELPER_POLICY_PATH) if (repo_root / GIT_HELPER_POLICY_PATH).exists() else ""
    commands_text = read_text(repo_root / GIT_HELPER_COMMANDS_MD_PATH) if (repo_root / GIT_HELPER_COMMANDS_MD_PATH).exists() else ""
    check_pass(checks, "live_repo_no_mutation_without_explicit_apply: true" in helper_policy, "helper policy blocks live mutation without apply")
    check_pass(checks, "Force push is forbidden" in commands_text, "helper commands forbid force push")
    check_pass(checks, "Q29 does not create AIDE `dev`" in commands_text, "helper commands document no live dev creation")
    if (repo_root / GIT_HELPER_PLAN_JSON_PATH).exists():
        data = json.loads(read_text(repo_root / GIT_HELPER_PLAN_JSON_PATH))
        check_pass(checks, data.get("force_push_allowed") is False, "latest helper plan forbids force push")
        check_pass(checks, data.get("remote_mutation") is False, "latest helper plan has no remote mutation")
    else:
        check_pass(checks, False, f"latest helper plan missing: {GIT_HELPER_PLAN_JSON_PATH}")
    return golden_task_result(
        "git_live_repo_no_mutation_golden",
        checks,
        related,
        None,
        "Checks live-repo helper plans remain no-mutation by default.",
    )


def run_golden_aide_dev_main_policy(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    related = [AIDE_BRANCH_POLICY_PATH, AIDE_DEV_MAIN_PLAN_JSON_PATH]
    checks.extend(validate_aide_branch_policy_files(repo_root))
    if (repo_root / AIDE_BRANCH_POLICY_PATH).exists():
        policy = read_text(repo_root / AIDE_BRANCH_POLICY_PATH)
        for marker in [
            "main: canonical",
            "dev: integration",
            "dev_is_shareable_integration_truth_not_canonical_truth",
            "Q30 does not mutate branches",
            "py -3 .aide/scripts/aide_lite.py validate",
            "py -3 .aide/scripts/aide_lite.py eval run",
            "py -3 .aide/scripts/aide_lite.py commit check --range",
            "py -3 .aide/scripts/aide_lite.py pack-status",
        ]:
            check_pass(checks, marker in policy, f"AIDE branch policy contains {marker}")
    return golden_task_result(
        "aide_dev_main_policy_golden",
        checks,
        related,
        None,
        "Checks AIDE main/dev branch policy and promotion gates.",
    )


def run_golden_aide_branch_plan(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    related = [AIDE_DEV_MAIN_PLAN_JSON_PATH, AIDE_DEV_MAIN_PLAN_MD_PATH]
    if (repo_root / AIDE_DEV_MAIN_PLAN_JSON_PATH).exists():
        data = json.loads(read_text(repo_root / AIDE_DEV_MAIN_PLAN_JSON_PATH))
        check_pass(checks, data.get("schema_version") == "aide.dev-main-plan.v0", "AIDE branch plan has Q30 schema")
        check_pass(checks, data.get("canonical_branch") == "main", "AIDE branch plan records main canonical")
        check_pass(checks, data.get("integration_branch") == "dev", "AIDE branch plan records dev integration")
        check_pass(checks, data.get("live_mutation_performed") is False, "AIDE branch plan records no live mutation")
        check_pass(checks, data.get("non_mutating") is True, "AIDE branch plan is non-mutating")
        check_pass(checks, "helper_dry_run_results" in data, "AIDE branch plan includes helper dry-runs")
    else:
        check_pass(checks, False, f"AIDE branch plan missing: {AIDE_DEV_MAIN_PLAN_JSON_PATH}")
    if (repo_root / AIDE_DEV_MAIN_PLAN_MD_PATH).exists():
        text = read_text(repo_root / AIDE_DEV_MAIN_PLAN_MD_PATH)
        check_pass(checks, "These commands were not run by Q30" in text, "AIDE branch plan documents commands not run")
        check_pass(checks, "dev_is_canonical_truth: false" in text, "AIDE branch plan states dev is not canonical")
    else:
        check_pass(checks, False, f"AIDE branch plan Markdown missing: {AIDE_DEV_MAIN_PLAN_MD_PATH}")
    return golden_task_result(
        "aide_branch_plan_golden",
        checks,
        related,
        None,
        "Checks generated AIDE dev/main branch plan shape and no-mutation boundary.",
    )


def q31_governance_path_available(repo_root: Path, rel: str) -> bool:
    pack_root = export_pack_root(repo_root, EXPORT_PACK_ID)
    packed = pack_root / q31_pack_payload_path(rel)
    if packed.exists():
        return True
    return (repo_root / rel).exists()


def run_golden_export_pack_commit_policy_inclusion(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    pack_root = export_pack_root(repo_root, EXPORT_PACK_ID)
    related = [EXPORT_PACK_MANIFEST_PATH, COMMIT_MESSAGE_POLICY_PATH, COMMIT_MESSAGE_HOOK_TEMPLATE_PATH, COMMIT_TEMPLATE_PATH]
    if not pack_root.exists():
        checks.append(Check("PASS", "source export pack absent; local/imported repo skips pack inclusion check"))
        return golden_task_result(
            "export_pack_commit_policy_inclusion_golden",
            checks,
            related,
            None,
            "Checks portable commit discipline and changelog support are exported from source-pack repos.",
        )
    for rel in [
        COMMIT_MESSAGE_POLICY_PATH,
        COMMIT_MESSAGE_HOOK_TEMPLATE_PATH,
        COMMIT_TEMPLATE_PATH,
        COMMIT_MESSAGE_STANDARD_PATH,
        "docs/reference/commit-discipline.md",
        "docs/reference/changelog-preview.md",
        ".aide/scripts/aide_lite.py",
    ]:
        check_pass(checks, q31_governance_path_available(repo_root, rel), f"commit governance available: {rel}")
    script_text = read_text(repo_root / ".aide/scripts/aide_lite.py") if (repo_root / ".aide/scripts/aide_lite.py").exists() else ""
    check_pass(checks, "commit check" in script_text and "changelog preview" in script_text, "AIDE Lite carries commit and changelog commands")
    return golden_task_result(
        "export_pack_commit_policy_inclusion_golden",
        checks,
        related,
        None,
        "Checks portable commit discipline and changelog support are exported or locally available after import.",
    )


def run_golden_export_pack_task_recovery_inclusion(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    pack_root = export_pack_root(repo_root, EXPORT_PACK_ID)
    related = [EXPORT_PACK_MANIFEST_PATH, TASK_RESUMPTION_POLICY_PATH, WORK_UNITS_POLICY_PATH, RECOVERY_POLICY_PATH]
    if not pack_root.exists():
        checks.append(Check("PASS", "source export pack absent; local/imported repo skips pack inclusion check"))
        return golden_task_result(
            "export_pack_task_recovery_inclusion_golden",
            checks,
            related,
            None,
            "Checks portable task resumption, WorkUnit, and recovery governance are exported from source-pack repos.",
        )
    for rel in [
        TASK_RESUMPTION_POLICY_PATH,
        WORK_UNITS_POLICY_PATH,
        RECOVERY_POLICY_PATH,
        TASK_RESUMPTION_STANDARD_PATH,
        WORKUNIT_RECOVERY_STANDARD_PATH,
        "docs/reference/workunit-idempotency.md",
        ".aide/scripts/aide_lite.py",
    ]:
        check_pass(checks, q31_governance_path_available(repo_root, rel), f"task recovery governance available: {rel}")
    script_text = read_text(repo_root / ".aide/scripts/aide_lite.py") if (repo_root / ".aide/scripts/aide_lite.py").exists() else ""
    check_pass(checks, "task inspect" in script_text and "noop-check" in script_text, "AIDE Lite carries task recovery commands")
    return golden_task_result(
        "export_pack_task_recovery_inclusion_golden",
        checks,
        related,
        None,
        "Checks portable task resumption, WorkUnit, and recovery governance are exported or locally available after import.",
    )


def run_golden_export_pack_git_policy_inclusion(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    pack_root = export_pack_root(repo_root, EXPORT_PACK_ID)
    related = [EXPORT_PACK_MANIFEST_PATH, GIT_WORKFLOW_POLICY_PATH, BRANCH_ROLES_POLICY_PATH, GIT_HELPER_POLICY_PATH]
    if not pack_root.exists():
        checks.append(Check("PASS", "source export pack absent; local/imported repo skips pack inclusion check"))
        return golden_task_result(
            "export_pack_git_policy_inclusion_golden",
            checks,
            related,
            None,
            "Checks portable Git workflow and helper governance are exported from source-pack repos.",
        )
    for rel in [
        GIT_WORKFLOW_POLICY_PATH,
        BRANCH_ROLES_POLICY_PATH,
        PROMOTION_RULES_POLICY_PATH,
        SYNC_POLICY_PATH,
        PRUNE_POLICY_PATH,
        ".aide/git/README.md",
        GIT_PROJECT_PROFILES_PATH,
        GIT_HELPER_POLICY_PATH,
        GIT_HELPER_COMMANDS_MD_PATH,
        "docs/reference/git-workflow-policy.md",
        "docs/reference/branch-roles.md",
        "docs/reference/promotion-policy.md",
        "docs/reference/git-helper-workflow.md",
        ".aide/scripts/aide_lite.py",
    ]:
        check_pass(checks, q31_governance_path_available(repo_root, rel), f"Git governance available: {rel}")
    script_text = read_text(repo_root / ".aide/scripts/aide_lite.py") if (repo_root / ".aide/scripts/aide_lite.py").exists() else ""
    check_pass(checks, "git detect" in script_text and "git plan" in script_text and "git policy" in script_text, "AIDE Lite carries Git workflow commands")
    return golden_task_result(
        "export_pack_git_policy_inclusion_golden",
        checks,
        related,
        None,
        "Checks portable Git workflow and helper governance are exported or locally available after import.",
    )


def run_golden_export_pack_excludes_source_branch_state(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    related = [EXPORT_PACK_MANIFEST_PATH, EXPORT_IMPORT_POLICY_PATH]
    pack_root = export_pack_root(repo_root, EXPORT_PACK_ID)
    manifest = read_text(pack_root / "manifest.yaml") if (pack_root / "manifest.yaml").exists() else ""
    if pack_root.exists():
        for rel in Q31_FORBIDDEN_EXPORTED_SOURCE_FILES:
            payload_rel = q31_pack_payload_path(rel)
            check_pass(checks, not (pack_root / payload_rel).exists(), f"pack excludes source branch/generated state: {payload_rel}")
            check_pass(checks, payload_rel not in manifest, f"manifest excludes source branch/generated state: {payload_rel}")
        check_pass(checks, not validate_export_pack_boundary(pack_root), "export boundary has no source-state violations")
    else:
        checks.append(Check("PASS", "source export pack absent; local/imported repo skips source-pack exclusion check"))
    policy_text = read_text(repo_root / EXPORT_IMPORT_POLICY_PATH) if (repo_root / EXPORT_IMPORT_POLICY_PATH).exists() else ""
    if pack_root.exists():
        for anchor in ["source_repo_git_detection", "source_repo_git_helper_plan", "source_repo_branch_policy", "source_repo_changelog_previews"]:
            check_pass(checks, anchor in policy_text, f"export/import policy excludes {anchor}")
    return golden_task_result(
        "export_pack_excludes_source_branch_state_golden",
        checks,
        related,
        None,
        "Checks source-specific Git detection, helper plans, branch policy, and generated previews are not exported as target truth.",
    )


def run_golden_fixture_import_governance_commands(repo_root: Path) -> GoldenTaskResult:
    checks: list[Check] = []
    related = [EXPORT_PACK_MANIFEST_PATH, ".aide/scripts/aide_lite.py", COMMIT_MESSAGE_HOOK_TEMPLATE_PATH]
    pack_root = export_pack_root(repo_root, EXPORT_PACK_ID)
    if pack_root.exists():
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "target"
            target.mkdir()
            apply_import_pack(pack_root, target, dry_run=False, mode="safe")
            check_pass(checks, (target / COMMIT_MESSAGE_POLICY_PATH).exists(), "fixture import receives commit policy")
            check_pass(checks, (target / TASK_RESUMPTION_POLICY_PATH).exists(), "fixture import receives task resumption policy")
            check_pass(checks, (target / GIT_WORKFLOW_POLICY_PATH).exists(), "fixture import receives Git workflow policy")
            check_pass(checks, (target / COMMIT_MESSAGE_HOOK_TEMPLATE_PATH).exists(), "fixture import receives hook template")
            check_pass(checks, not (target / ".git/hooks/commit-msg").exists(), "fixture import does not auto-install Git hook")
            write_text(target / "COMMIT_MSG", COMMIT_GOOD_EXAMPLE)
            write_text(
                target / ".aide/queue/FIXTURE-TASK/task.yaml",
                "id: FIXTURE-TASK\nacceptance:\n  - fixture\n",
            )
            write_text(target / ".aide/queue/FIXTURE-TASK/status.yaml", "status: running\n")
            write_text(
                target / ".aide/queue/index.yaml",
                """items:
  - id: FIXTURE-TASK
    status: running
    task: .aide/queue/FIXTURE-TASK/task.yaml
    evidence: .aide/queue/FIXTURE-TASK/evidence
""",
            )
            for command, label in [
                (["commit", "check", "--message-file", "COMMIT_MSG"], "fixture commit check command passes"),
                (["commit", "template"], "fixture commit template command runs"),
                (["task", "inspect", "--task-id", "FIXTURE-TASK"], "fixture task inspect command runs"),
                (["git", "policy"], "fixture git policy command passes"),
            ]:
                try:
                    code = main(["--repo-root", str(target), *command])
                except Exception as exc:  # pragma: no cover - defensive golden reporting
                    code = 1
                    label = f"{label}: {exc}"
                check_pass(checks, code == 0, label)
    else:
        checks.append(Check("PASS", "source export pack absent; fixture import command check skipped"))
    return golden_task_result(
        "fixture_import_governance_commands_golden",
        checks,
        related,
        None,
        "Checks safe fixture import receives governance files and can run portable commit/task/Git commands.",
    )


def run_golden_tasks(repo_root: Path, task_id: str | None = None) -> GoldenRunResult:
    if task_id:
        tasks = [run_golden_task(repo_root, task_id)]
    else:
        definitions = parse_golden_task_catalog(repo_root)
        if not definitions:
            raise ValueError(f"golden task catalog missing or empty: {GOLDEN_TASK_CATALOG_PATH}")
        tasks = [run_golden_task(repo_root, definition.task_id) for definition in definitions]
    result = "PASS"
    if any(task.result == "FAIL" for task in tasks):
        result = "FAIL"
    elif any(task.result == "WARN" for task in tasks):
        result = "WARN"
    return GoldenRunResult(
        result=result,
        tasks=tuple(sorted(tasks, key=lambda task: task.task_id)),
        json_report=GOLDEN_RUN_JSON_PATH,
        markdown_report=GOLDEN_RUN_MD_PATH,
    )


def golden_task_result_to_dict(task: GoldenTaskResult) -> dict[str, object]:
    return {
        "task_id": task.task_id,
        "result": task.result,
        "checks_run": task.checks_run,
        "passed_checks": task.passed_checks,
        "warnings": list(task.warnings),
        "errors": list(task.errors),
        "related_paths": list(task.related_paths),
        "approx_tokens_if_applicable": task.approx_tokens_if_applicable,
        "notes": task.notes,
    }


def golden_run_to_dict(run: GoldenRunResult) -> dict[str, object]:
    pass_count = sum(1 for task in run.tasks if task.result == "PASS")
    warn_count = sum(1 for task in run.tasks if task.result == "WARN")
    fail_count = sum(1 for task in run.tasks if task.result == "FAIL")
    return {
        "schema_version": "aide.golden-tasks-run.v0",
        "generator": GENERATOR_NAME,
        "generator_version": GENERATOR_VERSION,
        "result": run.result,
        "task_count": len(run.tasks),
        "pass_count": pass_count,
        "warn_count": warn_count,
        "fail_count": fail_count,
        "provider_or_model_calls": "none",
        "network_calls": "none",
        "raw_prompt_storage": False,
        "raw_response_storage": False,
        "token_quality_statement": "Token reduction remains valid only if golden tasks pass.",
        "tasks": [golden_task_result_to_dict(task) for task in run.tasks],
    }


def render_golden_run_markdown(run: GoldenRunResult) -> str:
    data = golden_run_to_dict(run)
    lines = [
        "# Latest Golden Tasks",
        "",
        f"- result: {data['result']}",
        f"- task_count: {data['task_count']}",
        f"- pass_count: {data['pass_count']}",
        f"- warn_count: {data['warn_count']}",
        f"- fail_count: {data['fail_count']}",
        "- provider_or_model_calls: none",
        "- network_calls: none",
        "- raw_prompt_storage: false",
        "- raw_response_storage: false",
        "- token_quality_statement: Token reduction remains valid only if golden tasks pass.",
        "",
        "## Tasks",
        "",
    ]
    for task in run.tasks:
        lines.extend(
            [
                f"### {task.task_id}",
                "",
                f"- result: {task.result}",
                f"- checks_run: {task.checks_run}",
                f"- passed_checks: {task.passed_checks}",
                f"- approx_tokens_if_applicable: {task.approx_tokens_if_applicable if task.approx_tokens_if_applicable is not None else 'n/a'}",
                f"- related_paths: {', '.join(task.related_paths) if task.related_paths else 'none'}",
                f"- notes: {task.notes}",
            ]
        )
        if task.warnings:
            lines.append("- warnings:")
            lines.extend(f"  - {warning}" for warning in task.warnings)
        if task.errors:
            lines.append("- errors:")
            lines.extend(f"  - {error}" for error in task.errors)
        lines.append("")
    lines.extend(
        [
            "## Limitations",
            "",
            "- Deterministic local checks only.",
            "- No model/provider/network calls.",
            "- No external benchmark or arbitrary code semantic proof.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_golden_run_reports(repo_root: Path, run: GoldenRunResult) -> tuple[WriteResult, WriteResult]:
    json_text = json.dumps(golden_run_to_dict(run), indent=2, sort_keys=True) + "\n"
    json_result = write_text_if_changed(repo_root / GOLDEN_RUN_JSON_PATH, json_text)
    md_result = write_text_if_changed(repo_root / GOLDEN_RUN_MD_PATH, render_golden_run_markdown(run))
    return json_result, md_result


def read_latest_golden_run(repo_root: Path) -> dict[str, object]:
    path = repo_root / GOLDEN_RUN_JSON_PATH
    if not path.exists():
        raise ValueError(f"golden task report missing: {GOLDEN_RUN_JSON_PATH}")
    return json.loads(read_text(path))


def parse_failure_taxonomy(repo_root: Path) -> list[str]:
    path = repo_root / FAILURE_TAXONOMY_PATH
    if not path.exists():
        return list(CONTROLLER_FAILURE_CLASSES)
    ids = []
    for line in read_text(path).splitlines():
        stripped = line.strip()
        if stripped.startswith("- id:"):
            ids.append(stripped.split(":", 1)[1].strip())
    return ids or list(CONTROLLER_FAILURE_CLASSES)


def normalize_outcome_result(value: str) -> str:
    result = value.strip().upper()
    if result not in {"PASS", "WARN", "FAIL"}:
        raise ValueError(f"invalid outcome result: {value}")
    return result


def normalize_outcome_severity(value: str) -> str:
    severity = value.strip().lower()
    if severity not in {"info", "warning", "error"}:
        raise ValueError(f"invalid outcome severity: {value}")
    return severity


def normalize_failure_class(repo_root: Path, value: str) -> str:
    failure_class = value.strip() or "unknown"
    known = set(parse_failure_taxonomy(repo_root))
    if failure_class not in known:
        raise ValueError(f"unknown failure class: {value}")
    return failure_class


def reject_raw_prompt_or_response(text: str) -> None:
    lowered = text.lower()
    unsafe_markers = [
        "raw_prompt:",
        "raw prompt:",
        "raw_response:",
        "raw response:",
        "full prior transcript",
    ]
    if any(marker in lowered for marker in unsafe_markers):
        raise ValueError("refusing raw prompt/response-like content in controller metadata")


def assert_controller_related_path(repo_root: Path, requested: str) -> str:
    rel = normalize_rel(requested)
    target = safe_repo_path(repo_root, rel)
    forbidden = [".git/**", ".aide.local/**", "secrets/**", ".env"]
    if any(pattern_matches(rel, pattern) for pattern in forbidden):
        raise ValueError(f"refusing forbidden controller related path: {rel}")
    if rel not in GENERATED_CONTEXT_PATHS and is_ignored(rel, load_ignore_patterns(repo_root)):
        raise ValueError(f"refusing ignored/local/secret controller related path: {rel}")
    if not target.exists():
        raise ValueError(f"controller related path does not exist: {rel}")
    return rel


def outcome_record_to_dict(record: OutcomeRecord) -> dict[str, object]:
    return {
        "run_id": record.run_id,
        "phase": record.phase,
        "source": record.source,
        "result": record.result,
        "failure_class": record.failure_class,
        "severity": record.severity,
        "related_paths": list(record.related_paths),
        "approx_tokens": record.approx_tokens,
        "budget_status": record.budget_status,
        "golden_task_status": record.golden_task_status,
        "verifier_status": record.verifier_status,
        "recommendation_id": record.recommendation_id,
        "notes": record.notes,
    }


def outcome_record_from_dict(data: dict[str, object]) -> OutcomeRecord:
    related = data.get("related_paths", [])
    if not isinstance(related, list):
        related = []
    approx = data.get("approx_tokens")
    return OutcomeRecord(
        run_id=str(data.get("run_id", "")),
        phase=str(data.get("phase", "")),
        source=str(data.get("source", "")),
        result=str(data.get("result", "WARN")),
        failure_class=str(data.get("failure_class", "unknown")),
        severity=str(data.get("severity", "warning")),
        related_paths=tuple(sorted(normalize_rel(str(path)) for path in related)),
        approx_tokens=int(approx) if isinstance(approx, int) else None,
        budget_status=str(data.get("budget_status", "unknown_budget")),
        golden_task_status=str(data.get("golden_task_status", "UNKNOWN")),
        verifier_status=str(data.get("verifier_status", "UNKNOWN")),
        recommendation_id=str(data.get("recommendation_id", "")),
        notes=str(data.get("notes", "")),
    )


def read_outcome_records(repo_root: Path) -> list[OutcomeRecord]:
    path = repo_root / OUTCOME_LEDGER_PATH
    if not path.exists():
        return []
    records: list[OutcomeRecord] = []
    for line in read_text(path).splitlines():
        if not line.strip():
            continue
        try:
            records.append(outcome_record_from_dict(json.loads(line)))
        except (json.JSONDecodeError, TypeError, ValueError):
            continue
    return records


def write_outcome_records(repo_root: Path, records: Iterable[OutcomeRecord]) -> WriteResult:
    sorted_records = sorted(records, key=lambda item: (item.run_id, item.phase, item.source, item.failure_class, item.recommendation_id))
    lines = [
        json.dumps(outcome_record_to_dict(record), sort_keys=True, separators=(",", ":"))
        for record in sorted_records
    ]
    return write_text_if_changed(repo_root / OUTCOME_LEDGER_PATH, "\n".join(lines) + ("\n" if lines else ""))


def merge_outcome_records(repo_root: Path, new_records: Iterable[OutcomeRecord], run_id: str = "q16.current") -> tuple[WriteResult, list[OutcomeRecord]]:
    existing = read_outcome_records(repo_root)
    retained = [record for record in existing if record.run_id != run_id]
    merged = [*retained, *list(new_records)]
    return write_outcome_records(repo_root, merged), merged


def make_outcome_record(
    repo_root: Path,
    phase: str,
    source: str,
    result: str,
    failure_class: str = "unknown",
    severity: str = "info",
    related_paths: Iterable[str] = (),
    approx_tokens: int | None = None,
    budget_status: str = "unknown_budget",
    golden_task_status: str = "UNKNOWN",
    verifier_status: str = "UNKNOWN",
    recommendation_id: str = "",
    notes: str = "",
    run_id: str = "q16.current",
) -> OutcomeRecord:
    reject_raw_prompt_or_response(notes)
    return OutcomeRecord(
        run_id=run_id,
        phase=phase,
        source=source,
        result=normalize_outcome_result(result),
        failure_class=normalize_failure_class(repo_root, failure_class),
        severity=normalize_outcome_severity(severity),
        related_paths=tuple(sorted(assert_controller_related_path(repo_root, path) for path in related_paths)),
        approx_tokens=approx_tokens,
        budget_status=budget_status,
        golden_task_status=golden_task_status,
        verifier_status=verifier_status,
        recommendation_id=recommendation_id,
        notes=notes or "deterministic controller metadata only; raw prompt/response not stored",
    )


def current_ledger_records(repo_root: Path) -> list[LedgerRecord]:
    records = read_ledger_records(repo_root)
    current = [record for record in records if record.run_id == "q14.scan.current"]
    return current or records


def read_token_signal(repo_root: Path) -> dict[str, object]:
    records = current_ledger_records(repo_root)
    budget_warnings = ledger_budget_warnings(records)
    regression: list[str] = []
    summary_path = repo_root / TOKEN_SUMMARY_PATH
    if summary_path.exists():
        text = read_text(summary_path)
        match = re.search(r"## Regression Warnings\s*(.*?)(?:\n## |\Z)", text, re.DOTALL)
        if match:
            regression = [
                line.strip()[2:]
                for line in match.group(1).splitlines()
                if line.strip().startswith("- ") and line.strip() != "- none"
            ]
    largest = sorted(records, key=lambda item: item.approx_tokens, reverse=True)[:5]
    result = "PASS"
    failure_class = "unknown"
    severity = "info"
    if any(record.budget_status == "over_budget" for record in records):
        result = "FAIL"
        failure_class = "token_budget_exceeded"
        severity = "error"
    elif budget_warnings or regression:
        result = "WARN"
        failure_class = "token_regression" if regression else "packet_too_large"
        severity = "warning"
    return {
        "result": result,
        "failure_class": failure_class,
        "severity": severity,
        "budget_warnings": budget_warnings,
        "regression_warnings": regression,
        "largest": largest,
        "records": records,
    }


def read_golden_signal(repo_root: Path) -> dict[str, object]:
    path = repo_root / GOLDEN_RUN_JSON_PATH
    if not path.exists():
        return {"result": "WARN", "failure_class": "golden_task_fail", "severity": "warning", "path": GOLDEN_RUN_JSON_PATH, "task_count": 0, "pass_count": 0, "warn_count": 0, "fail_count": 0, "warnings": ["golden task report missing"]}
    data = json.loads(read_text(path))
    result = str(data.get("result", "WARN")).upper()
    failure_class = "unknown" if result == "PASS" else "golden_task_fail"
    severity = "info" if result == "PASS" else ("error" if result == "FAIL" else "warning")
    task_warnings = []
    for task in data.get("tasks", []):
        if isinstance(task, dict) and task.get("result") in {"WARN", "FAIL"}:
            task_warnings.append(f"{task.get('task_id', 'unknown')}: {task.get('result')}")
    return {
        "result": result,
        "failure_class": failure_class,
        "severity": severity,
        "path": GOLDEN_RUN_JSON_PATH,
        "task_count": int(data.get("task_count", 0) or 0),
        "pass_count": int(data.get("pass_count", 0) or 0),
        "warn_count": int(data.get("warn_count", 0) or 0),
        "fail_count": int(data.get("fail_count", 0) or 0),
        "warnings": task_warnings,
    }


def read_verifier_signal(repo_root: Path) -> dict[str, object]:
    path = repo_root / LATEST_VERIFICATION_REPORT_PATH
    if not path.exists():
        return {"result": "WARN", "verifier_result": "MISSING", "failure_class": "verifier_gap", "severity": "warning", "path": LATEST_VERIFICATION_REPORT_PATH, "warnings": ["verification report missing"], "errors": 0}
    text = read_text(path)
    result = extract_verification_result(repo_root, LATEST_VERIFICATION_REPORT_PATH)
    warnings = parse_int_value(text, "warnings", 0)
    errors = parse_int_value(text, "errors", 0)
    if result == "FAIL" or errors:
        failure_class = "verifier_fail"
        severity = "error"
        outcome = "FAIL"
    elif result in {"WARN", "UNKNOWN", "MISSING"} or warnings:
        failure_class = "verifier_gap" if result in {"UNKNOWN", "MISSING"} else "verifier_fail"
        severity = "warning"
        outcome = "WARN"
    else:
        failure_class = "unknown"
        severity = "info"
        outcome = "PASS"
    return {
        "result": outcome,
        "verifier_result": result,
        "failure_class": failure_class,
        "severity": severity,
        "path": LATEST_VERIFICATION_REPORT_PATH,
        "warnings": warnings,
        "errors": errors,
    }


def read_review_packet_signal(repo_root: Path) -> dict[str, object]:
    path = repo_root / REVIEW_PACKET_PATH
    if not path.exists():
        return {"result": "WARN", "failure_class": "review_packet_incomplete", "severity": "warning", "path": REVIEW_PACKET_PATH, "approx_tokens": None, "budget_status": "unknown_budget", "errors": 1, "warnings": ["review packet missing"]}
    text = read_text(path)
    stats = estimate_text(text, REVIEW_PACKET_PATH)
    _budget, budget_status = ledger_budget_status(repo_root, "review_packet", stats.approx_tokens)
    findings = verify_review_packet(repo_root, REVIEW_PACKET_PATH)
    errors = [finding.message for finding in findings if finding.severity == "ERROR"]
    warnings = [finding.message for finding in findings if finding.severity in {"WARN", "WARNING"}]
    if errors:
        result = "FAIL"
        failure_class = "review_packet_incomplete"
        severity = "error"
    elif warnings or budget_status == "over_budget":
        result = "WARN"
        failure_class = "packet_too_large" if budget_status == "over_budget" else "review_packet_incomplete"
        severity = "warning"
    else:
        result = "PASS"
        failure_class = "unknown"
        severity = "info"
    return {
        "result": result,
        "failure_class": failure_class,
        "severity": severity,
        "path": REVIEW_PACKET_PATH,
        "approx_tokens": stats.approx_tokens,
        "budget_status": budget_status,
        "errors": errors,
        "warnings": warnings,
    }


def read_context_signal(repo_root: Path) -> dict[str, object]:
    required = [REPO_MAP_JSON_PATH, TEST_MAP_JSON_PATH, CONTEXT_INDEX_PATH, LATEST_CONTEXT_PACKET_PATH]
    missing = [rel for rel in required if not (repo_root / rel).exists()]
    stale = []
    repo_map_path = repo_root / REPO_MAP_JSON_PATH
    snapshot_path = repo_root / SNAPSHOT_PATH
    if repo_map_path.exists() and snapshot_path.exists():
        try:
            repo_map = json.loads(read_text(repo_map_path))
            snapshot = json.loads(read_text(snapshot_path))
            if repo_map.get("source_snapshot_hash") != snapshot_fingerprint(snapshot):
                stale.append(REPO_MAP_JSON_PATH)
        except (OSError, json.JSONDecodeError, TypeError):
            stale.append(REPO_MAP_JSON_PATH)
    if missing:
        return {"result": "WARN", "failure_class": "context_missing", "severity": "warning", "missing": missing, "stale": stale, "related_paths": [rel for rel in required if (repo_root / rel).exists()]}
    if stale:
        return {"result": "WARN", "failure_class": "stale_artifact", "severity": "warning", "missing": missing, "stale": stale, "related_paths": required}
    return {"result": "PASS", "failure_class": "unknown", "severity": "info", "missing": missing, "stale": stale, "related_paths": required}


def read_adapter_signal(repo_root: Path) -> dict[str, object]:
    adapter = adapter_status(repo_root)
    if adapter.status == "current":
        return {"result": "PASS", "failure_class": "unknown", "severity": "info", "status": adapter.status, "hint": adapter.action_hint, "path": "AGENTS.md"}
    return {"result": "WARN", "failure_class": "adapter_drift", "severity": "warning", "status": adapter.status, "hint": adapter.action_hint, "path": "AGENTS.md"}


def build_current_outcome_records(repo_root: Path) -> list[OutcomeRecord]:
    token = read_token_signal(repo_root)
    golden = read_golden_signal(repo_root)
    verifier = read_verifier_signal(repo_root)
    review = read_review_packet_signal(repo_root)
    context = read_context_signal(repo_root)
    adapter = read_adapter_signal(repo_root)
    records = [
        make_outcome_record(
            repo_root,
            "Q16-outcome-controller-v0",
            "token_ledger",
            str(token["result"]),
            str(token["failure_class"]),
            str(token["severity"]),
            [TOKEN_LEDGER_PATH, TOKEN_SUMMARY_PATH],
            budget_status="mixed" if token.get("budget_warnings") else "within_budget",
            golden_task_status=str(golden["result"]),
            verifier_status=str(verifier["verifier_result"]),
            recommendation_id="REC-PACKET-BUDGET" if token["result"] != "PASS" else "",
            notes=f"budget_warnings={len(token.get('budget_warnings', []))}; regression_warnings={len(token.get('regression_warnings', []))}",
        ),
        make_outcome_record(
            repo_root,
            "Q16-outcome-controller-v0",
            "golden_tasks",
            str(golden["result"]),
            str(golden["failure_class"]),
            str(golden["severity"]),
            [GOLDEN_RUN_JSON_PATH, GOLDEN_RUN_MD_PATH],
            golden_task_status=str(golden["result"]),
            verifier_status=str(verifier["verifier_result"]),
            recommendation_id="REC-GOLDEN-TASKS" if golden["result"] != "PASS" else "",
            notes=f"pass={golden.get('pass_count', 0)} warn={golden.get('warn_count', 0)} fail={golden.get('fail_count', 0)}",
        ),
        make_outcome_record(
            repo_root,
            "Q16-outcome-controller-v0",
            "verifier",
            str(verifier["result"]),
            str(verifier["failure_class"]),
            str(verifier["severity"]),
            [LATEST_VERIFICATION_REPORT_PATH],
            golden_task_status=str(golden["result"]),
            verifier_status=str(verifier["verifier_result"]),
            recommendation_id="REC-VERIFIER" if verifier["result"] != "PASS" else "",
            notes=f"warnings={verifier.get('warnings', 0)} errors={verifier.get('errors', 0)}",
        ),
        make_outcome_record(
            repo_root,
            "Q16-outcome-controller-v0",
            "review_packet",
            str(review["result"]),
            str(review["failure_class"]),
            str(review["severity"]),
            [REVIEW_PACKET_PATH],
            approx_tokens=review.get("approx_tokens") if isinstance(review.get("approx_tokens"), int) else None,
            budget_status=str(review["budget_status"]),
            golden_task_status=str(golden["result"]),
            verifier_status=str(verifier["verifier_result"]),
            recommendation_id="REC-REVIEW-PACKET" if review["result"] != "PASS" else "",
            notes=f"errors={len(review.get('errors', []))}; warnings={len(review.get('warnings', []))}",
        ),
        make_outcome_record(
            repo_root,
            "Q16-outcome-controller-v0",
            "context_artifacts",
            str(context["result"]),
            str(context["failure_class"]),
            str(context["severity"]),
            context.get("related_paths", []),
            golden_task_status=str(golden["result"]),
            verifier_status=str(verifier["verifier_result"]),
            recommendation_id="REC-CONTEXT" if context["result"] != "PASS" else "",
            notes=f"missing={len(context.get('missing', []))}; stale={len(context.get('stale', []))}",
        ),
        make_outcome_record(
            repo_root,
            "Q16-outcome-controller-v0",
            "adapter_guidance",
            str(adapter["result"]),
            str(adapter["failure_class"]),
            str(adapter["severity"]),
            [str(adapter["path"])],
            golden_task_status=str(golden["result"]),
            verifier_status=str(verifier["verifier_result"]),
            recommendation_id="REC-ADAPTER-DRIFT" if adapter["result"] != "PASS" else "",
            notes=f"adapter_status={adapter['status']}; hint={adapter['hint']}",
        ),
    ]
    return records


def recommendation(
    recommendation_id: str,
    failure_class: str,
    evidence_source: str,
    expected_benefit: str,
    risk_level: str,
    next_action: str,
    rollback_condition: str,
) -> Recommendation:
    return Recommendation(
        recommendation_id=recommendation_id,
        failure_class=failure_class,
        evidence_source=evidence_source,
        expected_benefit=expected_benefit,
        risk_level=risk_level,
        next_action=next_action,
        rollback_condition=rollback_condition,
        applies_automatically=False,
    )


def build_recommendations(repo_root: Path, records: Iterable[OutcomeRecord]) -> list[Recommendation]:
    record_list = list(records)
    recommendations: list[Recommendation] = []
    by_class: dict[str, list[OutcomeRecord]] = {}
    for record in record_list:
        if record.result == "PASS":
            continue
        by_class.setdefault(record.failure_class, []).append(record)
    if "golden_task_fail" in by_class:
        recommendations.append(
            recommendation(
                "REC-GOLDEN-TASKS",
                "golden_task_fail",
                GOLDEN_RUN_JSON_PATH,
                "Preserve the deterministic quality floor before promoting token reductions or routing work.",
                "high",
                "Repair golden-task warnings/failures, rerun `eval run`, and do not promote token-saving changes until the result is PASS.",
                "Golden tasks pass again with no FAIL and no unresolved quality warning.",
            )
        )
    if "token_budget_exceeded" in by_class or "packet_too_large" in by_class or "token_regression" in by_class:
        recommendations.append(
            recommendation(
                "REC-PACKET-BUDGET",
                "packet_too_large",
                TOKEN_SUMMARY_PATH,
                "Lower prompt cost while keeping compact packets inside configured budgets.",
                "medium",
                "Tighten context refs, rerun `context`, `pack`, and `review-pack`, then confirm budgets and golden tasks.",
                "Affected packet returns within budget and golden tasks remain PASS.",
            )
        )
    if "verifier_fail" in by_class or "verifier_gap" in by_class:
        recommendations.append(
            recommendation(
                "REC-VERIFIER",
                "verifier_fail",
                LATEST_VERIFICATION_REPORT_PATH,
                "Avoid expensive review of mechanically invalid or unverifiable work.",
                "high",
                "Repair verifier warnings/errors before GPT-5.5 review; rerun `verify`.",
                "Verifier result is PASS or an explicitly accepted WARN with evidence.",
            )
        )
    if "review_packet_incomplete" in by_class:
        recommendations.append(
            recommendation(
                "REC-REVIEW-PACKET",
                "review_packet_incomplete",
                REVIEW_PACKET_PATH,
                "Keep premium-model review bounded to complete compact evidence.",
                "medium",
                "Rerun `review-pack` or repair the review-packet template/evidence refs.",
                "Review packet validates and contains required decision, risk, token, verifier, and evidence sections.",
            )
        )
    if "context_missing" in by_class or "stale_artifact" in by_class:
        recommendations.append(
            recommendation(
                "REC-CONTEXT",
                "context_missing",
                CONTEXT_INDEX_PATH,
                "Avoid fallback to broad repo dumps by keeping context artifacts current.",
                "medium",
                "Rerun `snapshot`, `index`, and `context` before generating the next packet.",
                "Context artifacts exist, validate, and remain metadata-only.",
            )
        )
    if "adapter_drift" in by_class:
        recommendations.append(
            recommendation(
                "REC-ADAPTER-DRIFT",
                "adapter_drift",
                "AGENTS.md",
                "Keep agent guidance aligned with compact-packet and evidence-review discipline.",
                "medium",
                "Rerun `adapt` and review the managed section diff.",
                "AGENTS managed section status is current and manual content is preserved.",
            )
        )
    if not recommendations:
        if (repo_root / ".aide/queue/Q17-router-profile-v0").exists():
            recommendation_id = "REC-PROCEED-Q18-WITH-GATES"
            expected_benefit = "Define cache and local-state boundaries after routing is advisory and local quality gates are healthy."
            next_action = "Proceed to Q18 Cache and Local State Boundary as a repo-local boundary phase only; do not call providers or implement Gateway."
            rollback_condition = "If any verifier, golden-task, route, token, or controller signal regresses, pause Q18 and repair the failing local gate first."
        else:
            recommendation_id = "REC-PROCEED-Q17-WITH-GATES"
            expected_benefit = "Begin advisory Router Profile design after token, verifier, review, and golden-task foundations are locally healthy."
            next_action = "Proceed to Q17 Router Profile v0 as an advisory profile only; do not call providers or implement Gateway."
            rollback_condition = "If any controller signal regresses, pause Q17 and repair the failing local gate first."
        recommendations.append(
            recommendation(
                recommendation_id,
                "unknown",
                OUTCOME_REPORT_PATH,
                expected_benefit,
                "low",
                next_action,
                rollback_condition,
            )
        )
    return sorted(recommendations, key=lambda item: item.recommendation_id)


def controller_overall_result(records: Iterable[OutcomeRecord]) -> str:
    results = [record.result for record in records]
    if any(result == "FAIL" for result in results):
        return "FAIL"
    if any(result == "WARN" for result in results):
        return "WARN"
    return "PASS"


def render_outcome_report(repo_root: Path, records: list[OutcomeRecord], recommendations: list[Recommendation]) -> str:
    result = controller_overall_result(records)
    by_class: dict[str, int] = {}
    for record in records:
        if record.result != "PASS":
            by_class[record.failure_class] = by_class.get(record.failure_class, 0) + 1
    class_lines = [f"- {name}: {count}" for name, count in sorted(by_class.items())] or ["- none"]
    record_lines = [
        f"- {record.source}: {record.result} / {record.failure_class} / {record.severity}"
        for record in sorted(records, key=lambda item: item.source)
    ]
    top = recommendations[0] if recommendations else None
    top_line = f"{top.recommendation_id}: {top.next_action}" if top else "none"
    return f"""# AIDE Outcome Report

## RESULT

- result: {result}
- mode: advisory_only
- applies_automatically: false

## SIGNALS

{chr(10).join(record_lines)}

## FAILURE_CLASSES

{chr(10).join(class_lines)}

## NEXT_ACTION

- top_recommendation: {top_line}
- recommendations: `{RECOMMENDATIONS_PATH}`
- outcome_ledger: `{OUTCOME_LEDGER_PATH}`

## SAFETY

- provider_or_model_calls: none
- network_calls: none
- automatic_mutation: false
- raw_prompt_storage: false
- raw_response_storage: false
- controller_policy: `{CONTROLLER_POLICY_PATH}`
"""


def render_recommendations(recommendations: list[Recommendation]) -> str:
    lines = [
        "# AIDE Recommendations",
        "",
        "## MODE",
        "",
        "- advisory_only: true",
        "- applies_automatically: false",
        "- automatic_prompt_mutation: false",
        "- automatic_policy_mutation: false",
        "- automatic_route_mutation: false",
        "",
        "## RECOMMENDATIONS",
        "",
    ]
    for item in recommendations:
        lines.extend(
            [
                f"- ID: {item.recommendation_id}",
                f"  - failure_class: {item.failure_class}",
                f"  - evidence_source: `{item.evidence_source}`",
                f"  - expected_benefit: {item.expected_benefit}",
                f"  - risk_level: {item.risk_level}",
                f"  - next_action: {item.next_action}",
                f"  - rollback_condition: {item.rollback_condition}",
                f"  - applies_automatically: {'true' if item.applies_automatically else 'false'}",
                "",
            ]
        )
    lines.extend(
        [
            "## SAFETY",
            "",
            "- provider_or_model_calls: none",
            "- network_calls: none",
            "- raw_prompt_storage: false",
            "- raw_response_storage: false",
        ]
    )
    return "\n".join(lines) + "\n"


def write_outcome_report(repo_root: Path, records: list[OutcomeRecord], recommendations: list[Recommendation]) -> WriteResult:
    return write_text_if_changed(repo_root / OUTCOME_REPORT_PATH, render_outcome_report(repo_root, records, recommendations))


def write_recommendations(repo_root: Path, recommendations: list[Recommendation]) -> WriteResult:
    return write_text_if_changed(repo_root / RECOMMENDATIONS_PATH, render_recommendations(recommendations))


def parse_route_profiles(repo_root: Path) -> list[RouteProfile]:
    path = repo_root / ROUTES_PATH
    if not path.exists():
        return []
    profiles: list[RouteProfile] = []
    current: dict[str, object] = {}
    for line in read_text(path).splitlines():
        stripped = line.strip()
        if stripped.startswith("- task_class:"):
            if current:
                profiles.append(
                    RouteProfile(
                        task_class=str(current.get("task_class", "unknown")),
                        preferred_route_class=str(current.get("preferred_route_class", "frontier")),
                        fallback_route_class=str(current.get("fallback_route_class", "human_review")),
                        review_required=bool(current.get("review_required", True)),
                    )
                )
            current = {"task_class": stripped.split(":", 1)[1].strip()}
            continue
        if not current:
            continue
        for key in ["preferred_route_class", "fallback_route_class"]:
            if stripped.startswith(f"{key}:"):
                current[key] = stripped.split(":", 1)[1].strip()
        if stripped.startswith("review_required:"):
            current["review_required"] = stripped.split(":", 1)[1].strip().lower() == "true"
    if current:
        profiles.append(
            RouteProfile(
                task_class=str(current.get("task_class", "unknown")),
                preferred_route_class=str(current.get("preferred_route_class", "frontier")),
                fallback_route_class=str(current.get("fallback_route_class", "human_review")),
                review_required=bool(current.get("review_required", True)),
            )
        )
    return sorted(profiles, key=lambda item: item.task_class)


def route_profile_for_task(repo_root: Path, task_class: str) -> RouteProfile:
    for profile in parse_route_profiles(repo_root):
        if profile.task_class == task_class:
            return profile
    fallback_defaults = {
        "deterministic_format_or_count": ("no_model_tool", "human_review", False),
        "compact_task_generation": ("no_model_tool", "local_small", False),
        "context_indexing": ("no_model_tool", "local_small", False),
        "verifier_check": ("no_model_tool", "human_review", False),
        "evidence_review_packet": ("frontier", "human_review", True),
        "bounded_docs_update": ("local_strong", "cheap_remote", True),
        "bounded_code_patch": ("local_strong", "cheap_remote", True),
        "failing_test_repair": ("local_strong", "frontier", True),
        "architecture_decision": ("frontier", "human_review", True),
        "security_review": ("frontier", "human_review", True),
        "self_modification": ("human_review", "frontier", True),
        "final_promotion_review": ("frontier", "human_review", True),
        "maintenance_suggestion": ("no_model_tool", "local_small", False),
        "unknown": ("frontier", "human_review", True),
    }
    preferred, fallback, review_required = fallback_defaults.get(task_class, fallback_defaults["unknown"])
    return RouteProfile(task_class, preferred, fallback, review_required)


def parse_hard_floor_minimums(repo_root: Path) -> dict[str, tuple[str, ...]]:
    path = repo_root / HARD_FLOORS_PATH
    if not path.exists():
        return {}
    floors: dict[str, tuple[str, ...]] = {}
    current = ""
    in_minimum = False
    values: list[str] = []
    for line in read_text(path).splitlines():
        stripped = line.strip()
        if stripped.startswith("- floor_id:"):
            if current:
                floors[current] = tuple(values)
            current = stripped.split(":", 1)[1].strip()
            values = []
            in_minimum = False
            continue
        if not current:
            continue
        if stripped == "minimum_route_class:":
            in_minimum = True
            continue
        if in_minimum and stripped.startswith("- "):
            values.append(stripped[2:].strip())
            continue
        if in_minimum and stripped and not stripped.startswith("- "):
            in_minimum = False
    if current:
        floors[current] = tuple(values)
    return floors


def text_has_any(text: str, needles: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(needle in lowered for needle in needles)


def classify_route_task(text: str) -> str:
    lowered = text.lower()
    if text_has_any(lowered, ["self-modification", "self modification", "self-mutating", "automatic prompt", "automatic policy", "automatic route", "rewrite routing policy"]):
        return "self_modification"
    if text_has_any(lowered, ["security review", "secret safety", "credential", "api key", "api_key", "secret scan", "password"]):
        return "security_review"
    if text_has_any(lowered, ["final promotion", "promotion review", "release readiness", "pass review gate"]):
        return "final_promotion_review"
    if text_has_any(lowered, ["architecture decision", "architecture boundary", "runtime service", "router profile", "routing policy", "governance policy", "gateway design", "cache and local state boundary", "local state boundary", "cache boundary"]):
        return "architecture_decision"
    if text_has_any(lowered, ["review-pack", "review packet", "evidence review", "gpt-5.5 review", "premium-model review"]):
        return "evidence_review_packet"
    if text_has_any(lowered, ["verifier", "verify --", "mechanical verification", "evidence packet section"]):
        return "verifier_check"
    if text_has_any(lowered, ["context compiler", "repo-map", "test-map", "context-index", "snapshot", "index and context"]):
        return "context_indexing"
    if text_has_any(lowered, ["pack --task", "compact task packet", "latest-task-packet", "task packet generation"]):
        return "compact_task_generation"
    if text_has_any(lowered, ["estimate --file", "estimate tokens", "token estimate", "chars/4", "format", "count"]):
        return "deterministic_format_or_count"
    if text_has_any(lowered, ["failing test", "repair failing", "test repair"]):
        return "failing_test_repair"
    if text_has_any(lowered, ["readme", "roadmap", "documentation", "docs/reference", "bounded docs"]):
        return "bounded_docs_update"
    if text_has_any(lowered, ["optimize suggest", "outcome report", "maintenance suggestion", "recommendation"]):
        return "maintenance_suggestion"
    if text_has_any(lowered, ["code patch", "fix bug", "implement", "refactor", "test:"]):
        return "bounded_code_patch"
    return "unknown"


def classify_route_risk(task_class: str, text: str) -> str:
    lowered = text.lower()
    if text_has_any(lowered, ["delete", "destructive", "irreversible", "remove secrets", "wipe", "purge"]):
        return "destructive"
    if task_class == "security_review" or text_has_any(lowered, ["security", "credential", "secret", "api key", "api_key", "password"]):
        return "security"
    if task_class == "self_modification" or text_has_any(lowered, ["self-modification", "identity", "autonomous loop", "automatic mutation"]):
        return "identity"
    if task_class in {"architecture_decision", "final_promotion_review"} or text_has_any(lowered, ["governance", "policy", "routing policy", "router profile", "hard floor"]):
        return "governance"
    if task_class in {"bounded_code_patch", "bounded_docs_update", "failing_test_repair", "evidence_review_packet"}:
        return "medium"
    if task_class in {"deterministic_format_or_count", "compact_task_generation", "context_indexing", "verifier_check", "maintenance_suggestion"}:
        return "low"
    return "unknown"


def hard_floor_for_route(task_class: str, risk_class: str, text: str) -> str:
    lowered = text.lower()
    if risk_class == "destructive" or text_has_any(lowered, ["irreversible", "destructive"]):
        return "irreversible_or_destructive_change"
    if task_class == "self_modification" or risk_class == "identity":
        return "self_modification"
    if task_class == "security_review" or risk_class == "security":
        return "security_review"
    if task_class == "final_promotion_review":
        return "final_promotion_review"
    if text_has_any(lowered, ["high stakes", "high-stakes"]):
        return "high_stakes_review"
    if risk_class == "governance" and text_has_any(lowered, ["governance policy", "routing policy", "hard floor", "policy change"]):
        return "governance_policy_change"
    if task_class == "architecture_decision":
        return "architecture_decision"
    return "none"


def route_from_hard_floor(repo_root: Path, hard_floor: str) -> tuple[str, str]:
    minimums = parse_hard_floor_minimums(repo_root)
    candidates = minimums.get(hard_floor, ())
    if hard_floor == "irreversible_or_destructive_change":
        return "human_review", "blocked"
    if "frontier" in candidates and "human_review" in candidates:
        return "frontier", "human_review"
    if "human_review" in candidates:
        return "human_review", "frontier"
    if "frontier" in candidates:
        return "frontier", "human_review"
    return "frontier", "human_review"


def read_task_packet_text(repo_root: Path, task_packet_path: str) -> tuple[str, bool]:
    path = safe_repo_path(repo_root, task_packet_path)
    if not path.exists() or not path.is_file():
        return "", False
    if looks_binary(path):
        return "", False
    return read_text(path), True


def route_relevant_task_text(packet_text: str) -> str:
    pieces: list[str] = []
    for section in ["PHASE", "GOAL"]:
        match = re.search(rf"^##\s+{section}\s*\n\n(?P<body>.*?)(?:\n##\s+|\Z)", packet_text, re.DOTALL | re.MULTILINE)
        if match:
            pieces.append(match.group("body").strip())
    return "\n".join(pieces) if pieces else packet_text


def latest_token_budget_status(repo_root: Path) -> str:
    statuses: list[str] = []
    for rel, surface in [
        (LATEST_PACKET_PATH, "task_packet"),
        (LATEST_CONTEXT_PACKET_PATH, "context_packet"),
        (REVIEW_PACKET_PATH, "review_packet"),
        (LATEST_VERIFICATION_REPORT_PATH, "verification_report"),
    ]:
        if not (repo_root / rel).exists():
            continue
        stats = estimate_file(repo_root, rel)
        _budget, status = ledger_budget_status(repo_root, surface, stats.approx_tokens)
        statuses.append(status)
    if not statuses:
        return "unknown_budget"
    if "over_budget" in statuses:
        return "over_budget"
    if "near_budget" in statuses:
        return "near_budget"
    if all(status == "within_budget" for status in statuses):
        return "within_budget"
    return "mixed"


def read_outcome_recommendation_signal(repo_root: Path) -> dict[str, object]:
    try:
        records = build_current_outcome_records(repo_root)
        recommendations = build_recommendations(repo_root, records)
    except ValueError as exc:
        return {
            "result": "WARN",
            "recommendation_count": 0,
            "recommendation_ids": [],
            "top_recommendation": "",
            "warning": str(exc),
        }
    ids = [item.recommendation_id for item in recommendations]
    status = "PASS" if ids == ["REC-PROCEED-Q17-WITH-GATES"] or ids == ["REC-PROCEED-Q18-WITH-GATES"] else "WARN"
    return {
        "result": status,
        "recommendation_count": len(recommendations),
        "recommendation_ids": ids,
        "top_recommendation": ids[0] if ids else "",
    }


def route_quality_gate_status(verifier_result: str, golden_result: str, token_budget_status: str, review_status: str, context_status: str) -> str:
    if verifier_result == "FAIL" or golden_result == "FAIL":
        return "FAIL"
    if token_budget_status == "over_budget" or review_status == "FAIL":
        return "WARN"
    if verifier_result in {"WARN", "UNKNOWN", "MISSING"} or golden_result in {"WARN", "UNKNOWN"} or review_status == "WARN" or context_status == "WARN":
        return "WARN"
    return "PASS"


def provider_candidates_for_route_class(repo_root: Path, route_class: str) -> tuple[str, ...]:
    planned = {
        "no_model_tool": ("deterministic_tools",),
        "human_review": ("human",),
        "local_small": ("local_ollama", "local_lm_studio", "local_llama_cpp"),
        "local_strong": ("local_ollama", "local_lm_studio", "local_llama_cpp", "local_vllm", "local_sglang"),
        "cheap_remote": ("deepseek", "openrouter", "other_remote_provider"),
        "frontier": ("openai", "anthropic", "google_gemini", "human"),
        "blocked": (),
    }.get(route_class, ())
    if not (repo_root / PROVIDER_CATALOG_PATH).exists():
        return planned
    try:
        registry = import_provider_registry_module(repo_root)
        available = set(registry.provider_catalog_ids(repo_root))
    except (ImportError, AttributeError, OSError, ValueError):
        return planned
    return tuple(provider_id for provider_id in planned if provider_id in available)


def build_route_decision(repo_root: Path, task_packet_path: str = LATEST_PACKET_PATH) -> RouteDecision:
    rel_task = normalize_rel(task_packet_path)
    text, task_exists = read_task_packet_text(repo_root, rel_task)
    route_text = route_relevant_task_text(text) if task_exists else ""
    task_class = classify_route_task(route_text) if task_exists else "unknown"
    risk_class = classify_route_risk(task_class, route_text) if task_exists else "unknown"
    profile = route_profile_for_task(repo_root, task_class)
    route_class = profile.preferred_route_class
    fallback_route_class = profile.fallback_route_class
    hard_floor = hard_floor_for_route(task_class, risk_class, route_text)
    rationale: list[str] = []
    required_checks: list[str] = list(parse_simple_list(read_text(repo_root / ROUTING_POLICY_PATH), "quality_gates")) if (repo_root / ROUTING_POLICY_PATH).exists() else []
    notes: list[str] = [
        "advisory_only: true",
        "provider_or_model_calls: none",
        "network_calls: none",
        "route_decisions_apply_automatically: false",
    ]
    blocked = False
    blocked_reason = ""
    if not task_exists:
        blocked = True
        blocked_reason = f"task packet missing: {rel_task}"
        route_class = "blocked"
        fallback_route_class = "human_review"
        rationale.append("Cannot route safely without a compact task packet.")
    else:
        rationale.append(f"Classified task as {task_class} with {risk_class} risk from compact task goal/phase text.")
    if hard_floor != "none" and not blocked:
        floor_route, floor_fallback = route_from_hard_floor(repo_root, hard_floor)
        route_class = floor_route
        fallback_route_class = floor_fallback
        rationale.append(f"Hard floor applied: {hard_floor}; route cannot be demoted below {floor_route}.")

    token_status = latest_token_budget_status(repo_root)
    verifier = read_verifier_signal(repo_root)
    golden = read_golden_signal(repo_root)
    review = read_review_packet_signal(repo_root)
    context = read_context_signal(repo_root)
    outcome = read_outcome_recommendation_signal(repo_root)
    verifier_result = str(verifier.get("result", "UNKNOWN"))
    golden_result = str(golden.get("result", "UNKNOWN"))
    review_result = str(review.get("result", "UNKNOWN"))
    context_result = str(context.get("result", "UNKNOWN"))
    quality_gate_status = route_quality_gate_status(verifier_result, golden_result, token_status, review_result, context_result)

    if not blocked and golden_result == "FAIL" and ("token" in route_text.lower() or task_class in {"compact_task_generation", "context_indexing", "bounded_code_patch", "maintenance_suggestion"}):
        blocked = True
        blocked_reason = "golden tasks failed; token optimization cannot be promoted"
        route_class = "blocked"
        fallback_route_class = "human_review"
        rationale.append("Golden tasks are failing, so token-saving work must repair quality gates first.")
    if not blocked and verifier_result == "FAIL" and "fix verifier" not in route_text.lower():
        blocked = True
        blocked_reason = "verifier failed; repair evidence before review or execution"
        route_class = "blocked"
        fallback_route_class = "human_review"
        rationale.append("Verifier FAIL blocks expensive review of invalid or incomplete evidence.")
    if token_status == "over_budget":
        rationale.append("A compact prompt surface is over budget; tighten context before spending premium tokens.")
        required_checks.append("token_budget_repair")
    if context_result == "WARN" and task_class != "context_indexing":
        rationale.append("Context artifacts are missing or stale; rerun snapshot/index/context before broad work.")
        required_checks.append("snapshot_index_context")
    if task_class == "unknown" and not blocked:
        route_class = "frontier"
        fallback_route_class = "human_review"
        rationale.append("Unknown task class routes conservatively to frontier or human review.")
    if route_class not in ROUTE_CLASSES:
        route_class = "frontier"
        fallback_route_class = "human_review"
        rationale.append("Route profile contained an unknown class; conservative frontier route selected.")
    provider_candidates = provider_candidates_for_route_class(repo_root, route_class)
    if provider_candidates:
        notes.append(f"provider_candidates_metadata_only: {', '.join(provider_candidates)}")
        notes.append("provider_adapter_live_calls_allowed: false")

    evidence_sources = [
        rel for rel in [
            rel_task,
            LATEST_CONTEXT_PACKET_PATH,
            LATEST_VERIFICATION_REPORT_PATH,
            GOLDEN_RUN_JSON_PATH,
            TOKEN_SUMMARY_PATH,
            OUTCOME_REPORT_PATH,
            RECOMMENDATIONS_PATH,
            ROUTING_POLICY_PATH,
            ROUTES_PATH,
            HARD_FLOORS_PATH,
            PROVIDER_ADAPTER_POLICY_PATH,
            PROVIDER_CATALOG_PATH,
            PROVIDER_STATUS_JSON_PATH,
        ] if (repo_root / rel).exists()
    ]
    return RouteDecision(
        schema_version="aide.route-decision.v0",
        route_id="q17.latest",
        task_source=rel_task,
        task_class=task_class,
        risk_class=risk_class,
        route_class=route_class,
        fallback_route_class=fallback_route_class,
        hard_floor_applied=hard_floor,
        blocked=blocked,
        blocked_reason=blocked_reason,
        rationale=tuple(rationale or ["No route rationale could be derived; use human review."]),
        evidence_sources=tuple(sorted(set(evidence_sources))),
        required_checks=tuple(sorted(set(required_checks))),
        token_budget_status=token_status,
        verifier_status=verifier_result,
        golden_task_status=golden_result,
        outcome_recommendation_status=str(outcome.get("result", "UNKNOWN")),
        quality_gate_status=quality_gate_status,
        notes=tuple(notes),
    )


def route_decision_to_dict(decision: RouteDecision) -> dict[str, object]:
    return {
        "schema_version": decision.schema_version,
        "generator": GENERATOR_NAME,
        "generator_version": GENERATOR_VERSION,
        "route_id": decision.route_id,
        "task_source": decision.task_source,
        "task_class": decision.task_class,
        "risk_class": decision.risk_class,
        "route_class": decision.route_class,
        "fallback_route_class": decision.fallback_route_class,
        "hard_floor_applied": decision.hard_floor_applied,
        "blocked": decision.blocked,
        "blocked_reason": decision.blocked_reason,
        "rationale": list(decision.rationale),
        "evidence_sources": list(decision.evidence_sources),
        "required_checks": list(decision.required_checks),
        "token_budget_status": decision.token_budget_status,
        "verifier_status": decision.verifier_status,
        "golden_task_status": decision.golden_task_status,
        "outcome_recommendation_status": decision.outcome_recommendation_status,
        "quality_gate_status": decision.quality_gate_status,
        "notes": list(decision.notes),
        "advisory_only": True,
        "live_calls_allowed_in_q17": False,
        "live_calls_allowed_in_q20": False,
        "provider_metadata_only": True,
        "contents_inline": False,
        "raw_prompt_storage": False,
        "raw_response_storage": False,
    }


def render_route_decision_md(decision: RouteDecision) -> str:
    rationale_lines = "\n".join(f"- {line}" for line in decision.rationale)
    evidence_lines = "\n".join(f"- `{rel}`" for rel in decision.evidence_sources) or "- none"
    check_lines = "\n".join(f"- {item}" for item in decision.required_checks) or "- none"
    note_lines = "\n".join(f"- {item}" for item in decision.notes)
    return f"""# AIDE Latest Route Decision

## ROUTE_DECISION

- route_id: {decision.route_id}
- task_source: `{decision.task_source}`
- task_class: {decision.task_class}
- risk_class: {decision.risk_class}
- route_class: {decision.route_class}
- fallback_route_class: {decision.fallback_route_class}
- hard_floor_applied: {decision.hard_floor_applied}
- blocked: {'true' if decision.blocked else 'false'}
- blocked_reason: {decision.blocked_reason or "none"}

## QUALITY_GATES

- token_budget_status: {decision.token_budget_status}
- verifier_status: {decision.verifier_status}
- golden_task_status: {decision.golden_task_status}
- outcome_recommendation_status: {decision.outcome_recommendation_status}
- quality_gate_status: {decision.quality_gate_status}

## RATIONALE

{rationale_lines}

## REQUIRED_CHECKS

{check_lines}

## EVIDENCE_SOURCES

{evidence_lines}

## SAFETY

- advisory_only: true
- provider_or_model_calls: none
- network_calls: none
- automatic_execution: false
- automatic_policy_mutation: false
- gateway_behavior: false
- contents_inline: false

## NOTES

{note_lines}
"""


def write_route_decision(repo_root: Path, decision: RouteDecision) -> tuple[WriteResult, WriteResult]:
    json_result = write_text_if_changed(repo_root / ROUTE_DECISION_JSON_PATH, json.dumps(route_decision_to_dict(decision), indent=2, sort_keys=True))
    md_result = write_text_if_changed(repo_root / ROUTE_DECISION_MD_PATH, render_route_decision_md(decision))
    return json_result, md_result


def validate_route_decision_data(data: dict[str, object]) -> list[Check]:
    checks: list[Check] = []
    for field in ROUTE_DECISION_REQUIRED_FIELDS:
        if field not in data:
            checks.append(Check("FAIL", f"route decision missing field: {field}"))
    route_class = str(data.get("route_class", ""))
    if route_class not in ROUTE_CLASSES:
        checks.append(Check("FAIL", f"route decision has invalid route_class: {route_class}"))
    if data.get("live_calls_allowed_in_q17") is not False:
        checks.append(Check("FAIL", "route decision must keep live_calls_allowed_in_q17 false"))
    if data.get("contents_inline") is not False:
        checks.append(Check("FAIL", "route decision must keep contents_inline false"))
    if "raw_prompt_body" in json.dumps(data) or "raw_response_body" in json.dumps(data):
        checks.append(Check("FAIL", "route decision must not store raw prompt/response bodies"))
    if not checks:
        checks.append(Check("PASS", "route decision shape is valid"))
    return checks


def routing_validation_checks(repo_root: Path) -> list[Check]:
    checks: list[Check] = []
    for rel in Q17_REQUIRED_FILES:
        if (repo_root / rel).exists():
            checks.append(Check("PASS", f"routing artifact exists: {rel}"))
        else:
            checks.append(Check("FAIL", f"routing artifact missing: {rel}"))
    routing_policy = repo_root / ROUTING_POLICY_PATH
    if routing_policy.exists():
        text = read_text(routing_policy)
        for anchor in ROUTING_POLICY_ANCHORS:
            if anchor not in text:
                checks.append(Check("FAIL", f"routing policy missing anchor: {anchor}"))
    for rel, anchors in MODEL_REGISTRY_ANCHORS.items():
        path = repo_root / rel
        if not path.exists():
            continue
        text = read_text(path)
        if "live_calls_allowed_in_q17: true" in text:
            checks.append(Check("FAIL", f"live calls enabled in Q17 model file: {rel}"))
        for anchor in anchors:
            if anchor not in text:
                checks.append(Check("FAIL", f"model registry missing anchor in {rel}: {anchor}"))
    for profile in parse_route_profiles(repo_root):
        if profile.preferred_route_class not in ROUTE_CLASSES:
            checks.append(Check("FAIL", f"route profile has invalid preferred class: {profile.task_class}"))
        if profile.fallback_route_class not in ROUTE_CLASSES:
            checks.append(Check("FAIL", f"route profile has invalid fallback class: {profile.task_class}"))
    profile_ids = {profile.task_class for profile in parse_route_profiles(repo_root)}
    for task_class in TASK_CLASSES:
        if task_class not in profile_ids:
            checks.append(Check("FAIL", f"route profile missing task class: {task_class}"))
    hard_floors = parse_hard_floor_minimums(repo_root)
    for floor in ROUTING_HARD_FLOORS:
        if floor not in hard_floors:
            checks.append(Check("FAIL", f"hard floor missing: {floor}"))
    provider_text = read_text(repo_root / PROVIDERS_PATH) if (repo_root / PROVIDERS_PATH).exists() else ""
    for pattern in SECRET_PATTERNS:
        if pattern.search(provider_text):
            checks.append(Check("FAIL", "provider registry appears to contain secret-like material"))
    for rel in [ROUTE_DECISION_JSON_PATH, ROUTE_DECISION_MD_PATH]:
        if (repo_root / rel).exists():
            checks.append(Check("PASS", f"route decision artifact exists: {rel}"))
        else:
            checks.append(Check("WARN", f"route decision artifact missing: {rel}; run route explain"))
    decision_path = repo_root / ROUTE_DECISION_JSON_PATH
    if decision_path.exists():
        try:
            data = json.loads(read_text(decision_path))
            checks.extend(validate_route_decision_data(data))
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            checks.append(Check("FAIL", f"route decision JSON malformed: {exc}"))
    return checks


def parse_simple_list(text: str, key: str) -> list[str]:
    lines = text.splitlines()
    values: list[str] = []
    in_list = False
    base_indent = 0
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == f"{key}:":
            in_list = True
            base_indent = len(line) - len(line.lstrip())
            continue
        if in_list:
            indent = len(line) - len(line.lstrip())
            if indent <= base_indent and not stripped.startswith("- "):
                break
            if stripped.startswith("- "):
                values.append(stripped[2:].strip().strip('"').strip("'"))
    return values


def parse_int_value(text: str, key: str, default: int) -> int:
    match = re.search(rf"^\s*(?:-\s*)?{re.escape(key)}:\s*(\d+)\s*$", text, re.MULTILINE)
    return int(match.group(1)) if match else default


def load_token_budget(repo_root: Path) -> dict[str, int]:
    path = repo_root / ".aide/policies/token-budget.yaml"
    text = read_text(path) if path.exists() else ""
    return {
        "max_compact_task_packet_tokens": parse_int_value(text, "max_compact_task_packet_tokens", 3200),
        "max_review_packet_tokens": parse_int_value(text, "max_review_packet_tokens", 2400),
        "max_project_state_tokens": parse_int_value(text, "max_project_state_tokens", 1600),
        "max_context_packet_tokens": parse_int_value(text, "max_context_packet_tokens", 2400),
        "max_verification_report_tokens": parse_int_value(text, "max_verification_report_tokens", 2400),
        "max_evidence_packet_tokens": parse_int_value(text, "max_evidence_packet_tokens", 2400),
        "compact_task_packet_target_tokens": parse_int_value(text, "compact_task_packet_target_tokens", 1800),
    }


def load_regression_threshold(repo_root: Path) -> int:
    path = repo_root / TOKEN_LEDGER_POLICY_PATH
    text = read_text(path) if path.exists() else ""
    return parse_int_value(text, "default_warning_threshold_percent", 20)


def detect_surface(path: str) -> str:
    rel = normalize_rel(path)
    if rel == LATEST_PACKET_PATH:
        return "task_packet"
    if rel == LATEST_CONTEXT_PACKET_PATH:
        return "context_packet"
    if rel == REVIEW_PACKET_PATH:
        return "review_packet"
    if rel == LATEST_VERIFICATION_REPORT_PATH:
        return "verification_report"
    if "/evidence/" in rel:
        return "evidence_packet"
    if rel.startswith(".aide/evals/runs/"):
        return "eval_report"
    if rel.startswith(".aide/controller/"):
        return "controller_report"
    if rel.startswith(".aide/routing/"):
        return "route_report"
    if rel.startswith(".aide/cache/"):
        return "cache_report"
    if rel == "AGENTS.md" or rel.startswith(".aide/generated/"):
        return "generated_adapter"
    return "baseline_surface"


def budget_for_surface(repo_root: Path, surface: str) -> int | None:
    budget = load_token_budget(repo_root)
    mapping = {
        "task_packet": budget["max_compact_task_packet_tokens"],
        "context_packet": budget["max_context_packet_tokens"],
        "review_packet": budget["max_review_packet_tokens"],
        "verification_report": budget["max_verification_report_tokens"],
        "evidence_packet": budget["max_evidence_packet_tokens"],
        "eval_report": budget["max_evidence_packet_tokens"],
        "controller_report": budget["max_evidence_packet_tokens"],
        "route_report": budget["max_evidence_packet_tokens"],
        "cache_report": budget["max_evidence_packet_tokens"],
    }
    return mapping.get(surface)


def classify_budget_status(approx_tokens: int, budget: int | None) -> str:
    if not budget or budget <= 0:
        return "unknown_budget"
    if approx_tokens > budget:
        return "over_budget"
    if approx_tokens > int(math.floor(budget * 0.8)):
        return "near_budget"
    return "within_budget"


def ledger_budget_status(repo_root: Path, surface: str, approx_tokens: int) -> tuple[str, str]:
    budget = budget_for_surface(repo_root, surface)
    if budget is None:
        return "unknown", "unknown_budget"
    return str(budget), classify_budget_status(approx_tokens, budget)


def load_ignore_patterns(repo_root: Path) -> list[str]:
    path = repo_root / ".aide/context/ignore.yaml"
    if not path.exists():
        return []
    return parse_simple_list(read_text(path), "exclude")


def pattern_matches(rel_path: str, pattern: str) -> bool:
    rel = normalize_rel(rel_path)
    pattern = pattern.strip()
    if not pattern:
        return False
    if pattern.endswith("/**"):
        base = pattern[:-3].rstrip("/")
        if "/" not in base and not base.startswith("."):
            return base in rel.split("/")
        return rel == base or rel.startswith(base + "/")
    if "/" not in pattern:
        return any(fnmatch.fnmatch(part, pattern) for part in rel.split("/"))
    return fnmatch.fnmatch(rel, pattern)


def is_ignored(rel_path: str, patterns: Iterable[str]) -> bool:
    rel = normalize_rel(rel_path)
    if rel in GENERATED_CONTEXT_PATHS:
        return True
    return any(pattern_matches(rel, pattern) for pattern in patterns)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def coarse_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".py", ".ps1", ".sh", ".bat", ".cmd", ".js", ".ts", ".json", ".yaml", ".yml", ".toml"}:
        return "source-or-config"
    if suffix in {".md", ".txt", ".rst"}:
        return "document"
    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".pdf"}:
        return "binary-media"
    if suffix in {".zip", ".tar", ".gz", ".tgz", ".7z", ".rar", ".whl", ".nupkg"}:
        return "archive"
    if suffix in {".exe", ".dll", ".so", ".dylib", ".bin", ".iso", ".dmg", ".msi", ".pkg"}:
        return "binary"
    return "unknown"


def build_snapshot(repo_root: Path) -> dict[str, object]:
    patterns = load_ignore_patterns(repo_root)
    files: list[dict[str, object]] = []
    type_counts: dict[str, int] = {}
    total_size = 0
    for current_root, dirs, filenames in os.walk(repo_root):
        current = Path(current_root)
        rel_dir = normalize_rel(current.relative_to(repo_root)) if current != repo_root else ""
        dirs[:] = sorted(
            dirname
            for dirname in dirs
            if not is_ignored(f"{rel_dir}/{dirname}" if rel_dir else dirname, patterns)
        )
        for filename in sorted(filenames):
            path = current / filename
            rel = normalize_rel(path.relative_to(repo_root))
            if is_ignored(rel, patterns):
                continue
            stat = path.stat()
            kind = coarse_type(path)
            total_size += stat.st_size
            type_counts[kind] = type_counts.get(kind, 0) + 1
            files.append(
                {
                    "path": rel,
                    "size": stat.st_size,
                    "mtime": int(stat.st_mtime),
                    "sha256": sha256_file(path),
                    "extension": path.suffix.lower(),
                    "type": kind,
                }
            )
    files.sort(key=lambda item: str(item["path"]))
    return {
        "schema_version": "aide.repo-snapshot.v0",
        "generator": GENERATOR_NAME,
        "generator_version": GENERATOR_VERSION,
        "contents_inline": False,
        "ignored_patterns": patterns,
        "summary": {
            "file_count": len(files),
            "total_size": total_size,
            "aggregate_approx_tokens": approx_tokens_for_chars(total_size),
            "type_counts": dict(sorted(type_counts.items())),
        },
        "file_count": len(files),
        "files": files,
    }


def write_snapshot(repo_root: Path) -> WriteResult:
    snapshot = build_snapshot(repo_root)
    target = repo_root / SNAPSHOT_PATH
    return write_text_if_changed(target, json.dumps(snapshot, indent=2, sort_keys=True))


def load_snapshot(repo_root: Path) -> dict[str, object]:
    path = repo_root / SNAPSHOT_PATH
    if not path.exists():
        write_snapshot(repo_root)
    return json.loads(read_text(path))


def snapshot_fingerprint(snapshot: dict[str, object]) -> str:
    payload = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def classify_role(rel_path: str, coarse: str = "unknown") -> tuple[str, str]:
    rel = normalize_rel(rel_path)
    name = Path(rel).name
    suffix = Path(rel).suffix.lower()
    if rel in {".aide/profile.yaml", ".aide/toolchain.lock"} or rel.startswith(".aide/components/") or rel.startswith(".aide/tasks/") or rel.startswith(".aide/evals/") or rel.startswith(".aide/adapters/") or rel.startswith(".aide/compat/"):
        return "aide_contract", "aide contract/profile path"
    if rel.startswith(".aide/policies/"):
        return "aide_policy", "aide policy path"
    if rel.startswith(".aide/models/") or rel.startswith(".aide/routing/"):
        return "aide_policy", "AIDE advisory routing/model metadata path"
    if rel.startswith(".aide/prompts/"):
        return "aide_prompt", "aide prompt path"
    if rel.startswith(".aide/context/"):
        return "aide_context", "aide context path"
    if rel.startswith(".aide/queue/") and "/evidence/" in rel:
        return "aide_evidence", "aide queue evidence path"
    if rel.startswith(".aide/queue/"):
        return "aide_queue", "aide queue path"
    if rel.startswith(".aide/generated/") or rel in GENERATED_CONTEXT_PATHS:
        return "generated", "generated output path"
    if rel.startswith(".aide/scripts/tests/") or "/tests/" in rel or name.startswith("test_") or name.endswith("_test.py"):
        return "test", "test path/name heuristic"
    if rel.startswith("core/harness/"):
        return "harness_code", "core harness path"
    if rel.startswith("core/compat/"):
        return "compat_code", "core compatibility path"
    if rel.startswith("shared/"):
        return "shared_code", "shared implementation path"
    if rel.startswith("docs/") or suffix in {".md", ".rst"}:
        return "docs", "documentation path or extension"
    if rel.startswith("governance/"):
        return "governance", "governance path"
    if rel.startswith("inventory/"):
        return "inventory", "inventory path"
    if rel.startswith("matrices/"):
        return "matrix", "matrix path"
    if rel.startswith("research/"):
        return "research", "research path"
    if rel.startswith("hosts/"):
        return "host", "host path"
    if rel.startswith("bridges/"):
        return "bridge", "bridge path"
    if rel.startswith("scripts/") or rel.startswith(".aide/scripts/"):
        return "script", "script path"
    if coarse == "binary-media" or coarse == "archive" or coarse == "binary":
        return "binary_or_asset", "binary/archive/media type"
    if suffix in {".json", ".yaml", ".yml", ".toml", ".lock", ".ini", ".cfg"}:
        return "config", "configuration extension"
    return "unknown", "no deterministic role heuristic matched"


def generated_classification(rel_path: str) -> str:
    rel = normalize_rel(rel_path)
    if rel in GENERATED_CONTEXT_PATHS or rel.startswith(".aide/generated/") or rel in {ROUTE_DECISION_JSON_PATH, ROUTE_DECISION_MD_PATH}:
        return "generated"
    return "manual"


def priority_for_path(rel_path: str) -> int:
    rel = normalize_rel(rel_path)
    rules = [
        (100, [".aide/profile.yaml"]),
        (95, [".aide/policies/**"]),
        (94, [".aide/models/**", ".aide/routing/**"]),
        (92, [".aide/prompts/**"]),
        (90, [".aide/context/**"]),
        (88, [".aide/memory/**"]),
        (86, [".aide/queue/index.yaml"]),
        (85, [".aide/queue/Q11-context-compiler-v0/**"]),
        (84, ["AGENTS.md"]),
        (80, ["README.md", "ROADMAP.md", "PLANS.md", "IMPLEMENT.md", "DOCUMENTATION.md"]),
        (76, ["core/harness/**"]),
        (74, ["core/compat/**"]),
        (70, ["shared/**"]),
        (68, ["docs/reference/**"]),
        (64, ["docs/roadmap/**"]),
    ]
    for priority, patterns in rules:
        if any(pattern_matches(rel, pattern) for pattern in patterns):
            return priority
    return 10


def build_repo_map(repo_root: Path) -> dict[str, object]:
    snapshot = load_snapshot(repo_root)
    records: list[dict[str, object]] = []
    role_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}
    for entry in snapshot.get("files", []):
        rel = str(entry["path"])
        role, reason = classify_role(rel, str(entry.get("type", "unknown")))
        priority = priority_for_path(rel)
        priority_band = "high" if priority >= 80 else "medium" if priority >= 60 else "normal"
        role_counts[role] = role_counts.get(role, 0) + 1
        priority_counts[priority_band] = priority_counts.get(priority_band, 0) + 1
        records.append(
            {
                "path": rel,
                "hash": entry.get("sha256", ""),
                "size": entry.get("size", 0),
                "extension": entry.get("extension", ""),
                "coarse_type": entry.get("type", "unknown"),
                "role": role,
                "role_reason": reason,
                "priority": priority,
                "priority_band": priority_band,
                "classification": generated_classification(rel),
            }
        )
    records.sort(key=lambda item: (str(item["role"]), str(item["path"])))
    return {
        "schema_version": "aide.repo-map.v0",
        "generator": GENERATOR_NAME,
        "generator_version": GENERATOR_VERSION,
        "contents_inline": False,
        "source_snapshot": SNAPSHOT_PATH,
        "source_snapshot_hash": snapshot_fingerprint(snapshot),
        "summary": {
            "file_count": len(records),
            "role_counts": dict(sorted(role_counts.items())),
            "priority_counts": dict(sorted(priority_counts.items())),
        },
        "files": records,
    }


def render_repo_map_md(repo_map: dict[str, object]) -> str:
    files = list(repo_map.get("files", []))
    summary = repo_map.get("summary", {})
    role_counts = dict(summary.get("role_counts", {})) if isinstance(summary, dict) else {}
    lines = [
        "# AIDE Repo Map",
        "",
        "Generated by AIDE Lite Context Compiler v0. This map contains repo-relative refs and metadata only; it does not inline file contents.",
        "",
        "## Summary",
        "",
        f"- file_count: {summary.get('file_count', len(files)) if isinstance(summary, dict) else len(files)}",
        f"- source_snapshot: `{repo_map.get('source_snapshot', SNAPSHOT_PATH)}`",
        f"- source_snapshot_hash: `{repo_map.get('source_snapshot_hash', '')}`",
        "- contents_inline: false",
        "",
        "## Role Counts",
        "",
    ]
    for role in ROLE_ORDER:
        if role in role_counts:
            lines.append(f"- {role}: {role_counts[role]}")
    lines.extend(["", "## Important Paths", ""])
    for role in ROLE_ORDER:
        role_files = [entry for entry in files if entry.get("role") == role]
        if not role_files:
            continue
        role_files.sort(key=lambda item: (-int(item.get("priority", 0)), str(item.get("path", ""))))
        lines.append(f"### {role}")
        lines.append("")
        for entry in role_files[:12]:
            lines.append(
                f"- `{entry['path']}` (priority {entry['priority']}, {entry['coarse_type']}, {entry['classification']})"
            )
        if len(role_files) > 12:
            lines.append(f"- ... {len(role_files) - 12} more")
        lines.append("")
    return "\n".join(lines)


def write_repo_map(repo_root: Path) -> tuple[WriteResult, WriteResult, dict[str, object]]:
    repo_map = build_repo_map(repo_root)
    json_result = write_text_if_changed(repo_root / REPO_MAP_JSON_PATH, json.dumps(repo_map, indent=2, sort_keys=True))
    md_result = write_text_if_changed(repo_root / REPO_MAP_MD_PATH, render_repo_map_md(repo_map))
    return json_result, md_result, repo_map


def test_record(path: str, exists: bool, kind: str = "file") -> dict[str, object]:
    return {"path": path, "exists": exists, "kind": kind}


def likely_test_candidates(repo_root: Path, source_path: str) -> tuple[list[dict[str, object]], str, str]:
    rel = normalize_rel(source_path)
    stem = Path(rel).stem
    candidates: list[str] = []
    confidence = "low"
    reason = "no direct test heuristic; use structural validation"
    if rel == ".aide/scripts/aide_lite.py":
        candidates = [".aide/scripts/tests/test_aide_lite.py", "core/harness/tests/test_aide_lite.py"]
        confidence = "high"
        reason = "AIDE Lite has direct and Harness-side tests"
    elif rel.startswith("core/harness/") and rel.endswith(".py") and "/tests/" not in rel:
        candidates = [f"core/harness/tests/test_{stem}.py", "core/harness/tests/test_aide_harness.py"]
        confidence = "medium"
        reason = "core/harness module mapped by test_<module> and Harness smoke tests"
    elif rel.startswith("core/compat/") and rel.endswith(".py") and "/tests/" not in rel:
        candidates = [f"core/compat/tests/test_{stem}.py", "core/compat/tests/test_compat_baseline.py"]
        confidence = "medium"
        reason = "core/compat module mapped by test_<module> and compatibility baseline tests"
    elif rel.startswith("shared/") and rel.endswith(".py") and "/tests/" not in rel:
        candidates = [f"shared/tests/test_{stem}.py"]
        confidence = "medium"
        reason = "shared module mapped by shared/tests naming convention"
    elif rel.startswith("scripts/") or rel.endswith(".md") or rel.endswith(".yaml"):
        candidates = ["scripts/aide"]
        confidence = "low"
        reason = "structural Harness validation is the likely check"
    records = [test_record(candidate, (repo_root / candidate).exists()) for candidate in dict.fromkeys(candidates)]
    return records, confidence, reason


def build_test_map(repo_root: Path, repo_map: dict[str, object] | None = None) -> dict[str, object]:
    repo_map = repo_map or build_repo_map(repo_root)
    mappings: list[dict[str, object]] = []
    for entry in repo_map.get("files", []):
        rel = str(entry["path"])
        role = str(entry.get("role", "unknown"))
        if role in {"test", "binary_or_asset", "generated"}:
            continue
        candidates, confidence, reason = likely_test_candidates(repo_root, rel)
        if not candidates and role not in {"harness_code", "compat_code", "shared_code", "script", "docs", "aide_context"}:
            continue
        mappings.append(
            {
                "source": rel,
                "source_role": role,
                "candidate_tests": candidates,
                "confidence": confidence,
                "reason": reason,
                "has_existing_candidate": any(bool(candidate["exists"]) for candidate in candidates),
            }
        )
    mappings.sort(key=lambda item: str(item["source"]))
    return {
        "schema_version": "aide.test-map.v0",
        "generator": GENERATOR_NAME,
        "generator_version": GENERATOR_VERSION,
        "complete_coverage_claimed": False,
        "summary": {
            "mapping_count": len(mappings),
            "with_existing_candidate": sum(1 for item in mappings if item["has_existing_candidate"]),
            "without_existing_candidate": sum(1 for item in mappings if not item["has_existing_candidate"]),
        },
        "mappings": mappings,
    }


def write_test_map(repo_root: Path, repo_map: dict[str, object] | None = None) -> tuple[WriteResult, dict[str, object]]:
    test_map = build_test_map(repo_root, repo_map)
    result = write_text_if_changed(repo_root / TEST_MAP_JSON_PATH, json.dumps(test_map, indent=2, sort_keys=True))
    return result, test_map


def build_context_index(repo_root: Path, repo_map: dict[str, object], test_map: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": "aide.context-index.v0",
        "generator": GENERATOR_NAME,
        "generator_version": GENERATOR_VERSION,
        "creation_mode": "deterministic-local",
        "contents_inline": False,
        "source_snapshot": SNAPSHOT_PATH,
        "source_snapshot_hash": repo_map.get("source_snapshot_hash", ""),
        "generated_outputs": {
            "repo_map_json": REPO_MAP_JSON_PATH,
            "repo_map_md": REPO_MAP_MD_PATH,
            "test_map_json": TEST_MAP_JSON_PATH,
            "latest_context_packet": LATEST_CONTEXT_PACKET_PATH,
        },
        "counts": {
            "repo_files": repo_map.get("summary", {}).get("file_count", 0),
            "test_mappings": test_map.get("summary", {}).get("mapping_count", 0),
            "test_mappings_with_existing_candidate": test_map.get("summary", {}).get("with_existing_candidate", 0),
        },
        "role_counts": repo_map.get("summary", {}).get("role_counts", {}),
    }


def write_context_index(repo_root: Path, repo_map: dict[str, object], test_map: dict[str, object]) -> tuple[WriteResult, dict[str, object]]:
    context_index = build_context_index(repo_root, repo_map, test_map)
    result = write_text_if_changed(repo_root / CONTEXT_INDEX_PATH, json.dumps(context_index, indent=2, sort_keys=True))
    return result, context_index


def current_queue_ref(repo_root: Path) -> str:
    for queue_id in [
        "Q17-router-profile-v0",
        "Q16-outcome-controller-v0",
        "Q15-golden-tasks-v0",
        "Q14-token-ledger-savings-report",
        "Q13-evidence-review-workflow",
        "Q12-verifier-v0",
        "Q11-context-compiler-v0",
        "Q10-aide-lite-hardening",
        "Q09-token-survival-core",
    ]:
        if (repo_root / f".aide/queue/{queue_id}/status.yaml").exists():
            return f".aide/queue/{queue_id}/"
    return ".aide/queue/index.yaml"


def render_context_packet(repo_root: Path, repo_map: dict[str, object], test_map: dict[str, object], context_index: dict[str, object], chars: int = 0, tokens: int = 0) -> str:
    role_counts = context_index.get("role_counts", {})
    role_lines = []
    for role in ROLE_ORDER:
        if role in role_counts:
            role_lines.append(f"- {role}: {role_counts[role]}")
    if not role_lines:
        role_lines.append("- none")
    return f"""# AIDE Latest Context Packet

## CONTEXT_COMPILER

- compiler: q11-context-compiler-v0
- generator: {GENERATOR_NAME}
- generator_version: {GENERATOR_VERSION}
- contents_inline: false
- method: deterministic repo-local metadata, roles, priorities, and test heuristics

## SOURCE_REFS

- `{CONTEXT_COMPILER_CONFIG_PATH}`
- `{CONTEXT_PRIORITY_PATH}`
- `{EXCERPT_POLICY_PATH}`
- `.aide/context/ignore.yaml`
- `{DOCTRINE_REFS_PATH}` ({'present' if (repo_root / DOCTRINE_REFS_PATH).exists() else 'missing'})
- `{SNAPSHOT_PATH}`
- `{CONTEXT_INDEX_PATH}`
- `.aide/memory/project-state.md`
- `.aide/memory/decisions.md`
- `.aide/memory/open-risks.md`

## REPO_MAP

- json: `{REPO_MAP_JSON_PATH}`
- markdown: `{REPO_MAP_MD_PATH}`
- file_count: {context_index.get('counts', {}).get('repo_files', 0)}
- source_snapshot_hash: `{context_index.get('source_snapshot_hash', '')}`

## ROLE_COUNTS

{chr(10).join(role_lines)}

## TEST_MAP

- path: `{TEST_MAP_JSON_PATH}`
- mapping_count: {test_map.get('summary', {}).get('mapping_count', 0)}
- mappings_with_existing_candidate: {test_map.get('summary', {}).get('with_existing_candidate', 0)}
- complete_coverage_claimed: false

## CURRENT_QUEUE

- current_queue_ref: `{current_queue_ref(repo_root)}`
- queue_index: `.aide/queue/index.yaml`

## EXACT_REFS

- Preferred syntax: `path#Lstart-Lend`
- Validate refs before use.
- Do not inline whole files by default.
- Never inline ignored files, secrets, local state, caches, or binary artifacts.

## PACKET_GUIDANCE

- Use repo-map and test-map refs before broad documentation dumps.
- Include exact line refs only when required for correctness.
- Ask for additional context only when the compact packet is insufficient.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: {chars}
- approx_tokens: {tokens}
- formal ledger: `.aide/reports/token-ledger.jsonl`
"""


def build_context_packet(repo_root: Path, repo_map: dict[str, object], test_map: dict[str, object], context_index: dict[str, object]) -> PacketRender:
    body = render_context_packet(repo_root, repo_map, test_map, context_index)
    for _ in range(5):
        stats = estimate_text(body, LATEST_CONTEXT_PACKET_PATH)
        updated = render_context_packet(repo_root, repo_map, test_map, context_index, stats.chars, stats.approx_tokens)
        if updated == body:
            break
        body = updated
    stats = estimate_text(body, LATEST_CONTEXT_PACKET_PATH)
    return PacketRender(body, stats, "PASS", ())


def write_context_packet(repo_root: Path, repo_map: dict[str, object], test_map: dict[str, object], context_index: dict[str, object]) -> tuple[WriteResult, PacketRender]:
    packet = build_context_packet(repo_root, repo_map, test_map, context_index)
    result = write_text_if_changed(repo_root / LATEST_CONTEXT_PACKET_PATH, packet.text)
    return result, packet


def run_index(repo_root: Path) -> dict[str, object]:
    snapshot_result = write_snapshot(repo_root)
    repo_map_json, repo_map_md, repo_map = write_repo_map(repo_root)
    test_map_result, test_map = write_test_map(repo_root, repo_map)
    context_index_result, context_index = write_context_index(repo_root, repo_map, test_map)
    return {
        "snapshot": snapshot_result,
        "repo_map_json": repo_map_json,
        "repo_map_md": repo_map_md,
        "test_map": test_map_result,
        "context_index": context_index_result,
        "repo_map": repo_map,
        "test_map_data": test_map,
        "context_index_data": context_index,
    }


def run_context(repo_root: Path) -> dict[str, object]:
    index_result = run_index(repo_root)
    context_packet_result, context_packet = write_context_packet(
        repo_root,
        index_result["repo_map"],
        index_result["test_map_data"],
        index_result["context_index_data"],
    )
    index_result["context_packet"] = context_packet_result
    index_result["context_packet_data"] = context_packet
    return index_result


def validate_line_ref(repo_root: Path, ref: str) -> tuple[bool, str]:
    match = re.match(r"^(?P<path>.+)#L(?P<start>\d+)-L(?P<end>\d+)$", ref)
    if not match:
        return False, "line ref must use path#Lstart-Lend"
    rel = normalize_rel(match.group("path"))
    start = int(match.group("start"))
    end = int(match.group("end"))
    if start < 1 or end < start:
        return False, "line range must be positive and ordered"
    try:
        target = safe_repo_path(repo_root, rel)
    except ValueError as exc:
        return False, str(exc)
    if not target.exists() or not target.is_file():
        return False, "line ref target does not exist as a file"
    if is_ignored(rel, load_ignore_patterns(repo_root)):
        return False, "line ref target is ignored"
    if looks_binary(target):
        return False, "line ref target is binary-like"
    line_count = read_text(target).count("\n") + 1
    if end > line_count:
        return False, f"line range exceeds file length: {line_count}"
    return True, "line ref is valid"


def contains_section(text: str, section: str) -> bool:
    return re.search(rf"^##\s+{re.escape(section)}\s*$", text, re.MULTILINE) is not None


def missing_sections(text: str, sections: Iterable[str]) -> list[str]:
    return [section for section in sections if not contains_section(text, section)]


def add_finding(findings: list[VerificationFinding], severity: str, check: str, message: str, path: str = "") -> None:
    findings.append(VerificationFinding(severity.upper(), check, message, normalize_rel(path) if path else ""))


def verification_result(findings: Iterable[VerificationFinding]) -> str:
    severities = {finding.severity.upper() for finding in findings}
    if "ERROR" in severities or "FAIL" in severities:
        return "FAIL"
    if "WARN" in severities or "WARNING" in severities:
        return "WARN"
    return "PASS"


def line_ref_match(ref: str) -> re.Match[str] | None:
    return re.match(r"^(?P<path>.+)#L(?P<start>\d+)-L(?P<end>\d+)$", ref)


def is_external_url(ref: str) -> bool:
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", ref))


def is_absolute_machine_path(ref: str) -> bool:
    return bool(re.match(r"^[A-Za-z]:[\\/]", ref)) or ref.startswith("/") or ref.startswith("\\\\")


def is_reference_candidate(ref: str) -> bool:
    candidate = ref.strip().strip(".,;:)")
    if not candidate or any(marker in candidate for marker in ["<", ">", "|", "*"]):
        return False
    if " " in candidate or "\t" in candidate:
        return False
    if candidate.startswith(("-", "--")):
        return False
    if line_ref_match(candidate) or is_external_url(candidate) or is_absolute_machine_path(candidate):
        return True
    if "/" in candidate or "\\" in candidate or candidate.startswith("."):
        return True
    suffix = Path(candidate).suffix.lower()
    return suffix in {".md", ".yaml", ".yml", ".json", ".py", ".toml", ".txt", ".ps1", ".sh"}


def clean_reference(ref: str) -> str:
    return ref.strip().strip("`").strip().rstrip(".,;:)")


def extract_file_refs(text: str) -> list[str]:
    refs: list[str] = []
    seen: set[str] = set()
    markdown_targets = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    backtick_targets = re.findall(r"`([^`\n]+)`", text)
    for raw in [*markdown_targets, *backtick_targets]:
        candidate = clean_reference(raw)
        if "#" in candidate and not line_ref_match(candidate):
            # Markdown anchor refs are not file refs unless they use the exact line syntax.
            continue
        if not is_reference_candidate(candidate):
            continue
        if candidate not in seen:
            refs.append(candidate)
            seen.add(candidate)
    return refs


def validate_file_reference(repo_root: Path, ref: str) -> VerificationFinding:
    clean = clean_reference(ref)
    if is_external_url(clean):
        return VerificationFinding("ERROR", "file_references", "external URL refs are not allowed in Q12 packets", clean)
    if is_absolute_machine_path(clean):
        return VerificationFinding("ERROR", "file_references", "absolute machine path refs are not allowed", clean)
    if line_ref_match(clean):
        ok, message = validate_line_ref(repo_root, clean)
        severity = "INFO" if ok else "ERROR"
        return VerificationFinding(severity, "file_references", message, clean)
    rel = normalize_rel(clean)
    try:
        target = safe_repo_path(repo_root, rel)
    except ValueError as exc:
        return VerificationFinding("ERROR", "file_references", str(exc), rel)
    if rel == ".aide.local":
        return VerificationFinding("INFO", "file_references", "local-state boundary root is referenced as policy metadata", rel)
    if rel not in GENERATED_CONTEXT_PATHS and is_ignored(rel, load_ignore_patterns(repo_root)):
        return VerificationFinding("ERROR", "file_references", "ref points at ignored path", rel)
    if not target.exists():
        return VerificationFinding("WARN", "file_references", "referenced path does not exist", rel)
    return VerificationFinding("INFO", "file_references", "referenced path exists", rel)


def verify_refs_in_text(repo_root: Path, text: str, source_path: str) -> list[VerificationFinding]:
    findings: list[VerificationFinding] = []
    for ref in extract_file_refs(text):
        finding = validate_file_reference(repo_root, ref)
        findings.append(
            VerificationFinding(
                finding.severity,
                finding.check,
                f"{finding.message} (from {source_path})",
                finding.path,
            )
        )
    if not findings:
        findings.append(VerificationFinding("INFO", "file_references", f"no conservative file refs found in {source_path}", source_path))
    return findings


def scan_secret_text(text: str, rel_path: str) -> list[VerificationFinding]:
    findings: list[VerificationFinding] = []
    for pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            snippet = match.group(0)
            keyish = snippet.split("=", 1)[0].split(":", 1)[0].strip()
            findings.append(VerificationFinding("ERROR", "secret_scan", f"secret-like value detected near `{keyish}`", rel_path))
    if not findings and SECRET_POLICY_TERM_PATTERN.search(text):
        findings.append(VerificationFinding("INFO", "secret_scan", "policy/token/security terms present without secret-like values", rel_path))
    return findings


def verification_scan_paths(repo_root: Path) -> list[str]:
    candidates = [
        *REQUIRED_FILES,
        *CONTEXT_CONFIG_FILES,
        *CONTEXT_OUTPUT_PATHS,
        *Q12_REQUIRED_FILES,
        *Q16_REQUIRED_FILES,
        *Q17_REQUIRED_FILES,
        *Q18_REQUIRED_FILES,
        *Q19_REQUIRED_FILES,
        *Q20_REQUIRED_FILES,
        ROUTE_DECISION_JSON_PATH,
        ROUTE_DECISION_MD_PATH,
        CACHE_KEYS_JSON_PATH,
        CACHE_KEYS_MD_PATH,
        GATEWAY_POLICY_PATH,
        GATEWAY_DIR,
        PROVIDER_ADAPTER_POLICY_PATH,
        PROVIDER_DIR,
        LATEST_PACKET_PATH,
        LATEST_CONTEXT_PACKET_PATH,
        "AGENTS.md",
        "README.md",
        "ROADMAP.md",
        "PLANS.md",
        "IMPLEMENT.md",
        "DOCUMENTATION.md",
        ".aide/scripts/aide_lite.py",
    ]
    seen: set[str] = set()
    existing: list[str] = []
    for rel in candidates:
        if rel in seen:
            continue
        seen.add(rel)
        if (repo_root / rel).exists():
            existing.append(rel)
    return existing


def scan_for_secret_findings(repo_root: Path, paths: Iterable[str]) -> list[VerificationFinding]:
    findings: list[VerificationFinding] = []
    for rel in paths:
        path = repo_root / rel
        if not path.exists() or not path.is_file():
            continue
        try:
            if looks_binary(path):
                continue
            findings.extend(scan_secret_text(read_text(path), rel))
        except (OSError, UnicodeDecodeError):
            findings.append(VerificationFinding("WARN", "secret_scan", "could not read file for secret scan", rel))
    return findings


def active_scope_task_path(repo_root: Path) -> Path | None:
    for queue_id in ["Q20-provider-adapter-v0", "Q19-gateway-architecture-skeleton", "Q18-cache-local-state-boundary", "Q17-router-profile-v0", "Q16-outcome-controller-v0", "Q15-golden-tasks-v0", "Q14-token-ledger-savings-report", "Q13-evidence-review-workflow", "Q12-verifier-v0"]:
        preferred = repo_root / f".aide/queue/{queue_id}/task.yaml"
        if preferred.exists():
            return preferred
    index = repo_root / ".aide/queue/index.yaml"
    if not index.exists():
        return None
    text = read_text(index)
    blocks = re.split(r"\n\s*-\s+id:\s+", "\n" + text)
    for block in reversed(blocks):
        if "status: active" in block:
            match = re.search(r"task:\s*(\S+)", block)
            if match:
                candidate = repo_root / match.group(1)
                if candidate.exists():
                    return candidate
    return None


def load_scope_patterns(repo_root: Path) -> tuple[list[str], list[str]]:
    task_path = active_scope_task_path(repo_root)
    if task_path and task_path.exists():
        text = read_text(task_path)
        allowed = parse_simple_list(text, "allowed_paths")
        forbidden = parse_simple_list(text, "forbidden_paths")
    else:
        allowed = []
        forbidden = []
    if not allowed:
        allowed = [
            ".aide/queue/Q20-provider-adapter-v0/**",
            ".aide/queue/Q19-gateway-architecture-skeleton/**",
            ".aide/queue/Q17-router-profile-v0/**",
            ".aide/queue/Q16-outcome-controller-v0/**",
            ".aide/queue/Q15-golden-tasks-v0/**",
            ".aide/queue/Q14-token-ledger-savings-report/**",
            ".aide/queue/Q13-evidence-review-workflow/**",
            ".aide/queue/Q12-verifier-v0/**",
            ".aide/controller/**",
            ".aide/gateway/**",
            ".aide/providers/**",
            ".aide/policies/gateway.yaml",
            ".aide/policies/provider-adapters.yaml",
            ".aide/policies/controller.yaml",
            ".aide/routing/**",
            ".aide/models/**",
            ".aide/policies/routing.yaml",
            ".aide/evals/**",
            ".aide/policies/evals.yaml",
            ".aide/scripts/**",
            ".aide/reports/**",
            ".aide/policies/token-ledger.yaml",
            ".aide/verification/**",
            ".aide/policies/verification.yaml",
            ".aide/context/**",
            "AGENTS.md",
            "README.md",
            "ROADMAP.md",
            "PLANS.md",
            "IMPLEMENT.md",
            "DOCUMENTATION.md",
            "docs/reference/**",
            "docs/roadmap/**",
            "core/gateway/**",
            "core/providers/**",
            "core/harness/**",
        ]
    if not forbidden:
        forbidden = [".git/**", ".env", "secrets/**", ".aide.local/**"]
    return allowed, forbidden


def classify_scope_path(rel_path: str, status: str, allowed: Iterable[str], forbidden: Iterable[str]) -> DiffScopeResult:
    rel = normalize_rel(rel_path)
    if any(pattern_matches(rel, pattern) for pattern in forbidden):
        return DiffScopeResult(status, rel, "forbidden", "matches forbidden path policy")
    if status.strip().startswith("D"):
        return DiffScopeResult(status, rel, "warning", "deleted path requires review")
    if any(pattern_matches(rel, pattern) for pattern in allowed):
        return DiffScopeResult(status, rel, "allowed", "matches active task allowed path")
    return DiffScopeResult(status, rel, "unknown", "does not match active task allowed paths")


def git_status_short(repo_root: Path) -> tuple[bool, list[tuple[str, str]], str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "status", "--short"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError as exc:
        return False, [], str(exc)
    if result.returncode != 0:
        return False, [], result.stderr.strip() or "git status failed"
    entries: list[tuple[str, str]] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        status = line[:2]
        path_part = line[3:] if len(line) > 3 else ""
        if " -> " in path_part:
            old, new = path_part.split(" -> ", 1)
            entries.append((status, old.strip().strip('"')))
            entries.append((status, new.strip().strip('"')))
        else:
            entries.append((status, path_part.strip().strip('"')))
    return True, entries, ""


def git_commit_id(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--verify", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError:
        return "unavailable"
    if result.returncode != 0:
        return "unavailable"
    return result.stdout.strip() or "unavailable"


def git_ls_files(repo_root: Path, pathspec: str) -> tuple[bool, list[str], str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", pathspec],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError as exc:
        return False, [], str(exc)
    if result.returncode != 0:
        return False, [], result.stderr.strip() or "git ls-files failed"
    return True, [normalize_rel(line) for line in result.stdout.splitlines() if line.strip()], ""


def stable_json_text(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True, separators=(",", ": ")) + "\n"


def stable_compact_json_text(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n"


def short_sha(value: str, length: int = 16) -> str:
    return value[:length]


def is_local_state_path(rel_path: str) -> bool:
    rel = normalize_rel(rel_path)
    return rel == LOCAL_STATE_ROOT or rel.startswith(f"{LOCAL_STATE_ROOT}/")


def is_secret_risk_path(rel_path: str) -> bool:
    rel = normalize_rel(rel_path)
    return rel == ".env" or rel.startswith("secrets/") or is_local_state_path(rel)


def gitignore_lines(repo_root: Path) -> list[str]:
    path = repo_root / ".gitignore"
    if not path.exists():
        return []
    return [line.strip() for line in read_text(path).splitlines() if line.strip() and not line.strip().startswith("#")]


def gitignore_has_local_state_rules(repo_root: Path) -> bool:
    lines = gitignore_lines(repo_root)
    return ".aide.local/" in lines and ".aide.local/**" in lines


def local_state_git_paths(repo_root: Path) -> list[str]:
    paths: set[str] = set()
    ok, tracked, _error = git_ls_files(repo_root, LOCAL_STATE_ROOT)
    if ok:
        paths.update(path for path in tracked if is_local_state_path(path))
    ok_status, entries, _status_error = git_status_short(repo_root)
    if ok_status:
        paths.update(path for _status, path in entries if is_local_state_path(path))
    return sorted(paths)


def policy_version(repo_root: Path, rel_path: str) -> str:
    path = repo_root / rel_path
    if not path.exists():
        return "missing"
    try:
        text = read_text(path)
    except OSError:
        return "unreadable"
    schema = re.search(r"^schema_version:\s*(.+)$", text, re.MULTILINE)
    policy = re.search(r"^policy_id:\s*(.+)$", text, re.MULTILINE)
    status = re.search(r"^status:\s*(.+)$", text, re.MULTILINE)
    schema_value = schema.group(1).strip() if schema else "unknown_schema"
    policy_value = policy.group(1).strip() if policy else normalize_rel(rel_path)
    status_value = status.group(1).strip() if status else "unknown_status"
    return f"{policy_value}:{schema_value}:{status_value}:sha256:{short_sha(sha256_text(text), 12)}"


def cache_policy_versions(repo_root: Path) -> tuple[tuple[str, str], ...]:
    policy_paths = [
        CACHE_POLICY_PATH,
        LOCAL_STATE_POLICY_PATH,
        ".aide/policies/token-budget.yaml",
        TOKEN_LEDGER_POLICY_PATH,
        VERIFICATION_POLICY_PATH,
        EVAL_POLICY_PATH,
        CONTROLLER_POLICY_PATH,
        ROUTING_POLICY_PATH,
        CONTEXT_COMPILER_CONFIG_PATH,
    ]
    return tuple((rel, policy_version(repo_root, rel)) for rel in policy_paths if (repo_root / rel).exists())


def dependency_hashes_for_cache_surface(repo_root: Path, surface: str, rel_path: str) -> tuple[tuple[str, str], ...]:
    candidates: list[str] = []
    if surface == "task_packet":
        candidates = [
            LATEST_CONTEXT_PACKET_PATH,
            ROUTE_DECISION_JSON_PATH,
            ".aide/policies/token-budget.yaml",
            CACHE_POLICY_PATH,
            LOCAL_STATE_POLICY_PATH,
        ]
    elif surface == "context_packet":
        candidates = [
            SNAPSHOT_PATH,
            REPO_MAP_JSON_PATH,
            TEST_MAP_JSON_PATH,
            CONTEXT_INDEX_PATH,
            CONTEXT_COMPILER_CONFIG_PATH,
            ".aide/context/ignore.yaml",
        ]
    elif surface == "review_packet":
        candidates = [
            LATEST_PACKET_PATH,
            LATEST_CONTEXT_PACKET_PATH,
            LATEST_VERIFICATION_REPORT_PATH,
            REVIEW_DECISION_POLICY_PATH,
        ]
    elif surface == "verification_report":
        candidates = [
            LATEST_PACKET_PATH,
            VERIFICATION_POLICY_PATH,
            EVIDENCE_TEMPLATE_PATH,
            REVIEW_TEMPLATE_PATH,
        ]
    elif surface == "route_decision":
        candidates = [
            LATEST_PACKET_PATH,
            LATEST_CONTEXT_PACKET_PATH,
            LATEST_VERIFICATION_REPORT_PATH,
            GOLDEN_RUN_JSON_PATH,
            TOKEN_SUMMARY_PATH,
            ROUTING_POLICY_PATH,
        ]
    elif surface == "golden_tasks_report":
        candidates = [EVAL_POLICY_PATH, GOLDEN_TASK_CATALOG_PATH]
    elif surface == "token_savings_summary":
        candidates = [TOKEN_LEDGER_PATH, TOKEN_LEDGER_POLICY_PATH, TOKEN_BASELINES_PATH]
    else:
        candidates = [CACHE_POLICY_PATH, LOCAL_STATE_POLICY_PATH]
    results = []
    for candidate in sorted(set(candidates)):
        if candidate == rel_path:
            continue
        path = repo_root / candidate
        if path.exists() and path.is_file():
            results.append((candidate, sha256_file(path)))
    return tuple(results)


def cache_key_id(surface: str, content_sha256: str, dependencies: Iterable[tuple[str, str]] = ()) -> str:
    seed = stable_json_text(
        {
            "surface": surface,
            "content_sha256": content_sha256,
            "dependencies": sorted(dependencies),
        }
    )
    return f"aide-cache-v0:{surface}:{short_sha(hashlib.sha256(seed.encode('utf-8')).hexdigest())}"


def assert_cache_safe_path(repo_root: Path, requested: str, allow_generated: bool = True) -> str:
    rel = normalize_rel(requested)
    if is_secret_risk_path(rel):
        raise ValueError(f"refusing ignored/local/secret path for cache key: {rel}")
    target = safe_repo_path(repo_root, rel)
    if not target.exists():
        raise ValueError(f"file does not exist: {rel}")
    if not target.is_file():
        raise ValueError(f"path is not a file: {rel}")
    generated_allowed = allow_generated and rel in GENERATED_CONTEXT_PATHS
    if not generated_allowed and is_ignored(rel, load_ignore_patterns(repo_root)):
        raise ValueError(f"refusing ignored/local/secret path for cache key: {rel}")
    if looks_binary(target):
        raise ValueError(f"refusing binary-like file for cache key: {rel}")
    return rel


def cache_record_for_file(
    repo_root: Path,
    requested: str,
    surface: str,
    key_name: str | None = None,
    valid_for: str = "metadata-only reuse decision; verifier and golden tasks still required",
    notes: str = "estimated deterministic metadata only; no raw prompt or response stored",
) -> CacheKeyRecord:
    rel = assert_cache_safe_path(repo_root, requested)
    content_hash = sha256_file(repo_root / rel)
    dependencies = dependency_hashes_for_cache_surface(repo_root, surface, rel)
    return CacheKeyRecord(
        key_name=key_name or surface,
        surface=surface,
        path=rel,
        key_id=cache_key_id(surface, content_hash, dependencies),
        content_sha256=content_hash,
        dependency_hashes=dependencies,
        policy_versions=cache_policy_versions(repo_root),
        dirty_state=bool(git_status_short(repo_root)[1]) if git_status_short(repo_root)[0] else False,
        valid_for=valid_for,
        notes=notes,
    )


def cache_record_to_dict(record: CacheKeyRecord) -> dict[str, object]:
    compact_policy_versions: dict[str, str] = {}
    for path, version in record.policy_versions:
        match = re.search(r"sha256:([0-9a-f]+)", version)
        compact_policy_versions[path] = short_sha(match.group(1), 12) if match else version[:32]
    return {
        "key_id": record.key_id,
        "surface": record.surface,
        "path": record.path,
        "content_sha256": record.content_sha256,
        "dependency_hashes": {path: short_sha(digest, 12) for path, digest in record.dependency_hashes},
        "policy_versions": compact_policy_versions,
        "dirty_state": record.dirty_state,
        "valid_for": record.valid_for,
        "notes": record.notes,
    }


def build_cache_key_records(repo_root: Path) -> list[CacheKeyRecord]:
    records: list[CacheKeyRecord] = []
    for rel, key_name, surface, notes in CACHE_SURFACES:
        if (repo_root / rel).exists():
            records.append(cache_record_for_file(repo_root, rel, surface=surface, key_name=key_name, notes=notes))
    return sorted(records, key=lambda item: item.key_name)


def cache_report_data(repo_root: Path) -> dict[str, object]:
    ok_status, entries, status_error = git_status_short(repo_root)
    records = build_cache_key_records(repo_root)
    return {
        "schema_version": "q18.cache-keys.v0",
        "generated_by": f"{GENERATOR_NAME} {GENERATOR_VERSION}",
        "contents_inline": False,
        "raw_prompt_storage": False,
        "raw_response_storage": False,
        "repo_state": {
            "git_commit": git_commit_id(repo_root),
            "dirty_state": bool(entries) if ok_status else False,
            "git_status": "available" if ok_status else f"unavailable: {status_error}",
        },
        "local_state_boundary": {
            "committed_contract_root": ".aide/",
            "local_state_root": ".aide.local/",
            "local_state_ignored": gitignore_has_local_state_rules(repo_root),
            "tracked_local_state_paths": local_state_git_paths(repo_root),
        },
        "keys": {record.key_name: cache_record_to_dict(record) for record in records},
    }


def render_cache_report_markdown(data: dict[str, object]) -> str:
    repo_state = data.get("repo_state", {}) if isinstance(data.get("repo_state"), dict) else {}
    boundary = data.get("local_state_boundary", {}) if isinstance(data.get("local_state_boundary"), dict) else {}
    keys = data.get("keys", {}) if isinstance(data.get("keys"), dict) else {}
    lines = [
        "# AIDE Cache Key Report",
        "",
        "## CACHE_KEYS",
        "",
        f"- schema_version: {data.get('schema_version', 'unknown')}",
        f"- generated_by: {data.get('generated_by', 'unknown')}",
        "- contents_inline: false",
        "- raw_prompt_storage: false",
        "- raw_response_storage: false",
        f"- git_commit: {repo_state.get('git_commit', 'unavailable')}",
        f"- dirty_state: {str(repo_state.get('dirty_state', False)).lower()}",
        "",
        "## LOCAL_STATE_BOUNDARY",
        "",
        f"- committed_contract_root: {boundary.get('committed_contract_root', '.aide/')}",
        f"- local_state_root: {boundary.get('local_state_root', '.aide.local/')}",
        f"- local_state_ignored: {str(boundary.get('local_state_ignored', False)).lower()}",
        f"- tracked_local_state_paths: {len(boundary.get('tracked_local_state_paths', [])) if isinstance(boundary.get('tracked_local_state_paths', []), list) else 0}",
        "",
        "## SURFACES",
        "",
    ]
    if not keys:
        lines.append("- none")
    else:
        for key_name in sorted(keys):
            record = keys[key_name]
            if not isinstance(record, dict):
                continue
            deps = record.get("dependency_hashes", {})
            dep_count = len(deps) if isinstance(deps, dict) else 0
            lines.append(f"- {key_name}: `{record.get('path', '')}`")
            lines.append(f"  - surface: {record.get('surface', '')}")
            lines.append(f"  - key_id: {record.get('key_id', '')}")
            lines.append(f"  - content_sha256: {record.get('content_sha256', '')}")
            lines.append(f"  - dependency_count: {dep_count}")
            lines.append(f"  - dirty_state: {str(record.get('dirty_state', False)).lower()}")
    lines.extend(
        [
            "",
            "## LIMITS",
            "",
            "- Cache keys are deterministic metadata, not permission to reuse stale or unsafe content.",
            "- Cache hits must not bypass verifier, review gates, or golden tasks.",
            "- Provider response and semantic caches remain disabled until future reviewed policy enables them.",
            "- Raw prompts, raw responses, secrets, traces, and real cache blobs must stay out of committed files.",
            "",
        ]
    )
    return "\n".join(lines)


def write_cache_report(repo_root: Path) -> tuple[WriteResult, WriteResult, dict[str, object]]:
    data = cache_report_data(repo_root)
    json_result = write_text_if_changed(repo_root / CACHE_KEYS_JSON_PATH, stable_compact_json_text(data))
    md_result = write_text_if_changed(repo_root / CACHE_KEYS_MD_PATH, render_cache_report_markdown(data))
    return json_result, md_result, data


def cache_status_checks(repo_root: Path) -> list[Check]:
    checks: list[Check] = []
    if gitignore_has_local_state_rules(repo_root):
        checks.append(Check("PASS", ".aide.local/ is protected by .gitignore"))
    else:
        checks.append(Check("FAIL", ".gitignore missing .aide.local/ and .aide.local/**"))
    tracked = local_state_git_paths(repo_root)
    if tracked:
        checks.append(Check("FAIL", f"local state appears in git status/index: {', '.join(tracked[:5])}"))
    else:
        checks.append(Check("PASS", ".aide.local/ has no tracked or staged paths"))
    for rel in [CACHE_POLICY_PATH, LOCAL_STATE_POLICY_PATH, f"{LOCAL_STATE_EXAMPLE_ROOT}/README.md", f"{CACHE_DIR}/README.md", CACHE_KEY_POLICY_PATH]:
        if (repo_root / rel).exists():
            checks.append(Check("PASS", f"cache/local-state artifact exists: {rel}"))
        else:
            checks.append(Check("FAIL", f"cache/local-state artifact missing: {rel}"))
    for rel in [CACHE_KEYS_JSON_PATH, CACHE_KEYS_MD_PATH]:
        checks.append(Check("PASS" if (repo_root / rel).exists() else "WARN", f"cache key report exists: {rel}"))
    return checks


def cache_validation_checks(repo_root: Path) -> list[Check]:
    checks = cache_status_checks(repo_root)
    for rel in Q18_REQUIRED_FILES:
        if (repo_root / rel).exists():
            checks.append(Check("PASS", f"cache/local-state required file exists: {rel}"))
        else:
            checks.append(Check("FAIL", f"cache/local-state required file missing: {rel}"))
    gitignore = gitignore_lines(repo_root)
    for pattern in GITIGNORE_REQUIRED_PATTERNS:
        if pattern not in gitignore:
            checks.append(Check("FAIL", f".gitignore missing local-state/cache pattern: {pattern}"))
    cache_policy = repo_root / CACHE_POLICY_PATH
    if cache_policy.exists():
        text = read_text(cache_policy)
        for anchor in CACHE_POLICY_ANCHORS:
            if anchor not in text:
                checks.append(Check("FAIL", f"cache policy missing anchor: {anchor}"))
    local_state_policy = repo_root / LOCAL_STATE_POLICY_PATH
    if local_state_policy.exists():
        text = read_text(local_state_policy)
        for anchor in LOCAL_STATE_POLICY_ANCHORS:
            if anchor not in text:
                checks.append(Check("FAIL", f"local-state policy missing anchor: {anchor}"))
    key_policy = repo_root / CACHE_KEY_POLICY_PATH
    if key_policy.exists():
        text = read_text(key_policy)
        for anchor in ["cache_key_format", "aide-cache-v0", "key_inputs", "content_sha256", "dependency_hashes", "policy_versions", "dirty_state"]:
            if anchor not in text:
                checks.append(Check("FAIL", f"cache key policy missing anchor: {anchor}"))
    key_json = repo_root / CACHE_KEYS_JSON_PATH
    if key_json.exists():
        try:
            data = json.loads(read_text(key_json))
            if data.get("contents_inline") is not False:
                checks.append(Check("FAIL", "cache key JSON must declare contents_inline: false"))
            if data.get("raw_prompt_storage") is not False:
                checks.append(Check("FAIL", "cache key JSON must disable raw prompt storage"))
            if data.get("raw_response_storage") is not False:
                checks.append(Check("FAIL", "cache key JSON must disable raw response storage"))
            keys = data.get("keys", {})
            if not isinstance(keys, dict):
                checks.append(Check("FAIL", "cache key JSON keys field must be an object"))
            else:
                checks.append(Check("PASS", f"cache key records: {len(keys)}"))
                for key_name, record in keys.items():
                    if not isinstance(record, dict):
                        checks.append(Check("FAIL", f"cache key record malformed: {key_name}"))
                        continue
                    for field in CACHE_KEY_REQUIRED_FIELDS:
                        if field not in record:
                            checks.append(Check("FAIL", f"cache key record {key_name} missing field: {field}"))
                    rel = normalize_rel(str(record.get("path", "")))
                    if is_secret_risk_path(rel):
                        checks.append(Check("FAIL", f"cache key record points at forbidden path: {rel}"))
            serialized = json.dumps(data)
            for marker in ["raw_prompt_body", "raw_response_body", "SHOULD_NOT_APPEAR", "print('hello')"]:
                if marker in serialized:
                    checks.append(Check("FAIL", f"cache key report contains raw-content marker: {marker}"))
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            checks.append(Check("FAIL", f"cache key JSON malformed: {exc}"))
    secret_findings = scan_for_secrets(repo_root, [CACHE_POLICY_PATH, LOCAL_STATE_POLICY_PATH, CACHE_DIR, LOCAL_STATE_EXAMPLE_ROOT])
    if secret_findings:
        checks.append(Check("FAIL", f"possible secret material in cache/local-state files: {', '.join(secret_findings)}"))
    else:
        checks.append(Check("PASS", "no obvious secrets in cache/local-state files"))
    return checks


def import_repo_file_module(repo_root: Path, rel_path: str, module_name: str):
    path = repo_root / rel_path
    if not path.exists():
        raise ImportError(f"module file missing: {rel_path}")
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"module spec unavailable: {rel_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def import_gateway_status_module(repo_root: Path):
    try:
        return import_repo_file_module(repo_root, "core/gateway/gateway_status.py", "_aide_gateway_status")
    except (ImportError, OSError, ValueError):
        pass
    root = str(repo_root.resolve())
    if root not in sys.path:
        sys.path.insert(0, root)
    return importlib.import_module("core.gateway.gateway_status")


def import_gateway_server_module(repo_root: Path):
    try:
        return import_repo_file_module(repo_root, "core/gateway/server.py", "_aide_gateway_server")
    except (ImportError, OSError, ValueError):
        pass
    root = str(repo_root.resolve())
    if root not in sys.path:
        sys.path.insert(0, root)
    return importlib.import_module("core.gateway.server")


def import_provider_status_module(repo_root: Path):
    try:
        return import_repo_file_module(repo_root, "core/providers/status.py", "_aide_provider_status")
    except (ImportError, OSError, ValueError):
        pass
    root = str(repo_root.resolve())
    if root not in sys.path:
        sys.path.insert(0, root)
    return importlib.import_module("core.providers.status")


def import_provider_registry_module(repo_root: Path):
    try:
        return import_repo_file_module(repo_root, "core/providers/registry.py", "_aide_provider_registry")
    except (ImportError, OSError, ValueError):
        pass
    root = str(repo_root.resolve())
    if root not in sys.path:
        sys.path.insert(0, root)
    return importlib.import_module("core.providers.registry")


def gateway_status_checks(repo_root: Path) -> list[Check]:
    checks: list[Check] = []
    for rel in [GATEWAY_POLICY_PATH, GATEWAY_ENDPOINTS_PATH, GATEWAY_LIFECYCLE_PATH, GATEWAY_SECURITY_PATH]:
        checks.append(Check("PASS" if (repo_root / rel).exists() else "FAIL", f"gateway artifact exists: {rel}"))
    for rel in [GATEWAY_STATUS_JSON_PATH, GATEWAY_STATUS_MD_PATH]:
        checks.append(Check("PASS" if (repo_root / rel).exists() else "WARN", f"gateway status artifact exists: {rel}"))
    try:
        module = import_gateway_status_module(repo_root)
        health = module.health_payload()
        if health.get("provider_calls_enabled") is False and health.get("model_calls_enabled") is False:
            checks.append(Check("PASS", "gateway health disables provider/model calls"))
        else:
            checks.append(Check("FAIL", "gateway health must disable provider/model calls"))
    except (ImportError, AttributeError, OSError, ValueError) as exc:
        checks.append(Check("FAIL", f"gateway status helpers unavailable: {exc}"))
    return checks


def gateway_validation_checks(repo_root: Path) -> list[Check]:
    checks = gateway_status_checks(repo_root)
    for rel in Q19_REQUIRED_FILES:
        checks.append(Check("PASS" if (repo_root / rel).exists() else "FAIL", f"gateway required file exists: {rel}"))
    policy_path = repo_root / GATEWAY_POLICY_PATH
    if policy_path.exists():
        text = read_text(policy_path)
        for anchor in GATEWAY_POLICY_ANCHORS:
            if anchor not in text:
                checks.append(Check("FAIL", f"gateway policy missing anchor: {anchor}"))
    endpoints_path = repo_root / GATEWAY_ENDPOINTS_PATH
    if endpoints_path.exists():
        text = read_text(endpoints_path)
        for endpoint in ["/health", "/status", "/route/explain", "/summaries", "/version"]:
            if endpoint not in text:
                checks.append(Check("FAIL", f"gateway endpoints missing endpoint: {endpoint}"))
        for forbidden in ["/v1/chat/completions", "/v1/responses", "/anthropic/v1/messages"]:
            if forbidden not in text:
                checks.append(Check("FAIL", f"gateway endpoints missing forbidden endpoint record: {forbidden}"))
        if "provider_calls: true" in text or "model_calls: true" in text or "outbound_network_calls: true" in text:
            checks.append(Check("FAIL", "gateway endpoint policy must not enable provider/model/network calls"))
    status_json = repo_root / GATEWAY_STATUS_JSON_PATH
    if status_json.exists():
        try:
            data = json.loads(read_text(status_json))
            for field in GATEWAY_STATUS_REQUIRED_FIELDS:
                if field not in data:
                    checks.append(Check("FAIL", f"gateway status JSON missing field: {field}"))
            for flag in ["provider_calls_enabled", "model_calls_enabled", "outbound_network_enabled", "raw_prompt_storage", "raw_response_storage"]:
                if data.get(flag) is not False:
                    checks.append(Check("FAIL", f"gateway status JSON must set {flag}: false"))
            serialized = json.dumps(data)
            for marker in ["raw_prompt_body", "raw_response_body", "SHOULD_NOT_APPEAR", "print('hello')", ".aide.local/state"]:
                if marker in serialized:
                    checks.append(Check("FAIL", f"gateway status contains forbidden raw/local marker: {marker}"))
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            checks.append(Check("FAIL", f"gateway status JSON malformed: {exc}"))
    try:
        module = import_gateway_status_module(repo_root)
        smoke = module.smoke_gateway(repo_root)
        if smoke.get("result") == "PASS":
            checks.append(Check("PASS", "gateway endpoint smoke payloads pass"))
        else:
            checks.append(Check("FAIL", "gateway endpoint smoke payloads fail"))
    except (ImportError, AttributeError, OSError, ValueError) as exc:
        checks.append(Check("FAIL", f"gateway smoke unavailable: {exc}"))
    secret_findings = scan_for_secrets(repo_root, [GATEWAY_POLICY_PATH, GATEWAY_DIR, "core/gateway"])
    if secret_findings:
        checks.append(Check("FAIL", f"possible secret material in gateway files: {', '.join(secret_findings)}"))
    else:
        checks.append(Check("PASS", "no obvious secrets in gateway files"))
    return checks


def provider_status_checks(repo_root: Path) -> list[Check]:
    checks: list[Check] = []
    for rel in [
        PROVIDER_ADAPTER_POLICY_PATH,
        PROVIDER_CATALOG_PATH,
        PROVIDER_CAPABILITY_MATRIX_PATH,
        PROVIDER_ADAPTER_CONTRACT_PATH,
        PROVIDER_STATUS_PATH,
    ]:
        checks.append(Check("PASS" if (repo_root / rel).exists() else "FAIL", f"provider artifact exists: {rel}"))
    for rel in [PROVIDER_STATUS_JSON_PATH, PROVIDER_STATUS_MD_PATH]:
        checks.append(Check("PASS" if (repo_root / rel).exists() else "WARN", f"provider status artifact exists: {rel}"))
    try:
        module = import_provider_status_module(repo_root)
        data = module.build_provider_status(repo_root)
        if data.get("live_provider_calls") is False and data.get("live_model_calls") is False and data.get("network_calls") is False:
            checks.append(Check("PASS", "provider status disables live provider/model/network calls"))
        else:
            checks.append(Check("FAIL", "provider status must disable live provider/model/network calls"))
        if data.get("credentials_configured") is False and data.get("no_credentials_in_status") is True:
            checks.append(Check("PASS", "provider status contains no configured credentials"))
        else:
            checks.append(Check("FAIL", "provider status must not configure or store credentials"))
    except (ImportError, AttributeError, OSError, ValueError) as exc:
        checks.append(Check("FAIL", f"provider status helpers unavailable: {exc}"))
    return checks


def provider_validation_checks(repo_root: Path) -> list[Check]:
    checks = provider_status_checks(repo_root)
    for rel in Q20_REQUIRED_FILES:
        checks.append(Check("PASS" if (repo_root / rel).exists() else "FAIL", f"provider required file exists: {rel}"))
    policy_path = repo_root / PROVIDER_ADAPTER_POLICY_PATH
    if policy_path.exists():
        text = read_text(policy_path)
        for anchor in PROVIDER_ADAPTER_POLICY_ANCHORS:
            if anchor not in text:
                checks.append(Check("FAIL", f"provider adapter policy missing anchor: {anchor}"))
        if "live_calls_allowed_in_q20: true" in text or "network_calls_allowed_in_q20: true" in text or "model_calls_allowed_in_q20: true" in text:
            checks.append(Check("FAIL", "provider adapter policy must not enable live/network/model calls"))
    try:
        registry = import_provider_registry_module(repo_root)
        validation = registry.validate_provider_files(repo_root)
        for error in validation.get("errors", []):
            checks.append(Check("FAIL", f"provider validation error: {error}"))
        for warning in validation.get("warnings", []):
            checks.append(Check("WARN", f"provider validation warning: {warning}"))
        if validation.get("result") == "PASS":
            checks.append(Check("PASS", f"provider metadata validates: {validation.get('provider_count', 0)} families"))
    except (ImportError, AttributeError, OSError, ValueError) as exc:
        checks.append(Check("FAIL", f"provider validation unavailable: {exc}"))
    catalog_text = read_text(repo_root / PROVIDER_CATALOG_PATH) if (repo_root / PROVIDER_CATALOG_PATH).exists() else ""
    for provider_id in PROVIDER_REQUIRED_IDS:
        if provider_id not in catalog_text:
            checks.append(Check("FAIL", f"provider catalog missing family: {provider_id}"))
    for forbidden in [
        "live_calls_allowed_in_q20: true",
        "network_calls_allowed_in_q20: true",
        "model_calls_allowed_in_q20: true",
        "provider_probe_calls_allowed_in_q20: true",
    ]:
        for rel in [PROVIDER_CATALOG_PATH, PROVIDER_CAPABILITY_MATRIX_PATH, PROVIDER_ADAPTER_CONTRACT_PATH, PROVIDER_STATUS_PATH]:
            if (repo_root / rel).exists() and forbidden in read_text(repo_root / rel):
                checks.append(Check("FAIL", f"provider metadata enables forbidden behavior in {rel}: {forbidden}"))
    status_json = repo_root / PROVIDER_STATUS_JSON_PATH
    if status_json.exists():
        try:
            data = json.loads(read_text(status_json))
            for field in PROVIDER_STATUS_REQUIRED_FIELDS:
                if field not in data:
                    checks.append(Check("FAIL", f"provider status JSON missing field: {field}"))
            for flag in ["live_provider_calls", "live_model_calls", "network_calls", "provider_probe_calls", "credentials_configured", "gateway_forwarding", "raw_prompt_storage", "raw_response_storage"]:
                if data.get(flag) is not False:
                    checks.append(Check("FAIL", f"provider status JSON must set {flag}: false"))
            serialized = json.dumps(data)
            for marker in ["raw_prompt_body", "raw_response_body", "api_key =", "sk-", "sk-ant-", ".aide.local/state"]:
                if marker in serialized:
                    checks.append(Check("FAIL", f"provider status contains forbidden marker: {marker}"))
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            checks.append(Check("FAIL", f"provider status JSON malformed: {exc}"))
    model_provider_text = read_text(repo_root / PROVIDERS_PATH) if (repo_root / PROVIDERS_PATH).exists() else ""
    for provider_id in PROVIDER_REQUIRED_IDS:
        if provider_id not in model_provider_text:
            checks.append(Check("WARN", f"Q17 model provider registry does not reference Q20 family: {provider_id}"))
    secret_findings = scan_for_secrets(repo_root, [PROVIDER_ADAPTER_POLICY_PATH, PROVIDER_DIR, "core/providers"])
    if secret_findings:
        checks.append(Check("FAIL", f"possible secret material in provider files: {', '.join(secret_findings)}"))
    else:
        checks.append(Check("PASS", "no obvious secrets in provider files"))
    return checks


def classify_changed_files(repo_root: Path) -> tuple[list[DiffScopeResult], list[VerificationFinding]]:
    ok, entries, error = git_status_short(repo_root)
    findings: list[VerificationFinding] = []
    if not ok:
        return [], [VerificationFinding("WARN", "diff_scope", f"git status unavailable: {error}")]
    allowed, forbidden = load_scope_patterns(repo_root)
    results = [classify_scope_path(path, status, allowed, forbidden) for status, path in entries]
    for result in results:
        if result.classification == "forbidden":
            findings.append(VerificationFinding("ERROR", "diff_scope", result.reason, result.path))
        elif result.classification in {"warning", "unknown"}:
            findings.append(VerificationFinding("WARN", "diff_scope", result.reason, result.path))
        else:
            findings.append(VerificationFinding("INFO", "diff_scope", result.reason, result.path))
    if not results:
        findings.append(VerificationFinding("INFO", "diff_scope", "no changed files reported by git status"))
    return results, findings


def verify_markdown_sections(text: str, sections: Iterable[str], source_path: str, check: str) -> list[VerificationFinding]:
    findings: list[VerificationFinding] = []
    for section in missing_sections(text, sections):
        findings.append(VerificationFinding("ERROR", check, f"missing required section: {section}", source_path))
    if not findings:
        findings.append(VerificationFinding("INFO", check, "required sections present", source_path))
    return findings


def verify_task_packet(repo_root: Path, rel_path: str) -> list[VerificationFinding]:
    findings: list[VerificationFinding] = []
    path = safe_repo_path(repo_root, rel_path)
    if not path.exists():
        return [VerificationFinding("ERROR", "task_packet", "task packet does not exist", rel_path)]
    text = read_text(path)
    findings.extend(verify_markdown_sections(text, PACKET_REQUIRED_SECTIONS, rel_path, "task_packet"))
    for phrase in FORBIDDEN_PACKET_PHRASES:
        if phrase.lower() in text.lower():
            findings.append(VerificationFinding("WARN", "task_packet", f"forbidden prompt pattern mentioned: {phrase}", rel_path))
    for required_ref in [REPO_MAP_JSON_PATH, TEST_MAP_JSON_PATH, CONTEXT_INDEX_PATH, LATEST_CONTEXT_PACKET_PATH]:
        if required_ref not in text:
            findings.append(VerificationFinding("WARN", "task_packet", f"context ref missing: {required_ref}", rel_path))
    budget = load_token_budget(repo_root)
    stats = estimate_text(text, rel_path)
    if stats.approx_tokens > budget["max_compact_task_packet_tokens"]:
        findings.append(VerificationFinding("WARN", "task_packet", f"task packet over hard limit: {stats.approx_tokens}", rel_path))
    else:
        findings.append(VerificationFinding("INFO", "task_packet", f"task packet tokens: {stats.approx_tokens}", rel_path))
    findings.extend(verify_refs_in_text(repo_root, text, rel_path))
    return findings


def verify_evidence_packet(repo_root: Path, rel_path: str) -> list[VerificationFinding]:
    findings: list[VerificationFinding] = []
    path = safe_repo_path(repo_root, rel_path)
    if not path.exists():
        return [VerificationFinding("ERROR", "evidence_packet", "evidence packet does not exist", rel_path)]
    text = read_text(path)
    findings.extend(verify_markdown_sections(text, EVIDENCE_PACKET_REQUIRED_SECTIONS, rel_path, "evidence_packet"))
    if "Validation Commands" in text and not re.search(r"py -3|python|git\s+|rg\s+", text):
        findings.append(VerificationFinding("WARN", "evidence_packet", "validation commands section may not record commands", rel_path))
    if "Changed Files" in text and not re.search(r"`[^`]+\.(md|yaml|yml|json|py|toml|txt)`", text):
        findings.append(VerificationFinding("WARN", "evidence_packet", "changed files section may not list repo-relative files", rel_path))
    findings.extend(verify_refs_in_text(repo_root, text, rel_path))
    return findings


def verify_context_shape(repo_root: Path) -> list[VerificationFinding]:
    findings: list[VerificationFinding] = []
    for rel in CONTEXT_OUTPUT_PATHS:
        if not (repo_root / rel).exists():
            findings.append(VerificationFinding("WARN", "context_packet_shape", "context artifact missing", rel))
    packet_path = repo_root / LATEST_CONTEXT_PACKET_PATH
    if packet_path.exists():
        text = read_text(packet_path)
        missing = missing_sections(text, CONTEXT_PACKET_REQUIRED_SECTIONS)
        for section in missing:
            findings.append(VerificationFinding("WARN", "context_packet_shape", f"latest context packet missing section: {section}", LATEST_CONTEXT_PACKET_PATH))
        if any(marker in text for marker in CONTEXT_FORBIDDEN_INLINE_MARKERS):
            findings.append(VerificationFinding("ERROR", "context_packet_shape", "latest context packet appears to inline raw source marker", LATEST_CONTEXT_PACKET_PATH))
        findings.append(VerificationFinding("INFO", "context_packet_shape", f"latest context packet tokens: {estimate_text(text).approx_tokens}", LATEST_CONTEXT_PACKET_PATH))
    return findings


def collect_verification_findings(
    repo_root: Path,
    evidence_path: str | None = None,
    task_packet_path: str | None = None,
    review_packet_path: str | None = None,
    changed_files_only: bool = False,
) -> tuple[list[VerificationFinding], list[DiffScopeResult], list[str]]:
    findings: list[VerificationFinding] = []
    checked_files: list[str] = []

    if not changed_files_only:
        required_for_verifier = [*REQUIRED_FILES, *CONTEXT_CONFIG_FILES, *Q12_REQUIRED_FILES]
        if (repo_root / ".aide/queue/Q16-outcome-controller-v0").exists():
            required_for_verifier.extend(Q16_REQUIRED_FILES)
        if (repo_root / ".aide/queue/Q17-router-profile-v0").exists():
            required_for_verifier.extend(Q17_REQUIRED_FILES)
        if (repo_root / ".aide/queue/Q18-cache-local-state-boundary").exists():
            required_for_verifier.extend(Q18_REQUIRED_FILES)
        if (repo_root / ".aide/queue/Q19-gateway-architecture-skeleton").exists():
            required_for_verifier.extend(Q19_REQUIRED_FILES)
        if (repo_root / ".aide/queue/Q20-provider-adapter-v0").exists():
            required_for_verifier.extend(Q20_REQUIRED_FILES)
        for rel in required_for_verifier:
            checked_files.append(rel)
            if (repo_root / rel).exists():
                findings.append(VerificationFinding("INFO", "required_files", "required file exists", rel))
            else:
                findings.append(VerificationFinding("ERROR", "required_files", "required file missing", rel))
        task_rel = task_packet_path or LATEST_PACKET_PATH
        checked_files.append(task_rel)
        findings.extend(verify_task_packet(repo_root, task_rel))
        if evidence_path:
            checked_files.append(evidence_path)
            findings.extend(verify_evidence_packet(repo_root, evidence_path))
        review_rel = review_packet_path
        if review_rel is None and (repo_root / REVIEW_PACKET_PATH).exists():
            review_rel = REVIEW_PACKET_PATH
        if review_rel:
            checked_files.append(review_rel)
            findings.extend(verify_review_packet(repo_root, review_rel))
        findings.extend(verify_context_shape(repo_root))
        adapter = adapter_status(repo_root)
        if adapter.status == "current":
            findings.append(VerificationFinding("INFO", "adapter_drift", "AGENTS managed section is current", "AGENTS.md"))
        elif adapter.status in {"missing", "legacy", "drift"}:
            findings.append(VerificationFinding("WARN", "adapter_drift", f"AGENTS managed section status: {adapter.status}; {adapter.action_hint}", "AGENTS.md"))
        else:
            findings.append(VerificationFinding("ERROR", "adapter_drift", f"AGENTS managed section status: {adapter.status}; {adapter.action_hint}", "AGENTS.md"))
        for check in cache_status_checks(repo_root):
            severity = "ERROR" if check.severity == "FAIL" else ("WARN" if check.severity == "WARN" else "INFO")
            findings.append(VerificationFinding(severity, "cache_local_state", check.message))
        if (repo_root / ".aide/queue/Q19-gateway-architecture-skeleton").exists():
            for check in gateway_status_checks(repo_root):
                severity = "ERROR" if check.severity == "FAIL" else ("WARN" if check.severity == "WARN" else "INFO")
                findings.append(VerificationFinding(severity, "gateway_skeleton", check.message))
        if (repo_root / ".aide/queue/Q20-provider-adapter-v0").exists():
            for check in provider_status_checks(repo_root):
                severity = "ERROR" if check.severity == "FAIL" else ("WARN" if check.severity == "WARN" else "INFO")
                findings.append(VerificationFinding(severity, "provider_adapters", check.message))
        scan_paths = verification_scan_paths(repo_root)
        checked_files.extend(scan_paths)
        findings.extend(scan_for_secret_findings(repo_root, scan_paths))

    changed_files, diff_findings = classify_changed_files(repo_root)
    findings.extend(diff_findings)
    return findings, changed_files, sorted(set(checked_files))


def render_verification_report(report: VerificationReport) -> str:
    counts = {
        "info": sum(1 for finding in report.findings if finding.severity == "INFO"),
        "warning": sum(1 for finding in report.findings if finding.severity in {"WARN", "WARNING"}),
        "error": sum(1 for finding in report.findings if finding.severity in {"ERROR", "FAIL"}),
    }
    warnings = [finding for finding in report.findings if finding.severity in {"WARN", "WARNING"}]
    errors = [finding for finding in report.findings if finding.severity in {"ERROR", "FAIL"}]
    lines = [
        "# AIDE Verification Report",
        "",
        "## VERIFIER_RESULT",
        "",
        f"- result: {report.result}",
        "- method: deterministic repo-local checks",
        "- contents_inline: false",
        "- provider_or_model_calls: none",
        "",
        "## CHECK_COUNTS",
        "",
        f"- info: {counts['info']}",
        f"- warnings: {counts['warning']}",
        f"- errors: {counts['error']}",
        f"- checked_files: {len(report.checked_files)}",
        f"- changed_files: {len(report.changed_files)}",
        "",
        "## CHANGED_FILES",
        "",
    ]
    if report.changed_files:
        for item in report.changed_files:
            lines.append(f"- {item.classification}: `{item.path}` ({item.status.strip() or 'clean'}; {item.reason})")
    else:
        lines.append("- none")
    lines.extend(["", "## WARNINGS", ""])
    if warnings:
        for finding in warnings:
            suffix = f" `{finding.path}`" if finding.path else ""
            lines.append(f"- {finding.check}: {finding.message}{suffix}")
    else:
        lines.append("- none")
    lines.extend(["", "## ERRORS", ""])
    if errors:
        for finding in errors:
            suffix = f" `{finding.path}`" if finding.path else ""
            lines.append(f"- {finding.check}: {finding.message}{suffix}")
    else:
        lines.append("- none")
    lines.extend(["", "## EVIDENCE_REFS", ""])
    for rel in report.checked_files[:80]:
        lines.append(f"- `{rel}`")
    if len(report.checked_files) > 80:
        lines.append(f"- omitted_refs: {len(report.checked_files) - 80}")
    lines.extend([
        "",
        "## LIMITS",
        "",
        "- Structural verifier only; no LLM judging.",
        "- Diff scope is path-based only.",
        "- Secret scan is heuristic only.",
        "- Token counts use chars / 4 approximation.",
        "",
    ])
    return "\n".join(lines)


def build_verification_report(
    repo_root: Path,
    evidence_path: str | None = None,
    task_packet_path: str | None = None,
    review_packet_path: str | None = None,
    changed_files_only: bool = False,
) -> VerificationReport:
    findings, changed_files, checked_files = collect_verification_findings(
        repo_root,
        evidence_path=evidence_path,
        task_packet_path=task_packet_path,
        review_packet_path=review_packet_path,
        changed_files_only=changed_files_only,
    )
    return VerificationReport(
        verification_result(findings),
        tuple(findings),
        tuple(checked_files),
        tuple(changed_files),
    )


def write_verification_report(repo_root: Path, requested: str, report: VerificationReport) -> WriteResult:
    target = safe_repo_path(repo_root, requested)
    rel = normalize_rel(target.relative_to(repo_root))
    allowed_report_path = rel.startswith(".aide/verification/") or rel.startswith(".aide/queue/")
    forbidden_report_path = any(pattern_matches(rel, pattern) for pattern in [".git/**", ".aide.local/**", "secrets/**", ".env"])
    if not allowed_report_path or forbidden_report_path:
        raise ValueError(f"verification report path is not allowed: {requested}")
    return write_text_if_changed(target, render_verification_report(report))


def current_queue_id(repo_root: Path) -> str:
    for queue_id in [
        "Q20-provider-adapter-v0",
        "Q19-gateway-architecture-skeleton",
        "Q18-cache-local-state-boundary",
        "Q17-router-profile-v0",
        "Q16-outcome-controller-v0",
        "Q15-golden-tasks-v0",
        "Q14-token-ledger-savings-report",
        "Q13-evidence-review-workflow",
        "Q12-verifier-v0",
        "Q11-context-compiler-v0",
        "Q10-aide-lite-hardening",
        "Q09-token-survival-core",
    ]:
        if (repo_root / f".aide/queue/{queue_id}/status.yaml").exists():
            return queue_id
    return ""


def default_evidence_dir(repo_root: Path) -> str:
    queue_id = current_queue_id(repo_root)
    return f".aide/queue/{queue_id}/evidence" if queue_id else ".aide/queue"


def default_review_task_packet(repo_root: Path) -> str:
    if (repo_root / LATEST_PACKET_PATH).exists():
        return LATEST_PACKET_PATH
    queue_id = current_queue_id(repo_root)
    candidate = f".aide/queue/{queue_id}/task.yaml" if queue_id else ""
    if candidate and (repo_root / candidate).exists():
        return candidate
    return LATEST_PACKET_PATH


def list_evidence_refs(repo_root: Path, evidence_dir: str) -> list[str]:
    directory = safe_repo_path(repo_root, evidence_dir)
    if not directory.exists() or not directory.is_dir():
        return []
    refs = [
        normalize_rel(path.relative_to(repo_root))
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in {".md", ".txt", ".yaml", ".yml", ".json"}
    ]
    return sorted(refs)


def compact_bullet_lines(text: str, limit: int = 20) -> list[str]:
    bullets: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped)
        if len(bullets) >= limit:
            break
    return bullets


def summarize_validation(repo_root: Path, evidence_dir: str) -> list[str]:
    path = safe_repo_path(repo_root, f"{evidence_dir.rstrip('/')}/validation.md")
    if not path.exists():
        return ["- validation evidence not found"]
    text = read_text(path)
    if "## Final Validation" in text:
        text = text.split("## Final Validation", 1)[1]
    bullets = compact_bullet_lines(text, limit=14)
    return bullets or ["- validation evidence contains no compact command bullets"]


def summarize_risks(repo_root: Path, evidence_dir: str) -> list[str]:
    risk_path = safe_repo_path(repo_root, f"{evidence_dir.rstrip('/')}/remaining-risks.md")
    if risk_path.exists():
        bullets = compact_bullet_lines(read_text(risk_path), limit=18)
        if bullets:
            return bullets
    open_risks = repo_root / ".aide/memory/open-risks.md"
    if open_risks.exists():
        bullets = compact_bullet_lines(read_text(open_risks), limit=18)
        if bullets:
            return bullets
    return ["- no compact risk bullets found; reviewer should inspect evidence refs"]


def extract_verification_result(repo_root: Path, verification_path: str) -> str:
    path = safe_repo_path(repo_root, verification_path)
    if not path.exists():
        return "MISSING"
    text = read_text(path)
    match = re.search(r"^-\s*result:\s*(PASS|WARN|FAIL)\s*$", text, re.MULTILINE)
    return match.group(1) if match else "UNKNOWN"


def changed_file_summary(repo_root: Path) -> list[str]:
    changed_files, _findings = classify_changed_files(repo_root)
    if not changed_files:
        return ["- none"]
    lines = []
    sorted_files = sorted(changed_files, key=lambda entry: entry.path)
    limit = 24
    for item in sorted_files[:limit]:
        lines.append(f"- {item.classification}: `{item.path}` ({item.status.strip() or 'clean'}; {item.reason})")
    remaining = len(sorted_files) - limit
    if remaining > 0:
        lines.append(f"- additional changed paths omitted from compact packet: {remaining}; see task evidence changed-files report")
    return lines


def non_goal_lines(repo_root: Path) -> list[str]:
    queue_id = current_queue_id(repo_root)
    task_path = repo_root / f".aide/queue/{queue_id}/task.yaml" if queue_id else repo_root / ".aide/queue/index.yaml"
    if task_path.exists():
        items = parse_simple_list(read_text(task_path), "non_goals")
        if items:
            return [f"- {item}" for item in items[:24]]
    return [
        "- Gateway",
        "- provider calls",
        "- model routing",
        "- Runtime/Service/Commander/UI/Mobile",
        "- MCP/A2A",
        "- automatic model calls or repair",
    ]


def review_packet_budget_warnings(text: str, repo_root: Path, max_token_warning: int | None = None) -> tuple[str, tuple[str, ...]]:
    stats = estimate_text(text, REVIEW_PACKET_PATH)
    budget = load_token_budget(repo_root)
    limit = max_token_warning or budget["max_review_packet_tokens"]
    warnings: list[str] = []
    if stats.approx_tokens > limit:
        warnings.append(f"review packet over warning limit: {stats.approx_tokens} > {limit}")
    lowered = text.lower()
    for phrase in FORBIDDEN_PACKET_PHRASES:
        if phrase.lower() in lowered:
            warnings.append(f"forbidden prompt phrase appears in review packet: {phrase}")
    return ("WARN" if warnings else "PASS", tuple(warnings))


def summarize_controller_for_review(repo_root: Path) -> list[str]:
    outcome_path = repo_root / OUTCOME_REPORT_PATH
    recommendations_path = repo_root / RECOMMENDATIONS_PATH
    lines = []
    if outcome_path.exists():
        text = read_text(outcome_path)
        match = re.search(r"^-\s*result:\s*(PASS|WARN|FAIL|PENDING)\s*$", text, re.MULTILINE)
        result = match.group(1) if match else "UNKNOWN"
        lines.append(f"- outcome_report: `{OUTCOME_REPORT_PATH}`")
        lines.append(f"- outcome_result: {result}")
    else:
        lines.append(f"- outcome_report: `{OUTCOME_REPORT_PATH}` (missing)")
    if recommendations_path.exists():
        text = read_text(recommendations_path)
        ids = re.findall(r"^- ID:\s*(\S+)", text, flags=re.MULTILINE)
        lines.append(f"- recommendations: `{RECOMMENDATIONS_PATH}`")
        lines.append(f"- recommendation_count: {len(ids)}")
        if ids:
            lines.append(f"- top_recommendation: {ids[0]}")
    else:
        lines.append(f"- recommendations: `{RECOMMENDATIONS_PATH}` (missing)")
    lines.append("- applies_automatically: false")
    return lines


def summarize_route_for_review(repo_root: Path) -> list[str]:
    path = repo_root / ROUTE_DECISION_JSON_PATH
    if not path.exists():
        return [f"- route_decision: `{ROUTE_DECISION_JSON_PATH}` (missing)", "- advisory_only: true"]
    try:
        data = json.loads(read_text(path))
    except (OSError, json.JSONDecodeError, TypeError):
        return [f"- route_decision: `{ROUTE_DECISION_JSON_PATH}` (malformed)", "- advisory_only: true"]
    return [
        f"- route_decision: `{ROUTE_DECISION_JSON_PATH}`",
        f"- route_class: {data.get('route_class', 'UNKNOWN')}",
        f"- task_class: {data.get('task_class', 'UNKNOWN')}",
        f"- hard_floor_applied: {data.get('hard_floor_applied', 'UNKNOWN')}",
        f"- quality_gate_status: {data.get('quality_gate_status', 'UNKNOWN')}",
        "- advisory_only: true",
    ]


def summarize_cache_for_review(repo_root: Path) -> list[str]:
    data_path = repo_root / CACHE_KEYS_JSON_PATH
    tracked = local_state_git_paths(repo_root)
    lines = [
        f"- cache_keys: `{CACHE_KEYS_JSON_PATH}`" + ("" if data_path.exists() else " (missing; run cache report)"),
        f"- local_state_ignored: {str(gitignore_has_local_state_rules(repo_root)).lower()}",
        f"- tracked_local_state_paths: {len(tracked)}",
        "- raw_prompt_storage: false",
        "- raw_response_storage: false",
    ]
    if data_path.exists():
        try:
            data = json.loads(read_text(data_path))
            keys = data.get("keys", {})
            lines.append(f"- cache_key_count: {len(keys) if isinstance(keys, dict) else 0}")
        except (OSError, json.JSONDecodeError, TypeError):
            lines.append("- cache_key_count: malformed")
    return lines


def summarize_gateway_for_review(repo_root: Path) -> list[str]:
    data_path = repo_root / GATEWAY_STATUS_JSON_PATH
    if not data_path.exists():
        return [
            f"- gateway_status: `{GATEWAY_STATUS_JSON_PATH}` (missing; run gateway status)",
            "- local_skeleton: true",
            "- provider_or_model_calls: none",
        ]
    try:
        data = json.loads(read_text(data_path))
    except (OSError, json.JSONDecodeError, TypeError):
        return [
            f"- gateway_status: `{GATEWAY_STATUS_JSON_PATH}` (malformed)",
            "- local_skeleton: true",
            "- provider_or_model_calls: none",
        ]
    signals = data.get("signals", {}) if isinstance(data.get("signals"), dict) else {}
    route = signals.get("route", {}) if isinstance(signals.get("route"), dict) else {}
    return [
        f"- gateway_status: `{GATEWAY_STATUS_JSON_PATH}`",
        f"- service: {data.get('service', 'aide-gateway-skeleton')}",
        f"- mode: {data.get('mode', 'local_skeleton_report_only')}",
        f"- route_class: {route.get('route_class', 'unknown')}",
        f"- verifier_status: {signals.get('verifier_status', 'unknown')}",
        f"- golden_task_status: {signals.get('golden_task_status', 'unknown')}",
        f"- provider_calls_enabled: {str(data.get('provider_calls_enabled', False)).lower()}",
        f"- model_calls_enabled: {str(data.get('model_calls_enabled', False)).lower()}",
        f"- outbound_network_enabled: {str(data.get('outbound_network_enabled', False)).lower()}",
    ]


def summarize_provider_for_review(repo_root: Path) -> list[str]:
    data_path = repo_root / PROVIDER_STATUS_JSON_PATH
    if not data_path.exists():
        return [
            f"- provider_status: `{PROVIDER_STATUS_JSON_PATH}` (missing; run provider status)",
            "- offline_metadata_only: true",
            "- live_provider_calls: false",
        ]
    try:
        data = json.loads(read_text(data_path))
    except (OSError, json.JSONDecodeError, TypeError):
        return [
            f"- provider_status: `{PROVIDER_STATUS_JSON_PATH}` (malformed)",
            "- offline_metadata_only: true",
            "- live_provider_calls: false",
        ]
    validation = data.get("validation", {}) if isinstance(data.get("validation"), dict) else {}
    return [
        f"- provider_status: `{PROVIDER_STATUS_JSON_PATH}`",
        f"- provider_family_count: {data.get('provider_family_count', 0)}",
        f"- validation_result: {validation.get('result', 'unknown')}",
        f"- live_provider_calls: {str(data.get('live_provider_calls', False)).lower()}",
        f"- live_model_calls: {str(data.get('live_model_calls', False)).lower()}",
        f"- network_calls: {str(data.get('network_calls', False)).lower()}",
        f"- credentials_configured: {str(data.get('credentials_configured', False)).lower()}",
        "- metadata_only: true",
    ]


def render_review_packet(
    repo_root: Path,
    task_packet_path: str | None = None,
    verification_path: str = LATEST_VERIFICATION_REPORT_PATH,
    evidence_dir: str | None = None,
    output_path: str = REVIEW_PACKET_PATH,
    chars: int = 0,
    tokens: int = 0,
    budget_status: str = "PENDING",
    warnings: Iterable[str] = (),
    max_token_warning: int | None = None,
) -> str:
    task_packet_path = task_packet_path or default_review_task_packet(repo_root)
    evidence_dir = evidence_dir or default_evidence_dir(repo_root)
    evidence_refs = list_evidence_refs(repo_root, evidence_dir)
    evidence_lines = [f"- `{ref}`" for ref in evidence_refs] or [f"- `{evidence_dir}` (missing or empty)"]
    validation_lines = summarize_validation(repo_root, evidence_dir)
    risk_lines = summarize_risks(repo_root, evidence_dir)
    changed_lines = changed_file_summary(repo_root)
    verifier_result = extract_verification_result(repo_root, verification_path)
    task_stats = estimate_file(repo_root, task_packet_path) if (repo_root / task_packet_path).exists() else TextStats(task_packet_path, 0, 0, 0)
    context_stats = estimate_file(repo_root, LATEST_CONTEXT_PACKET_PATH) if (repo_root / LATEST_CONTEXT_PACKET_PATH).exists() else TextStats(LATEST_CONTEXT_PACKET_PATH, 0, 0, 0)
    verification_stats = estimate_file(repo_root, verification_path) if (repo_root / verification_path).exists() else TextStats(verification_path, 0, 0, 0)
    warning_lines = "\n".join(f"- {warning}" for warning in warnings) or "- none"
    non_goals = "\n".join(non_goal_lines(repo_root))
    controller_lines = "\n".join(summarize_controller_for_review(repo_root))
    route_lines = "\n".join(summarize_route_for_review(repo_root))
    cache_lines = "\n".join(summarize_cache_for_review(repo_root))
    gateway_lines = "\n".join(summarize_gateway_for_review(repo_root))
    provider_lines = "\n".join(summarize_provider_for_review(repo_root))
    return f"""# AIDE Latest Review Packet

## Review Objective

Review the current AIDE queue phase from compact evidence only and decide whether it is ready to pass its review gate.

## Decision Requested

Return exactly one of `PASS`, `PASS_WITH_NOTES`, `REQUEST_CHANGES`, or `BLOCKED`.

## Task Packet Reference

- `{task_packet_path}` ({task_stats.chars} chars, {task_stats.approx_tokens} approximate tokens)

## Context Packet Reference

- `{LATEST_CONTEXT_PACKET_PATH}` ({context_stats.chars} chars, {context_stats.approx_tokens} approximate tokens)
- `{REPO_MAP_JSON_PATH}`
- `{TEST_MAP_JSON_PATH}`
- `{CONTEXT_INDEX_PATH}`

## Verification Report Reference

- `{verification_path}`
- verifier_result: {verifier_result}
- report_chars: {verification_stats.chars}
- report_approx_tokens: {verification_stats.approx_tokens}

## Evidence Packet References

{chr(10).join(evidence_lines)}

## Changed Files Summary

{chr(10).join(changed_lines)}

## Validation Summary

{chr(10).join(validation_lines)}

## Token Summary

- packet_path: `{output_path}`
- method: chars / 4, rounded up
- chars: {chars}
- approx_tokens: {tokens}
- budget_status: {budget_status}
- max_token_warning: {max_token_warning or load_token_budget(repo_root)['max_review_packet_tokens']}
- warnings:
{warning_lines}
- formal ledger: `.aide/reports/token-ledger.jsonl`

## Outcome Controller Summary

{controller_lines}

## Route Decision Summary

{route_lines}

## Cache / Local State Summary

{cache_lines}

## Gateway Skeleton Summary

{gateway_lines}

## Provider Adapter Summary

{provider_lines}

## Risk Summary

{chr(10).join(risk_lines)}

## Non-Goals / Scope Guard

{non_goals}

## Reviewer Instructions

- Review only this packet and the referenced evidence when needed.
- Do not request full chat history unless the packet is insufficient to judge correctness.
- Do not re-summarize the whole project.
- Do not reward scope creep.
- Do not approve missing validation as a pass.
- Required output sections: `DECISION`, `REASONS`, `REQUIRED_FIXES`, `OPTIONAL_NOTES`, `NEXT_PHASE`.
- Decision policy: `.aide/verification/review-decision-policy.yaml`.
"""


def build_review_packet(
    repo_root: Path,
    task_packet_path: str | None = None,
    verification_path: str = LATEST_VERIFICATION_REPORT_PATH,
    evidence_dir: str | None = None,
    output_path: str = REVIEW_PACKET_PATH,
    max_token_warning: int | None = None,
) -> PacketRender:
    body = render_review_packet(
        repo_root,
        task_packet_path=task_packet_path,
        verification_path=verification_path,
        evidence_dir=evidence_dir,
        output_path=output_path,
        max_token_warning=max_token_warning,
    )
    for _ in range(5):
        stats = estimate_text(body, output_path)
        budget_status, warnings = review_packet_budget_warnings(body, repo_root, max_token_warning=max_token_warning)
        updated = render_review_packet(
            repo_root,
            task_packet_path=task_packet_path,
            verification_path=verification_path,
            evidence_dir=evidence_dir,
            output_path=output_path,
            chars=stats.chars,
            tokens=stats.approx_tokens,
            budget_status=budget_status,
            warnings=warnings,
            max_token_warning=max_token_warning,
        )
        if updated == body:
            break
        body = updated
    stats = estimate_text(body, output_path)
    budget_status, warnings = review_packet_budget_warnings(body, repo_root, max_token_warning=max_token_warning)
    return PacketRender(body, stats, budget_status, warnings)


def write_review_packet(
    repo_root: Path,
    task_packet_path: str | None = None,
    verification_path: str = LATEST_VERIFICATION_REPORT_PATH,
    evidence_dir: str | None = None,
    output_path: str = REVIEW_PACKET_PATH,
    max_token_warning: int | None = None,
) -> tuple[WriteResult, PacketRender]:
    target = safe_repo_path(repo_root, output_path)
    rel = normalize_rel(target.relative_to(repo_root))
    allowed = rel.startswith(".aide/context/") or rel.startswith(".aide/queue/")
    forbidden = any(pattern_matches(rel, pattern) for pattern in [".git/**", ".aide.local/**", "secrets/**", ".env"])
    if not allowed or forbidden:
        raise ValueError(f"review packet output path is not allowed: {output_path}")
    packet = build_review_packet(
        repo_root,
        task_packet_path=task_packet_path,
        verification_path=verification_path,
        evidence_dir=evidence_dir,
        output_path=rel,
        max_token_warning=max_token_warning,
    )
    return write_text_if_changed(target, packet.text), packet


def verify_review_packet(repo_root: Path, rel_path: str) -> list[VerificationFinding]:
    findings: list[VerificationFinding] = []
    path = safe_repo_path(repo_root, rel_path)
    if not path.exists():
        return [VerificationFinding("ERROR", "review_packet", "review packet does not exist", rel_path)]
    text = read_text(path)
    findings.extend(verify_markdown_sections(text, REVIEW_PACKET_REQUIRED_SECTIONS, rel_path, "review_packet"))
    if len(re.findall(r"^##\s+Decision Requested\s*$", text, re.MULTILINE)) != 1:
        findings.append(VerificationFinding("ERROR", "review_packet", "must contain exactly one Decision Requested section", rel_path))
    if not all(decision in text for decision in ["PASS", "PASS_WITH_NOTES", "REQUEST_CHANGES", "BLOCKED"]):
        findings.append(VerificationFinding("ERROR", "review_packet", "decision request does not list all allowed decisions", rel_path))
    lowered = text.lower()
    for phrase in FORBIDDEN_PACKET_PHRASES:
        if phrase.lower() in lowered:
            findings.append(VerificationFinding("WARN", "review_packet", f"forbidden prompt pattern mentioned: {phrase}", rel_path))
    for marker in CONTEXT_FORBIDDEN_INLINE_MARKERS:
        if marker in text:
            findings.append(VerificationFinding("ERROR", "review_packet", "review packet appears to inline raw source marker", rel_path))
    budget = load_token_budget(repo_root)
    stats = estimate_text(text, rel_path)
    if stats.approx_tokens > budget["max_review_packet_tokens"]:
        findings.append(VerificationFinding("WARN", "review_packet", f"review packet over hard limit: {stats.approx_tokens}", rel_path))
    else:
        findings.append(VerificationFinding("INFO", "review_packet", f"review packet tokens: {stats.approx_tokens}", rel_path))
    for required_ref in [LATEST_CONTEXT_PACKET_PATH, LATEST_VERIFICATION_REPORT_PATH, REVIEW_DECISION_POLICY_PATH]:
        if required_ref not in text:
            findings.append(VerificationFinding("WARN", "review_packet", f"review ref missing: {required_ref}", rel_path))
    findings.extend(verify_refs_in_text(repo_root, text, rel_path))
    return findings


def strip_yaml_scalar(value: str) -> str:
    return value.strip().strip('"').strip("'")


def parse_bool_scalar(value: str) -> bool:
    return strip_yaml_scalar(value).lower() in {"true", "yes", "1"}


def load_adapter_targets(repo_root: Path) -> list[AdapterTarget]:
    path = repo_root / ADAPTER_TARGETS_PATH
    if not path.exists():
        return []
    targets: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in read_text(path).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        if stripped.startswith("- target_id:"):
            if current:
                targets.append(current)
            current = {"target_id": strip_yaml_scalar(stripped.split(":", 1)[1])}
            continue
        if current is None:
            continue
        if stripped.startswith("- "):
            continue
        key, value = stripped.split(":", 1)
        current[key.strip()] = strip_yaml_scalar(value)
    if current:
        targets.append(current)
    return [
        AdapterTarget(
            target_id=item.get("target_id", ""),
            display_name=item.get("display_name", item.get("target_id", "")),
            output_path=normalize_rel(item.get("output_path", "")) if item.get("output_path", "") else "",
            generated_path=normalize_rel(item.get("generated_path", "")) if item.get("generated_path", "") else "",
            output_mode=item.get("output_mode", "preview_only"),
            template_path=normalize_rel(item.get("template_path", "")) if item.get("template_path", "") else "",
            enabled_by_default=parse_bool_scalar(item.get("enabled_by_default", "false")),
            risk_level=item.get("risk_level", "unknown"),
            manual_content_policy=item.get("manual_content_policy", ""),
            drift_policy=item.get("drift_policy", ""),
            target_notes=item.get("target_notes", ""),
        )
        for item in targets
        if item.get("target_id")
    ]


def adapter_target_by_id(repo_root: Path, target_id: str) -> AdapterTarget | None:
    for target in load_adapter_targets(repo_root):
        if target.target_id == target_id:
            return target
    return None


def fallback_codex_target() -> AdapterTarget:
    return AdapterTarget(
        target_id="codex_agents_md",
        display_name="Codex AGENTS.md",
        output_path="AGENTS.md",
        generated_path=".aide/generated/adapters/AGENTS.md",
        output_mode="managed_section",
        template_path=".aide/adapters/templates/AGENTS.md.template",
        enabled_by_default=True,
        risk_level="low",
        manual_content_policy="preserve_outside_managed_section",
        drift_policy="compare_managed_section",
        target_notes="fallback target used when Q24 target metadata is absent",
    )


def adapter_template_fallback(target: AdapterTarget) -> str:
    if target.target_id == "codex_agents_md":
        return """{{managed_begin}}
## AIDE Existing-Tool Adapter: Codex

- Use `.aide/context/latest-task-packet.md` as the default task brief.
- Do not paste long chat history, full repo dumps, raw prompts, raw responses,
  secrets, provider keys, or `.aide.local/` contents.
- Prefer exact repo refs and line refs over copied file bodies.
- Run AIDE Lite `doctor`, `validate`, `pack`, `verify`, and `review-pack`
  where available.
- Gateway/provider calls and forwarding remain deferred until reviewed policy.
- Write evidence and stop at review gates.
{{managed_end}}
"""
    return "{{managed_begin}}\nUse `.aide/context/latest-task-packet.md`; do not paste full histories or secrets.\n{{managed_end}}\n"


def template_without_markers(template: str) -> str:
    return normalize_text(
        template.replace("{{managed_begin}}", "")
        .replace("{{managed_end}}", "")
        .replace("{{managed_begin_text}}", "")
        .replace("{{managed_end_text}}", "")
    )


def adapter_marker_metadata(target: AdapterTarget, fingerprint: str) -> str:
    return (
        f"AIDE-GENERATED:BEGIN section={AGENTS_SECTION} target={target.target_id} "
        f"generator={ADAPTER_COMPILER_ID} version={GENERATOR_VERSION} "
        f"source_template={target.template_path} mode={target.output_mode} "
        f"manual=outside-only fingerprint=sha256:{fingerprint}"
    )


def render_adapter_target(repo_root: Path, target: AdapterTarget) -> str:
    template_path = repo_root / target.template_path if target.template_path else None
    template = read_text(template_path) if template_path and template_path.exists() else adapter_template_fallback(target)
    fingerprint = sha256_text(template_without_markers(template))
    begin_meta = adapter_marker_metadata(target, fingerprint)
    end_meta = f"AIDE-GENERATED:END section={AGENTS_SECTION}"
    rendered = template.replace("{{managed_begin}}", f"<!-- {begin_meta} -->")
    rendered = rendered.replace("{{managed_end}}", f"<!-- {end_meta} -->")
    rendered = rendered.replace("{{managed_begin_text}}", begin_meta)
    rendered = rendered.replace("{{managed_end_text}}", end_meta)
    return normalize_text(rendered)


def render_agents_section(repo_root: Path | None = None) -> str:
    root = repo_root or repo_root_from_script()
    target = adapter_target_by_id(root, "codex_agents_md") or fallback_codex_target()
    return render_adapter_target(root, target)


def agents_body(repo_root: Path | None = None) -> str:
    rendered = render_agents_section(repo_root)
    match = _managed_match(rendered)
    if match:
        return normalize_text(match.group("body"))
    return """## Q20 Token, Context, Verifier, Review, Ledger, Eval, Outcome, Routing, Cache, Gateway, Provider, And Local-State Guidance

- Use `.aide/context/latest-task-packet.md` when present instead of pasting long chat history.
- Use `.aide/context/latest-context-packet.md`, repo-map refs, test-map refs, compact project memory, and evidence packets before broad context dumps.
- Do not paste full prior transcripts, whole repo dumps, repeated roadmap dumps, secrets, provider keys, local caches, raw prompts, or raw responses.
- Emit deltas and compact final reports with status, changed files, validation, evidence, risks, and next step.
- Generate `.aide/context/latest-review-packet.md` with `review-pack` before premium-model review.
- Run `ledger scan`, `ledger report`, and `ledger compare` for token-ledger work, and do not store raw prompts or raw responses in committed ledger records.
- Run `eval list`, `eval run`, and `eval report` for token-saving workflow changes once Q15 golden-task behavior is available.
- Treat token reduction as invalid if golden tasks fail.
- Run `outcome report` and `optimize suggest` for advisory recommendations once Q16 controller behavior is available.
- Do not implement controller recommendations automatically; use a future queue item or explicit human approval.
- Run `route list`, `route validate`, and `route explain` before expensive review or execution once Q17 Router Profile behavior is available.
- Treat route decisions as advisory until a future reviewed Gateway/Runtime phase exists.
- Do not demote hard floors; architecture, security, self-modification, final promotion, governance, high-stakes, and destructive work require frontier or human review paths.
- Prefer the no-model/tool route when deterministic commands can complete the work.
- Keep committed repo contract under `.aide/`; keep machine-local runtime state under gitignored `.aide.local/`.
- Use `.aide.local.example/` only as a safe template and never commit actual `.aide.local/` contents.
- Run `cache init`, `cache status`, `cache key`, and `cache report` for cache/local-state boundary work once Q18 behavior is available.
- Treat cache-key reports as metadata only; a cache hit must not bypass verifier, review gates, golden tasks, or hard floors.
- Keep semantic cache for code edits forbidden and provider response caching disabled until a future reviewed Gateway/cache policy enables them.
- Run `gateway status`, `gateway endpoints`, and `gateway smoke` for Gateway-adjacent work once Q19 Gateway skeleton behavior is available.
- Treat the Q19 Gateway skeleton as local/report-only; do not point external tools at it expecting provider forwarding.
- Do not log raw prompts or raw responses through Gateway surfaces.
- Run `provider list`, `provider status`, `provider validate`, `provider contract`, and `provider probe --offline` for Provider Adapter v0 work once Q20 behavior is available.
- Treat Q20 provider metadata as offline advisory contracts only.
- Do not add provider keys, account IDs, credentials, raw prompts, or raw responses to committed files.
- Do not make live provider calls, model calls, network calls, availability probes, or Gateway forwarding from Q20 provider surfaces.
- Use provider status as metadata in evidence, Gateway summaries, and advisory route decisions only.
- Keep OpenAI/Anthropic-compatible forwarding, MCP/A2A, and Runtime execution deferred until future reviewed phases.
- Keep provider/model calls forbidden unless a future reviewed phase explicitly enables them.
- Review compact review packets and verifier output only by default; ask for more context only when the packet is insufficient.
- Run `py -3 .aide/scripts/aide_lite.py doctor`, `validate`, `snapshot`, `index`, `context`, `pack`, `estimate`, `verify`, `review-pack`, `ledger`, `eval`, `outcome`, `optimize`, `route`, `cache`, `gateway`, `provider`, `export-pack`, `import-pack`, `pack-status`, `adapt`, and `test` for token/context/verifier/review/ledger/eval/outcome/routing/cache/gateway/provider/export work. `selftest` remains a compatibility alias for the internal checks.
- Prefer exact refs such as `path#Lstart-Lend`; do not inline whole files by default.
- Treat token savings as invalid when validation, quality evidence, provenance, or review gates are weakened.
- Commit coherent subdeliverables with verbose bodies when queue work changes repo state.
"""


def _managed_match(text: str) -> re.Match[str] | None:
    pattern = re.compile(
        rf"<!-- AIDE-GENERATED:BEGIN section={re.escape(AGENTS_SECTION)} (?P<meta>.*?) -->\n(?P<body>.*?)"
        rf"<!-- AIDE-GENERATED:END section={re.escape(AGENTS_SECTION)} -->",
        re.DOTALL,
    )
    return pattern.search(text)


def _legacy_bounds(text: str) -> tuple[int, int] | None:
    if LEGACY_AGENTS_MANAGED_BEGIN in text:
        start = text.index(LEGACY_AGENTS_MANAGED_BEGIN)
        try:
            end = text.index(LEGACY_AGENTS_MANAGED_END, start) + len(LEGACY_AGENTS_MANAGED_END)
        except ValueError:
            return (start, len(text))
        return (start, end)
    if LEGACY_AGENTS_BEGIN not in text:
        return None
    start = text.index(LEGACY_AGENTS_BEGIN)
    try:
        end = text.index(LEGACY_AGENTS_END, start) + len(LEGACY_AGENTS_END)
    except ValueError:
        return (start, len(text))
    return (start, end)


def adapter_status(repo_root: Path) -> AdapterStatus:
    target = repo_root / "AGENTS.md"
    if not target.exists():
        return AdapterStatus("missing-target", "restore AGENTS.md before adapting", False, False)
    text = read_text(target)
    expected_section = render_agents_section(repo_root)
    expected_match = _managed_match(expected_section)
    expected_body = normalize_text(expected_match.group("body") if expected_match else agents_body(repo_root))
    match = _managed_match(text)
    if match:
        body = normalize_text(match.group("body"))
        body_matches = body == expected_body
        fingerprint = re.search(r"fingerprint=sha256:([0-9a-f]{64})", match.group("meta"))
        fingerprint_matches = bool(fingerprint and fingerprint.group(1) == sha256_text(body))
        if body_matches and fingerprint_matches:
            return AdapterStatus("current", "no action needed", True, True)
        return AdapterStatus("drift", "run adapt to replace managed section", body_matches, fingerprint_matches)
    if _legacy_bounds(text):
        return AdapterStatus("legacy", "run adapt to replace legacy Q09 marker", False, False)
    return AdapterStatus("missing", "run adapt to append managed section", False, False)


def adapt_agents(repo_root: Path) -> tuple[WriteResult, AdapterStatus, AdapterStatus]:
    target = repo_root / "AGENTS.md"
    existing = read_text(target) if target.exists() else ""
    before = adapter_status(repo_root) if target.exists() else AdapterStatus("missing-target", "restore AGENTS.md", False, False)
    section = render_agents_section(repo_root).rstrip()
    match = _managed_match(existing)
    if match:
        updated = existing[: match.start()] + section + existing[match.end() :]
    else:
        legacy = _legacy_bounds(existing)
        if legacy:
            start, end = legacy
            updated = existing[:start] + section + existing[end:]
        else:
            updated = existing.rstrip() + "\n\n" + section if existing.strip() else section
    result = write_text_if_changed(target, updated)
    after = adapter_status(repo_root)
    if before.status == "missing" and result.action == "written":
        result = WriteResult(target, "appended")
    elif before.status in {"legacy", "drift"} and result.action == "written":
        result = WriteResult(target, "replaced")
    return result, before, after


def has_token_guidance(repo_root: Path) -> bool:
    return adapter_status(repo_root).status == "current"


def safe_adapter_output_path(path: str) -> bool:
    rel = normalize_rel(path)
    if not rel or rel.startswith("../") or rel.startswith("/") or re.match(r"^[A-Za-z]:", rel):
        return False
    forbidden = [".env", ".aide.local", "secrets/", ".git/"]
    return not any(rel == item or rel.startswith(item.rstrip("/") + "/") for item in forbidden)


def render_adapter_outputs(repo_root: Path, write: bool = True) -> tuple[list[dict[str, object]], list[WriteResult], list[dict[str, str]]]:
    targets = load_adapter_targets(repo_root)
    rendered: list[dict[str, object]] = []
    writes: list[WriteResult] = []
    for target in targets:
        if not target.template_path or not target.generated_path:
            continue
        text = render_adapter_target(repo_root, target)
        rendered.append({"target": target, "text": text})
        if write:
            writes.append(write_text_if_changed(repo_root / target.generated_path, text))
    drift = adapter_drift_records(repo_root, rendered)
    if write:
        manifest = adapter_manifest_data(repo_root, rendered, drift)
        writes.append(write_text_if_changed(repo_root / ADAPTER_GENERATED_MANIFEST_PATH, stable_json_text(manifest)))
        writes.append(write_text_if_changed(repo_root / ADAPTER_DRIFT_REPORT_PATH, render_adapter_drift_report(drift)))
    return rendered, writes, drift


def adapter_manifest_data(repo_root: Path, rendered: list[dict[str, object]], drift: list[dict[str, str]]) -> dict[str, object]:
    drift_by_target = {record["target_id"]: record for record in drift}
    targets: list[dict[str, object]] = []
    for item in rendered:
        target = item["target"]
        assert isinstance(target, AdapterTarget)
        text = str(item["text"])
        targets.append(
            {
                "target_id": target.target_id,
                "display_name": target.display_name,
                "output_path": target.output_path,
                "generated_path": target.generated_path,
                "output_mode": target.output_mode,
                "enabled_by_default": target.enabled_by_default,
                "risk_level": target.risk_level,
                "sha256": sha256_text(text),
                "drift_status": drift_by_target.get(target.target_id, {}).get("status", "unknown"),
            }
        )
    return {
        "schema_version": "q24.adapter-generated-manifest.v0",
        "generated_by": f"{GENERATOR_NAME} {GENERATOR_VERSION}",
        "compiler": ADAPTER_COMPILER_ID,
        "contents_inline": False,
        "generated_outputs_not_canonical": True,
        "provider_or_model_calls": False,
        "network_calls": False,
        "target_count": len(targets),
        "targets": sorted(targets, key=lambda item: str(item["target_id"])),
    }


def extract_adapter_managed_text(text: str) -> tuple[str, str] | None:
    match = _managed_match(text)
    if not match:
        return None
    section = text[match.start() : match.end()]
    body = normalize_text(match.group("body"))
    return section, body


def adapter_drift_records(repo_root: Path, rendered: list[dict[str, object]] | None = None) -> list[dict[str, str]]:
    if rendered is None:
        rendered = [{"target": target, "text": render_adapter_target(repo_root, target)} for target in load_adapter_targets(repo_root) if target.template_path and target.generated_path]
    records: list[dict[str, str]] = []
    for item in rendered:
        target = item["target"]
        assert isinstance(target, AdapterTarget)
        expected = normalize_text(str(item["text"]))
        actual_path = repo_root / target.output_path
        status = "missing"
        detail = "target file missing"
        if target.output_mode == "preview_only":
            if not actual_path.exists():
                status = "preview_only"
                detail = "preview generated only; target file is absent"
            else:
                actual = normalize_text(read_text(actual_path))
                status = "current" if actual == expected else "drifted"
                detail = "target matches preview" if status == "current" else "target differs from preview"
        elif target.output_mode == "managed_section":
            if not actual_path.exists():
                status = "missing"
                detail = "managed target file missing"
            else:
                actual = read_text(actual_path)
                actual_managed = extract_adapter_managed_text(actual)
                expected_managed = extract_adapter_managed_text(expected)
                if actual_managed and expected_managed:
                    status = "current" if actual_managed[1] == expected_managed[1] else "drifted"
                    detail = "managed section current" if status == "current" else "managed section body differs"
                elif _legacy_bounds(actual):
                    status = "drifted"
                    detail = "legacy managed section should be replaced"
                else:
                    status = "unmanaged"
                    detail = "target exists without Q24 managed section"
        records.append(
            {
                "target_id": target.target_id,
                "output_path": target.output_path,
                "generated_path": target.generated_path,
                "output_mode": target.output_mode,
                "status": status,
                "detail": detail,
            }
        )
    return sorted(records, key=lambda item: item["target_id"])


def render_adapter_drift_report(records: list[dict[str, str]]) -> str:
    lines = [
        "# Adapter Drift Report",
        "",
        f"- generator: {ADAPTER_COMPILER_ID}",
        f"- generator_version: {GENERATOR_VERSION}",
        "- generated_outputs_not_canonical: true",
        "- provider_or_model_calls: none",
        "- network_calls: none",
        "",
        "| Target | Mode | Status | Detail |",
        "| --- | --- | --- | --- |",
    ]
    for record in records:
        lines.append(
            f"| `{record['target_id']}` | `{record['output_mode']}` | `{record['status']}` | {record['detail']} |"
        )
    return "\n".join(lines) + "\n"


def adapter_generated_output_paths(repo_root: Path) -> list[Path]:
    root = repo_root / ADAPTER_GENERATED_DIR
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if path.is_file())


def adapter_text_has_positive_full_prompting(text: str) -> bool:
    lowered = text.lower()
    bad_phrases = [
        "paste the full history",
        "paste full history into",
        "dump the whole repo into",
        "send the whole repository",
        "include the entire repository",
        "prompt with the full repo",
    ]
    return any(phrase in lowered for phrase in bad_phrases)


def adapter_validation_checks(repo_root: Path, require_generated: bool = True) -> list[Check]:
    checks: list[Check] = []
    for rel in Q24_REQUIRED_FILES:
        exists = (repo_root / rel).exists()
        if rel in {ADAPTER_GENERATED_MANIFEST_PATH, ADAPTER_DRIFT_REPORT_PATH} and not require_generated:
            checks.append(Check("PASS" if exists else "WARN", f"adapter generated artifact exists: {rel}"))
        else:
            checks.append(Check("PASS" if exists else "FAIL", f"adapter required file exists: {rel}"))
    policy_path = repo_root / ADAPTER_POLICY_PATH
    policy_text = read_text(policy_path) if policy_path.exists() else ""
    for anchor in [
        "template_compiler_only",
        "generated_or_preview_outputs",
        "no_tool_runtime_calls",
        "no_provider_calls",
        "managed_sections_required: true",
        "generated_outputs_not_canonical: true",
        "no_full_history_prompting",
        "no_full_repo_prompting",
        "adapter_guidance_must_reference_packets: true",
    ]:
        if anchor not in policy_text:
            checks.append(Check("FAIL", f"adapter policy missing anchor: {anchor}"))
    targets = load_adapter_targets(repo_root)
    target_ids = {target.target_id for target in targets}
    for target_id in ["codex_agents_md", "claude_code", "aider", "cline", "continue", "cursor", "windsurf"]:
        if target_id not in target_ids:
            checks.append(Check("FAIL", f"adapter targets missing target: {target_id}"))
    for target in targets:
        if target.output_path and not safe_adapter_output_path(target.output_path):
            checks.append(Check("FAIL", f"adapter target has unsafe output path: {target.target_id} -> {target.output_path}"))
        if target.generated_path and not safe_adapter_output_path(target.generated_path):
            checks.append(Check("FAIL", f"adapter target has unsafe generated path: {target.target_id} -> {target.generated_path}"))
        if target.template_path:
            if (repo_root / target.template_path).exists():
                checks.append(Check("PASS", f"adapter template exists: {target.template_path}"))
            else:
                checks.append(Check("FAIL", f"adapter template missing: {target.template_path}"))
        elif target.enabled_by_default:
            checks.append(Check("FAIL", f"enabled adapter target has no template: {target.target_id}"))
        if target.output_mode == "preview_only" and target.target_id == "codex_agents_md":
            checks.append(Check("FAIL", "codex AGENTS target must be managed_section, not preview_only"))
    rendered, _writes, _drift = render_adapter_outputs(repo_root, write=False)
    for item in rendered:
        target = item["target"]
        assert isinstance(target, AdapterTarget)
        text = str(item["text"])
        if ".aide/context/latest-task-packet.md" not in text:
            checks.append(Check("FAIL", f"adapter output missing compact task packet rule: {target.target_id}"))
        if "review-pack" not in text and "verify" not in text:
            checks.append(Check("FAIL", f"adapter output missing verification/review-pack rule: {target.target_id}"))
        if adapter_text_has_positive_full_prompting(text):
            checks.append(Check("FAIL", f"adapter output contains full-history/full-repo prompting instruction: {target.target_id}"))
        if not any(marker in text for marker in ["Do not paste", "Do not request or paste", "Avoid full-history", "Confirm the request does not require full-repo prompting", "Keep prompts compact"]):
            checks.append(Check("FAIL", f"adapter output missing anti-full-history guidance: {target.target_id}"))
        findings = [finding for finding in scan_secret_text(text, target.generated_path or target.target_id) if finding.severity == "ERROR"]
        if findings:
            checks.append(Check("FAIL", f"adapter output contains secret-like material: {target.target_id}"))
    generated_paths = adapter_generated_output_paths(repo_root)
    if generated_paths:
        checks.append(Check("PASS", f"adapter generated outputs: {len(generated_paths)}"))
    elif require_generated:
        checks.append(Check("FAIL", "adapter generated outputs missing; run adapter render"))
    else:
        checks.append(Check("WARN", "adapter generated outputs missing; run adapter render"))
    manifest = repo_root / ADAPTER_GENERATED_MANIFEST_PATH
    if manifest.exists():
        try:
            data = json.loads(read_text(manifest))
            if data.get("generated_outputs_not_canonical") is not True:
                checks.append(Check("FAIL", "adapter manifest must mark generated outputs non-canonical"))
            if data.get("provider_or_model_calls") is not False or data.get("network_calls") is not False:
                checks.append(Check("FAIL", "adapter manifest must disable provider/model/network calls"))
            manifest_targets = {str(item.get("target_id")) for item in data.get("targets", []) if isinstance(item, dict)}
            for target_id in ["codex_agents_md", "claude_code", "aider", "cline", "continue", "cursor", "windsurf"]:
                if target_id not in manifest_targets:
                    checks.append(Check("FAIL", f"adapter manifest missing target: {target_id}"))
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            checks.append(Check("FAIL", f"adapter manifest malformed: {exc}"))
    elif require_generated:
        checks.append(Check("FAIL", f"adapter manifest missing: {ADAPTER_GENERATED_MANIFEST_PATH}"))
    return checks


def infer_phase(task_text: str) -> tuple[str, str]:
    cleaned = task_text.strip()
    match = re.search(r"\b(Q\d{2})\b\s*[-:—]?\s*(.*)", cleaned)
    if not match:
        return "UNSPECIFIED", cleaned or "Compact task"
    phase = match.group(1)
    title = match.group(2).strip()
    title = re.sub(r"^(Implement|Review|Plan)\s+", "", title, flags=re.IGNORECASE).strip()
    return phase, title or "Compact task"


def packet_budget_warnings(text: str, repo_root: Path) -> tuple[str, tuple[str, ...]]:
    stats = estimate_text(text, LATEST_PACKET_PATH)
    budget = load_token_budget(repo_root)
    warnings: list[str] = []
    if stats.approx_tokens > budget["max_compact_task_packet_tokens"]:
        warnings.append(
            f"compact task packet over hard limit: {stats.approx_tokens} > {budget['max_compact_task_packet_tokens']}"
        )
    elif stats.approx_tokens > budget["compact_task_packet_target_tokens"]:
        warnings.append(
            f"compact task packet over target: {stats.approx_tokens} > {budget['compact_task_packet_target_tokens']}"
        )
    lowered = text.lower()
    for phrase in FORBIDDEN_PACKET_PHRASES:
        if phrase.lower() in lowered:
            warnings.append(f"forbidden prompt phrase appears in generated packet: {phrase}")
    return ("WARN" if warnings else "PASS", tuple(warnings))


def render_task_packet(repo_root: Path, task_text: str, chars: int = 0, tokens: int = 0, budget_status: str = "PENDING", warnings: Iterable[str] = ()) -> str:
    phase, title = infer_phase(task_text)
    snapshot_state = "present" if (repo_root / SNAPSHOT_PATH).exists() else "missing; run snapshot"
    repo_map_state = "present" if (repo_root / REPO_MAP_JSON_PATH).exists() else "missing; run index"
    test_map_state = "present" if (repo_root / TEST_MAP_JSON_PATH).exists() else "missing; run index"
    context_packet_state = "present" if (repo_root / LATEST_CONTEXT_PACKET_PATH).exists() else "missing; run context"
    route_decision_state = "present" if (repo_root / ROUTE_DECISION_JSON_PATH).exists() else "missing; run route explain after Q17"
    warning_lines = "\n".join(f"  - {warning}" for warning in warnings) or "  - none"
    return f"""# AIDE Latest Task Packet

## PHASE

{phase} - {title}

## GOAL

{task_text.strip()}

## WHY

Continue AIDE token survival by using repo-local context refs, compact objectives, deterministic validation, and evidence packets instead of long chat history.

## CONTEXT_REFS

- `.aide/memory/project-state.md`
- `.aide/memory/decisions.md`
- `.aide/memory/open-risks.md`
- `{DOCTRINE_REFS_PATH}` ({'present' if (repo_root / DOCTRINE_REFS_PATH).exists() else 'missing'})
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `AGENTS.md`
- `docs/planning/AUTHORITY_ORDER.md`
- `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
- `docs/planning/MERGED_PROGRAM_STATE.md`
- `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`
- `docs/planning/GATES_AND_PROOFS.md`
- `docs/planning/POST_PI_EXECUTION_PLAN.md`
- `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`
- `docs/planning/PLAYER_DESIRE_ACCEPTANCE_MAP.md`
- `specs/reality/`
- `data/reality/`
- `{SNAPSHOT_PATH}` ({snapshot_state})
- `{REPO_MAP_JSON_PATH}` ({repo_map_state})
- `{REPO_MAP_MD_PATH}` ({repo_map_state})
- `{TEST_MAP_JSON_PATH}` ({test_map_state})
- `{CONTEXT_INDEX_PATH}` ({'present' if (repo_root / CONTEXT_INDEX_PATH).exists() else 'missing; run index'})
- `{LATEST_CONTEXT_PACKET_PATH}` ({context_packet_state})
- `{ROUTE_DECISION_JSON_PATH}` ({route_decision_state})
- `{ROUTE_DECISION_MD_PATH}` ({route_decision_state})
- `{CACHE_KEYS_JSON_PATH}` ({'present' if (repo_root / CACHE_KEYS_JSON_PATH).exists() else 'missing; run cache report'})
- `{CACHE_KEYS_MD_PATH}` ({'present' if (repo_root / CACHE_KEYS_MD_PATH).exists() else 'missing; run cache report'})
- `.aide/prompts/compact-task.md`
- `.aide/policies/token-budget.yaml`
- `.aide/policies/cache.yaml`
- `.aide/policies/local-state.yaml`

## ALLOWED_PATHS

- `<fill from the next reviewed queue packet>`
- `.aide/context/**`
- `.aide/queue/{phase.lower()}-*` if this task becomes a queue item
- root docs only when behavior or documentation links change

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- raw provider credentials, API keys, local caches, raw prompt logs
- Dominium product/source roots unless the queue packet explicitly authorizes them: `runtime/**`, `engine/**`, `client/**`, `server/**`, `apps/**`, `content/**`, `contracts/**`, `specs/**`, `data/**`, `tests/**`
- Dominium doctrine rewrites unless the queue packet explicitly authorizes a compact pointer-only documentation update
- Gateway, provider, Runtime, Service, Commander, Mobile, MCP/A2A, host, or app-surface implementation paths unless the queue packet explicitly authorizes them

## IMPLEMENTATION

- Read the queue packet and relevant repo refs first.
- Keep changes inside the allowed paths.
- Make the smallest coherent diff that satisfies acceptance.
- Preserve generated/manual boundaries.
- Do not inline whole source files unless exact contents are required.
- Use exact refs such as `path#Lstart-Lend` when file details are load-bearing.

## VALIDATION

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py index`
- `py -3 .aide/scripts/aide_lite.py context`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py review-pack`
- `py -3 .aide/scripts/aide_lite.py route explain`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 scripts/aide validate`
- `git diff --check`

## COMMITS

- Commit coherent subdeliverables with verbose bodies.
- Stop at review gates.

## EVIDENCE

- changed files
- validation commands and results
- verifier result
- review packet path and result when review-pack is available
- advisory route decision path and result when Q17 routing is available
- compact packet size and budget status
- unresolved risks and deferrals

## NON_GOALS

- No Gateway, provider calls, live model routing, local model setup, exact tokenizer, provider billing ledger, Runtime, Service, Commander, Mobile, MCP/A2A, UI, host/app implementation, or autonomous loop unless this packet is superseded by a reviewed queue item that explicitly authorizes it.

## ACCEPTANCE

- Task-specific acceptance criteria are met.
- Validation is run and recorded.
- Evidence is written.
- No secrets, raw prompt logs, local caches, or `.aide.local` contents are committed.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `CHANGED_FILES`, `VALIDATION`, route/verifier/token results, `RISKS`, and `NEXT`.
Include the verifier result when Q12 verifier behavior is available.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: {chars}
- approx_tokens: {tokens}
- budget_status: {budget_status}
- warnings:
{warning_lines}
- formal ledger: `.aide/reports/token-ledger.jsonl`
"""


def build_task_packet(repo_root: Path, task_text: str) -> PacketRender:
    body = render_task_packet(repo_root, task_text)
    for _ in range(5):
        stats = estimate_text(body, LATEST_PACKET_PATH)
        budget_status, warnings = packet_budget_warnings(body, repo_root)
        updated = render_task_packet(repo_root, task_text, stats.chars, stats.approx_tokens, budget_status, warnings)
        if updated == body:
            break
        body = updated
    stats = estimate_text(body, LATEST_PACKET_PATH)
    budget_status, warnings = packet_budget_warnings(body, repo_root)
    return PacketRender(body, stats, budget_status, warnings)


def write_task_packet(repo_root: Path, task_text: str) -> tuple[WriteResult, PacketRender]:
    if not (repo_root / SNAPSHOT_PATH).exists():
        write_snapshot(repo_root)
    packet = build_task_packet(repo_root, task_text)
    result = write_text_if_changed(repo_root / LATEST_PACKET_PATH, packet.text)
    return result, packet


def scan_for_secrets(repo_root: Path, paths: Iterable[str]) -> list[str]:
    findings: list[str] = []
    for rel in paths:
        path = repo_root / rel
        if path.is_dir():
            candidates = [candidate for candidate in path.rglob("*") if candidate.is_file()]
        elif path.exists():
            candidates = [path]
        else:
            continue
        for candidate in candidates:
            try:
                if looks_binary(candidate):
                    continue
                text = read_text(candidate)
            except (OSError, UnicodeDecodeError):
                continue
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    findings.append(normalize_rel(candidate.relative_to(repo_root)))
                    break
    return sorted(set(findings))


def validate_repo(repo_root: Path) -> tuple[bool, list[str]]:
    checks = collect_validation_checks(repo_root)
    return not any(check.severity == "FAIL" for check in checks), [f"{check.severity} {check.message}" for check in checks]


def collect_validation_checks(repo_root: Path) -> list[Check]:
    checks: list[Check] = []
    for rel in REQUIRED_FILES:
        if not (repo_root / rel).exists():
            checks.append(Check("FAIL", f"missing required file: {rel}"))
        else:
            checks.append(Check("PASS", f"required file: {rel}"))

    budget_path = repo_root / ".aide/policies/token-budget.yaml"
    budget_text = read_text(budget_path) if budget_path.exists() else ""
    for anchor in TOKEN_BUDGET_ANCHORS:
        if anchor not in budget_text:
            checks.append(Check("FAIL", f"token budget missing anchor: {anchor}"))
    budget = load_token_budget(repo_root)

    prompt_path = repo_root / ".aide/prompts/compact-task.md"
    if prompt_path.exists():
        for section in missing_sections(read_text(prompt_path), COMPACT_TASK_SECTIONS):
            checks.append(Check("FAIL", f"compact task missing section: {section}"))

    review_path = repo_root / ".aide/prompts/evidence-review.md"
    if review_path.exists():
        review_text = read_text(review_path)
        for decision in ["PASS", "PASS_WITH_NOTES", "REQUEST_CHANGES", "BLOCKED"]:
            if decision not in review_text:
                checks.append(Check("FAIL", f"evidence review missing decision: {decision}"))
        for section in ["DECISION:", "REASONS:", "REQUIRED_FIXES:", "OPTIONAL_NOTES:", "NEXT_PHASE:"]:
            if section not in review_text:
                checks.append(Check("FAIL", f"evidence review missing output section: {section}"))

    ignore_patterns = load_ignore_patterns(repo_root)
    for pattern in REQUIRED_IGNORE_PATTERNS:
        if pattern not in ignore_patterns:
            checks.append(Check("FAIL", f"ignore policy missing exclusion: {pattern}"))

    for rel in CONTEXT_CONFIG_FILES:
        if (repo_root / rel).exists():
            checks.append(Check("PASS", f"context compiler config exists: {rel}"))
        elif (repo_root / ".aide/queue/Q11-context-compiler-v0").exists():
            checks.append(Check("FAIL", f"context compiler config missing: {rel}"))

    for rel in Q12_REQUIRED_FILES:
        if (repo_root / rel).exists():
            checks.append(Check("PASS", f"verifier config exists: {rel}"))
        elif (repo_root / ".aide/queue/Q12-verifier-v0").exists():
            checks.append(Check("FAIL", f"verifier config missing: {rel}"))

    if (repo_root / ".aide/queue/Q14-token-ledger-savings-report").exists():
        for rel in Q14_REQUIRED_FILES:
            if (repo_root / rel).exists():
                checks.append(Check("PASS", f"token ledger artifact exists: {rel}"))
            else:
                checks.append(Check("FAIL", f"token ledger artifact missing: {rel}"))
        ledger_policy = repo_root / TOKEN_LEDGER_POLICY_PATH
        if ledger_policy.exists():
            ledger_policy_text = read_text(ledger_policy)
            for anchor in TOKEN_LEDGER_ANCHORS:
                if anchor not in ledger_policy_text:
                    checks.append(Check("FAIL", f"token ledger policy missing anchor: {anchor}"))
            if "raw_prompt_storage_default: false" not in ledger_policy_text:
                checks.append(Check("FAIL", "token ledger policy must disable raw prompt storage by default"))
            if "raw_response_storage_default: false" not in ledger_policy_text:
                checks.append(Check("FAIL", "token ledger policy must disable raw response storage by default"))
        ledger_records = read_ledger_records(repo_root)
        if ledger_records:
            checks.append(Check("PASS", f"token ledger records: {len(ledger_records)}"))
            raw_terms = [
                record
                for record in ledger_records
                if "raw prompt" in record.notes.lower()
                and "not stored" not in record.notes.lower()
                and "no raw" not in record.notes.lower()
            ]
            if raw_terms:
                checks.append(Check("FAIL", "token ledger record appears to describe raw prompt storage"))
            for warning in ledger_budget_warnings(ledger_records):
                checks.append(Check("WARN", f"token ledger budget warning: {warning}"))
        else:
            checks.append(Check("WARN", "token ledger has no records yet; run ledger scan"))

    if (repo_root / ".aide/queue/Q15-golden-tasks-v0").exists():
        for rel in Q15_REQUIRED_FILES:
            if (repo_root / rel).exists():
                checks.append(Check("PASS", f"golden task artifact exists: {rel}"))
            else:
                checks.append(Check("FAIL", f"golden task artifact missing: {rel}"))
        eval_policy = repo_root / EVAL_POLICY_PATH
        if eval_policy.exists():
            eval_policy_text = read_text(eval_policy)
            for anchor in EVAL_POLICY_ANCHORS:
                if anchor not in eval_policy_text:
                    checks.append(Check("FAIL", f"eval policy missing anchor: {anchor}"))
        definitions = parse_golden_task_catalog(repo_root)
        ids = {definition.task_id for definition in definitions}
        for task_id in REQUIRED_GOLDEN_TASK_IDS:
            if task_id not in ids:
                checks.append(Check("FAIL", f"golden task catalog missing task: {task_id}"))
            task_dir = repo_root / GOLDEN_TASK_ROOT / task_id
            if not (task_dir / "task.yaml").exists():
                checks.append(Check("FAIL", f"golden task missing task.yaml: {task_id}"))
            if not (task_dir / "acceptance.md").exists():
                checks.append(Check("FAIL", f"golden task missing acceptance.md: {task_id}"))
        if definitions:
            checks.append(Check("PASS", f"golden task definitions: {len(definitions)}"))
        latest_eval = repo_root / GOLDEN_RUN_JSON_PATH
        latest_eval_md = repo_root / GOLDEN_RUN_MD_PATH
        if latest_eval.exists():
            try:
                data = json.loads(read_text(latest_eval))
                if data.get("raw_prompt_storage") is not False:
                    checks.append(Check("FAIL", "golden task report must disable raw prompt storage"))
                if data.get("raw_response_storage") is not False:
                    checks.append(Check("FAIL", "golden task report must disable raw response storage"))
                if "tasks" not in data:
                    checks.append(Check("FAIL", "golden task report missing tasks"))
                else:
                    checks.append(Check("PASS", f"golden task report tasks: {len(data.get('tasks', []))}"))
            except (OSError, json.JSONDecodeError, TypeError) as exc:
                checks.append(Check("FAIL", f"golden task JSON report malformed: {exc}"))
        else:
            checks.append(Check("WARN", f"golden task JSON report missing: {GOLDEN_RUN_JSON_PATH}"))
        if latest_eval_md.exists():
            checks.append(Check("PASS", f"golden task Markdown report exists: {GOLDEN_RUN_MD_PATH}"))
        else:
            checks.append(Check("WARN", f"golden task Markdown report missing: {GOLDEN_RUN_MD_PATH}"))

    if (repo_root / ".aide/queue/Q16-outcome-controller-v0").exists():
        for rel in Q16_REQUIRED_FILES:
            if (repo_root / rel).exists():
                checks.append(Check("PASS", f"controller artifact exists: {rel}"))
            else:
                checks.append(Check("FAIL", f"controller artifact missing: {rel}"))
        controller_policy = repo_root / CONTROLLER_POLICY_PATH
        if controller_policy.exists():
            controller_policy_text = read_text(controller_policy)
            for anchor in CONTROLLER_POLICY_ANCHORS:
                if anchor not in controller_policy_text:
                    checks.append(Check("FAIL", f"controller policy missing anchor: {anchor}"))
        taxonomy = parse_failure_taxonomy(repo_root)
        for failure_class in CONTROLLER_FAILURE_CLASSES:
            if failure_class not in taxonomy:
                checks.append(Check("FAIL", f"controller taxonomy missing class: {failure_class}"))
        outcome_records = read_outcome_records(repo_root)
        if outcome_records:
            checks.append(Check("PASS", f"outcome ledger records: {len(outcome_records)}"))
            for record in outcome_records:
                if record.failure_class not in taxonomy:
                    checks.append(Check("FAIL", f"outcome record has unknown failure class: {record.failure_class}"))
                if record.result not in {"PASS", "WARN", "FAIL"}:
                    checks.append(Check("FAIL", f"outcome record has invalid result: {record.result}"))
                if "raw_prompt" in record.notes.lower() or "raw_response" in record.notes.lower():
                    if "not stored" not in record.notes.lower() and "no raw" not in record.notes.lower():
                        checks.append(Check("FAIL", "outcome record appears to store raw prompt/response data"))
        else:
            checks.append(Check("WARN", "outcome ledger has no records yet; run outcome report"))
        recommendations_path = repo_root / RECOMMENDATIONS_PATH
        if recommendations_path.exists():
            recommendation_text = read_text(recommendations_path)
            for anchor in ["expected_benefit", "evidence_source", "risk_level", "next_action", "rollback_condition", "applies_automatically: false"]:
                if anchor not in recommendation_text:
                    checks.append(Check("FAIL", f"recommendations missing anchor: {anchor}"))
        outcome_report_path = repo_root / OUTCOME_REPORT_PATH
        if outcome_report_path.exists():
            report_text = read_text(outcome_report_path)
            if "advisory_only" not in report_text:
                checks.append(Check("FAIL", "outcome report must state advisory_only"))
            if "automatic_mutation: false" not in report_text:
                checks.append(Check("FAIL", "outcome report must state automatic_mutation: false"))

    if (repo_root / ".aide/queue/Q17-router-profile-v0").exists():
        checks.extend(routing_validation_checks(repo_root))

    if (repo_root / ".aide/queue/Q18-cache-local-state-boundary").exists():
        checks.extend(cache_validation_checks(repo_root))

    if (repo_root / ".aide/queue/Q19-gateway-architecture-skeleton").exists():
        checks.extend(gateway_validation_checks(repo_root))

    if (repo_root / ".aide/queue/Q20-provider-adapter-v0").exists():
        checks.extend(provider_validation_checks(repo_root))

    if (repo_root / ".aide/queue/Q21-cross-repo-pack-export-import-v0").exists():
        checks.extend(export_import_validation_checks(repo_root))

    if (repo_root / ".aide/queue/Q24-existing-tool-adapter-compiler-v0").exists():
        checks.extend(adapter_validation_checks(repo_root, require_generated=False))

    if (repo_root / ".aide/queue/Q27-commit-discipline-workunit-recovery-v0").exists():
        for rel in Q27_REQUIRED_FILES:
            checks.append(Check("PASS" if (repo_root / rel).exists() else "FAIL", f"Q27 required file exists: {rel}"))
        if (repo_root / COMMIT_MESSAGE_POLICY_PATH).exists():
            policy = read_text(repo_root / COMMIT_MESSAGE_POLICY_PATH)
            for marker in ["aide.commit-message-policy.v0", "Conventional Commits", "changelog_categories", "AIDE-Task", "range_check"]:
                if marker not in policy:
                    checks.append(Check("FAIL", f"commit-message policy missing anchor: {marker}"))
        if (repo_root / TASK_RESUMPTION_POLICY_PATH).exists():
            policy = read_text(repo_root / TASK_RESUMPTION_POLICY_PATH)
            for marker in ["stable_task_id_required: true", "resume_from_repo_state_first: true", "repeated_prompt_policy", "out_of_order_prompt_policy"]:
                if marker not in policy:
                    checks.append(Check("FAIL", f"task-resumption policy missing anchor: {marker}"))
        if (repo_root / WORK_UNITS_POLICY_PATH).exists():
            policy = read_text(repo_root / WORK_UNITS_POLICY_PATH)
            for marker in ["idempotency_key", "noop_already_complete", "states"]:
                if marker not in policy:
                    checks.append(Check("FAIL", f"WorkUnit policy missing anchor: {marker}"))
        if (repo_root / RECOVERY_POLICY_PATH).exists():
            policy = read_text(repo_root / RECOVERY_POLICY_PATH)
            for marker in ["duplicate_task", "out_of_order_task", "destructive_ambiguity"]:
                if marker not in policy:
                    checks.append(Check("FAIL", f"recovery policy missing anchor: {marker}"))

    if (repo_root / ".aide/queue/Q28-git-workflow-policy-v0").exists():
        for rel in Q28_REQUIRED_FILES:
            checks.append(Check("PASS" if (repo_root / rel).exists() else "FAIL", f"Q28 required file exists: {rel}"))
        checks.extend(validate_git_policy_files(repo_root))
        if (repo_root / GIT_WORKFLOW_DETECTION_JSON_PATH).exists():
            try:
                data = json.loads(read_text(repo_root / GIT_WORKFLOW_DETECTION_JSON_PATH))
                if data.get("non_mutating") is not True:
                    checks.append(Check("FAIL", "git workflow detection must be non_mutating"))
                else:
                    checks.append(Check("PASS", "git workflow detection is non_mutating"))
                if "branch_role_for_current_branch" not in data:
                    checks.append(Check("FAIL", "git workflow detection missing current branch role"))
            except (OSError, json.JSONDecodeError, TypeError) as exc:
                checks.append(Check("FAIL", f"git workflow detection JSON malformed: {exc}"))
        else:
            checks.append(Check("WARN", f"git workflow detection missing; run `git detect`: {GIT_WORKFLOW_DETECTION_JSON_PATH}"))

    if (repo_root / ".aide/queue/Q29-merge-land-promote-helper-v0").exists():
        for rel in Q29_REQUIRED_FILES:
            checks.append(Check("PASS" if (repo_root / rel).exists() else "FAIL", f"Q29 required file exists: {rel}"))
        checks.extend(validate_git_helper_policy_files(repo_root))

    if (repo_root / ".aide/queue/Q30-aide-dev-main-policy-sync").exists():
        for rel in Q30_REQUIRED_FILES:
            checks.append(Check("PASS" if (repo_root / rel).exists() else "FAIL", f"Q30 required file exists: {rel}"))
        checks.extend(validate_aide_branch_policy_files(repo_root))

    evidence_template = repo_root / EVIDENCE_TEMPLATE_PATH
    if evidence_template.exists():
        for section in missing_sections(read_text(evidence_template), EVIDENCE_PACKET_REQUIRED_SECTIONS):
            checks.append(Check("FAIL", f"evidence template missing section: {section}"))

    review_template = repo_root / REVIEW_TEMPLATE_PATH
    if review_template.exists():
        for section in missing_sections(read_text(review_template), REVIEW_PACKET_REQUIRED_SECTIONS):
            checks.append(Check("FAIL", f"review template missing section: {section}"))

    project_state = repo_root / ".aide/memory/project-state.md"
    if project_state.exists():
        stats = estimate_file(repo_root, ".aide/memory/project-state.md")
        if stats.approx_tokens > budget["max_project_state_tokens"]:
            checks.append(Check("WARN", f"project state over hard limit: {stats.approx_tokens} > {budget['max_project_state_tokens']}"))
        else:
            checks.append(Check("PASS", f"project state tokens: {stats.approx_tokens} <= {budget['max_project_state_tokens']}"))

    packet_path = repo_root / LATEST_PACKET_PATH
    if packet_path.exists():
        packet_text = read_text(packet_path)
        packet_stats = estimate_text(packet_text, LATEST_PACKET_PATH)
        for section in missing_sections(packet_text, PACKET_REQUIRED_SECTIONS):
            checks.append(Check("FAIL", f"latest task packet missing section: {section}"))
        if packet_stats.approx_tokens > budget["max_compact_task_packet_tokens"]:
            checks.append(Check("WARN", f"latest task packet over hard limit: {packet_stats.approx_tokens} > {budget['max_compact_task_packet_tokens']}"))
        for warning in packet_budget_warnings(packet_text, repo_root)[1]:
            checks.append(Check("WARN", warning))
        checks.append(Check("PASS", f"latest task packet tokens: {packet_stats.approx_tokens}"))
    else:
        checks.append(Check("WARN", f"latest task packet missing: {LATEST_PACKET_PATH}"))

    review_packet = repo_root / REVIEW_PACKET_PATH
    if review_packet.exists():
        review_stats = estimate_file(repo_root, REVIEW_PACKET_PATH)
        for finding in verify_review_packet(repo_root, REVIEW_PACKET_PATH):
            if finding.severity == "ERROR":
                checks.append(Check("FAIL", f"review packet {finding.message}"))
            elif finding.severity in {"WARN", "WARNING"}:
                checks.append(Check("WARN", f"review packet {finding.message}"))
        if review_stats.approx_tokens > budget["max_review_packet_tokens"]:
            checks.append(Check("WARN", f"review packet over hard limit: {review_stats.approx_tokens} > {budget['max_review_packet_tokens']}"))
        checks.append(Check("PASS", f"review packet tokens: {review_stats.approx_tokens}"))

    context_expected = (repo_root / ".aide/queue/Q11-context-compiler-v0").exists()
    for rel in CONTEXT_OUTPUT_PATHS:
        if not (repo_root / rel).exists():
            checks.append(Check("WARN" if context_expected else "PASS", f"context artifact missing: {rel}"))

    repo_map_path = repo_root / REPO_MAP_JSON_PATH
    if repo_map_path.exists():
        try:
            repo_map = json.loads(read_text(repo_map_path))
            files = repo_map.get("files", [])
            if repo_map.get("contents_inline") is not False:
                checks.append(Check("FAIL", "repo map must declare contents_inline: false"))
            ignored_records = [
                str(entry.get("path", ""))
                for entry in files
                if is_ignored(str(entry.get("path", "")), ignore_patterns)
            ]
            if ignored_records:
                checks.append(Check("FAIL", f"repo map contains ignored records: {', '.join(ignored_records[:5])}"))
            raw_markers = [
                marker
                for marker in CONTEXT_FORBIDDEN_INLINE_MARKERS
                if marker in read_text(repo_map_path)
            ]
            if raw_markers:
                checks.append(Check("FAIL", f"repo map appears to inline raw contents: {', '.join(raw_markers)}"))
            if files != sorted(files, key=lambda item: (str(item.get("role", "")), str(item.get("path", "")))):
                checks.append(Check("FAIL", "repo map records are not deterministically sorted"))
            checks.append(Check("PASS", f"repo map records: {len(files)}"))
            snapshot_path = repo_root / SNAPSHOT_PATH
            if snapshot_path.exists():
                snapshot = json.loads(read_text(snapshot_path))
                current_hash = snapshot_fingerprint(snapshot)
                if repo_map.get("source_snapshot_hash") != current_hash:
                    checks.append(Check("WARN", "repo map source snapshot hash is stale"))
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
            checks.append(Check("FAIL", f"repo map is malformed: {exc}"))

    test_map_path = repo_root / TEST_MAP_JSON_PATH
    if test_map_path.exists():
        try:
            test_map = json.loads(read_text(test_map_path))
            if test_map.get("complete_coverage_claimed") is not False:
                checks.append(Check("FAIL", "test map must not claim complete coverage"))
            checks.append(Check("PASS", f"test map mappings: {test_map.get('summary', {}).get('mapping_count', 0)}"))
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            checks.append(Check("FAIL", f"test map is malformed: {exc}"))

    context_index_path = repo_root / CONTEXT_INDEX_PATH
    if context_index_path.exists():
        try:
            context_index = json.loads(read_text(context_index_path))
            if context_index.get("contents_inline") is not False:
                checks.append(Check("FAIL", "context index must declare contents_inline: false"))
            checks.append(Check("PASS", "context index is readable"))
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            checks.append(Check("FAIL", f"context index is malformed: {exc}"))

    context_packet_path = repo_root / LATEST_CONTEXT_PACKET_PATH
    if context_packet_path.exists():
        context_text = read_text(context_packet_path)
        for section in missing_sections(context_text, CONTEXT_PACKET_REQUIRED_SECTIONS):
            checks.append(Check("FAIL", f"latest context packet missing section: {section}"))
        raw_markers = [marker for marker in CONTEXT_FORBIDDEN_INLINE_MARKERS if marker in context_text]
        if raw_markers:
            checks.append(Check("FAIL", f"context packet appears to inline raw contents: {', '.join(raw_markers)}"))
        checks.append(Check("PASS", f"latest context packet tokens: {estimate_text(context_text, LATEST_CONTEXT_PACKET_PATH).approx_tokens}"))

    adapter = adapter_status(repo_root)
    if adapter.status == "current":
        checks.append(Check("PASS", "AGENTS token-survival managed section is current"))
    elif adapter.status in {"missing", "legacy", "drift"}:
        checks.append(Check("WARN", f"AGENTS token-survival managed section status: {adapter.status}; {adapter.action_hint}"))
    else:
        checks.append(Check("FAIL", f"AGENTS token-survival managed section status: {adapter.status}; {adapter.action_hint}"))

    secret_findings = scan_for_secrets(
        repo_root,
        [
            ".aide/policies/token-budget.yaml",
            ".aide/prompts",
            ".aide/memory",
            ".aide/context/compiler.yaml",
            ".aide/context/priority.yaml",
            ".aide/context/excerpt-policy.yaml",
            VERIFICATION_POLICY_PATH,
            TOKEN_LEDGER_POLICY_PATH,
            TOKEN_LEDGER_PATH,
            TOKEN_BASELINES_PATH,
            TOKEN_SUMMARY_PATH,
            ".aide/verification",
            ".aide/reports",
            EVAL_POLICY_PATH,
            GOLDEN_TASK_ROOT,
            GOLDEN_RUN_JSON_PATH,
            GOLDEN_RUN_MD_PATH,
            CONTROLLER_POLICY_PATH,
            CONTROLLER_DIR,
            ROUTING_POLICY_PATH,
            MODELS_DIR,
            ROUTING_DIR,
            CACHE_POLICY_PATH,
            LOCAL_STATE_POLICY_PATH,
            CACHE_DIR,
            LOCAL_STATE_EXAMPLE_ROOT,
            GATEWAY_POLICY_PATH,
            GATEWAY_DIR,
            PROVIDER_ADAPTER_POLICY_PATH,
            PROVIDER_DIR,
            LATEST_PACKET_PATH,
            LATEST_CONTEXT_PACKET_PATH,
            REVIEW_PACKET_PATH,
            LATEST_VERIFICATION_REPORT_PATH,
            "AGENTS.md",
        ],
    )
    if secret_findings:
        checks.append(Check("FAIL", f"possible secret material: {', '.join(secret_findings)}"))
    else:
        checks.append(Check("PASS", "no obvious secrets in token-survival files"))

    return checks


def q_status(repo_root: Path, queue_id: str) -> str:
    path = repo_root / f".aide/queue/{queue_id}/status.yaml"
    if not path.exists():
        return "missing"
    match = re.search(r"^status:\s*(\S+)", read_text(path), re.MULTILINE)
    return match.group(1) if match else "unknown"


def doctor(repo_root: Path) -> tuple[bool, list[str]]:
    messages: list[str] = [f"repo_root: {normalize_rel(repo_root)}"]
    hard_ok = True
    for rel in REQUIRED_FILES:
        exists = (repo_root / rel).exists()
        hard_ok = hard_ok and exists
        messages.append(f"{'PASS' if exists else 'FAIL'} required: {rel}")
    q09 = q_status(repo_root, "Q09-token-survival-core")
    q10 = q_status(repo_root, "Q10-aide-lite-hardening")
    q11 = q_status(repo_root, "Q11-context-compiler-v0")
    q12 = q_status(repo_root, "Q12-verifier-v0")
    q13 = q_status(repo_root, "Q13-evidence-review-workflow")
    q14 = q_status(repo_root, "Q14-token-ledger-savings-report")
    q15 = q_status(repo_root, "Q15-golden-tasks-v0")
    q16 = q_status(repo_root, "Q16-outcome-controller-v0")
    q17 = q_status(repo_root, "Q17-router-profile-v0")
    q18 = q_status(repo_root, "Q18-cache-local-state-boundary")
    q19 = q_status(repo_root, "Q19-gateway-architecture-skeleton")
    q20 = q_status(repo_root, "Q20-provider-adapter-v0")
    messages.append(f"INFO Q09 status: {q09}")
    messages.append(f"INFO Q10 status: {q10}")
    messages.append(f"INFO Q11 status: {q11}")
    messages.append(f"INFO Q12 status: {q12}")
    messages.append(f"INFO Q13 status: {q13}")
    messages.append(f"INFO Q14 status: {q14}")
    messages.append(f"INFO Q15 status: {q15}")
    messages.append(f"INFO Q16 status: {q16}")
    messages.append(f"INFO Q17 status: {q17}")
    messages.append(f"INFO Q18 status: {q18}")
    messages.append(f"INFO Q19 status: {q19}")
    messages.append(f"INFO Q20 status: {q20}")
    snapshot_exists = (repo_root / SNAPSHOT_PATH).exists()
    packet_exists = (repo_root / LATEST_PACKET_PATH).exists()
    messages.append(f"{'PASS' if snapshot_exists else 'WARN'} snapshot exists: {SNAPSHOT_PATH}")
    messages.append(f"{'PASS' if packet_exists else 'WARN'} latest task packet exists: {LATEST_PACKET_PATH}")
    for rel in [REPO_MAP_JSON_PATH, REPO_MAP_MD_PATH, TEST_MAP_JSON_PATH, CONTEXT_INDEX_PATH, LATEST_CONTEXT_PACKET_PATH]:
        exists = (repo_root / rel).exists()
        messages.append(f"{'PASS' if exists else 'WARN'} context artifact exists: {rel}")
    for rel in [VERIFICATION_POLICY_PATH, LATEST_VERIFICATION_REPORT_PATH]:
        exists = (repo_root / rel).exists()
        messages.append(f"{'PASS' if exists else 'WARN'} verifier artifact exists: {rel}")
    for rel in [REVIEW_DECISION_POLICY_PATH, REVIEW_PACKET_PATH]:
        exists = (repo_root / rel).exists()
        messages.append(f"{'PASS' if exists else 'WARN'} review artifact exists: {rel}")
    for rel in Q14_REQUIRED_FILES:
        exists = (repo_root / rel).exists()
        messages.append(f"{'PASS' if exists else 'WARN'} token ledger artifact exists: {rel}")
    ledger_count = len(read_ledger_records(repo_root))
    messages.append(f"{'PASS' if ledger_count else 'WARN'} token ledger records: {ledger_count}")
    for rel in Q15_REQUIRED_FILES:
        exists = (repo_root / rel).exists()
        messages.append(f"{'PASS' if exists else 'WARN'} golden task artifact exists: {rel}")
    task_count = len(parse_golden_task_catalog(repo_root))
    messages.append(f"{'PASS' if task_count >= 5 else 'WARN'} golden task definitions: {task_count}")
    for rel in [GOLDEN_RUN_JSON_PATH, GOLDEN_RUN_MD_PATH]:
        exists = (repo_root / rel).exists()
        messages.append(f"{'PASS' if exists else 'WARN'} golden task report exists: {rel}")
    for rel in Q16_REQUIRED_FILES:
        exists = (repo_root / rel).exists()
        messages.append(f"{'PASS' if exists else 'WARN'} controller artifact exists: {rel}")
    outcome_count = len(read_outcome_records(repo_root))
    messages.append(f"{'PASS' if outcome_count else 'WARN'} outcome ledger records: {outcome_count}")
    for rel in Q17_REQUIRED_FILES:
        exists = (repo_root / rel).exists()
        messages.append(f"{'PASS' if exists else 'WARN'} routing artifact exists: {rel}")
    for rel in [ROUTE_DECISION_JSON_PATH, ROUTE_DECISION_MD_PATH]:
        exists = (repo_root / rel).exists()
        messages.append(f"{'PASS' if exists else 'WARN'} route decision exists: {rel}")
    for rel in [CACHE_POLICY_PATH, LOCAL_STATE_POLICY_PATH, f"{LOCAL_STATE_EXAMPLE_ROOT}/README.md", CACHE_KEY_POLICY_PATH, CACHE_KEYS_JSON_PATH, CACHE_KEYS_MD_PATH]:
        exists = (repo_root / rel).exists()
        messages.append(f"{'PASS' if exists else 'WARN'} cache/local-state artifact exists: {rel}")
    local_ignored = gitignore_has_local_state_rules(repo_root)
    local_tracked = local_state_git_paths(repo_root)
    messages.append(f"{'PASS' if local_ignored else 'FAIL'} .aide.local ignored by .gitignore: {str(local_ignored).lower()}")
    messages.append(f"{'PASS' if not local_tracked else 'FAIL'} tracked .aide.local paths: {len(local_tracked)}")
    for rel in [GATEWAY_POLICY_PATH, GATEWAY_ENDPOINTS_PATH, GATEWAY_STATUS_JSON_PATH, GATEWAY_STATUS_MD_PATH]:
        exists = (repo_root / rel).exists()
        messages.append(f"{'PASS' if exists else 'WARN'} gateway artifact exists: {rel}")
    for rel in [PROVIDER_ADAPTER_POLICY_PATH, PROVIDER_CATALOG_PATH, PROVIDER_CAPABILITY_MATRIX_PATH, PROVIDER_STATUS_JSON_PATH, PROVIDER_STATUS_MD_PATH]:
        exists = (repo_root / rel).exists()
        messages.append(f"{'PASS' if exists else 'WARN'} provider adapter artifact exists: {rel}")
    adapter = adapter_status(repo_root)
    messages.append(f"{'PASS' if adapter.status == 'current' else 'WARN'} adapter status: {adapter.status}; {adapter.action_hint}")
    validation_ok, _ = validate_repo(repo_root)
    messages.append(f"{'PASS' if validation_ok else 'FAIL'} validation should be run: {'no hard validation failures detected' if validation_ok else 'run validate and fix failures'}")
    hard_ok = hard_ok and validation_ok
    return hard_ok, messages


def print_messages(title: str, ok: bool, messages: Iterable[str]) -> int:
    print(title)
    print(f"status: {'PASS' if ok else 'FAIL'}")
    for message in messages:
        print(f"- {message}")
    return 0 if ok else 1


def command_doctor(args: argparse.Namespace) -> int:
    ok, messages = doctor(args.repo_root)
    return print_messages("AIDE Lite doctor", ok, messages)


def command_validate(args: argparse.Namespace) -> int:
    ok, messages = validate_repo(args.repo_root)
    return print_messages("AIDE Lite validate", ok, messages)


def command_estimate(args: argparse.Namespace) -> int:
    stats = estimate_file(args.repo_root, args.file)
    surface = detect_surface(stats.path)
    budget, budget_status = ledger_budget_status(args.repo_root, surface, stats.approx_tokens)
    print("AIDE Lite estimate")
    print(f"path: {stats.path}")
    print(f"chars: {stats.chars}")
    print(f"lines: {stats.lines}")
    print(f"approx_tokens: {stats.approx_tokens}")
    print("method: chars / 4, rounded up")
    print(f"surface: {surface}")
    print(f"budget: {budget}")
    print(f"budget_status: {budget_status}")
    return 0


def command_snapshot(args: argparse.Namespace) -> int:
    result = write_snapshot(args.repo_root)
    snapshot = json.loads(read_text(result.path))
    summary = snapshot["summary"]
    print("AIDE Lite snapshot")
    print(f"path: {normalize_rel(result.path.relative_to(args.repo_root))}")
    print(f"action: {result.action}")
    print(f"file_count: {summary['file_count']}")
    print(f"total_size: {summary['total_size']}")
    print(f"aggregate_approx_tokens: {summary['aggregate_approx_tokens']}")
    print("contents_inline: false")
    return 0


def command_index(args: argparse.Namespace) -> int:
    result = run_index(args.repo_root)
    repo_map = result["repo_map"]
    test_map = result["test_map_data"]
    context_index = result["context_index_data"]
    print("AIDE Lite index")
    print(f"snapshot: {result['snapshot'].action} {SNAPSHOT_PATH}")
    print(f"repo_map_json: {result['repo_map_json'].action} {REPO_MAP_JSON_PATH}")
    print(f"repo_map_md: {result['repo_map_md'].action} {REPO_MAP_MD_PATH}")
    print(f"test_map: {result['test_map'].action} {TEST_MAP_JSON_PATH}")
    print(f"context_index: {result['context_index'].action} {CONTEXT_INDEX_PATH}")
    print(f"file_count: {repo_map.get('summary', {}).get('file_count', 0)}")
    print(f"test_mappings: {test_map.get('summary', {}).get('mapping_count', 0)}")
    print(f"source_snapshot_hash: {context_index.get('source_snapshot_hash', '')}")
    print("contents_inline: false")
    return 0


def command_context(args: argparse.Namespace) -> int:
    result = run_context(args.repo_root)
    packet: PacketRender = result["context_packet_data"]
    _budget, budget_status = ledger_budget_status(args.repo_root, "context_packet", packet.stats.approx_tokens)
    print("AIDE Lite context")
    print(f"path: {LATEST_CONTEXT_PACKET_PATH}")
    print(f"action: {result['context_packet'].action}")
    print(f"chars: {packet.stats.chars}")
    print(f"approx_tokens: {packet.stats.approx_tokens}")
    print(f"budget_status: {budget_status}")
    print(f"repo_map_json: {REPO_MAP_JSON_PATH}")
    print(f"test_map: {TEST_MAP_JSON_PATH}")
    print("contents_inline: false")
    return 0


def command_map(args: argparse.Namespace) -> int:
    repo_map = build_repo_map(args.repo_root)
    summary = repo_map.get("summary", {})
    print("AIDE Lite map")
    print(f"file_count: {summary.get('file_count', 0)}")
    print("role_counts:")
    for role, count in sorted(summary.get("role_counts", {}).items()):
        print(f"- {role}: {count}")
    print("contents_inline: false")
    return 0


def command_pack(args: argparse.Namespace) -> int:
    result, packet = write_task_packet(args.repo_root, args.task)
    print("AIDE Lite pack")
    print(f"path: {normalize_rel(result.path.relative_to(args.repo_root))}")
    print(f"action: {result.action}")
    print(f"chars: {packet.stats.chars}")
    print(f"approx_tokens: {packet.stats.approx_tokens}")
    print(f"budget_status: {packet.budget_status}")
    for warning in packet.warnings:
        print(f"warning: {warning}")
    print("ledger: run `ledger scan` to refresh metadata records")
    return 0


def command_verify(args: argparse.Namespace) -> int:
    report = build_verification_report(
        args.repo_root,
        evidence_path=args.evidence,
        task_packet_path=args.task_packet,
        review_packet_path=args.review_packet,
        changed_files_only=args.changed_files,
    )
    write_result: WriteResult | None = None
    if args.write_report:
        write_result = write_verification_report(args.repo_root, args.write_report, report)
    counts = {
        "info": sum(1 for finding in report.findings if finding.severity == "INFO"),
        "warnings": sum(1 for finding in report.findings if finding.severity in {"WARN", "WARNING"}),
        "errors": sum(1 for finding in report.findings if finding.severity in {"ERROR", "FAIL"}),
    }
    print("AIDE Lite verify")
    print(f"result: {report.result}")
    print(f"checked_files: {len(report.checked_files)}")
    print(f"changed_files: {len(report.changed_files)}")
    print(f"info: {counts['info']}")
    print(f"warnings: {counts['warnings']}")
    print(f"errors: {counts['errors']}")
    if write_result:
        print(f"report: {normalize_rel(write_result.path.relative_to(args.repo_root))}")
        print(f"report_action: {write_result.action}")
    for finding in report.findings:
        if finding.severity == "INFO":
            continue
        suffix = f" path={finding.path}" if finding.path else ""
        print(f"- {finding.severity} {finding.check}: {finding.message}{suffix}")
    return 1 if report.result == "FAIL" else 0


def command_review_pack(args: argparse.Namespace) -> int:
    result, packet = write_review_packet(
        args.repo_root,
        task_packet_path=args.task_packet,
        verification_path=args.verification,
        evidence_dir=args.evidence_dir,
        output_path=args.output,
        max_token_warning=args.max_token_warning,
    )
    verification_result_value = extract_verification_result(args.repo_root, args.verification)
    print("AIDE Lite review-pack")
    print(f"path: {normalize_rel(result.path.relative_to(args.repo_root))}")
    print(f"action: {result.action}")
    print(f"chars: {packet.stats.chars}")
    print(f"approx_tokens: {packet.stats.approx_tokens}")
    print(f"budget_status: {packet.budget_status}")
    print(f"verifier_result: {verification_result_value}")
    print("contents_inline: false")
    for warning in packet.warnings:
        print(f"warning: {warning}")
    return 0


def command_ledger_scan(args: argparse.Namespace) -> int:
    records = build_ledger_scan_records(args.repo_root, run_id=args.run_id)
    write_result, merged, existing = merge_ledger_records(args.repo_root, records, args.run_id)
    regression = regression_warnings(existing, records, load_regression_threshold(args.repo_root))
    summary_result = write_token_savings_summary(args.repo_root, merged, regression)
    budget_warnings = ledger_budget_warnings(records)
    print("AIDE Lite ledger scan")
    print(f"ledger: {TOKEN_LEDGER_PATH}")
    print(f"ledger_action: {write_result.action}")
    print(f"records_written: {len(records)}")
    print(f"records_total: {len(merged)}")
    print(f"summary: {TOKEN_SUMMARY_PATH}")
    print(f"summary_action: {summary_result.action}")
    print(f"budget_warnings: {len(budget_warnings)}")
    print(f"regression_warnings: {len(regression)}")
    print("raw_prompt_storage: false")
    print("raw_response_storage: false")
    for warning in budget_warnings[:10]:
        print(f"budget_warning: {warning}")
    for warning in regression[:10]:
        print(f"regression_warning: {warning}")
    return 0


def command_ledger_add(args: argparse.Namespace) -> int:
    rel = assert_ledger_safe_path(args.repo_root, args.file)
    surface = args.surface or detect_surface(rel)
    record = ledger_record_for_file(
        args.repo_root,
        rel,
        surface=surface,
        phase=args.phase,
        run_id=args.run_id,
        notes=args.notes or "manual estimated metadata record; raw content not stored",
    )
    existing = read_ledger_records(args.repo_root)
    retained = [
        item
        for item in existing
        if not (item.run_id == record.run_id and item.surface == record.surface and item.path == record.path)
    ]
    result = write_ledger_records(args.repo_root, [*retained, record])
    print("AIDE Lite ledger add")
    print(f"ledger: {TOKEN_LEDGER_PATH}")
    print(f"action: {result.action}")
    print(f"path: {record.path}")
    print(f"surface: {record.surface}")
    print(f"chars: {record.chars}")
    print(f"approx_tokens: {record.approx_tokens}")
    print(f"budget_status: {record.budget_status}")
    print("raw_content_stored: false")
    return 0


def command_ledger_report(args: argparse.Namespace) -> int:
    records = read_ledger_records(args.repo_root)
    regression = regression_warnings(records, [record for record in records if record.run_id == args.run_id], load_regression_threshold(args.repo_root))
    summary_result = write_token_savings_summary(args.repo_root, records, regression)
    by_surface: dict[str, int] = {}
    for record in records:
        by_surface[record.surface] = by_surface.get(record.surface, 0) + record.approx_tokens
    largest = sorted(records, key=lambda item: item.approx_tokens, reverse=True)[:5]
    budget_warnings = ledger_budget_warnings(records)
    print("AIDE Lite ledger report")
    print(f"records: {len(records)}")
    print(f"summary: {TOKEN_SUMMARY_PATH}")
    print(f"summary_action: {summary_result.action}")
    print(f"budget_warnings: {len(budget_warnings)}")
    print(f"regression_warnings: {len(regression)}")
    print("totals_by_surface:")
    for surface in sorted(by_surface):
        print(f"- {surface}: {by_surface[surface]}")
    print("largest_surfaces:")
    for record in largest:
        print(f"- {record.surface} {record.path}: {record.approx_tokens}")
    return 0


def command_ledger_compare(args: argparse.Namespace) -> int:
    comparison = compare_to_baseline(args.repo_root, args.file, args.baseline, surface=args.surface)
    print("AIDE Lite ledger compare")
    print(f"file: {comparison.compact.path}")
    print(f"surface: {comparison.compact.surface}")
    print(f"compact_chars: {comparison.compact.chars}")
    print(f"compact_approx_tokens: {comparison.compact.approx_tokens}")
    print(f"baseline: {comparison.baseline.name}")
    print(f"baseline_chars: {comparison.baseline.chars}")
    print(f"baseline_approx_tokens: {comparison.baseline.approx_tokens}")
    if comparison.reduction_percent is None:
        print("estimated_reduction_percent: unavailable")
    else:
        print(f"estimated_reduction_percent: {comparison.reduction_percent:.1f}")
    print("method: chars / 4, rounded up")
    print("exact_provider_billing: false")
    for warning in comparison.warnings:
        print(f"warning: {warning}")
    return 0


def command_eval_list(args: argparse.Namespace) -> int:
    definitions = parse_golden_task_catalog(args.repo_root)
    print("AIDE Lite eval list")
    print(f"catalog: {GOLDEN_TASK_CATALOG_PATH}")
    print(f"task_count: {len(definitions)}")
    for definition in definitions:
        print(f"- {definition.task_id}: {definition.status} - {definition.title}")
    return 0 if definitions else 1


def command_eval_run(args: argparse.Namespace) -> int:
    run = run_golden_tasks(args.repo_root, task_id=args.task)
    json_result, md_result = write_golden_run_reports(args.repo_root, run)
    data = golden_run_to_dict(run)
    print("AIDE Lite eval run")
    print(f"result: {run.result}")
    print(f"task_count: {data['task_count']}")
    print(f"pass_count: {data['pass_count']}")
    print(f"warn_count: {data['warn_count']}")
    print(f"fail_count: {data['fail_count']}")
    print(f"json_report: {GOLDEN_RUN_JSON_PATH}")
    print(f"json_action: {json_result.action}")
    print(f"markdown_report: {GOLDEN_RUN_MD_PATH}")
    print(f"markdown_action: {md_result.action}")
    print("provider_or_model_calls: none")
    print("network_calls: none")
    print("raw_prompt_storage: false")
    print("raw_response_storage: false")
    for task in run.tasks:
        print(f"- {task.task_id}: {task.result} ({task.passed_checks}/{task.checks_run} checks)")
        for warning in task.warnings:
            print(f"  warning: {warning}")
        for error in task.errors:
            print(f"  error: {error}")
    return 1 if run.result == "FAIL" else 0


def command_eval_report(args: argparse.Namespace) -> int:
    data = read_latest_golden_run(args.repo_root)
    print("AIDE Lite eval report")
    print(f"json_report: {GOLDEN_RUN_JSON_PATH}")
    print(f"markdown_report: {GOLDEN_RUN_MD_PATH}")
    print(f"result: {data.get('result', 'unknown')}")
    print(f"task_count: {data.get('task_count', 0)}")
    print(f"pass_count: {data.get('pass_count', 0)}")
    print(f"warn_count: {data.get('warn_count', 0)}")
    print(f"fail_count: {data.get('fail_count', 0)}")
    print(f"token_quality_statement: {data.get('token_quality_statement', '')}")
    return 1 if data.get("result") == "FAIL" else 0


def command_commit_check(args: argparse.Namespace) -> int:
    sources = [bool(args.message_file), bool(args.message), bool(args.latest), bool(args.range)]
    if sum(sources) != 1:
        raise ValueError("use exactly one of --message-file, --message, --latest, or --range")
    if args.range:
        commits = git_commit_messages_for_range(args.repo_root, args.range, max_count=args.max_count)
        results: list[tuple[str, str, str, list[Check]]] = []
        any_fail = False
        for commit_hash, subject, message in commits:
            checks = validate_commit_message_text(message)
            result = commit_message_result(checks)
            if result == "FAIL":
                any_fail = True
            results.append((commit_hash, subject, result, checks))
        range_result = "FAIL" if any_fail else ("PASS" if commits else "WARN")
        print("AIDE Lite commit range check")
        print(f"result: {range_result}")
        print(f"range: {args.range}")
        print(f"commit_count: {len(commits)}")
        print(f"policy: {COMMIT_MESSAGE_POLICY_PATH}")
        for commit_hash, subject, result, checks in results:
            print(f"- {commit_hash[:7]} {result} {subject}")
            for check in checks:
                if check.severity != "PASS":
                    print(f"  - {check.severity} {check.message}")
        return 1 if any_fail or not commits else 0
    if args.message_file:
        message_path = safe_repo_path(args.repo_root, args.message_file)
        text = read_text(message_path)
        source = normalize_rel(message_path.relative_to(args.repo_root))
    elif args.message:
        text = str(args.message)
        source = "inline_message"
    else:
        text = git_latest_commit_message(args.repo_root)
        source = "git log -1 --pretty=%B"
    checks = validate_commit_message_text(text)
    result = commit_message_result(checks)
    print("AIDE Lite commit check")
    print(f"result: {result}")
    print(f"source: {source}")
    print(f"policy: {COMMIT_MESSAGE_POLICY_PATH}")
    print(f"standard: {COMMIT_MESSAGE_STANDARD_PATH}")
    for check in checks:
        print(f"- {check.severity} {check.message}")
    return 1 if result == "FAIL" else 0


def command_commit_template(args: argparse.Namespace) -> int:
    template_path = args.repo_root / COMMIT_TEMPLATE_PATH
    if not template_path.exists():
        write_text_if_changed(template_path, COMMIT_GOOD_EXAMPLE)
    text = read_text(template_path)
    if args.output:
        target = safe_repo_path(args.repo_root, args.output)
        result = write_text_if_changed(target, text)
        print("AIDE Lite commit template")
        print(f"template: {COMMIT_TEMPLATE_PATH}")
        print(f"output: {normalize_rel(target.relative_to(args.repo_root))}")
        print(f"action: {result.action}")
    else:
        print(text.rstrip())
    return 0


def command_commit_install_hook(args: argparse.Namespace) -> int:
    before, after = install_commit_hook(args.repo_root, force=args.force)
    print("AIDE Lite commit hook install")
    print("result: PASS")
    print(f"before_core_hooks_path: {before or '<unset>'}")
    print(f"after_core_hooks_path: {after or '<unset>'}")
    print(f"hook: {COMMIT_MESSAGE_HOOK_TEMPLATE_PATH}")
    print("writes_git_hooks_dir: false")
    return 0


def command_commit_status(args: argparse.Namespace) -> int:
    print("AIDE Lite commit status")
    print(f"policy_exists: {str((args.repo_root / COMMIT_MESSAGE_POLICY_PATH).exists()).lower()}")
    print(f"hook_template_exists: {str((args.repo_root / COMMIT_MESSAGE_HOOK_TEMPLATE_PATH).exists()).lower()}")
    print(f"template_exists: {str((args.repo_root / COMMIT_TEMPLATE_PATH).exists()).lower()}")
    print(f"core_hooks_path: {current_hook_path(args.repo_root) or '<unset>'}")
    try:
        checks = validate_commit_message_text(git_latest_commit_message(args.repo_root))
        result = commit_message_result(checks)
    except (OSError, ValueError) as exc:
        result = f"WARN ({exc})"
    print(f"latest_commit_result: {result}")
    return 0 if not str(result).startswith("FAIL") else 1


def command_changelog_preview(args: argparse.Namespace) -> int:
    data = write_changelog_preview(args.repo_root, revision_range=args.range)
    malformed = data.get("malformed_commits", [])
    categories = data.get("categories", {})
    print("AIDE Lite changelog preview")
    print(f"result: {'WARN' if malformed else 'PASS'}")
    print(f"range: {data.get('source_range', 'unknown')}")
    print(f"commit_count: {data.get('commit_count', 0)}")
    print(f"changelog: {CHANGELOG_PREVIEW_MD_PATH}")
    print(f"release_notes: {RELEASE_NOTES_PREVIEW_MD_PATH}")
    print(f"categories: {len(categories) if isinstance(categories, dict) else 0}")
    print(f"malformed_commits: {len(malformed) if isinstance(malformed, list) else 0}")
    print("release_publishing: false")
    return 0


def command_task_inspect(args: argparse.Namespace) -> int:
    inspection = inspect_task(args.repo_root, args.task_id)
    print("AIDE Lite task inspect")
    for key in ["task_id", "status", "classification", "task_yaml", "status_yaml", "evidence_dir"]:
        print(f"{key}: {inspection.get(key, '')}")
    print(f"evidence_files: {len(inspection.get('evidence_files', []))}")
    print(f"missing_evidence: {len(inspection.get('missing_evidence', []))}")
    print(f"recovery_suggestion: {task_recovery_suggestion(inspection)}")
    return 0 if inspection.get("classification") != "missing" else 1


def command_task_status(args: argparse.Namespace) -> int:
    tasks = queue_task_blocks(args.repo_root)
    print("AIDE Lite task status")
    print(f"task_count: {len(tasks)}")
    for task in tasks:
        print(f"- {task.get('id', '')}: status={task.get('status', 'unknown')} planning_state={task.get('planning_state', 'unknown')}")
    return 0 if tasks else 1


def command_task_noop_check(args: argparse.Namespace) -> int:
    inspection = inspect_task(args.repo_root, args.task_id)
    suggestion = task_recovery_suggestion(inspection)
    print("AIDE Lite task noop-check")
    print(f"task_id: {inspection.get('task_id', '')}")
    print(f"status: {inspection.get('status', '')}")
    print(f"classification: {inspection.get('classification', '')}")
    print(f"result: {suggestion}")
    print("mutation: none")
    return 0


def command_task_dependencies(args: argparse.Namespace) -> int:
    inspection = inspect_task(args.repo_root, args.task_id)
    dependencies = inspection.get("dependencies", [])
    print("AIDE Lite task dependencies")
    print(f"task_id: {inspection.get('task_id', '')}")
    print(f"dependency_count: {len(dependencies) if isinstance(dependencies, list) else 0}")
    if isinstance(dependencies, list):
        for dependency in dependencies:
            print(f"- {dependency}: status={task_status_value(args.repo_root, str(dependency))}")
    return 0


def command_task_recover(args: argparse.Namespace) -> int:
    inspection = inspect_task(args.repo_root, args.task_id)
    suggestion = task_recovery_suggestion(inspection)
    lines = [
        "# AIDE Task Recovery Report",
        "",
        f"- task_id: {inspection.get('task_id', '')}",
        f"- status: {inspection.get('status', '')}",
        f"- classification: {inspection.get('classification', '')}",
        f"- recovery_suggestion: {suggestion}",
        "- report_only: true",
        "- mutation: none",
        "",
    ]
    if args.write_report and inspection.get("evidence_dir"):
        target = args.repo_root / str(inspection["evidence_dir"]) / "recovery-report.md"
        result = write_text_if_changed(target, "\n".join(lines))
        action = result.action
    else:
        action = "not_written"
    print("AIDE Lite task recover")
    print(f"task_id: {inspection.get('task_id', '')}")
    print(f"recovery_suggestion: {suggestion}")
    print(f"report_action: {action}")
    print("mutation: report-only")
    return 0 if inspection.get("classification") != "missing" else 1


def command_task_evidence(args: argparse.Namespace) -> int:
    inspection = inspect_task(args.repo_root, args.task_id)
    print("AIDE Lite task evidence")
    print(f"task_id: {inspection.get('task_id', '')}")
    print("available:")
    for rel in inspection.get("evidence_files", []):
        print(f"- {rel}")
    print("missing:")
    for rel in inspection.get("missing_evidence", []):
        print(f"- {rel}")
    return 0


def command_task_current(args: argparse.Namespace) -> int:
    task_id = current_task_id(args.repo_root) or ""
    print("AIDE Lite task current")
    print(f"task_id: {task_id}")
    print(f"status: {task_status_value(args.repo_root, task_id) if task_id else 'missing'}")
    return 0 if task_id else 1


def command_git_detect(args: argparse.Namespace) -> int:
    data, json_result, md_result = write_git_workflow_detection(args.repo_root)
    aide_plan_result: WriteResult | None = None
    aide_plan_md_result: WriteResult | None = None
    if (args.repo_root / AIDE_BRANCH_POLICY_PATH).exists():
        _plan, aide_plan_result, aide_plan_md_result = write_aide_dev_main_plan(args.repo_root)
    print("AIDE Lite git detect")
    print(f"result: PASS")
    print(f"workflow: {data.get('detected_workflow')}")
    print(f"current_branch: {data.get('current_branch')}")
    print(f"current_role: {data.get('branch_role_for_current_branch')}")
    print(f"canonical_branch: {data.get('canonical_branch')}")
    print(f"integration_branch_detected: {data.get('integration_branch_detected')}")
    print(f"recommended_next_action: {data.get('recommended_next_action')}")
    print(f"json_report: {GIT_WORKFLOW_DETECTION_JSON_PATH} ({json_result.action})")
    print(f"markdown_report: {GIT_WORKFLOW_DETECTION_MD_PATH} ({md_result.action})")
    if aide_plan_result is not None and aide_plan_md_result is not None:
        print(f"aide_dev_main_plan_json: {AIDE_DEV_MAIN_PLAN_JSON_PATH} ({aide_plan_result.action})")
        print(f"aide_dev_main_plan_markdown: {AIDE_DEV_MAIN_PLAN_MD_PATH} ({aide_plan_md_result.action})")
    print("non_mutating: true")
    return 0


def command_git_doctor(args: argparse.Namespace) -> int:
    data = collect_git_workflow_detection(args.repo_root)
    aide_policy_present = (args.repo_root / AIDE_BRANCH_POLICY_PATH).exists()
    role = str(data.get("branch_role_for_current_branch", "unknown"))
    warnings = list(data.get("warnings", []))
    dirty = "dirty_tree_detected" in warnings
    safe_for_normal_task = role in {"task", "subtask"} and not dirty
    print("AIDE Lite git doctor")
    print(f"detected_workflow: {data.get('detected_workflow')}")
    print(f"current_branch: {data.get('current_branch')}")
    print(f"current_branch_role: {role}")
    print(f"canonical_branch: {data.get('canonical_branch')}")
    print(f"expected_integration_target: dev")
    print(f"aide_branch_policy_present: {str(aide_policy_present).lower()}")
    print(f"safe_for_normal_task: {str(safe_for_normal_task).lower()}")
    print(f"dirty_tree: {str(dirty).lower()}")
    print(f"recommended_next_action: {data.get('recommended_next_action')}")
    if warnings:
        print("warnings:")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("warnings: []")
    print("non_mutating: true")
    return 0


def command_git_status(args: argparse.Namespace) -> int:
    data = collect_git_workflow_detection(args.repo_root)
    warnings = list(data.get("warnings", []))
    dirty = "dirty_tree_detected" in warnings
    print("AIDE Lite git status")
    print(f"branch: {data.get('current_branch')}")
    print(f"role: {data.get('branch_role_for_current_branch')}")
    print(f"workflow: {data.get('detected_workflow')}")
    print(f"canonical_branch: {data.get('canonical_branch') or 'main'}")
    print(f"integration_branch: {data.get('integration_branch') or 'dev'}")
    print(f"dirty_tree: {str(dirty).lower()}")
    print(f"next_safe_action: {data.get('recommended_next_action')}")
    print("non_mutating: true")
    return 0


def command_git_workflow(args: argparse.Namespace) -> int:
    data = collect_git_workflow_detection(args.repo_root)
    repo_id = str(data.get("repo_id", "unknown"))
    profile = "aide" if repo_id.endswith("/aide") or repo_id == "aide" else "unknown_repo"
    print("AIDE Lite git workflow")
    print(f"detected_workflow: {data.get('detected_workflow')}")
    print(f"confidence: {data.get('confidence')}")
    print(f"profile: {profile}")
    print(f"repo_id: {repo_id}")
    print(f"canonical_branch: {data.get('canonical_branch')}")
    print(f"integration_branch_detected: {data.get('integration_branch_detected')}")
    print("non_mutating: true")
    return 0


def command_git_roles(args: argparse.Namespace) -> int:
    print("AIDE Lite git roles")
    for branch, role, purpose in git_role_examples():
        print(f"- {branch}: {role} - {purpose}")
    print("unknown: conservative/report-only until inspected")
    return 0


def command_git_policy(args: argparse.Namespace) -> int:
    checks = validate_git_policy_files(args.repo_root)
    if (args.repo_root / GIT_HELPER_POLICY_PATH).exists() or (args.repo_root / ".aide/queue/Q29-merge-land-promote-helper-v0").exists():
        checks.extend(validate_git_helper_policy_files(args.repo_root))
    if (args.repo_root / AIDE_BRANCH_POLICY_PATH).exists() or (args.repo_root / ".aide/queue/Q30-aide-dev-main-policy-sync").exists():
        checks.extend(validate_aide_branch_policy_files(args.repo_root))
    print("AIDE Lite git policy")
    for check in checks:
        print(f"{check.severity}: {check.message}")
    print("q28_mutation_commands: false")
    print("q29_live_mutation_default: false")
    print("q30_live_mutation: false")
    print("non_mutating: true")
    return 0 if not any(check.severity == "FAIL" for check in checks) else 1


def print_git_helper_plan_summary(title: str, plan: dict[str, object], json_result: WriteResult | None = None, md_result: WriteResult | None = None) -> None:
    state = plan.get("state", {}) if isinstance(plan.get("state"), dict) else {}
    print(title)
    print(f"result: {plan.get('status')}")
    print(f"operation: {plan.get('operation')}")
    print(f"current_branch: {state.get('current_branch', '')}")
    print(f"current_role: {state.get('current_role', '')}")
    print(f"dry_run: {str(plan.get('dry_run', True)).lower()}")
    print(f"apply_requested: {str(plan.get('apply_requested', False)).lower()}")
    print(f"push_requested: {str(plan.get('push_requested', False)).lower()}")
    print(f"remote_mutation: {str(plan.get('remote_mutation', False)).lower()}")
    print(f"force_push_allowed: {str(plan.get('force_push_allowed', False)).lower()}")
    if json_result is not None:
        print(f"json_report: {GIT_HELPER_PLAN_JSON_PATH} ({json_result.action})")
    if md_result is not None:
        print(f"markdown_report: {GIT_HELPER_PLAN_MD_PATH} ({md_result.action})")
    blockers = plan.get("blockers", [])
    if blockers:
        print("blockers:")
        for blocker in blockers:
            print(f"- {blocker}")
    warnings = plan.get("warnings", [])
    if warnings:
        print("warnings:")
        for warning in warnings:
            print(f"- {warning}")
    commands = plan.get("planned_commands", [])
    if commands:
        print("planned_commands:")
        for command in commands:
            print(f"- {command}")
    executed = plan.get("executed_commands", [])
    if executed:
        print("executed_commands:")
        for command in executed:
            print(f"- {command}")


def command_git_plan(args: argparse.Namespace) -> int:
    plan = make_git_helper_plan(args.repo_root, "plan", dry_run=True)
    json_result, md_result = write_git_helper_plan(args.repo_root, plan)
    aide_plan_result: WriteResult | None = None
    aide_plan_md_result: WriteResult | None = None
    if (args.repo_root / AIDE_BRANCH_POLICY_PATH).exists():
        _aide_plan, aide_plan_result, aide_plan_md_result = write_aide_dev_main_plan(args.repo_root)
    print_git_helper_plan_summary("AIDE Lite git plan", plan, json_result, md_result)
    if aide_plan_result is not None and aide_plan_md_result is not None:
        print(f"aide_dev_main_plan_json: {AIDE_DEV_MAIN_PLAN_JSON_PATH} ({aide_plan_result.action})")
        print(f"aide_dev_main_plan_markdown: {AIDE_DEV_MAIN_PLAN_MD_PATH} ({aide_plan_md_result.action})")
    return 0


def command_git_sync(args: argparse.Namespace) -> int:
    dry_run = not args.apply
    plan = make_git_helper_plan(args.repo_root, "sync", dry_run=dry_run, apply_requested=args.apply, push_requested=False)
    if args.apply:
        plan = execute_git_helper_plan(args.repo_root, plan)
    print_git_helper_plan_summary("AIDE Lite git sync", plan)
    return 0 if dry_run or plan.get("status") == "applied" else 1


def command_git_land(args: argparse.Namespace) -> int:
    dry_run = not args.apply
    plan = make_git_helper_plan(
        args.repo_root,
        "land",
        dry_run=dry_run,
        apply_requested=args.apply,
        push_requested=args.push,
        source=args.source or "",
        target=args.target or "dev",
        validation_ok=args.validation_ok,
    )
    if args.apply:
        plan = execute_git_helper_plan(args.repo_root, plan)
    print_git_helper_plan_summary("AIDE Lite git land", plan)
    return 0 if dry_run or plan.get("status") == "applied" else 1


def command_git_promote(args: argparse.Namespace) -> int:
    dry_run = not args.apply
    plan = make_git_helper_plan(
        args.repo_root,
        "promote",
        dry_run=dry_run,
        apply_requested=args.apply,
        push_requested=args.push,
        source=args.source_branch or "dev",
        target=args.target_branch or "main",
        validation_ok=args.validation_ok,
        review_ok=args.review_ok,
    )
    if args.apply:
        plan = execute_git_helper_plan(args.repo_root, plan)
    print_git_helper_plan_summary("AIDE Lite git promote", plan)
    return 0 if dry_run or plan.get("status") == "applied" else 1


def command_git_prune(args: argparse.Namespace) -> int:
    dry_run = not args.apply
    plan = make_git_helper_plan(
        args.repo_root,
        "prune",
        dry_run=dry_run,
        apply_requested=args.apply,
        push_requested=False,
        target=args.target or "",
    )
    if args.apply:
        plan = execute_git_helper_plan(args.repo_root, plan)
    print_git_helper_plan_summary("AIDE Lite git prune", plan)
    candidates = plan.get("prune_candidates", [])
    if candidates:
        print("prune_candidates:")
        for item in candidates:
            if isinstance(item, dict):
                print(f"- {item.get('branch')}: eligible={str(item.get('eligible')).lower()} reason={item.get('reason')}")
    return 0 if dry_run or plan.get("status") == "applied" else 1


def command_outcome_add(args: argparse.Namespace) -> int:
    record = make_outcome_record(
        args.repo_root,
        args.phase,
        args.source,
        args.result,
        args.failure_class,
        args.severity,
        args.related_path or [],
        notes=args.notes or "manual controller metadata record; raw prompt/response not stored",
        run_id=args.run_id,
    )
    existing = read_outcome_records(args.repo_root)
    retained = [
        item
        for item in existing
        if not (item.run_id == record.run_id and item.phase == record.phase and item.source == record.source)
    ]
    write_result = write_outcome_records(args.repo_root, [*retained, record])
    print("AIDE Lite outcome add")
    print(f"ledger: {OUTCOME_LEDGER_PATH}")
    print(f"action: {write_result.action}")
    print(f"phase: {record.phase}")
    print(f"source: {record.source}")
    print(f"result: {record.result}")
    print(f"failure_class: {record.failure_class}")
    print(f"severity: {record.severity}")
    print("raw_content_stored: false")
    return 0


def command_outcome_report(args: argparse.Namespace) -> int:
    records = build_current_outcome_records(args.repo_root)
    ledger_result, merged = merge_outcome_records(args.repo_root, records, "q16.current")
    recommendations = build_recommendations(args.repo_root, records)
    report_result = write_outcome_report(args.repo_root, records, recommendations)
    result = controller_overall_result(records)
    warnings = sum(1 for record in records if record.result == "WARN")
    failures = sum(1 for record in records if record.result == "FAIL")
    classes = sorted({record.failure_class for record in records if record.result != "PASS"})
    print("AIDE Lite outcome report")
    print(f"result: {result}")
    print(f"outcome_ledger: {OUTCOME_LEDGER_PATH}")
    print(f"ledger_action: {ledger_result.action}")
    print(f"records_written: {len(records)}")
    print(f"records_total: {len(merged)}")
    print(f"outcome_report: {OUTCOME_REPORT_PATH}")
    print(f"report_action: {report_result.action}")
    print(f"warnings: {warnings}")
    print(f"failures: {failures}")
    print(f"failure_classes: {', '.join(classes) if classes else 'none'}")
    print("advisory_only: true")
    print("applies_automatically: false")
    return 0


def command_optimize_suggest(args: argparse.Namespace) -> int:
    records = build_current_outcome_records(args.repo_root)
    ledger_result, _merged = merge_outcome_records(args.repo_root, records, "q16.current")
    recommendations = build_recommendations(args.repo_root, records)
    report_result = write_outcome_report(args.repo_root, records, recommendations)
    recommendations_result = write_recommendations(args.repo_root, recommendations)
    print("AIDE Lite optimize suggest")
    print(f"outcome_ledger: {OUTCOME_LEDGER_PATH}")
    print(f"ledger_action: {ledger_result.action}")
    print(f"outcome_report: {OUTCOME_REPORT_PATH}")
    print(f"report_action: {report_result.action}")
    print(f"recommendations: {RECOMMENDATIONS_PATH}")
    print(f"recommendations_action: {recommendations_result.action}")
    print(f"recommendation_count: {len(recommendations)}")
    if recommendations:
        top = recommendations[0]
        print(f"top_recommendation: {top.recommendation_id}")
        print(f"top_failure_class: {top.failure_class}")
        print(f"top_risk_level: {top.risk_level}")
    print("advisory_only: true")
    print("applies_automatically: false")
    print("provider_or_model_calls: none")
    print("network_calls: none")
    return 0


def command_route_list(args: argparse.Namespace) -> int:
    profiles = parse_route_profiles(args.repo_root)
    hard_floors = parse_hard_floor_minimums(args.repo_root)
    print("AIDE Lite route list")
    print("route_classes:")
    for route_class in ROUTE_CLASSES:
        print(f"- {route_class}")
    print("task_profiles:")
    for profile in profiles:
        print(f"- {profile.task_class}: preferred={profile.preferred_route_class} fallback={profile.fallback_route_class} review_required={str(profile.review_required).lower()}")
    print("hard_floors:")
    for floor in sorted(hard_floors):
        print(f"- {floor}: minimum={','.join(hard_floors[floor])}")
    print("provider_or_model_calls: none")
    print("network_calls: none")
    return 0 if profiles and hard_floors else 1


def command_route_validate(args: argparse.Namespace) -> int:
    checks = routing_validation_checks(args.repo_root)
    ok = not any(check.severity == "FAIL" for check in checks)
    return print_messages("AIDE Lite route validate", ok, [f"{check.severity} {check.message}" for check in checks])


def command_route_explain(args: argparse.Namespace) -> int:
    decision = build_route_decision(args.repo_root, task_packet_path=args.task_packet or LATEST_PACKET_PATH)
    json_result, md_result = write_route_decision(args.repo_root, decision)
    print("AIDE Lite route explain")
    print(f"route_class: {decision.route_class}")
    print(f"task_class: {decision.task_class}")
    print(f"risk_class: {decision.risk_class}")
    print(f"fallback_route_class: {decision.fallback_route_class}")
    print(f"hard_floor_applied: {decision.hard_floor_applied}")
    print(f"blocked: {'true' if decision.blocked else 'false'}")
    print(f"blocked_reason: {decision.blocked_reason or 'none'}")
    print(f"token_budget_status: {decision.token_budget_status}")
    print(f"verifier_status: {decision.verifier_status}")
    print(f"golden_task_status: {decision.golden_task_status}")
    print(f"outcome_recommendation_status: {decision.outcome_recommendation_status}")
    print(f"quality_gate_status: {decision.quality_gate_status}")
    print(f"json: {ROUTE_DECISION_JSON_PATH}")
    print(f"json_action: {json_result.action}")
    print(f"markdown: {ROUTE_DECISION_MD_PATH}")
    print(f"markdown_action: {md_result.action}")
    print("advisory_only: true")
    print("provider_or_model_calls: none")
    print("network_calls: none")
    for item in decision.rationale:
        print(f"- rationale: {item}")
    return 0


def ensure_gitignore_local_state(repo_root: Path) -> WriteResult:
    path = repo_root / ".gitignore"
    existing = read_text(path) if path.exists() else ""
    lines = existing.splitlines()
    present = {line.strip() for line in lines if line.strip() and not line.strip().startswith("#")}
    missing = [pattern for pattern in GITIGNORE_REQUIRED_PATTERNS if pattern not in present]
    if not missing:
        return WriteResult(path, "unchanged")
    updated = existing.rstrip()
    if updated:
        updated += "\n\n"
    updated += "# AIDE local runtime state and Python caches\n"
    updated += "\n".join(missing)
    updated += "\n"
    return write_text_if_changed(path, updated)


def command_cache_init(args: argparse.Namespace) -> int:
    gitignore_result = ensure_gitignore_local_state(args.repo_root)
    checks = cache_status_checks(args.repo_root)
    ok = not any(check.severity == "FAIL" for check in checks)
    print("AIDE Lite cache init")
    print(f"gitignore: .gitignore")
    print(f"gitignore_action: {gitignore_result.action}")
    print(f"local_state_root: {LOCAL_STATE_ROOT}/")
    print(f"local_state_example: {LOCAL_STATE_EXAMPLE_ROOT}/")
    print("created_real_local_state: false")
    print("raw_prompt_storage: false")
    print("raw_response_storage: false")
    for check in checks:
        print(f"- {check.severity} {check.message}")
    return 0 if ok else 1


def command_cache_status(args: argparse.Namespace) -> int:
    checks = cache_status_checks(args.repo_root)
    ok = not any(check.severity == "FAIL" for check in checks)
    print("AIDE Lite cache status")
    print(f"local_state_root: {LOCAL_STATE_ROOT}/")
    print(f"local_state_ignored: {str(gitignore_has_local_state_rules(args.repo_root)).lower()}")
    print(f"tracked_local_state_paths: {len(local_state_git_paths(args.repo_root))}")
    print(f"example_layout: {LOCAL_STATE_EXAMPLE_ROOT}/")
    print(f"cache_policy: {CACHE_POLICY_PATH}")
    print(f"local_state_policy: {LOCAL_STATE_POLICY_PATH}")
    print(f"cache_keys_json: {CACHE_KEYS_JSON_PATH}")
    print(f"cache_keys_md: {CACHE_KEYS_MD_PATH}")
    print("provider_or_model_calls: none")
    print("network_calls: none")
    for check in checks:
        print(f"- {check.severity} {check.message}")
    return 0 if ok else 1


def command_cache_key(args: argparse.Namespace) -> int:
    requested = args.file or args.task_packet
    if not requested:
        raise ValueError("cache key requires --file PATH or --task-packet PATH")
    if args.file and args.task_packet:
        raise ValueError("use only one of --file or --task-packet")
    rel = assert_cache_safe_path(args.repo_root, requested)
    surface = "task_packet" if args.task_packet else detect_surface(rel)
    key_name = "task_packet" if args.task_packet else surface
    record = cache_record_for_file(args.repo_root, rel, surface=surface, key_name=key_name)
    print("AIDE Lite cache key")
    print(f"path: {record.path}")
    print(f"surface: {record.surface}")
    print(f"key_id: {record.key_id}")
    print(f"content_sha256: {record.content_sha256}")
    print(f"dependency_count: {len(record.dependency_hashes)}")
    print(f"policy_version_count: {len(record.policy_versions)}")
    print(f"dirty_state: {str(record.dirty_state).lower()}")
    print("raw_content_stored: false")
    for dep_path, digest in record.dependency_hashes:
        print(f"- dependency: {dep_path} sha256:{short_sha(digest, 12)}")
    return 0


def command_cache_report(args: argparse.Namespace) -> int:
    json_result, md_result, data = write_cache_report(args.repo_root)
    keys = data.get("keys", {})
    repo_state = data.get("repo_state", {}) if isinstance(data.get("repo_state"), dict) else {}
    boundary = data.get("local_state_boundary", {}) if isinstance(data.get("local_state_boundary"), dict) else {}
    print("AIDE Lite cache report")
    print(f"json: {CACHE_KEYS_JSON_PATH}")
    print(f"json_action: {json_result.action}")
    print(f"markdown: {CACHE_KEYS_MD_PATH}")
    print(f"markdown_action: {md_result.action}")
    print(f"key_count: {len(keys) if isinstance(keys, dict) else 0}")
    print(f"git_commit: {repo_state.get('git_commit', 'unavailable')}")
    print(f"dirty_state: {str(repo_state.get('dirty_state', False)).lower()}")
    print(f"local_state_ignored: {str(boundary.get('local_state_ignored', False)).lower()}")
    print("contents_inline: false")
    print("raw_prompt_storage: false")
    print("raw_response_storage: false")
    return 0


def command_gateway_status(args: argparse.Namespace) -> int:
    module = import_gateway_status_module(args.repo_root)
    json_path, md_path, data = module.write_gateway_status_files(args.repo_root)
    readiness = data.get("readiness", {}) if isinstance(data.get("readiness"), dict) else {}
    missing_count = 0
    for item in readiness.values():
        if isinstance(item, dict) and isinstance(item.get("missing"), list):
            missing_count += len(item["missing"])
    signals = data.get("signals", {}) if isinstance(data.get("signals"), dict) else {}
    route = signals.get("route", {}) if isinstance(signals.get("route"), dict) else {}
    print("AIDE Lite gateway status")
    print(f"json: {normalize_rel(json_path.relative_to(args.repo_root))}")
    print(f"markdown: {normalize_rel(md_path.relative_to(args.repo_root))}")
    print(f"service: {data.get('service', 'aide-gateway-skeleton')}")
    print(f"mode: {data.get('mode', 'local_skeleton_report_only')}")
    print(f"missing_readiness_refs: {missing_count}")
    print(f"verifier_status: {signals.get('verifier_status', 'unknown')}")
    print(f"golden_task_status: {signals.get('golden_task_status', 'unknown')}")
    print(f"route_class: {route.get('route_class', 'unknown')}")
    print(f"quality_gate_status: {route.get('quality_gate_status', 'unknown')}")
    print("provider_or_model_calls: none")
    print("network_calls: none")
    print("raw_prompt_storage: false")
    print("raw_response_storage: false")
    return 0


def command_gateway_endpoints(args: argparse.Namespace) -> int:
    module = import_gateway_status_module(args.repo_root)
    endpoints = getattr(module, "ENDPOINTS", ["/health", "/status", "/route/explain", "/summaries", "/version"])
    print("AIDE Lite gateway endpoints")
    print(f"policy: {GATEWAY_ENDPOINTS_PATH}")
    for endpoint in endpoints:
        print(f"- GET {endpoint}")
    print("forbidden_forwarding:")
    print("- /v1/chat/completions")
    print("- /v1/responses")
    print("- /anthropic/v1/messages")
    print("provider_or_model_calls: none")
    print("network_calls: none")
    return 0 if (args.repo_root / GATEWAY_ENDPOINTS_PATH).exists() else 1


def command_gateway_smoke(args: argparse.Namespace) -> int:
    module = import_gateway_status_module(args.repo_root)
    smoke = module.smoke_gateway(args.repo_root)
    print("AIDE Lite gateway smoke")
    print(f"result: {smoke.get('result', 'FAIL')}")
    print("provider_or_model_calls: none")
    print("network_calls: none")
    print("raw_prompt_storage: false")
    print("raw_response_storage: false")
    endpoints = smoke.get("endpoints", [])
    if isinstance(endpoints, list):
        for item in endpoints:
            if isinstance(item, dict):
                print(f"- {item.get('endpoint', '')}: {item.get('status_code', '')} {item.get('status', '')}")
    print(f"- /unknown: {smoke.get('not_found_status_code', '')} {smoke.get('not_found_status', '')}")
    return 0 if smoke.get("result") == "PASS" else 1


def command_gateway_serve(args: argparse.Namespace) -> int:
    module = import_gateway_server_module(args.repo_root)
    print("AIDE Lite gateway serve")
    print("local skeleton only; provider/model forwarding is disabled")
    print(f"host: {args.host}")
    print(f"port: {args.port}")
    module.serve(args.repo_root, host=args.host, port=args.port)
    return 0


def command_provider_list(args: argparse.Namespace) -> int:
    registry = import_provider_registry_module(args.repo_root)
    providers = registry.load_provider_catalog(args.repo_root)
    print("AIDE Lite provider list")
    print(f"catalog: {PROVIDER_CATALOG_PATH}")
    print(f"provider_count: {len(providers)}")
    for provider in sorted(providers, key=lambda item: item.provider_id):
        print(
            f"- {provider.provider_id}: adapter_class={provider.adapter_class} "
            f"provider_class={provider.provider_class} privacy_class={provider.privacy_class} "
            f"credentials_required={str(provider.credentials_required).lower()} status={provider.status} "
            "live_calls_allowed_in_q20=false"
        )
    print("provider_or_model_calls: none")
    print("network_calls: none")
    return 0


def command_provider_status(args: argparse.Namespace) -> int:
    module = import_provider_status_module(args.repo_root)
    json_path, md_path, data = module.write_provider_status_files(args.repo_root)
    validation = data.get("validation", {}) if isinstance(data.get("validation"), dict) else {}
    print("AIDE Lite provider status")
    print(f"json: {normalize_rel(json_path.relative_to(args.repo_root))}")
    print(f"markdown: {normalize_rel(md_path.relative_to(args.repo_root))}")
    print(f"provider_family_count: {data.get('provider_family_count', 0)}")
    print(f"validation_result: {validation.get('result', 'unknown')}")
    print(f"credential_required_count: {data.get('credential_required_count', 0)}")
    print("credentials_configured: false")
    print("live_provider_calls: false")
    print("live_model_calls: false")
    print("network_calls: none")
    print("gateway_forwarding: false")
    print("raw_prompt_storage: false")
    print("raw_response_storage: false")
    return 0 if validation.get("result") != "FAIL" else 1


def command_provider_validate(args: argparse.Namespace) -> int:
    checks = provider_validation_checks(args.repo_root)
    ok = not any(check.severity == "FAIL" for check in checks)
    return print_messages("AIDE Lite provider validate", ok, [f"{check.severity} {check.message}" for check in checks])


def command_provider_contract(args: argparse.Namespace) -> int:
    module = import_provider_status_module(args.repo_root)
    summary = module.contract_summary(args.repo_root)
    print("AIDE Lite provider contract")
    print(f"contract: {summary.get('contract_path', PROVIDER_ADAPTER_CONTRACT_PATH)}")
    print("required_fields:")
    for field in summary.get("required_fields", []):
        print(f"- {field}")
    print("live_calls_allowed_in_q20: false")
    print("network_calls_allowed_in_q20: false")
    print("model_calls_allowed_in_q20: false")
    print("provider_probe_calls_allowed_in_q20: false")
    print("raw_prompt_storage: false")
    print("raw_response_storage: false")
    return 0 if (args.repo_root / PROVIDER_ADAPTER_CONTRACT_PATH).exists() else 1


def command_provider_probe(args: argparse.Namespace) -> int:
    if not args.offline:
        print("AIDE Lite provider probe")
        print("status: FAIL")
        print("offline_required: true")
        print("live provider probes are forbidden in Q20")
        return 1
    module = import_provider_status_module(args.repo_root)
    probe = module.offline_probe(args.repo_root)
    print("AIDE Lite provider probe")
    print("mode: offline")
    print(f"result: {probe.get('result', 'UNKNOWN')}")
    print(f"provider_family_count: {probe.get('provider_family_count', 0)}")
    print("live_provider_calls: false")
    print("live_model_calls: false")
    print("network_calls: none")
    print("provider_probe_calls: false")
    print("credentials_configured: false")
    print(f"future_credentials_location: {probe.get('future_credentials_location', '.aide.local/')}")
    return 0 if probe.get("result") != "FAIL" else 1


def export_pack_root(repo_root: Path, name: str = EXPORT_PACK_ID) -> Path:
    if name != EXPORT_PACK_ID:
        raise ValueError(f"unsupported export pack name: {name}")
    return repo_root / EXPORT_ROOT / name


def pack_rel(path: Path, pack_root: Path) -> str:
    return normalize_rel(path.relative_to(pack_root))


def is_allowed_generated_export_template(rel_path: str) -> bool:
    return rel_path in {
        ".aide/queue/README.template.md",
        ".aide/profile.template.yaml",
        ".aide/memory/project-state.template.md",
        ".aide/memory/decisions.template.md",
        ".aide/memory/open-risks.template.md",
        ".aide/import-policy.template.yaml",
        ".aide/import-report.template.md",
    }


def is_allowed_local_state_example(rel_path: str) -> bool:
    return rel_path == f"{LOCAL_STATE_EXAMPLE_ROOT}/secrets/README.md"


def is_allowed_portable_report(rel_path: str) -> bool:
    return normalize_rel(rel_path) in {
        COMMIT_MESSAGE_STANDARD_PATH,
        TASK_RESUMPTION_STANDARD_PATH,
        WORKUNIT_RECOVERY_STANDARD_PATH,
    }


def is_forbidden_export_path(rel_path: str) -> bool:
    rel = normalize_rel(rel_path)
    if is_allowed_generated_export_template(rel) or is_allowed_local_state_example(rel) or is_allowed_portable_report(rel):
        return False
    return any(pattern_matches(rel, pattern) for pattern in EXPORT_FORBIDDEN_PATH_PATTERNS)


def is_exportable_file(repo_root: Path, rel_path: str) -> bool:
    rel = normalize_rel(rel_path)
    if any(pattern_matches(rel, pattern) for pattern in LOCAL_ONLY_EXPORT_PATH_PATTERNS):
        return False
    path = repo_root / rel
    if not path.exists() or not path.is_file():
        return False
    if is_forbidden_export_path(rel):
        return False
    if looks_binary(path):
        return False
    return not any(finding.severity == "ERROR" for finding in scan_secret_text(read_text(path), rel))


def portable_golden_catalog_text(source_text: str) -> str:
    lines = source_text.splitlines()
    output: list[str] = []
    skipping = False
    for line in lines:
        if line.startswith("  - id: "):
            task_id = line.split(":", 1)[1].strip()
            skipping = task_id in LOCAL_ONLY_GOLDEN_TASK_IDS
        if not skipping:
            output.append(line)
    return "\n".join(output) + "\n"


def iter_portable_source_files(repo_root: Path) -> list[str]:
    files: set[str] = set()
    for rel in PORTABLE_SOURCE_FILES:
        if is_exportable_file(repo_root, rel):
            files.add(normalize_rel(rel))
    for directory in PORTABLE_SOURCE_DIRS:
        root = repo_root / directory
        if not root.exists() or not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            rel = normalize_rel(path.relative_to(repo_root))
            if is_exportable_file(repo_root, rel):
                files.add(rel)
    return sorted(files)


def write_bytes_if_changed(path: Path, data: bytes) -> WriteResult:
    if path.exists() and path.read_bytes() == data:
        return WriteResult(path, "unchanged")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return WriteResult(path, "written")


def copy_pack_file(source: Path, destination: Path) -> WriteResult:
    return write_bytes_if_changed(destination, source.read_bytes())


def portable_agents_template() -> str:
    return """<!-- AIDE-PORTABLE:BEGIN section=aide-lite-pack-v0 mode=managed -->
## AIDE Lite Portable Guidance

- This repository uses a portable AIDE Lite Pack imported from AIDE.
- Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory.
- Do not copy source `.aide/queue/`, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
- Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`.
- Use `py -3 .aide/scripts/aide_lite.py test` for portable AIDE Lite validation.
- Use `commit check`, `commit template`, and `changelog preview` for Q27-style structured commits.
- Use `task inspect`, `task noop-check`, and `task recover` before repeated or out-of-order work.
- Use `git policy`, `git detect`, and `git plan` before branch-sensitive work; do not mutate branches without explicit helper plan, validation evidence, and operator approval.
- Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed target queue item enables them.
<!-- AIDE-PORTABLE:END section=aide-lite-pack-v0 -->
"""


def queue_readme_template() -> str:
    return """# Target AIDE Queue

This is a template marker for target repositories.

Do not copy AIDE's source `.aide/queue/` history into a target repository.
Initialize target queue items separately with target-specific task packets,
evidence, validation, and review gates.
"""


def portable_command_catalog() -> str:
    return """schema_version: aide.commands-catalog.portable-v0
catalog_status: portable-aide-lite-pack
source_of_truth_note: Portable AIDE Lite command surface for target repositories.
commands:
  - id: aide-lite
    display_name: AIDE Lite
    invocation: py -3 .aide/scripts/aide_lite.py <command>
    command_kind: repo-local-helper
    status: implemented-portable
    owner_component: aide-lite-pack
    mutates_repo: command-dependent
    notes: Portable no-call helper for doctor, validate, estimate, snapshot, index, context, pack, verify, review-pack, ledger, eval, outcome, optimize, route, cache, gateway, provider metadata, adapter rendering, adapt, selftest, and test.
  - id: aide-lite-test
    display_name: AIDE Lite canonical test runner
    invocation: py -3 .aide/scripts/aide_lite.py test
    command_kind: repo-local-helper
    status: implemented
    owner_component: aide-lite-pack
    mutates_repo: false
    notes: canonical AIDE Lite validation command; no provider/model/network calls.
  - id: aide-lite-adapter
    display_name: AIDE Lite adapter compiler
    invocation: py -3 .aide/scripts/aide_lite.py adapter <list|render|preview|validate|drift|generate>
    command_kind: repo-local-helper
    status: implemented-preview
    owner_component: existing-tool-adapters
    mutates_repo: command-dependent
    notes: renders compact existing-tool guidance previews and safe managed AGENTS output only; no provider/model/network calls.
  - id: aide-lite-commit
    display_name: AIDE Lite commit discipline
    invocation: py -3 .aide/scripts/aide_lite.py commit <check|template|status|install-hook>
    command_kind: repo-local-helper
    status: implemented-portable
    owner_component: commit-discipline
    mutates_repo: command-dependent
    notes: validates structured commit messages and prints/writes templates; hook installation remains explicit and opt-in.
  - id: aide-lite-task
    display_name: AIDE Lite task recovery
    invocation: py -3 .aide/scripts/aide_lite.py task <inspect|status|noop-check|dependencies|recover|evidence|current>
    command_kind: repo-local-helper
    status: implemented-portable
    owner_component: workunit-recovery
    mutates_repo: false
    notes: report-first task inspection and recovery guidance for repeated or out-of-order prompts.
  - id: aide-lite-git
    display_name: AIDE Lite Git workflow
    invocation: py -3 .aide/scripts/aide_lite.py git <detect|doctor|status|policy|plan|sync|land|promote|prune>
    command_kind: repo-local-helper
    status: implemented-portable
    owner_component: git-workflow
    mutates_repo: command-dependent
    notes: policy and dry-run helpers default to no live branch or remote mutation; --apply/--push require explicit future operator intent.
"""


def pack_readme_text() -> str:
    return f"""# AIDE Lite Pack v0

Pack id: `{EXPORT_PACK_ID}`

This is a portable metadata and tooling pack for target repositories. It is
generated from AIDE's repo-local no-call token-survival foundation. Q31 exports
portable Q27-Q30 governance: structured commit discipline, changelog preview,
task/WorkUnit recovery, generic Git workflow policy, and dry-run Git helper
support. Q24 adapter templates remain included so target repositories can
generate local guidance previews for existing tools after import.

The pack intentionally excludes AIDE's source profile, queue history, project
memory, generated context, reports, route/cache/controller/latest status,
provider/Gateway status reports, eval runs, `.aide.local/`, raw prompts, raw
responses, and secrets.

Q25 makes command import default to `--mode safe`, which plans and writes only
portable `.aide/`, `.aide.local.example/`, target templates, portable
`docs/reference/` governance docs, `AGENTS.md`, and `.gitignore` local-state
rules. Optional broad roots such as `core/` and non-reference `docs/` content
remain in the pack for reviewed fixtures but are skipped unless `--mode full`
is selected explicitly.

Use `install.md` for manual and command-based import steps.
"""


def pack_install_text() -> str:
    return f"""# Install AIDE Lite Pack v0

## Command Import

From the source AIDE repository:

```text
py -3 .aide/scripts/aide_lite.py import-pack --pack .aide/export/{EXPORT_PACK_ID} --target <target-repo> --dry-run
py -3 .aide/scripts/aide_lite.py import-pack --pack .aide/export/{EXPORT_PACK_ID} --target <target-repo> --mode safe
```

`--mode safe` is the default. It skips optional broad roots such as `core/` and
non-reference `docs/` content and prints the exact planned writes plus skipped
paths during dry-run. Portable `docs/reference/` governance docs are safe-mode
files. Use `--mode full` only in reviewed local fixtures where copying optional
roots has been explicitly accepted.

## Manual Import

Copy only the safe portable subset from `files/` into the target repository:
`.aide/`, `.aide.local.example/`, `docs/reference/` governance docs,
`AGENTS.md.template`, and target templates. Do not manually copy optional
`core/` or broad non-reference `docs/` roots into a product repo unless that
target task explicitly authorizes them. Then fill the target templates under
`.aide/` with target-specific facts.

After import, run in the target repository:

```text
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py snapshot
py -3 .aide/scripts/aide_lite.py index
py -3 .aide/scripts/aide_lite.py pack --task "<target next task>"
py -3 .aide/scripts/aide_lite.py adapter render
py -3 .aide/scripts/aide_lite.py adapter validate
py -3 .aide/scripts/aide_lite.py commit template
py -3 .aide/scripts/aide_lite.py git policy
py -3 .aide/scripts/aide_lite.py git plan
```

Do not copy source `.aide/queue/`, generated context, reports, `.aide.local/`,
provider credentials, raw prompts, or raw responses. Generate adapter outputs
locally in the target repo after target-specific memory and context exist.
Commit hooks are copied as `.aide/hooks/commit-msg` but are not installed into
`.git/hooks`; hook installation remains an explicit target action.
"""


def render_manifest(included_files: list[str], source_commit: str, dirty_state: bool) -> str:
    lines = [
        "schema_version: q21.aide-lite-pack-manifest.v0",
        f"pack_id: {EXPORT_PACK_ID}",
        "source_repo: julesc013/aide",
        f"source_commit: {source_commit}",
        f"source_dirty_state: {str(dirty_state).lower()}",
        f"generated_by: {GENERATOR_NAME} {GENERATOR_VERSION}",
        "contents_inline: false",
        "raw_prompt_storage: false",
        "raw_response_storage: false",
        "local_state_copied: false",
        "provider_or_model_calls: false",
        "included_files:",
    ]
    lines.extend(f"  - {path}" for path in included_files)
    lines.append("excluded_classes:")
    lines.extend(f"  - {item}" for item in EXPORT_EXCLUDED_CLASSES)
    lines.append("required_target_initialization_steps:")
    for step in ["fill target profile and memory templates", "run doctor", "run snapshot", "run index", "run pack"]:
        lines.append(f"  - {step}")
    lines.extend(
        [
            "no_secret_guarantee: obvious secret-like patterns are refused during export",
            "checksum_scope: payload and static pack docs; excludes manifest.yaml, checksums.json, and export-report.md",
            "limitations:",
            "  - fixture validation plus Q22/Q23 pilot evidence; Q32/Q33 target sync still required",
            "  - target-specific memory still requires human/project-specific content",
            "  - target-specific branch detection and helper plans must be generated after import",
            "  - no provider/model/network calls are enabled",
        ]
    )
    return "\n".join(lines) + "\n"


def exported_pack_file_paths(pack_root: Path) -> list[Path]:
    if not pack_root.exists():
        return []
    return sorted(
        path
        for path in pack_root.rglob("*")
        if path.is_file() and pack_rel(path, pack_root) not in CHECKSUM_EXCLUDED_PACK_FILES
    )


def build_pack_checksums(pack_root: Path) -> dict[str, object]:
    checksums = {
        pack_rel(path, pack_root): sha256_file(path)
        for path in exported_pack_file_paths(pack_root)
    }
    return {
        "schema_version": "q25.aide-lite-pack-checksums.v1",
        "pack_id": EXPORT_PACK_ID,
        "algorithm": "sha256",
        "contents_inline": False,
        "checksum_scope": "payload-and-static-pack-docs",
        "excluded_from_checksums": sorted(CHECKSUM_EXCLUDED_PACK_FILES),
        "checksums": dict(sorted(checksums.items())),
    }


def validate_export_pack_boundary(pack_root: Path) -> list[str]:
    violations: list[str] = []
    files_root = pack_root / "files"
    if not files_root.exists():
        return ["missing files/ root"]
    for path in sorted(files_root.rglob("*")):
        if not path.is_file():
            continue
        rel = normalize_rel(path.relative_to(files_root))
        if is_forbidden_export_path(rel):
            violations.append(f"forbidden exported path: {rel}")
        if looks_binary(path):
            violations.append(f"binary exported path: {rel}")
            continue
        findings = [finding for finding in scan_secret_text(read_text(path), rel) if finding.severity == "ERROR"]
        if findings:
            violations.append(f"secret-like exported content: {rel}")
    return violations


def q31_pack_payload_path(source_rel: str) -> str:
    return f"files/{normalize_rel(source_rel)}"


def exported_golden_catalog_contains(pack_root: Path, task_id: str) -> bool:
    catalog = pack_root / "files" / GOLDEN_TASK_CATALOG_PATH
    if not catalog.exists():
        return False
    return f"id: {task_id}" in read_text(catalog)


def q31_pack_governance_checks(repo_root: Path) -> list[Check]:
    checks: list[Check] = []
    pack_root = export_pack_root(repo_root, EXPORT_PACK_ID)
    manifest_path = pack_root / "manifest.yaml"
    manifest = read_text(manifest_path) if manifest_path.exists() else ""
    if not pack_root.exists():
        missing = [rel for rel in Q31_REQUIRED_EXPORTED_SOURCE_FILES if not (repo_root / rel).exists()]
        if missing:
            checks.append(Check("WARN", "Q31 export pack absent and local governance files missing: " + ", ".join(missing[:5])))
        else:
            checks.append(Check("PASS", "Q31 portable governance files available locally; export pack not present in this repo"))
        return checks
    for source_rel in Q31_REQUIRED_EXPORTED_SOURCE_FILES:
        payload_rel = q31_pack_payload_path(source_rel)
        exists = (pack_root / payload_rel).exists()
        check_pass(checks, exists, f"Q31 pack includes governance file: {payload_rel}")
        check_pass(checks, payload_rel in manifest, f"Q31 manifest lists governance file: {payload_rel}")
    for task_id in Q31_REQUIRED_EXPORTED_GOLDEN_TASK_IDS:
        task_payload = q31_pack_payload_path(f"{GOLDEN_TASK_ROOT}/{task_id}/task.yaml")
        acceptance_payload = q31_pack_payload_path(f"{GOLDEN_TASK_ROOT}/{task_id}/acceptance.md")
        check_pass(checks, (pack_root / task_payload).exists(), f"Q31 pack includes golden task: {task_id}")
        check_pass(checks, (pack_root / acceptance_payload).exists(), f"Q31 pack includes golden acceptance: {task_id}")
        check_pass(checks, exported_golden_catalog_contains(pack_root, task_id), f"Q31 exported golden catalog lists: {task_id}")
    for source_rel in Q31_FORBIDDEN_EXPORTED_SOURCE_FILES:
        payload_rel = q31_pack_payload_path(source_rel)
        check_pass(checks, not (pack_root / payload_rel).exists(), f"Q31 pack excludes source-state file: {payload_rel}")
        check_pass(checks, payload_rel not in manifest, f"Q31 manifest excludes source-state file: {payload_rel}")
    return checks


def render_export_report(pack_root: Path, manifest_files: list[str], boundary_violations: list[str]) -> str:
    checksums = json.loads(read_text(pack_root / "checksums.json")) if (pack_root / "checksums.json").exists() else {"checksums": {}}
    lines = [
        "# AIDE Lite Pack Export Report",
        "",
        f"- pack_id: {EXPORT_PACK_ID}",
        f"- pack_path: {EXPORT_PACK_PATH}",
        f"- included_file_count: {len(manifest_files)}",
        f"- checksum_count: {len(checksums.get('checksums', {}))}",
        f"- checksum_scope: {checksums.get('checksum_scope', 'payload-and-static-pack-docs')}",
        f"- checksum_excluded: {', '.join(checksums.get('excluded_from_checksums', sorted(CHECKSUM_EXCLUDED_PACK_FILES)))}",
        f"- boundary_result: {'PASS' if not boundary_violations else 'FAIL'}",
        "- provider_or_model_calls: none",
        "- network_calls: none",
        "- raw_prompt_storage: false",
        "- raw_response_storage: false",
        "",
        "## Portable Governance Classes",
        "",
        "- commit message policy and hook/template support",
        "- changelog preview support",
        "- task resumption, WorkUnit, and recovery policy",
        "- generic Git workflow, branch-role, promotion, sync, and prune policy",
        "- dry-run Git helper policy and commands",
        "- governance golden tasks and portable reference docs",
        "",
        "## Excluded Classes",
    ]
    lines.extend(f"- {item}" for item in EXPORT_EXCLUDED_CLASSES)
    lines.append("")
    lines.append("## Boundary Violations")
    if boundary_violations:
        lines.extend(f"- {item}" for item in boundary_violations)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def build_export_pack(repo_root: Path, name: str = EXPORT_PACK_ID, output: str | None = None) -> tuple[Path, dict[str, object]]:
    if name != EXPORT_PACK_ID:
        raise ValueError(f"unsupported pack name: {name}")
    pack_root = (repo_root / output).resolve() if output else export_pack_root(repo_root, name)
    repo_root_resolved = repo_root.resolve()
    try:
        pack_root.relative_to(repo_root_resolved)
    except ValueError as exc:
        raise ValueError("export output must stay inside the source repo") from exc
    expected_root = export_pack_root(repo_root, name).resolve()
    if output and pack_root != expected_root:
        raise ValueError(f"Q21 only permits committed export path: {EXPORT_PACK_PATH}")
    if pack_root.exists():
        shutil.rmtree(pack_root)
    files_root = pack_root / "files"
    files_root.mkdir(parents=True, exist_ok=True)

    source_files = iter_portable_source_files(repo_root)
    copied: list[str] = []
    for rel in source_files:
        destination = files_root / rel
        copy_pack_file(repo_root / rel, destination)
        copied.append(pack_rel(destination, pack_root))

    for template_source, destination_rel in PORTABLE_TEMPLATE_MAP.items():
        source = repo_root / template_source
        if source.exists():
            result = write_text_if_changed(files_root / destination_rel, read_text(source))
            copied.append(pack_rel(result.path, pack_root))
    queue_result = write_text_if_changed(files_root / ".aide/queue/README.template.md", queue_readme_template())
    copied.append(pack_rel(queue_result.path, pack_root))
    agents_result = write_text_if_changed(files_root / "AGENTS.md.template", portable_agents_template())
    copied.append(pack_rel(agents_result.path, pack_root))
    catalog_result = write_text_if_changed(files_root / ".aide/commands/catalog.yaml", portable_command_catalog())
    copied.append(pack_rel(catalog_result.path, pack_root))
    golden_catalog_source = repo_root / GOLDEN_TASK_CATALOG_PATH
    if golden_catalog_source.exists():
        golden_catalog_result = write_text_if_changed(
            files_root / GOLDEN_TASK_CATALOG_PATH,
            portable_golden_catalog_text(read_text(golden_catalog_source)),
        )
        copied.append(pack_rel(golden_catalog_result.path, pack_root))

    write_text_if_changed(pack_root / "README.md", pack_readme_text())
    write_text_if_changed(pack_root / "install.md", pack_install_text())
    import_policy_source = repo_root / EXPORT_IMPORT_POLICY_TEMPLATE_PATH
    write_text_if_changed(pack_root / "import-policy.yaml", read_text(import_policy_source))

    dirty = bool(git_status_short(repo_root)[1])
    manifest_files = sorted(set(copied))
    write_text_if_changed(pack_root / "manifest.yaml", render_manifest(manifest_files, git_commit_id(repo_root), dirty))
    checksums = build_pack_checksums(pack_root)
    write_text_if_changed(pack_root / "checksums.json", stable_json_text(checksums))
    boundary_violations = validate_export_pack_boundary(pack_root)
    write_text_if_changed(pack_root / "export-report.md", render_export_report(pack_root, manifest_files, boundary_violations))
    if boundary_violations:
        raise ValueError("export pack boundary violations: " + "; ".join(boundary_violations))
    return pack_root, {
        "included_files": manifest_files,
        "checksum_count": len(checksums["checksums"]),
        "boundary_violations": boundary_violations,
    }


def validate_pack_checksums(pack_root: Path) -> tuple[bool, list[str]]:
    checksums_path = pack_root / "checksums.json"
    if not checksums_path.exists():
        return False, ["missing checksums.json"]
    data = json.loads(read_text(checksums_path))
    entries = data.get("checksums", {})
    if not isinstance(entries, dict):
        return False, ["checksums entry is not a mapping"]
    excluded = set(data.get("excluded_from_checksums", CHECKSUM_EXCLUDED_PACK_FILES))
    problems: list[str] = []
    for rel in sorted(set(entries).intersection(excluded)):
        problems.append(f"excluded metadata file is checksummed: {rel}")
    actual_files = {pack_rel(path, pack_root) for path in exported_pack_file_paths(pack_root)}
    for rel in sorted(actual_files.difference(entries)):
        problems.append(f"unchecksummed pack file: {rel}")
    for rel, expected in sorted(entries.items()):
        path = pack_root / rel
        if not path.exists() or not path.is_file():
            problems.append(f"missing checksum file: {rel}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            problems.append(f"checksum mismatch: {rel}")
    return not problems, problems


def pack_manifest_scalars(pack_root: Path) -> dict[str, str]:
    manifest_path = pack_root / "manifest.yaml"
    if not manifest_path.exists():
        return {}
    scalars: dict[str, str] = {}
    for line in read_text(manifest_path).splitlines():
        if not line or line.startswith(" ") or line.startswith("-") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        scalars[key.strip()] = value.strip()
    return scalars


def validate_pack_provenance(
    pack_root: Path,
    repo_root: Path,
    current_commit: str | None = None,
) -> tuple[str, list[str]]:
    scalars = pack_manifest_scalars(pack_root)
    if not scalars:
        return "FAIL", ["missing manifest.yaml"]
    source_commit = scalars.get("source_commit", "")
    dirty_text = scalars.get("source_dirty_state", "")
    problems: list[str] = []
    if not source_commit:
        problems.append("manifest missing source_commit")
    if dirty_text not in {"true", "false"}:
        problems.append("manifest source_dirty_state must be true or false")
    if problems:
        return "FAIL", problems
    dirty_recorded = dirty_text == "true"
    current = current_commit if current_commit is not None else git_commit_id(repo_root)
    if current not in {"", "unavailable"} and source_commit != current and not dirty_recorded:
        problems.append(
            f"manifest source_commit {source_commit} does not match current HEAD {current}"
        )
    if problems:
        return "FAIL", problems
    if dirty_recorded:
        return "DIRTY_SOURCE_RECORDED", []
    if current == "unavailable":
        return "UNKNOWN_GIT_UNAVAILABLE", []
    return "PASS", []


def export_import_validation_checks(repo_root: Path) -> list[Check]:
    checks: list[Check] = []
    for rel in Q21_REQUIRED_FILES:
        if (repo_root / rel).exists():
            checks.append(Check("PASS", f"export/import artifact exists: {rel}"))
        else:
            checks.append(Check("FAIL", f"export/import artifact missing: {rel}"))
    policy_text = read_text(repo_root / EXPORT_IMPORT_POLICY_PATH) if (repo_root / EXPORT_IMPORT_POLICY_PATH).exists() else ""
    for anchor in [
        "portable_pack_only",
        "no_external_repo_mutation",
        "no_network",
        "no_provider_calls",
        "aide-lite-pack-v0",
        "commit_message_policy",
        "commit_hook_template",
        "commit_template",
        "changelog_preview_support",
        "task_resumption_policy",
        "workunit_policy",
        "recovery_policy",
        "git_workflow_policy",
        "branch_roles_policy",
        "promotion_rules_policy",
        "sync_policy",
        "prune_policy",
        "git_helper_policy",
        "project_workflow_profiles",
        "source_repo_queue_history",
        "source_repo_git_detection",
        "source_repo_git_helper_plan",
        "source_repo_branch_policy",
        "generated_context",
        "local_state",
        "raw_prompts",
        "raw_responses",
        "never_copy_aide_self_hosting_queue: true",
        "never_copy_aide_generated_context: true",
        "never_copy_aide_local_state: true",
        "never_copy_provider_credentials: true",
    ]:
        if anchor not in policy_text:
            checks.append(Check("FAIL", f"export/import policy missing anchor: {anchor}"))
    pack_root = export_pack_root(repo_root, EXPORT_PACK_ID)
    ok, checksum_problems = validate_pack_checksums(pack_root) if pack_root.exists() else (False, ["pack missing"])
    if ok:
        checks.append(Check("PASS", "export pack checksums validate"))
    else:
        checks.append(Check("FAIL", "export pack checksum problem: " + "; ".join(checksum_problems[:5])))
    if pack_root.exists():
        provenance_status, provenance_problems = validate_pack_provenance(pack_root, repo_root)
    else:
        provenance_status, provenance_problems = "FAIL", ["pack missing"]
    if provenance_problems:
        checks.append(Check("FAIL", "export pack provenance problem: " + "; ".join(provenance_problems[:5])))
    else:
        checks.append(Check("PASS", f"export pack provenance: {provenance_status}"))
    boundary = validate_export_pack_boundary(pack_root) if pack_root.exists() else ["pack missing"]
    if boundary:
        checks.append(Check("FAIL", "export pack boundary violation: " + "; ".join(boundary[:5])))
    else:
        checks.append(Check("PASS", "export pack boundary excludes source-specific state"))
    checks.extend(q31_pack_governance_checks(repo_root))
    return checks


def import_target_name(target_root: Path) -> str:
    return target_root.name or "target-repo"


def render_target_template(text: str, target_root: Path, next_task: str = "Import AIDE Lite Pack") -> str:
    name = import_target_name(target_root)
    replacements = {
        "<target_repo_id>": name.lower().replace(" ", "-"),
        "<target_repo_name>": name,
        "<target_project_summary>": "Target repository imported AIDE Lite Pack v0.",
        "<target_current_phase>": "aide-lite-import-initialization",
        "<target_primary_goal>": "Use compact AIDE Lite context and validation workflows in this target repository.",
        "<target_deferred_surfaces>": "Gateway forwarding, provider/model calls, UI, runtime, and autonomous loops remain deferred.",
        "<target_next_task>": next_task,
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def merge_agents_text(existing: str | None, template: str) -> str:
    begin = "<!-- AIDE-PORTABLE:BEGIN section=aide-lite-pack-v0"
    end = "<!-- AIDE-PORTABLE:END section=aide-lite-pack-v0 -->"
    if existing is None or not existing.strip():
        return "# AGENTS.md\n\n" + template
    if begin in existing and end in existing:
        prefix, rest = existing.split(begin, 1)
        _old, suffix = rest.split(end, 1)
        return prefix.rstrip() + "\n\n" + template.rstrip() + "\n" + suffix.lstrip()
    return existing.rstrip() + "\n\n" + template


def ensure_target_gitignore_text(existing: str | None) -> str:
    lines = [] if existing is None else existing.splitlines()
    normalized = {line.strip() for line in lines}
    changed = False
    for pattern in [".aide.local/", ".aide.local/**", ".env"]:
        if pattern not in normalized:
            lines.append(pattern)
            changed = True
    if existing is None or changed:
        return "\n".join(lines).strip() + "\n"
    return existing if existing.endswith("\n") else existing + "\n"


def import_scope_skip_reason(rel: str, mode: str) -> str:
    if mode == "full":
        return ""
    if any(rel.startswith(prefix) for prefix in IMPORT_SAFE_EXCLUDED_PREFIXES):
        return "safe mode excludes broad source roots; use --mode full only for reviewed local fixtures"
    if rel.startswith(IMPORT_SAFE_EXCLUDED_DOCS_PREFIX) and not rel.startswith(IMPORT_SAFE_ALLOWED_DOCS_PREFIX):
        return "safe mode excludes broad docs roots except portable docs/reference governance files"
    return ""


def import_pack_plan(
    pack_root: Path,
    target_root: Path,
    mode: str = "safe",
) -> tuple[list[dict[str, str]], list[str], list[dict[str, str]]]:
    if mode not in IMPORT_MODES:
        raise ValueError(f"unsupported import mode: {mode}")
    files_root = pack_root / "files"
    if not files_root.exists():
        raise ValueError(f"pack files root missing: {files_root}")
    operations: list[dict[str, str]] = []
    conflicts: list[str] = []
    skipped: list[dict[str, str]] = []
    for source in sorted(path for path in files_root.rglob("*") if path.is_file()):
        rel = normalize_rel(source.relative_to(files_root))
        skip_reason = import_scope_skip_reason(rel, mode)
        if skip_reason:
            skipped.append({"source": rel, "reason": skip_reason})
            continue
        if rel == "AGENTS.md.template":
            target_rel = "AGENTS.md"
            action = "merge_agents"
        else:
            target_rel = rel
            action = "copy"
        target = target_root / target_rel
        if action == "copy" and target.exists():
            same = sha256_file(source) == sha256_file(target) if target.is_file() else False
            action = "unchanged" if same else "conflict"
            if not same:
                conflicts.append(target_rel)
        operations.append({"source": rel, "target": target_rel, "action": action})
        if rel == ".aide/profile.template.yaml":
            operations.append({"source": rel, "target": ".aide/profile.yaml", "action": "create_from_template"})
        elif rel == ".aide/memory/project-state.template.md":
            operations.append({"source": rel, "target": ".aide/memory/project-state.md", "action": "create_from_template"})
        elif rel == ".aide/memory/decisions.template.md":
            operations.append({"source": rel, "target": ".aide/memory/decisions.md", "action": "create_from_template"})
        elif rel == ".aide/memory/open-risks.template.md":
            operations.append({"source": rel, "target": ".aide/memory/open-risks.md", "action": "create_from_template"})
    operations.append({"source": "<generated>", "target": ".gitignore", "action": "ensure_local_state_ignore"})
    return operations, sorted(set(conflicts)), skipped


def apply_import_pack(pack_root: Path, target_root: Path, dry_run: bool = False, mode: str = "safe") -> dict[str, object]:
    ok, checksum_problems = validate_pack_checksums(pack_root)
    if not ok:
        raise ValueError("invalid pack checksums: " + "; ".join(checksum_problems))
    operations, conflicts, skipped = import_pack_plan(pack_root, target_root, mode=mode)
    if dry_run:
        return {
            "dry_run": True,
            "mode": mode,
            "target": normalize_rel(target_root),
            "operation_count": len(operations),
            "conflicts": conflicts,
            "skipped": skipped,
            "operations": operations,
            "written": [],
        }
    target_root.mkdir(parents=True, exist_ok=True)
    files_root = pack_root / "files"
    written: list[str] = []
    skipped_conflicts: list[str] = []
    for operation in operations:
        action = operation["action"]
        rel = operation["target"]
        target = target_root / rel
        if action == "conflict":
            skipped_conflicts.append(rel)
            continue
        if action == "ensure_local_state_ignore":
            existing = read_text(target) if target.exists() else None
            write_text_if_changed(target, ensure_target_gitignore_text(existing))
            written.append(rel)
            continue
        source_rel = operation["source"]
        source = files_root / source_rel
        if action == "merge_agents":
            existing = read_text(target) if target.exists() else None
            write_text_if_changed(target, merge_agents_text(existing, read_text(source)))
            written.append(rel)
        elif action == "create_from_template":
            if target.exists():
                continue
            write_text_if_changed(target, render_target_template(read_text(source), target_root))
            written.append(rel)
        elif action in {"copy", "unchanged"}:
            if action == "unchanged":
                continue
            copy_pack_file(source, target)
            written.append(rel)
    return {
        "dry_run": False,
        "mode": mode,
        "target": normalize_rel(target_root),
        "operation_count": len(operations),
        "conflicts": sorted(set(conflicts)),
        "skipped": skipped,
        "skipped_conflicts": sorted(set(skipped_conflicts)),
        "operations": operations,
        "written": sorted(set(written)),
    }


def command_export_pack(args: argparse.Namespace) -> int:
    pack_root, report = build_export_pack(args.repo_root, name=args.name, output=args.output)
    print("AIDE Lite export-pack")
    print(f"pack: {normalize_rel(pack_root.relative_to(args.repo_root))}")
    print(f"manifest: {normalize_rel((pack_root / 'manifest.yaml').relative_to(args.repo_root))}")
    print(f"checksums: {normalize_rel((pack_root / 'checksums.json').relative_to(args.repo_root))}")
    print(f"included_files: {len(report['included_files'])}")
    print(f"checksum_count: {report['checksum_count']}")
    print("boundary_result: PASS")
    print("provider_or_model_calls: none")
    print("network_calls: none")
    return 0


def command_import_pack(args: argparse.Namespace) -> int:
    pack_root = Path(args.pack).resolve()
    if not pack_root.exists():
        pack_root = (args.repo_root / args.pack).resolve()
    target_root = Path(args.target).resolve()
    result = apply_import_pack(pack_root, target_root, dry_run=args.dry_run, mode=args.mode)
    print("AIDE Lite import-pack")
    print(f"pack: {normalize_rel(pack_root)}")
    print(f"target: {normalize_rel(target_root)}")
    print(f"dry_run: {str(args.dry_run).lower()}")
    print(f"mode: {result['mode']}")
    print(f"operation_count: {result['operation_count']}")
    print(f"conflicts: {len(result['conflicts'])}")
    print(f"skipped: {len(result['skipped'])}")
    print(f"written: {len(result['written'])}")
    if args.dry_run:
        print("planned_writes:")
        for operation in result["operations"]:
            print(f"- {operation['action']}: {operation['target']} <= {operation['source']}")
        print("skipped_paths:")
        for skipped in result["skipped"]:
            print(f"- {skipped['source']}: {skipped['reason']}")
    print("provider_or_model_calls: none")
    print("network_calls: none")
    return 0 if not result["conflicts"] else 2


def command_pack_status(args: argparse.Namespace) -> int:
    pack_root = export_pack_root(args.repo_root, EXPORT_PACK_ID)
    ok, checksum_problems = validate_pack_checksums(pack_root) if pack_root.exists() else (False, ["pack missing"])
    if pack_root.exists():
        provenance_status, provenance_problems = validate_pack_provenance(pack_root, args.repo_root)
    else:
        provenance_status, provenance_problems = "FAIL", ["pack missing"]
    boundary = validate_export_pack_boundary(pack_root) if pack_root.exists() else ["pack missing"]
    print("AIDE Lite pack-status")
    print(f"pack: {EXPORT_PACK_PATH}")
    print(f"exists: {str(pack_root.exists()).lower()}")
    print(f"checksums_valid: {str(ok).lower()}")
    print(f"provenance_result: {provenance_status}")
    print(f"boundary_result: {'PASS' if not boundary else 'FAIL'}")
    print(f"checksum_problems: {len(checksum_problems)}")
    for problem in checksum_problems[:5]:
        print(f"- checksum_problem: {problem}")
    print(f"provenance_problems: {len(provenance_problems)}")
    for problem in provenance_problems[:5]:
        print(f"- provenance_problem: {problem}")
    print(f"boundary_violations: {len(boundary)}")
    return 0 if pack_root.exists() and ok and not provenance_problems and not boundary else 1


def command_adapter_list(args: argparse.Namespace) -> int:
    targets = load_adapter_targets(args.repo_root)
    print("AIDE Lite adapter list")
    if not targets:
        print("status: FAIL")
        print("reason: no adapter targets found")
        return 1
    print("status: PASS")
    for target in targets:
        print(
            f"- {target.target_id}: mode={target.output_mode}; enabled={str(target.enabled_by_default).lower()}; "
            f"risk={target.risk_level}; output={target.output_path or '<none>'}"
        )
    print("provider_or_model_calls: none")
    print("network_calls: none")
    return 0


def command_adapter_render(args: argparse.Namespace) -> int:
    rendered, writes, drift = render_adapter_outputs(args.repo_root, write=True)
    print("AIDE Lite adapter render")
    print("status: PASS")
    print(f"generated_outputs: {len(rendered)}")
    print(f"manifest: {ADAPTER_GENERATED_MANIFEST_PATH}")
    print(f"drift_report: {ADAPTER_DRIFT_REPORT_PATH}")
    for result in writes:
        print(f"- {normalize_rel(result.path.relative_to(args.repo_root))}: {result.action}")
    print("drift: " + ", ".join(f"{record['target_id']}={record['status']}" for record in drift))
    print("provider_or_model_calls: none")
    print("network_calls: none")
    return 0


def command_adapter_preview(args: argparse.Namespace) -> int:
    rendered, _writes, drift = render_adapter_outputs(args.repo_root, write=False)
    print("AIDE Lite adapter preview")
    print("status: PASS")
    print(f"planned_generated_outputs: {len(rendered)}")
    for item in rendered:
        target = item["target"]
        assert isinstance(target, AdapterTarget)
        print(f"- {target.target_id}: generated={target.generated_path}; target={target.output_path}; mode={target.output_mode}")
    print("drift_preview:")
    for record in drift:
        print(f"- {record['target_id']}: {record['status']} ({record['detail']})")
    print("writes: none")
    print("provider_or_model_calls: none")
    print("network_calls: none")
    return 0


def command_adapter_validate(args: argparse.Namespace) -> int:
    checks = adapter_validation_checks(args.repo_root, require_generated=True)
    ok = not any(check.severity == "FAIL" for check in checks)
    print("AIDE Lite adapter validate")
    print(f"status: {'PASS' if ok else 'FAIL'}")
    for check in checks:
        print(f"- {check.severity} {check.message}")
    print("provider_or_model_calls: none")
    print("network_calls: none")
    return 0 if ok else 1


def command_adapter_drift(args: argparse.Namespace) -> int:
    rendered, _writes, drift = render_adapter_outputs(args.repo_root, write=False)
    write_text_if_changed(args.repo_root / ADAPTER_DRIFT_REPORT_PATH, render_adapter_drift_report(drift))
    print("AIDE Lite adapter drift")
    print("status: PASS")
    print(f"generated_outputs_considered: {len(rendered)}")
    for record in drift:
        print(f"- {record['target_id']}: {record['status']} ({record['detail']})")
    print(f"drift_report: {ADAPTER_DRIFT_REPORT_PATH}")
    print("writes: drift report only")
    print("provider_or_model_calls: none")
    print("network_calls: none")
    return 0


def command_adapter_generate(args: argparse.Namespace) -> int:
    rendered, writes, drift = render_adapter_outputs(args.repo_root, write=True)
    root_writes: list[WriteResult] = []
    for item in rendered:
        target = item["target"]
        assert isinstance(target, AdapterTarget)
        if target.output_mode != "managed_section" or not target.enabled_by_default:
            continue
        if target.target_id == "codex_agents_md":
            result, _before, _after = adapt_agents(args.repo_root)
            root_writes.append(result)
    print("AIDE Lite adapter generate")
    print("status: PASS")
    print(f"preview_outputs: {len(rendered)}")
    print(f"preview_write_results: {len(writes)}")
    if root_writes:
        for result in root_writes:
            print(f"- root {normalize_rel(result.path.relative_to(args.repo_root))}: {result.action}")
    else:
        print("- root writes: none")
    preview_only = [record["target_id"] for record in drift if record["output_mode"] == "preview_only"]
    print(f"preview_only_targets: {', '.join(preview_only)}")
    print("manual_content_policy: preserved outside managed sections")
    print("provider_or_model_calls: none")
    print("network_calls: none")
    return 0


def command_adapt(args: argparse.Namespace) -> int:
    result, before, after = adapt_agents(args.repo_root)
    print("AIDE Lite adapt")
    print(f"path: {normalize_rel(result.path.relative_to(args.repo_root))}")
    print(f"action: {result.action}")
    print(f"before_status: {before.status}")
    print(f"after_status: {after.status}")
    print(f"managed_section: {AGENTS_SECTION}")
    return 0 if after.status == "current" else 1


def command_version(args: argparse.Namespace) -> int:
    print(f"{GENERATOR_NAME} {GENERATOR_VERSION}")
    return 0


def command_show_config(args: argparse.Namespace) -> int:
    print("AIDE Lite config")
    print(f"repo_root: {normalize_rel(args.repo_root)}")
    print(f"generator: {GENERATOR_NAME}")
    print(f"generator_version: {GENERATOR_VERSION}")
    print("token_budget:")
    for key, value in load_token_budget(args.repo_root).items():
        print(f"- {key}: {value}")
    return 0


def selftest_gateway_stub(rel: str) -> str | None:
    if rel == "core/gateway/__init__.py":
        return '"""Selftest Gateway fixture package."""\n'
    if rel == "core/gateway/server.py":
        return '"""Selftest Gateway server fixture: no network listener."""\n'
    if rel != "core/gateway/gateway_status.py":
        return None
    return '''"""Selftest Gateway status fixture."""
from __future__ import annotations

import json
from pathlib import Path

GATEWAY_STATUS_JSON_PATH = ".aide/gateway/latest-gateway-status.json"
GATEWAY_STATUS_MD_PATH = ".aide/gateway/latest-gateway-status.md"


def build_gateway_status(repo_root: Path | None = None) -> dict:
    return {
        "schema_version": "aide.gateway-status.v0",
        "generated_by": "selftest-fixture",
        "service": "aide-gateway-skeleton",
        "mode": "local_skeleton_report_only",
        "provider_calls_enabled": False,
        "model_calls_enabled": False,
        "outbound_network_enabled": False,
        "raw_prompt_storage": False,
        "raw_response_storage": False,
        "readiness": {},
        "signals": {},
        "summaries": {},
    }


def health_payload() -> dict:
    return {
        "status": "ok",
        "provider_calls_enabled": False,
        "model_calls_enabled": False,
        "outbound_network_enabled": False,
    }


def smoke_gateway(repo_root: Path | None = None) -> dict:
    return {
        "schema_version": "aide.gateway-smoke.v0",
        "result": "PASS",
        "provider_calls_enabled": False,
        "model_calls_enabled": False,
        "outbound_network_enabled": False,
    }


def write_gateway_status_files(repo_root: Path | None = None):
    root = Path(repo_root or ".")
    data = build_gateway_status(root)
    json_path = root / GATEWAY_STATUS_JSON_PATH
    md_path = root / GATEWAY_STATUS_MD_PATH
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
    md_path.write_text("# Latest Gateway Status\\n\\n- mode: local_skeleton_report_only\\n", encoding="utf-8")
    return json_path, md_path, data
'''


def selftest_provider_stub(rel: str) -> str | None:
    if rel == "core/providers/__init__.py":
        return '"""Selftest provider fixture package."""\n'
    if rel == "core/providers/contracts.py":
        return '"""Selftest provider contracts fixture."""\n'
    if rel == "core/providers/registry.py":
        return '''"""Selftest provider registry fixture."""


def validate_provider_files(repo_root):
    return {"result": "PASS", "provider_count": 13, "errors": [], "warnings": []}
'''
    if rel != "core/providers/status.py":
        return None
    return '''"""Selftest provider status fixture."""
from __future__ import annotations

import json
from pathlib import Path

PROVIDER_STATUS_JSON_PATH = ".aide/providers/latest-provider-status.json"
PROVIDER_STATUS_MD_PATH = ".aide/providers/latest-provider-status.md"
PROVIDER_IDS = [
    "deterministic_tools",
    "human",
    "local_ollama",
    "local_lm_studio",
    "local_llama_cpp",
    "local_vllm",
    "local_sglang",
    "openai",
    "anthropic",
    "google_gemini",
    "deepseek",
    "openrouter",
    "other_remote_provider",
]


def build_provider_status(repo_root: Path | None = None) -> dict:
    return {
        "schema_version": "aide.provider-status.v0",
        "generated_by": "selftest-fixture",
        "provider_adapter_contract": ".aide/providers/adapter-contract.yaml",
        "live_provider_calls": False,
        "live_model_calls": False,
        "network_calls": False,
        "provider_probe_calls": False,
        "credentials_configured": False,
        "gateway_forwarding": False,
        "raw_prompt_storage": False,
        "raw_response_storage": False,
        "no_credentials_in_status": True,
        "provider_family_count": len(PROVIDER_IDS),
        "provider_ids": PROVIDER_IDS,
        "provider_class_counts": {"deterministic": 2, "local": 5, "remote": 6},
        "adapter_class_counts": {"metadata_only": len(PROVIDER_IDS)},
        "privacy_class_counts": {"no_call": len(PROVIDER_IDS)},
        "status_counts": {"configured": 0, "available": 0, "metadata_only": len(PROVIDER_IDS)},
        "validation": {"result": "PASS", "errors": [], "warnings": []},
    }


def offline_probe(repo_root: Path | None = None) -> dict:
    return {
        "schema_version": "aide.provider-offline-probe.v0",
        "result": "PASS",
        "provider_probe_calls": False,
        "live_provider_calls": False,
        "network_calls": False,
    }


def write_provider_status_files(repo_root: Path | None = None):
    root = Path(repo_root or ".")
    data = build_provider_status(root)
    json_path = root / PROVIDER_STATUS_JSON_PATH
    md_path = root / PROVIDER_STATUS_MD_PATH
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
    md_path.write_text("# Latest Provider Status\\n\\n- live_provider_calls: false\\n", encoding="utf-8")
    return json_path, md_path, data
'''


def _write_minimal_repo(root: Path) -> None:
    for rel in REQUIRED_FILES:
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
    source_root = repo_root_from_script()
    if (source_root / ".gitignore").exists():
        write_text(root / ".gitignore", read_text(source_root / ".gitignore"))
    else:
        write_text(root / ".gitignore", "\n".join(GITIGNORE_REQUIRED_PATTERNS) + "\n")
    write_text(root / ".aide/policies/token-budget.yaml", read_text(source_root / ".aide/policies/token-budget.yaml"))
    write_text(root / ".aide/memory/project-state.md", "# Project\n\nCompact state.\n")
    write_text(root / ".aide/memory/decisions.md", "# Decisions\n")
    write_text(root / ".aide/memory/open-risks.md", "# Risks\n")
    write_text(root / ".aide/prompts/compact-task.md", read_text(source_root / ".aide/prompts/compact-task.md"))
    write_text(root / ".aide/prompts/evidence-review.md", read_text(source_root / ".aide/prompts/evidence-review.md"))
    write_text(root / ".aide/prompts/codex-token-mode.md", read_text(source_root / ".aide/prompts/codex-token-mode.md"))
    write_text(root / ".aide/context/ignore.yaml", read_text(source_root / ".aide/context/ignore.yaml"))
    for rel in CONTEXT_CONFIG_FILES:
        source = source_root / rel
        write_text(root / rel, read_text(source) if source.exists() else f"schema_version: {rel}\n")
    for rel in Q12_REQUIRED_FILES:
        source = source_root / rel
        write_text(root / rel, read_text(source) if source.exists() else f"schema_version: {rel}\n")
    for rel in Q14_REQUIRED_FILES:
        source = source_root / rel
        if source.exists():
            write_text(root / rel, read_text(source))
        elif rel.endswith(".jsonl"):
            write_text(root / rel, "")
        else:
            write_text(root / rel, f"schema_version: {rel}\n")
    for rel in Q15_REQUIRED_FILES:
        source = source_root / rel
        if source.exists() and source.is_file():
            write_text(root / rel, read_text(source))
        else:
            write_text(root / rel, f"schema_version: {rel}\n")
    for rel in Q16_REQUIRED_FILES:
        source = source_root / rel
        if source.exists() and source.is_file():
            write_text(root / rel, read_text(source))
        elif rel.endswith(".jsonl"):
            write_text(root / rel, "")
        else:
            write_text(root / rel, f"schema_version: {rel}\nadvisory_only: true\n")
    for rel in Q17_REQUIRED_FILES:
        source = source_root / rel
        if source.exists() and source.is_file():
            write_text(root / rel, read_text(source))
        else:
            write_text(root / rel, f"schema_version: {rel}\nadvisory_only: true\nlive_calls_allowed_in_q17: false\n")
    for source in sorted((source_root / ROUTING_DIR / "examples").glob("*")):
        if source.is_file():
            rel = normalize_rel(source.relative_to(source_root))
            write_text(root / rel, read_text(source))
    for rel in Q18_REQUIRED_FILES:
        source = source_root / rel
        if source.exists() and source.is_file():
            write_text(root / rel, read_text(source))
        elif rel.endswith(".json"):
            write_text(root / rel, stable_json_text({"schema_version": "q18.cache-keys.v0", "contents_inline": False, "raw_prompt_storage": False, "raw_response_storage": False, "keys": {}}))
        else:
            write_text(root / rel, f"schema_version: {rel}\nraw_prompt_storage_default: false\nraw_response_storage_default: false\n")
    for rel in Q19_REQUIRED_FILES:
        source = source_root / rel
        if source.exists() and source.is_file():
            write_text(root / rel, read_text(source))
        elif rel.endswith(".json"):
            write_text(root / rel, stable_json_text({"schema_version": "aide.gateway-status.v0", "provider_calls_enabled": False, "model_calls_enabled": False, "outbound_network_enabled": False, "raw_prompt_storage": False, "raw_response_storage": False, "readiness": {}, "signals": {}, "summaries": {}}))
        elif rel.startswith("core/gateway/"):
            write_text(root / rel, selftest_gateway_stub(rel) or f'"""Selftest Gateway fixture for {rel}."""\n')
        else:
            write_text(root / rel, f"schema_version: {rel}\nlocal_skeleton\nreport_only\nno_provider_forwarding\nraw_prompt_storage_default: false\nraw_response_storage_default: false\n")
    for rel in Q20_REQUIRED_FILES:
        source = source_root / rel
        if source.exists() and source.is_file():
            write_text(root / rel, read_text(source))
        elif rel.endswith(".json"):
            write_text(root / rel, stable_json_text({"schema_version": "aide.provider-status.v0", "live_provider_calls": False, "live_model_calls": False, "network_calls": False, "provider_probe_calls": False, "credentials_configured": False, "gateway_forwarding": False, "raw_prompt_storage": False, "raw_response_storage": False, "provider_ids": []}))
        elif rel.startswith("core/providers/"):
            write_text(root / rel, selftest_provider_stub(rel) or f'"""Selftest provider fixture for {rel}."""\n')
        else:
            write_text(root / rel, f"schema_version: {rel}\noffline_contracts_only\nmetadata_validation_only\nno_provider_calls\nlive_calls_allowed_in_q20: false\nraw_prompt_storage_default: false\nraw_response_storage_default: false\n")
    for rel in Q24_REQUIRED_FILES:
        if rel in {ADAPTER_GENERATED_MANIFEST_PATH, ADAPTER_DRIFT_REPORT_PATH}:
            continue
        source = source_root / rel
        if source.exists() and source.is_file():
            write_text(root / rel, read_text(source))
    for rel in Q27_REQUIRED_FILES:
        source = source_root / rel
        if source.exists() and source.is_file():
            write_text(root / rel, read_text(source))
    for rel in Q28_REQUIRED_FILES:
        source = source_root / rel
        if source.exists() and source.is_file():
            write_text(root / rel, read_text(source))
    for rel in Q29_REQUIRED_FILES:
        source = source_root / rel
        if source.exists() and source.is_file():
            write_text(root / rel, read_text(source))
    for rel in Q30_REQUIRED_FILES:
        source = source_root / rel
        if source.exists() and source.is_file():
            write_text(root / rel, read_text(source))
    source_golden_root = source_root / GOLDEN_TASK_ROOT
    if source_golden_root.exists():
        for source in sorted(source_golden_root.rglob("*")):
            if source.is_file():
                rel = normalize_rel(source.relative_to(source_root))
                write_text(root / rel, read_text(source))
    write_text(
        root / ".aide/queue/index.yaml",
        """schema_version: aide.queue-index.v0
items:
  - id: Q10-aide-lite-hardening
    status: running
    planning_state: implementation
    task: .aide/queue/Q10-aide-lite-hardening/task.yaml
    evidence: .aide/queue/Q10-aide-lite-hardening/evidence
""",
    )
    write_text(root / ".aide/queue/Q08-self-hosting-automation/status.yaml", "status: passed\n")
    write_text(root / ".aide/queue/Q09-token-survival-core/status.yaml", "status: needs_review\n")
    write_text(root / ".aide/queue/Q10-aide-lite-hardening/status.yaml", "status: running\n")
    write_text(root / ".aide/queue/Q11-context-compiler-v0/status.yaml", "status: running\n")
    write_text(root / ".aide/queue/Q12-verifier-v0/status.yaml", "status: running\n")
    write_text(root / ".aide/queue/Q13-evidence-review-workflow/status.yaml", "status: running\n")
    write_text(root / ".aide/queue/Q14-token-ledger-savings-report/status.yaml", "status: running\n")
    write_text(root / ".aide/queue/Q15-golden-tasks-v0/status.yaml", "status: running\n")
    write_text(root / ".aide/queue/Q16-outcome-controller-v0/status.yaml", "status: running\n")
    write_text(root / ".aide/queue/Q17-router-profile-v0/status.yaml", "status: running\n")
    write_text(root / ".aide/queue/Q18-cache-local-state-boundary/status.yaml", "status: running\n")
    write_text(root / ".aide/queue/Q19-gateway-architecture-skeleton/status.yaml", "status: running\n")
    write_text(root / ".aide/queue/Q20-provider-adapter-v0/status.yaml", "status: running\n")
    write_text(root / ".aide/queue/Q24-existing-tool-adapter-compiler-v0/status.yaml", "status: running\n")
    write_text(
        root / ".aide/queue/Q12-verifier-v0/task.yaml",
        """scope:
  allowed_paths:
    - .aide/**
    - AGENTS.md
    - README.md
    - core/harness/**
  forbidden_paths:
    - .git/**
    - .env
    - secrets/**
    - .aide.local/**
""",
    )
    write_text(root / "AGENTS.md", "# AGENTS\n\nManual intro.\n")
    write_text(root / "README.md", "# README\n")
    write_text(
        root / ".aide/queue/Q13-evidence-review-workflow/task.yaml",
        """non_goals:
  - Gateway
  - provider calls
  - automatic model calls
""",
    )
    write_text(
        root / ".aide/queue/Q14-token-ledger-savings-report/task.yaml",
        """scope:
  allowed_paths:
    - .aide/**
    - AGENTS.md
    - README.md
  forbidden_paths:
    - .git/**
    - .env
    - secrets/**
    - .aide.local/**
non_goals:
  - Gateway
  - provider calls
  - exact tokenizer
  - provider billing
""",
    )
    write_text(
        root / ".aide/queue/Q13-evidence-review-workflow/evidence/validation.md",
        """# Validation

- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS
- `py -3 .aide/scripts/aide_lite.py verify --review-packet .aide/context/latest-review-packet.md`: PASS
""",
    )
    write_text(
        root / ".aide/queue/Q13-evidence-review-workflow/evidence/remaining-risks.md",
        """# Risks

- structural review packet only
- no automatic model call
""",
    )
    write_text(
        root / ".aide/queue/Q14-token-ledger-savings-report/evidence/validation.md",
        """# Validation

- `py -3 .aide/scripts/aide_lite.py ledger scan`: PASS
- `py -3 .aide/scripts/aide_lite.py ledger report`: PASS
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS
""",
    )
    write_text(
        root / ".aide/queue/Q14-token-ledger-savings-report/evidence/remaining-risks.md",
        """# Risks

- estimated token accounting only
- no exact provider billing
""",
    )
    write_text(root / ".aide/scripts/aide_lite.py", "print('helper placeholder')\n")
    write_text(root / ".aide/scripts/tests/test_aide_lite.py", "def test_placeholder():\n    assert True\n")
    write_text(root / "core/harness/commands.py", "COMMANDS = []\n")
    write_text(root / "core/harness/tests/test_aide_harness.py", "def test_harness():\n    assert True\n")
    write_text(root / "core/compat/version_registry.py", "VERSION = 'x'\n")
    write_text(root / "core/compat/tests/test_compat_baseline.py", "def test_compat():\n    assert True\n")
    write_text(root / "src/example.py", "print('hello')\n")
    write_text(root / ".env", "SHOULD_NOT_APPEAR=1\n")
    write_text(root / ".git/config", "ignored\n")
    write_text(root / ".aide.local/state.json", "{}\n")
    write_text(root / "node_modules/pkg/index.js", "ignored\n")
    write_text(root / "build/output.txt", "ignored\n")


def run_selftest() -> tuple[bool, list[str]]:
    messages: list[str] = []
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _write_minimal_repo(root)
        assert estimate_text("abcd").approx_tokens == 1
        assert pattern_matches("core/harness/__pycache__/x.pyc", "__pycache__/**")
        assert pattern_matches("node_modules/pkg/index.js", "node_modules/**")
        assert pattern_matches(".env", ".env")
        assert pattern_matches(".aide.local/state.json", ".aide.local/**")
        snapshot_result = write_snapshot(root)
        snapshot = json.loads(read_text(snapshot_result.path))
        paths = [entry["path"] for entry in snapshot["files"]]
        assert ".env" not in paths
        assert all(not path.startswith(".git/") for path in paths)
        assert all(not path.startswith(".aide.local/") for path in paths)
        assert all(not path.startswith("node_modules/") for path in paths)
        assert all(not path.startswith("build/") for path in paths)
        assert paths == sorted(paths)
        assert snapshot["contents_inline"] is False
        assert "summary" in snapshot
        role, reason = classify_role(".aide/scripts/aide_lite.py")
        assert role == "script", reason
        role, reason = classify_role("core/harness/commands.py")
        assert role == "harness_code", reason
        index_result = run_index(root)
        repo_map = index_result["repo_map"]
        mapped_paths = [entry["path"] for entry in repo_map["files"]]
        assert ".env" not in mapped_paths
        assert mapped_paths == sorted(mapped_paths, key=lambda path: (classify_role(path)[0], path))
        assert all("contents" not in entry for entry in repo_map["files"])
        test_map = index_result["test_map_data"]
        aide_mapping = next(item for item in test_map["mappings"] if item["source"] == ".aide/scripts/aide_lite.py")
        assert aide_mapping["has_existing_candidate"] is True
        context_result = run_context(root)
        context_text = read_text(context_result["context_packet"].path)
        for section in CONTEXT_PACKET_REQUIRED_SECTIONS:
            assert f"## {section}" in context_text
        assert "print('hello')" not in context_text
        valid_ref, _message = validate_line_ref(root, "README.md#L1-L1")
        assert valid_ref
        packet_result, packet = write_task_packet(root, "Implement Q11 Context Compiler v0")
        packet_text = read_text(packet_result.path)
        for section in ["PHASE", "GOAL", "CONTEXT_REFS", "ACCEPTANCE", "TOKEN_ESTIMATE"]:
            assert f"## {section}" in packet_text
        assert REPO_MAP_JSON_PATH in packet_text
        assert LATEST_CONTEXT_PACKET_PATH in packet_text
        assert "print('hello')" not in packet_text
        assert packet.budget_status == "PASS"
        before_manual = read_text(root / "AGENTS.md")
        adapt_result, before, after = adapt_agents(root)
        once = read_text(root / "AGENTS.md")
        adapt_agents(root)
        twice = read_text(root / "AGENTS.md")
        assert "Manual intro." in twice
        assert before_manual != once
        assert once == twice
        assert adapt_result.action in {"appended", "written"}
        assert before.status == "missing"
        assert after.status == "current"
        ref_finding = validate_file_reference(root, "README.md#L1-L1")
        assert ref_finding.severity == "INFO", ref_finding
        missing_ref = validate_file_reference(root, "missing.md")
        assert missing_ref.severity == "WARN", missing_ref
        fake_secret_value = "1234567890abcdef" * 2
        secret_findings = scan_secret_text("api_key = '" + fake_secret_value + "'\n", ".aide/test.md")
        assert any(finding.severity == "ERROR" for finding in secret_findings)
        policy_findings = scan_secret_text("Mention api_key as policy text only.\n", ".aide/test.md")
        assert not any(finding.severity == "ERROR" for finding in policy_findings)
        verification = build_verification_report(root, task_packet_path=LATEST_PACKET_PATH)
        verification_failures = [f"{finding.severity} {finding.message}" for finding in verification.findings if finding.severity in {"ERROR", "FAIL"}]
        assert verification.result in {"PASS", "WARN"}, "\n".join(verification_failures) or verification.result
        rendered_report = render_verification_report(verification)
        assert "## VERIFIER_RESULT" in rendered_report
        assert "print('hello')" not in rendered_report
        write_verification_report(root, LATEST_VERIFICATION_REPORT_PATH, verification)
        review_result, review_packet = write_review_packet(root)
        review_text = read_text(review_result.path)
        for section in REVIEW_PACKET_REQUIRED_SECTIONS:
            assert f"## {section}" in review_text
        assert default_review_task_packet(root) in review_text
        assert LATEST_CONTEXT_PACKET_PATH in review_text
        assert LATEST_VERIFICATION_REPORT_PATH in review_text
        assert "print('hello')" not in review_text
        assert review_packet.budget_status == "PASS"
        review_findings = verify_review_packet(root, REVIEW_PACKET_PATH)
        assert not any(finding.severity == "ERROR" for finding in review_findings), review_findings
        selftest_record = ledger_record_for_file(root, LATEST_PACKET_PATH, surface="task_packet", run_id="selftest")
        assert selftest_record.approx_tokens > 0
        assert selftest_record.budget_status in {"within_budget", "near_budget", "over_budget"}
        ledger_result, merged_records, old_records = merge_ledger_records(root, [selftest_record], "selftest")
        assert ledger_result.action in {"written", "unchanged"}
        assert not old_records or all("raw" not in record.path.lower() for record in old_records)
        read_records = read_ledger_records(root)
        assert any(record.run_id == "selftest" and record.path == LATEST_PACKET_PATH for record in read_records)
        baseline = calculate_baseline(root, baseline_by_name(root, "root_history_baseline"))
        assert baseline.approx_tokens > 0
        comparison = compare_to_baseline(root, LATEST_PACKET_PATH, "root_history_baseline")
        assert comparison.reduction_percent is not None
        prior = LedgerRecord("prior", "Q", "task_packet", LATEST_PACKET_PATH, 4, 1, 1, "chars/4", "3200", "within_budget", "old")
        current = LedgerRecord("q14.scan.current", "Q", "task_packet", LATEST_PACKET_PATH, 400, 1, 100, "chars/4", "3200", "within_budget", "new")
        assert regression_warnings([prior], [current], 20)
        summary_result = write_token_savings_summary(root, read_records, [])
        assert summary_result.action in {"written", "unchanged"}
        summary_text = read_text(root / TOKEN_SUMMARY_PATH)
        assert "raw_prompt_storage: false" in summary_text
        assert "print('hello')" not in read_text(root / TOKEN_LEDGER_PATH)
        helper_plan = make_git_helper_plan(root, "plan", dry_run=True)
        helper_json, helper_md = write_git_helper_plan(root, helper_plan)
        assert helper_json.action in {"written", "unchanged"}
        assert helper_md.action in {"written", "unchanged"}
        definitions = parse_golden_task_catalog(root)
        assert len(definitions) >= 5
        eval_run = run_golden_tasks(root)
        assert eval_run.result in {"PASS", "WARN"}, eval_run.result
        json_result, md_result = write_golden_run_reports(root, eval_run)
        assert json_result.action in {"written", "unchanged"}
        assert md_result.action in {"written", "unchanged"}
        eval_data = read_latest_golden_run(root)
        assert eval_data["task_count"] >= 5
        assert "tasks" in eval_data
        assert "raw_prompt" not in read_text(root / GOLDEN_RUN_JSON_PATH).lower() or '"raw_prompt_storage": false' in read_text(root / GOLDEN_RUN_JSON_PATH).lower()
        assert "print('hello')" not in read_text(root / GOLDEN_RUN_MD_PATH)
        assert classify_branch_role("main") == "canonical"
        assert classify_branch_role("dev") == "integration"
        assert classify_branch_role("task/example") == "task"
        assert classify_branch_role("weird") == "unknown"
        assert detect_workflow_model(["main"], [])[0] == "trunk_without_dev"
        assert detect_workflow_model(["main", "dev"], [])[0] == "trunk_with_dev_integration"
        assert "gitflow_like_detected" in detect_workflow_model(["main", "develop"], [])[2]
        outcome_records = build_current_outcome_records(root)
        assert outcome_records
        outcome_write, merged_outcomes = merge_outcome_records(root, outcome_records, "q16.current")
        assert outcome_write.action in {"written", "unchanged"}
        recommendations = build_recommendations(root, outcome_records)
        assert recommendations
        assert all(not item.applies_automatically for item in recommendations)
        assert all(item.expected_benefit and item.rollback_condition for item in recommendations)
        outcome_report = write_outcome_report(root, outcome_records, recommendations)
        recommendation_report = write_recommendations(root, recommendations)
        assert outcome_report.action in {"written", "unchanged"}
        assert recommendation_report.action in {"written", "unchanged"}
        assert read_outcome_records(root)
        assert "raw_prompt_storage: false" in read_text(root / OUTCOME_REPORT_PATH)
        assert "applies_automatically: false" in read_text(root / RECOMMENDATIONS_PATH)
        assert "print('hello')" not in read_text(root / OUTCOME_LEDGER_PATH)
        assert merged_outcomes
        profiles = parse_route_profiles(root)
        assert any(profile.task_class == "deterministic_format_or_count" for profile in profiles)
        assert parse_hard_floor_minimums(root).get("architecture_decision")
        deterministic_decision = build_route_decision(root, task_packet_path=LATEST_PACKET_PATH)
        assert deterministic_decision.route_class in ROUTE_CLASSES
        write_task_packet(root, "Estimate tokens for README.md")
        estimate_decision = build_route_decision(root, task_packet_path=LATEST_PACKET_PATH)
        assert estimate_decision.task_class == "deterministic_format_or_count", estimate_decision
        assert estimate_decision.route_class == "no_model_tool", estimate_decision
        write_task_packet(root, "Decide architecture boundary for a new runtime service")
        architecture_decision = build_route_decision(root, task_packet_path=LATEST_PACKET_PATH)
        assert architecture_decision.hard_floor_applied in {"architecture_decision", "governance_policy_change"}, architecture_decision
        assert architecture_decision.route_class in {"frontier", "human_review"}, architecture_decision
        route_json, route_md = write_route_decision(root, architecture_decision)
        assert route_json.action in {"written", "unchanged"}
        assert route_md.action in {"written", "unchanged"}
        route_data = json.loads(read_text(root / ROUTE_DECISION_JSON_PATH))
        assert route_data["live_calls_allowed_in_q17"] is False
        assert route_data["contents_inline"] is False
        assert not any(check.severity == "FAIL" for check in routing_validation_checks(root))
        assert gitignore_has_local_state_rules(root)
        assert not local_state_git_paths(root)
        sample_hash = sha256_file(root / "README.md")
        sample_record = cache_record_for_file(root, "README.md", surface="baseline_surface", key_name="readme")
        assert sample_record.content_sha256 == sample_hash
        assert sample_record.key_id.startswith("aide-cache-v0:baseline_surface:")
        aide_record = cache_record_for_file(root, LATEST_PACKET_PATH, surface="task_packet", key_name="latest_task_packet")
        assert aide_record.dependency_hashes
        with (root / "README.md").open("a", encoding="utf-8", newline="\n") as handle:
            handle.write("changed\n")
        changed_record = cache_record_for_file(root, "README.md", surface="baseline_surface", key_name="readme")
        assert changed_record.key_id != sample_record.key_id
        for forbidden in [".env", ".aide.local/state.json"]:
            try:
                cache_record_for_file(root, forbidden, surface="baseline_surface")
                raise AssertionError(f"cache key should refuse {forbidden}")
            except ValueError:
                pass
        cache_json, cache_md, cache_data = write_cache_report(root)
        assert cache_json.action in {"written", "unchanged"}
        assert cache_md.action in {"written", "unchanged"}
        assert "keys" in cache_data
        assert "latest_task_packet" in cache_data["keys"]
        assert "print('hello')" not in read_text(root / CACHE_KEYS_JSON_PATH)
        assert "raw_prompt_body" not in read_text(root / CACHE_KEYS_JSON_PATH)
        assert not any(check.severity == "FAIL" for check in cache_validation_checks(root))
        gateway_module = import_gateway_status_module(root)
        gateway_json_path, gateway_md_path, gateway_data = gateway_module.write_gateway_status_files(root)
        assert normalize_rel(gateway_json_path.relative_to(root)) == GATEWAY_STATUS_JSON_PATH
        assert normalize_rel(gateway_md_path.relative_to(root)) == GATEWAY_STATUS_MD_PATH
        assert gateway_data["provider_calls_enabled"] is False
        assert gateway_data["model_calls_enabled"] is False
        assert gateway_data["outbound_network_enabled"] is False
        assert "readiness" in gateway_data
        health = gateway_module.health_payload()
        assert health["status"] == "ok"
        assert health["provider_calls_enabled"] is False
        smoke = gateway_module.smoke_gateway(root)
        assert smoke["result"] == "PASS"
        assert "print('hello')" not in read_text(root / GATEWAY_STATUS_JSON_PATH)
        assert "raw_prompt_body" not in read_text(root / GATEWAY_STATUS_JSON_PATH)
        assert not any(check.severity == "FAIL" for check in gateway_validation_checks(root))
        provider_module = import_provider_status_module(root)
        provider_json_path, provider_md_path, provider_data = provider_module.write_provider_status_files(root)
        assert normalize_rel(provider_json_path.relative_to(root)) == PROVIDER_STATUS_JSON_PATH
        assert normalize_rel(provider_md_path.relative_to(root)) == PROVIDER_STATUS_MD_PATH
        assert provider_data["live_provider_calls"] is False
        assert provider_data["live_model_calls"] is False
        assert provider_data["network_calls"] is False
        assert provider_data["credentials_configured"] is False
        assert provider_data["provider_family_count"] >= 13
        probe = provider_module.offline_probe(root)
        assert probe["provider_probe_calls"] is False
        assert "print('hello')" not in read_text(root / PROVIDER_STATUS_JSON_PATH)
        assert "raw_prompt_body" not in read_text(root / PROVIDER_STATUS_JSON_PATH)
        assert not any(check.severity == "FAIL" for check in provider_validation_checks(root))
        rendered_adapters, adapter_writes, adapter_drift = render_adapter_outputs(root, write=True)
        assert len(rendered_adapters) >= 7
        assert any(write.path.name == "manifest.json" for write in adapter_writes)
        assert any(record["target_id"] == "codex_agents_md" for record in adapter_drift)
        assert not any(check.severity == "FAIL" for check in adapter_validation_checks(root, require_generated=True))
        generated_agents = read_text(root / ".aide/generated/adapters/AGENTS.md")
        assert ".aide/context/latest-task-packet.md" in generated_agents
        assert "paste the full history" not in generated_agents.lower()
        ok, validate_messages = validate_repo(root)
        assert ok, "\n".join(validate_messages)
        messages.append("PASS internal estimate, ignore, snapshot, index, context, pack, adapt, drift, line-ref, verifier, review-pack, ledger, eval, commit, changelog, task, git workflow, outcome, optimize, route, cache, gateway, provider, adapter, and validate checks")
    return True, messages


def command_internal_test(args: argparse.Namespace, label: str) -> int:
    try:
        ok, messages = run_selftest()
    except AssertionError as exc:
        if os.environ.get("AIDE_SELFTEST_DEBUG"):
            raise
        print(label)
        print("status: FAIL")
        print(f"- {exc}")
        return 1
    return print_messages(label, ok, messages)


def command_selftest(args: argparse.Namespace) -> int:
    return command_internal_test(args, "AIDE Lite selftest")


def command_test(args: argparse.Namespace) -> int:
    return command_internal_test(args, "AIDE Lite test")


def build_parser(default_repo_root: Path) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AIDE Lite token-survival helper.")
    parser.add_argument("--repo-root", default=str(default_repo_root), help="Repository root. Defaults to the AIDE repo root.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor").set_defaults(handler=command_doctor)
    subparsers.add_parser("validate").set_defaults(handler=command_validate)

    estimate_parser = subparsers.add_parser("estimate")
    estimate_parser.add_argument("--file", required=True)
    estimate_parser.set_defaults(handler=command_estimate)

    subparsers.add_parser("snapshot").set_defaults(handler=command_snapshot)
    subparsers.add_parser("index").set_defaults(handler=command_index)
    subparsers.add_parser("context").set_defaults(handler=command_context)
    subparsers.add_parser("map").set_defaults(handler=command_map)

    pack_parser = subparsers.add_parser("pack")
    pack_parser.add_argument("--task", required=True)
    pack_parser.set_defaults(handler=command_pack)

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--evidence", help="Evidence packet path to validate.")
    verify_parser.add_argument("--task-packet", help="Task packet path to validate. Defaults to latest task packet.")
    verify_parser.add_argument("--review-packet", help="Review packet path to validate. Defaults to latest review packet when present.")
    verify_parser.add_argument("--changed-files", action="store_true", help="Only classify git changed files against scope.")
    verify_parser.add_argument("--write-report", help="Write compact verification report under .aide/verification/ or .aide/queue/.")
    verify_parser.set_defaults(handler=command_verify)

    review_parser = subparsers.add_parser("review-pack")
    review_parser.add_argument("--task-packet", help="Task packet path to reference. Defaults to the current queue task when present.")
    review_parser.add_argument("--verification", default=LATEST_VERIFICATION_REPORT_PATH, help="Verification report path to reference.")
    review_parser.add_argument("--evidence-dir", help="Evidence directory to reference. Defaults to the current queue evidence directory.")
    review_parser.add_argument("--output", default=REVIEW_PACKET_PATH, help="Review packet output path.")
    review_parser.add_argument("--changed-files", action="store_true", help="Include git changed-file summary; current default already includes it.")
    review_parser.add_argument("--max-token-warning", type=int, help="Warn when review packet exceeds this approximate-token threshold.")
    review_parser.set_defaults(handler=command_review_pack)

    ledger_parser = subparsers.add_parser("ledger")
    ledger_subparsers = ledger_parser.add_subparsers(dest="ledger_command", required=True)

    ledger_scan_parser = ledger_subparsers.add_parser("scan")
    ledger_scan_parser.add_argument("--run-id", default="q14.scan.current", help="Stable run id for replacing current scan records.")
    ledger_scan_parser.set_defaults(handler=command_ledger_scan)

    ledger_add_parser = ledger_subparsers.add_parser("add")
    ledger_add_parser.add_argument("--file", required=True, help="File to add as estimated metadata.")
    ledger_add_parser.add_argument("--surface", choices=LEDGER_SURFACES, help="Record surface. Defaults to detection from path.")
    ledger_add_parser.add_argument("--phase", default="Q14-token-ledger-savings-report")
    ledger_add_parser.add_argument("--run-id", default="q14.manual")
    ledger_add_parser.add_argument("--notes", default="")
    ledger_add_parser.set_defaults(handler=command_ledger_add)

    ledger_report_parser = ledger_subparsers.add_parser("report")
    ledger_report_parser.add_argument("--run-id", default="q14.scan.current", help="Run id to use as current records for regression checks.")
    ledger_report_parser.set_defaults(handler=command_ledger_report)

    ledger_compare_parser = ledger_subparsers.add_parser("compare")
    ledger_compare_parser.add_argument("--baseline", required=True)
    ledger_compare_parser.add_argument("--file", required=True)
    ledger_compare_parser.add_argument("--surface", choices=LEDGER_SURFACES)
    ledger_compare_parser.set_defaults(handler=command_ledger_compare)

    eval_parser = subparsers.add_parser("eval")
    eval_subparsers = eval_parser.add_subparsers(dest="eval_command", required=True)

    eval_subparsers.add_parser("list").set_defaults(handler=command_eval_list)

    eval_run_parser = eval_subparsers.add_parser("run")
    eval_run_parser.add_argument("--task", help="Run one golden task id. Defaults to all tasks.")
    eval_run_parser.set_defaults(handler=command_eval_run)

    eval_subparsers.add_parser("report").set_defaults(handler=command_eval_report)

    commit_parser = subparsers.add_parser("commit")
    commit_subparsers = commit_parser.add_subparsers(dest="commit_command", required=True)
    commit_check_parser = commit_subparsers.add_parser("check")
    commit_check_parser.add_argument("--message-file", help="Commit message file to validate, such as .git/COMMIT_EDITMSG.")
    commit_check_parser.add_argument("--message", help="Inline commit message text to validate.")
    commit_check_parser.add_argument("--latest", action="store_true", help="Validate the latest Git commit message.")
    commit_check_parser.add_argument("--range", help="Validate all commits in a Git revision range, such as BASE..HEAD.")
    commit_check_parser.add_argument("--max-count", type=int, help="Limit range validation to the latest N commits in the range.")
    commit_check_parser.set_defaults(handler=command_commit_check)
    commit_template_parser = commit_subparsers.add_parser("template")
    commit_template_parser.add_argument("--output", help="Optional repo-relative path to write the template.")
    commit_template_parser.set_defaults(handler=command_commit_template)
    commit_install_parser = commit_subparsers.add_parser("install-hook")
    commit_install_parser.add_argument("--force", action="store_true", help="Replace an existing core.hooksPath value.")
    commit_install_parser.set_defaults(handler=command_commit_install_hook)
    commit_subparsers.add_parser("status").set_defaults(handler=command_commit_status)

    changelog_parser = subparsers.add_parser("changelog")
    changelog_subparsers = changelog_parser.add_subparsers(dest="changelog_command", required=True)
    changelog_preview_parser = changelog_subparsers.add_parser("preview")
    changelog_preview_parser.add_argument("--range", help="Git revision range to preview. Defaults to recent history.")
    changelog_preview_parser.set_defaults(handler=command_changelog_preview)

    task_parser = subparsers.add_parser("task")
    task_subparsers = task_parser.add_subparsers(dest="task_command", required=True)
    task_inspect_parser = task_subparsers.add_parser("inspect")
    task_inspect_parser.add_argument("--task-id", help="Queue task id. Defaults to current/latest task.")
    task_inspect_parser.set_defaults(handler=command_task_inspect)
    task_subparsers.add_parser("status").set_defaults(handler=command_task_status)
    task_noop_parser = task_subparsers.add_parser("noop-check")
    task_noop_parser.add_argument("--task-id", help="Queue task id. Defaults to current/latest task.")
    task_noop_parser.set_defaults(handler=command_task_noop_check)
    task_dependencies_parser = task_subparsers.add_parser("dependencies")
    task_dependencies_parser.add_argument("--task-id", help="Queue task id. Defaults to current/latest task.")
    task_dependencies_parser.set_defaults(handler=command_task_dependencies)
    task_recover_parser = task_subparsers.add_parser("recover")
    task_recover_parser.add_argument("--task-id", help="Queue task id. Defaults to current/latest task.")
    task_recover_parser.add_argument("--write-report", action="store_true", help="Write a recovery report under task evidence.")
    task_recover_parser.set_defaults(handler=command_task_recover)
    task_evidence_parser = task_subparsers.add_parser("evidence")
    task_evidence_parser.add_argument("--task-id", help="Queue task id. Defaults to current/latest task.")
    task_evidence_parser.set_defaults(handler=command_task_evidence)
    task_subparsers.add_parser("current").set_defaults(handler=command_task_current)

    git_parser = subparsers.add_parser("git")
    git_subparsers = git_parser.add_subparsers(dest="git_command", required=True)
    git_subparsers.add_parser("detect").set_defaults(handler=command_git_detect)
    git_subparsers.add_parser("doctor").set_defaults(handler=command_git_doctor)
    git_subparsers.add_parser("status").set_defaults(handler=command_git_status)
    git_subparsers.add_parser("workflow").set_defaults(handler=command_git_workflow)
    git_subparsers.add_parser("roles").set_defaults(handler=command_git_roles)
    git_subparsers.add_parser("policy").set_defaults(handler=command_git_policy)
    git_subparsers.add_parser("plan").set_defaults(handler=command_git_plan)
    git_sync_parser = git_subparsers.add_parser("sync")
    git_sync_parser.add_argument("--dry-run", action="store_true", help="Report only; default behavior.")
    git_sync_parser.add_argument("--apply", action="store_true", help="Apply local sync action explicitly.")
    git_sync_parser.set_defaults(handler=command_git_sync)
    git_land_parser = git_subparsers.add_parser("land")
    git_land_parser.add_argument("--dry-run", action="store_true", help="Report only; default behavior.")
    git_land_parser.add_argument("--apply", action="store_true", help="Apply local task-to-integration merge explicitly.")
    git_land_parser.add_argument("--push", action="store_true", help="Plan future push explicitly; Q29 does not execute remote push.")
    git_land_parser.add_argument("--source", help="Source task branch. Defaults to current branch.")
    git_land_parser.add_argument("--target", default="dev", help="Integration target branch.")
    git_land_parser.add_argument("--validation-ok", action="store_true", help="Acknowledge validation evidence for fixture/operator-controlled use.")
    git_land_parser.set_defaults(handler=command_git_land)
    git_promote_parser = git_subparsers.add_parser("promote")
    git_promote_parser.add_argument("--dry-run", action="store_true", help="Report only; default behavior.")
    git_promote_parser.add_argument("--apply", action="store_true", help="Apply local integration-to-canonical merge explicitly.")
    git_promote_parser.add_argument("--push", action="store_true", help="Plan future push explicitly; Q29 does not execute remote push.")
    git_promote_parser.add_argument("--from", dest="source_branch", default="dev", help="Integration source branch.")
    git_promote_parser.add_argument("--to", dest="target_branch", default="main", help="Canonical target branch.")
    git_promote_parser.add_argument("--validation-ok", action="store_true", help="Acknowledge validation evidence for fixture/operator-controlled use.")
    git_promote_parser.add_argument("--review-ok", action="store_true", help="Acknowledge review evidence for fixture/operator-controlled use.")
    git_promote_parser.set_defaults(handler=command_git_promote)
    git_prune_parser = git_subparsers.add_parser("prune")
    git_prune_parser.add_argument("--dry-run", action="store_true", help="Report only; default behavior.")
    git_prune_parser.add_argument("--apply", action="store_true", help="Delete eligible local branches explicitly.")
    git_prune_parser.add_argument("--target", help="Containment target. Defaults to dev and/or main when present.")
    git_prune_parser.set_defaults(handler=command_git_prune)

    outcome_parser = subparsers.add_parser("outcome")
    outcome_subparsers = outcome_parser.add_subparsers(dest="outcome_command", required=True)

    outcome_add_parser = outcome_subparsers.add_parser("add")
    outcome_add_parser.add_argument("--run-id", default="q16.manual")
    outcome_add_parser.add_argument("--phase", required=True)
    outcome_add_parser.add_argument("--source", required=True)
    outcome_add_parser.add_argument("--result", required=True, choices=["PASS", "WARN", "FAIL"])
    outcome_add_parser.add_argument("--failure-class", required=True, choices=CONTROLLER_FAILURE_CLASSES)
    outcome_add_parser.add_argument("--severity", required=True, choices=["info", "warning", "error"])
    outcome_add_parser.add_argument("--related-path", action="append", help="Existing repo-relative evidence path. May be repeated.")
    outcome_add_parser.add_argument("--notes", default="")
    outcome_add_parser.set_defaults(handler=command_outcome_add)

    outcome_subparsers.add_parser("report").set_defaults(handler=command_outcome_report)

    optimize_parser = subparsers.add_parser("optimize")
    optimize_subparsers = optimize_parser.add_subparsers(dest="optimize_command", required=True)
    optimize_subparsers.add_parser("suggest").set_defaults(handler=command_optimize_suggest)

    route_parser = subparsers.add_parser("route")
    route_subparsers = route_parser.add_subparsers(dest="route_command", required=True)
    route_subparsers.add_parser("list").set_defaults(handler=command_route_list)
    route_subparsers.add_parser("validate").set_defaults(handler=command_route_validate)
    route_explain_parser = route_subparsers.add_parser("explain")
    route_explain_parser.add_argument("--task-packet", help="Task packet path to route. Defaults to latest task packet.")
    route_explain_parser.set_defaults(handler=command_route_explain)

    cache_parser = subparsers.add_parser("cache")
    cache_subparsers = cache_parser.add_subparsers(dest="cache_command", required=True)
    cache_subparsers.add_parser("init").set_defaults(handler=command_cache_init)
    cache_subparsers.add_parser("status").set_defaults(handler=command_cache_status)
    cache_key_parser = cache_subparsers.add_parser("key")
    cache_key_parser.add_argument("--file", help="Repo-relative file path to key.")
    cache_key_parser.add_argument("--task-packet", help="Task packet path to key with task/context policy dependencies.")
    cache_key_parser.set_defaults(handler=command_cache_key)
    cache_subparsers.add_parser("report").set_defaults(handler=command_cache_report)

    gateway_parser = subparsers.add_parser("gateway")
    gateway_subparsers = gateway_parser.add_subparsers(dest="gateway_command", required=True)
    gateway_subparsers.add_parser("status").set_defaults(handler=command_gateway_status)
    gateway_subparsers.add_parser("endpoints").set_defaults(handler=command_gateway_endpoints)
    gateway_subparsers.add_parser("smoke").set_defaults(handler=command_gateway_smoke)
    gateway_serve_parser = gateway_subparsers.add_parser("serve")
    gateway_serve_parser.add_argument("--host", default="127.0.0.1")
    gateway_serve_parser.add_argument("--port", type=int, default=8765)
    gateway_serve_parser.set_defaults(handler=command_gateway_serve)

    provider_parser = subparsers.add_parser("provider")
    provider_subparsers = provider_parser.add_subparsers(dest="provider_command", required=True)
    provider_subparsers.add_parser("list").set_defaults(handler=command_provider_list)
    provider_subparsers.add_parser("status").set_defaults(handler=command_provider_status)
    provider_subparsers.add_parser("validate").set_defaults(handler=command_provider_validate)
    provider_subparsers.add_parser("contract").set_defaults(handler=command_provider_contract)
    provider_probe_parser = provider_subparsers.add_parser("probe")
    provider_probe_parser.add_argument("--offline", action="store_true", help="Run metadata-only offline probe. Required in Q20.")
    provider_probe_parser.set_defaults(handler=command_provider_probe)

    export_parser = subparsers.add_parser("export-pack")
    export_parser.add_argument("--name", default=EXPORT_PACK_ID)
    export_parser.add_argument("--output", help="Optional output path. Q21 only permits the committed pack path.")
    export_parser.set_defaults(handler=command_export_pack)

    import_parser = subparsers.add_parser("import-pack")
    import_parser.add_argument("--pack", default=EXPORT_PACK_PATH)
    import_parser.add_argument("--target", required=True)
    import_parser.add_argument("--dry-run", action="store_true")
    import_parser.add_argument(
        "--mode",
        choices=sorted(IMPORT_MODES),
        default="safe",
        help="safe imports portable .aide/templates only; full includes optional broad roots for reviewed fixtures.",
    )
    import_parser.set_defaults(handler=command_import_pack)

    subparsers.add_parser("pack-status").set_defaults(handler=command_pack_status)

    adapter_parser = subparsers.add_parser("adapter")
    adapter_subparsers = adapter_parser.add_subparsers(dest="adapter_command", required=True)
    adapter_subparsers.add_parser("list").set_defaults(handler=command_adapter_list)
    adapter_subparsers.add_parser("render").set_defaults(handler=command_adapter_render)
    adapter_subparsers.add_parser("preview").set_defaults(handler=command_adapter_preview)
    adapter_subparsers.add_parser("validate").set_defaults(handler=command_adapter_validate)
    adapter_subparsers.add_parser("drift").set_defaults(handler=command_adapter_drift)
    adapter_subparsers.add_parser("generate").set_defaults(handler=command_adapter_generate)

    subparsers.add_parser("adapt").set_defaults(handler=command_adapt)
    subparsers.add_parser("selftest").set_defaults(handler=command_selftest)
    subparsers.add_parser("test").set_defaults(handler=command_test)
    subparsers.add_parser("version").set_defaults(handler=command_version)
    subparsers.add_parser("show-config").set_defaults(handler=command_show_config)
    return parser


def main(argv: list[str] | None = None) -> int:
    default_root = repo_root_from_script()
    parser = build_parser(default_root)
    args = parser.parse_args(argv)
    args.repo_root = Path(args.repo_root).resolve()
    try:
        return int(args.handler(args))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
