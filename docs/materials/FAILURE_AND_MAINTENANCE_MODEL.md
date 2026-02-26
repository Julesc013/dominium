Status: CANONICAL
Last Reviewed: 2026-02-26
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: MAT-0 failure and maintenance constitution
Binding Sources: docs/canon/constitution_v1.md, docs/canon/glossary_v1.md

# Failure and Maintenance Model

This document defines baseline constitutional rules for material failure and maintenance scaffolding.

## 1) Failure Modes

- Failure modes are registry-defined and deterministic.
- Macro tier applies failure risk as distribution-level state.
- Micro tier applies failures as explicit part state only in ROI.
- No implicit spontaneous failure mutation is allowed outside process execution.

## 2) Maintenance

- Maintenance backlog is an explicit field on relevant assemblies/projects.
- Maintenance is represented as commitments and executed via processes.
- Deferred maintenance increases configured failure probability and risk accumulation.
- Maintenance outcomes must emit provenance events.

## 3) Entropy Integration

- Entropy-like efficiency loss metrics may be tracked in ledger channels or companion metrics.
- Default constitutional behavior is track-only, not globally enforced.
- Future domain solvers may add enforcement constraints without rewriting this contract.

