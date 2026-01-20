# SPEC_BUDGET_PROFILES (HWCAPS0)

Schema ID: BUDGET_PROFILES
Schema Version: 1.0.0
Status: binding.
Scope: deterministic budget profile inputs and resolved budget outputs.

## Purpose
Define abstract, deterministic budgets used to bound per-tick work without
consulting wall-clock time. Budgets control performance only.

## BudgetProfile Fields (inputs)
- budget_profile_id: string identifier
- base_cpu_authoritative: u32 units
- base_cpu_derived: u32 units
- base_io_derived: u32 units
- base_net: u32 units
- memory_budget_class: small | medium | large | huge
- degradation_policy_id: string identifier
- cpu_scale_min: u32 (>= 1)
- cpu_scale_max: u32 (>= cpu_scale_min)
- io_scale_max: u32 (>= 1)
- net_scale_max: u32 (>= 1)

## Resolved Budget Outputs
- per_tick_cpu_budget_units_authoritative
- per_tick_cpu_budget_units_derived
- per_tick_io_budget_units_derived
- per_tick_net_budget_units
- memory_budget_class
- degradation_policy_id

## Rules
- Budgets are upper bounds, not measurements.
- Budgets must be deterministic given the same SysCaps + ProfileConfig.
- Unknown SysCaps values must resolve to conservative scaling.
- No wall-clock or benchmarking dependencies are allowed.
