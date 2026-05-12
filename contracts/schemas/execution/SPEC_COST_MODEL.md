# SPEC_COST_MODEL (EXEC0)

Status: binding.
Scope: declarative cost model metadata for Work IR tasks.
Non-goals: runtime scheduling or performance optimization.

## Purpose
Cost models provide deterministic, declarative estimates so backends can apply
budgets and degradation rules without rewriting gameplay logic.

## CostModel
Fields:
- cost_id: stable, deterministic identifier.
- cpu_upper_bound: abstract units (non-negative integer).
- memory_upper_bound: abstract units (non-negative integer).
- bandwidth_upper_bound: abstract units (non-negative integer).
- latency_sensitivity: low | medium | high
- degradation_priority: integer (higher means preserve longer)

Rules:
- Cost models are estimates, not measurements.
- Bounds MUST be deterministic and auditable.
- cost_id MUST be stable across equivalent versions.
- degradation_priority influences backend degradation order; higher values are
  degraded last.

## Budget Integration
Budgets are applied by execution backends. Cost models supply the required
inputs for budget evaluation and graceful degradation but do not encode
backend-specific policy.

## Forbidden Patterns
- Omitting cost models for TaskNode entries.
- Encoding execution policy directly in gameplay logic.
