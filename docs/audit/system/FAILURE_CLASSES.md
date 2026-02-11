Status: DERIVED
Last Reviewed: 2026-02-11
Supersedes: none
Superseded By: none

# Failure Class Registry

This registry classifies recurring mechanical failure classes and binds each class to:

- a remediation playbook,
- at least one regression test,
- and a stable explanation reference.

## TOOL_DISCOVERY

- playbook: `dominium.playbook.tool_discovery`
- coverage focus: empty `PATH`, arbitrary `CWD`, missing tool discovery paths

## DERIVED_ARTIFACT_STALE

- playbook: `dominium.playbook.derived_artifact_stale`
- coverage focus: canonical artifact hash stability and timestamp exclusion

## SCHEMA_MISMATCH

- playbook: `dominium.playbook.schema_mismatch`
- coverage focus: schema diffs, migration requirements, compatibility checks

## UI_BIND_DRIFT

- playbook: `dominium.playbook.ui_bind_drift`
- coverage focus: UI binding drift and direct-gate invocation regressions

## BUILD_OUTPUT_MISSING

- playbook: `dominium.playbook.build_output_missing`
- coverage focus: queue continuation under missing build outputs

## PATH_CWD_DEPENDENCY

- playbook: `dominium.playbook.path_cwd_dependency`
- coverage focus: empty-path and arbitrary-cwd execution resilience

## WORKSPACE_COLLISION

- playbook: `dominium.playbook.workspace_collision`
- coverage focus: workspace-scoped build/dist isolation and parallel runs

## IDENTITY_DRIFT

- playbook: `dominium.playbook.doc_canon_drift`
- coverage focus: identity fingerprint explanation and drift lock checks
