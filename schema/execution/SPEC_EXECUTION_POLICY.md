# SPEC_EXECUTION_POLICY (HWCAPS0)

Schema ID: EXEC_POLICY
Schema Version: 1.0.0
Status: binding.
Scope: deterministic execution policy selection.

## Purpose
Define how SysCaps, data-defined profiles, and law constraints select
execution backends deterministically without altering gameplay meaning.

## Inputs
- SysCaps (see `schema/syscaps/SPEC_SYS_CAPS.md`)
- ProfileConfig (data-defined, see `schema/syscaps/SPEC_PLATFORM_PROFILES.md`)
- LawConstraints (evaluated elsewhere, provided as booleans)

LawConstraints fields (booleans):
- allow_multithread
- allow_simd
- allow_gpu_derived
- allow_modified_clients
- allow_unauthenticated
- allow_debug_tools

## Outputs
- scheduler_backend: exec2_single_thread | exec3_parallel
- ecs_backend: soa_default
- kernel_backends:
  - allow_scalar (always true)
  - allow_simd (caps + profile + law)
  - allow_gpu_derived (caps + profile + law; DERIVED-only)
- render_backend_allowlist (optional; client-only)
- budget_profile: resolved budgets (see SPEC_BUDGET_PROFILES)
- audit summary (structured, deterministic)

## Selection Algorithm (Deterministic)
1) Start from ordered preference lists in ProfileConfig.
2) Filter by LawConstraints (deny overrides allow).
3) Filter by SysCaps (unknown treated conservatively).
4) Select the first eligible backend in order.
5) If no scheduler is eligible, fall back to exec2_single_thread and record
   an audit downgrade.
6) GPU backends are never eligible for authoritative tasks.

## Determinism and Safety Rules
- SysCaps never influence gameplay meaning, only backends/budgets.
- No wall-clock or benchmarking inputs are allowed.
- Unknown SysCaps values must not trigger optimistic selection.
- All downgrades must be explicit and auditable.
- Scalar kernels and exec2 must remain valid fallbacks.
