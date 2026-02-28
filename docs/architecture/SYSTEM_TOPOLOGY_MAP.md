# System Topology Map

Status: Canonical (ARCH-REF-2)
Version: 1.0.0

## Purpose
- The System Topology Map is a deterministic, derived governance artifact.
- It describes architectural structure and declared semantic dependencies.
- It is used for enforcement, impact analysis, and drift detection.

## Non-Goals
- It is not a runtime dependency.
- It must not alter simulation semantics.
- It must not add production runtime cost.

## Node Kinds
- `module`
- `schema`
- `registry`
- `tool`
- `process_family`
- `contract_set`
- `policy_set`

## Edge Kinds
- `depends_on`
- `produces`
- `consumes`
- `validates`
- `enforces`
- `migrates`

## Determinism Requirements
- Stable node identity and deterministic node ordering.
- Stable edge identity and deterministic edge ordering.
- Canonical serialization for JSON artifacts.
- Stable deterministic fingerprint from canonical content (excluding run-meta fields).

## Artifacts
- `docs/audit/TOPOLOGY_MAP.json`
- `docs/audit/TOPOLOGY_MAP.md`

## Governance Use
- RepoX/AuditX enforce declared-boundary coverage.
- Semantic impact selection uses topology plus changed files.
- Unknown/uncertain impact analysis must safely fall back to broader verification.

## Planned CTRL Nodes
- `module:src/control`
- `module:src/control/control_plane_engine.py`
- `module:src/control/control_ir_validator.py`
- `module:src/control/control_decision_log.py`

These nodes are declared as planned topology surfaces so enforcement can require
the correct test envelopes before CTRL runtime migration is complete.

## CTRL Semantic Impact Requirements
Changes under `src/control/**` must require:
- multiplayer determinism envelope suites
- RS-5 arbitration/fairness suites
- replay/reenactment determinism suites
