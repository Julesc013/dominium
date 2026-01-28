# SysCaps and Execution Policy (HWCAPS0)

Status: draft.
Scope: deterministic backend selection and budget resolution.

## Invariants
- Backend selection is deterministic and auditable.
- Unknown SysCaps are treated conservatively.
- GPU is derived-only for authoritative work.

## SysCaps Fields
SysCaps define conservative hardware/platform signals:
- CPU: core counts, SMT presence, core class, cache class, SIMD caps.
- GPU: presence, memory model, compute queue availability, class bucket.
- Storage: HDD/SSD/NVMe class, direct-storage support.
- Network: offline/lan/wan class (server overrides allowed).
- Platform: OS and architecture family.

Field semantics and allowed values are defined in:
- `schema/syscaps/SPEC_SYS_CAPS.md`
- `schema/syscaps/SPEC_SYS_CAPS_FIELDS.md`

## Unknown Handling Rules
- Unknown values are allowed and treated conservatively.
- No benchmarking or wall-clock timing is permitted for detection.
- Unknown does not imply absence; it implies "do not select".

## Policy Resolution Algorithm
1) Load the ordered preferences from the selected profile.
2) Apply law constraints (deny-by-law overrides allow-by-profile).
3) Filter by SysCaps (unknown treated as unavailable).
4) Select the first eligible backend in order.
5) If no scheduler qualifies, fall back to exec2_single_thread and record it.
6) GPU is never eligible for authoritative tasks (derived only).

## Law Constraints
Execution policy consumes law outputs as boolean flags:
- allow_multithread
- allow_simd
- allow_gpu_derived
- allow_modified_clients
- allow_unauthenticated
- allow_debug_tools

Policy never evaluates law itself; it only consumes evaluated flags.

## Audit Outputs
Policy selection produces a structured audit summary:
- Selected scheduler backend and kernel masks.
- Denial reasons (profile, law, or SysCaps).
- Deterministic budget outputs and policy hash.

Audits prevent silent fallbacks and allow tooling to explain degradations.

## Forbidden assumptions
- Benchmarking or wall-clock timing can drive authoritative selection.
- Unknown hardware is treated as available.

## Dependencies
- SysCaps schema: `schema/syscaps/README.md`
- Execution model: `docs/architecture/EXECUTION_MODEL.md`

## See also
- `docs/architecture/HARDWARE_EVOLUTION_STRATEGY.md`
