# Hardware Evolution Strategy (HWCAPS0)

Status: draft.
Scope: performance adaptation without gameplay rewrites.

## Invariants
- Hardware changes may alter performance, never authoritative truth.
- Authoritative outcomes remain deterministic across backends.
- Execution policy is data-driven (SysCaps + profiles), not ad hoc code.

## Historical Shifts (2000+)
- Multicore CPUs forced parallel scheduling and stable commit ordering.
- SIMD widening (SSE2 → AVX2/AVX-512, NEON → SVE) split scalar vs vector paths.
- Explicit graphics APIs (DX12/Vulkan/Metal) decoupled driver scheduling.
- Heterogeneous cores (P/E cores, big.LITTLE) broke naive core-count heuristics.
- NUMA and chiplets introduced locality-sensitive budgeting.
- SSD/NVMe displaced HDD assumptions for IO pacing and streaming.
- GPU compute expanded derived workloads, but strict determinism remains CPU-only.
- Ray tracing introduced new GPU-heavy derived paths and IO pressure.
- NPUs introduced offload paths with non-deterministic latency.

## Dominium Strategy
- Work IR + Access IR for authoritative work representation (EXEC0).
- Backend registries for deterministic selection and auditability.
- Execution policy layer (SysCaps + profiles + law constraints).
- Deterministic budget model and degradation ladders (ARCH0 A6).
- Strict separation: engine selects backends, game retains meaning.

## Determinism Statement
Policies may change performance, not truth. Authoritative outcomes remain
identical across hardware profiles and backend selections.

## Forbidden assumptions
- New hardware justifies changing simulation semantics.
- GPU or accelerator paths may write authoritative state.

## Dependencies
- Execution model: `docs/architecture/EXECUTION_MODEL.md`
- SysCaps policy: `docs/architecture/SYS_CAPS_AND_EXEC_POLICY.md`
- SysCaps schema: `schema/syscaps/README.md`

## See also
- `docs/architecture/EXECUTION_MODEL.md`
- `docs/architecture/SYS_CAPS_AND_EXEC_POLICY.md`
