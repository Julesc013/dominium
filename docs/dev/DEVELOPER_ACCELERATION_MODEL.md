Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Requires `tools/xstack/run.py`, `tools/dev/dev.py`, and `tools/dev/impact_graph/`.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Developer Acceleration Model

## Purpose

This document defines the deterministic acceleration layer used to keep developer iteration fast without bypassing canonical verification surfaces.

Binding references:

- `AGENTS.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/testing/xstack_profiles.md`
- `docs/dev/IMPACT_GRAPH.md`

## Lanes

### Dev lane

- Goal: shortest deterministic feedback loop during active changes.
- Primary entrypoint: `tools/dev/dev verify` for strict checks, plus impacted subsets via `tools/dev/dev impacted-tests`.
- Must not run packaging/publish operations.
- Produces non-gating acceleration artifacts:
  - `build/impact_graph.json`
  - impact/test selection summaries
  - optional profile traces

### Verify lane

- Goal: deterministic policy and behavioral validation for change acceptance.
- Primary entrypoint: `tools/xstack/run strict`.
- Runs full strict checks including RepoX, AuditX, TestX all-tests, packaging verification, and UI binding checks.
- Produces canonical xstack report:
  - `tools/xstack/out/strict/latest/report.json`

### Dist lane

- Goal: deterministic packaging and reproducible distribution proof.
- Primary entrypoints:
  - `tools/setup/build --bundle bundle.base.lab --out dist`
  - `tools/xstack/run strict` (packaging/lab validation step)
- Must include lockfile and registry hash validation.
- Must not change version metadata implicitly.

## XStack profile intent

### FAST

- Uses deterministic impacted-test subset selection by default.
- If impact graph is unavailable or incomplete, FAST falls back to full TestX suite for safety.
- Never silently skips tests.

### STRICT

- Runs full deterministic suite and strict invariants.
- Used as the acceptance gate for this repository.

### FULL

- Runs strict-equivalent gates plus deterministic sharding/stress surfaces.
- Intentionally slower and used for higher-assurance validation.

## Impact graph model

- Impact graph is deterministic and content-derived.
- Changed files propagate impact through deterministic edges to:
  - tests
  - build targets/products
  - generated artifacts
- Graph artifact (`build/impact_graph.json`) is derived and reproducible for identical input trees.

See `docs/dev/IMPACT_GRAPH.md` for node/edge contract.

## Regression lock philosophy

- Observer MVP behavior is protected by explicit baseline locks.
- Baseline file:
  - `data/regression/observer_baseline.json`
- Baselines are stable by default; updates must be explicit and traceable.
- Baseline updates require commit intent marker `REGRESSION-UPDATE`.

## CI artifact consumption

CI lanes consume deterministic artifacts for auditability and speed:

- impact graph snapshot (`build/impact_graph.json`)
- AuditX findings (`docs/audit/auditx/*`)
- XStack reports (`tools/xstack/out/<profile>/latest/report.json`)
- profiling traces (schema-validated, non-gating)
  - `docs/audit/perf/profile_trace.sample.json`
  - `docs/audit/perf/profile_trace.sample.md`

## Build Identity Identifier (BII) usage

- BII is recorded in profile artifacts to tie performance traces to build/tool identity.
- BII is diagnostic metadata only.
- BII must not alter pass/fail decisions in FAST/STRICT/FULL.
- Profile trace artifacts are validated against `schemas/profile_trace.schema.json` before publication.

## Intentionally slow paths

The following remain intentionally expensive:

- FULL profile multi-shard regression runs
- complete TestX suite in STRICT/FULL
- full packaging reproducibility verification

These are preserved to maintain deterministic confidence and prevent hidden quality drift.
